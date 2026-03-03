import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 설정
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def crawl_sbi():
    print("🚀 SBI 금융경제연구소 수집 시작...")
    # 실제 SBI 리서치 URL (예시: http://www.sbi-rc.jp/ or 한국 관련 섹션)
    # 여기서는 오너님이 지정하신 한국/일본 규제 관련 소스를 크롤링한다고 가정
    url = "http://www.sbi-rc.jp/report/" 
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # SBI 리서치 특유의 리스트 구조 파싱 (사이트 구조에 맞게 조정됨)
        items = soup.select('.report_list li') # 예시 셀렉터
        
        for item in items:
            try:
                title = item.select_one('.title').text.strip()
                link = "http://www.sbi-rc.jp" + item.select_one('a')['href']
                date_str = item.select_one('.date').text.strip()
                
                # 중복 체크 및 저장
                existing = supabase.table("raw_intelligence") \
                    .select("id").eq("link", link).execute()
                
                if not existing.data:
                    data = {
                        "source": "SBI Research",
                        "title": f"[SBI] {title}",
                        "link": link,
                        "summary": f"SBI 금융경제연구소 분석 리포트: {title}",
                        "sector": "REGULATION",
                        "created_at": datetime.utcnow().isoformat()
                    }
                    supabase.table("raw_intelligence").insert(data).execute()
                    print(f"  ✅ 신규 리포트 발견: {title}")
            except:
                continue
                
    except Exception as e:
        print(f"  ❌ SBI 수집 실패: {e}")

if __name__ == "__main__":
    crawl_sbi()
