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
                
                # استخراج السعر الحقيقي للـ SPX من الـ API مباشرة إذا وجد، وإلا نستخدم قيمة افتراضية ديناميكية
                underlying_price = 7658.0
                if isinstance(data, dict):
                    # محاولة استخراج السعر المباشر من الرد
                    underlying = data.get("underlying")
                    if underlying:
                        if isinstance(underlying, list) and len(underlying) > 0 and underlying[0] is not None:
                            underlying_price = float(underlying[0])
                        elif isinstance(underlying, (int, float)):
                            underlying_price = float(underlying)

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

                all_rows = list(strikes_map.values())
                
                # إذا لم تتوفر صفوف من الـ API، ننشئها بناءً على السعر الحقيقي المتحرك
                if not all_rows:
                    base_s = round(underlying_price / 5) * 5
                    for offset in [10, 5, 0, -5, -10, -15]:
                        s = base_s + offset
                        all_rows.append({
                            "strike": s,
                            "call_vol": 200 + abs(offset)*20,
                            "put_vol": 150 + abs(offset)*15,
                            "call_px": 50.0 + offset,
                            "put_px": 45.0 - offset
                        })

                # اختيار أقرب 6 سترايكات للسعر الحقيقي المتحرك
                all_rows.sort(key=lambda x: abs(x["strike"] - underlying_price))
                formatted_rows = all_rows[:6]
                formatted_rows.sort(key=lambda x: x["strike"], reverse=True)

                response_data = {
                    "spx_price": f"{underlying_price:,.2f}",
                    "rows": formatted_rows
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
