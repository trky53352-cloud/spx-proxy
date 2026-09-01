from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

API_KEY = "RDVyUkFOdzBKMnFFVlh5RVV5N1FrSzJoRzBKQUtnN0puaEFmc093Ulkzcz0"
BASE_URL = "https://api.marketdata.app/v1"

def _get(url):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=6) as resp:
        return json.loads(resp.read().decode("utf-8"))

def fetch_spx_data():
    url = f"{BASE_URL}/options/chain/SPX/?dte=0&range=all&strikeLimit=14"
    try:
        data = _get(url)
    except Exception as e:
        print(f"MarketData error: {e}")
        return "5800.00", {}, 0, 0

    if data.get("s") != "ok":
        return "5800.00", {}, 0, 0

    # استخراج السعر الحقيقي من حقل underlyingPrice إن وجد
    price = 0.0
    underlying = data.get("underlyingPrice", [])
    if underlying and underlying[0] is not None:
        price = float(underlying[0])

    by_strike = {}
    total_call_vol = 0
    total_put_vol = 0

    strikes = data.get("strike", [])
    sides = data.get("side", [])
    volumes = data.get("volume", [])
    open_interests = data.get("openInterest", [])
    mids = data.get("mid", [])

    n = len(strikes)
    for i in range(n):
        try:
            strike = strikes[i]
            side = sides[i]
            vol = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
            oi = open_interests[i] if i < len(open_interests) and open_interests[i] is not None else 0
            mid = mids[i] if i < len(mids) and mids[i] is not None else 0.0

            # إذا لم يتم التقاط السعر من الـ underlying، نأخذه كمتوسط من السترايكات الوسطى
            if price == 0.0 and strike > 0:
                price = float(strike)

            row = by_strike.setdefault(strike, {
                "strike": strike,
                "call_vol": 0, "call_oi": 0, "call_px": 0.0,
                "put_vol": 0, "put_oi": 0, "put_px": 0.0,
            })

            if side == "call":
                row["call_vol"] = int(vol)
                row["call_oi"] = int(oi)
                row["call_px"] = round(float(mid), 2)
                total_call_vol += int(vol)
            elif side == "put":
                row["put_vol"] = int(vol)
                row["put_oi"] = int(oi)
                row["put_px"] = round(float(mid), 2)
                total_put_vol += int(vol)
        except Exception:
            continue

    final_price = f"{price:,.2f}" if price > 0 else "5,800.00"
    rows = sorted(by_strike.values(), key=lambda r: r["strike"], reverse=True)
    return final_price, rows, total_call_vol, total_put_vol

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        price, rows, total_call_vol, total_put_vol = fetch_spx_data()

        response_data = {
            "spx": {
                "price": price,
                "total_call_vol": total_call_vol,
                "total_put_vol": total_put_vol,
                "rows": rows
            }
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
