#!/bin/bash

# ============================================================
#  HACKERHUB — 100% Bash Language Badge Fixed for Kali Linux
# ============================================================

set -euo pipefail

# ---------- colors ----------
R='\033[1;31m'; G='\033[1;32m'; Y='\033[1;33m'
B='\033[1;34m'; M='\033[1;35m'; C='\033[1;36m'
W='\033[1;37m'; D='\033[0;37m'; NC='\033[0m'

BASE_DIR="$HOME/hackerhub"
HTML_FILE="$BASE_DIR/index.html"
GITATTR_FILE="$BASE_DIR/.gitattributes"
PORT=8080
BROWSER_CMD=""

# Detect available desktop browser in Kali Linux
for b in xdg-open firefox chromium google-chrome Brave-browser; do
    if command -v "$b" &>/dev/null; then
        BROWSER_CMD="$b"
        break
    fi
done

# ---------- cleanup ----------
cleanup() { 
    echo -e "\n${G}[*]${NC} Shutting down HackerHub..."
    exit 0 
}
trap cleanup SIGINT SIGTERM

# ---------- ensure dir ----------
mkdir -p "$BASE_DIR"

# ============================================================
#  GENERATE .gitattributes (For 100% Bash Language Badge on GitHub)
# ============================================================
generate_gitattributes() {
cat > "$GITATTR_FILE" << 'ATTRTOF'
index.html linguist-vendored=true
ATTRTOF
}

# ============================================================
#  GENERATE HTML (FreeFire Quiz + FakeTube)
# ============================================================
generate_html() {
cat > "$HTML_FILE" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>HackerHub — FreeFire Quiz + FakeTube</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0a;font-family:'Rajdhani',sans-serif;min-height:100vh;color:#fff;overflow-x:hidden;}
#particles-canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;}
.container{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:20px 15px;}
.header{text-align:center;padding:25px 0 15px;border-bottom:2px solid #ff6600;margin-bottom:25px;}
.header h1{font-family:'Orbitron',sans-serif;font-size:2.2em;font-weight:900;background:linear-gradient(135deg,#ff6600,#ffaa00,#ff3300);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:3px;}
.header p{color:#ffaa00;font-size:1.1em;margin-top:5px;letter-spacing:1px;}
.header .nav-tabs{display:flex;justify-content:center;gap:15px;margin-top:15px;flex-wrap:wrap;}
.nav-tabs button{background:transparent;border:2px solid #ff6600;color:#ffaa00;padding:10px 25px;border-radius:30px;font-family:'Orbitron',sans-serif;font-size:0.85em;font-weight:700;cursor:pointer;transition:all 0.3s;text-transform:uppercase;letter-spacing:1px;}
.nav-tabs button:hover,.nav-tabs button.active{background:#ff6600;color:#000;box-shadow:0 0 20px rgba(255,102,0,0.4);}
.section{display:none;}
.section.active{display:block;}
.yt-header{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #222;margin-bottom:15px;flex-wrap:wrap;}
.yt-header .logo{font-family:'Orbitron',sans-serif;font-size:1.8em;font-weight:900;color:#ff0000;}
.yt-header .logo span{color:#fff;}
.yt-search-bar{flex:1;min-width:200px;display:flex;gap:0;}
.yt-search-bar input{flex:1;padding:10px 15px;border:2px solid #333;border-right:none;border-radius:25px 0 0 25px;background:#111;color:#fff;font-size:0.95em;outline:none;}
.yt-search-bar button{padding:10px 20px;border:2px solid #333;border-left:none;border-radius:0 25px 25px 0;background:#222;color:#fff;cursor:pointer;font-weight:700;transition:0.2s;}
.yt-search-bar button:hover{background:#ff0000;border-color:#ff0000;}
.yt-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;padding:10px 0;}
.yt-card{background:#111;border-radius:12px;overflow:hidden;border:1px solid #222;transition:0.3s;cursor:pointer;}
.yt-card:hover{transform:translateY(-4px);border-color:#ff6600;box-shadow:0 8px 25px rgba(255,102,0,0.15);}
.yt-thumb{width:100%;height:170px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;align-items:center;justify-content:center;position:relative;font-size:3em;}
.yt-thumb .duration{position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,0.85);padding:3px 8px;border-radius:4px;font-size:0.8em;color:#fff;}
.yt-info{padding:12px;}
.yt-info h3{font-size:1em;color:#eee;margin-bottom:5px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.yt-info p{color:#888;font-size:0.85em;}
.yt-info .channel{color:#aaa;font-size:0.8em;margin-top:4px;}
.yt-watch-page{display:none;padding:15px 0;}
.yt-watch-page.active{display:block;}
.yt-watch-page .back-btn{background:transparent;border:1px solid #ff6600;color:#ffaa00;padding:8px 20px;border-radius:20px;cursor:pointer;font-weight:700;margin-bottom:15px;transition:0.3s;}
.yt-watch-page .back-btn:hover{background:#ff6600;color:#000;}
.yt-video-player{width:100%;aspect-ratio:16/9;background:#000;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:4em;position:relative;overflow:hidden;border:1px solid #222;}
.yt-video-player .play-overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);cursor:pointer;transition:0.3s;}
.yt-video-player .play-overlay:hover{background:rgba(0,0,0,0.1);}
.yt-progress{height:4px;background:#333;border-radius:2px;margin:8px 0;position:relative;overflow:hidden;}
.yt-progress-bar{height:100%;width:0%;background:#ff0000;border-radius:2px;transition:width 0.5s;}
.yt-video-title{font-size:1.3em;font-weight:700;margin:10px 0 5px;}
.yt-video-stats{color:#888;font-size:0.9em;margin-bottom:10px;}
.yt-channel-bar{display:flex;align-items:center;gap:10px;padding:10px 0;border-top:1px solid #222;border-bottom:1px solid #222;margin:10px 0;}
.yt-channel-bar .avatar{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#ff6600,#ff3300);display:flex;align-items:center;justify-content:center;font-weight:900;}
.yt-channel-bar .sub-btn{margin-left:auto;background:#ff0000;border:none;color:#fff;padding:8px 18px;border-radius:20px;font-weight:700;cursor:pointer;}
.yt-comment{display:flex;gap:10px;padding:12px 0;border-bottom:1px solid #1a1a1a;}
.yt-comment .c-avatar{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#444,#666);flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:0.8em;}
.yt-comment .c-body{flex:1;}
.yt-comment .c-name{font-weight:700;color:#ddd;font-size:0.9em;}
.yt-comment .c-text{color:#bbb;font-size:0.9em;margin-top:2px;}
.yt-comment .c-time{color:#666;font-size:0.75em;margin-top:3px;}
.quiz-header{text-align:center;margin-bottom:20px;}
.quiz-header h2{font-family:'Orbitron',sans-serif;font-size:1.8em;color:#ff6600;text-shadow:0 0 15px rgba(255,102,0,0.3);}
.quiz-stats{display:flex;justify-content:center;gap:25px;flex-wrap:wrap;margin:15px 0;}
.stat-box{background:#111;border:1px solid #333;border-radius:12px;padding:12px 20px;text-align:center;min-width:100px;}
.stat-box .num{font-size:1.6em;font-weight:900;color:#ff6600;}
.stat-box .lbl{font-size:0.8em;color:#888;text-transform:uppercase;}
.quiz-categories{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin:15px 0;}
.cat-btn{background:transparent;border:1px solid #444;color:#aaa;padding:8px 16px;border-radius:20px;cursor:pointer;font-weight:600;transition:0.3s;font-size:0.85em;}
.cat-btn:hover,.cat-btn.active{background:#ff6600;border-color:#ff6600;color:#000;}
.quiz-question{background:#111;border:1px solid #333;border-radius:16px;padding:25px;margin:15px 0;}
.quiz-question .q-num{color:#ff6600;font-size:0.9em;font-weight:700;}
.quiz-question .q-text{font-size:1.3em;font-weight:700;margin:10px 0 18px;line-height:1.4;}
.quiz-options{display:grid;gap:10px;}
.quiz-option{background:#1a1a1a;border:2px solid #2a2a2a;border-radius:12px;padding:14px 18px;cursor:pointer;transition:all 0.25s;font-size:1em;color:#ddd;font-weight:600;display:flex;align-items:center;gap:12px;}
.quiz-option:hover{background:#222;border-color:#444;}
.quiz-option .letter{width:30px;height:30px;border-radius:50%;background:#2a2a2a;display:flex;align-items:center;justify-content:center;font-weight:900;flex-shrink:0;}
.quiz-option.selected{border-color:#ff6600;background:#1a1200;}
.quiz-option.selected .letter{background:#ff6600;color:#000;}
.quiz-option.correct{border-color:#00cc66;background:#0a1a10;}
.quiz-option.correct .letter{background:#00cc66;color:#000;}
.quiz-option.wrong{border-color:#ff3333;background:#1a0a0a;}
.quiz-option.wrong .letter{background:#ff3333;color:#000;}
.quiz-option.disabled{cursor:not-allowed;opacity:0.7;}
.quiz-next-btn{display:block;margin:20px auto 10px;background:linear-gradient(135deg,#ff6600,#ff3300);border:none;color:#000;padding:14px 40px;border-radius:30px;font-family:'Orbitron',sans-serif;font-size:1em;font-weight:700;cursor:pointer;transition:0.3s;text-transform:uppercase;letter-spacing:1px;}
.quiz-next-btn:hover{transform:scale(1.05);box-shadow:0 0 30px rgba(255,102,0,0.4);}
.quiz-next-btn:disabled{opacity:0.4;cursor:not-allowed;transform:none;box-shadow:none;}
.quiz-result{display:none;text-align:center;padding:30px;background:#111;border:1px solid #333;border-radius:20px;margin:15px 0;}
.quiz-result.active{display:block;}
.quiz-result .rank-badge{font-size:5em;margin:10px 0;}
.quiz-result .rank-title{font-family:'Orbitron',sans-serif;font-size:2em;color:#ff6600;margin:10px 0;}
.quiz-result .score-text{font-size:1.4em;color:#ddd;margin:10px 0;}
.quiz-result .sub-text{color:#888;font-size:0.95em;max-width:400px;margin:10px auto;}
.restart-btn{background:transparent;border:2px solid #ff6600;color:#ffaa00;padding:12px 35px;border-radius:30px;cursor:pointer;font-weight:700;font-size:1em;margin-top:15px;transition:0.3s;}
.restart-btn:hover{background:#ff6600;color:#000;}
.quiz-review{display:none;margin:15px 0;}
.quiz-review.active{display:block;}
.quiz-review h3{color:#ffaa00;margin-bottom:15px;font-family:'Orbitron',sans-serif;}
.review-item{background:#111;border:1px solid #222;border-radius:12px;padding:15px;margin-bottom:10px;}
.review-item .r-q{color:#eee;font-weight:700;margin-bottom:5px;}
.review-item .r-a{font-size:0.9em;}
.review-item .r-correct{color:#00cc66;}
.review-item .r-wrong{color:#ff3333;}
@keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.section.active{animation:fadeIn 0.4s ease;}
@media(max-width:600px){
  .header h1{font-size:1.5em;}
  .yt-grid{grid-template-columns:1fr;}
  .quiz-option{font-size:0.9em;padding:12px 14px;}
  .stat-box{min-width:80px;padding:10px 14px;}
  .stat-box .num{font-size:1.2em;}
  .nav-tabs button{padding:8px 16px;font-size:0.75em;}
}
</style>
</head>
<body>
<canvas id="particles-canvas"></canvas>
<div class="container">
  <div class="header">
    <h1>⚡ HACKERHUB</h1>
    <p>⎯⎯⎯⎯⎯⎯ FreeFire Quiz + FakeTube ⎯⎯⎯⎯⎯⎯</p>
    <div class="nav-tabs">
      <button class="active" onclick="switchTab('faketube')">🎬 FakeTube</button>
      <button onclick="switchTab('quiz')">🔥 FreeFire Quiz</button>
    </div>
  </div>
  <div id="section-faketube" class="section active">
    <div class="yt-header">
      <div class="logo">YT<span>ube</span></div>
      <div class="yt-search-bar">
        <input type="text" id="yt-search-input" placeholder="Search..." value="free fire gameplay">
        <button onclick="ytSearch()">🔍</button>
      </div>
    </div>
    <div id="yt-main"><div class="yt-grid" id="yt-grid"></div></div>
    <div class="yt-watch-page" id="yt-watch-page">
      <button class="back-btn" onclick="ytBack()">← Back to Home</button>
      <div class="yt-video-player" id="yt-player"><div class="play-overlay" onclick="togglePlay()">▶️</div></div>
      <div class="yt-progress"><div class="yt-progress-bar" id="yt-progress-bar"></div></div>
      <div class="yt-video-title" id="yt-video-title">Video Title</div>
      <div class="yt-video-stats" id="yt-video-stats">1,234,567 views • 1 day ago</div>
      <div class="yt-channel-bar">
        <div class="avatar">FF</div>
        <div><strong>FreeFire Clips</strong><br><span style="color:#888;font-size:0.8em;">12.4M subscribers</span></div>
        <button class="sub-btn">Subscribe</button>
      </div>
      <div style="margin-top:15px;"><h3 style="color:#aaa;font-size:1.1em;margin-bottom:10px;">Comments (24)</h3><div id="yt-comments"></div></div>
    </div>
  </div>
  <div id="section-quiz" class="section">
    <div class="quiz-header">
      <h2>🔥 FREE FIRE MCQ CHALLENGE</h2>
      <p style="color:#888;">Test your Free Fire knowledge!</p>
    </div>
    <div class="quiz-stats" id="quiz-stats">
      <div class="stat-box"><div class="num" id="q-current">0</div><div class="lbl">Current</div></div>
      <div class="stat-box"><div class="num" id="q-total">0</div><div class="lbl">Total</div></div>
      <div class="stat-box"><div class="num" id="q-correct">0</div><div class="lbl">Correct</div></div>
      <div class="stat-box"><div class="num" id="q-score">0%</div><div class="lbl">Score</div></div>
    </div>
    <div class="quiz-categories" id="quiz-categories"></div>
    <div id="quiz-area"></div>
    <div class="quiz-result" id="quiz-result">
      <div class="rank-badge" id="rank-badge">🏆</div>
      <div class="rank-title" id="rank-title">GRANDMASTER</div>
      <div class="score-text" id="final-score">10 / 10</div>
      <div class="sub-text" id="rank-desc">Perfect score! You're a Free Fire legend!</div>
      <button class="restart-btn" onclick="restartQuiz()">🔄 Play Again</button>
      <button class="restart-btn" style="margin-left:10px;" onclick="showReview()">📝 Review Answers</button>
    </div>
    <div class="quiz-review" id="quiz-review"></div>
  </div>
</div>
<script>
const canvas=document.getElementById('particles-canvas');const ctx=canvas.getContext('2d');let particles=[];
function resizeCanvas(){canvas.width=window.innerWidth;canvas.height=window.innerHeight;}
resizeCanvas();window.addEventListener('resize',resizeCanvas);
class Particle{
  constructor(){this.reset();}
  reset(){this.x=Math.random()*canvas.width;this.y=Math.random()*canvas.height;this.size=Math.random()*2+0.5;this.speedX=(Math.random()-0.5)*0.5;this.speedY=(Math.random()-0.5)*0.5;this.opacity=Math.random()*0.5+0.1;}
  update(){this.x+=this.speedX;this.y+=this.speedY;if(this.x<0||this.x>canvas.width||this.y<0||this.y>canvas.height)this.reset();}
  draw(){ctx.fillStyle=`rgba(255,102,0,${this.opacity})`;ctx.beginPath();ctx.arc(this.x,this.y,this.size,0,Math.PI*2);ctx.fill();}
}
for(let i=0;i<80;i++)particles.push(new Particle());
function animate(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  particles.forEach(p=>{p.update();p.draw();});
  for(let i=0;i<particles.length;i++){
    for(let j=i+1;j<particles.length;j++){
      const dx=particles[i].x-particles[j].x;const dy=particles[i].y-particles[j].y;const dist=Math.sqrt(dx*dx+dy*dy);
      if(dist<120){ctx.strokeStyle=`rgba(255,102,0,${0.08*(1-dist/120)})`;ctx.lineWidth=0.5;ctx.beginPath();ctx.moveTo(particles[i].x,particles[i].y);ctx.lineTo(particles[j].x,particles[j].y);ctx.stroke();}
    }
  }
  requestAnimationFrame(animate);
}
animate();
function switchTab(tab){
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('.nav-tabs button').forEach(b=>b.classList.remove('active'));
  document.getElementById(`section-${tab}`).classList.add('active');
  event.target.classList.add('active');
}
const ytVideos=[
  {id:1,title:"FREE FIRE BEST HEADSHOT TRICKS 2025",channel:"FreeFire Pro",views:"2.3M",time:"3 days ago",dur:"10:24",emoji:"🎯"},
  {id:2,title:"NEW CHARACTER ABILITY TIER LIST",channel:"FF Insider",views:"1.8M",time:"1 week ago",dur:"15:37",emoji:"📊"},
  {id:3,title:"BOOYAH! 50 KILL SOLO RUSH GAMEPLAY",channel:"RushGamer",views:"4.1M",time:"2 days ago",dur:"18:42",emoji:"🔥"},
  {id:4,title:"ALL NEW EVOLUTION WEAPONS 2025 SHOWCASE",channel:"WeaponMaster",views:"892K",time:"5 days ago",dur:"12:15",emoji:"⚔️"},
  {id:5,title:"BERMUDA MAP SECRET SPOTS YOU DIDN'T KNOW",channel:"MapExplorer",views:"1.2M",time:"1 day ago",dur:"8:50",emoji:"🗺️"},
  {id:6,title:"FREE FIRE VS PUBG MOBILE WHICH IS BETTER?",channel:"GameCompare",views:"5.6M",time:"1 month ago",dur:"22:10",emoji:"💥"},
  {id:7,title:"HOW TO GET DIAMONDS FOR FREE 2025",channel:"FF Hacks",views:"3.4M",time:"4 days ago",dur:"7:35",emoji:"💎"},
  {id:8,title:"CLASH SQUAD RANKED TIPS & TRICKS",channel:"SquadLeader",views:"756K",time:"6 days ago",dur:"14:20",emoji:"👥"},
  {id:9,title:"NEW PET ABILITIES FULL GUIDE 2025",channel:"PetMaster",views:"523K",time:"2 weeks ago",dur:"11:05",emoji:"🐾"},
  {id:10,title:"BERMUDA REMASTERED VS ORIGINAL COMPARISON",channel:"FF Streams",views:"2.1M",time:"3 weeks ago",dur:"16:48",emoji:"🏝️"},
  {id:11,title:"TOP 10 WEAPONS FOR CLASH SQUAD 2025",channel:"Weapons Lab",views:"980K",time:"8 days ago",dur:"9:55",emoji:"🔫"},
  {id:12,title:"PRO PLAYER SETTINGS YOU MUST USE!",channel:"Settings Pro",views:"1.5M",time:"2 days ago",dur:"6:40",emoji:"⚙️"}
];
const comments=[
  {name:"@booyahking",text:"Best headshot tricks ever! Got 3 booyahs today!",avatar:"👑"},
  {name:"@freefirefan21",text:"Bro this is insane 🔥🔥🔥",avatar:"🔥"},
  {name:"@gamerpro_ff",text:"Thanks for the tips! My gameplay improved so much",avatar:"💪"},
  {name:"@squad_leader",text:"Who else wants a new map in 2025? 🙋",avatar:"🙋"},
  {name:"@headshot_machine",text:"My record is 32 kills in ranked match",avatar:"🎯"},
  {name:"@diamond_hunter",text:"The free diamonds trick actually works! Legit!",avatar:"💎"},
  {name:"@clash_squad_yt",text:"Clash Squad tips are on point! Got to Heroic!",avatar:"🏆"},
  {name:"@ff_legend",text:"Been playing since 2019 and still learning new stuff",avatar:"👴"},
  {name:"@new_player_25",text:"Just started playing this game, very helpful thanks!",avatar:"🌟"},
  {name:"@rank_pusher",text:"Grandmaster rank here! Anyone want to squad up?",avatar:"👊"}
];
function renderGrid(videos){
  const grid=document.getElementById('yt-grid');grid.innerHTML='';
  videos.forEach(v=>{
    const card=document.createElement('div');card.className='yt-card';
    card.innerHTML=`<div class="yt-thumb" style="font-size:3.5em;">${v.emoji}<span class="duration">${v.dur}</span></div><div class="yt-info"><h3>${v.title}</h3><p>${v.views} views • ${v.time}</p><div class="channel">${v.channel}</div></div>`;
    card.onclick=()=>openVideo(v);grid.appendChild(card);
  });
}
renderGrid(ytVideos);
function ytSearch(){
  const q=document.getElementById('yt-search-input').value.toLowerCase();
  renderGrid(ytVideos.filter(v=>v.title.toLowerCase().includes(q)||v.channel.toLowerCase().includes(q)));
}
document.getElementById('yt-search-input').addEventListener('keyup',e=>{if(e.key==='Enter')ytSearch();});
function openVideo(video){
  document.getElementById('yt-main').style.display='none';
  const wp=document.getElementById('yt-watch-page');wp.classList.add('active');
  document.getElementById('yt-video-title').textContent=video.title;
  document.getElementById('yt-video-stats').textContent=`${video.views} views • ${video.time}`;
  document.getElementById('yt-player').querySelector('.play-overlay').textContent='▶️';
  document.getElementById('yt-progress-bar').style.width='0%';
  const cDiv=document.getElementById('yt-comments');cDiv.innerHTML='';
  comments.slice(0,6).forEach(c=>{
    cDiv.innerHTML+=`<div class="yt-comment"><div class="c-avatar">${c.avatar}</div><div class="c-body"><div class="c-name">${c.name}</div><div class="c-text">${c.text}</div><div class="c-time">2 hours ago</div></div></div>`;
  });
}
let isPlaying=false;
function togglePlay(){
  isPlaying=!isPlaying;
  const overlay=document.getElementById('yt-player').querySelector('.play-overlay');
  overlay.textContent=isPlaying?'⏸️':'▶️';
  if(isPlaying){
    let w=0;const bar=document.getElementById('yt-progress-bar');
    const interval=setInterval(()=>{
      w+=Math.random()*2+0.5;if(w>=100){w=100;clearInterval(interval);isPlaying=false;overlay.textContent='▶️';}
      bar.style.width=w+'%';
    },300);
    window._ytInterval=interval;
  }else{clearInterval(window._ytInterval);}
}
function ytBack(){
  document.getElementById('yt-main').style.display='block';
  document.getElementById('yt-watch-page').classList.remove('active');
  clearInterval(window._ytInterval);isPlaying=false;
}
const allQuestions=[
  {q:"Which weapon has the highest headshot damage in Free Fire?",o:["AWM","M82B","Woodpecker","Kar98k"],a:1,cat:"Weapons"},
  {q:"What is the magazine capacity of the M249?",o:["100","120","150","80"],a:1,cat:"Weapons"},
  {q:"Which weapon uses .50 caliber rounds?",o:["M82B","AWM","M24","SVD"],a:0,cat:"Weapons"},
  {q:"What is the fire rate of the MP40?",o:["83","78","90","75"],a:2,cat:"Weapons"},
  {q:"Which SMG has the fastest reload speed?",o:["MP5","Vector","UMP","PP Bizon"],a:1,cat:"Weapons"},
  {q:"The Woodpecker is classified as which weapon type?",o:["Assault Rifle","Shotgun","Pistol","Sniper"],a:2,cat:"Weapons"},
  {q:"Which attachment reduces recoil the most?",o:["Foregrip","Silencer","Muzzle","Stock"],a:0,cat:"Weapons"},
  {q:"What is Hayato's awakening ability called?",o:["Bushido","Blazing","Gunslinger","Raging"],a:0,cat:"Characters"},
  {q:"Which character has the 'Drop The Beat' ability?",o:["DJ Alok","Kla","Jai","Sonia"],a:0,cat:"Characters"},
  {q:"What does Chrono's ability do?",o:["Creates shield","Heals team","Increases speed","Revives"],a:0,cat:"Characters"},
  {q:"Who is the medic character with 'Healing Heart'?",o:["Kla","Antonio","Miguel","Jota"],a:1,cat:"Characters"},
  {q:"What is Wukong's ability?",o:["Invisibility","Clone","Wall hack","Shield"],a:1,cat:"Characters"},
  {q:"Which character has the ability 'Riptide Rhythm'?",o:["Thiva","Sonia","Dimitri","Shani"],a:0,cat:"Characters"},
  {q:"Steffie's ability reduces damage from which source?",o:["Grenades","Bullets","Gloo walls","Vehicles"],a:0,cat:"Characters"},
  {q:"Which is the smallest map in Free Fire?",o:["Kalahari","Bermuda","Purgatory","Alpine"],a:0,cat:"Maps"},
  {q:"How many locations does Bermuda have?",o:["10","12","8","14"],a:1,cat:"Maps"},
  {q:"Which map was added in OB35 update?",o:["NeXTerra","Kalahari","Bermuda Remastered","Alpine"],a:0,cat:"Maps"},
  {q:"Kalahari is based on which real-world desert?",o:["Sahara","Kalahari","Gobi","Mojave"],a:1,cat:"Maps"},
  {q:"What is the name of the air drop weapon exclusive to Bermuda?",o:["AWM","M249","M79","Flame Thrower"],a:0,cat:"Maps"},
  {q:"How many players drop in a Clash Squad match?",o:["8","4","6","10"],a:0,cat:"Maps"},
  {q:"What does the pet 'Mr. Waggor' do?",o:["Spawns gloo walls","Heals","Detects enemies","Increases damage"],a:0,cat:"Pets"},
  {q:"Which pet has the ability 'Panda's Blessing'?",o:["Bea","Panda","Rocky","Finny"],a:0,cat:"Pets"},
  {q:"What is the maximum level for a pet?",o:["10","7","15","5"],a:0,cat:"Pets"},
  {q:"Which pet detects enemies within a certain range?",o:["Detective Panda","Ottero","Robo","Falco"],a:0,cat:"Pets"},
  {q:"The pet 'Dr. Beanie' is known for what?",o:["Healing","Shielding","Scanning","Speed boost"],a:2,cat:"Pets"},
  {q:"How many pet slots can a player unlock?",o:["3","2","4","1"],a:0,cat:"Pets"},
  {q:"What is the highest rank in Free Fire?",o:["Grandmaster","Heroic","Master","Legendary"],a:0,cat:"Ranked"},
  {q:"How many points to reach Heroic from Master?",o:["600","400","800","500"],a:0,cat:"Ranked"},
  {q:"What rank requires 1000 points?",o:["Grandmaster","Heroic","Master","Legendary"],a:2,cat:"Ranked"},
  {q:"How many tiers are in the ranked system?",o:["7","6","8","5"],a:1,cat:"Ranked"},
  {q:"What is the lowest ranked tier?",o:["Bronze","Silver","Gold","Platinum"],a:0,cat:"Ranked"},
  {q:"How many points do you lose for 8th place in ranked?",o:["35","25","45","40"],a:0,cat:"Ranked"},
  {q:"Which rank comes after Diamond?",o:["Heroic","Master","Grandmaster","Platinum"],a:0,cat:"Ranked"},
  {q:"What is the name of Free Fire's battle pass?",o:["Elite Pass","Premium Pass","Battle Pass","Gold Pass"],a:0,cat:"Ranked"},
  {q:"Which company developed Free Fire?",o:["111 Dots Studio","Garena","Tencent","Krafton"],a:1,cat:"General"},
  {q:"In which year was Free Fire globally released?",o:["2017","2016","2018","2019"],a:0,cat:"General"},
  {q:"What is the maximum number of players in a Battle Royale match?",o:["52","50","60","48"],a:0,cat:"General"},
  {q:"How many grenade types are there?",o:["4","3","5","6"],a:0,cat:"General"},
  {q:"What is the name of Free Fire's ranking event mode?",o:["Clash Squad","Bomb Squad","Team Strike","Rampage"],a:1,cat:"General"},
  {q:"Which vehicle has the fastest speed?",o:["Motorcycle","SUV","Jeep","Buggy"],a:0,cat:"General"}
];
const categories=[...new Set(allQuestions.map(q=>q.cat))];
let filteredQuestions=[...allQuestions];
let currentQ=0;let score=0;let selectedAnswers=[];
let answered=[];
let quizMode='all';
function initQuiz(){
  currentQ=0;score=0;selectedAnswers=[];answered=[];
  document.getElementById('quiz-result').classList.remove('active');
  document.getElementById('quiz-review').classList.remove('active');
  document.getElementById('quiz-review').innerHTML='';
  renderCategories();renderQuestion();
}
function renderCategories(){
  const div=document.getElementById('quiz-categories');div.innerHTML=`<button class="cat-btn active" onclick="filterCategory('all')">ALL (${allQuestions.length})</button>`;
  categories.forEach(c=>{
    const count=allQuestions.filter(q=>q.cat===c).length;
    div.innerHTML+=`<button class="cat-btn" onclick="filterCategory('${c}')">${c} (${count})</button>`;
  });
}
function filterCategory(cat){
  document.querySelectorAll('.cat-btn').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
  quizMode=cat;
  if(cat==='all')filteredQuestions=[...allQuestions];
  else filteredQuestions=allQuestions.filter(q=>q.cat===cat);
  initQuiz();
}
function renderQuestion(){
  const area=document.getElementById('quiz-area');
  if(currentQ>=filteredQuestions.length){showResult();return;}
  const q=filteredQuestions[currentQ];const total=filteredQuestions.length;
  document.getElementById('q-current').textContent=currentQ+1;
  document.getElementById('q-total').textContent=total;
  document.getElementById('q-correct').textContent=score;
  document.getElementById('q-score').textContent=total>0?Math.round(score/total*100)+'%':'0%';
  const letters=['A','B','C','D'];
  area.innerHTML=`
    <div class="quiz-question">
      <div class="q-num">Question ${currentQ+1}/${total} • ${q.cat}</div>
      <div class="q-text">${q.q}</div>
      <div class="quiz-options" id="quiz-options">
        ${q.o.map((opt,i)=>`<div class="quiz-option" data-idx="${i}" onclick="selectAnswer(${i})"><div class="letter">${letters[i]}</div><span>${opt}</span></div>`).join('')}
      </div>
    </div>
    <button class="quiz-next-btn" id="next-btn" disabled onclick="nextQuestion()">NEXT →</button>`;
}
function selectAnswer(idx){
  if(answered[currentQ]!==undefined)return;
  const opts=document.querySelectorAll('.quiz-option');
  opts.forEach((o,i)=>{o.classList.remove('selected');if(i===idx)o.classList.add('selected');});
  selectedAnswers[currentQ]=idx;document.getElementById('next-btn').disabled=false;
}
function nextQuestion(){
  if(answered[currentQ]!==undefined)return;
  const q=filteredQuestions[currentQ];const sel=selectedAnswers[currentQ];
  const opts=document.querySelectorAll('.quiz-option');const correct=q.a;
  let isCorrect=false;if(sel===correct){isCorrect=true;score++;}
  answered[currentQ]=sel;
  opts.forEach((o,i)=>{
    o.classList.remove('selected','correct','wrong','disabled');
    o.classList.add('disabled');
    if(i===correct)o.classList.add('correct');
    if(i===sel&&sel!==correct)o.classList.add('wrong');
  });
  currentQ++;
  document.getElementById('q-correct').textContent=score;
  document.getElementById('q-score').textContent=Math.round(score/filteredQuestions.length*100)+'%';
  setTimeout(()=>renderQuestion(),600);
}
function showResult(){
  const area=document.getElementById('quiz-area');area.innerHTML='';
  const total=filteredQuestions.length;const pct=total>0?Math.round(score/total*100):0;
  document.getElementById('q-current').textContent=total;
  document.getElementById('q-correct').textContent=score;
  document.getElementById('q-score').textContent=pct+'%';
  document.getElementById('final-score').textContent=`${score} / ${total} — ${pct}%`;
  let rank,desc,badge;
  if(pct===100){rank='GRANDMASTER';desc='Perfect score! You are a Free Fire LEGEND!';badge='🏆';}
  else if(pct>=90){rank='HEROIC';desc='Outstanding! Nearly flawless!';badge='🥇';}
  else if(pct>=75){rank='MASTER';desc='Great knowledge! You know Free Fire well!';badge='🥈';}
  else if(pct>=60){rank='DIAMOND';desc='Good job! Keep learning!';badge='💎';}
  else if(pct>=45){rank='PLATINUM';desc='Not bad! Study a bit more!';badge='🥉';}
  else if(pct>=30){rank='GOLD';desc='You have room to improve!';badge='⭐';}
  else if(pct>=15){rank='SILVER';desc='Keep practicing!';badge='🌙';}
  else{rank='BRONZE';desc='Time to hit the training ground!';badge='🪨';}
  document.getElementById('rank-title').textContent=rank;
  document.getElementById('rank-badge').textContent=badge;
  document.getElementById('rank-desc').textContent=desc;
  document.getElementById('quiz-result').classList.add('active');
}
function showReview(){
  const div=document.getElementById('quiz-review');div.innerHTML='<h3>📝 Answer Review</h3>';
  filteredQuestions.forEach((q,i)=>{
    const ans=answered[i]!==undefined?answered[i]:'N/A';
    const isCorrect=ans===q.a;
    div.innerHTML+=`<div class="review-item"><div class="r-q">Q${i+1}: ${q.q}</div><div class="r-a ${isCorrect?'r-correct':'r-wrong'}">${isCorrect?'✅ Correct':'❌ Wrong'} — Your answer: ${ans==='N/A'?'Skipped':q.o[ans]}${!isCorrect?` | Correct: ${q.o[q.a]}`:''}</div></div>`;
  });
  div.classList.add('active');
}
function restartQuiz(){initQuiz();}
initQuiz();
</script>
</body>
</html>
HTMLEOF
}

# Generate configuration and files
echo -e "${C}[*]${NC} Generating HackerHub files and setting up for 100% Bash badge..."
generate_gitattributes
generate_html

# Start web server
echo -e "${G}[*]${NC} Starting web server on http://localhost:$PORT..."
cd "$BASE_DIR"

if [ -n "$BROWSER_CMD" ] && [ "$EUID" -ne 0 ]; then
    (sleep 1 && "$BROWSER_CMD" "http://localhost:$PORT" &>/dev/null &)
elif [ "$EUID" -eq 0 ]; then
    echo -e "${Y}[!] Note: Running as root. Open http://localhost:$PORT manually in your browser.${NC}"
fi

if command -v python3 &>/dev/null; then
    python3 -m http.server "$PORT"
else
    echo -e "${R}[!] Error: Python3 is required to run the local server.${NC}"
    exit 1
fi
