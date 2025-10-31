import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
from dotenv import load_dotenv
import os

load_dotenv()

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Financial Research AI Agent", page_icon="📈", layout="wide")

# ------------------ API KEY ------------------
api_key = "655558496649450db82e67900acc199d"  # IMPORTANT: Add your News API key here from https://newsapi.org/register

# ------------------ HEADER ------------------
st.title("📈 Financial Research AI Agent – Indian Stock Analyzer")
st.markdown("Analyze Indian stock data with real-time charts, basic indicators (MA, RSI), news, and sentiment analysis.")
st.info("💡 Tip: Use `.NS` for NSE stocks and `.BO` for BSE stocks (e.g., RELIANCE.NS, TCS.NS).")

# API Key Status
if not api_key or api_key.strip() == "":
    st.warning("⚠️ News API key not configured. Get your free key from [newsapi.org](https://newsapi.org/register)")
else:
    st.success("✅ News API key configured")

# ------------------ INPUTS ------------------
col1, col2, col3 = st.columns(3)
symbol1 = col1.text_input("Enter 1st Stock Symbol", value="RELIANCE.NS").upper().strip()
symbol2 = col2.text_input("Enter 2nd Stock Symbol (optional)", value="TCS.NS").upper().strip()
period = col3.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)

# Debug button
if st.checkbox("🔧 Debug Mode"):
    st.info(f"**Symbol 1:** {symbol1}")
    st.info(f"**Symbol 2:** {symbol2}")
    st.info(f"**Period:** {period}")
    st.info(f"**Symbol 2 is different:** {symbol2 and symbol2 != symbol1}")

# ------------------ CACHING FUNCTIONS ------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(symbol, time_period):
    """Fetch stock data with error handling."""
    try:
        # Method 1: Direct download
        data = yf.download(symbol, period=time_period, progress=False)
        
        if data.empty:
            return None, f"⚠️ No data for {symbol}. Check symbol format (use .NS for NSE, .BO for BSE)"
        
        # Handle multi-index
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Ensure Close column exists
        if "Close" not in data.columns:
            return None, f"❌ No 'Close' price data for {symbol}"
        
        # Clean data
        data = data.dropna(subset=["Close"])
        
        if len(data) < 20:
            return None, f"⚠️ Insufficient data ({len(data)} days). Need at least 20 days."
        
        # Calculate indicators
        data["MA20"] = data["Close"].rolling(window=20).mean()
        
        # RSI
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        avg_loss = avg_loss.replace(0, 1e-10)
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))
        
        # Reset index
        data = data.reset_index()
        
        return data, None

    except Exception as e:
        return None, f"❌ Error: {str(e)}"


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_financial_news(symbol, api_key_input):
    """Fetch news articles."""
    if not api_key_input or api_key_input.strip() == "":
        return None, "🔑 API key not configured"
    
    company_name = symbol.replace(".NS", "").replace(".BO", "")
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{company_name}",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": api_key_input.strip()
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            articles = result.get("articles", [])
            if not articles:
                return [], f"ℹ️ No news found for {company_name}"
            return articles, None
        elif response.status_code == 401:
            return None, "❌ Invalid API key"
        elif response.status_code == 429:
            return None, "⚠️ Rate limit exceeded (100/day on free tier)"
        else:
            error_msg = response.json().get("message", f"HTTP {response.status_code}")
            return None, f"⚠️ API Error: {error_msg}"
            
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timeout"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def analyze_sentiment(text):
    """Analyze sentiment using VADER."""
    try:
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            return "Positive", "🟢", compound
        elif compound <= -0.05:
            return "Negative", "🔴", compound
        else:
            return "Neutral", "🟡", compound
    except:
        return "Neutral", "🟡", 0.0


# ------------------ PLOTTING FUNCTIONS ------------------
def plot_stock(data, symbol):
    """Stock price chart."""
    fig = go.Figure()
    
    x_data = data["Date"] if "Date" in data.columns else data.index
    
    fig.add_trace(go.Scatter(
        x=x_data, y=data["Close"], mode="lines", name=f"{symbol} Close",
        line=dict(color="#1f77b4", width=2.5)
    ))
    
    fig.add_trace(go.Scatter(
        x=x_data, y=data["MA20"], mode="lines", name="20-Day MA",
        line=dict(color="#ff7f0e", width=2, dash="dash")
    ))
    
    fig.update_layout(
        title=f"<b>{symbol}</b> Stock Price",
        xaxis_title="Date", yaxis_title="Price (INR)",
        hovermode="x unified", template="plotly_white",
        height=400, margin=dict(t=50, b=50)
    )
    
    return fig


def plot_rsi(data, symbol):
    """RSI chart."""
    fig = go.Figure()
    
    x_data = data["Date"] if "Date" in data.columns else data.index
    
    fig.add_trace(go.Scatter(
        x=x_data, y=data["RSI"], mode="lines", name="RSI",
        line=dict(color="#2ca02c", width=2.5)
    ))
    
    fig.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dot", line_color="blue", annotation_text="Oversold (30)")
    fig.add_hline(y=50, line_dash="dot", line_color="gray", line_width=1, opacity=0.5)
    
    fig.update_layout(
        title=f"<b>{symbol}</b> RSI",
        xaxis_title="Date", yaxis_title="RSI Value",
        template="plotly_white", height=300, yaxis=dict(range=[0, 100])
    )
    
    return fig


def plot_sentiment_gauge(avg_sentiment, symbol):
    """Sentiment gauge."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_sentiment,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{symbol}</b><br>Avg Sentiment", 'font': {'size': 18}},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.05], 'color': '#ffcccc'},
                {'range': [-0.05, 0.05], 'color': '#ffffcc'},
                {'range': [0.05, 1], 'color': '#ccffcc'}
            ],
            'threshold': {'line': {'color': "red", 'width': 3}, 'value': 0}
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def display_stock_section(symbol, period):
    """Display stock analysis section."""
    st.markdown(f"#### {symbol}")
    
    with st.spinner(f"Loading {symbol}..."):
        data, error = fetch_stock_data(symbol, period)
    
    if error:
        st.error(error)
        return None
    
    if data is None or data.empty:
        st.warning(f"No data available for {symbol}")
        return None
    
    # Metrics
    latest_price = data['Close'].iloc[-1]
    price_change = data['Close'].iloc[-1] - data['Close'].iloc[-2] if len(data) > 1 else 0
    price_change_pct = (price_change / data['Close'].iloc[-2] * 100) if len(data) > 1 and data['Close'].iloc[-2] != 0 else 0
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Latest Price", f"₹{latest_price:.2f}", f"{price_change_pct:+.2f}%")
    col_m2.metric("Data Points", len(data))
    col_m3.metric("Latest RSI", f"{data['RSI'].iloc[-1]:.2f}" if not pd.isna(data['RSI'].iloc[-1]) else "N/A")
    
    # Charts
    st.plotly_chart(plot_stock(data, symbol), use_container_width=True)
    st.plotly_chart(plot_rsi(data, symbol), use_container_width=True)
    
    # Data table
    with st.expander("📋 Recent Data"):
        display_cols = ["Close", "MA20", "RSI"]
        if "Date" in data.columns:
            display_cols.insert(0, "Date")
        
        recent = data[display_cols].tail(10).copy()
        if "Date" in recent.columns:
            recent["Date"] = pd.to_datetime(recent["Date"]).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            recent.style.format({
                "Close": "₹{:.2f}",
                "MA20": "₹{:.2f}",
                "RSI": "{:.2f}"
            }),
            use_container_width=True
        )
    
    return data


def display_news_section(symbol, api_key_input):
    """Display news and sentiment."""
    st.subheader(f"📰 News & Sentiment: {symbol}")
    
    if not api_key_input or api_key_input.strip() == "":
        st.error("🔑 News API key not configured!")
        st.info("Get your free API key from [newsapi.org/register](https://newsapi.org/register)")
        return
    
    with st.spinner(f"Fetching news for {symbol}..."):
        articles, error = fetch_financial_news(symbol, api_key_input)
    
    if error:
        st.error(error)
        return
    
    if not articles or len(articles) == 0:
        st.warning(f"No news articles found for {symbol}")
        return
    
    # Analyze sentiment
    sentiments = []
    sentiment_data = []
    
    for article in articles[:8]:
        title = article.get("title", "No title")
        description = article.get("description", "")
        
        full_text = f"{title}. {description}" if description else title
        sentiment, color, compound = analyze_sentiment(full_text)
        sentiments.append(compound)
        
        sentiment_data.append({
            "title": title,
            "description": description,
            "sentiment": sentiment,
            "color": color,
            "score": compound,
            "source": article.get("source", {}).get("name", "Unknown"),
            "date": article.get("publishedAt", "")[:10],
            "url": article.get("url", "#")
        })
    
    if not sentiments:
        st.warning("Could not analyze sentiment")
        return
    
    # Summary
    avg_sentiment = sum(sentiments) / len(sentiments)
    positive_count = sum(1 for s in sentiments if s >= 0.05)
    neutral_count = sum(1 for s in sentiments if -0.05 < s < 0.05)
    negative_count = sum(1 for s in sentiments if s <= -0.05)
    
    st.markdown("#### 📊 Sentiment Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Score", f"{avg_sentiment:.3f}")
    col2.metric("🟢 Positive", positive_count)
    col3.metric("🟡 Neutral", neutral_count)
    col4.metric("🔴 Negative", negative_count)
    
    # Gauge
    st.plotly_chart(plot_sentiment_gauge(avg_sentiment, symbol), use_container_width=True)
    
    # Interpretation
    if avg_sentiment >= 0.05:
        st.success(f"✅ **POSITIVE** - Favorable news coverage for {symbol}")
    elif avg_sentiment <= -0.05:
        st.error(f"⚠️ **NEGATIVE** - Concerning news coverage for {symbol}")
    else:
        st.info(f"ℹ️ **NEUTRAL** - Balanced news coverage for {symbol}")
    
    # Headlines
    st.markdown("#### 📰 Headlines")
    for idx, item in enumerate(sentiment_data, 1):
        with st.expander(f"{item['color']} **{idx}. {item['title']}**"):
            if item['description']:
                st.markdown(f"*{item['description']}*")
            st.markdown(f"[🔗 Read Article]({item['url']})")
            st.caption(f"Score: {item['score']:.3f} | {item['date']} | {item['source']}")


# ------------------ MAIN APPLICATION ------------------
st.divider()

tab1, tab2 = st.tabs(["📊 Technical Analysis", "📰 News & Sentiment"])

with tab1:
    st.markdown("### 📈 Stock Price & Technical Indicators")
    
    # Display Stock 1
    colA, colB = st.columns(2)
    
    with colA:
        data1 = display_stock_section(symbol1, period)
    
    # Display Stock 2 only if different
    with colB:
        if symbol2 and symbol2.strip() and symbol2 != symbol1:
            data2 = display_stock_section(symbol2, period)
        else:
            st.info("💡 Enter a second stock symbol above for comparison")
            data2 = None
    
    # Comparison Chart
    if data1 is not None and data2 is not None:
        st.divider()
        st.markdown("### 📊 Comparison Chart")
        
        fig = go.Figure()
        
        x1 = data1["Date"] if "Date" in data1.columns else data1.index
        x2 = data2["Date"] if "Date" in data2.columns else data2.index
        
        fig.add_trace(go.Scatter(
            x=x1, y=data1["Close"], name=symbol1,
            line=dict(width=2.5, color="#1f77b4")
        ))
        
        fig.add_trace(go.Scatter(
            x=x2, y=data2["Close"], name=symbol2,
            line=dict(width=2.5, color="#ff7f0e")
        ))
        
        fig.update_layout(
            title=f"<b>{symbol1} vs {symbol2}</b>",
            xaxis_title="Date", yaxis_title="Price (INR)",
            hovermode="x unified", template="plotly_white", height=450
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance
        st.markdown("#### 📈 Performance Comparison")
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown(f"**{symbol1}**")
            perf1 = ((data1['Close'].iloc[-1] - data1['Close'].iloc[0]) / data1['Close'].iloc[0] * 100)
            st.metric("Period Return", f"{perf1:+.2f}%")
        
        with comp_col2:
            st.markdown(f"**{symbol2}**")
            perf2 = ((data2['Close'].iloc[-1] - data2['Close'].iloc[0]) / data2['Close'].iloc[0] * 100)
            st.metric("Period Return", f"{perf2:+.2f}%")

with tab2:
    st.markdown("### 📰 News & Sentiment Analysis")
    
    # News for Stock 1
    display_news_section(symbol1, api_key)
    
    st.divider()
    
    # News for Stock 2
    if symbol2 and symbol2.strip() and symbol2 != symbol1:
        display_news_section(symbol2, api_key)
    else:
        st.info("💡 Add a second stock symbol for comparison")

# ------------------ FOOTER ------------------
st.divider()
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("**Data:** Yahoo Finance, NewsAPI")
with footer_col2:
    st.caption("**Indicators:** 20-Day MA, 14-Day RSI")
with footer_col3:
    st.caption("**Sentiment:** VADER")

st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
st.caption("⚠️ For educational purposes only. Not financial advice.")