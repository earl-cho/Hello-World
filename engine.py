# engine.py (가격 수집 전용)
import os
import time
import requests
from supabase import create_client
from dotenv import load_dotenv

# 1. 설정 로드
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ .env 파일 오류: 키가 없습니다.")
    exit()

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Supabase 연결 실패: {e}")
    exit()

def get_bitcoin_price():
    """바이낸스에서 비트코인 가격 조회"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"⚠️ 가격 조회 실패: {e}")
        return None

def main():
    print("🚀 [Engine Start] 비트코인 가격 수집기를 가동합니다...")
    print("   (종료하려면 Ctrl+C를 누르세요)")
    
    while True:
        price = get_bitcoin_price()
        
        if price:
            try:
                # DB 저장
                data = {"symbol": "BTC", "price": price}
                supabase.table("market_data").insert(data).execute()
                print(f"✅ 저장 완료: ${price:,.2f}")
            except Exception as e:
                # 여기서 401 에러가 나면 키가 틀린 것임
                print(f"❌ DB 저장 실패: {e}")
                if "401" in str(e):
                    print("🚨 치명적 오류: API 키가 틀렸습니다. .env를 확인하세요.")
                    break
        
        # 5분 대기 (테스트할 땐 10초로 줄여도 됨)
        time.sleep(300) 

if __name__ == "__main__":
    main()