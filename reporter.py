import os
import streamlit as st # secrets를 쓰기 위해 추가
from supabase import create_client
import google.generativeai as genai
from serpapi import GoogleSearch
import json
from datetime import datetime

# ===============================================================
# [보안 설정] Secrets에서 키 가져오기 (이제 해킹 걱정 없음!)
# ===============================================================
# 내 컴퓨터에서는 .streamlit/secrets.toml 에서 가져오고,
# 웹사이트에서는 아까 설정한 Secrets에서 가져옵니다.
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
except FileNotFoundError:
    print("❌ 에러: .streamlit/secrets.toml 파일을 찾을 수 없습니다.")
    exit()
# ===============================================================

# 1. 연결 설정
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_latest_price():
    """DB에서 가장 최근 비트코인 가격을 가져옵니다."""
    response = supabase.table("market_data") \
        .select("*").order("created_at", desc=True).limit(1).execute()
    if response.data:
        return response.data[0]['price']
    return 0

def get_news():
    """구글에서 최신 비트코인 뉴스를 3개 긁어옵니다."""
    params = {
        "engine": "google_news",
        "q": "Bitcoin crypto market", # 검색어
        "gl": "kr", # 지역: 한국
        "hl": "ko", # 언어: 한국어
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    news_results = results.get("news_results", [])[:3] # 상위 3개만
    
    news_text = ""
    for i, news in enumerate(news_results):
        news_text += f"{i+1}. {news.get('title')} ({news.get('source')})\n"
    
    return news_text

def analyze_and_report():
    print("🕵️ AI 기자가 취재를 시작합니다...")
    
    # 데이터 수집
    price = get_latest_price()
    news = get_news()
    
    if not news:
        print("❌ 뉴스를 못 찾았습니다.")
        return

    print(f"💰 현재 가격: ${price:,.2f}")
    print(f"📰 수집된 뉴스:\n{news}")

    # AI에게 지시 (프롬프트 엔지니어링)
    prompt = f"""
    당신은 전설적인 암호화폐 시장 분석가입니다.
    현재 비트코인 가격은 ${price:,.2f} 입니다.
    
    최신 뉴스 헤드라인입니다:
    {news}
    
    위 정보를 바탕으로 투자자를 위한 '시장 분석 리포트'를 작성해주세요.
    반드시 다음 JSON 형식으로만 답변하세요 (다른 말 하지 마세요):
    {{
        "title": "자극적이고 클릭을 유도하는 멋진 제목",
        "content": "3줄 요약 스타일의 핵심 분석 내용 (이모지 포함)",
        "sentiment": "매수 / 매도 / 관망 중 하나 선택"
    }}
    """

    # Gemini에게 생각 요청
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    try:
        # JSON 변환 (AI가 가끔 ```json ... ``` 을 붙일 때가 있어서 제거)
        clean_text = response.text.replace("```json", "").replace("```", "")
        report_data = json.loads(clean_text)
        
        # DB에 저장
        data = {
            "title": report_data["title"],
            "content": report_data["content"],
            "sentiment": report_data["sentiment"],
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("ai_reports").insert(data).execute()
        print("✅ 기사 송고 완료! (DB 저장 성공)")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print("AI 원본 응답:", response.text)

if __name__ == "__main__":
    analyze_and_report()