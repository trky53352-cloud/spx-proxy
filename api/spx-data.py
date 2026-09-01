from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. جلب سعر SPX
        spx_price = 7626.00
        try:
            req = urllib.request.Request("https://query1.finance.yahoo.com/v1/finance/quote?symbols=%5ESPX", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                val = data.get('quoteResponse', {}).get('result', [{}])[0].get('regularMarketPrice')
                if val: spx_price = float(val)
        except Exception:
            pass

        # 2. جلب سعر ناسداك (NDX)
        ndx_price = 21500.00
        try:
            req = urllib.request.Request("https://query1.finance.yahoo.com/v1/finance/quote?symbols=%5ENDX", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                val = data.get('quoteResponse', {}).get('result', [{}])[0].get('regularMarketPrice')
                if val: ndx_price = float(val)
        except Exception:
            pass

        # دالة لتوليد صفوف السترايكات
        def generate_rows(price, step, offsets):
            base_strike = round(price / step) * step
            rows = []
            total_c = 0
            total_p = 0
            for i, offset in enumerate(offsets):
                s = float(base_strike + offset)
                dist = abs(s - price)
                call_v = max(35000, int(145000 - (dist * (2500 if step == 5 else 1000)) + (i * 2000)))
                put_v = max(28000, int(120000 - (dist * (2200 if step == 5 else 900)) - (i * 1000)))
                total_c += call_v
                total_p += put_v
                rows.append({
                    "strike": s,
                    "call_vol": call_v,
                    "call_px": round(max(0.5, 45.0 - (offset * 1.2)), 2),
                    "put_vol": put_v,
                    "put_px": round(max(0.5, 25.0 + (offset * 1.2)), 2)
                })
            return rows, total_c, total_p

        spx_rows, spx_tc, spx_tp = generate_rows(spx_price, 5, [15, 10, 5, 0, -5, -10, -15])
        ndx_rows, ndx_tc, ndx_tp = generate_rows(ndx_price, 25, [75, 50, 25, 0, -25, -50, -75])

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
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
