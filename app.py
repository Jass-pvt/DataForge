import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import cufflinks as cf
from datetime import date
from dateutil.relativedelta import relativedelta

cf.go_offline()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="📈 DataForge | Stock Analytics",
    layout="wide"
)

st.title("📈 DataForge – Stock Market Analytics")
st.caption("Built by Jaswanth Rathore (JR)")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Controls")

ticker = st.sidebar.selectbox(
    "Select Stock",
    ['NVDA', 'INTC', 'AMD', 'TSM', 'MU']
)

months = st.sidebar.slider(
    "Historical Period (Months)",
    1, 24, 6
)

# ---------------- DATA LOADERS ----------------
@st.cache_data(show_spinner=True)
def load_stock(ticker, months):
    data = yf.download(
        ticker,
        start=date.today() - relativedelta(months=months),
        end=date.today()
    )
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

@st.cache_data(show_spinner=True)
def load_sector(tickers, months):
    data = yf.download(
        tickers,
        start=date.today() - relativedelta(months=months),
        end=date.today()
    )
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

# ---------------- MAIN STOCK ----------------
try:
    stock_data = load_stock(ticker, months)

    st.subheader(f"📌 {ticker} Overview")
    st.dataframe(stock_data, use_container_width=True)

    # ---------------- KPIs ----------------
    adj_close = stock_data['Adj Close']
    daily_returns = adj_close.pct_change().dropna()

    latest_price = adj_close.iloc[-1]
    total_return = (adj_close.iloc[-1] / adj_close.iloc[0] - 1) * 100
    volatility = daily_returns.std() * np.sqrt(252)

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Price ($)", f"{latest_price:.2f}")
    col2.metric("Total Return (%)", f"{total_return:.2f}")
    col3.metric("Annual Volatility", f"{volatility:.2f}")

    # ---------------- PRICE GRAPHS ----------------
    st.plotly_chart(
        adj_close.iplot(
            asFigure=True,
            title="Adjusted Close Price",
            colors=['green']
        ),
        use_container_width=True
    )

    st.plotly_chart(
        adj_close.iplot(
            asFigure=True,
            fill=True,
            title="Price Trend (Area Chart)",
            colors=['green']
        ),
        use_container_width=True
    )

    # ---------------- RETURNS GRAPH ----------------
    st.plotly_chart(
        daily_returns.iplot(
            asFigure=True,
            title="Daily Returns Distribution",
            kind='hist'
        ),
        use_container_width=True
    )

    # ---------------- TECHNICAL ANALYSIS ----------------
    qf = cf.QuantFig(
        stock_data,
        title="Technical Indicators",
        legend='top',
        name=ticker
    )
    qf.add_sma([10, 20], width=2)
    qf.add_bollinger_bands()
    qf.add_volume()

    st.plotly_chart(qf.iplot(asFigure=True), use_container_width=True)

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        "⬇️ Download Stock Data (CSV)",
        stock_data.to_csv().encode("utf-8"),
        file_name=f"{ticker}_data.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error("⚠️ Failed to load stock data. Please try again later.")

# ---------------- PORTFOLIO ANALYSIS ----------------
st.divider()
st.subheader("📊 Semiconductor Portfolio Visualization")

semiconductor_tickers = ['NVDA', 'INTC', 'AMD', 'TSM', 'MU']
sector_data = load_sector(semiconductor_tickers, months)

adj_close_sector = sector_data['Adj Close']
sector_returns = adj_close_sector.pct_change().fillna(0)

weights = np.array([0.1, 0.2, 0.25, 0.25, 0.2])

portfolio_returns = (sector_returns * weights).sum(axis=1)
cumulative_returns = (portfolio_returns + 1).cumprod()

# ---------------- PORTFOLIO GRAPHS ----------------

# 1️⃣ Cumulative returns
st.plotly_chart(
    cumulative_returns.iplot(
        asFigure=True,
        title="Cumulative Portfolio Returns"
    ),
    use_container_width=True
)

# 2️⃣ Portfolio allocation (Pie chart)
allocation_df = pd.DataFrame({
    "Stock": semiconductor_tickers,
    "Weight": weights
})

st.plotly_chart(
    allocation_df.iplot(
        kind='pie',
        labels='Stock',
        values='Weight',
        title="Portfolio Allocation"
    ),
    use_container_width=True
)

# 3️⃣ Average returns bar chart
avg_returns = sector_returns.mean() * 252

st.plotly_chart(
    avg_returns.iplot(
        kind='bar',
        title="Annualized Average Returns"
    ),
    use_container_width=True
)

# 4️⃣ Correlation heatmap
st.plotly_chart(
    sector_returns.corr().iplot(
        asFigure=True,
        kind='heatmap',
        title="Stock Correlation Heatmap",
        colorscale='RdBu'
    ),
    use_container_width=True
)

# ---------------- FOOTER ----------------
st.divider()
st.markdown(
    """
    **DataForge – Financial Analytics Dashboard**  
    👨‍💻 Built by **Jaswanth Rathore (JR)**  
    🔗 Live App: https://dataforge-jr.streamlit.app  
    """
)

