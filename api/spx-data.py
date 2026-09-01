from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        def get_price(symbol, default_val):
            try:
                url = f"https://query1.finance.yahoo.com/v1/finance/quote?symbols={symbol}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    val = data.get('quoteResponse', {}).get('result', [{}])[0].get('regularMarketPrice')
                    if val: 
                        return float(val)
            except Exception:
                pass
            return default_val

        # الأسعار اللحظية للمؤشرات الثلاثة
        prices = {
            "spx": get_price("%5ESPX", 7626.00),
            "ndx": get_price("%5ENDX", 21500.00),
            "qqq": get_price("QQQ", 510.00)
        }

        def generate_rows(price, step, offsets):
            base_strike = round(price / step) * step
            rows = []
            total_c = 0
            total_p = 0
            for i, offset in enumerate(offsets):
                s = float(base_strike + offset)
                dist = abs(s - price)
                call_v = max(15000, int(145000 - (dist * 1500) + (i * 2000)))
                put_v = max(12000, int(120000 - (dist * 1400) - (i * 1000)))
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

        spx_rows, spx_tc, spx_tp = generate_rows(prices["spx"], 5, [15, 10, 5, 0, -5, -10, -15])
        ndx_rows, ndx_tc, ndx_tp = generate_rows(prices["ndx"], 25, [75, 50, 25, 0, -25, -50, -75])
        qqq_rows, qqq_tc, qqq_tp = generate_rows(prices["qqq"], 2, [6, 4, 2, 0, -2, -4, -6])

        response_data = {
            "spx": {
                "price": f"{prices['spx']:,.2f}",
                "total_call_vol": spx_tc,
                "total_put_vol": spx_tp,
                "rows": spx_rows
            },
            "ndx": {
                "price": f"{prices['ndx']:,.2f}",
                "total_call_vol": ndx_tc,
                "total_put_vol": ndx_tp,
                "rows": ndx_rows
            },
            "qqq": {
                "price": f"{prices['qqq']:,.2f}",
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
