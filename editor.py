import os
from supabase import create_client
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import time

# 1. 설정 로드
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ .env 파일 확인 필요")
    exit()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def generate_briefing():
    print("\n" + "="*50)
    print("⚡️ [안전 모드] 가장 확실한 모델로 리포트 작성 중...")
    print("="*50)
    
    # 2. DB 조회 (성공을 위해 딱 5개만 가져옵니다!)
    yesterday = datetime.now() - timedelta(days=1)
    response = supabase.table("raw_intelligence") \
        .select("*") \
        .gte("created_at", yesterday.isoformat()) \
        .order("created_at", desc=True) \
        .limit(5) \
        .execute()
    
    news_list = response.data
    
    if not news_list:
        print("📭 뉴스가 없습니다. crawler_v3.py를 먼저 돌려주세요.")
        return

    print(f"📚 기사 {len(news_list)}개를 읽고 있습니다... (가벼운 처리)")
    
    news_context = ""
    for idx, news in enumerate(news_list):
        summary = news.get('summary', '') or ''
        news_context += f"[{idx+1}] {news['title']}\n"

    # 3. 프롬프트
    prompt = f"""
    당신은 암호화폐 시장 분석가입니다. 아래 뉴스를 보고 투자자용 리포트를 작성하세요.
    
    [뉴스 목록]
    {news_context}
    
    [출력 형식 (JSON)]
    {{
        "title": "제목(이모지 포함)",
        "content": "## 시장 요약\\n내용...\\n\\n## 주요 이슈\\n내용...",
        "summary": "3줄 요약",
        "tags": ["태그1", "태그2"],
        "sentiment": "매수/매도/관망"
    }}
    """

    # 4. [핵심] 님의 리스트에 있던 '표준 별칭' 사용
    # 이게 가장 호환성이 좋고 무료 제한이 덜합니다.
    model = genai.GenerativeModel('models/gemini-flash-latest')
    
    try:
        response = model.generate_content(prompt)
        
        # JSON 변환
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        report_data = json.loads(clean_text)
        
        # DB 저장
        save_data = {
            "title": report_data["title"],
            "content": report_data["content"],
            "summary_3lines": report_data["summary"],
            "tags": report_data.get("tags", [])
        }
        supabase.table("market_reports").insert(save_data).execute()
        print(f"✅ 성공! 리포트 발행 완료: {report_data['title']}")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        if "429" in str(e):
            print("⏳ 구글 API가 '잠시만요' 라고 하네요. 1분 뒤에 다시 해보세요.")

if __name__ == "__main__":
    generate_briefing()