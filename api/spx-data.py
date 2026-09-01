from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

# =========================================================
# مفتاح MarketData.app المباشر الخاص بك
# =========================================================
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

def fetch_live_price(symbol, fallback_price):
    try:
        data = _get(f"{BASE_URL}/stocks/prices/{symbol}/")
        if data.get("s") == "ok" and data.get("mid"):
            return round(float(data["mid"][0]), 2)
    except Exception as e:
        print(f"MarketData price error for {symbol}: {e}")
    return fallback_price

def fetch_option_chain(symbol, strikes_each_side=7):
    url = (
        f"{BASE_URL}/options/chain/{symbol}/"
        f"?dte=0&range=all&strikeLimit={strikes_each_side * 2}"
    )
    try:
        data = _get(url)
    except Exception as e:
        print(f"MarketData chain error for {symbol}: {e}")
        return {}, 0, 0

    if data.get("s") != "ok":
        return {}, 0, 0

    by_strike = {}
    total_call_vol = 0
    total_put_vol = 0

    n = len(data.get("strike", []))
    for i in range(n):
        strike = data["strike"][i]
        side = data["side"][i]
        vol = data.get("volume", [0] * n)[i] or 0
        oi = data.get("openInterest", [0] * n)[i] or 0
        mid = data.get("mid", [0] * n)[i] or 0

        row = by_strike.setdefault(strike, {
            "strike": strike,
            "call_vol": 0, "call_oi": 0, "call_px": 0.0,
            "put_vol": 0, "put_oi": 0, "put_px": 0.0,
        })

        if side == "call":
            row["call_vol"] = vol
            row["call_oi"] = oi
            row["call_px"] = round(mid, 2)
            total_call_vol += vol
        else:
            row["put_vol"] = vol
            row["put_oi"] = oi
            row["put_px"] = round(mid, 2)
            total_put_vol += vol

    return by_strike, total_call_vol, total_put_vol

def build_symbol_payload(symbol, fallback_price):
    price = fetch_live_price(symbol, fallback_price)
    by_strike, total_call_vol, total_put_vol = fetch_option_chain(symbol)
    rows = sorted(by_strike.values(), key=lambda r: r["strike"], reverse=True)

    return {
        "price": f"{price:,.2f}",
        "total_call_vol": total_call_vol,
        "total_put_vol": total_put_vol,
        "rows": rows,
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response_data = {
            "spx": build_symbol_payload("SPX", 7620.00),
            "ndx": build_symbol_payload("NDX", 25000.00),
            "qqq": build_symbol_payload("QQQ", 707.77),
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
