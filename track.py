import os
import folium
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
    212: (31.7917, -7.0926), 213: (28.0339, 1.6596), 216: (33.8869, 9.5375),
    218: (26.3351, 17.2283), 220: (13.4432, -15.3101), 221: (14.4974, -14.4524),
    222: (18.0731, -15.9586), 223: (17.5707, -3.9962), 224: (9.9456, -9.6966),
    225: (7.5400, -5.5471), 226: (12.2383, -1.5616), 227: (17.6078, 8.0817),
    228: (8.6195, 0.8248), 229: (9.3077, 2.3158), 230: (-20.3484, 57.5522),
    231: (6.4281, -9.4295), 232: (8.4606, -11.7799), 233: (7.9465, -1.0232),
    234: (9.0820, 8.6753), 235: (15.4542, 18.7322), 236: (6.6111, 21.0937),
    237: (7.3697, 12.3547), 238: (16.0021, -24.0132), 240: (1.6508, 10.2679),
    241: (-0.8037, 11.6094), 242: (-0.2280, 15.8277), 243: (-4.0383, 21.7587),
    244: (-8.8742, 125.7275), 245: (11.8037, -15.1804), 248: (-4.6796, 55.4920),
    249: (15.5527, 48.5164), 250: (-1.9403, 29.8739), 251: (9.1450, 40.4897),
    252: (5.1521, 46.1996), 253: (-11.8750, 43.8722), 254: (-0.0236, 37.9062),
    255: (-6.3690, 34.8888), 256: (1.3733, 32.2903), 257: (-3.3731, 29.9189),
    258: (-18.6657, 35.5296), 260: (-13.1339, 27.8493), 261: (-18.7669, 46.8691),
    262: (-20.9042, 55.5714), 263: (-19.0154, 29.1549), 264: (-22.9576, 18.4904),
    265: (-13.1339, 27.8493), 266: (-29.6100, 28.2336), 267: (-22.3285, 24.6849),
    268: (-26.5225, 31.4659), 290: (-24.3770, -14.3050), 291: (15.3500, 38.9667),
    297: (-12.1676, -72.9963), 298: (62.0145, -6.7741), 299: (64.9631, -19.0208),
    350: (36.1408, -5.3536), 351: (39.3999, -8.2245), 352: (49.8153, 6.1296),
    353: (53.4129, -8.2439), 354: (64.9631, -19.0208), 355: (41.1533, 20.1683),
    356: (35.9375, 14.3754), 357: (35.1264, 33.4299), 358: (61.9241, 25.7482),
    359: (42.7339, 25.4858), 370: (55.1694, 23.8813), 371: (56.8796, 24.6032),
    372: (58.5953, 25.0136), 373: (47.4116, 28.3699), 374: (40.0691, 45.0382),
    375: (53.7098, 27.9534), 376: (41.6086, 21.7453), 377: (43.7628, 11.2463),
    378: (43.9424, 12.4578), 380: (48.3794, 31.1656), 381: (44.0165, 21.0059),
    382: (42.7087, 19.3744), 385: (45.1000, 15.2000), 386: (46.1512, 14.9955),
    387: (43.9159, 17.6791), 389: (41.6086, 21.7453), 420: (49.8175, 15.4730),
    421: (48.6690, 19.6990), 423: (47.1667, 9.5333), 500: (-51.7963, -59.5236),
    501: (17.1899, -88.4976), 502: (14.6349, -90.5069), 503: (13.7942, -88.8965),
    504: (15.2000, -86.2419), 505: (12.8654, -85.2072), 506: (9.7489, -83.7534),
    507: (8.5379, -80.7821), 508: (46.9411, -56.2745), 509: (18.9712, -72.2852),
    590: (16.2650, -61.5510), 591: (-16.2902, -63.5887), 592: (4.8604, -58.9302),
    593: (-1.8312, -78.1834), 594: (3.9339, -53.0000), 595: (-23.4425, -58.4438),
    596: (14.6415, -61.0242), 597: (3.9193, -56.0278), 598: (-32.5228, -55.7658),
    599: (12.1696, -68.9900), 670: (-8.5500, 125.5667), 673: (4.5353, 114.7277),
    675: (-6.3150, 143.9555), 676: (-21.2000, -175.2000), 677: (-9.4438, 159.9726),
    678: (-16.5782, 168.2312), 679: (-17.7134, 178.0650), 680: (7.5141, 134.5825),
    681: (-13.5920, 172.1450), 682: (-21.2370, -159.7773), 683: (-19.0544, -169.8684),
    685: (-13.8333, -171.7500), 686: (-1.4650, 173.0110), 687: (-20.9146, 165.7778),
    688: (-8.5300, 179.1960), 689: (-17.6797, -149.4068), 690: (-9.4536, 160.1688),
    691: (6.8860, 158.2277), 692: (7.0930, 171.3800), 850: (39.0194, 125.7381),
    852: (22.3193, 114.1694), 853: (22.1564, 113.5503), 855: (12.5657, 104.9910),
    856: (19.8563, 102.4955), 880: (23.6850, 90.3563), 886: (23.6978, 120.9605),
    960: (3.2028, 73.2207), 961: (33.8547, 35.8623), 962: (30.5852, 36.2384),
    963: (34.8021, 38.9968), 964: (33.2232, 43.6793), 965: (29.3117, 47.4818),
    966: (23.8859, 45.0792), 967: (15.5527, 48.5164), 968: (21.4735, 55.9754),
    970: (31.9474, 35.2272), 971: (23.4241, 53.8478), 972: (31.0461, 34.8516),
    973: (26.0667, 50.5577), 974: (25.3548, 51.1839), 975: (26.9314, 89.6000),
    976: (46.8625, 103.8467), 977: (28.3949, 84.1240), 992: (38.8610, 71.2761),
    993: (38.9697, 59.5563), 994: (40.1431, 47.5769), 995: (42.3154, 43.3569),
    996: (41.2044, 74.7661), 998: (41.3775, 64.5853),
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


# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE =""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>PhoneLocator - Number Lookup & Live GPS</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:linear-gradient(135deg, #001a33, #003366, #004d99, #0066cc); color:#e0f7e0; min-height:100vh; animation:bgShift 15s ease infinite; background-size:400% 400%; }
@keyframes bgShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
body::before { content:''; position:fixed; top:0; left:0; width:100%; height:100%; background:radial-gradient(ellipse at 20% 50%, rgba(0,255,100,0.05) 0%, transparent 50%), radial-gradient(ellipse at 80% 50%, rgba(0,255,150,0.05) 0%, transparent 50%); pointer-events:none; z-index:0; }
.container { max-width:1200px; margin:0 auto; padding:20px; position:relative; z-index:1; }
header { text-align:center; padding:25px 20px 15px; }
.logo { display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:4px; }
.logo i { font-size:28px; color:#00ff88; background:rgba(0,255,100,0.1); padding:10px; border-radius:12px; }
header h1 { font-size:24px; font-weight:800; background:linear-gradient(135deg,#00ff88,#00ffcc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
header p { color:#80e0a0; font-size:13px; margin-top:2px; }
.tabs { display:flex; gap:8px; justify-content:center; margin-bottom:18px; }
.tab-btn { padding:10px 22px; border-radius:10px; border:1px solid rgba(0,255,100,0.15); background:rgba(0,50,100,0.6); color:#80e0a0; font-size:14px; font-weight:500; font-family:'Inter',sans-serif; cursor:pointer; transition:all 0.3s; display:flex; align-items:center; gap:8px; }
.tab-btn:hover { border-color:rgba(0,255,100,0.3); color:#e0f7e0; }
.tab-btn.active { background:rgba(0,255,100,0.15); border-color:#00ff88; color:#00ff88; }
.tab-content { display:none; }
.tab-content.active { display:block; }
.search-card { background:linear-gradient(145deg,rgba(0,40,80,0.9),rgba(0,20,50,0.95)); border:1px solid rgba(0,255,100,0.15); border-radius:20px; padding:25px; backdrop-filter:blur(20px); margin-bottom:20px; box-shadow:0 8px 32px rgba(0,0,0,0.3); }
.search-form { display:flex; gap:10px; align-items:center; }
.input-group { flex:1; position:relative; }
.input-group i { position:absolute; left:14px; top:50%; transform:translateY(-50%); color:#006633; font-size:14px; }
.search-card input[type="text"] { width:100%; padding:14px 14px 14px 42px; background:rgba(0,60,100,0.6); border:1px solid rgba(0,255,100,0.2); border-radius:10px; color:#e0f7e0; font-size:15px; font-family:'Inter',sans-serif; outline:none; transition:all 0.3s; }
.search-card input[type="text"]:focus { border-color:#00ff88; box-shadow:0 0 0 3px rgba(0,255,100,0.15); background:rgba(0,60,100,0.8); }
.search-card input[type="text"]::placeholder { color:#409060; }
.search-card button { padding:14px 28px; background:linear-gradient(135deg,#00cc66,#00ff88); color:#001a33; border:none; border-radius:10px; font-size:15px; font-weight:600; font-family:'Inter',sans-serif; cursor:pointer; transition:all 0.3s; display:flex; align-items:center; gap:8px; white-space:nowrap; }
.search-card button:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(0,255,100,0.3); }
.examples { display:flex; gap:6px; margin-top:10px; flex-wrap:wrap; align-items:center; }
.examples span { font-size:11px; color:#409060; }
.example-btn { padding:4px 10px; background:rgba(0,255,100,0.08); border:1px solid rgba(0,255,100,0.12); border-radius:6px; color:#80e0a0; font-size:11px; font-family:'Inter',sans-serif; cursor:pointer; transition:all 0.2s; }
.example-btn:hover { background:rgba(0,255,100,0.15); border-color:rgba(0,255,100,0.3); color:#e0f7e0; }
.error { background:rgba(255,68,68,0.1); border:1px solid rgba(255,68,68,0.25); border-radius:10px; padding:12px 16px; color:#fca5a5; font-size:14px; margin-bottom:16px; display:flex; align-items:center; gap:8px; }
.results-grid { display:grid; grid-template-columns:1fr 1.5fr; gap:18px; }
.info-panel { background:linear-gradient(145deg,rgba(0,40,80,0.9),rgba(0,20,50,0.95)); border:1px solid rgba(0,255,100,0.1); border-radius:18px; padding:24px; backdrop-filter:blur(20px); }
.info-panel h2 { font-size:14px; font-weight:600; color:#80e0a0; text-transform:uppercase; letter-spacing:1px; margin-bottom:16px; display:flex; align-items:center; gap:8px; }
.info-panel h2 i { color:#00ff88; font-size:12px; }
.info-item { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid rgba(0,255,100,0.05); }
.info-item:last-child { border-bottom:none; }
.info-label { font-size:13px; color:#409060; display:flex; align-items:center; gap:8px; }
.info-label i { width:14px; color:#00ff88; font-size:12px; }
.info-value { font-size:13px; font-weight:500; color:#e0f7e0; text-align:right; word-break:break-all; }
.badge { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:500; }
.badge-country { background:rgba(0,255,100,0.12); color:#00ff88; }
.badge-carrier { background:rgba(0,255,150,0.12); color:#00ffaa; }
.map-panel { background:linear-gradient(145deg,rgba(0,40,80,0.9),rgba(0,20,50,0.95)); border:1px solid rgba(0,255,100,0.1); border-radius:18px; padding:15px; backdrop-filter:blur(20px); min-height:380px; }
.map-panel .folium-map, .map-panel iframe, #liveMap { width:100%; height:100%; min-height:360px; border:none; border-radius:10px; }
#liveMap { z-index:1; }
.empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:50px 20px; text-align:center; grid-column:1/-1; }
.empty-state i { font-size:44px; color:rgba(0,255,100,0.2); margin-bottom:14px; }
.empty-state h3 { color:#409060; font-size:17px; font-weight:500; }
.empty-state p { color:#306040; font-size:13px; margin-top:4px; }
footer { text-align:center; padding:18px; color:#306040; font-size:11px; }
.status-bar { display:flex; gap:15px; align-items:center; flex-wrap:wrap; margin-bottom:12px; padding:10px 14px; background:rgba(0,40,80,0.7); border-radius:10px; border:1px solid rgba(0,255,100,0.08); }
.status-dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.status-dot.green { background:#00ff88; box-shadow:0 0 8px rgba(0,255,100,0.4); animation:pulse 1.5s infinite; }
.status-dot.yellow { background:#fbbf24; box-shadow:0 0 8px rgba(251,191,36,0.4); }
.status-dot.red { background:#ef4444; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }
.tracker-info { font-size:12px; color:#80e0a0; }
.tracker-info span { color:#00ff88; font-weight:600; }
.copy-link { padding:6px 14px; background:rgba(0,255,100,0.1); border:1px solid rgba(0,255,100,0.2); border-radius:6px; color:#80e0a0; font-size:12px; font-family:'Inter',sans-serif; cursor:pointer; transition:all 0.2s; }
.copy-link:hover { background:rgba(0,255,100,0.2); color:#e0f7e0; }
.target-url-box { display:flex; gap:8px; align-items:center; margin-top:8px; }
.target-url-box input { flex:1; padding:10px 14px; background:rgba(0,60,100,0.6); border:1px solid rgba(0,255,100,0.15); border-radius:8px; color:#e0f7e0; font-size:13px; font-family:monospace; outline:none; }
.target-url-box input:focus { border-color:#00ff88; }
@media (max-width:768px) { .results-grid { grid-template-columns:1fr; } .search-form { flex-direction:column; } .search-card button { width:100%; justify-content:center; } header h1 { font-size:20px; } .search-card { padding:18px; } .info-panel,.map-panel { padding:15px; } .tabs { flex-direction:column; align-items:stretch; } }
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

<!-- Tab 1: Number Lookup -->
<div id="tab-lookup" class="tab-content active">
<div class="search-card">
<form class="search-form" method="POST" action="/" id="phoneForm">
<div class="input-group"><i class="fas fa-phone"></i>
<input type="text" name="phone_number" id="phoneInput" placeholder="Enter phone with country code (e.g., +14155552671)" value="{{ phone_value }}" required>
</div>
<button type="submit"><i class="fas fa-search"></i> Track</button>
</form>

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

<!-- Tab 2: Live GPS Tracker -->
<div id="tab-live" class="tab-content">
<div class="search-card">
<h2 style="font-size:15px;font-weight:600;color:#80e0a0;margin-bottom:12px;display:flex;align-items:center;gap:8px;"><i class="fas fa-satellite" style="color:#00ff88;"></i> Live GPS Tracker</h2>
<p style="font-size:13px;color:#409060;margin-bottom:14px;">
