import os
import json
from supabase import create_client
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# 핵심 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 모델 설정 (최신 안정 버전 및 정교한 파라미터 적용)
genai.configure(api_key=GEMINI_API_KEY)
# [🛡️ PARAMETER TUNING] 사실성 강화를 위해 temperature를 낮게 유지
model = genai.GenerativeModel('gemini-2.0-flash', generation_config={"temperature": 0.3})

def get_latest_intelligence():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. 수집된 인텔리전스 가져오기
    intel_response = supabase.table("raw_intelligence") \
        .select("*") \
        .order("created_at", desc=True) \
        .limit(20) \
        .execute()
    
    # 2. 최근 7일간 발행된 리포트 가져오기 (중복 방지용)
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    past_reports = supabase.table("market_reports") \
        .select("title, summary_3lines") \
        .gt("created_at", seven_days_ago) \
        .execute()
    
    return intel_response.data, past_reports.data

def generate_masterpiece():
    print("🎨 [Blackboard Masterpiece Writer] 집필을 시작합니다...")
    
    raw_intel, past_reports = get_latest_intelligence()
    if not raw_intel:
        print("📭 분석할 인텔리전스가 없습니다.")
        return

    # 컨텍스트 구성 (content가 없을 경우 summary를 대안으로 사용)
    context_list = []
    for i, item in enumerate(raw_intel):
        text_body = item.get('content') or item.get('summary') or ""
        context_list.append(f"[{i+1}] {item['title']}: {text_body[:500]}")
    
    context = "\n".join(context_list)
    past_context = "\n".join([f"- {r['title']}" for r in past_reports])

    # [🔥 MASTERPIECE PROMPT - 100% OWNER CUSTOMIZED]
    prompt = f"""
당신은 'Blackboard'의 수석 연구위원이자 오너 Earl의 페르소나를 완벽히 계승한 'Regulation Arbitrager'입니다.
단순한 기사 작성이 아닌, 오직 오너의 관점(비즈니스 밸류, 규제 틈새 시장, 철학적 깊이)에서 단 하나의 **'마스터피스(Masterpiece)'** 아티클을 작성하십시오.

[🛡️ ZERO HALLUCINATION POLICY - STRICT ENFORCEMENT]
1. 없는 사실을 지어내지 마십시오. (소스 텍스트에 기반한 사실만 기술)
2. 근거 없는 낙관이나 추측성 보도를 배제하십시오.
3. 깊이가 부족한 내용은 아예 다루지 마십시오.

[🚫 ANTI-REPETITION & 7-DAY RULE]
1. 아래 [최근 7일간 다룬 주제]와 겹치는 내용은 새로운 업데이트가 없는 한 절대 반복하지 마십시오.
2. 과거 사례를 인용할 때는 "지난번 대비 어떤 변화가 있는가?"라는 '진화적 분석'이 포함되어야 합니다.

[작성 가이드라인]
1. **Headline**: 시장의 본질을 꿰뚫는 강력하고 권위 있는 한 줄.
2. **Executive Summary**: 바쁜 오너들을 위한 날카로운 3줄 요약.
3. **Deep Deep Analysis**: 
   - 'Contextual Connection': 뉴스 데이터를 거시 경제 및 규제 흐름과 연결.
   - 'Business Implication': "그래서 우리는 어떻게 움직여야 하는가?"에 대한 답.
4. **Tone**: 냉철하고 분석적인 금융 전문지 전문기자 톤 (이모지 절대 금지).

[최근 7일간 다룬 주제]
{past_context}

[취재 데이터]
{context}

---
내용의 깊이가 얕거나 중복이 심해 발행할 가치가 없다고 판단되면, JSON 형식 대신 오직 "SKIP" 이라는 단어 하나만 출력하십시오.
---

[출력 형식 (JSON)]
{{
    "title": "...",
    "summary": "...",
    "content": "## Executive Summary\\n...\\n\\n## Decision Context\\n...\\n\\n## Strategic Implication\\n...",
    "tags": ["Regulation", "Enterprise", "US", "KR", "Alpha"]
}}
"""

    response = model.generate_content(prompt)
    response_text = response.text.strip()

    if response_text == "SKIP":
        print("⚠️ [SKIP] 현재 충분한 깊이의 인사이트가 확보되지 않아 발행을 보류합니다.")
        return

    try:
        # JSON 정제 및 변환
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        # DB 저장 (market_reports 테이블)
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        save_data = {
            "title": data["title"],
            "summary_3lines": data["summary"],
            "content": data["content"],
            "tags": data.get("tags", []),
            "created_at": datetime.now().isoformat()
        }
        supabase.table("market_reports").insert(save_data).execute()
        print(f"✅ [MASTERPIECE] 발행 성공: {data['title']}")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print("AI 원본 응답:", response.text)

if __name__ == "__main__":
    generate_masterpiece()
