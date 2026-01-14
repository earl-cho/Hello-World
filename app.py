# app.py (대시보드 전용)
import streamlit as st
import pandas as pd
from supabase import create_client
import time
import os
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(page_title="Blackboard Dashboard", page_icon="♟️", layout="wide")

# 키 로드
load_dotenv()
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    st.error("❌ API 키가 없습니다.")
    st.stop()

# DB 연결
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"DB 연결 실패: {e}")
    st.stop()

# --- UI 시작 ---
st.title("♟️ Blackboard : Crypto & Intelligence")
if st.button("🔄 새로고침"):
    st.rerun()
st.divider()

# 1. 차트 섹션
st.subheader("📈 Bitcoin Price (Live)")
try:
    # market_data 테이블에서 가져옴
    res = supabase.table("market_data").select("*").order("created_at", desc=True).limit(288).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df = df.sort_values('created_at')
        latest = df.iloc[-1]['price']
        st.metric("BTC/USDT", f"${latest:,.2f}")
        st.line_chart(df, x='created_at', y='price', color='#F7931A')
    else:
        st.info("데이터가 없습니다. 터미널에서 'python engine.py'를 실행하세요.")
except Exception as e:
    st.error(f"차트 에러: {e}")

st.divider()

# 2. 리포트 섹션
st.subheader("🤖 AI Analyst Report")
try:
    # market_reports 테이블에서 가져옴
    res = supabase.table("market_reports").select("*").order("created_at", desc=True).limit(1).execute()
    if res.data:
        report = res.data[0]
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"### {report['title']}")
            st.markdown(report['content'])
        with c2:
            st.info(f"**요약**\n\n{report['summary_3lines']}")
            st.caption(f"발행: {report['created_at'][:16]}")
    else:
        st.warning("리포트가 없습니다. 'python editor.py'를 실행하세요.")
except Exception as e:
    st.error(f"리포트 에러: {e}")