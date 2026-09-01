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
    # إضافة المعايير الأساسية لجلب السلسلة
    response = requests.get(
        "https://api.marketdata.app/v1/options/chain/SPX/", headers=headers
    )
    
    # إذا لم تكن الاستجابة ناجحة، أظهر كود الخطأ
    if response.status_code != 200:
        return jsonify({"error": f"API returned status {response.status_code}", "details": response.text}), 500

    data = response.json()

    formatted_rows = []
    spx_val = "7,686.62"

    if isinstance(data, dict):
        # التحقق من مفاتيح البيانات وحالة الرد
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
        "spx_price": spx_val,
        "rows": formatted_rows,
        "raw_keys": list(data.keys()) if isinstance(data, dict) else "not a dict"
    })

  except Exception as e:
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
