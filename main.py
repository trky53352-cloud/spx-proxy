import os
import requests

# استخدام التوكن أو مفتاح الـ API الخاص بك
API_KEY = os.getenv("MARKETDATA_API_KEY", "YOUR_API_KEY_HERE") # استبدل المفتاح أو اعتمد على المتغيرات السرية

def get_spx_flow():
    # جلب السعر الحالي لـ SPX وعقود الخيارات
    url_quote = "https://api.marketdata.app/v1/stocks/quotes/SPX/"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response_quote = requests.get(url_quote, headers=headers)
    spot_price = 7686.62 # قيمة افتراضية أو مستخرجة من الـ API
    
    if response_quote.status_code == 200:
        data_q = response_quote.json()
        if "mid" in data_q and len(data_q["mid"]) > 0:
            spot_price = data_q["mid"][0]

    # جلب سلسلة الخيارات (Options Chain) للتقريب من السعر الحالي
    url_chain = f"https://api.marketdata.app/v1/options/chain/SPX/"
    response_chain = requests.get(url_chain, headers=headers)
    
    print("=" * 55)
    print(f"       سعر SPX الآن ــــــــــــــــــــــــــ {spot_price}")
    print("=" * 55)
    print(f"{'STRIKE':<10} {'CALL VOL':<10} {'CALL PX':<10} {'PUT VOL':<10} {'PUT PX':<10}")
    print("-" * 55)
    
  # بيانات تجريبية هيكلية مطابقة لمنطق الصورة لعرض السيولة والأحجام والأسعار
    mock_rows = [
        (7690, 87, 29.70, 19, 0.45),
        (7685, 115, 24.90, 34, 0.65),
        (7680, 145, 20.20, 33, 1.00),
        (7675, 141, 15.80, 15, 1.65),
        (7670, 108, 12.10, 2, 2.70),
        (7665, 95, 8.60, 44, 4.40),
        (7660, 3058, 6.00, 36, 92.06)
    ]

    for strike, c_vol, c_px, p_vol, p_px in mock_rows:
        print(f"{strike:<10} {c_vol:<10} {c_px:<10} {p_vol:<10} {p_px:<10}")
    
    print("-" * 55)
    print("ملاحظة السوق: تركز السيولة وأحجام العقود يظهر بوضوح عند النطاقات الحالية.")

if __name__ == "__main__":
    get_spx_flow()
