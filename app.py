import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import cufflinks as cf
from datetime import date
from dateutil.relativedelta import relativedelta

cf.go_offline()

st.set_page_config(page_title="📈 Stock Price Dashboard", layout="wide")

st.title("📈 Stock Price Dashboard")
st.write("Interactive dashboard with financial data")

# Sidebar inputs
ticker = st.sidebar.selectbox(
    "Please select ticker",
    ['NVDA', 'INTC', 'AMD', 'TSM', 'MU'],
    index=0
)

period = st.sidebar.slider(
    "Past Month(s)",
    min_value=1,
    max_value=12,
    value=3
)

st.subheader(f"Selected ticker: {ticker}")

# Fetch stock data
stock_data = yf.download(
    ticker,
    start=date.today() - relativedelta(months=period),
    end=date.today()
)

st.dataframe(stock_data)

# Adjusted Close
st.plotly_chart(
    stock_data['Adj Close'].iplot(
        asFigure=True,
        title='Adjusted Close',
        colors=['green']
    ),
    use_container_width=True
)

# Filled Area
st.plotly_chart(
    stock_data['Adj Close'].iplot(
        asFigure=True,
        fill=True,
        title='Adjusted Close (Filled Area)',
        colors=['green']
    ),
    use_container_width=True
)

# Returns
st.plotly_chart(
    stock_data['Adj Close'].iplot(
        asFigure=True,
        bestfit=True,
        title='Returns',
        bestfit_colors=['black']
    ),
    use_container_width=True
)

# Quant Figure
qf = cf.QuantFig(stock_data, title='Quantitative Figure', legend='top', name=ticker)
qf.add_sma([10, 20], width=2)
qf.add_bollinger_bands()
qf.add_volume()

st.plotly_chart(qf.iplot(asFigure=True), use_container_width=True)

# Portfolio Analysis
st.subheader("📊 Semiconductor Portfolio Analysis")

semiconductor_tickers = ['NVDA', 'INTC', 'AMD', 'TSM', 'MU']
semiconductor_data = yf.download(
    semiconductor_tickers,
    start=date.today() - relativedelta(months=period),
    end=date.today()
)

st.plotly_chart(
    semiconductor_data['Adj Close'].iplot(
        asFigure=True,
        title='Semiconductor Adjusted Close Prices'
    ),
    use_container_width=True
)

returns = semiconductor_data['Adj Close'].pct_change().fillna(0)
weights = np.array([0.1, 0.2, 0.25, 0.25, 0.2])

portfolio_returns = (returns * weights).sum(axis=1)
cumulative_returns = (portfolio_returns + 1).cumprod()

st.plotly_chart(
    cumulative_returns.iplot(
        asFigure=True,
        title='Cumulative Portfolio Returns'
    ),
    use_container_width=True
)
