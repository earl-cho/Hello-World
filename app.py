import streamlit as st
import pandas as pd
from supabase import create_client
import time

# ---------------------------------------------------------
# [설정] Secrets에서 키 가져오기 (보안 강화)
# ---------------------------------------------------------
# 이제 코드를 누가 훔쳐봐도 키는 모릅니다.
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

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


st.markdown("---") # 구분선
st.subheader("🤖 AI Analyst Report")

# 1. DB에서 최신 리포트 1개 가져오기
report_response = supabase.table("ai_reports") \
    .select("*") \
    .order("created_at", desc=True) \
    .limit(1) \
    .execute()

# 2. 화면에 예쁘게 보여주기
if report_response.data:
    report = report_response.data[0]
    
    # 감정(매수/매도)에 따라 색상 정하기
    sentiment_color = "gray"
    if "매수" in report['sentiment']:
        sentiment_color = "green" # 호재면 초록색
    elif "매도" in report['sentiment']:
        sentiment_color = "red"   # 악재면 빨간색
        
    # 박스 안에 내용 출력
    with st.container(border=True):
        st.markdown(f"### {report['title']}")
        st.caption(f"작성일: {report['created_at'][:10]} | 투자의견: :{sentiment_color}[{report['sentiment']}]")
        st.write(report['content'])
else:
    st.info("아직 도착한 리포트가 없습니다. 잠시 후 다시 시도해주세요.")