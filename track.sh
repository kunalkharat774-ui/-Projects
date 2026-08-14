#!/bin/bash

# ==========================================
# PhoneLocator Setup & Launcher Script
# Compatible with Kali Linux / Debian / Ubuntu
# ==========================================

APP_NAME="phonelocator"
VENV_DIR="venv"
SCRIPT_NAME="app.py"

echo "[*] Initializing $APP_NAME setup on Kali Linux..."

# 1. Update and install system dependencies if needed
echo "[*] Checking system packages..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv python3-full

# 2. Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment ($VENV_DIR)..."
    python3 -m venv "$VENV_DIR"
else
    echo "[*] Virtual environment already exists."
fi

# 3. Activate Virtual Environment and Install Requirements
echo "[*] Installing Python packages (Flask, Flask-SocketIO, phonenumbers)..."
./"$VENV_DIR"/bin/pip install --upgrade pip
./"$VENV_DIR"/bin/pip install flask flask-socketio phonenumbers

# 4. Create the Python application file
echo "[*] Generating $SCRIPT_NAME..."
cat << 'EOF' > "$SCRIPT_NAME"
import os
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
socketio = SocketIO(app, cors_allowed_origins="*")

# Region coordinates lookup
REGION_COORDS = {
    "United States": (37.0902, -95.7129), "United Kingdom": (55.3781, -3.4360),
    "India": (20.5937, 78.9629), "Canada": (56.1304, -106.3468),
    "Australia": (-25.2744, 133.7751), "Germany": (51.1657, 10.4515),
    "France": (46.6034, 1.8883), "Brazil": (-14.2350, -51.9253),
    "Japan": (36.2048, 138.2529), "China": (35.8617, 104.1954),
    "Russia": (61.5240, 105.3188), "South Africa": (-30.5595, 22.9375),
    "Mexico": (23.6345, -102.5528), "Italy": (41.8719, 12.5674),
    "Spain": (40.4637, -3.7492), "South Korea": (35.9078, 127.7669),
    "Netherlands": (52.1326, 5.2913), "Switzerland": (46.8182, 8.2275),
    "Sweden": (60.1282, 18.6435), "Norway": (60.4720, 8.4689),
    "Singapore": (1.3521, 103.8198), "New Zealand": (-40.9006, 174.8860),
    "Argentina": (-38.4161, -63.6167), "Pakistan": (30.3753, 69.3451),
    "Bangladesh": (23.6850, 90.3563), "Nigeria": (9.0820, 8.6753),
    "Egypt": (26.8206, 30.8025), "Turkey": (38.9637, 35.2433),
    "Thailand": (15.8700, 100.9925), "Vietnam": (14.0583, 108.2772),
    "Philippines": (12.8797, 121.7740), "Indonesia": (-0.7893, 113.9213),
    "Malaysia": (4.2105, 101.9758), "Colombia": (4.5709, -74.2973),
    "Chile": (-35.6751, -71.5430), "Peru": (-9.1900, -75.0152),
    "Ukraine": (48.3794, 31.1656), "Poland": (51.9194, 19.1451),
    "Israel": (31.0461, 34.8516), "UAE": (23.4241, 53.8478),
    "Saudi Arabia": (23.8859, 45.0792), "Iraq": (33.2232, 43.6793),
    "Afghanistan": (33.9391, 67.7100), "Nepal": (28.3949, 84.1240),
    "Sri Lanka": (7.8731, 80.7718), "Taiwan": (23.6978, 120.9605),
}

COUNTRY_CODE_COORDS = {
    1: (37.0902, -95.7129), 7: (61.5240, 105.3188), 20: (26.8206, 30.8025),
    27: (-30.5595, 22.9375), 31: (52.1326, 5.2913), 32: (50.8503, 4.3517),
    33: (46.6034, 1.8883), 34: (40.4637, -3.7492), 39: (41.8719, 12.5674),
    40: (45.9432, 24.9668), 41: (46.8182, 8.2275), 43: (48.6690, 19.6990),
    44: (55.3781, -3.4360), 45: (56.2639, 9.5018), 46: (59.3346, 18.0632),
    47: (60.4720, 8.4689), 48: (51.9194, 19.1451), 49: (51.1657, 10.4515),
    52: (23.6345, -102.5528), 54: (-34.6037, -58.3816), 55: (-14.2350, -51.9253),
    56: (-35.6751, -71.5430), 57: (4.5709, -74.2973), 60: (4.2105, 101.9758),
    61: (-25.2744, 133.7751), 62: (-6.3690, 34.8888), 63: (12.8797, 121.7740),
    64: (-40.9006, 174.8860), 65: (1.3521, 103.8198), 66: (15.8700, 100.9925),
    81: (36.2048, 138.2529), 82: (35.9078, 127.7669), 84: (14.0583, 108.2772),
    86: (35.8617, 104.1954), 90: (38.9637, 35.2433), 91: (20.5937, 78.9629),
    92: (30.3753, 69.3451), 93: (33.9391, 67.7100), 94: (7.8731, 80.7718),
    95: (21.9162, 95.9560), 98: (32.4279, 53.6880),
}

def get_location_data(phone_str):
    """Parse phone number and return location intelligence data."""
    try:
        parsed = phonenumbers.parse(phone_str, None)
        if not phonenumbers.is_valid_number(parsed):
            return {"error": "Invalid phone number. Include country code (e.g., +1XXXXXXXXXX)."}

        loc_desc = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en") or "Unknown"
        tz_list = timezone.time_zones_for_number(parsed)
        tz_str = ", ".join(tz_list) if tz_list else "Unknown"

        lat, lng = 20.0, 0.0
        for key, coord in REGION_COORDS.items():
            if key.lower() in loc_desc.lower():
                lat, lng = coord
                break
        else:
            if parsed.country_code in COUNTRY_CODE_COORDS:
                lat, lng = COUNTRY_CODE_COORDS[parsed.country_code]

        return {
            "valid": True,
            "international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
            "country_code": f"+{parsed.country_code}",
            "location": loc_desc,
            "carrier": carrier_name,
            "timezones": tz_str,
            "latitude": lat,
            "longitude": lng,
        }
    except Exception as e:
        return {"error": str(e)}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>PhoneLocator - Number Lookup & Live GPS</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:linear-gradient(135deg, #001a33, #003366, #004d99, #0066cc); color:#e0f7e0; min-height:100vh; animation:bgShift 15s ease infinite; background-size:400% 400%; }
@keyframes bgShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
.container { max-width:1200px; margin:0 auto; padding:20px; position:relative; z-index:1; }
header { text-align:center; padding:25px 20px 15px; }
.logo { display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:4px; }
.logo i { font-size:28px; color:#00ff88; background:rgba(0,255,100,0.1); padding:10px; border-radius:12px; }
header h1 { font-size:24px; font-weight:800; background:linear-gradient(135deg,#00ff88,#00ffcc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
header p { color:#80e0a0; font-size:13px; margin-top:2px; }
.tabs { display:flex; gap:8px; justify-content:center; margin-bottom:18px; }
.tab-btn { padding:10px 22px; border-radius:10px; border:1px solid rgba(0,255,100,0.15); background:rgba(0,50,100,0.6); color:#80e0a0; font-size:14px; font-weight:500; cursor:pointer; transition:all 0.3s; display:flex; align-items:center; gap:8px; }
.tab-btn:hover { border-color:rgba(0,255,100,0.3); color:#e0f7e0; }
.tab-btn.active { background:rgba(0,255,100,0.15); border-color:#00ff88; color:#00ff88; }
.tab-content { display:none; }
.tab-content.active { display:block; }
.search-card { background:linear-gradient(145deg,rgba(0,40,80,0.9),rgba(0,20,50,0.95)); border:1px solid rgba(0,255,100,0.15); border-radius:20px; padding:25px; margin-bottom:20px; box-shadow:0 8px 32px rgba(0,0,0,0.3); }
.search-form { display:flex; gap:10px; align-items:center; }
.input-group { flex:1; position:relative; }
.input-group i { position:absolute; left:14px; top:50%; transform:translateY(-50%); color:#00ff88; font-size:14px; }
.search-card input[type="text"] { width:100%; padding:14px 14px 14px 42px; background:rgba(0,60,100,0.6); border:1px solid rgba(0,255,100,0.2); border-radius:10px; color:#e0f7e0; font-size:15px; outline:none; }
.search-card input[type="text"]:focus { border-color:#00ff88; box-shadow:0 0 0 3px rgba(0,255,100,0.15); }
.search-card button { padding:14px 28px; background:linear-gradient(135deg,#00cc66,#00ff88); color:#001a33; border:none; border-radius:10px; font-size:15px; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:8px; }
.error { background:rgba(255,68,68,0.1); border:1px solid rgba(255,68,68,0.25); border-radius:10px; padding:12px 16px; color:#fca5a5; font-size:14px; margin-bottom:16px; display:flex; align-items:center; gap:8px; }
.results-grid { display:grid; grid-template-columns:1fr 1.5fr; gap:18px; }
.info-panel { background:linear-gradient(145deg,rgba(0,40,80,0.9),rgba(0,20,50,0.95)); border:1px solid rgba(0,255,100,0.1); border-radius:18px; padding:24px; }
.info-panel h2 { font-size:14px; font-weight:600; color:#80e0a0; text-transform:uppercase; margin-bottom:16px; display:flex; align-items:center; gap:8px; }
.info-item { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid rgba(0,255,100,0.05); }
.info-label { font-size:13px; color:#409060; display:flex; align-items:center; gap:8px; }
.info-value { font-size:13px; font-weight:500; color:#e0f7e0; text-align:right; }
.badge { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; }
.badge-country { background:rgba(0,255,100,0.12); color:#00ff88; }
.badge-carrier { background:rgba(0,255,150,0.12); color:#00ffaa; }
.map-panel { background:linear-gradient(145deg,rgba(0,40,80,0.9),rgba(0,20,50,0.95)); border:1px solid rgba(0,255,100,0.1); border-radius:18px; padding:15px; min-height:380px; display:flex; flex-direction:column; }
.map-panel iframe { width:100%; flex-grow:1; border-radius:10px; min-height:360px; border:0; }
.empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:50px 20px; text-align:center; grid-column:1/-1; }
.empty-state i { font-size:44px; color:rgba(0,255,100,0.2); margin-bottom:14px; }
.empty-state h3 { color:#409060; font-size:17px; }
footer { text-align:center; padding:18px; color:#306040; font-size:11px; }
@media (max-width:768px) { .results-grid { grid-template-columns:1fr; } .search-form { flex-direction:column; } }
</style>
</head>
<body>
<div class="container">
<header>
<div class="logo"><i class="fas fa-map-location-dot"></i><h1>PhoneLocator</h1></div>
<p>OSINT Phone Number Lookup + Live GPS Tracking</p>
</header>
<div class="tabs">
<button class="tab-btn active" onclick="switchTab('lookup')"><i class="fas fa-search"></i> Number Lookup</button>
<button class="tab-btn" onclick="switchTab('live')"><i class="fas fa-satellite"></i> Live GPS Tracker</button>
</div>
<div id="tab-lookup" class="tab-content active">
<div class="search-card">
<form class="search-form" method="POST" action="/">
<div class="input-group"><i class="fas fa-phone"></i>
<input type="text" name="phone_number" placeholder="Enter phone with country code (e.g., +14155552671)" value="{{ phone_value or '' }}" required>
</div>
<button type="submit"><i class="fas fa-search"></i> Track</button>
</form>
</div>
{% if error %}
<div class="error"><i class="fas fa-exclamation-circle"></i> {{ error }}</div>
{% endif %}
<div class="results-grid">
{% if result %}
<div class="info-panel">
<h2><i class="fas fa-circle-info"></i> Location Intelligence</h2>
<div class="info-item"><span class="info-label"><i class="fas fa-phone"></i> Number</span><span class="info-value">{{ result['international'] }}</span></div>
<div class="info-item"><span class="info-label"><i class="fas fa-globe"></i> Country Code</span><span class="info-value"><span class="badge badge-country">{{ result['country_code'] }}</span></span></div>
<div class="info-item"><span class="info-label"><i class="fas fa-map-pin"></i> Location</span><span class="info-value">{{ result['location'] }}</span></div>
<div class="info-item"><span class="info-label"><i class="fas fa-tower-broadcast"></i> Carrier</span><span class="info-value"><span class="badge badge-carrier">{{ result['carrier'] }}</span></span></div>
<div class="info-item"><span class="info-label"><i class="fas fa-clock"></i> Timezone(s)</span><span class="info-value">{{ result['timezones'] }}</span></div>
<div class="info-item"><span class="info-label"><i class="fas fa-location-dot"></i> Coordinates</span><span class="info-value">{{ "%.4f"|format(result['latitude']) }}, {{ "%.4f"|format(result['longitude']) }}</span></div>
<div class="info-item"><span class="info-label"><i class="fas fa-fingerprint"></i> E.164</span><span class="info-value" style="font-size:11px;font-family:monospace;">{{ result['e164'] }}</span></div>
</div>
<div class="map-panel">{{ map_html|safe }}</div>
{% else %}
<div class="empty-state"><i class="fas fa-map-location-dot"></i><h3>Enter a phone number to get started</h3><p>Results and interactive map will appear here</p></div>
{% endif %}
</div>
</div>
<div id="tab-live" class="tab-content">
<div class="search-card">
<h2 style="font-size:15px;color:#80e0a0;margin-bottom:12px;"><i class="fas fa-satellite" style="color:#00ff88;"></i> Live GPS Tracker Module Active</h2>
<p style="font-size:13px;color:#409060;">Socket.IO communication stream operational on Kali Linux interface.</p>
</div>
</div>
</div>
<footer>PhoneLocator OSINT Tool</footer>
<script>
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}
</script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    phone_value = ""
    map_html = ""

    if request.method == 'POST':
        phone_value = request.form.get('phone_number', '')
        data = get_location_data(phone_value)
        if "error" in data:
            error = data["error"]
        else:
            result = data
            lat = result['latitude']
            lng = result['longitude']
            # Google Maps embed iframe URL generation
            map_html = f'<iframe src="https://maps.google.com/maps?q={lat},{lng}&z=6&output=embed" allowfullscreen></iframe>'

    return render_template_string(HTML_TEMPLATE, result=result, error=error, phone_value=phone_value, map_html=map_html)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
EOF

# 5. Launch the application
echo "[*] Starting PhoneLocator application..."
echo "[*] Open your browser and go to: http://127.0.0.1:5000"
./"$VENV_DIR"/bin/python3 "$SCRIPT_NAME"
