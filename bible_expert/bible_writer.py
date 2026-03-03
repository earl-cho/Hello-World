import os
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# 환경 변수 로드
load_dotenv()

# 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BIBLE_PATH = "/Users/earl/Blackboard/regulation_bible_v4_0.md"
PERSONA_PATH = "/Users/earl/Blackboard/bible_expert/PERSONA.md"

# 모델 설정 (가장 최신 안정 버전 사용)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def get_recent_intelligence():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # 최근 24시간 내의 고가치 인텔리전스 추출
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    response = supabase.table("raw_intelligence") \
        .select("*") \
        .gt("created_at", yesterday) \
        .order("created_at", desc=True) \
        .execute()
    return response.data

def generate_bible_update(intelligence_data, persona_content, current_bible):
    prompt = f"""
당신은 'Regulation Arbitrager' 페르소나를 가진 전문 규제 리포터입니다.
아래의 [페르소나 지침]과 [현재 바이블 내용]을 바탕으로, 새롭게 수집된 [인텔리전스 데이터]를 분석하여 바이블을 업데이트하세요.

[페르소나 지침]
{persona_content}

[현재 바이블 내용]
{current_bible[:2000]}... (중략)

[인텔리전스 데이터]
{json.dumps(intelligence_data, ensure_ascii=False)}

[작성 지침]
1. '금주 업데이트' 섹션에 추가할 요약 포인트를 작성하세요. (날짜 포함)
2. 본문의 해당 국가/섹션에 심층 분석 내용을 추가하세요. 단순 요약이 아닌 비즈니스 임팩트와 오너의 철학이 담긴 분석이어야 합니다.
3. 기존 내용을 삭제하지 말고, 새로운 통찰을 덧붙이는 방식으로 확장하세요.
4. 반드시 한국어로 작성하세요.
"""
    response = model.generate_content(prompt)
    return response.text

def apply_updates(new_content):
    with open(BIBLE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 7일 주 관리 로직: '금주 업데이트' 섹션에서 7일이 지난 항목 자동 아카이빙/삭제
    lines = content.split('\n')
    new_lines = []
    in_weekly_section = False
    
    # 날짜 기준 계산
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    for line in lines:
        if "## 금주 업데이트" in line:
            in_weekly_section = True
            new_lines.append(line)
            continue
        
        if in_weekly_section and line.startswith("---"):
            in_weekly_section = False
            
        if in_weekly_section and line.startswith("-"):
            # 날짜 추출 시도 (YYYY-MM-DD 형식 예상)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date_match:
                item_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                if item_date < seven_days_ago:
                    continue # 7일 지난 항목은 제외
        
        new_lines.append(line)

    # 신규 내용 통합 (이 부분은 페르소나에 따른 정교한 병합 로직이 필요함)
    # 여기서는 단순 예시로 전체 업데이트된 텍스트를 반환받아 처리한다고 가정
    final_content = new_content # AI가 생성한 전체 문서를 그대로 사용하거나 로직에 따라 병합

    with open(BIBLE_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content)

if __name__ == "__main__":
    print(f"[{datetime.now()}] Regulation Bible Update Started...")
    
    with open(PERSONA_PATH, 'r', encoding='utf-8') as f:
        persona = f.read()
    
    with open(BIBLE_PATH, 'r', encoding='utf-8') as f:
        bible = f.read()
        
    intel = get_recent_intelligence()
    if intel:
        new_bible = generate_bible_update(intel, persona, bible)
        apply_updates(new_bible)
        print("Update Completed successfully.")
    else:
        print("No new intelligence found.")
