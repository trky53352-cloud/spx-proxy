import os
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# مفتاح Market Data الخاص بك
API_TOKEN = "OFBBWEVfdkM4ChlxS0N6cm9GUzhyYWtWViZLUXNb1d6QUYTWmILTW1nbz0"


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/api/spx-data")
def get_spx_data():
  headers = {"Authorization": f"Bearer {API_TOKEN}"}

  try:
    # جلب سلسلة عقود الخيارات وسعر SPX الحالي من Market Data API
    response = requests.get(
        "https://api.marketdata.app/v1/options/chain/SPX/", headers=headers
    )
    data = response.json()

    # إعادة البيانات للواجهة بصيغة JSON
    return jsonify(data)
  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
