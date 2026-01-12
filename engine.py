import ccxt
import time
from supabase import create_client
from datetime import datetime

# ---------------------------------------------------------
# [설정] Supabase 프로젝트 키 (따옴표 안에 복사한 값을 넣으세요)
# ---------------------------------------------------------
SUPABASE_URL = 'https://hrfqvipwxuqssnnwowno.supabase.co'
SUPABASE_KEY = 'sb_publishable_Sdz_-3XX4Y05hgcBHooRPw_yufksqyO'

# DB 연결
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 바이낸스 거래소 연결 (데이터 가져오는 곳)
exchange = ccxt.binance()

def fetch_and_save():
    try:
        # 1. 바이낸스에서 비트코인 가격 조회
        ticker = exchange.fetch_ticker('BTC/USDT')
        current_price = ticker['last']
        
        # 2. 펀딩비 조회 (선물 시장 데이터)
        # 현물(Spot)에는 펀딩비가 없어서 예외처리 하거나, 선물(Swap) 시장을 봐야 함
        # 일단은 가격만 먼저 저장해서 테스트
        
        print(f"💰 현재 BTC 가격: {current_price} USDT")

        # 3. 데이터 포장
        data = {
            "ticker": "BTC/USDT",
            "price": current_price,
            "created_at": datetime.utcnow().isoformat()
        }

        # 4. Supabase(DB)로 쏘기!
        # 'market_data' 테이블이 없으면 에러가 납니다. (Table 생성 필수)
        response = supabase.table("market_data").insert(data).execute()
        print("✅ DB 저장 완료!")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

# ---------------------------------------------------------
# [실행] 10초마다 반복 (테스트용)
# ---------------------------------------------------------
print("🚀 블랙보드 데이터 엔진 시동 중...")
while True:
    fetch_and_save()
    time.sleep(10) # 10초 휴식