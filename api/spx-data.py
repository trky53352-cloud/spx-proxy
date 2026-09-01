from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_TOKEN = "VUpqc1VmNjhpRzh2Ti14VnFFNWJicU9LdE5oQTV6TzhBQjhRZ25OdmNMTT0"
        try:
            url = f"https://api.marketdata.app/v1/options/chain/SPX/?token={API_TOKEN}"
            
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=10) as api_response:
                res_body = api_response.read().decode('utf-8')
                data = json.loads(res_body)
                
                formatted_rows = []
                if isinstance(data, dict):
                    strikes = data.get("strike", [])
                    call_vol = data.get("callVolume", [])
                    put_vol = data.get("putVolume", [])
                    call_px = data.get("callBid", [])
                    put_px = data.get("putBid", [])

                    for i in range(len(strikes)):
                        formatted_rows.append({
                            "strike": strikes[i],
                            "call_vol": call_vol[i] if i < len(call_vol) else 0,
                            "put_vol": put_vol[i] if i < len(put_vol) else 0,
                            "call_px": call_px[i] if i < len(call_px) else 0,
                            "put_px": put_px[i] if i < len(put_px) else 0
                        })

                response_data = {
                    "spx_price": "7,686.62",
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
