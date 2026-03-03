import os
import json
from supabase import create_client
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def generate_article():
    print("🖋️ 전문 아티클 생성 시작...")
    
    # 최근 24시간 내 수집된 주요 인텔리전스 확보
    yesterday = datetime.now() - timedelta(hours=24)
    res = supabase.table("raw_intelligence") \
        .select("*").gte("created_at", yesterday.isoformat()).order("created_at", desc=True).limit(10).execute()
    
    if not res.data:
        print("📭 작성할 재료(Intelligence)가 없습니다.")
        return

    context = ""
    for idx, item in enumerate(res.data):
        context += f"[{idx+1}] {item['title']} : {item['summary']}\n"

    # 오너 페르소나 주입 (Regulation Arbitrager + Blackboard Identity)
    prompt = f"""
당신은 'Blackboard'의 수석 연구원이자 'Regulation Arbitrager'입니다.
오너의 관점(비즈니스 밸류, 규제 틈새 시장, 철학적 깊이)에서 아래 뉴스들을 종합 분석하여 단 하나의 마스터피스 아티클을 작성하세요.

[수집된 데이터]
{context}

[작성 가이드라인]
1. 제목은 시장을 뒤흔들 수 있는 통찰력 있는 한 문장이어야 합니다.
2. 내용은 단순 요약이 아닌, '그래서 우리는 어떻게 움직여야 하는가?'에 집중하세요.
3. 3줄 요약(Executive Summary)을 반드시 포함하세요.
4. 전문 용어를 적절히 섞어 권위 있는 금융 전문지 느낌을 내세요.

[출력 형식 (JSON)]
{{
    "title": "...",
    "summary": "...",
    "content": "...",
    "tags": ["Regulation", "US", "KR", "Alpha"]
}}
"""
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        
        save_data = {
            "title": data["title"],
            "summary_3lines": data["summary"],
            "content": data["content"],
            "tags": data["tags"],
            "status": "DRAFT", # 관리자 검수용
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("market_reports").insert(save_data).execute()
        print(f"✅ 아티클 초안 생성 완료: {data['title']}")
        
    except Exception as e:
        print(f"❌ 생성 실패: {e}")

if __name__ == "__main__":
    generate_article()
