from http.server import BaseHTTPRequestHandler
import json
import urllib.request

API_KEY = "RDVyUkF0dzBKMnFFV1h5RVV5N1FrSzJoRzBKQUtnN0puaEFmc093Ulkzcz0="
BASE_URL = "https://api.marketdata.app/v1"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # تمرير المفتاح مباشرة عبر الـ URL لتجنب رفض الـ Header
            url = f"{BASE_URL}/options/quotes/SPX/?token={API_KEY}"
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json"
                }
            )
            
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
                
                mid_price = data.get("mid", [0])
                price_val = mid_price[0] if isinstance(mid_price, list) and len(mid_price) > 0 else 0.0
                
                call_volumes = data.get("callVolume", [0])
                put_volumes = data.get("putVolume", [0])
                
                total_call_vol = sum(call_volumes) if isinstance(call_volumes, list) else 0
                total_put_vol = sum(put_volumes) if isinstance(put_volumes, list) else 0

                output = {
                    "spx": {
                        "price": price_val,
                        "total_call_vol": total_call_vol,
                        "total_put_vol": total_put_vol,
                        "status": "success"
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(output).encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_output = {"error": str(e), "spx": {"price": 0, "total_call_vol": 0, "total_put_vol": 0}}
            self.wfile.write(json.dumps(error_output).encode('utf-8'))
        return
