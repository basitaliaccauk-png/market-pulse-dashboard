import pandas as pd
import yfinance as yf
import plotly.express as px
import streamlit as st


# -----------------------------
# Title
# -----------------------------

st.title("Market Pulse Dashboard")


# -----------------------------
# Asset Dictionary
# -----------------------------

TICKERS = {
    "FTSE 100": "^FTSE",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Gold": "GC=F",
    "Oil": "CL=F",
    "VIX": "^VIX"
}


# -----------------------------
# Sidebar Controls
# -----------------------------

st.sidebar.header("Controls")

start_date = st.sidebar.date_input(
    "Start Date",
    value=pd.to_datetime("2023-01-01")
)

selected_assets = st.sidebar.multiselect(
    "Select Assets",
    list(TICKERS.keys()),
    default=list(TICKERS.keys())
)

if len(selected_assets) == 0:
    st.warning("Please select at least one asset.")
    st.stop()



# Time Range Selector
time_range = st.sidebar.radio(
    "Select Time Range",
    ["1M", "3M", "6M", "1Y", "Max"],
    index=3
)

# Convert time range into start date
today = pd.Timestamp.today()

if time_range == "1M":
    start_date = today - pd.DateOffset(months=1)
elif time_range == "3M":
    start_date = today - pd.DateOffset(months=3)
elif time_range == "6M":
    start_date = today - pd.DateOffset(months=6)
elif time_range == "1Y":
    start_date = today - pd.DateOffset(years=1)
else:
    start_date = "2020-01-01"
# -----------------------------
# Data Download
# -----------------------------

data = yf.download(
    [TICKERS[a] for a in selected_assets],
    start=start_date,
    auto_adjust=True,
    progress=False
)["Close"]

if isinstance(data, pd.Series):
    data = data.to_frame()

data.columns = selected_assets


# -----------------------------
# Normalization & Returns
# -----------------------------

normalized = data / data.iloc[0] * 100
returns = normalized.pct_change().dropna()


# -----------------------------
# Summary Metrics
# -----------------------------

st.subheader("Summary")

col1, col2, col3 = st.columns(3)

latest_returns = normalized.iloc[-1] - 100
vol = returns.std() * (252 ** 0.5) * 100

with col1:
    st.metric("Best Performer",
              latest_returns.idxmax(),
              f"{latest_returns.max():.2f}%")

with col2:
    st.metric("Worst Performer",
              latest_returns.idxmin(),
              f"{latest_returns.min():.2f}%")

with col3:
    st.metric("Most Volatile",
              vol.idxmax(),
              f"{vol.max():.2f}%")


# -----------------------------
# Performance Chart
# -----------------------------

df = normalized.reset_index()

fig = px.line(
    df,
    x="Date",
    y=df.columns[1:],
    title="Market Performance (Base = 100)"
)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Statistics Table
# -----------------------------

stats = pd.DataFrame({
    "Total Return (%)": (normalized.iloc[-1] - 100),
    "Volatility (%)": vol
})

st.subheader("Performance Statistics")
st.dataframe(stats.round(2))


# -----------------------------
# Correlation Heatmap
# -----------------------------

st.subheader("Asset Correlation")

corr = returns.corr()

fig_corr = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdBu_r",
    title="Correlation Matrix"
)

st.plotly_chart(fig_corr, use_container_width=True)


# -----------------------------
# Rolling Volatility
# -----------------------------

st.subheader("Rolling Volatility (30-Day)")

rolling_vol = returns.rolling(window=30).std() * (252 ** 0.5)

df_vol = rolling_vol.reset_index()

fig_vol = px.line(
    df_vol,
    x="Date",
    y=df_vol.columns[1:],
    title="30-Day Annualized Volatility"
)

st.plotly_chart(fig_vol, use_container_width=True)


# -----------------------------
# Drawdown
# -----------------------------

st.subheader("Drawdown (Loss from Peak)")

cumulative = (1 + returns).cumprod()
running_max = cumulative.cummax()
drawdown = (cumulative - running_max) / running_max * 100

df_dd = drawdown.reset_index()

fig_dd = px.line(
    df_dd,
    x="Date",
    y=df_dd.columns[1:],
    title="Drawdown (%)"
)

st.plotly_chart(fig_dd, use_container_width=True)


# -----------------------------
# Insights
# -----------------------------

st.subheader("Market Insights")

best_asset = latest_returns.idxmax()
worst_asset = latest_returns.idxmin()
most_volatile = vol.idxmax()

st.write(f"Best performing asset: {best_asset}")
st.write(f"Worst performing asset: {worst_asset}")
st.write(f"Most volatile asset: {most_volatile}")