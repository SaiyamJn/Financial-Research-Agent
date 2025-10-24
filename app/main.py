import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Financial Research AI Agent", page_icon="📈", layout="wide")

# ------------------ HEADER ------------------
st.title(" Financial Research AI Agent – Indian Stock Analyzer")
st.markdown(
    "Analyze Indian stock data with real-time charts, basic indicators (MA, RSI), and comparison view."
)

st.info(" Tip: Use `.NS` for NSE stocks and `.BO` for BSE stocks (e.g., RELIANCE.NS, TCS.NS).")

# ------------------ INPUTS ------------------
col1, col2 = st.columns(2)
symbol1 = col1.text_input("Enter 1st Stock Symbol", value="RELIANCE.NS").upper().strip()
symbol2 = col2.text_input("Enter 2nd Stock Symbol (optional)", value="TCS.NS").upper().strip()

period = st.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)

# ------------------ FUNCTIONS ------------------
def fetch_data(symbol):
    """Safely fetch stock data and compute technical indicators."""
    try:
        data = yf.download(symbol, period=period, interval="1d", progress=False)

        # Validate response
        if data.empty:
            return None, f"No data available for {symbol}. Market may be closed or symbol is invalid."

        # Flatten multi-index if needed
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Moving Average (20-day)
        data["MA20"] = data["Close"].rolling(window=20).mean()

        # RSI Calculation (14-day)
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        return data, None

    except Exception as e:
        return None, f"Error fetching data for {symbol}: {e}"


def plot_stock(data, symbol):
    """Generate stock price chart with Moving Average."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name=f"{symbol} Close"))
    fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], mode="lines", name="20-Day MA", line=dict(color="orange")))
    fig.update_layout(
        title=f"{symbol} Stock Price with 20-Day MA",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.25)
    )
    return fig


def plot_rsi(data, symbol):
    """Generate RSI chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["RSI"], mode="lines", name="RSI", line=dict(color="green")))
    fig.add_hline(y=70, line_dash="dot", line_color="red")
    fig.add_hline(y=30, line_dash="dot", line_color="blue")
    fig.update_layout(
        title=f"{symbol} Relative Strength Index (RSI)",
        xaxis_title="Date",
        yaxis_title="RSI",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.25)
    )
    return fig

# ------------------ MAIN SECTION ------------------
st.divider()
colA, colB = st.columns(2)

# ---- STOCK 1 ----
data1, error1 = fetch_data(symbol1)
with colA:
    st.subheader(f" {symbol1}")
    if error1:
        st.warning(error1)
    elif data1 is not None:
        st.plotly_chart(plot_stock(data1, symbol1), use_container_width=True)
        st.plotly_chart(plot_rsi(data1, symbol1), use_container_width=True)
        st.dataframe(data1[["Close", "MA20", "RSI"]].tail(10).style.format("{:.2f}"))
    else:
        st.info("Enter a valid stock symbol to view data.")

# ---- STOCK 2 ----
if symbol2 and symbol2 != symbol1:
    data2, error2 = fetch_data(symbol2)
    with colB:
        st.subheader(f" {symbol2}")
        if error2:
            st.warning(error2)
        elif data2 is not None:
            st.plotly_chart(plot_stock(data2, symbol2), use_container_width=True)
            st.plotly_chart(plot_rsi(data2, symbol2), use_container_width=True)
            st.dataframe(data2[["Close", "MA20", "RSI"]].tail(10).style.format("{:.2f}"))
        else:
            st.info("Enter another valid stock symbol for comparison.")

st.divider()

# ---- COMPARISON SECTION ----
if data1 is not None and "Close" in data1.columns and symbol2 and data2 is not None:
    st.subheader("📊 Stock Price Comparison")
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Scatter(x=data1.index, y=data1["Close"], name=symbol1))
    fig_compare.add_trace(go.Scatter(x=data2.index, y=data2["Close"], name=symbol2))
    fig_compare.update_layout(
        title=f"{symbol1} vs {symbol2} Stock Comparison",
        xaxis_title="Date",
        yaxis_title="Closing Price (INR)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.25)
    )
    st.plotly_chart(fig_compare, use_container_width=True)
elif symbol2:
    st.warning("Comparison unavailable — please check both stock symbols.")

st.divider()
st.caption(f"🧠 Built with Streamlit | Data Source: Yahoo Finance | Last updated: {datetime.now().strftime('%Y-%m-%d')}")
