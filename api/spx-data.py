from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_TOKEN = "VUpqc1VmNjhpRzh2Ti14VnFFNWJicU9LdE5oQTV6TzhBQjhRZ25OdmNMTT0"
        
        underlying_price = 7658.00
        formatted_rows = [
            {"strike": 7670.0, "call_vol": 2600, "call_px": 65.0, "put_vol": 1840, "put_px": 65.0},
            {"strike": 7665.0, "call_vol": 3600, "call_px": 72.5, "put_vol": 2740, "put_px": 57.5},
            {"strike": 7660.0, "call_vol": 4600, "call_px": 80.0, "put_vol": 3640, "put_px": 50.0},
            {"strike": 7655.0, "call_vol": 4400, "call_px": 87.5, "put_vol": 3460, "put_px": 42.5},
            {"strike": 7650.0, "call_vol": 3400, "call_px": 95.0, "put_vol": 2560, "put_px": 35.0},
            {"strike": 7645.0, "call_vol": 2400, "call_px": 102.5, "put_vol": 1660, "put_px": 27.5}
        ]

        try:
            url = f"https://api.marketdata.app/v1/options/chain/SPX/?token={API_TOKEN}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=8) as api_response:
                res_body = api_response.read().decode('utf-8')
                data = json.loads(res_body)
                
                if isinstance(data, dict):
                    # محاولة استخراج السعر الأساسي الحقيقي من الـ API
                    underlying = data.get("underlying")
                    if underlying:
                        if isinstance(underlying, list) and len(underlying) > 0 and underlying[0] is not None:
                            underlying_price = float(underlying[0])
                        elif isinstance(underlying, (int, float)):
                            underlying_price = float(underlying)

                    strikes = data.get("strike", [])
                    sides = data.get("side", [])
                    volumes = data.get("volume", [])
                    bids = data.get("bid", [])

                    strikes_map = {}
                    for i in range(len(strikes)):
                        s_val = strikes[i]
                        if s_val is None:
                            continue
                        try:
                            s_float = float(s_val)
                        except:
                            continue

                        if s_float not in strikes_map:
                            strikes_map[s_float] = {"strike": s_float, "call_vol": 0, "put_vol": 0, "call_px": 0.0, "put_px": 0.0}
                        
                        side = str(sides[i]).lower() if i < len(sides) and sides[i] is not None else ""
                        vol = int(volumes[i]) if i < len(volumes) and volumes[i] is not None else 0
                        bid = float(bids[i]) if i < len(bids) and bids[i] is not None else 0.0

                        if "call" in side:
                            strikes_map[s_float]["call_vol"] += vol
                            if bid > 0: strikes_map[s_float]["call_px"] = bid
                        elif "put" in side:
                            strikes_map[s_float]["put_vol"] += vol
                            if bid > 0: strikes_map[s_float]["put_px"] = bid

                    api_rows = list(strikes_map.values())
                    if api_rows:
                        api_rows.sort(key=lambda x: abs(x["strike"] - underlying_price))
                        if len(api_rows) >= 6:
                            formatted_rows = api_rows[:6]
                            formatted_rows.sort(key=lambda x: x["strike"], reverse=True)

        except Exception:
            pass

        response_data = {
            "spx_price": f"{underlying_price:,.2f}",
            "rows": formatted_rows
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
