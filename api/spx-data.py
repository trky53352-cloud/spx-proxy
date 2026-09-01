from http.server import BaseHTTPRequestHandler
import json
import urllib.request

API_KEY = "RDVyUkFOdzBKMnFFVlh5RVV5N1FrSzJoRzBKQUtnN0puaEFmc093Ulkzcz0"
BASE_URL = "https://api.marketdata.app/v1"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # جلب مباشر لسلسلة خيارات SPX والأسعار الفورية
        url = f"{BASE_URL}/options/chain/SPX/?dte=0&range=all&strikeLimit=14"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "application/json",
            },
        )
        
        price_val = 5800.00
        by_strike = {}
        total_call_vol = 0
        total_put_vol = 0

        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("s") == "ok":
                    # محاولة قطة السعر من الـ underlying
                    underlying = data.get("underlyingPrice", [])
                    if underlying and underlying[0] is not None:
                        price_val = float(underlying[0])

                    strikes = data.get("strike", [])
                    sides = data.get("side", [])
                    volumes = data.get("volume", [])
                    open_interests = data.get("openInterest", [])
                    mids = data.get("mid", [])

                    for i in range(len(strikes)):
                        try:
                            strike = strikes[i]
                            side = sides[i]
                            vol = volumes[i] if volumes[i] is not None else 0
                            oi = open_interests[i] if open_interests[i] is not None else 0
                            mid = mids[i] if mids[i] is not None else 0.0

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
                        except:
                            continue
        except Exception as e:
            print(f"Error: {e}")

        rows = sorted(by_strike.values(), key=lambda r: r["strike"], reverse=True)
        
        response_data = {
            "spx": {
                "price": f"{price_val:,.2f}",
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
