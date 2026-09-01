import os
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

API_TOKEN = "OFBBWEVfdkM4ChlxS0N6cm9GUzhyYWtWViZLUXNb1d6QUYTWmILTW1nbz0"

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/api/spx-data")
def get_spx_data():
  headers = {"Authorization": f"Bearer {API_TOKEN}"}

  try:
    response = requests.get(
        "https://api.marketdata.app/v1/options/chain/SPX/", headers=headers
    )
    data = response.json()

    # استخراج البيانات وتجهيزها بالهيكل المناسب للواجهة
    formatted_rows = []
    spx_val = "7,686.62" # قيمة افتراضية أو مستخرجة

    if data.get("status") == "ok" and "strike" in data:
        strikes = data.get("strike", [])
        call_vol = data.get("callVolume", [])
        put_vol = data.get("putVolume", [])
        call_px = data.get("callBid", []) # أو Mid حسب المتوفر
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
        "spx_price": spx_val,
        "rows": formatted_rows
    })

  except Exception as e:
    return jsonify({"error": str(e), "rows": []}), 500

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
