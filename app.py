import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="📈 DataForge | Stock Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- TITLE ----------------
st.title("📈 DataForge – Stock Market Analytics")
st.caption("Built by Jaswanth Rathore (JR)")
st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛️ Market Controls")
st.sidebar.divider()

ticker = st.sidebar.selectbox(
    "📌 Select Stock",
    ['NVDA', 'INTC', 'AMD', 'TSM', 'MU']
)

months = st.sidebar.slider(
    "🕒 Historical Period (Months)",
    1, 24, 6
)

st.sidebar.info("📊 Data Source: Yahoo Finance")

# ---------------- DATA LOADER ----------------
@st.cache_data(show_spinner=True)
def load_stock(ticker, months):
    df = yf.download(
        ticker,
        start=date.today() - relativedelta(months=months),
        end=date.today(),
        auto_adjust=False
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

@st.cache_data(show_spinner=True)
def load_sector(tickers, months):
    df = yf.download(
        tickers,
        start=date.today() - relativedelta(months=months),
        end=date.today(),
        auto_adjust=False
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# ---------------- MAIN APP ----------------
try:
    stock_data = load_stock(ticker, months)

    price_col = "Adj Close" if "Adj Close" in stock_data.columns else "Close"
    prices = stock_data[price_col]
    returns = prices.pct_change().dropna()

    # ---------------- KPI METRICS ----------------
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Latest Price",
        f"${prices.iloc[-1]:.2f}",
        delta=f"{returns.iloc[-1]*100:.2f}%"
    )

    col2.metric(
        "📈 Total Return",
        f"{((prices.iloc[-1] / prices.iloc[0]) - 1) * 100:.2f}%"
    )

    col3.metric(
        "⚡ Annual Volatility",
        f"{returns.std() * np.sqrt(252):.2f}"
    )

    st.divider()

    # ---------------- TABS ----------------
    tab1, tab2, tab3 = st.tabs(["📈 Charts", "📐 Indicators", "📊 Data"])

    # ---------------- PRICE CHART ----------------
    with tab1:
        ma20 = prices.rolling(20).mean()
        ma50 = prices.rolling(50).mean()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=prices.index,
            y=prices,
            mode="lines",
            name="Price",
            line=dict(color="#00E676", width=3)
        ))

        fig.add_trace(go.Scatter(
            x=ma20.index,
            y=ma20,
            name="MA 20",
            line=dict(color="orange")
        ))

        fig.add_trace(go.Scatter(
            x=ma50.index,
            y=ma50,
            name="MA 50",
            line=dict(color="cyan")
        ))

        fig.update_layout(
            title=f"{ticker} Price Trend",
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Returns Histogram
        hist = go.Figure()
        hist.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            marker_color="#00E676"
        ))
        hist.update_layout(
            title="Daily Returns Distribution",
            template="plotly_dark"
        )

        st.plotly_chart(hist, use_container_width=True)

    # ---------------- TECHNICAL INDICATORS ----------------
    with tab2:
        upper_band = ma20 + 2 * prices.rolling(20).std()
        lower_band = ma20 - 2 * prices.rolling(20).std()

        bb = go.Figure()

        bb.add_trace(go.Scatter(x=prices.index, y=prices, name="Price"))
        bb.add_trace(go.Scatter(x=upper_band.index, y=upper_band, name="Upper Band"))
        bb.add_trace(go.Scatter(x=lower_band.index, y=lower_band, name="Lower Band"))

        bb.update_layout(
            title="Bollinger Bands",
            template="plotly_dark",
            height=450
        )

        st.plotly_chart(bb, use_container_width=True)

    # ---------------- RAW DATA ----------------
    with tab3:
        st.dataframe(stock_data, use_container_width=True)

except Exception as e:
    st.error("⚠️ Unable to load stock data.")

# ---------------- PORTFOLIO ANALYSIS ----------------
st.divider()
st.subheader("📊 Semiconductor Portfolio Overview")

sector_data = load_sector(['NVDA', 'INTC', 'AMD', 'TSM', 'MU'], months)
price_col = "Adj Close" if "Adj Close" in sector_data.columns else "Close"

prices = sector_data[price_col]
returns = prices.pct_change().fillna(0)

weights = np.array([0.1, 0.2, 0.25, 0.25, 0.2])
portfolio_returns = (returns * weights).sum(axis=1)
cumulative_returns = (portfolio_returns + 1).cumprod()

col1, col2 = st.columns([2, 1])

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cumulative_returns.index,
        y=cumulative_returns,
        line=dict(color="#00E676", width=3)
    ))
    fig.update_layout(
        title="📈 Portfolio Growth",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    allocation = pd.DataFrame({
        "Stock": prices.columns,
        "Weight": weights
    })

    pie = go.Figure(data=[go.Pie(
        labels=allocation["Stock"],
        values=allocation["Weight"],
        hole=0.4
    )])

    pie.update_layout(
        title="📐 Portfolio Allocation",
        template="plotly_dark"
    )

    st.plotly_chart(pie, use_container_width=True)

# ---------------- CORRELATION HEATMAP ----------------
corr = returns.corr()

heatmap = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=corr.columns,
    y=corr.columns,
    colorscale="RdBu"
))

heatmap.update_layout(
    title="🔗 Correlation Heatmap",
    template="plotly_dark"
)

st.plotly_chart(heatmap, use_container_width=True)

# ---------------- FOOTER ----------------
st.divider()
st.markdown(
    """
    **DataForge – Financial Analytics Dashboard**  
    👨‍💻 Built by **Jaswanth Rathore (JR)**  
    🚀 Streamlit Cloud Deployed  
    """
)

