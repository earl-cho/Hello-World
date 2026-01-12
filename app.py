import streamlit as st
import pandas as pd
from supabase import create_client
import time

# ---------------------------------------------------------
# [설정] Supabase 키 (engine.py에 넣었던 것과 똑같은 것!)
# ---------------------------------------------------------
SUPABASE_URL = 'https://hrfqvipwxuqssnnwowno.supabase.co'
SUPABASE_KEY = 'sb_publishable_Sdz_-3XX4Y05hgcBHooRPw_yufksqyO'

# DB 연결
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# [화면 구성]
# ---------------------------------------------------------
st.set_page_config(page_title="Blackboard Dashboard", layout="wide")
st.title("📈 Blackboard: Crypto Live")

# 새로고침 버튼
if st.button('데이터 새로고침'):
    st.rerun()

# 1. DB에서 데이터 가져오기 (최신 100개만)
response = supabase.table("market_data") \
    .select("*") \
    .order("created_at", desc=True) \
    .limit(100) \
    .execute()

# 2. 데이터 가공 (Pandas 사용)
df = pd.DataFrame(response.data)

if not df.empty:
    # 시간 순서대로 정렬 (차트 그리기 위해)
    df = df.sort_values('created_at')
    
    # 가장 최신 가격
    last_price = df.iloc[-1]['price']
    st.metric(label="BTC/USDT", value=f"${last_price:,.2f}")

    # 3. 차트 그리기
    st.subheader("Price Chart (Real-time)")
    # X축: 시간, Y축: 가격
    st.line_chart(data=df, x='created_at', y='price', color='#00FF00')

    # 4. 데이터 표 보여주기 (옵션)
    with st.expander("Raw Data 보기"):
        st.dataframe(df)
else:
    st.warning("아직 데이터가 없습니다. engine.py를 실행해주세요!")
