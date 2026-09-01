import json
import urllib.request
from flask import Flask, jsonify

app = Flask(__name__)

API_TOKEN = "OFBBWEVfdkM4ChlxS0N6cm9GUzhyYWtWViZLUXNb1d6QUYTWmILTW1nbz0"

@app.route("/")
def index():
    return "API Proxy is running."

@app.route("/api/spx-data")
def get_spx_data():
    try:
        url = "https://api.marketdata.app/v1/options/chain/SPX/"
        req = urllib.request.Request(
            url, 
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            data = json.loads(res_body)
            
            formatted_rows = []
            if isinstance(data, dict):
                strikes = data.get("strike", [])
                call_vol = data.get("callVolume", [])
                put_vol = data.get("putVolume", [])
                call_px = data.get("callBid", [])
                put_px = data.get("putBid", [])

                for i in range(len(strikes)):
                    formatted_rows.append({
                        "strike": strikes[i],
                        "call_vol": call_vol[i] if i < len(call_vol) else 0,
                        "put_vol": put_vol[i] if i < len(put_vol) else 0,
                        "call_px": call_px[i] if i < len(call_px) else 0,
                        "put_px": put_px[i] if i < len(put_px) else 0
                    })

            return jsonify({
                "spx_price": "7,686.62",
                "rows": formatted_rows
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
