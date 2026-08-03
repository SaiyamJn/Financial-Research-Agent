# 📊 Financial Research AI Agent

An **AI-powered financial research assistant** that analyzes **Indian stock market data** and visualizes key trends through interactive charts and technical indicators.  
This project is part of the **8-Week Financial Research AI Agent Development Program** focused on practical fintech data analysis and AI integration.

---

## 🧠 Project Overview

This application helps users analyze Indian stock data in real-time using financial APIs and AI-powered agents.  
It provides:
- 📈 **Live Stock Analysis** via Yahoo Finance  
- ⚙️ **Technical Indicators** such as Moving Average (MA20) and Relative Strength Index (RSI)  
- 🧾 **Stock Comparison** between two Indian stocks  
- 🤖 **AI Agent Workflows** for research, sentiment analysis, and portfolio insights
- 💬 **LLM Integration** with Gemini and Groq for intelligent analysis

The goal is to develop a working **financial research assistant** that demonstrates core fintech skills — data handling, analytics, visualization, and AI integration.

---

## 🧩 Features Implemented

✅ Real-time Indian stock data fetching  
✅ Interactive price charts using Plotly  
✅ Company info and summary statistics display  
✅ Technical indicators: 20-day MA & 14-day RSI  
✅ Two-stock comparison view  
✅ React-based interactive UI  
✅ **AI Agent Workflows** (Research, Sentiment, Portfolio, Unified Analysis)
✅ **LLM Integration** (Gemini-Pro & Groq Llama3)
✅ **MongoDB** for data persistence
✅ **Redis** for caching

---

## 🚀 Quick Start

### Backend Setup

**Terminal 1:**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# or
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

**Terminal 2:**
```bash
cd frontend/s
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port shown in terminal)

### Environment Configuration

Create a `.env` file in the `backend` directory:

```env
# News API
NEWS_API_KEY=your_news_api_key

# Database
MONGO_URI=mongodb+srv://username:password@agenticai.vpefmoj.mongodb.net/?appName=AgenticAi
MONGO_DB_NAME=financial

# Cache
REDIS_URL=redis://redis:6379/0

# LLM API Keys (at least one required for AI agents)
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## 📡 API Endpoints

### 🤖 AI Agent Routes (`/api/agents`)

#### 1. **Unified Analysis Agent** ⭐
Combines sentiment, technical, and LLM analysis into a single comprehensive response.

**POST** `/api/agents/unified`
```json
{
  "ticker": "AAPL",
  "description": "analyze this stock" // optional
}
```

**GET** `/api/agents/unified/{ticker}?description=analyze%20this%20stock`
- Query params: `description` (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    // Combined analysis results
  },
  "message": "Unified analysis complete"
}
```

#### 2. **Research Agent**
Performs comprehensive research analysis on a stock ticker.

**POST** `/api/agents/research`
```json
{
  "ticker": "AAPL",
  "query": "What are the key risks?" // optional
}
```

**GET** `/api/agents/research/{ticker}?query=key%20risks`
- Query params: `query` (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    // Research analysis results
  }
}
```

#### 3. **Sentiment Agent**
Analyzes sentiment from a list of texts.

**POST** `/api/agents/sentiment`
```json
{
  "texts": [
    "Apple stock is performing well",
    "Market shows positive trends"
  ],
  "sources": ["news", "twitter"] // optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    // Sentiment analysis results
  }
}
```

#### 4. **Ticker Sentiment Agent**
Analyzes sentiment from news articles for a specific ticker.

**POST** `/api/agents/sentiment/ticker`
```json
{
  "ticker": "AAPL",
  "articles": [
    {
      "title": "Apple announces new product",
      "description": "Apple stock rises..."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    // Sentiment analysis results
  }
}
```

#### 5. **Portfolio Agent**
Analyzes multiple stocks in a portfolio.

**POST** `/api/agents/portfolio`
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "watchlist_id": 123 // optional
}
```

**GET** `/api/agents/portfolio/analyze?tickers=AAPL,MSFT,GOOGL&watchlist_id=123`
- Query params: `tickers` (comma-separated, required), `watchlist_id` (optional)
- Maximum 20 tickers allowed

**Response:**
```json
{
  "success": true,
  "data": {
    // Portfolio analysis results
  }
}
```

#### 6. **LLM Handler**
Direct access to LLM models (Gemini-Pro or Groq Llama3).

**POST** `/api/agents/llm`
```json
{
  "model": "gemini-pro", // or "groq-llama3"
  "prompt": "Analyze the current market trends"
}
```

**Response:**
```json
{
  "success": true,
  "model": "gemini-pro",
  "response": "LLM response text..."
}
```

#### 7. **Health Check**
Check agent availability status.

**GET** `/api/agents/health`

**Response:**
```json
{
  "status": "healthy",
  "agents": {
    "research": "available",
    "sentiment": "available",
    "portfolio": "available",
    "llm": "available"
  }
}
```

### 📊 Stock Routes (`/api`)

- **GET** `/api/stock-data?symbol=AAPL&period=3mo` - Fetch stock data
- **GET** `/api/news?symbol=AAPL` - Get news articles for a ticker

### 📰 News Routes (`/api`)

- **GET** `/api/news/{symbol}?limit=10` - Get news with sentiment analysis

### 📋 Watchlist Routes (`/api`)

- **GET** `/api/watchlists` - Get all watchlists
- **POST** `/api/watchlists` - Create a watchlist
- **GET** `/api/watchlists/{id}` - Get specific watchlist
- **PUT** `/api/watchlists/{id}` - Update watchlist
- **DELETE** `/api/watchlists/{id}` - Delete watchlist

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangGraph** - AI agent workflow orchestration
- **LangChain** - LLM integration framework
- **MongoDB** (Motor) - Database
- **Redis** - Caching layer
- **yfinance** - Stock data fetching
- **VADER Sentiment** - Sentiment analysis
- **Groq** - Fast LLM inference
- **Google Gemini** - Advanced LLM capabilities

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client

---

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔑 Required API Keys

1. **NEWS_API_KEY** - For fetching financial news (required for news features)
2. **GROQ_API_KEY** - For Groq Llama3 LLM (required for AI agents)
3. **GEMINI_API_KEY** - For Google Gemini LLM (required for AI agents)

**Note:** At least one LLM API key (GROQ or GEMINI) is required for AI agent functionality.

---

## 📁 Project Structure

```
Financial-Research-Agent/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── graphs/          # LangGraph workflows
│   │   │   │   ├── unified_agent_graph.py
│   │   │   │   ├── research_graph.py
│   │   │   │   ├── sentiment_graph.py
│   │   │   │   └── portfolio_graph.py
│   │   │   ├── nodes/           # Agent nodes
│   │   │   │   ├── llm_node.py
│   │   │   │   ├── sentiment_node.py
│   │   │   │   └── ...
│   │   │   └── state/           # Agent state management
│   │   ├── routes/              # API routes
│   │   │   ├── agent_routes.py  # AI agent endpoints
│   │   │   ├── stock_routes.py
│   │   │   ├── news_routes.py
│   │   │   └── watchlist_routes.py
│   │   ├── services/            # Business logic
│   │   ├── models/              # Database models
│   │   └── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   └── s/                       # React frontend
└── README.md
```

---

## 🧪 Testing

Run tests from the backend directory:
```bash
cd backend
pytest app/tests/
```

---

## ☁️ Deploy (Vercel frontend + hosted backend)

Vercel hosts the **React frontend only**. The FastAPI backend (agents, MongoDB, Redis, LLM calls) must run on a long-lived host such as **Render**, **Railway**, or **Fly.io** — serverless timeouts are too short for the agent pipelines.

### 1. Deploy the backend (Render example)

1. Push this repo to GitHub.
2. Create a new **Web Service** on [Render](https://render.com) (or use the included `render.yaml`).
3. Set root directory to `backend`, build: `pip install -r requirements.txt`, start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Add env vars from `backend/.env.example` (`NEWS_API_KEY`, `GROQ_API_KEY` / `GEMINI_API_KEY`, `MONGO_URI`, etc.).
5. Copy the public URL, e.g. `https://financial-research-api.onrender.com`.

### 2. Deploy the frontend on Vercel

1. Import the GitHub repo in [Vercel](https://vercel.com).
2. **Root Directory**: leave repo root (uses root `vercel.json`) **or** set to `frontend/s`.
3. Add Environment Variable:
   - `VITE_API_BASE_URL` = `https://YOUR-BACKEND-URL/api`  
     (no trailing slash)
4. Deploy. Open routes like `/dashboard` should work via SPA rewrites.

Local frontend override: copy `frontend/s/.env.example` → `frontend/s/.env`.

---

## 📄 License

This project is part of the 8-Week Financial Research AI Agent Development Program.