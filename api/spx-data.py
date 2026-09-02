from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

API_KEY = "aFRTZHJWbk9yY0xkYWRFc2xOcXN6dTdwM0RRWjFFcGdxbS1xM1RRYUg4RT0"
BASE_URL = "https://api.marketdata.app/v1"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # إرسال التوكن عبر الـ Headers لتفادي قيود الـ IP المتغيرة
            url = f"{BASE_URL}/options/chain/SPX/?strikeCount=7"
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                }
            )
            
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
                
                strikes = data.get("strike", [])
                call_volumes = data.get("callVolume", [])
                put_volumes = data.get("putVolume", [])
                expirations = data.get("expiration", [])
                
                strikes_data = []
                limit = min(7, len(strikes))
                for i in range(limit):
                    strikes_data.append({
                        "strike": strikes[i],
                        "expiration": expirations[i] if i < len(expirations) else 0,
                        "call_volume": call_volumes[i] if i < len(call_volumes) else 0,
                        "put_volume": put_volumes[i] if i < len(put_volumes) else 0
                    })

                output = {
                    "spx_chain_7": strikes_data,
                    "status": "success"
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
                "spx_chain_7": []
            }
            self.wfile.write(json.dumps(error_output).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_output = {"error": str(e), "spx_chain_7": []}
            self.wfile.write(json.dumps(error_output).encode('utf-8'))
        return
