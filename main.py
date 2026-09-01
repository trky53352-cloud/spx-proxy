import requests

# ---------------------------------------------------------------
# إعدادات مؤشر SPX
# ---------------------------------------------------------------
API_TOKEN = "MHA1S3lGSGw1ZF8xekR4SlhSVXExek5CQURwaDJNWXZKc29qYzFyRHpUTT0"
UNDERLYING = "SPX"
STRIKE_RANGE = 7

BASE_URL = f"https://api.marketdata.app/v1/options/chain/{UNDERLYING}/"

def fetch_option_chain():
    params = {"token": API_TOKEN, "pm": "true"}
    response = requests.get(BASE_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    if data.get("s") != "ok":
        raise RuntimeError(f"فشل الطلب من المنصة: {data}")
    return data

def get_underlying_price(data):
    prices = data.get("underlyingPrice")
    if prices:
        return prices[0]
    return None

def build_table(data, spot_price):
    strikes = data.get("strike", [])
    sides = data.get("side", [])
    bids = data.get("bid", [])
    asks = data.get("ask", [])
    lasts = data.get("last", [])
    volumes = data.get("volume", [])
    ois = data.get("openInterest", [])

    table = {}
    for i, strike in enumerate(strikes):
        side = sides[i] if i < len(sides) else None
        if not side:
            continue
            
        entry = {
            "bid": bids[i] if i < len(bids) else 0,
            "ask": asks[i] if i < len(asks) else 0,
            "last": lasts[i] if i < len(lasts) else 0,
            "volume": volumes[i] if i < len(volumes) else 0,
            "open_interest": ois[i] if i < len(ois) else 0,
        }
        table.setdefault(strike, {})[side] = entry

    if spot_price and table.keys():
        strikes_sorted = sorted(table.keys(), key=lambda s: abs(s - spot_price))
        selected = sorted(strikes_sorted[: STRIKE_RANGE * 2 + 1], reverse=True)
    else:
        selected = sorted(table.keys(), reverse=True)[: STRIKE_RANGE * 2]

    return {s: table[s] for s in selected if s in table}

def print_table(table, spot_price):
    print("=" * 78)
    print(f" السعر الحالي المباشر لـ {UNDERLYING}: {spot_price}")
    print("=" * 78)
    print(f"{'STRIKE':<10}{'CALL VOL':<10}{'CALL PX':<10}{'PUT VOL':<10}{'PUT PX':<10}")
    print("-" * 78)

    for strike, sides in table.items():
        call = sides.get("call", {})
        put = sides.get("put", {})
        
        print(
            f"{strike:<10}"
            f"{call.get('volume', 0):<10}"
            f"{call.get('last', 0):<10.2f}"
            f"{put.get('volume', 0):<10}"
            f"{put.get('last', 0):<10.2f}"
        )
    print("=" * 78)

if __name__ == "__main__":
    try:
        chain_data = fetch_option_chain()
        spot = get_underlying_price(chain_data)
        chain_table = build_table(chain_data, spot)
        print_table(chain_table, spot)
    except Exception as e:
        print(f"حدث خطأ أثناء جلب بيانات SPX: {e}")
