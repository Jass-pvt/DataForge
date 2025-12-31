import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import cufflinks as cf
from datetime import date
from dateutil.relativedelta import relativedelta

cf.go_offline()

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="📈 DataForge | Stock Analytics",
    layout="wide"
)

st.title("📈 DataForge – Stock Market Analytics")
st.caption("Built by Jaswanth Rathore (JR)")

# -------------------- SIDEBAR --------------------
st.sidebar.header("⚙️ Controls")

ticker = st.sidebar.selectbox(
    "Select Stock Ticker",
    ['NVDA', 'INTC', 'AMD', 'TSM', 'MU']
)

months = st.sidebar.slider(
    "Historical Data (Months)",
    1, 24, 6
)

# -------------------- DATA LOADER --------------------
@st.cache_data(show_spinner=True)
def load_stock_data(ticker, months):
    return yf.download(
        ticker,
        start=date.today() - relativedelta(months=months),
        end=date.today()
    )

@st.cache_data(show_spinner=True)
def load_sector_data(tickers, months):
    return yf.download(
        tickers,
        start=date.today() - relativedelta(months=months),
        end=date.today()
    )

# -------------------- MAIN DATA --------------------
try:
    stock_data = load_stock_data(ticker, months)

    st.subheader(f"📌 {ticker} Stock Overview")
    st.dataframe(stock_data, use_container_width=True)

    # -------------------- KPIs --------------------
    latest_price = stock_data['Adj Close'].iloc[-1]
    returns = stock_data['Adj Close'].pct_change()
    volatility = returns.std() * np.sqrt(252)
    total_return = (latest_price / stock_data['Adj Close'].iloc[0] - 1) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Price ($)", f"{latest_price:.2f}")
    col2.metric("Total Return (%)", f"{total_return:.2f}")
    col3.metric("Annual Volatility", f"{volatility:.2f}")

    # -------------------- PRICE CHARTS --------------------
    st.plotly_chart(
        stock_data['Adj Close'].iplot(
            asFigure=True,
            title="Adjusted Close Price",
            colors=['green']
        ),
        use_container_width=True
    )

    st.plotly_chart(
        stock_data['Adj Close'].iplot(
            asFigure=True,
            fill=True,
            title="Price Trend (Area)",
            colors=['green']
        ),
        use_container_width=True
    )

    # -------------------- RETURNS --------------------
    st.plotly_chart(
        returns.iplot(
            asFigure=True,
            title="Daily Returns",
            bestfit=True
        ),
        use_container_width=True
    )

    # -------------------- QUANT FIG --------------------
    qf = cf.QuantFig(
        stock_data,
        title="Technical Analysis",
        legend='top',
        name=ticker
    )
    qf.add_sma([10, 20], width=2)
    qf.add_bollinger_bands()
    qf.add_volume()

    st.plotly_chart(qf.iplot(asFigure=True), use_container_width=True)

    # -------------------- DOWNLOAD --------------------
    st.download_button(
        "⬇️ Download Stock Data (CSV)",
        stock_data.to_csv().encode("utf-8"),
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error("⚠️ Unable to load stock data. Please try again.")

# -------------------- PORTFOLIO ANALYSIS --------------------
st.divider()
st.subheader("📊 Semiconductor Portfolio Analysis")

semiconductor_tickers = ['NVDA', 'INTC', 'AMD', 'TSM', 'MU']
sector_data = load_sector_data(semiconductor_tickers, months)

adj_close = sector_data['Adj Close']
returns = adj_close.pct_change().fillna(0)

weights = np.array([0.1, 0.2, 0.25, 0.25, 0.2])

portfolio_returns = (returns * weights).sum(axis=1)
cumulative_returns = (portfolio_returns + 1).cumprod()

# Portfolio chart
st.plotly_chart(
    cumulative_returns.iplot(
        asFigure=True,
        title="Cumulative Portfolio Returns"
    ),
    use_container_width=True
)

# Sharpe Ratio
sharpe_ratio = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)
st.metric("📈 Portfolio Sharpe Ratio", f"{sharpe_ratio:.2f}")

# -------------------- CORRELATION --------------------
st.subheader("🔗 Stock Correlation Heatmap")

st.plotly_chart(
    returns.corr().iplot(
        asFigure=True,
        kind='heatmap',
        title="Correlation Matrix",
        colorscale='RdBu'
    ),
    use_container_width=True
)

# -------------------- FOOTER --------------------
st.divider()
st.markdown(
    "🔗 **GitHub:** https://github.com/Jass-pvt  \n"
    "🚀 **Live App:** dataforge-jr.streamlit.app"
)
