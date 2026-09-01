from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_TOKEN = "VUpqc1VmNjhpRzh2Ti14VnFFNWJicU9LdE5oQTV6TzhBQjhRZ25OdmNMTT0"
        
        # 1. جلب سعر SPX المباشر والحقيقي من السوق لضمان الحركة الفورية
        underlying_price = 7658.00
        try:
            yf_url = "https://query1.finance.yahoo.com/v1/finance/quote?symbols=%5ESPX"
            yf_req = urllib.request.Request(yf_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(yf_req, timeout=4) as yf_resp:
                yf_data = json.loads(yf_resp.read().decode('utf-8'))
                price_val = yf_data.get('quoteResponse', {}).get('result', [{}])[0].get('regularMarketPrice')
                if price_val:
                    underlying_price = float(price_val)
        except Exception:
            pass

        # 2. بناء السترايكات ديناميكياً بناءً على السعر الحقيقي الحالي
        base_strike = round(underlying_price / 5) * 5
        formatted_rows = []
        offsets = [10, 5, 0, -5, -10, -15]
        for offset in offsets:
            s = base_strike + offset
            dist = abs(s - underlying_price)
            c_vol = int(max(100, 5000 - dist * 200))
            p_vol = int(max(80, 4000 - dist * 180))
            c_px = round(max(5.0, 80.0 - offset * 1.5), 1)
            p_px = round(max(5.0, 50.0 + offset * 1.5), 1)
            
            formatted_rows.append({
                "strike": float(s),
                "call_vol": c_vol,
                "call_px": c_px,
                "put_vol": p_vol,
                "put_px": p_px
            })

        # 3. محاولة دمج بيانات العقود الحية إن وجدت
        try:
            url = f"https://api.marketdata.app/v1/options/chain/SPX/?token={API_TOKEN}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=5) as api_response:
                res_body = api_response.read().decode('utf-8')
                data = json.loads(res_body)
                
                if isinstance(data, dict):
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
