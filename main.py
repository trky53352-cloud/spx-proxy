
import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

API_TOKEN = "OFBBWEVfdkM4ChlxS0N6cm9GUzhyYWtWViZLUXNb1d6QUYTWmILTW1nbz0"

@app.route("/")
def index():
    return "API Proxy is running. Go to /api/spx-data"

@app.route("/api/spx-data")
def get_spx_data():
  try:
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(
        "https://api.marketdata.app/v1/options/chain/SPX/", headers=headers, timeout=10
    )
    
    return jsonify({
        "status_code": response.status_code,
        "response_text": response.text[:1000]
    })
  except Exception as e:
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
