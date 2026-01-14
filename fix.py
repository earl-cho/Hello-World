# fix.py
import os

# 올바른 editor.py의 내용 (gemini-pro 사용)
correct_code = r"""import os
from supabase import create_client
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

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
    print("⚡️ [Gemini Pro 모드] editor.py 정상 작동 중...")
    print("="*50)
    
    # DB 조회 (15개)
    yesterday = datetime.now() - timedelta(days=1)
    response = supabase.table("raw_intelligence") \
        .select("*") \
        .gte("created_at", yesterday.isoformat()) \
        .order("created_at", desc=True) \
        .limit(15) \
        .execute()
    
    news_list = response.data
    
    if not news_list:
        print("📭 뉴스가 없습니다. crawler_v3.py를 먼저 돌려주세요.")
        return

    print(f"📚 기사 {len(news_list)}개를 읽고 리포트를 작성합니다...")
    
    news_context = ""
    for idx, news in enumerate(news_list):
        summary = news.get('summary', '') or ''
        news_context += f"[{idx+1}] {news['title']}\n"

    # 프롬프트
    prompt = f'''
    당신은 암호화폐 시장 분석가입니다. 아래 뉴스를 보고 투자자용 리포트를 작성하세요.
    [뉴스 목록]
    {news_context}
    [출력 형식 (JSON)]
    {{
        "title": "제목",
        "content": "내용",
        "summary": "3줄 요약",
        "tags": ["태그1", "태그2"]
    }}
    '''

    # [핵심] 여기가 'gemini-pro' 입니다.
    model = genai.GenerativeModel('gemini-pro')
    
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        report_data = json.loads(clean_text)
        
        save_data = {
            "title": report_data["title"],
            "content": report_data["content"],
            "summary_3lines": report_data["summary"],
            "tags": report_data["tags"]
        }
        supabase.table("market_reports").insert(save_data).execute()
        print(f"✅ 성공! 제목: {report_data['title']}")
        
    except Exception as e:
        print(f"❌ 에러: {e}")

if __name__ == "__main__":
    generate_briefing()
"""

# 현재 폴더의 editor.py를 위 내용으로 덮어씁니다.
file_path = "editor.py"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(correct_code)

print(f"✅ {os.path.abspath(file_path)} 파일이 'Gemini Pro' 버전으로 강제 업데이트 되었습니다.")
print("이제 'python editor.py'를 실행해보세요.")