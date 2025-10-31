import streamlit as st # type: ignore
import yfinance as yf # type: ignore
import pandas as pd
import plotly.graph_objects as go # type: ignore
from datetime import datetime
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # type: ignore
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Financial Research AI Agent", page_icon="📈", layout="wide")

# ------------------ API KEY (HARDCODED) ------------------
# Enter your News API key here
api_key = "your_api_key_here"  

# ------------------ HEADER ------------------
st.title("📈 Financial Research AI Agent – Indian Stock Analyzer")
st.markdown(
    "Analyze Indian stock data with real-time charts, basic indicators (MA, RSI), news, and sentiment analysis."
)

st.info("💡 Tip: Use `.NS` for NSE stocks and `.BO` for BSE stocks (e.g., RELIANCE.NS, TCS.NS).")

# ------------------ INPUTS ------------------
col1, col2, col3 = st.columns(3)
symbol1 = col1.text_input("Enter 1st Stock Symbol", value="RELIANCE.NS").upper().strip()
symbol2 = col2.text_input("Enter 2nd Stock Symbol (optional)", value="TCS.NS").upper().strip()
period = col3.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)

# ------------------ CACHING FUNCTIONS ------------------
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(symbol, time_period):
    """Safely fetch stock data and compute technical indicators."""
    try:
        data = yf.download(symbol, period=time_period, interval="1d", progress=False)

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


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_financial_news(symbol, api_key_input):
    """Fetch financial news for Indian stocks with filtering."""
    
    if not api_key_input or api_key_input == "YOUR_API_KEY_HERE":
        return None, "API key not configured. Please add your News API key in the code."
    
    # Extract company name from symbol (remove .NS or .BO)
    company_name = symbol.replace(".NS", "").replace(".BO", "")
    
    try:
        # NewsAPI endpoint with Indian business sources
        url = "https://newsapi.org/v2/everything"
        
        params = {
            "q": f"{company_name} stock OR {company_name} share",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": api_key_input,
            "domains": "economictimes.indiatimes.com,moneycontrol.com,business-standard.com,livemint.com,financialexpress.com"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            if not articles:
                return [], "No recent news found for this stock. Try checking the symbol or try again later."
            return articles, None
        elif response.status_code == 401:
            return None, "❌ Invalid API key. Please check your News API key and try again."
        elif response.status_code == 426:
            return None, "❌ API upgrade required. Your current plan doesn't support the requested domains."
        elif response.status_code == 429:
            return None, "⚠️ API rate limit exceeded (100 requests/day on free tier). Please try again later or upgrade your plan."
        else:
            return None, f"API Error: HTTP {response.status_code}. Please try again later."
            
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timeout. Please check your internet connection and try again."
    except requests.exceptions.ConnectionError:
        return None, "🌐 Connection error. Please check your internet connection."
    except Exception as e:
        return None, f"Error fetching news: {str(e)}"


def analyze_sentiment(text):
    """Analyze sentiment using VADER (optimized for financial text)."""
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    
    # Classify based on compound score
    compound = scores['compound']
    if compound >= 0.05:
        sentiment = "Positive"
        color = "🟢"
    elif compound <= -0.05:
        sentiment = "Negative"
        color = "🔴"
    else:
        sentiment = "Neutral"
        color = "🟡"
    
    return sentiment, color, compound


# ------------------ PLOTTING FUNCTIONS ------------------
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
        legend=dict(orientation="h", y=-0.25),
        height=400
    )
    return fig


def plot_rsi(data, symbol):
    """Generate RSI chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["RSI"], mode="lines", name="RSI", line=dict(color="green")))
    fig.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dot", line_color="blue", annotation_text="Oversold")
    fig.update_layout(
        title=f"{symbol} Relative Strength Index (RSI)",
        xaxis_title="Date",
        yaxis_title="RSI",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", y=-0.25),
        height=300
    )
    return fig


def plot_sentiment_gauge(avg_sentiment, symbol):
    """Create a gauge chart for average sentiment."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_sentiment,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{symbol} Sentiment Score"},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.05], 'color': "lightcoral"},
                {'range': [-0.05, 0.05], 'color': "lightyellow"},
                {'range': [0.05, 1], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0
            }
        }
    ))
    fig.update_layout(height=250)
    return fig


def display_news_sentiment(symbol, api_key_input):
    """Display news and sentiment analysis for a stock."""
    st.subheader(f"📰 News & Sentiment Analysis: {symbol}")
    
    if not api_key_input or api_key_input == "YOUR_API_KEY_HERE":
        st.error("🔑 API key not configured. Please add your News API key in the code.")
        st.info("Get your free API key from https://newsapi.org/register (100 requests/day)")
        return
    
    with st.spinner(f"Fetching news for {symbol}..."):
        articles, error = fetch_financial_news(symbol, api_key_input)
    
    if error:
        st.error(error)
        if "rate limit" in error.lower():
            st.info("💡 Tip: News data is cached for 30 minutes. Wait a while before fetching new articles.")
        return
    
    if not articles:
        st.info(f"No recent news available for {symbol}. The stock might not have recent coverage in Indian financial sources.")
        return
    
    # Analyze sentiment for all articles
    sentiments = []
    sentiment_data = []
    
    for article in articles[:8]:  # Limit to 8 articles for display
        title = article.get("title", "No title")
        sentiment, color, compound = analyze_sentiment(title)
        sentiments.append(compound)
        
        sentiment_data.append({
            "title": title,
            "sentiment": sentiment,
            "color": color,
            "score": compound,
            "source": article.get("source", {}).get("name", "Unknown"),
            "date": article.get("publishedAt", "")[:10],
            "url": article.get("url", "#")
        })
    
    # Calculate average sentiment
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    positive_count = sum(1 for s in sentiments if s >= 0.05)
    neutral_count = sum(1 for s in sentiments if -0.05 < s < 0.05)
    negative_count = sum(1 for s in sentiments if s <= -0.05)
    
    col1.metric("Avg Sentiment", f"{avg_sentiment:.2f}", 
                delta="Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral")
    col2.metric("🟢 Positive", positive_count)
    col3.metric("🟡 Neutral", neutral_count)
    col4.metric("🔴 Negative", negative_count)
    
    # Sentiment gauge
    st.plotly_chart(plot_sentiment_gauge(avg_sentiment, symbol), use_container_width=True)
    
    # Display individual headlines
    st.markdown("#### Recent Headlines")
    for idx, item in enumerate(sentiment_data, 1):
        with st.container():
            col_a, col_b = st.columns([0.9, 0.1])
            col_a.markdown(f"**{idx}. [{item['title']}]({item['url']})**")
            col_b.markdown(f"{item['color']} **{item['sentiment']}**")
            st.caption(f"📅 {item['date']} | 📰 {item['source']} | Score: {item['score']:.2f}")
            st.divider()

# ------------------ MAIN SECTION ------------------
st.divider()

# Create tabs for better organization
tab1, tab2 = st.tabs(["📊 Technical Analysis", "📰 News & Sentiment"])

with tab1:
    colA, colB = st.columns(2)

    # ---- STOCK 1 ----
    data1, error1 = fetch_stock_data(symbol1, period)
    with colA:
        st.subheader(f"📈 {symbol1}")
        if error1:
            st.warning(error1)
        elif data1 is not None:
            st.plotly_chart(plot_stock(data1, symbol1), use_container_width=True)
            st.plotly_chart(plot_rsi(data1, symbol1), use_container_width=True)
            
            # Display recent data
            with st.expander("📋 View Recent Data"):
                st.dataframe(data1[["Close", "MA20", "RSI"]].tail(10).style.format("{:.2f}"))
        else:
            st.info("Enter a valid stock symbol to view data.")

    # ---- STOCK 2 ----
    if symbol2 and symbol2 != symbol1:
        data2, error2 = fetch_stock_data(symbol2, period)
        with colB:
            st.subheader(f"📈 {symbol2}")
            if error2:
                st.warning(error2)
            elif data2 is not None:
                st.plotly_chart(plot_stock(data2, symbol2), use_container_width=True)
                st.plotly_chart(plot_rsi(data2, symbol2), use_container_width=True)
                
                with st.expander("📋 View Recent Data"):
                    st.dataframe(data2[["Close", "MA20", "RSI"]].tail(10).style.format("{:.2f}"))
            else:
                st.info("Enter another valid stock symbol for comparison.")

    # ---- COMPARISON SECTION ----
    if data1 is not None and "Close" in data1.columns and symbol2 and data2 is not None:
        st.divider()
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
            legend=dict(orientation="h", y=-0.25),
            height=400
        )
        st.plotly_chart(fig_compare, use_container_width=True)

with tab2:
    st.markdown("### 📰 Financial News & Sentiment Analysis")
    st.caption("Sentiment analysis uses VADER (Valence Aware Dictionary and sEntiment Reasoner) optimized for financial text")
    
    # Display news for Stock 1
    display_news_sentiment(symbol1, api_key)
    
    st.divider()
    
    # Display news for Stock 2 if provided
    if symbol2 and symbol2 != symbol1:
        display_news_sentiment(symbol2, api_key)

st.divider()
st.caption(f"🧠 Built with Streamlit | Data: Yahoo Finance & NewsAPI | Sentiment: VADER | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")