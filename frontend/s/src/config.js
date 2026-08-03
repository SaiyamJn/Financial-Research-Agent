/**
 * Shared API base URL.
 * Set VITE_API_BASE_URL in Vercel (e.g. https://your-backend.onrender.com/api)
 * Falls back to local FastAPI during development.
 */
const raw = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const API_BASE = raw.replace(/\/$/, "");
export const AGENTS_API_BASE = `${API_BASE}/agents`;
