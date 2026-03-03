import os
from supabase import create_client
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import random

# 1. 설정 로드
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY: exit()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# [자산] 고화질 썸네일 라이브러리 (Unsplash)
# ---------------------------------------------------------
IMAGE_ASSETS = {
    "REGULATION": [
        "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&w=800&q=80", # 법봉
        "https://images.unsplash.com/photo-1555881400-74d7acaacd25?auto=format&fit=crop&w=800&q=80", # 문서
        "https://images.unsplash.com/photo-1521791055366-0d553872125f?auto=format&fit=crop&w=800&q=80", # 정장
        "https://images.unsplash.com/photo-1577415124269-fc1140a69e91?auto=format&fit=crop&w=800&q=80"  # 의회
    ],
    "BITCOIN": [
        "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&w=800&q=80", # BTC 실물
        "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=800&q=80", # BTC 골드
        "https://images.unsplash.com/photo-1591994843349-f415893b3a6b?auto=format&fit=crop&w=800&q=80"  # 차트
    ],
    "ENTERPRISE": [
        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80", # 빌딩
        "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=800&q=80", # 회의
        "https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&w=800&q=80"  # 월가
    ],
    "TECH": [
        "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=800&q=80", # 블록체인
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80", # 보안
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"  # 서버
    ]
}

def pick_thumbnail(title, tags, content):
    """AI가 작성한 글을 분석해 가장 적절한 사진 선택"""
    text = (title + str(tags) + content).upper()
    
    # 키워드 우선순위 매칭
    if any(x in text for x in ["SEC", "LAW", "REGULATION", "BIDEN", "TRUMP", "KOREA", "FSC", "국회", "규제"]):
        return random.choice(IMAGE_ASSETS["REGULATION"])
    elif any(x in text for x in ["ETF", "BANK", "BLACKROCK", "FUND", "INSTITUTIONAL", "기업", "기관"]):
        return random.choice(IMAGE_ASSETS["ENTERPRISE"])
    elif any(x in text for x in ["BITCOIN", "BTC", "PRICE", "CHART", "가격"]):
        return random.choice(IMAGE_ASSETS["BITCOIN"])
    else:
        return random.choice(IMAGE_ASSETS["TECH"])

def generate_briefing():
    print("\n" + "="*60)
    print("🎩 [Editor] 블랙록 수석 전략가 모드로 분석 중...")
    print("="*60)
    
    # 1. 뉴스 데이터 확보 (최근 48시간)
    yesterday = datetime.now() - timedelta(hours=48)
    response = supabase.table("raw_intelligence") \
        .select("*").gte("created_at", yesterday.isoformat()).order("created_at", desc=True).limit(40).execute()
    
    news_list = response.data
    if not news_list:
        print("📭 분석할 뉴스가 부족합니다.")
        return

    # 2. 컨텍스트 주입
    news_context = ""
    for idx, news in enumerate(news_list):
        news_context += f"[{idx+1}] {news['title']} - {news.get('summary', '')}\n"

    # 3. [핵심] 고지능 프롬프트 (High-Context Prompt)
    # 대시보드(app.py)가 섹터별로 분류할 수 있도록 태그 생성을 유도합니다.
    prompt = f"""
    당신은 월스트리트 자산운용사(BlackRock)의 '수석 크립토 전략가'입니다.
    고객(기관 투자자)에게 보낼 Daily Market Brief를 작성하십시오.
    
    [입력된 뉴스 데이터]
    {news_context}
    
    [작성 가이드라인 - 엄수]
    1. **Tone & Manner:** 냉철하고, 분석적이며, 전문적인 금융 용어를 사용하십시오. (이모지 절대 금지)
    2. **Insight:** 단순 뉴스 나열이 아닌, '이것이 시장에 미칠 영향(Implication)'을 분석하십시오.
    3. **Tags:** 다음 키워드 중 주제에 맞는 것을 반드시 포함하십시오: 
       ['Regulation', 'Enterprise', 'Crypto Native', 'Korea', 'Japan', 'US', 'Macro']
       (이 태그는 시스템이 기사를 분류하는 데 사용됩니다.)

    [출력 포맷 (JSON Only)]
    {{
        "title": "시선을 끄는 통찰력 있는 제목 (한글)",
        "content": "## Executive Summary\\n(3줄 요약)\\n\\n## Market Analysis\\n(본문 내용: 거시경제, 규제, 기관 동향 위주 서술)",
        "summary": "대시보드 노출용 3줄 핵심 요약",
        "tags": ["Tag1", "Tag2", "Tag3"]
    }}
    """

    model = genai.GenerativeModel('models/gemini-flash-latest')
    
    try:
        # AI 생성
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        report_data = json.loads(clean_text)
        
        # 4. 이미지 매칭 (AI가 쓴 글을 보고 선택)
        image_url = pick_thumbnail(report_data["title"], report_data.get("tags", []), report_data["content"])
        
        # 5. DB 저장
        save_data = {
            "title": report_data["title"],
            "content": report_data["content"],
            "summary_3lines": report_data["summary"],
            "tags": report_data.get("tags", []),
            "image_url": image_url
        }
        
        supabase.table("market_reports").insert(save_data).execute()
        print(f"✅ 리포트 발행 완료: {report_data['title']}")
        print(f"   (태그: {report_data.get('tags')})")
        print(f"   (이미지: {image_url})")
        
    except Exception as e:
        print(f"❌ 생성 실패: {e}")

if __name__ == "__main__":
    generate_briefing()