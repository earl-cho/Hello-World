import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

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
    h1, h2, h3, h4, h5, h6, p, li, a, div, span {
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

    /* 버튼 스타일 */
    [data-testid="stButton"] button {
        background-color: #f8fafc !important;
        color: #1a1a1a !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px;
        transition: all 0.2s;
    }
    [data-testid="stButton"] button:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    /* Header Visibility */
    header[data-testid="stHeader"], .stAppHeader {
        background-color: rgba(255, 255, 255, 0.95) !important;
    }
    header[data-testid="stHeader"] *, .stAppHeader * {
        color: #1a1a1a !important;
    }
    
    /* 섹션 헤더 */
    .section-header {
        font-size: 1.4rem;
        font-weight: 900;
        color: #1a1a1a;
        border-bottom: 3px solid #1a1a1a;
        padding-bottom: 0.8rem;
        margin-bottom: 2rem;
        margin-top: 4rem;
        text-transform: uppercase;
        letter-spacing: -0.02em;
    }
    
    /* 서브 헤더 */
    .sub-header {
        font-size: 1.0rem;
        font-weight: 800;
        color: #334155;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-bottom: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ----------------------------------------------------------------
       [CARD LAYOUT SYSTEM] 
       Grid Alignment & Fixed Heights
    ---------------------------------------------------------------- */
    
    /* Global Image Reset - Force 16:9 */
    img {
        aspect-ratio: 16 / 9 !important;
        object-fit: cover !important;
        width: 100% !important;
        border-radius: 8px;
    }
    
    /* Card Container */
    .news-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%; /* Fill streamlit column */
        display: flex;
        flex-direction: column;
        margin-bottom: 24px;
    }
    
    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }

    /* Image Wrapper */
    .card-img-box {
        position: relative;
        width: 100%;
        aspect-ratio: 16 / 9;
        overflow: hidden;
        border-bottom: 1px solid #f1f5f9;
        background-color: #f8fafc;
    }
    
    .card-img-box img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    
    .news-card:hover .card-img-box img {
        transform: scale(1.05);
    }

    /* Card Content */
    .card-content {
        padding: 16px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 140px; /* Ensure visual balance */
    }
    
    /* Title: Max 2 lines */
    .card-title {
        color: #0f172a !important;
        font-weight: 700;
        font-size: 1.05rem;
        line-height: 1.5;
        margin-bottom: 12px;
        
        display: -webkit-box;
        -webkit-line-clamp: 2; /* Limit to 2 lines */
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 3.0em; /* Fixed height for 2 lines */
        text-decoration: none;
    }
    
    .card-title:hover {
        color: #2563eb !important;
    }
    
    .card-meta {
        font-size: 0.75rem;
        color: #64748b !important;
        font-weight: 500;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: auto; /* Push to bottom */
        padding-top: 12px;
        border-top: 1px solid #f1f5f9;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1400px;
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

def go_to_sector(sector_name):
    st.query_params["sector"] = sector_name
    st.rerun()

def go_to_home():
    st.query_params.clear()
    st.rerun()

def categorize_report(report):
    # 1. Check Explicit Tags from DB (Source of Truth)
    tags = report.get('tags') or []
    tags_upper = [str(t).upper() for t in tags]
    
    if 'ENTERPRISE' in tags_upper: return 'ENTERPRISE'
    if 'CRYPTO_NATIVE' in tags_upper: return 'CRYPTO NATIVE' # Note: app.py uses space 'CRYPTO NATIVE' in UI/logic
    if 'REGULATION' in tags_upper: return 'REGULATION'
    
    # 2. Fallback (Legacy)
    title = (report.get('title') or '').lower() + str(tags).lower()
    if any(x in title for x in ['sec', '규제', 'policy', '법', '국회', '승인', 'fsc', 'regulation']): return 'REGULATION'
    elif any(x in title for x in ['etf', 'blackrock', '은행', '기업', '매수', 'partnership', 'enterprise']): return 'ENTERPRISE'
    else: return 'CRYPTO NATIVE'

# 기본 이미지
DEFAULT_IMG = "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=800&q=80"

# ---------------------------------------------------------
# [Component] 카드 그리기
# ---------------------------------------------------------
def draw_card(report, suffix=""):
    # 1. Image Logic (Safe Fallback)
    img_path = report.get('image_url') or DEFAULT_IMG
    
    # If it's our local static path, try to find the actual local file for st.image
    local_path = None
    if img_path.startswith("/static/"):
        filename = os.path.basename(img_path)
        test_path = os.path.join(os.getcwd(), "static", "thumbnails", filename)
        if os.path.exists(test_path):
            local_path = test_path
            
    # Display Logic: Use URL or Local Path
    display_img = local_path if local_path else img_path
    
    article_id = report.get('id')
    link = f"?article_id={article_id}"
    title = report.get("title", "No Title")
    date_str = report.get("created_at", "")[:10]
    
    # Render with new CSS classes
    html = f"""
    <div class="news-card">
        <a href="{link}" target="_self" class="card-img-box">
            <img src="{display_img}">
        </a>
        <div class="card-content">
            <a href="{link}" target="_self" class="card-title">{title}</a>
            <div class="card-meta">
                <span>{date_str}</span>
                <span>⟶ Read</span>
            </div>
        </div>
    </div>
    """
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
        
        # Use image directly (all images are now Unsplash URLs)
        try:
            st.image(img_url, use_container_width=True)
        except Exception as e:
            st.warning(f"이미지 로드 실패: {e}")
            st.image(DEFAULT_IMG, use_container_width=True)
        
        st.markdown(f"## {article['title']}")
        st.caption(f"PUBLISHED: {article['created_at'][:16].replace('T', ' ')}")
        
        with st.container(border=True):
            st.markdown("**EXECUTIVE SUMMARY**")
            st.info(article['summary_3lines'])
        
        st.markdown(article['content'])
        st.divider()
        st.caption("END OF REPORT")
        
        
    except Exception as e:
        st.error(f"Error loading article: {e}")
        if st.button("BACK"): go_to_home()

# ---------------------------------------------------------
# [View 3] 섹터별 리스트 페이지 (Full List)
# ---------------------------------------------------------
def render_sector_list(sector_name):
    st.button("← BACK TO DASHBOARD", on_click=go_to_home)
    st.title(f"{sector_name} ARCHIVE")
    
    # 한번에 100개 로딩
    try:
        res = supabase.table("market_reports").select("*").order("created_at", desc=True).limit(100).execute()
        all_reports = res.data if res.data else []
        
        # 필터링
        filtered = [r for r in all_reports if categorize_report(r) == sector_name]
        
        if not filtered:
            st.info("No articles in this sector yet.")
            return

        # 4열 그리드로 출력
        cols = st.columns(4)
        for idx, report in enumerate(filtered):
            with cols[idx % 4]:
                draw_card(report, suffix=f"list_{idx}")
                st.markdown("---")

    except Exception as e:
        st.error(f"Error loading list: {e}")

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

    # DATA FETCH (Dashboard용 60개)
    reports = []
    try:
        res = supabase.table("market_reports").select("*").order("created_at", desc=True).limit(60).execute()
        if res.data: 
            reports = res.data
            st.sidebar.write(f"📊 DB Status: {len(reports)} reports found")
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")
        return

    if not reports:
        st.warning("NO DATA found in 'market_reports'. Please check if data exists in Supabase.")
        return
    
    # st.sidebar.info(f"📊 {len(reports)} articles loaded.")

    # --- TOP HIGHLIGHTS ---
    st.markdown('<div class="section-header">TOP HIGHLIGHTS</div>', unsafe_allow_html=True)
    
    highlights = reports[:4]
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            if i < len(highlights):
                draw_card(highlights[i], suffix="top")

    # --- SECTOR BRIEFING ---
    st.markdown('<div class="section-header">SECTOR BRIEFING</div>', unsafe_allow_html=True)

    # --- Helper to render sector row ---
    def render_sector_row(title, sector_code, data_list):
        c1, c2 = st.columns([8, 2])
        with c1:
            st.markdown(f'<div class="sub-header">{title}</div>', unsafe_allow_html=True)
        with c2:
            if st.button(f"VIEW ALL ({sector_code})", key=f"more_{sector_code}"):
                go_to_sector(sector_code)
        
        r_cols = st.columns(4)
        for i, col in enumerate(r_cols):
            with col:
                if i < len(data_list):
                    draw_card(data_list[i], suffix=f"{sector_code}_{i}")
    
    # 분류 (Categorization)
    sec_reg = [r for r in reports if categorize_report(r) == 'REGULATION']
    sec_ent = [r for r in reports if categorize_report(r) == 'ENTERPRISE']
    sec_nat = [r for r in reports if categorize_report(r) == 'CRYPTO NATIVE']

    # Debug: Show counts if no articles in a sector
    if not sec_reg and not sec_ent and not sec_nat:
        st.error("Filtering logic resulted in empty lists. Showing all reports as 'CRYPTO NATIVE'.")
        sec_nat = reports

    st.sidebar.write(f"📁 REG: {len(sec_reg)} | ENT: {len(sec_ent)} | NAT: {len(sec_nat)}")

    render_sector_row("REGULATION & MACRO", "REGULATION", sec_reg[:8])
    render_sector_row("ENTERPRISE ADOPTION", "ENTERPRISE", sec_ent[:8])
    render_sector_row("CRYPTO NATIVE TECHNOLOGY", "CRYPTO NATIVE", sec_nat[:8])

    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    st.caption("© 2026 GLOBAL MONITOR")

if "article_id" in query_params:
    render_article_page(query_params["article_id"])
elif "sector" in query_params:
    render_sector_list(query_params["sector"])
else:
    render_dashboard()