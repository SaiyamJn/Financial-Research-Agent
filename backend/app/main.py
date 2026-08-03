# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .services.stocks import fetch_stock_data
from .services.news import get_news_for_ticker   # ✅ Correct import
from .services.sentiment import analyze_sentiment_batch
from .routes import stock_routes, news_routes, watchlist_routes, agent_routes
from .db import init_db
from .utils.cache import close_redis

import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

load_dotenv()

app = FastAPI(title="Financial Research AI API", version="1.0")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ⭐ Added LLM API keys (Gemini + Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# ---------------- STOCK ROUTE ----------------
@app.get("/api/stock-data")
async def get_stock_data(symbol: str, period: str = "3mo"):
    # ✅ Add caching for faster loading (with error handling)
    cache_available = False
    cache_key = f"stock_data:{symbol}:{period}"
    
    try:
        from .utils.cache import get_cached, set_cached
        cache_available = True
        
        # Check cache first (ignore cache errors)
        try:
            cached = await get_cached(cache_key)
            if cached:
                return cached
        except Exception as cache_err:
            # Cache failed, continue without cache
            print(f"⚠️ Cache read error (continuing): {cache_err}")
            cache_available = False
    except ImportError:
        # Cache not available, continue without it
        cache_available = False
    
    # Fetch data
    data, error = await fetch_stock_data(symbol, period)
    if error:
        return {"success": False, "error": error}

    result = {
        "success": True,
        "data": data["data"],
        "metrics": data.get("metrics", {})
    }
    
    # Try to cache (ignore errors)
    if cache_available:
        try:
            await set_cached(cache_key, result, expire=300)
        except Exception:
            pass  # Cache failed, but we still return the data
    
    return result


# ---------------- NEWS ROUTE ----------------
@app.get("/api/news")
async def get_news(symbol: str):
    # ✅ Add caching for faster loading (with error handling)
    cache_key = None
    try:
        from .utils.cache import get_cached, set_cached
        cache_key = f"news_sentiment:{symbol}"
        
        # Check cache first (ignore cache errors)
        try:
            cached = await get_cached(cache_key)
            if cached:
                return cached
        except Exception as cache_err:
            # Cache failed, continue without cache
            print(f"⚠️ Cache read error (continuing): {cache_err}")
    except ImportError:
        # Cache not available, continue without it
        pass
    
    # ✅ Use correct async news fetcher
    articles = await get_news_for_ticker(symbol)

    # If empty or failed
    if not articles:
        return {
            "success": True,
            "articles": [],
            "sentiment_summary": {
                "avg_score": 0,
                "positive_count": 0,
                "neutral_count": 0,
                "negative_count": 0,
                "overall": "Neutral",
            },
        }

    analyzed = analyze_sentiment_batch(articles)

    if not analyzed:
        return {
            "success": True,
            "articles": [],
            "sentiment_summary": {
                "avg_score": 0,
                "positive_count": 0,
                "neutral_count": 0,
                "negative_count": 0,
                "overall": "Neutral",
            },
        }

    scores = [a.get("score", 0) for a in analyzed]

    avg = sum(scores) / len(scores)
    positive = len([s for s in scores if s >= 0.05])
    neutral = len([s for s in scores if -0.05 < s < 0.05])
    negative = len([s for s in scores if s <= -0.05])
    overall = "Positive" if avg >= 0.05 else "Negative" if avg <= -0.05 else "Neutral"

    result = {
        "success": True,
        "articles": analyzed,
        "sentiment_summary": {
            "avg_score": round(avg, 3),
            "positive_count": positive,
            "neutral_count": neutral,
            "negative_count": negative,
            "overall": overall,
        },
    }
    
    # Try to cache (ignore errors)
    if cache_key:
        try:
            await set_cached(cache_key, result, expire=120)
        except Exception:
            pass  # Cache failed, but we still return the data
    
    return result


# ---------------- BACKEND ROUTES REGISTRATION ----------------
app.include_router(stock_routes.router, prefix="/api")
app.include_router(news_routes.router, prefix="/api")
app.include_router(watchlist_routes.router, prefix="/api")
app.include_router(agent_routes.router, prefix="/api")  # AI Agent routes


# ---------------- STARTUP & SHUTDOWN ---------------- 
@app.on_event("startup")
async def startup_event():
    db_instance = await init_db()
    if db_instance is not None:
        print("✅ MongoDB connection initialized")
    else:
        print("⚠️ MongoDB not available - app running without database features")


@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()
    print("🧹 Redis connection closed")
