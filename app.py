import os
from MasterPro import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
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
>>>>>>> 4a52bd6b9ae38f80b18bfedb00d29b27546ecfb7
