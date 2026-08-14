from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Target GraphQL API URL (Apna exact URL yahan dalein)
GRAPHQL_URL = "https://example.com/graphql"

@app.route('/api/track', methods=['GET'])
def track_user():
    username = request.args.get('username')
    
    if not username:
        return jsonify({"error": "Username parameter missing hai!"}), 400

    # 1. Headers set karna sabse zaroori hai Kali Linux ke liye
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # 2. Apni GraphQL Query setup karein
    graphql_query = {
        "query": """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                # Apni baki fields yahan dalein
            }
        }
        """,
        "variables": {"username": username}
    }

    try:
        # Request bhejein custom headers ke saath
        response = requests.post(GRAPHQL_URL, json=graphql_query, headers=headers, timeout=10)

        # Response check karein
        if response.status_code == 200:
            try:
                data = response.json()
                return jsonify(data), 200
            except ValueError:
                # Agar response JSON nahi hai (HTML block page mila)
                return jsonify({
                    "error": "Server ne JSON ki jagah HTML bheja (Request Blocked).",
                    "raw_response": response.text[:200]
                }), 500
        else:
            return jsonify({
                "error": f"API Request Failed with Status Code {response.status_code}",
                "details": response.text[:200]
            }), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network Exception: {str(e)}"}), 500

if __name__ == '__main__':
    # 0.0.0.0 par run karein taaki VM network accessible rahe
    app.run(host='0.0.0.0', port=5000, debug=True)
