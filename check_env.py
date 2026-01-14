import os
from dotenv import load_dotenv
from supabase import create_client

# 1. 환경변수 로드
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"\n🔍 [환경변수 진단]")
print(f"1. URL 확인: {url}")
if url and "supabase.co" in url:
    print("   👉 URL 형식은 맞아 보입니다.")
else:
    print("   ❌ URL이 이상합니다. https://...supabase.co 형식인지 확인하세요.")

print(f"2. KEY 확인: {key[:10]}... (앞부분만 표시)")
if key and key.startswith("eyJ"):
    print("   👉 Key 형식(JWT)은 맞아 보입니다.")
else:
    print("   ❌ Key가 이상합니다. 'eyJ...'로 시작해야 합니다.")

print("\n📡 [Supabase 접속 테스트]")
try:
    supabase = create_client(url, key)
    # 아무 테이블이나 찔러보기 (데이터가 없어도 에러만 안 나면 됨)
    response = supabase.table("market_data").select("*").limit(1).execute()
    print("✅ 접속 성공! Supabase 문이 열렸습니다.")
except Exception as e:
    print(f"❌ 접속 실패: {e}")
    print("   -> .env 파일의 SUPABASE_KEY를 다시 확인하세요.")