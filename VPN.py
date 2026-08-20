import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Professional HTML Template (Using Bootstrap for "Proper" Look)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional IP Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .tracker-card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); background: white; margin-top: 50px; padding: 30px; }
        .data-label { font-weight: bold; color: #555; text-transform: uppercase; font-size: 0.8rem; }
        .data-value { font-size: 1.1rem; color: #000; margin-bottom: 15px; }
        .map-container { height: 300px; width: 100%; border-radius: 10px; margin-top: 20px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8 tracker-card">
                <h2 class="text-center mb-4">🌍 VPN IP Tracker</h2>
                
                <!-- Search Form -->
                <form method="POST" class="mb-4">
                    <div class="input-group">
                        <input type="text" name="ip_address" class="form-control" placeholder="Enter IP Address (e.g. 8.8.8.8)" value="{{ data.query }}">
                        <button class="btn btn-primary" type="submit">Track IP</button>
                    </div>
                </form>

                {% if data.status == 'success' %}
                <div class="row">
                    <div class="col-sm-6">
                        <p class="data-label">IP Address</p>
                        <p class="data-value">{{ data.query }}</p>
                        <p class="data-label">Location</p>
                        <p class="data-value">{{ data.city }}, {{ data.regionName }}, {{ data.country }}</p>
                    </div>
                    <div class="col-sm-6">
                        <p class="data-label">ISP / Organization</p>
                        <p class="data-value">{{ data.isp }}</p>
                        <p class="data-label">Timezone</p>
                        <p class="data-value">{{ data.timezone }}</p>
                    </div>
                </div>
                
                <!-- Google Maps Embed -->
                <iframe class="map-container" frameborder="0" 
                    src="https://maps.google.com/maps?q={{ data.lat }},{{ data.lon }}&z=12&output=embed">
                </iframe>
                
                {% else %}
                <div class="alert alert-danger">Could not fetch data for this IP. Please check the address.</div>
                {% endif %}
                
                <p class="text-muted text-center mt-4" style="font-size: 0.7rem;">Made with ❤️ by Kk's</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

def get_ip_info(ip=""):
    """Fetch live data from a real IP Geolocation API."""
    try:
        # If running locally, request.remote_addr is '127.0.0.1'. 
        # In that case, we leave it blank to let the API detect our real public IP.
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url)
        return response.json()
    except Exception:
        return {"status": "fail"}

@app.route('/', methods=['GET', 'POST'])
def index():
    target_ip = ""
    if request.method == 'POST':
        target_ip = request.form.get('ip_address')
    
    # Get info (if target_ip is empty, the API tracks the visitor's IP)
    ip_data = get_ip_info(target_ip)
    return render_template_string(HTML_TEMPLATE, data=ip_data)

if __name__ == '__main__':
    # Use debug=True for development. Run on port 5000.
    app.run(debug=True, port=5000)
