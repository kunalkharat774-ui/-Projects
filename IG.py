#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IG TRACKER - Instagram User Activity Tracker (single file)
Fetches REAL public Instagram data live via instaloader. No mock data.

Install:
    pip install flask instaloader requests

Run:
    python ig_tracker.py
    -> open http://127.0.0.1:5000

Optional (reduces Instagram rate limits / enables extra data):
    export INSTA_USER=your_instagram_username
    export INSTA_PASS=your_instagram_password
"""

import base64
import os
import re
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
         Created by @kunalkharat//
"""

# ---------- Configuration ----------
PORT = int(os.environ.get("PORT", 5000))
CACHE_TTL = int(os.environ.get("CACHE_TTL", 600))        # seconds to cache a profile
MAX_POSTS = int(os.environ.get("MAX_POSTS", 6))          # recent posts to analyze
MAX_FOLLOWING = int(os.environ.get("MAX_FOLLOWING", 25)) # real followees to fetch (cap)
MAX_FOLLOWERS = int(os.environ.get("MAX_FOLLOWERS", 15)) # real followers to fetch (cap)
MAX_COMMENTERS = int(os.environ.get("MAX_COMMENTERS", 15)) # real commenters to fetch
MAX_TAGGED = int(os.environ.get("MAX_TAGGED", 5))        # real tagged posts to fetch
INSTA_USER = os.environ.get("INSTA_USER", "")            # optional: real IG login
INSTA_PASS = os.environ.get("INSTA_PASS", "")

# ---------- Loader (single shared instance, thread-safe) ----------
_loader = None
_loader_lock = threading.Lock()

def get_loader():
    """Build one instaloader instance; login if credentials provided."""
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
            )
            if INSTA_USER and INSTA_PASS:
                try:
                    L.login(INSTA_USER, INSTA_PASS)
                    print("[*] Logged into Instagram as", INSTA_USER)
                except Exception as e:
                    print("[!] Login failed, continuing anonymous:", e)
            _loader = L
        return _loader

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

def fetch_profile(username):
    """Pull REAL profile + REAL interaction data straight from Instagram."""
    loader = get_loader()
    profile = instaloader.Profile.from_username(loader.context, username)

    data = {
        "username": profile.username,
        "full_name": _safe_full_name(profile),
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
    activity = {"recent_posts": [], "last_post": None, "avg_gap_days": None}
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
                    "date_utc": p.date_utc.isoformat() + "Z",
                    "timestamp": int(p.date_utc.timestamp()),
                    "likes": p.likes,
                    "comments": p.comments,
                    "caption": (p.caption or "")[:220],
                    "shortcode": p.shortcode,
                    "url": "https://www.instagram.com/p/%s/" % p.shortcode,
                    "thumb": p.url,
                })
            activity["last_post"] = posts[-1].date_utc.isoformat() + "Z"
            if len(posts) > 1:
                gaps = [(posts[i].date_utc - posts[i - 1].date_utc).total_seconds() / 86400.0
                        for i in range(1, len(posts))]
                activity["avg_gap_days"] = round(sum(gaps) / len(gaps), 2)
    except instaloader.PrivateProfileNotFollowedException:
        activity["error"] = "private"
    except instaloader.QueryReturnedBadRequestException:
        activity["error"] = "rate_limited"

    data["activity"] = activity

    # --- Real SOCIAL INTERACTION data (only what Instagram makes public) ---
    social = {"followees": [], "followers": [], "commenters": [], "tagged": [],
              "errors": [], "private": profile.is_private}

    if not profile.is_private:
        # 1) Who the user follows (real followees)
        try:
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
        except Exception as e:
            social["errors"].append("followees: %s" % e)

        # 2) Real follower sample
        try:
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
        except Exception as e:
            social["errors"].append("followers: %s" % e)

        # 3) Who comments on their posts (real commenters, deduped)
        try:
            seen_users = set()
            for p in posts:
                for c in p.get_comments():
                    if c.owner.username in seen_users:
                        continue
                    seen_users.add(c.owner.username)
                    social["commenters"].append({
                        "username": c.owner.username,
                        "full_name": _safe_full_name(c.owner),
                        "comment": c.text[:200],
                        "date_utc": c.created_at_utc.isoformat() + "Z",
                        "timestamp": int(c.created_at_utc.timestamp()),
                        "post_url": "https://www.instagram.com/p/%s/" % p.shortcode,
                    })
                    if len(social["commenters"]) >= MAX_COMMENTERS:
                        break
                if len(social["commenters"]) >= MAX_COMMENTERS:
                    break
        except Exception as e:
            social["errors"].append("commenters: %s" % e)

        # 4) Who tags them (real tagged posts)
        try:
            for tp in profile.get_tagged_posts():
                owner_name = getattr(tp, 'owner', None)
                if owner_name:
                    owner_name = getattr(owner_name, 'username', 'unknown')
                else:
                    owner_name = 'unknown'
                social["tagged"].append({
                    "username": owner_name,
                    "caption": (tp.caption or "")[:200],
                    "date_utc": tp.date_utc.isoformat() + "Z",
                    "timestamp": int(tp.date_utc.timestamp()),
                    "shortcode": tp.shortcode,
                    "url": "https://www.instagram.com/p/%s/" % tp.shortcode,
                })
                if len(social["tagged"]) >= MAX_TAGGED:
                    break
        except Exception as e:
            social["errors"].append("tagged: %s" % e)

    data["social"] = social
    return data

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template_string(PAGE, hacker_art=HACKER_ART)

@app.route("/api/track")
def api_track():
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

# ---------- Frontend (hacker-terminal theme) ----------
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IG TRACKER // Instagram Activity Tracker</title>
<style>
  :root { --green:#00ff66; --dim:#1d7a44; --red:#ff3b30; --bg:#050a06; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); color:var(--green); font-family:'Courier New',Consolas,monospace; min-height:100vh; }
  .wrap { max-width:920px; margin:0 auto; padding:24px 16px 60px; }
  pre.art { color:var(--green); font-size:12px; line-height:1.1; overflow-x:auto; text-shadow:0 0 8px rgba(0,255,102,.5); }
  h1 { font-size:14px; letter-spacing:2px; color:var(--dim); margin:8px 0 18px; }
  .panel { border:1px solid var(--dim); padding:16px; background:rgba(0,255,102,.03); }
  form { display:flex; gap:8px; flex-wrap:wrap; }
  input { flex:1; min-width:220px; background:#000; color:var(--green); border:1px solid var(--dim); padding:12px; font-family:inherit; font-size:15px; outline:none; }
  input:focus { border-color:var(--green); box-shadow:0 0 10px rgba(0,255,102,.25); }
  button { background:var(--green); color:#000; border:0; padding:12px 22px; font-family:inherit; font-weight:bold; cursor:pointer; letter-spacing:1px; }
  button:hover { background:#33ff85; }
  #status { margin:14px 0; min-height:20px; }
  #status.scan { animation:blink 1s infinite; }
  @keyframes blink { 50% { opacity:.35; } }
  .card { display:none; margin-top:20px; }
  .card.on { display:block; }
  .head { display:flex; gap:16px; align-items:center; border:1px solid var(--dim); padding:16px; flex-wrap:wrap; }
  .head img { width:90px; height:90px; border:1px solid var(--dim); border-radius:50%; background:#000; }
  .head .name { font-size:22px; font-weight:bold; }
  .head .user { color:var(--dim); }
  .badge { display:inline-block; border:1px solid var(--green); padding:2px 8px; margin:4px 6px 0 0; font-size:11px; letter-spacing:1px; }
  .badge.red { border-color:var(--red); color:var(--red); }
  .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin-top:14px; }
  .stat { border:1px solid var(--dim); padding:12px; text-align:center; }
  .stat b { display:block; font-size:20px; }
  .stat span { color:var(--dim); font-size:11px; letter-spacing:1px; }
  h2 { font-size:13px; letter-spacing:2px; color:var(--dim); margin:24px 0 10px; border-bottom:1px solid var(--dim); padding-bottom:6px; }
  .bio { margin-top:14px; border:1px solid var(--dim); padding:12px; white-space:pre-wrap; word-break:break-word; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  td, th { border:1px solid var(--dim); padding:8px 10px; text-align:left; }
  th { color:var(--dim); font-size:11px; letter-spacing:1px; }
  td a { color:var(--green); }
  .err { color:var(--red); border:1px solid var(--red); padding:12px; margin-top:14px; display:none; }
  .meta { color:var(--dim); font-size:12px; margin-top:10px; }
  .chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }
  .chip { display:inline-flex; align-items:center; gap:8px; border:1px solid var(--dim); padding:6px 10px; text-decoration:none; color:var(--green); font-size:12px; background:rgba(0,255,102,.03); }
  .chip:hover { border-color:var(--green); }
  .chip img { width:26px; height:26px; border-radius:50%; object-fit:cover; background:#000; }
  .chip .v { color:var(--green); font-size:11px; }
  .foot { margin-top:30px; color:var(--dim); font-size:11px; line-height:1.6; border-top:1px solid var(--dim); padding-top:12px; }
  ::selection { background:var(--green); color:#000; }
</style>
</head>
<body>
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
    <h2> RECENT ACTIVITY:- </h2>
    <div id="posts"></div>
    <h2> INTERACTION MAP - WHO THEY FOLLOW </h2>
    <div id="followees" class="chips"></div>
    <h2> FOLLOWER </h2>
    <div id="followers" class="chips"></div>
    <h2> WHO COMMENTS ON THEIR POSTS </h2>
    <div id="commenters"></div>
    <h2> RECENTLY TAGGED POSTS </h2>
    <div id="tagged"></div>
    <p class="meta" id="meta"></p>
  </div>
  <div class="foot">
   🚨 DISCLAIMER & USAGE NOTE

• PRIVACY LIMITS: 
  Instagram does NOT expose private DMs, like history, or "online now" status. 
  No tool can access this data.

• PUBLIC DATA (Fetched Live):
  - Profile stats & post history (timestamps, likes, comments)
  - Following list & follower sample
  - Commenters on posts & tagged posts

• RATE LIMITS & PERFORMANCE:
  - Anonymous scraping is rate-limited (~200 requests/hour/IP).
  - Export INSTA_USER and INSTA_PASS to use an authenticated session and remove limits.
  - Large accounts take 20–60 seconds to scan as all sections are fetched live.
  </div>
</div>
<script>
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmtNum(n){ return (n||0).toLocaleString('en-US'); }
function rel(t){
  var s=(Date.now()/1000)-t; if(s<0)s=0;
  if(s<3600) return Math.floor(s/60)+'m ago';
  if(s<86400) return Math.floor(s/3600)+'h ago';
  if(s<2592000) return Math.floor(s/86400)+'d ago';
  return new Date(t*1000).toISOString().slice(0,10);
}
function chips(list){
  if(!list || !list.length) return '<p>no public data available.</p>';
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
      document.getElementById('sLast').textContent=a.last_post?rel(new Date(a.last_post).getTime()/1000):'n/a';
      document.getElementById('sGap').textContent=(a.avg_gap_days!==null&&a.avg_gap_days!==undefined)?a.avg_gap_days:'n/a';
      var box=document.getElementById('posts');
      if(a.error==='private' || !a.recent_posts.length){
        box.innerHTML='<p>private account or no public posts available.</p>';
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
      document.getElementById('followees').innerHTML=s.private?'<p>private account - follow list hidden by instagram.</p>':chips(s.followees);
      document.getElementById('followers').innerHTML=s.private?'<p>private account - follower list hidden by instagram.</p>':chips(s.followers);
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
      } else { cb.innerHTML='<p>no public comments found.</p>'; }
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
      } else { tb.innerHTML='<p>no public tagged posts found.</p>'; }
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
    print("[*] IG TRACKER online -> http://127.0.0.1:%d" % PORT)
    print("[*] Interaction scan enabled: followees(%d) followers(%d) commenters(%d) tagged(%d)"
          % (MAX_FOLLOWING, MAX_FOLLOWERS, MAX_COMMENTERS, MAX_TAGGED))
    app.run(host="0.0.0.0", port=PORT, debug=False)