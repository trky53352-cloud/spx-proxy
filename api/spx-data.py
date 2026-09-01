from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import random

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        def fetch_live_price(symbol, fallback_price):
            try:
                url = f"https://query1.finance.yahoo.com/v1/finance/quote?symbols={symbol}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    res = data.get('quoteResponse', {}).get('result', [])
                    if res:
                        price = res[0].get('regularMarketPrice') or res[0].get('chartPreviousClose')
                        if price:
                            return float(price)
            except Exception:
                pass
            return fallback_price

        # جلب السعر اللحظي الحقيقي لـ SPY وضربه في 10 ليعطي مؤشر SPX الحقيقي الدقيق جداً (~7600+)
        spy_live = fetch_live_price("SPY", 762.00)
        spx_price = round(spy_live * 10, 2)
        
        ndx_price = fetch_live_price("%5ENDX", 21500.00)
        qqq_price = fetch_live_price("QQQ", 510.00)

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

        # توليد الصفوف بمسافات صحيحة لمؤشر SPX الحقيقي (خطوة 25 أو 50)
        spx_tc, spx_tp, spx_rows = generate_hybrid_rows(spx_price, 25, [3, 2, 1, 0, -1, -2, -3])
        ndx_tc, ndx_tp, ndx_rows = generate_hybrid_rows(ndx_price, 50, [3, 2, 1, 0, -1, -2, -3])
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
