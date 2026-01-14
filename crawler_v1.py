import feedparser
import requests
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

# ---------------------------------------------------------
# [설정] 환경변수 로드
# ---------------------------------------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ .env 파일 확인 필요")
    exit()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# [설정] 가짜 신분증 (User-Agent)
# ---------------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ---------------------------------------------------------
# [타겟 소스] 요청하신 4곳 확정
# ---------------------------------------------------------
RSS_FEEDS = [
    {
        "source": "CoinDesk (Policy)", 
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml&tag=policy",
        "must_filter": False # 이미 Policy 채널이라 필터 불필요
    },
    {
        "source": "The Block", 
        "url": "https://www.theblock.co/rss.xml", # 수정: .xml 추가
        "must_filter": True # 전체 뉴스라 필터링 필요
    },
    {
        "source": "Ledger Insights", 
        "url": "https://www.ledgerinsights.com/feed/", # 추가: 엔터프라이즈/규제 맛집
        "must_filter": True
    },
    {
        "source": "매일경제 (경제)", 
        "url": "https://www.mk.co.kr/rss/30100041/",
        "must_filter": True # 경제 뉴스 중 코인만 골라내야 함
    }
]

# ---------------------------------------------------------
# [핵심] 키워드 그물망 (User 니즈 반영)
# ---------------------------------------------------------
KEYWORDS = [
    # 1. 규제/기관
    "sec", "fsc", "fsa", "regulation", "law", "ban", "tax", "policy", "legal", "compliance",
    "규제", "금융위", "금감원", "법안", "세금", "과세", "승인", "기소", "판결",
    
    # 2. 자산/토큰 (매일경제 필터용)
    "crypto", "bitcoin", "ethereum", "stablecoin", "cbdc", "sto", "rwa", "token", "digital asset", "virtual asset",
    "크립토", "비트코인", "이더리움", "가상자산", "디지털자산", "토큰", "증권형", "현물", "블록체인"
]

def save_to_db(category, source, title, link, date):
    data = {
        "category": category,
        "source_name": source,
        "title": title,
        "url": link,
        "published_date": str(date)
    }
    
    try:
        response = supabase.table("raw_intelligence").select("url").eq("url", link).execute()
        if not response.data: 
            supabase.table("raw_intelligence").insert(data).execute()
            print(f"✅ [저장] {title[:30]}...") 
        else:
            pass # 중복 생략
    except Exception as e:
        print(f"⚠️ 저장 에러: {e}")

def run_crawler():
    print("🕵️ 블랙보드 수집 엔진 v2 가동 (매경/더블록/렛저인사이트)...")
    
    for feed in RSS_FEEDS:
        print(f"\n📡 [{feed['source']}] 접속 시도...")
        
        try:
            # 1. 요청
            response = requests.get(feed['url'], headers=HEADERS, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ 접속 실패 (코드: {response.status_code}) -> URL 확인 필요")
                continue

            # 2. 파싱
            parsed_feed = feedparser.parse(response.content)
            entries = parsed_feed.entries
            print(f"   -> {len(entries)}개 기사 스캔 중...")

            # 3. 필터링 및 저장
            saved_count = 0
            for entry in entries[:10]: # 소스당 최신 10개 검사
                title = entry.title
                link = entry.link
                published = entry.get('published', datetime.now().isoformat())
                
                # 필터 로직
                title_lower = title.lower()
                is_match = False
                
                if not feed['must_filter']:
                    # 코인데스크 Policy 같은 전문 채널은 무조건 통과
                    is_match = True
                else:
                    # 그 외(매경, 더블록 등)는 키워드가 하나라도 있어야 통과
                    if any(k in title_lower for k in KEYWORDS):
                        is_match = True
                
                if is_match:
                    save_to_db("regulation", feed['source'], title, link, published)
                    saved_count += 1
            
            if saved_count == 0 and feed['must_filter']:
                print("   [결과] 저장된 기사 없음 (키워드 매칭 실패)")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")

    print("\n🎉 수집 완료!")

if __name__ == "__main__":
    run_crawler()