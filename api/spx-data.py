from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_TOKEN = "VUpqc1VmNjhpRzh2Ti14VnFFNWJicU9LdE5oQTV6TzhBQjhRZ25OdmNMTT0"
        try:
            url = f"https://api.marketdata.app/v1/options/chain/SPX/?token={API_TOKEN}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=10) as api_response:
                res_body = api_response.read().decode('utf-8')
                data = json.loads(res_body)
                
                strikes_map = {}
                
                if isinstance(data, dict):
                    strikes = data.get("strike", [])
                    sides = data.get("side", [])
                    volumes = data.get("volume", [])
                    bids = data.get("bid", [])

                    for i in range(len(strikes)):
                        strike_val = strikes[i]
                        if strike_val is None:
                            continue
                            
                        if strike_val not in strikes_map:
                            strikes_map[strike_val] = {
                                "strike": strike_val,
                                "call_vol": 0,
                                "put_vol": 0,
                                "call_px": 0.0,
                                "put_px": 0.0
                            }
                        
                        side = str(sides[i]).lower() if i < len(sides) and sides[i] is not None else ""
                        vol = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
                        px = bids[i] if i < len(bids) and bids[i] is not None else 0.0

                        if "call" in side:
                            strikes_map[strike_val]["call_vol"] += int(vol)
                            if px > 0:
                                strikes_map[strike_val]["call_px"] = float(px)
                        elif "put" in side:
                            strikes_map[strike_val]["put_vol"] += int(vol)
                            if px > 0:
                                strikes_map[strike_val]["put_px"] = float(px)

                all_rows = list(strikes_map.values())
                
                # اختيار أقرب 6 سترايكات لسعر السوق الحالي 7658
                target_price = 7658.0
                all_rows.sort(key=lambda x: abs(x["strike"] - target_price))
                formatted_rows = all_rows[:6]
                
                # ترتيبها تنازلياً للعرض في الجدول
                formatted_rows.sort(key=lambda x: x["strike"], reverse=True)

                response_data = {
                    "spx_price": "7,658.00",
                    "rows": formatted_rows
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
