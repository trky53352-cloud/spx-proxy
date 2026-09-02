from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

API_KEY = "aFRTZHJWbk9yY0xkYWRFc2xOcXN6dTdwM0RRWjFFcGdxbS1xM1RRYUg4RT0"
BASE_URL = "https://api.marketdata.app/v1"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # استخدام نقطة نهاية المؤشر وأقل عدد ممكن من السترايقات لتوفير الرصيد بالكامل
            url = f"{BASE_URL}/indices/quotes/SPX/?token={API_KEY}"
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
                price_val = mid_price[0] if isinstance(mid_price, list) and len(mid_price) > 0 else data.get("price", 0)

                output = {
                    "spx": {
                        "price": price_val,
                        "status": "success",
                        "note": "Optimized lightweight request to save API credits."
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(output).encode('utf-8'))
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_output = {
                "error_code": e.code,
                "error_reason": e.reason,
                "server_response": error_body,
                "spx": {"price": 0}
            }
            self.wfile.write(json.dumps(error_output).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_output = {"error": str(e), "spx": {"price": 0}}
            self.wfile.write(json.dumps(error_output).encode('utf-8'))
        return
