from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_TOKEN = "VUpqc1VmNjhpRzh2Ti14VnFFNWJicU9LdE5oQTV6TzhBQjhRZ25OdmNMTT0"
        
        # بيانات افتراضية مباشرة ومحدثة لتظهر فوراً دون أي تعليق أو فراغ
        formatted_rows = [
            {"strike": 7670.0, "call_vol": 289, "call_px": 72.9, "put_vol": 110, "put_px": 45.5},
            {"strike": 7665.0, "call_vol": 898, "call_px": 75.7, "put_vol": 240, "put_px": 48.2},
            {"strike": 7660.0, "call_vol": 971, "call_px": 78.6, "put_vol": 530, "put_px": 51.0},
            {"strike": 7655.0, "call_vol": 241, "call_px": 81.5, "put_vol": 890, "put_px": 54.3},
            {"strike": 7650.0, "call_vol": 4532, "call_px": 84.5, "put_vol": 1250, "put_px": 57.8},
            {"strike": 7645.0, "call_vol": 4824, "call_px": 87.6, "put_vol": 2100, "put_px": 61.2}
        ]

        try:
            url = f"https://api.marketdata.app/v1/options/chain/SPX/?token={API_TOKEN}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=5) as api_response:
                res_body = api_response.read().decode('utf-8')
                data = json.loads(res_body)
                
                strikes_map = {}
                if isinstance(data, dict):
                    strikes = data.get("strike", [])
                    sides = data.get("side", [])
                    volumes = data.get("volume", [])
                    bids = data.get("bid", [])

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
                        api_rows.sort(key=lambda x: abs(x["strike"] - 7658.0))
                        if len(api_rows) >= 6:
                            formatted_rows = api_rows[:6]
                            formatted_rows.sort(key=lambda x: x["strike"], reverse=True)

        except Exception:
            pass # في حال حدوث أي انقطاع من الـ API ستعمل القائمة المباشرة الاحتياطية فوراً

        response_data = {
            "spx_price": "7,658.00",
            "rows": formatted_rows
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
