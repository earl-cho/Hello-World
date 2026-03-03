import feedparser
import requests
from supabase import create_client
import os
import sys
import traceback
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup

# ---------------------------------------------------------
# [설정] 환경변수 로드
# ---------------------------------------------------------
load_dotenv('/Users/earl/Blackboard/.env')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ .env 파일 확인 필요")
    exit()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

RSS_FEEDS = [
    {"source": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "must_filter": True},
    {"source": "The Block", "url": "https://www.theblock.co/rss.xml", "must_filter": True},
    {"source": "Ledger Insights", "url": "https://www.ledgerinsights.com/feed/", "must_filter": False},
    {"source": "CoinTelegraph", "url": "https://cointelegraph.com/rss", "must_filter": True},
    {"source": "Vitalik Buterin", "url": "https://vitalik.eth.limo/feed.xml", "must_filter": False},
    {"source": "EFF (Privacy)", "url": "https://www.eff.org/rss/updates.xml", "must_filter": True},
    {"source": "Dark.fi", "url": "https://dark.fi/rss.xml", "must_filter": False},
    {"source": "매일경제 (경제)", "url": "https://www.mk.co.kr/rss/30100041/", "must_filter": True},
    {"source": "매일경제 (증권)", "url": "https://www.mk.co.kr/rss/40200003/", "must_filter": True},
    {"source": "BlockMedia (KR)", "url": "https://www.blockmedia.co.kr/feed", "must_filter": True},
    {"source": "CoinPost", "url": "https://coinpost.jp/feed", "must_filter": True},
    {"source": "あたらしい経済", "url": "https://www.neweconomy.jp/feed", "must_filter": False},
    {"source": "Cointelegraph Japan", "url": "https://jp.cointelegraph.com/rss", "must_filter": True},
    {"source": "CRYPTO TIMES", "url": "https://crypto-times.jp/feed/", "must_filter": True},
    {"source": "BitTimes", "url": "https://bittimes.net/feed", "must_filter": False},
    {"source": "CoinChoice", "url": "https://coinchoice.net/feed/", "must_filter": False},
    {"source": "Nikkei Technology", "url": "https://www.nikkei.com/rss/RDF/technology.rdf", "must_filter": True},
    {"source": "Bloomberg Japan", "url": "https://www.bloomberg.co.jp/feeds/news.rss", "must_filter": True},
    {"source": "Yahoo! News Business", "url": "https://news.yahoo.co.jp/rss/topics/business.xml", "must_filter": True},
    {"source": "한국경제 (경제)", "url": "https://www.hankyung.com/feed/economy", "must_filter": True},
    {"source": "TechM", "url": "https://news.google.com/rss/search?q=site:techm.kr+블록체인&hl=ko&gl=KR&ceid=KR:ko", "must_filter": False},
    {"source": "TokenPost", "url": "https://news.google.com/rss/search?q=site:tokenpost.kr&hl=ko&gl=KR&ceid=KR:ko", "must_filter": False},
    {"source": "Google News (KR: Ent/Reg/RWA)", "url": "https://news.google.com/rss/search?q=(\"디지털 자산\" OR \"토큰 증권\" OR \"스테이블코인\" OR \"RWA\" OR \"실물연계자산\") OR (\"블록체인\" AND (\"파트너십\" OR \"협약\" OR \"도입\" OR \"규제\" OR \"금융위\")) when:24h&hl=ko&gl=KR&ceid=KR:ko", "must_filter": False},
    {"source": "Digital Asset (KR)", "url": "https://news.google.com/rss/search?q=site:digitalasset.works&hl=ko&gl=KR&ceid=KR:ko", "must_filter": False},
    {"source": "Wu Blockchain", "url": "https://news.google.com/rss/search?q=site:wublock.co&hl=en-US&gl=US&ceid=US:en", "must_filter": False},
    {"source": "서울경제 (Seoul Economic)", "url": "https://rss.sedaily.com/sedaily_all.xml", "must_filter": True},
    {"source": "파이낸셜뉴스 (Financial News)", "url": "https://www.fnnews.com/rss/fnnews/financial_news.xml", "must_filter": True},
    {"source": "US SEC", "url": "https://www.sec.gov/news/pressreleases.rss", "must_filter": False},
    {"source": "KR FSC", "url": "https://fsc.go.kr/about/fsc_bbs_rss/?fid=0111", "must_filter": False},
    {"source": "JP FSA", "url": "https://www.fsa.go.jp/fsaNewsListAll_rss2.xml", "must_filter": False},
    {"source": "JP FSA (English)", "url": "https://www.fsa.go.jp/fsaEnNewsList_rss2.xml", "must_filter": False},
    {"source": "a16z News", "url": "https://www.a16z.news/feed", "must_filter": True},
    {"source": "Variant Fund", "url": "https://variant.fund/feed/", "must_filter": True},
    {"source": "Placeholder", "url": "https://www.placeholder.vc/blog?format=rss", "must_filter": True},
    {"source": "Multicoin Capital", "url": "https://multicoin.capital/rss.xml", "must_filter": True},
    {"source": "Dragonfly", "url": "https://dragonfly.mirror.xyz/feed/atom", "must_filter": True},
    {"source": "Paradigm (Research)", "url": "https://www.paradigm.xyz/rss.xml", "must_filter": True},
    {"source": "Ethereum Foundation", "url": "https://blog.ethereum.org/feed.xml", "must_filter": False},
    {"source": "Flashbots", "url": "https://writings.flashbots.net/rss.xml", "must_filter": False},
    {"source": "Coin Center", "url": "https://www.coincenter.org/feed", "must_filter": True},
    {"source": "Hester Peirce (SEC)", "url": "https://news.google.com/rss/search?q=site:sec.gov+\"Hester+Peirce\"&hl=en-US&gl=US&ceid=US:en", "must_filter": False},
    {"source": "Fidelity Digital Assets", "url": "https://news.google.com/rss/search?q=site:fidelitydigitalassets.com&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "CME Group (Insights)", "url": "https://news.google.com/rss/search?q=site:cmegroup.com+(\"bitcoin\"+OR+\"crypto\"+OR+\"ether\")+when:7d&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "Coinbase Institutional", "url": "https://news.google.com/rss/search?q=site:coinbase.com/institutional+OR+site:coinbase.com/blog+\"institutional\"&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "JP Morgan (Insights)", "url": "https://news.google.com/rss/search?q=site:jpmorgan.com+(\"blockchain\"+OR+\"crypto\"+OR+\"digital+assets\"+OR+\"tokenization\"+OR+\"kinexys\")+when:7d&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "Goldman Sachs (Insights)", "url": "https://news.google.com/rss/search?q=site:goldmansachs.com+(\"blockchain\"+OR+\"crypto\"+OR+\"digital+assets\"+OR+\"tokenization\")+when:7d&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "Blackrock (Insights)", "url": "https://news.google.com/rss/search?q=site:blackrock.com+(\"blockchain\"+OR+\"crypto\"+OR+\"digital+assets\"+OR+\"tokenization\"+OR+\"bitcoin+etf\"+OR+\"ethereum+etf\")+when:7d&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "ARK Invest (Research)", "url": "https://news.google.com/rss/search?q=site:ark-invest.com+(\"blockchain\"+OR+\"crypto\"+OR+\"digital+assets\"+OR+\"bitcoin\")+when:7d&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "McKinsey (Insights)", "url": "https://news.google.com/rss/search?q=site:mckinsey.com+(\"blockchain\"+OR+\"crypto\"+OR+\"web3\"+OR+\"digital+assets\"+OR+\"tokenization\")+when:7d&hl=en-US&gl=US&ceid=US:en", "must_filter": True},
    {"source": "BCG (Insights)", "url": "https://news.google.com/rss/search?q=site:bcg.com+(\"blockchain\"+OR+\"crypto\"+OR+\"web3\"+OR+\"digital+assets\"+OR+\"tokenization\")+when:7d&hl=en-US&gl=US&ceid=US:en", "must_filter": True}
]

KEYWORDS = [
    "crypto", "bitcoin", "ethereum", "stablecoin", "cbdc", "rwa", "blockchain", "defi", "nft",
    "tokenization", "digital asset", "kinexys",
    "暗호資産", "가상자산", "비트코인", "이더리움", "블록체인",
    "암호화폐",
    "regulation", "law", "policy", "금융위", "금감원", "금융청", "規制", "金融",
    "ステーブルコイン", "トークン化", "デジタル資産", "預託", "信託", "地方創생", "カストディ"
]
# Short keywords that need strict word boundary check or specific context
# Short keywords that need strict word boundary check or specific context
STRICT_KEYWORDS = ["sto", "dao", "dex", "mev", "l2", "zk", "sec", "fsc", "fsa", "bitcoin etf", "ethereum etf"] 

# Keywords that should be EXCLUDED unless a crypto keyword is also present
BLACKLIST_KEYWORDS = [
    "esg", "climate transition", "sustainable finance", "green bond", 
    "s&p 500", "nasdaq 100", "dow jones", "interest rate", "fed hike", 
    "inflation data", "cpi", "unemployment rate", "mortgage",
    "bonds", "treasury yield", "corporate bond", "high yield bond",
    "hiring", "recruitment", "java backend", "operational strategy",
    "stewardship code", "shareholder value", "dividend"
]

def clean_html(text):
    if not text: return ""
    return BeautifulSoup(text, "html.parser").get_text()

def extract_image(entry):
    if 'media_content' in entry: return entry.media_content[0]['url']
    if 'media_thumbnail' in entry: return entry.media_thumbnail[0]['url']
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/'): return link['href']
    if 'summary' in entry:
        soup = BeautifulSoup(entry.summary, 'html.parser')
        img = soup.find('img')
        if img: return img['src']
    return None

def detect_sector(title, summary):
    title = str(title) if title else ""
    summary = str(summary) if summary else ""
    text = (title + " " + summary).lower()
    
    # [Score System]
    # Strong Keywords (+5): Uniquely identifies the sector.
    # Weak Keywords (+1): Supporting context.
    
    scores = {
        "enterprise": 0,
        "crypto_native": 0,
        "regulation": 0
    }
    
    # --- 1. ENTERPRISE ADOPTION ---
    ent_strong = [
        "blackrock", "fidelity", "etf", "asset mana", "rwa", "sto", "tokenization", 
        "real world asset", "market maker", "liquidity provider", "citadel", "jpmorgan",
        "jp morgan", "chase bank", "goldman", "sachs", "citi", "bank of america", "visa", 
        "mastercard", "paypal", "stripe", "tokenized", "private credit", "treasury", "bond", 
        "cbdc", "stablecoin issuer", "franklin templeton", "wisdomtree", "grayscale",
        "자산운용", "상장지수", "토큰증권", "실물자산", "기관투자", "수탁", "커스터디"
    ]
    ent_weak = [
        "enterprise", "institutional", "partnership", "adoption", "bank", "fund", 
        "investment", "finance", "settlement", "payment", "stablecoin", "securities",
        "기업", "기관", "채택", "협약", "은행", "투자", "결제", "증권"
    ]
    
    for k in ent_strong:
        if k in text: scores["enterprise"] += 5
    for k in ent_weak:
        if k in text: scores["enterprise"] += 1
        
    # --- 2. CRYPTO NATIVE ---
    nat_strong = [
        "tornado", "mixer", "privacy", "zero knowledge", "zk-", "zk rollup", "proof", 
        "censorship", "decentralization", "self-custody", "dao", "governance", 
        "vitalik", "ethereum foundation", "layer2", "l2", "arbitrum", "optimism", 
        "base chain", "mev", "flashbot", "staking", "restaking", "eigenlayer",
        "smart contract", "on-chain", "protocol", "dapp", "dex", "uniswap",
        "프라이버시", "영지식", "증명", "탈중앙", "검열", "다오", "거버넌스", "레이어2", 
        "스테이킹", "온체인", "프로토콜", "스마트 컨트랙트"
    ]
    nat_weak = [
        "crypto", "bitcoin", "ethereum", "blockchain", "developer", "upgrade", "fork", 
        "wallet", "metamask", "ledger",
        "크립토", "지갑", "업그레이드"
    ]
    
    for k in nat_strong:
        if k in text: scores["crypto_native"] += 5
    for k in nat_weak:
        if k in text: scores["crypto_native"] += 1
        
    # --- 3. REGULATION ---
    # Regulation needs careful weighting. It often appears as context.
    # We give it points, but usually less aggressively than "Primary Subject" keywords.
    reg_strong = [
        "sec", "cftc", "fsc", "fsa", "fin cen", "fatf", "lawsuit", "sue", "indictment", 
        "arrest", "jail", "sentence", "legislation", "bill", "congress", "senate", 
        "parliament", "white house", "president", "prime minister", "mi ca", "fit21",
        "금융위", "금감원", "금융청", "당국", "소송", "구속", "징역", "법안", "국회"
    ]
    reg_weak = [
        "regulation", "regulator", "policy", "law", "legal", "compliance", "ban", "restrict",
        "judge", "court", "ruling", "decision", "fine", "penalty",
        "규제", "정책", "법", "판결", "벌금"
    ]
    
    for k in reg_strong:
        if k in text: scores["regulation"] += 2  # Strong Reg key = +2 (Not +5, to allow 'Tornado(5) sanctioned(2)' -> Native)
    for k in reg_weak:
        if k in text: scores["regulation"] += 1

    # --- DECISION ---
    # Find the category with maximum score
    max_score = -1
    best_sector = "regulation" # Default fallback
    
    # Prioritize comparison: Ent vs Native vs Reg
    # If tie, we prefer Native/Ent over Reg? Or maybe simple Max.
    # Let's iterate.
    for sector, score in scores.items():
        if score > max_score:
            max_score = score
            best_sector = sector
        elif score == max_score:
            # Tie breaking logic
            if best_sector == "regulation" and sector in ["enterprise", "crypto_native"]:
                best_sector = sector # Bias away from Reg
            elif best_sector == "enterprise" and sector == "crypto_native":
                best_sector = "crypto_native" # Bias towards Native (Cypherpunk is usually more specific)
    
    # If total score is very low (e.g. 0 or 1), default to Regulation or General
    if max_score <= 1:
        return "regulation"
        
    return best_sector

def save_to_db(category, source, title, link, date, summary="", image_url=None):
    data = {
        "category": category,
        "source_name": source,
        "title": title,
        "url": link,
        "published_date": str(date),
        "summary": summary[:1000],
        "content": summary, # [FIX] article_writer와의 호환성을 위해 content 필드에도 저장
        "image_url": image_url
    }
    try:
        response = supabase.table("raw_intelligence").select("url").eq("url", link).execute()
        if not response.data:
            supabase.table("raw_intelligence").insert(data).execute()
            print(f"  ✅ [저장] ({category}) {title[:30]}...")
    except Exception as e:
        print(f"  ⚠️ DB 저장 에러: {e}")

def run_crawler():
    print(f"🕵️ Blackboard Crawler v4.5 (Full Production) - Targets: {len(RSS_FEEDS)} feeds")
    
    for feed in RSS_FEEDS:
        print(f"\n📡 [{feed['source']}] 스캔 중...")
        try:
            resp = requests.get(feed['url'], headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                print(f"  ❌ HTTP Error: {resp.status_code}")
                continue
                
            parsed = feedparser.parse(resp.content)
            print(f"  Found {len(parsed.entries)} entries")
            
            for entry in parsed.entries[:15]:
                try:
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    if not link: continue
                    
                    published = entry.get('published', datetime.now().isoformat())
                    raw_summary = entry.get('summary', entry.get('description', ''))
                    summary = clean_html(raw_summary)
                    image_url = extract_image(entry)
                    
                    if feed.get('must_filter'):
                        text = (title + " " + summary).lower()
                        
                        # 1. First, check if it's explicitly about crypto/blockchain
                        found = any(k in text for k in KEYWORDS)
                        if not found:
                            import re
                            for k in STRICT_KEYWORDS:
                                if re.search(rf"\b{k}\b", text):
                                    found = True
                                    break
                        
                        if not found:
                            continue
                            
                        # 2. Second, check if it's generic TradFi noise (Blacklist)
                        # Even if 'found' is True, if it contains blacklist keys and NO strong crypto keys, we skip.
                        # Strong crypto keys for override
                        STRONG_CRYPTO = ["bitcoin", "ethereum", "crypto", "blockchain", "digit asset", "tokenization", "rwa", "sto"]
                        has_strong_crypto = any(s in text for s in STRONG_CRYPTO)
                        
                        if not has_strong_crypto:
                            has_blacklist = any(b in text for b in BLACKLIST_KEYWORDS)
                            if has_blacklist:
                                # print(f"  ⏭️ [Blacklist Skip] {title[:30]}...")
                                continue
                    
                    sector = detect_sector(title, summary)
                    save_to_db(sector, feed['source'], title, link, published, summary, image_url)
                except Exception as inner_e:
                    print(f"  ⚠️ Error processing entry: {inner_e}")
            
            print(f"  ✅ Completed [{feed['source']}]")

        except Exception as e:
            print(f"  ❌ Error processing {feed['source']}: {e}")
            traceback.print_exc()

    print("\n🎉 All feeds processed successfully.")

if __name__ == "__main__":
    run_crawler()