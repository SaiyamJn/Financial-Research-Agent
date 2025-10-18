import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.title("Financial Research AI Agent – Prototype")

symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS, TCS.NS):", "RELIANCE.NS")
data = yf.download(symbol, period="1mo", interval="1d")

if not data.empty:
    fig = px.line(data, x=data.index, y="Close", title=f"{symbol} Stock Prices (1 Month)")
    st.plotly_chart(fig)
else:
    st.warning("No data found. Try another symbol.")
