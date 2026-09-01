from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_TOKEN = "VUpqc1VmNjhpRzh2Ti14VnFFNWJicU9LdE5oQTV6TzhBQjhRZ25OdmNMTT0"
        
        underlying_price = 7658.00
        strikes_map = {}
        has_valid_data = False

        try:
            # 1. جلب تواريخ الاستحقاق المتاحة لمعرفة أقرب تاريخ عقود SPX
            exp_url = f"https://api.marketdata.app/v1/options/expirations/SPX/?token={API_TOKEN}"
            req_exp = urllib.request.Request(exp_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_exp, timeout=4) as exp_resp:
                exp_data = json.loads(exp_resp.read().decode('utf-8'))
                expirations = exp_data.get("expirations", [])
                
                target_exp = expirations[0] if expirations else None
            
            # 2. جلب سلسلة الخيارات الحقيقية لتاريخ الاستحقاق المحدد
            if target_exp:
                chain_url = f"https://api.marketdata.app/v1/options/chain/SPX/?expiration={target_exp}&token={API_TOKEN}"
            else:
                chain_url = f"https://api.marketdata.app/v1/options/chain/SPX/?token={API_TOKEN}"
                
            req_chain = urllib.request.Request(chain_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_chain, timeout=5) as api_response:
                res_body = api_response.read().decode('utf-8')
                data = json.loads(res_body)
                
                if isinstance(data, dict):
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
                    asks = data.get("ask", [])

                    for i in range(len(strikes)):
                        s_val = strikes[i]
                        if s_val is None:
                            continue
                        try:
                            s_float = float(s_val)
                        except:
                            continue

                        if s_float not in strikes_map:
                            strikes_map[s_float] = {
                                "strike": s_float, 
                                "call_vol": 0, "call_px": 0.0, 
                                "put_vol": 0, "put_px": 0.0
                            }
                        
                        side = str(sides[i]).lower() if i < len(sides) and sides[i] is not None else ""
                        vol = int(volumes[i]) if i < len(volumes) and volumes[i] is not None else 0
                        
                        price = 0.0
                        if i < len(bids) and bids[i] is not None and float(bids[i]) > 0:
                            price = float(bids[i])
                        elif i < len(asks) and asks[i] is not None and float(asks[i]) > 0:
                            price = float(asks[i])

                        if "call" in side:
                            strikes_map[s_float]["call_vol"] += vol
                            if price > 0: strikes_map[s_float]["call_px"] = price
                        elif "put" in side:
                            strikes_map[s_float]["put_vol"] += vol
                            if price > 0: strikes_map[s_float]["put_px"] = price
        except Exception:
            pass

        # التحقق من وجود عقود حقيقية بحجوم أو أسعار غير صفرية
        if strikes_map:
            for s_data in strikes_map.values():
                if s_data["call_vol"] > 0 or s_data["put_vol"] > 0 or s_data["call_px"] > 0 or s_data["put_px"] > 0:
                    has_valid_data = True
                    break

        formatted_rows = []
        if has_valid_data:
            all_rows = list(strikes_map.values())
            all_rows.sort(key=lambda x: abs(x["strike"] - underlying_price))
            selected = all_rows[:6]
            selected.sort(key=lambda x: x["strike"], reverse=True)
            formatted_rows = selected
        else:
            rounded_base = round(underlying_price / 5) * 5
            for offset in [10, 5, 0, -5, -10, -15]:
                formatted_rows.append({
                    "strike": float(rounded_base + offset),
                    "call_vol": 0, "call_px": 0.0,
                    "put_vol": 0, "put_px": 0.0
                })

        response_data = {
            "spx_price": f"{underlying_price:,.2f}",
            "data_source": "Live API" if has_valid_data else "Fallback Simulation",
            "rows": formatted_rows
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
