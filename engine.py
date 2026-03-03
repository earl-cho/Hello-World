import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# ---------------------------------------------------------
# [설정] 페이지 설정
# ---------------------------------------------------------
st.set_page_config(page_title="GLOBAL MONITOR", page_icon=None, layout="wide")

# ---------------------------------------------------------
# [CSS] 16:9 썸네일 및 카드 디자인
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    
    /* 🚨 [Color Fix] 다크모드 대응: 배경을 흰색으로 강제했으므로, 주요 텍스트도 검은색으로 강제 */
    h1, h2, h3, h4, h5, h6, p, li, a {
        color: #1a1a1a !important;
    }

    /* 국가 표시 태그 전용 스타일 (강제 흰색) */
    .region-tag {
        color: #ffffff !important;
    }
    
    /* 사이드바 강제 Light Mode */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }

    /* Better Button Visibility */
    [data-testid="stButton"] button {
        background-color: #f0f2f6 !important;
        color: #1a1a1a !important;
        border: 1px solid #d1d5db !important;
    }
    [data-testid="stButton"] button:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }



    /* Streamlit Header / Menu Visibility */
    header[data-testid="stHeader"], .stAppHeader {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }
    header[data-testid="stHeader"] *, .stAppHeader * {
        color: #1a1a1a !important;
    }
    
    /* 섹션 헤더 */
    .section-header {
        font-size: 1.2rem;
        font-weight: 900;
        color: #1a1a1a;
        border-bottom: 2px solid #1a1a1a;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
        margin-top: 3rem;
        text-transform: uppercase;
        letter-spacing: 0.05rem;
    }
    
    /* 서브 헤더 */
    .sub-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #4a5568;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.3rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }

    /* 🚨 [핵심] 16:9 썸네일 강제 적용 */
    .thumb-16-9 {
        width: 100%;
        aspect-ratio: 16 / 9;
        object-fit: cover;
        border-radius: 0px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.8rem;
    }
    
    /* 뉴스 카드 컨테이너 */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        border: 1px solid transparent;
        transition: 0.2s;
    }
    
    /* 카드 호버 효과 */
    .card-container {
        border: 1px solid #e2e8f0;
        padding: 10px;
        transition: 0.2s;
        height: 100%;
        background-color: white;
    }
    .card-container:hover {
        border-color: #000000;
        transform: translateY(-2px);
    }
    
    /* 텍스트 스타일 */
    .card-title {
        font-weight: 700;
        font-size: 1rem;
        line-height: 1.4;
        color: #000000;
        margin-bottom: 0.5rem;
    }
    .card-meta {
        font-size: 0.8rem;
        color: #718096;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
    }
    
    /* Robust Title Link */
    .card-title-link {
        text-decoration: none !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 3 !important;
        -webkit-box-orient: vertical !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        min-height: 4.2em !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.2rem !important;
    }
    .card-title-link:hover {
        color: #333333 !important;
        text-decoration: none !important;
    }

    /* 📄 [Refinement] Article Detail Typography */
    .stMarkdown div p {
        font-size: 1.35rem !important;
        line-height: 1.7 !important;
        margin-bottom: 0.8rem !important;
        color: #1a1a1a !important;
    }
    .stMarkdown div h3 {
        font-size: 1.9rem !important;
        font-weight: 900 !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1rem !important;
        color: #2563eb !important; /* Blue-600 */
        text-transform: uppercase !important;
        font-style: italic !important;
    }
    
    /* 버튼 스타일 */
    .read-btn {
        width: 100%;
        border: 1px solid #cbd5e1;
        background-color: white;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.4rem;
        cursor: pointer;
    }
    .read-btn:hover {
        background-color: #1a1a1a;
        color: white;
        border-color: #1a1a1a;
    }

    .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# [Backend] 연결
# ---------------------------------------------------------
load_dotenv()
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL: st.stop()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# [Logic]
# ---------------------------------------------------------
query_params = st.query_params

def go_to_article(article_id):
    st.query_params["article_id"] = article_id
    st.rerun()

def go_to_home():
    st.query_params.clear()
    st.rerun()

def categorize_report(report):
    # 1. 태그 기반 확실한 분류 (우선순위)
    tags = report.get('tags') or []
    # 리스트가 아니라 문자열일 경우 파싱 (Supabase 데이터 타입 대응)
    if isinstance(tags, str):
        import json
        try: tags = json.loads(tags.replace("'", '"'))
        except: tags = [tags]
    
    # 대소문자 통일
    tags = [str(t).upper() for t in tags]
    
    if 'REGULATION' in tags: return 'REGULATION'
    if 'ENTERPRISE' in tags: return 'ENTERPRISE'
    if 'CRYPTO_NATIVE' in tags or 'CRYPTO NATIVE' in tags: return 'CRYPTO NATIVE'

    # 2. 키워드 기반 분류 (Fallback)
    title = (report.get('title') or '').lower()
    if any(x in title for x in ['sec', '규제', 'policy', '법', '국회', '승인']): return 'REGULATION'
    elif any(x in title for x in ['etf', 'blackrock', '은행', '기업', '매수']): return 'ENTERPRISE'
    else: return 'CRYPTO NATIVE'

# 기본 이미지
DEFAULT_IMG = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=800&q=80"

# ---------------------------------------------------------
# [Component] 카드 그리기 
# ---------------------------------------------------------
def draw_card(report, suffix=""):
    img_url = report.get('image_url') or DEFAULT_IMG
    link = f"?article_id={report['id']}"
    date_str = report['created_at'][:10]
    
    # HTML Rendering
    html = (
        f'<div style="margin-bottom:20px;">'
        f'<a href="{link}" target="_self">'
        f'<img src="{img_url}" style="width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:4px;">'
        f'</a>'
        f'<a href="{link}" target="_self" style="text-decoration:none;color:black;font-weight:bold;display:block;margin-top:10px;">{report["title"]}</a>'
        f'<div style="font-size:0.8rem;color:gray;">{date_str}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------
# [Component] 카드 그리기 함수 (에러 해결: suffix 추가)
# ---------------------------------------------------------
def draw_card(report, suffix=""):
    img_url = report.get('image_url') or DEFAULT_IMG
    link = f"?article_id={report['id']}"
    date_str = report['created_at'][:10]
    title_upper = (report.get('title') or "").upper()
    
    # Aggressive Region Detection
    tags = report.get('tags') or []
    if isinstance(tags, str):
        import json
        try: tags = json.loads(tags.replace("'", '"'))
        except: tags = [tags]
    tags_upper = [str(t).upper() for t in tags]
    
    # Ultra-Aggressive Keywords
    KEYWORDS = {
        "KR": ["한국", "국내", "금융위", "금감원", "국회", "당국", "의원", "정부", "입법", "민주당", "국민의힘", "업비트", "빗썸", "코인원", "코빗", "고팍스", "가상자산", "토큰증권", "KOREA", "KRW", "아시아"],
        "US": ["US", "SEC", "FED", "ETF", "바이든", "트럼프", "미국", "월스트리트", "NYSE", "NASDAQ", "USA", "SEC"],
        "JP": ["JP", "일본", "FSA", "재무성", "엔화", "JAPAN"],
        "EU": ["EU", "유럽", "MICA", "EUROPE"],
        "CN": ["CN", "중국", "CHINA", "홍콩", "HK"],
        "UK": ["UK", "영국", "BRITAIN", "FCA"]
    }
    
    region = "GLOBAL"
    # Priority: KR first, then others
    found_regions = []
    
    # 1. Check tags
    for r, kws in KEYWORDS.items():
        if any(kw in tags_upper for kw in kws):
            found_regions.append(r)
    
    # 2. Check Title
    for r, kws in KEYWORDS.items():
        if any(kw in title_upper for kw in kws):
            found_regions.append(r)
            
    if found_regions:
        # Prioritize KR if present, else take the first found
        if "KR" in found_regions:
            region = "KR"
        else:
            region = found_regions[0]
    
    flag_map = {"US": "🇺🇸", "KR": "🇰🇷", "JP": "🇯🇵", "EU": "🇪🇺", "CN": "🇨🇳", "UK": "🇬🇧", "GLOBAL": "🌐"}
    flag = flag_map.get(region, "🌐")

    # High Contrast Tag Styling
    tag_style = "position:absolute;top:8px;right:8px;background:#334155;padding:3px 10px;border-radius:6px;font-size:0.75rem;font-weight:900;border:1.5px solid #ffffff;box-shadow:0 2px 4px rgba(0,0,0,0.3);z-index:20;"
    
    html = (
        f'<div style="margin-bottom:20px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;background-color:#ffffff!important;box-shadow:0 1px 3px rgba(0,0,0,0.1);">'
        f'<div style="position:relative;width:100%;aspect-ratio:16/9;">'
        f'<a href="{link}" target="_self" style="display:block;width:100%;height:100%;">'
        f'<img src="{img_url}" style="width:100%;height:100%;object-fit:cover;display:block;">'
        f'</a>'
        f'<div class="region-tag" style="{tag_style}">{flag} {region}</div>'
        f'</div>'
        f'<div style="padding:16px;background-color:#ffffff!important;">'
        f'<div style="font-size:0.8rem;color:#718096!important;margin-bottom:8px;">{date_str}</div>'
        f'<a href="{link}" target="_self" class="card-title-link">{report["title"]}</a>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------
# [View 1] 상세 페이지
# ---------------------------------------------------------
def render_article_page(article_id):
    try:
        res = supabase.table("market_reports").select("*").eq("id", article_id).execute()
        if not res.data:
            st.error("NOT FOUND")
            if st.button("BACK"): go_to_home()
            return
        
        article = res.data[0]
        if st.button("← DASHBOARD", use_container_width=False): go_to_home()
        st.divider()
        
        # 상세 페이지 이미지
        img_url = article.get('image_url') or DEFAULT_IMG
        st.image(img_url, use_container_width=True)
        
        st.markdown(f"## {article['title']}")
        st.caption(f"PUBLISHED: {article['created_at'][:16].replace('T', ' ')}")
        
        with st.container(border=True):
            st.markdown("**EXECUTIVE SUMMARY**")
            st.info(article['summary_3lines'])
        
        st.markdown(article['content'])
        st.divider()
        st.caption("END OF REPORT")
        
    except:
        if st.button("BACK"): go_to_home()

# ---------------------------------------------------------
# [View 3] 관리자 (CMS) 페이지
# ---------------------------------------------------------
def render_admin():
    st.title("🛡️ ADMIN CONSOLE")
    st.markdown("---")

    # 대기 중인 초안 가져오기
    try:
        res = supabase.table("market_reports").select("*").eq("status", "DRAFT").order("created_at", desc=True).execute()
        drafts = res.data
    except Exception as e:
        # 🟢 [Fallback] 컬럼 없음 에러 처리
        if "Could not find the 'status' column" in str(e) or "PGRST204" in str(e):
            st.error("⚠️ DB 설정 필요: 'status' 컬럼이 없습니다.")
            st.info("Supabase SQL Editor에서 아래 명령어를 실행해주세요:")
            st.code("ALTER TABLE market_reports ADD COLUMN status text DEFAULT 'DRAFT';", language="sql")
            return
        st.error(f"DB Error: {e}")
        return

    if not drafts:
        st.success("🎉 대기 중인 초안이 없습니다. (모두 발행됨)")
        return

    st.subheader(f"대기 중인 초안: {len(drafts)}건")
    
    for article in drafts:
        # 카테고리 표시 (Tags의 첫 번째 요소)
        tags = article.get('tags') or []
        category = tags[0] if tags else "General"
        
        with st.expander(f"📝 [{category}] {article['title']}", expanded=False):
            # KST 변환 (UTC+9)
            try:
                utc_time = datetime.fromisoformat(article['created_at'].replace('Z', '+00:00'))
                kst_time = utc_time + timedelta(hours=9)
                time_str = kst_time.strftime("%Y-%m-%d %H:%M:%S (KST)")
            except:
                time_str = article['created_at']
            
            # 🖼️ 썸네일 미리보기
            if article.get('image_url'):
                st.image(article['image_url'], width=300, caption="Preview Thumbnail")

            st.caption(f"Created: {time_str}")
            # 수정 폼
            new_title = st.text_input("제목", value=article['title'], key=f"t_{article['id']}")
            new_summary = st.text_area("3줄 요약", value=article['summary_3lines'], key=f"s_{article['id']}")
            new_content = st.text_area("본문 (Markdown)", value=article['content'], height=400, key=f"c_{article['id']}")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                # 발행 버튼
                if st.button("🚀 PUBLISH NOW", key=f"pub_{article['id']}"):
                    try:
                        supabase.table("market_reports").update({
                            "title": new_title,
                            "summary_3lines": new_summary,
                            "content": new_content,
                            "status": "PUBLISHED"
                        }).eq("id", article['id']).execute()
                        st.success("발행 완료! (새로고침이 필요합니다)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"발행 실패: {e}")
            with col2:
                # 삭제 버튼
                if st.button("🗑️ DELETE", key=f"del_{article['id']}"):
                    supabase.table("market_reports").delete().eq("id", article['id']).execute()
                    st.warning("삭제됨")
                    st.rerun()

    st.markdown("---")
    st.subheader("🗂️ PUBLISHED REPORTS (이미 발행된 글)")

    # 발행된 글 가져오기 (status != 'DRAFT')
    try:
        # status가 DRAFT가 아닌 것들 (NULL 포함)
        res_pub = supabase.table("market_reports").select("*").neq("status", "DRAFT").order("created_at", desc=True).limit(20).execute()
        published = res_pub.data
    except:
        # Fallback: status 컬럼 없을 때
        res_pub = supabase.table("market_reports").select("*").order("created_at", desc=True).limit(20).execute()
        published = res_pub.data

    if not published:
        st.info("발행된 글이 없습니다.")
        return

    for pub_article in published:
        with st.expander(f"✅ {pub_article['title']}", expanded=False):
            st.caption(f"ID: {pub_article['id']} / Date: {pub_article['created_at'][:10]}")
            
            c1, c2 = st.columns([1, 4])
            with c1:
                # 삭제 버튼
                if st.button("🗑️ DELETE PERMANENTLY", key=f"del_pub_{pub_article['id']}"):
                    supabase.table("market_reports").delete().eq("id", pub_article['id']).execute()
                    st.error("영구 삭제되었습니다.")
                    st.rerun()
            with c2:
                # 상태 변경 (Unpublish)
                if st.button("↩️ REVERT TO DRAFT", key=f"rev_{pub_article['id']}"):
                    try:
                        supabase.table("market_reports").update({"status": "DRAFT"}).eq("id", pub_article['id']).execute()
                        st.success("초안으로 되돌렸습니다.")
                        st.rerun()
                    except:
                        st.error("DB에 status 컬럼이 없어서 되돌릴 수 없습니다.")

# ---------------------------------------------------------
# [View 2] 메인 대시보드
# ---------------------------------------------------------
def render_dashboard():


    col_h1, col_h2 = st.columns([6, 1])
    with col_h1:
        st.title("GLOBAL MONITOR")
    with col_h2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("REFRESH"): st.rerun()

    # DATA FETCH
    reports = []
    try:
        # 🟢 [CMS] 오직 'PUBLISHED' 상태이거나 status가 없는(기존) 글만 노출
        res = supabase.table("market_reports").select("*").order("created_at", desc=True).limit(60).execute()
        if res.data: 
            # 필터링 로직: status가 'DRAFT'인 것은 제외
            reports = [r for r in res.data if r.get('status') != 'DRAFT']
    except: pass

    if not reports:
        st.warning("NO DATA. 크롤러와 에디터를 먼저 실행해주세요.")
        return

    # --- TOP HIGHLIGHTS ---
    st.markdown('<div class="section-header">TOP HIGHLIGHTS</div>', unsafe_allow_html=True)
    
    highlights = reports[:4]
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            if i < len(highlights):
                # 🔥 수정: suffix="top" 추가
                draw_card(highlights[i], suffix="top")

    # --- SECTOR BRIEFING ---
    st.markdown('<div class="section-header">SECTOR BRIEFING</div>', unsafe_allow_html=True)
    
    sec_reg = [r for r in reports if categorize_report(r) == 'REGULATION']
    sec_ent = [r for r in reports if categorize_report(r) == 'ENTERPRISE']
    sec_nat = [r for r in reports if categorize_report(r) == 'CRYPTO NATIVE']

    # 1. REGULATION
    st.markdown('<div class="sub-header">REGULATION & MACRO</div>', unsafe_allow_html=True)
    r_cols = st.columns(4)
    for i, col in enumerate(r_cols):
        with col:
            if i < len(sec_reg):
                # 🔥 수정: suffix="reg" 추가
                draw_card(sec_reg[i], suffix="reg")

    # 2. ENTERPRISE
    st.markdown('<div class="sub-header">ENTERPRISE ADOPTION</div>', unsafe_allow_html=True)
    e_cols = st.columns(4)
    for i, col in enumerate(e_cols):
        with col:
            if i < len(sec_ent):
                # 🔥 수정: suffix="ent" 추가
                draw_card(sec_ent[i], suffix="ent")

    # 3. CRYPTO NATIVE
    st.markdown('<div class="sub-header">CRYPTO NATIVE TECHNOLOGY</div>', unsafe_allow_html=True)
    n_cols = st.columns(4)
    for i, col in enumerate(n_cols):
        with col:
            if i < len(sec_nat):
                # 🔥 수정: suffix="nat" 추가
                draw_card(sec_nat[i], suffix="nat")

    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("© 2026 GLOBAL MONITOR")

if "article_id" in query_params:
    render_article_page(query_params["article_id"])
else:
    # 사이드바에서 모드 전환
    with st.sidebar:
        st.header("Global Monitor")
        mode = st.radio("Mode", ["Dashboard", "Admin (CMS)"])
    
    if mode == "Dashboard":
        render_dashboard()
    else:
        render_admin()