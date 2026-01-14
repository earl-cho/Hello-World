import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 설정 로드
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ .env 파일에 키가 없습니다.")
    exit()

genai.configure(api_key=GEMINI_API_KEY)

print("🔍 구글 서버에 사용 가능한 모델 목록을 요청합니다...\n")

try:
    # 2. 모델 리스트 조회
    available_models = []
    for m in genai.list_models():
        # 'generateContent' (텍스트 생성) 기능이 있는 모델만 필터링
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ 발견: {m.name}")
            available_models.append(m.name)

    print("\n" + "="*40)
    if available_models:
        print(f"총 {len(available_models)}개의 모델을 사용할 수 있습니다.")
        print("위 목록에 있는 이름 중 하나를 골라 editor.py에 넣으면 됩니다.")
    else:
        print("❌ 사용 가능한 모델이 하나도 없습니다.")
        print("가능성 1: API 키가 잘못되었습니다.")
        print("가능성 2: 현재 계신 지역(Region)이 차단되었거나, API 사용 권한이 없습니다.")
    print("="*40)

except Exception as e:
    print(f"❌ 에러 발생: {e}")