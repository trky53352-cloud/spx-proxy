from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import os
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # استبدل هذه المفاتيح بقيم حسابك أو اجعلها تُقرأ من متغيرات البيئة
        API_KEY = os.environ.get("APCA_API_KEY_ID", "YOUR_API_KEY")
        API_SECRET = os.environ.get("APCA_API_SECRET_KEY", "YOUR_SECRET_KEY")
        
        # استخدام رابط الـ Live أو Paper حسب حسابك (افتراضي Live Data endpoint)
        BASE_URL = "https://data.alpaca.markets/v2/stocks"

        def fetch_alpaca_price(symbol, fallback_price):
            try:
                url = f"{BASE_URL}/{symbol}/quotes/latest"
                req = urllib.request.Request(url, headers={
                    'APCA-API-KEY-ID': API_KEY,
                    'APCA-API-SECRET-KEY': API_SECRET,
                    'Accept': 'application/json'
                })
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    # استخراج سعر الـ Ask أو Bid أو الأخير من Alpaca
                    quote = data.get('quote', {})
                    price = quote.get('ap') or quote.get('bp') or quote.get('p')
                    if price:
                        return float(price)
            except Exception as e:
                print(f"Alpaca Error for {symbol}: {e}")
            return fallback_price

        # جلب الأسعار اللحظية الحقيقية من Alpaca
        spy_live = fetch_alpaca_price("SPY", 762.00)
        spx_price = round(spy_live * 10, 2)
        
        qqq_price = fetch_alpaca_price("QQQ", 707.77)
        ndx_price = round(qqq_price * 30.5, 2)

        def generate_hybrid_rows(price, step, offsets):
            base_strike = round(price / step) * step
            rows = []
            total_c = 0
            total_p = 0
            
            for i, offset in enumerate(offsets):
                s = float(base_strike + (offset * step))
                dist = abs(s - price)
                
                call_v = int(max(25000, 150000 - (dist * 2000) + random.randint(-5000, 5000)))
                put_v = int(max(20000, 130000 - (dist * 1800) + random.randint(-4000, 4000)))
                
                total_c += call_v
                total_p += put_v
                
                rows.append({
                    "strike": s,
                    "call_vol": call_v,
                    "call_px": round(max(0.5, 30.0 - (abs(offset) * 1.5)), 2),
                    "put_vol": put_v,
                    "put_px": round(max(0.5, 20.0 + (abs(offset) * 1.5)), 2)
                })
                
            return total_c, total_p, rows

        spx_tc, spx_tp, spx_rows = generate_hybrid_rows(spx_price, 5, [3, 2, 1, 0, -1, -2, -3])
        ndx_tc, ndx_tp, ndx_rows = generate_hybrid_rows(ndx_price, 100, [3, 2, 1, 0, -1, -2, -3])
        qqq_tc, qqq_tp, qqq_rows = generate_hybrid_rows(qqq_price, 2, [3, 2, 1, 0, -1, -2, -3])

        response_data = {
            "spx": {
                "price": f"{spx_price:,.2f}",
                "total_call_vol": spx_tc,
                "total_put_vol": spx_tp,
                "rows": spx_rows
            },
            "ndx": {
                "price": f"{ndx_price:,.2f}",
                "total_call_vol": ndx_tc,
                "total_put_vol": ndx_tp,
                "rows": ndx_rows
            },
            "qqq": {
                "price": f"{qqq_price:,.2f}",
                "total_call_vol": qqq_tc,
                "total_put_vol": qqq_tp,
                "rows": qqq_rows
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
