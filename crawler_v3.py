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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ---------------------------------------------------------
# [타겟 소스] 매경(경제/증권) + 블록미디어(보험용)
# ---------------------------------------------------------
RSS_FEEDS = [
    {
        "source": "CoinDesk (Policy)", 
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml&tag=policy",
        "must_filter": False 
    },
    {
        "source": "The Block", 
        "url": "https://www.theblock.co/rss.xml", 
        "must_filter": True 
    },
    {
        "source": "Ledger Insights", 
        "url": "https://www.ledgerinsights.com/feed/", 
        "must_filter": True
    },
    {
        "source": "매일경제 (경제)", 
        "url": "https://www.mk.co.kr/rss/30100041/",
        "must_filter": True 
    },
    {
        "source": "매일경제 (증권)", 
        "url": "https://www.mk.co.kr/rss/40200003/", 
        "must_filter": True 
    },
    {
        "source": "BlockMedia (KR)", # 매경이 조용할 때를 대비한 보험
        "url": "https://www.blockmedia.co.kr/feed",
        "must_filter": False # 여긴 전용지니까 필터 없이 다 가져옴
    }
]

# ---------------------------------------------------------
# [키워드] 영어/한국어 그물망
# ---------------------------------------------------------
KEYWORDS = [
    "sec", "fsc", "fsa", "regulation", "law", "ban", "tax", "policy", "legal",
    "crypto", "bitcoin", "ethereum", "stablecoin", "cbdc", "sto", "rwa", "token",
    "규제", "금융", "금감원", "법안", "세금", "승인", "기소",
    "크립토", "비트코인", "이더리움", "가상자산", "디지털자산", "토큰", "증권형", "블록체인", "코인"
]

def save_to_db(category, source, title, link, date, summary=""):
    # 요약문(summary)도 같이 저장하면 나중에 AI가 읽기 좋습니다.
    data = {
        "category": category,
        "source_name": source,
        "title": title,
        "url": link,
        "published_date": str(date),
        "summary": summary[:500] # 너무 길면 자름
    }
    
    try:
        response = supabase.table("raw_intelligence").select("url").eq("url", link).execute()
        if not response.data: 
            supabase.table("raw_intelligence").insert(data).execute()
            print(f"✅ [저장] {title[:20]}...") 
        else:
            pass 
    except Exception as e:
        print(f"⚠️ 저장 에러: {e}")

def run_crawler():
    print("🕵️ 블랙보드 수집 엔진 v3 가동 (본문 검색 + 블록미디어)...")
    
    for feed in RSS_FEEDS:
        print(f"\n📡 [{feed['source']}] 접속 시도...")
        
        try:
            response = requests.get(feed['url'], headers=HEADERS, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ 접속 실패 (코드: {response.status_code})")
                continue

            parsed_feed = feedparser.parse(response.content)
            entries = parsed_feed.entries
            print(f"   -> {len(entries)}개 기사 스캔 중...")

            saved_count = 0
            # 매경 같은 곳은 기사가 많으니 20개까지 확인
            scan_limit = 20 if "매일경제" in feed['source'] else 10

            for entry in entries[:scan_limit]: 
                title = entry.title
                link = entry.link
                published = entry.get('published', datetime.now().isoformat())
                
                # [업그레이드] 제목뿐만 아니라 요약글(description)도 가져옴
                summary = entry.get('description', '') 
                
                # 검색 대상: 제목 + 요약글 (소문자로 변환)
                target_text = (title + " " + summary).lower()
                
                is_match = False
                
                if not feed['must_filter']:
                    is_match = True
                else:
                    if any(k in target_text for k in KEYWORDS):
                        is_match = True
                
                if is_match:
                    save_to_db("regulation", feed['source'], title, link, published, summary)
                    saved_count += 1
                else:
                    # [디버깅] 매일경제에서 뭘 버리는지 딱 1개만 샘플로 보여줌
                    if "매일경제" in feed['source'] and saved_count == 0 and entries.index(entry) == 0:
                         print(f"   [탈락 예시] {title} (키워드 없음)")

            if saved_count == 0 and feed['must_filter']:
                print("   [결과] 저장된 기사 없음.")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")

    print("\n🎉 수집 완료!")

if __name__ == "__main__":
    run_crawler()