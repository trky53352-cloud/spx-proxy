from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_TOKEN = "VUpqc1VmNjhpRzh2Ti14VnFFNWJicU9LdE5oQTV6TzhBQjhRZ25OdmNMTT0"
        try:
            # إضافة بارامترات تطلب أحدث بيانات متاحة
            url = f"https://api.marketdata.app/v1/options/chain/SPX/?token={API_TOKEN}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=10) as api_response:
                res_body = api_response.read().decode('utf-8')
                data = json.loads(res_body)
                
                strikes_map = {}
                
                if isinstance(data, dict):
                    strikes = data.get("strike", [])
                    # فحص عدة احتمالات لأسماء حقول الفوليوم والأسعار في الـ API
                    call_vol = data.get("callVolume") or data.get("volume", [])
                    put_vol = data.get("putVolume", [])
                    call_px = data.get("callBid") or data.get("bid", [])
                    put_px = data.get("putBid", [])

                    for i in range(len(strikes)):
                        strike_val = strikes[i]
                        if strike_val is None:
                            continue
                        
                        # نطاق واسع حول 7658 لضمان التقاط العقود النشطة
                        if 7500 <= strike_val <= 7800:
                            c_vol = call_vol[i] if i < len(call_vol) and call_vol[i] is not None else 0
                            p_vol = put_vol[i] if i < len(put_vol) and put_vol[i] is not None else 0
                            c_px = call_px[i] if i < len(call_px) and call_px[i] is not None else 0
                            p_px = put_px[i] if i < len(put_px) and put_px[i] is not None else 0

                            if strike_val not in strikes_map:
                                strikes_map[strike_val] = {
                                    "strike": strike_val,
                                    "call_vol": int(c_vol),
                                    "put_vol": int(p_vol),
                                    "call_px": float(c_px),
                                    "put_px": float(p_px)
                                }
                            else:
                                strikes_map[strike_val]["call_vol"] += int(c_vol)
                                strikes_map[strike_val]["put_vol"] += int(p_vol)

                formatted_rows = list(strikes_map.values())
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
