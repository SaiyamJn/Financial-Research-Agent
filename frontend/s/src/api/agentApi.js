// src/api/agentApi.js
import { AGENTS_API_BASE as API_BASE_URL } from "../config";

// --------- RESEARCH AGENT ----------
export async function runResearchAgent(ticker, query = null) {
  const res = await fetch(`${API_BASE_URL}/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker, query }),
  });

  if (!res.ok) throw new Error(`Research agent error: ${res.status}`);
  return await res.json();
}

// --------- SENTIMENT AGENT ----------
export async function runSentimentAgent(texts, sources = null) {
  const res = await fetch(`${API_BASE_URL}/sentiment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texts, sources }),
  });

  if (!res.ok) throw new Error(`Sentiment agent error: ${res.status}`);
  return await res.json();
}

// --------- PORTFOLIO AGENT ----------
export async function runPortfolioAgent(tickers, watchlistId = null) {
  const res = await fetch(`${API_BASE_URL}/portfolio`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tickers, watchlist_id: watchlistId }),
  });

  if (!res.ok) throw new Error(`Portfolio agent error: ${res.status}`);
  return await res.json();
}

// --------- UNIFIED AGENT ----------
// --------- UNIFIED AGENT ----------
export async function runUnifiedAgent(ticker, query) {
  try {
    const res = await fetch(`${API_BASE_URL}/unified`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, description: query }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("❌ Backend error:", errorText);
      throw new Error(`Unified agent error: ${res.status}`);
    }

    return await res.json(); // ✅ RETURN the response!
  } catch (error) {
    console.error("❌ Fetch error:", error);
    throw error;
  }
}
// --------- GENERIC LLM CALL ----------
export async function runLLM(model, prompt) {
  const res = await fetch(`${API_BASE_URL}/llm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      prompt,
    }),
  });

  if (!res.ok) throw new Error(`LLM API error: ${res.status}`);
  return await res.json(); // { success, model, response }
}

// --------- GEMINI PRO (via backend) ----------
export async function runGeminiLLM(prompt) {
  return await runLLM("gemini-pro", prompt);
}

// --------- GROQ LLM (e.g., Mixtral, Llama3) ----------
export async function runGroqLLM(prompt) {
  return await runLLM("groq-llama3", prompt);
}