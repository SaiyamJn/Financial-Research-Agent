import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Financial Research AI Agent", page_icon="📈", layout="wide")

st.title("📊 Financial Research AI Agent – Indian Stock Analyzer")
st.markdown(
    "Enter an Indian stock symbol below (e.g., **RELIANCE.NS**, **TCS.NS**, **INFY.NS**, **HDFCBANK.NS**) "
    "to view its price trends and key stats."
)

symbol = st.text_input("Stock Symbol", value="RELIANCE.NS").upper()
period = st.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=1)

if symbol:
    try:
        # Fetch data
        data = yf.download(symbol, period=period, interval="1d", progress=False)

        # ---- FIX FOR MULTI-INDEX ----
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if not data.empty:
            st.success(f"✅ Showing data for **{symbol}**")

            # ---- STOCK INFO ----
            ticker = yf.Ticker(symbol)
            info = ticker.info
            st.subheader("Company Information")
            st.write({
                "Name": info.get("longName", "N/A"),
                "Sector": info.get("sector", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "Previous Close": info.get("previousClose", "N/A"),
            })

            # ---- PLOT CHART ----
            fig = px.line(
                data,
                x=data.index,
                y="Close",
                title=f"{symbol} Stock Closing Prices ({period})",
                labels={"Close": "Closing Price (INR)", "Date": "Date"},
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # ---- SUMMARY STATISTICS ----
            st.subheader("Price Summary")
            st.dataframe(data.describe().T.style.format("{:.2f}"))
        else:
            st.warning("⚠️ No data found. Check the symbol or try another period.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.info("Enter a stock symbol to begin.")
