from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import time

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # دالة لجلب بيانات الخيارات الحقيقية (Options Chain) من ياهو فاينانس
        def get_options_data(symbol, default_price, step):
            try:
                # 1. جلب بيانات الأصول وعقود الخيارات المتاحة
                url = f"https://query1.finance.yahoo.com/v7/finance/options/{symbol}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=4) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    result = data.get('optionChain', {}).get('result', [])
                    if not result:
                        return default_price, 0, 0, []
                    
                    quote = result[0].get('quote', {})
                    underlying_price = quote.get('regularMarketPrice', default_price)
                    
                    # اختيار أقرب تاريخ استحقاق متاح في العادة (أول تاريخ في القائمة)
                    expiration_dates = result[0].get('expirationDates', [])
                    options_chain = result[0].get('options', [])
                    
                    calls_map = {}
                    puts_map = {}
                    
                    if options_chain:
                        # استخراج عقود Calls و Puts من تاريخ الاستحقاق الأول
                        opt_data = options_chain[0]
                        for c in opt_data.get('calls', []):
                            strike = c.get('strike')
                            vol = c.get('volume', 0) or 0
                            last_px = c.get('lastPrice', 0.0) or 0.0
                            calls_map[strike] = {"vol": vol, "px": last_px}
                            
                        for p in opt_data.get('puts', []):
                            strike = p.get('strike')
                            vol = p.get('volume', 0) or 0
                            last_px = p.get('lastPrice', 0.0) or 0.0
                            puts_map[strike] = {"vol": vol, "px": last_px}

                    # تحديد السترايك الأساسي والقريب من السعر الحالي
                    base_strike = round(underlying_price / step) * step
                    
                    # تحديد النطاقات حسب الأصل
                    if symbol == "%5ESPX":
                        offsets = [30, 20, 10, 0, -10, -20, -30]
                    elif symbol == "%5ENDX":
                        offsets = [75, 50, 25, 0, -25, -50, -75]
                    else:
                        offsets = [6, 4, 2, 0, -2, -4, -6]

                    rows = []
                    total_c = 0
                    total_p = 0

                    for offset in offsets:
                        s = float(base_strike + offset)
                        # البحث عن أقرب سترايك متوفر في البيانات القادمة أو افتراضي إذا لم يوجد فوليوم مسجل
                        c_info = calls_map.get(s, {"vol": 0, "px": 0.0})
                        p_info = puts_map.get(s, {"vol": 0, "px": 0.0})

                        call_v = c_info["vol"]
                        put_v = p_info["vol"]
                        
                        total_c += call_v
                        total_p += put_v

                        rows.append({
                            "strike": s,
                            "call_vol": call_v,
                            "call_px": round(c_info["px"], 2),
                            "put_vol": put_v,
                            "put_px": round(p_info["px"], 2)
                        })

                    return underlying_price, total_c, total_p, rows

            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
            
            return default_price, 0, 0, []

        # جلب البيانات الحقيقية لكل مؤشر/صندوق
        spx_p, spx_tc, spx_tp, spx_rows = get_options_data("%5ESPX", 7626.00, 10)
        ndx_p, ndx_tc, ndx_tp, ndx_rows = get_options_data("%5ENDX", 21500.00, 25)
        qqq_p, qqq_tc, qqq_tp, qqq_rows = get_options_data("QQQ", 510.00, 2)

        response_data = {
            "spx": {
                "price": f"{spx_p:,.2f}",
                "total_call_vol": spx_tc,
                "total_put_vol": spx_tp,
                "rows": spx_rows
            },
            "ndx": {
                "price": f"{ndx_p:,.2f}",
                "total_call_vol": ndx_tc,
                "total_put_vol": ndx_tp,
                "rows": ndx_rows
            },
            "qqq": {
                "price": f"{qqq_p:,.2f}",
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
