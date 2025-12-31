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
    df = yf.download(
        ticker,
        start=date.today() - relativedelta(months=months),
        end=date.today(),
        group_by="column",
        auto_adjust=False
    )

    # Flatten columns if MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


@st.cache_data(show_spinner=True)
def load_sector(tickers, months):
    df = yf.download(
        tickers,
        start=date.today() - relativedelta(months=months),
        end=date.today(),
        group_by="column",
        auto_adjust=False
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


# ---------------- MAIN STOCK ----------------
try:
    stock_data = load_stock(ticker, months)

    # ✅ SAFE price column selection
    price_col = "Adj Close" if "Adj Close" in stock_data.columns else "Close"

    st.subheader(f"📌 {ticker} Overview")
    st.dataframe(stock_data, use_container_width=True)

    prices = stock_data[price_col]
    returns = prices.pct_change().dropna()

    # ---------------- KPIs ----------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Price ($)", f"{prices.iloc[-1]:.2f}")
    col2.metric(
        "Total Return (%)",
        f"{((prices.iloc[-1] / prices.iloc[0]) - 1) * 100:.2f}"
    )
    col3.metric(
        "Annual Volatility",
        f"{returns.std() * np.sqrt(252):.2f}"
    )

    # ---------------- PRICE GRAPHS ----------------
    st.plotly_chart(
        prices.iplot(
            asFigure=True,
            title=f"{ticker} Price Trend",
            colors=["green"]
        ),
        use_container_width=True
    )

    st.plotly_chart(
        prices.iplot(
            asFigure=True,
            fill=True,
            title="Price Area Representation",
            colors=["green"]
        ),
        use_container_width=True
    )

    # ---------------- RETURNS HISTOGRAM ----------------
    st.plotly_chart(
        returns.iplot(
            asFigure=True,
            kind="hist",
            title="Daily Returns Distribution"
        ),
        use_container_width=True
    )

    # ---------------- TECHNICAL ANALYSIS ----------------
    qf = cf.QuantFig(
        stock_data,
        title="Technical Indicators",
        legend="top",
        name=ticker
    )
    qf.add_sma([10, 20])
    qf.add_bollinger_bands()
    qf.add_volume()

    st.plotly_chart(qf.iplot(asFigure=True), use_container_width=True)

except Exception as e:
    st.error("⚠️ Unable to load stock data. Please try again.")

# ---------------- PORTFOLIO ANALYSIS ----------------
st.divider()
st.subheader("📊 Semiconductor Portfolio Visualization")

sector_data = load_sector(['NVDA', 'INTC', 'AMD', 'TSM', 'MU'], months)

price_col = "Adj Close" if "Adj Close" in sector_data.columns else "Close"
prices = sector_data[price_col]

returns = prices.pct_change().fillna(0)

weights = np.array([0.1, 0.2, 0.25, 0.25, 0.2])
portfolio_returns = (returns * weights).sum(axis=1)
cumulative_returns = (portfolio_returns + 1).cumprod()

# ---------------- PORTFOLIO GRAPHS ----------------
st.plotly_chart(
    cumulative_returns.iplot(
        asFigure=True,
        title="Cumulative Portfolio Returns"
    ),
    use_container_width=True
)

allocation = pd.DataFrame({
    "Stock": prices.columns,
    "Weight": weights
})

st.plotly_chart(
    allocation.iplot(
        kind="pie",
        labels="Stock",
        values="Weight",
        title="Portfolio Allocation"
    ),
    use_container_width=True
)

st.plotly_chart(
    returns.corr().iplot(
        asFigure=True,
        kind="heatmap",
        title="Correlation Heatmap",
        colorscale="RdBu"
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

