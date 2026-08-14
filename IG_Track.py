#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IG TRACKER - Instagram User Activity Tracker (single file, Kali-ready)
Fetches REAL public Instagram data live via instaloader. No mock data.

IMPORTANT (2024+): Instagram REQUIRES login for follow/follower/comment/tagged data.
Anonymous mode no longer works for those sections.

Install (Kali 2023+ enforces PEP 668 - use a venv):
    python3 -m venv ~/igtracker
    ~/igtracker/bin/pip install -U flask instaloader requests

Run (REQUIRED - without credentials the app refuses to start):
    export INSTA_USER=your_real_ig_username
    export INSTA_PASS=your_real_ig_password
    ~/igtracker/bin/python ig_tracker.py
    -> open http://127.0.0.1:5000

Notes:
  - Use a DEDICATED account, NO 2FA, no security checkpoint.
  - First successful login saves a session to ~/.config/instaloader/ and reuses it
    on restart (fewer logins = fewer blocks).
  - If you see "Please wait a few minutes" errors: wait 5-10 min, restart, and
    lower MAX_* caps (e.g. MAX_FOLLOWING=10 MAX_FOLLOWERS=5).
  - Binds to 127.0.0.1 by default. To expose on LAN set HOST=0.0.0.0 AND
    API_TOKEN=some-secret (otherwise anyone on the network can drive your session).
"""

import base64
import os
import re
import secrets
import sys
import threading
import time

import instaloader
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# ---------- HACKER ASCII ART (printed at startup + shown on the site) ----------
HACKER_ART = r"""
      _          _                          _             _
  ___| |__   ___| |_ __ _ _ __   __ _ _ __ | |_ ___ _ __ / |
 / __| '_ \ / _ \ __/ _` | '_ \ / _` | '_ \| __/ _ \ '__| | |
| (__| | | |  __/ || (_| | | | | (_| | |_) | ||  __/ |   | | |
 \___|_| |_|\___|\__\__,_|_| |_|\__,_| .__/ \__\___|_|   |_|
                                     |_|
         I N S T A G R A M   A C T I V I T Y   T R A C K E R

         Created by @kunalkharat//
"""

# ---------- Configuration ----------
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 5000))
CACHE_TTL = int(os.environ.get("CACHE_TTL", 600))        # seconds to cache a profile
MAX_POSTS = int(os.environ.get("MAX_POSTS", 6))          # recent posts to analyze
MAX_FOLLOWING = int(os.environ.get("MAX_FOLLOWING", 25)) # real followees cap (LOW = fewer blocks)
MAX_FOLLOWERS = int(os.environ.get("MAX_FOLLOWERS", 15)) # real followers cap
MAX_COMMENTERS = int(os.environ.get("MAX_COMMENTERS", 15)) # real commenters cap
MAX_TAGGED = int(os.environ.get("MAX_TAGGED", 5))        # real tagged posts cap
API_TOKEN = os.environ.get("API_TOKEN", "").strip()      # optional; if set, /api/track needs ?token=
INSTA_USER = os.environ.get("INSTA_USER", "").strip()
INSTA_PASS = os.environ.get("INSTA_PASS", "")

# ---------- MANDATORY login check (Instagram blocks anonymous scraping) ----------
if not (INSTA_USER and INSTA_PASS):
    print(HACKER_ART)
    print("[!] FATAL: Instagram now requires login for follow/follower/comment/tagged data.")
    print("[!] Without login, those sections show 'no public data' because Instagram")
    print("[!] BLOCKS the queries (Login required / 401 Unauthorized).")
    print("[!]")
    print("[!] Fix - run with real credentials:")
    print("[!]     export INSTA_USER=your_real_ig_username")
    print("[!]     export INSTA_PASS=your_real_ig_password")
    print("[!]     python ig_tracker.py")
    print("[!]")
    print("[!] Use a dedicated account WITHOUT 2FA / security checkpoint.")
    sys.exit(1)

# ---------- Loader (single shared instance, session-reusing) ----------
_loader = None
_loader_lock = threading.Lock()

def get_loader():
    """Build one instaloader instance; reuse saved session, else login (saves session)."""
    global _loader
    with _loader_lock:
        if _loader is None:
            L = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                post_metadata_txt_pattern="",
                quiet=True,
                max_connection_attempts=3,
            )
            try:
                L.load_session_from_file(INSTA_USER)  # reuse ~/.config/instaloader/session-<user>
                print("[*] Reused saved session for", INSTA_USER)
            except Exception:
                print("[*] Logging into Instagram as", INSTA_USER, "...")
                try:
                    L.login(INSTA_USER, INSTA_PASS)    # auto-saves session file
                    print("[*] Login OK - session saved for reuse")
                except instaloader.TwoFactorAuthRequiredException:
                    print("[!] 2FA is enabled on that account - instaloader cannot complete 2FA login.")
                    print("[!] Create a dedicated account WITHOUT 2FA.")
                    sys.exit(1)
                except instaloader.BadCredentialsException:
                    print("[!] Wrong username or password.")
                    sys.exit(1)
                except instaloader.ConnectionException as e:
                    print("[!] Instagram blocked/rate-limited the login:", e)
                    print("[!] Wait 10-15 minutes and try again.")
                    sys.exit(1)
            _loader = L
        return _loader

# ---------- Instaloader is NOT thread-safe: serialize all scans ----------
_scan_lock = threading.Lock()

# ---------- Simple in-memory cache (avoid hammering Instagram) ----------
_cache = {}
_cache_lock = threading.Lock()

def cache_get(username):
    with _cache_lock:
        entry = _cache.get(username.lower())
        if entry and (time.time() - entry[0]) < CACHE_TTL:
            return entry[1]
    return None

def cache_set(username, payload):
    with _cache_lock:
        _cache[username.lower()] = (time.time(), payload)

# ---------- Real data fetching ----------
USERNAME_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")

def _to_base64(url):
    """Embed profile pic directly so it always renders."""
    if not url:
        return None
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        ctype = r.headers.get("Content-Type") or "image/jpeg"
        return "data:" + ctype + ";base64," + base64.b64encode(r.content).decode()
    except Exception:
        return url  # fall back to the raw CDN link

def _safe_full_name(profile_obj):
    """full_name can require a network call; never let it crash the scan."""
    try:
        return profile_obj.full_name or ""
    except Exception:
        return ""

def _utc_iso(dt):
    """Clean ISO-8601 UTC string ('2024-01-01T00:00:00Z'), not '+00:00Z'."""
    return dt.replace(tzinfo=None).isoformat() + "Z"

def _with_retry(fn, label, errors, tries=3, base_delay=8.0):
    """Run a collection function; retry with backoff on Instagram throttling."""
    last = None
    for attempt in range(tries):
        try:
            fn()
            return
        except Exception as e:
            last = e
            if attempt < tries - 1:
                time.sleep(base_delay * (attempt + 1))
    errors.append("%s: %s" % (label, last))

# NOTE: each _collect_* resets its own list first so a retry after a
# mid-iteration failure cannot produce duplicates or overrun MAX_* caps.
def _collect_followees(profile, social):
    social["followees"] = []
    for f in profile.get_followees():
        social["followees"].append({
            "username": f.username,
            "full_name": _safe_full_name(f),
            "is_verified": f.is_verified,
            "is_private": f.is_private,
            "pic": f.profile_pic_url,
        })
        if len(social["followees"]) >= MAX_FOLLOWING:
            break

def _collect_followers(profile, social):
    social["followers"] = []
    for f in profile.get_followers():
        social["followers"].append({
            "username": f.username,
            "full_name": _safe_full_name(f),
            "is_verified": f.is_verified,
            "is_private": f.is_private,
            "pic": f.profile_pic_url,
        })
        if len(social["followers"]) >= MAX_FOLLOWERS:
            break

def _collect_commenters(profile, posts, social):
    social["commenters"] = []
    seen = set()
    for p in posts:
        for c in p.get_comments():
            if c.owner.username in seen:
                continue
            seen.add(c.owner.username)
            social["commenters"].append({
                "username": c.owner.username,
                "full_name": _safe_full_name(c.owner),
                "comment": c.text[:200],
                "date_utc": _utc_iso(c.created_at_utc),
                "timestamp": int(c.created_at_utc.timestamp()),
                "post_url": "https://www.instagram.com/p/%s/" % p.shortcode,
            })
            if len(social["commenters"]) >= MAX_COMMENTERS:
                return

def _collect_tagged(profile, social):
    social["tagged"] = []
    for tp in profile.get_tagged_posts():
        social["tagged"].append({
            "username": tp.owner.username,
            "full_name": _safe_full_name(tp.owner),
            "caption": (tp.caption or "")[:200],
            "date_utc": _utc_iso(tp.date_utc),
            "timestamp": int(tp.date_utc.timestamp()),
            "shortcode": tp.shortcode,
            "url": "https://www.instagram.com/p/%s/" % tp.shortcode,
        })
        if len(social["tagged"]) >= MAX_TAGGED:
            return

def fetch_profile(username):
    """Serialize scans: instaloader's shared context is not thread-safe."""
    with _scan_lock:
        return _fetch_profile_unlocked(username)

def _fetch_profile_unlocked(username):
    """Pull REAL profile + REAL interaction data straight from Instagram."""
    loader = get_loader()
    profile = instaloader.Profile.from_username(loader.context, username)

    data = {
        "username": profile.username,
        "full_name": profile.full_name,
        "biography": profile.biography,
        "external_url": profile.external_url,
        "followers": profile.followers,
        "following": profile.followees,
        "posts_count": profile.mediacount,
        "is_private": profile.is_private,
        "is_verified": profile.is_verified,
        "is_business": profile.is_business_account,
        "business_category": profile.business_category_name,
        "profile_pic": _to_base64(profile.profile_pic_url),
        "profile_pic_url": profile.profile_pic_url,
    }

    # --- Real activity: actual posts with real timestamps + engagement ---
    activity = {"recent_posts": [], "last_post": None, "last_post_ts": None, "avg_gap_days": None}
    posts = []
    try:
        for post in profile.get_posts():
            posts.append(post)
            if len(posts) >= MAX_POSTS:
                break
        if posts:
            posts.reverse()  # oldest -> newest for gap math
            for p in posts:
                activity["recent_posts"].append({
                    "date_utc": _utc_iso(p.date_utc),
                    "timestamp": int(p.date_utc.timestamp()),
                    "likes": p.likes,
                    "comments": p.comments,
                    "caption": (p.caption or "")[:220],
                    "shortcode": p.shortcode,
                    "url": "https://www.instagram.com/p/%s/" % p.shortcode,
                    "thumb": p.url,
                })
            activity["last_post"] = _utc_iso(posts[-1].date_utc)
            activity["last_post_ts"] = int(posts[-1].date_utc.timestamp())
            if len(posts) > 1:
                gaps = [(posts[i].date_utc - posts[i - 1].date_utc).total_seconds() / 86400.0
                        for i in range(1, len(posts))]
                activity["avg_gap_days"] = round(sum(gaps) / len(gaps), 2)
    except instaloader.PrivateProfileNotFollowedException:
        activity["error"] = "private"
    except instaloader.QueryReturnedBadRequestException:
        activity["error"] = "rate_limited"

    data["activity"] = activity

    # --- Real SOCIAL INTERACTION data (login REQUIRED by Instagram) ---
    social = {"followees": [], "followers": [], "commenters": [], "tagged": [],
              "errors": [], "private": profile.is_private, "logged_in": True}

    if not profile.is_private:
        _with_retry(lambda: _collect_followees(profile, social), "followees", social["errors"])
        time.sleep(REQUEST_DELAY)
        _with_retry(lambda: _collect_followers(profile, social), "followers", social["errors"])
        time.sleep(REQUEST_DELAY)
        _with_retry(lambda: _collect_commenters(profile, posts, social), "commenters", social["errors"])
        time.sleep(REQUEST_DELAY)
        _with_retry(lambda: _collect_tagged(profile, social), "tagged", social["errors"])

    data["social"] = social
    return data

# ---------- Routes ----------
def _check_token():
    """If API_TOKEN is set, require ?token= on every API call."""
    if not API_TOKEN:
        return None
    tok = request.args.get("token", "")
    if secrets.compare_digest(tok, API_TOKEN):
        return None
    return jsonify({"error": "missing or invalid API token (set API_TOKEN to enable auth)"}), 401

@app.route("/")
def index():
    return render_template_string(PAGE, hacker_art=HACKER_ART)

@app.route("/api/track")
def api_track():
    denied = _check_token()
    if denied:
        return denied

    username = request.args.get("username", "").strip().lstrip("@")
    if not username:
        return jsonify({"error": "Enter an Instagram username"}), 400
    if not USERNAME_RE.match(username):
        return jsonify({"error": "Invalid username format"}), 400

    cached = cache_get(username)
    if cached:
        return jsonify({"ok": True, "cached": True, "profile": cached})

    try:
        payload = fetch_profile(username)
        cache_set(username, payload)
        return jsonify({"ok": True, "cached": False, "profile": payload})
    except instaloader.ProfileNotExistsException:
        return jsonify({"error": "@%s does not exist on Instagram" % username}), 404
    except instaloader.ConnectionException as e:
        return jsonify({"error": "Rate-limited or connection error from Instagram: %s" % e}), 429
    except Exception as e:
        return jsonify({"error": "Unexpected error: %s" % e}), 500

# ---------- Frontend (hacker-terminal theme + matrix rain background) ----------
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IG TRACKER // Instagram Activity Tracker</title>
<style>
  :root { --green:#00ff66; --dim:#1d7a44; --red:#ff3b30; --bg:#050a06; }
  * { box-sizing:border-box; margin:0; padding:0; }
  html,body { height:100%; }
  body { background:var(--bg); color:var(--green); font-family:'Courier New',Consolas,monospace; min-height:100vh; overflow-x:hidden; }
  /* ---------- MATRIX RAIN BACKGROUND (behind everything) ---------- */
  #matrix { position:fixed; inset:0; z-index:0; pointer-events:none; }
  #glow { position:fixed; inset:0; z-index:1; background:rgba(5,10,6,.62); pointer-events:none; }
  .wrap { position:relative; z-index:2; max-width:920px; margin:0 auto; padding:24px 16px 60px; }
  pre.art { color:var(--green); font-size:12px; line-height:1.1; overflow-x:auto; text-shadow:0 0 8px rgba(0,255,102,.5); }
  h1 { font-size:14px; letter-spacing:2px; color:var(--dim); margin:8px 0 18px; }
  .panel { border:1px solid var(--dim); padding:16px; background:rgba(0,255,102,.04); }
  form { display:flex; gap:8px; flex-wrap:wrap; }
  input { flex:1; min-width:220px; background:rgba(0,0,0,.85); color:var(--green); border:1px solid var(--dim); padding:12px; font-family:inherit; font-size:15px; outline:none; }
  input:focus { border-color:var(--green); box-shadow:0 0 10px rgba(0,255,102,.25); }
  button { background:var(--green); color:#000; border:0; padding:12px 22px; font-family:inherit; font-weight:bold; cursor:pointer; letter-spacing:1px; }
  button:hover { background:#33ff85; }
  #status { margin:14px 0; min-height:20px; }
  #status.scan { animation:blink 1s infinite; }
  @keyframes blink { 50% { opacity:.35; } }
  .card { display:none; margin-top:20px; }
  .card.on { display:block; }
  .head { display:flex; gap:16px; align-items:center; border:1px solid var(--dim); padding:16px; background:rgba(0,255,102,.04); flex-wrap:wrap; }
  .head img { width:90px; height:90px; border:1px solid var(--dim); border-radius:50%; background:#000; }
  .head .name { font-size:22px; font-weight:bold; }
  .head .user { color:var(--dim); }
  .badge { display:inline-block; border:1px solid var(--green); padding:2px 8px; margin:4px 6px 0 0; font-size:11px; letter-spacing:1px; }
  .badge.red { border-color:var(--red); color:var(--red); }
  .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin-top:14px; }
  .stat { border:1px solid var(--dim); padding:12px; text-align:center; background:rgba(0,255,102,.03); }
  .stat b { display:block; font-size:20px; }
  .stat span { color:var(--dim); font-size:11px; letter-spacing:1px; }
  h2 { font-size:13px; letter-spacing:2px; color:var(--dim); margin:24px 0 10px; border-bottom:1px solid var(--dim); padding-bottom:6px; }
  .bio { margin-top:14px; border:1px solid var(--dim); padding:12px; background:rgba(0,255,102,.03); white-space:pre-wrap; word-break:break-word; }
  table { width:100%; border-collapse:collapse; font-size:13px; background:rgba(0,0,0,.4); }
  td, th { border:1px solid var(--dim); padding:8px 10px; text-align:left; }
  th { color:var(--dim); font-size:11px; letter-spacing:1px; }
  td a { color:var(--green); }
  .err { color:var(--red); border:1px solid var(--red); padding:12px; margin-top:14px; display:none; background:rgba(0,0,0,.4); }
  .meta { color:var(--dim); font-size:12px; margin-top:10px; }
  .warn { color:#ffcc00; border:1px solid #ffcc00; padding:10px; font-size:12px; margin-top:8px; word-break:break-word; background:rgba(0,0,0,.4); }
  .chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }
  .chip { display:inline-flex; align-items:center; gap:8px; border:1px solid var(--dim); padding:6px 10px; text-decoration:none; color:var(--green); font-size:12px; background:rgba(0,255,102,.05); }
  .chip:hover { border-color:var(--green); }
  .chip img { width:26px; height:26px; border-radius:50%; object-fit:cover; background:#000; }
  .chip .v { color:var(--green); font-size:11px; }
  .foot { margin-top:30px; color:var(--dim); font-size:11px; line-height:1.6; border-top:1px solid var(--dim); padding-top:12px; }
  ::selection { background:var(--green); color:#000; }
</style>
</head>
<body>
<!-- MATRIX RAIN CANVAS (dark green binary rain) -->
<canvas id="matrix"></canvas>
<div id="glow"></div>

<div class="wrap">
  <pre class="art">{{ hacker_art }}</pre>
  <h1>Instagram Activity Hi-Jacking</h1>
  <div class="panel">
    <form id="f">
      <input id="u" type="text" placeholder="Enter Instagram Username" autocomplete="off" spellcheck="false">
      <button type="submit">TRACK</button>
    </form>
    <div id="status">[*] system ready. enter a username to begin reconnaissance.</div>
  </div>
  <div class="err" id="err"></div>
  <div class="card" id="card">
    <div class="head">
      <img id="pp" alt="profile pic">
      <div>
        <div class="name"><span id="fn"></span></div>
        <div class="user">@<span id="un"></span></div>
        <div>
          <span class="badge" id="bPub" style="display:none">PUBLIC</span>
          <span class="badge red" id="bPriv" style="display:none">PRIVATE</span>
          <span class="badge" id="bVer" style="display:none">VERIFIED</span>
          <span class="badge" id="bBiz" style="display:none">BUSINESS</span>
        </div>
      </div>
    </div>
    <div class="bio" id="bio"></div>
    <div class="stats">
      <div class="stat"><b id="sFoll">-</b><span>FOLLOWERS</span></div>
      <div class="stat"><b id="sFing">-</b><span>FOLLOWING</span></div>
      <div class="stat"><b id="sPost">-</b><span>POSTS</span></div>
      <div class="stat"><b id="sLast">-</b><span>LAST POST</span></div>
      <div class="stat"><b id="sGap">-</b><span>AVG GAP (DAYS)</span></div>
    </div>
    <h2>// RECENT ACTIVITY - REAL POST TIMESTAMPS &amp; ENGAGEMENT</h2>
    <div id="posts"></div>
    <h2>// INTERACTION MAP - WHO THEY FOLLOW (REAL)</h2>
    <div id="followees" class="chips"></div>
    <h2>// FOLLOWER SAMPLE (REAL)</h2>
    <div id="followers" class="chips"></div>
    <h2>// WHO COMMENTS ON THEIR POSTS (REAL)</h2>
    <div id="commenters"></div>
    <h2>// RECENTLY TAGGED POSTS (REAL)</h2>
    <div id="tagged"></div>
    <p class="meta" id="meta"></p>
  </div>
  <div class="foot">
   PRIVACY LIMITS: Instagram does NOT expose private DMs, like history, or "online now" status. No tool can access those.
   PUBLIC DATA (fetched live with a logged-in session): profile stats, post history, follow list, follower list, commenters,
   tagged posts. Instagram BLOCKS these queries anonymously - login (INSTA_USER/INSTA_PASS) is mandatory. Sessions are saved
   and reused. If a section fails with "Please wait a few minutes", Instagram throttled your IP: wait 5-10 min, restart, and
   lower MAX_* caps (e.g. MAX_FOLLOWING=10 MAX_FOLLOWERS=5 MAX_TAGGED=3 python ig_tracker.py). Every entry shown is real.
   Runs on 127.0.0.1 by default; set HOST=0.0.0.0 to expose on LAN and API_TOKEN=secret to protect the API.
  </div>
</div>

<script>
// ================= MATRIX RAIN (dark green binary) =================
(function(){
  var cv=document.getElementById('matrix'), x=cv.getContext('2d');
  var W,H,cols,drops;
  function size(){
    W=cv.width=innerWidth; H=cv.height=innerHeight;
    cols=Math.floor(W/14);
    drops=[];
    for(var i=0;i<cols;i++) drops.push(Math.floor(Math.random()*-40));
  }
  size(); window.addEventListener('resize',size);
  var chars=('01'+'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン').split('');
  setInterval(function(){
    x.fillStyle='rgba(5,10,6,0.10)'; x.fillRect(0,0,W,H);
    x.font='14px monospace';
    for(var i=0;i<cols;i++){
      var ch=chars[Math.floor(Math.random()*chars.length)];
      x.fillStyle=(Math.random()>0.975)?'#ccffdd':'#00ff66';  // occasional bright flash
      x.fillText(ch,i*14,drops[i]*14);
      if(drops[i]*14>H && Math.random()>0.975) drops[i]=0;
      drops[i]++;
    }
  },50);
})();

// ================= TRACKER LOGIC =================
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmtNum(n){ return (n||0).toLocaleString('en-US'); }
function rel(t){
  if(!isFinite(t)) return '?';          // guard against NaN / invalid input
  var s=(Date.now()/1000)-t; if(s<0)s=0;
  if(s<3600) return Math.floor(s/60)+'m ago';
  if(s<86400) return Math.floor(s/3600)+'h ago';
  if(s<2592000) return Math.floor(s/86400)+'d ago';
  return new Date(t*1000).toISOString().slice(0,10);
}
function findErr(errs,key){ return (errs||[]).filter(function(e){ return e.indexOf(key)===0; }).join(' | '); }
function chips(list){
  if(!list || !list.length) return '';
  return list.map(function(x){
    var pic=x.pic?'<img src="'+esc(x.pic)+'" onerror="this.style.display=\'none\'">':'';
    var v=x.is_verified?' <span class="v">[VERIFIED]</span>':'';
    var nm=x.full_name?' ('+esc(x.full_name)+')':'';
    return '<a class="chip" target="_blank" rel="noopener" href="https://www.instagram.com/'+encodeURIComponent(x.username)+'">'+
           pic+'<span>@'+esc(x.username)+nm+'</span>'+v+'</a>';
  }).join('');
}
document.getElementById('f').addEventListener('submit', function(e){
  e.preventDefault();
  var u=document.getElementById('u').value.trim().replace(/^@/,'');
  var st=document.getElementById('status'), err=document.getElementById('err'), card=document.getElementById('card');
  if(!u){ st.textContent='[!] enter a username first.'; return; }
  err.style.display='none'; card.classList.remove('on');
  st.className='scan'; st.textContent='[*] scanning profile + interactions for @'+u+' ... (20-60s for big accounts)';
  fetch('/api/track?username='+encodeURIComponent(u))
    .then(function(r){ return r.json().then(function(j){ return {ok:r.ok, j:j}; }); })
    .then(function(res){
      st.className='';
      if(!res.ok){ err.textContent='[!] '+res.j.error; err.style.display='block'; return; }
      var p=res.j.profile, a=p.activity||{}, s=p.social||{};
      document.getElementById('pp').src=p.profile_pic||'';
      document.getElementById('fn').textContent=p.full_name||'';
      document.getElementById('un').textContent=p.username;
      document.getElementById('bPub').style.display=p.is_private?'none':'inline-block';
      document.getElementById('bPriv').style.display=p.is_private?'inline-block':'none';
      document.getElementById('bVer').style.display=p.is_verified?'inline-block':'none';
      document.getElementById('bBiz').style.display=p.is_business?'inline-block':'none';
      document.getElementById('bio').textContent=p.biography||'(no bio)';
      document.getElementById('sFoll').textContent=fmtNum(p.followers);
      document.getElementById('sFing').textContent=fmtNum(p.following);
      document.getElementById('sPost').textContent=fmtNum(p.posts_count);
      document.getElementById('sLast').textContent=(a.last_post_ts!==undefined&&a.last_post_ts!==null)?rel(a.last_post_ts):'n/a';
      document.getElementById('sGap').textContent=(a.avg_gap_days!==null&&a.avg_gap_days!==undefined)?a.avg_gap_days:'n/a';
      var box=document.getElementById('posts');
      if(a.error==='private'){
        box.innerHTML='<p>private account - posts hidden from public.</p>';
      } else if(a.error==='rate_limited'){
        box.innerHTML='<div class="warn">[!] instagram rate-limited the post query. wait 5-10 min, then retry.</div>';
      } else if(!a.recent_posts.length){
        box.innerHTML='<p>no public posts found.</p>';
      } else {
        var h='<table><tr><th>POSTED (UTC)</th><th>WHEN</th><th>LIKES</th><th>COMMENTS</th><th>CAPTION</th><th>LINK</th></tr>';
        a.recent_posts.slice().reverse().forEach(function(x){
          var c=esc(x.caption||'-').slice(0,120);
          h+='<tr><td>'+new Date(x.timestamp*1000).toISOString().replace('T',' ').slice(0,16)+'</td>'+
             '<td>'+rel(x.timestamp)+'</td><td>'+fmtNum(x.likes)+'</td><td>'+fmtNum(x.comments)+'</td>'+
             '<td>'+c+'</td><td><a target="_blank" rel="noopener" href="'+x.url+'">view</a></td></tr>';
        });
        h+='</table>'; box.innerHTML=h;
      }
      // --- FOLLOWEES: real data, exact error reason ---
      var fe=document.getElementById('followees');
      if(s.private){ fe.innerHTML='<p>private account - follow list hidden by instagram.</p>'; }
      else if(s.followees&&s.followees.length){ fe.innerHTML=chips(s.followees); }
      else { var e1=findErr(s.errors,'followees'); fe.innerHTML=e1?'<div class="warn">[!] '+esc(e1)+'<br>Fix: wait a few minutes + lower MAX_FOLLOWING, then retry.</div>':'<p>no public data available.</p>'; }
      // --- FOLLOWERS ---
      var fl=document.getElementById('followers');
      if(s.private){ fl.innerHTML='<p>private account - follower list hidden by instagram.</p>'; }
      else if(s.followers&&s.followers.length){ fl.innerHTML=chips(s.followers); }
      else { var e2=findErr(s.errors,'followers'); fl.innerHTML=e2?'<div class="warn">[!] '+esc(e2)+'<br>Fix: wait a few minutes + lower MAX_FOLLOWERS, then retry.</div>':'<p>no public data available.</p>'; }
      // --- COMMENTERS ---
      var cb=document.getElementById('commenters');
      if(s.private){ cb.innerHTML='<p>private account - comments not public.</p>'; }
      else if(s.commenters&&s.commenters.length){
        var ch='<table><tr><th>USER</th><th>COMMENT</th><th>WHEN</th><th>ON POST</th></tr>';
        s.commenters.forEach(function(x){
          ch+='<tr><td><a target="_blank" rel="noopener" href="https://www.instagram.com/'+encodeURIComponent(x.username)+'">@'+esc(x.username)+'</a></td>'+
              '<td>'+esc(x.comment)+'</td><td>'+rel(x.timestamp)+'</td>'+
              '<td><a target="_blank" rel="noopener" href="'+x.post_url+'">view</a></td></tr>';
        });
        ch+='</table>'; cb.innerHTML=ch;
      } else { var e3=findErr(s.errors,'commenters'); cb.innerHTML=e3?'<div class="warn">[!] '+esc(e3)+'</div>':'<p>no public comments found.</p>'; }
      // --- TAGGED POSTS ---
      var tb=document.getElementById('tagged');
      if(s.private){ tb.innerHTML='<p>private account - tagged posts not public.</p>'; }
      else if(s.tagged&&s.tagged.length){
        var th='<table><tr><th>TAGGED BY</th><th>WHEN</th><th>CAPTION</th><th>LINK</th></tr>';
        s.tagged.forEach(function(x){
          th+='<tr><td><a target="_blank" rel="noopener" href="https://www.instagram.com/'+encodeURIComponent(x.username)+'">@'+esc(x.username)+'</a></td>'+
              '<td>'+rel(x.timestamp)+'</td><td>'+esc(x.caption||'-').slice(0,100)+'</td>'+
              '<td><a target="_blank" rel="noopener" href="'+x.url+'">view</a></td></tr>';
        });
        th+='</table>'; tb.innerHTML=th;
      } else { var e4=findErr(s.errors,'tagged'); tb.innerHTML=e4?'<div class="warn">[!] '+esc(e4)+'<br>Fix: wait 5-10 min for the IP block to lift, then retry.</div>':'<p>no public tagged posts found.</p>'; }
      var errs=(s.errors||[]).length?' <span class="meta">[partial: '+esc(s.errors.join(' | '))+' ]</span>':'';
      document.getElementById('meta').innerHTML=(res.j.cached?'[data served from cache]':'[data fetched live from instagram]')+errs;
      card.classList.add('on');
    })
    .catch(function(e2){ st.className=''; err.textContent='[!] request failed: '+e2; err.style.display='block'; });
});
</script>
</body>
</html>"""

if __name__ == "__main__":
    print(HACKER_ART)
    print("[*] IG TRACKER online -> http://%s:%d" % (HOST, PORT))
    print("[*] Logged in as:", INSTA_USER)
    print("[*] Caps: followees(%d) followers(%d) commenters(%d) tagged(%d)"
          % (MAX_FOLLOWING, MAX_FOLLOWERS, MAX_COMMENTERS, MAX_TAGGED))
    if API_TOKEN:
        print("[*] API token protection: ENABLED (pass ?token=... to /api/track)")
    if HOST != "127.0.0.1":
        print("[!] Listening on %s - anyone on the network can reach this. Use API_TOKEN!" % HOST)
    app.run(host=HOST, port=PORT, debug=False)
