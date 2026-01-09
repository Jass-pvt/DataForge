import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="📈 DataForge | AI Stock Analytics",
    layout="wide"
)

st.title("📈 DataForge – AI Stock Market Analytics")
st.caption("Built by Jaswanth Rathore (JR)")
st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛️ Controls")
ticker = st.sidebar.selectbox("📌 Stock", ['NVDA', 'INTC', 'AMD', 'TSM', 'MU'])
months = st.sidebar.slider("🕒 History (Months)", 1, 24, 6)

st.sidebar.divider()
st.sidebar.markdown("## 🧮 Calculators")

fd_btn = st.sidebar.button("🏦 FD Calculator")
sip_btn = st.sidebar.button("📊 SIP Calculator")
lump_btn = st.sidebar.button("💰 Lumpsum Calculator")

# ---------------- DATA LOADER ----------------
@st.cache_data
def load_stock(ticker, months):
    df = yf.download(
        ticker,
        start=date.today() - relativedelta(months=months),
        end=date.today()
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# ---------------- STOCK DATA ----------------
data = load_stock(ticker, months)
price_col = "Adj Close" if "Adj Close" in data.columns else "Close"
prices = data[price_col]
returns = prices.pct_change().dropna()

# ---------------- KPIs ----------------
c1, c2, c3 = st.columns(3)
c1.metric("💰 Price", f"${prices.iloc[-1]:.2f}", f"{returns.iloc[-1]*100:.2f}%")
c2.metric("📈 Total Return", f"{((prices.iloc[-1]/prices.iloc[0])-1)*100:.2f}%")
c3.metric("⚡ Volatility", f"{returns.std()*np.sqrt(252):.2f}")

st.divider()

# ---------------- AI STOCK SUMMARY ----------------
st.subheader("🧠 AI Stock Summary")

ma20 = prices.rolling(20).mean()
ma50 = prices.rolling(50).mean()

trend = "Bullish 📈" if ma20.iloc[-1] > ma50.iloc[-1] else "Bearish 📉"
vol = "High" if returns.std() > 0.02 else "Moderate"

ai_summary = f"""
**AI Insight for {ticker}:**

• Market Trend: **{trend}**  
• Volatility Level: **{vol}**  
• Price is {'above' if prices.iloc[-1] > ma50.iloc[-1] else 'below'} 50-day average  
• Momentum suggests **{'strength' if trend=='Bullish 📈' else 'weakness'}**  

📌 *This is an AI-generated analytical summary based on price action & indicators.*
"""

st.info(ai_summary)

# ---------------- BUY / SELL SIGNAL ----------------
st.subheader("📌 Trading Signal")

if ma20.iloc[-1] > ma50.iloc[-1] and returns.iloc[-1] > 0:
    st.success("✅ BUY Signal – Uptrend with positive momentum")
elif ma20.iloc[-1] < ma50.iloc[-1] and returns.iloc[-1] < 0:
    st.error("❌ SELL Signal – Downtrend detected")
else:
    st.warning("⏸️ HOLD – Market is sideways")

# ---------------- PRICE CHART ----------------
fig = go.Figure()

fig.add_trace(go.Scatter(x=prices.index, y=prices, name="Price", line=dict(color="#00E676", width=3)))
fig.add_trace(go.Scatter(x=ma20.index, y=ma20, name="MA 20", line=dict(color="orange")))
fig.add_trace(go.Scatter(x=ma50.index, y=ma50, name="MA 50", line=dict(color="cyan")))

fig.update_layout(title=f"{ticker} Price Trend", template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

# ================== CALCULATORS ==================

def fd_calculator():
    st.subheader("🏦 Fixed Deposit Calculator")
    p = st.number_input("Principal (₹)", 1000)
    r = st.number_input("Interest Rate (%)", 1.0)
    t = st.number_input("Years", 1)
    maturity = p * (1 + r/100) ** t
    st.success(f"💰 Maturity Amount: ₹{maturity:,.2f}")

def sip_calculator():
    st.subheader("📊 SIP Calculator")
    m = st.number_input("Monthly Investment (₹)", 500)
    r = st.number_input("Expected Return (%)", 1.0)
    y = st.number_input("Years", 1)
    n = y * 12
    rate = r / 100 / 12
    future = m * (((1+rate)**n - 1) / rate) * (1+rate)
    st.success(f"💰 Future Value: ₹{future:,.2f}")

def lump_calculator():
    st.subheader("💰 Lumpsum Calculator")
    p = st.number_input("Investment (₹)", 1000)
    r = st.number_input("Annual Return (%)", 1.0)
    t = st.number_input("Years", 1)
    future = p * (1 + r/100) ** t
    st.success(f"💰 Future Value: ₹{future:,.2f}")

# ---------------- FULL SCREEN CALCULATOR ----------------
if fd_btn or sip_btn or lump_btn:
    st.divider()
    st.markdown("## 🧮 Financial Calculator")

    with st.container():
        if fd_btn:
            fd_calculator()
        if sip_btn:
            sip_calculator()
        if lump_btn:
            lump_calculator()

# ---------------- FOOTER ----------------
st.divider()
st.markdown("""
**DataForge – AI Powered Financial Dashboard**  
👨‍💻 Built by **Jaswanth Rathore (JR)**  
🚀 Streamlit Cloud Ready  
""")
