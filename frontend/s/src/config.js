/**
 * Shared API base URL.
 * Set VITE_API_BASE_URL in Vercel to your Render URL + /api
 * e.g. https://financial-research-agent-wiqb.onrender.com/api
 * Falls back to local FastAPI during development.
 */
function resolveApiBase() {
  let base = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api").replace(
    /\/$/,
    ""
  );
  // If someone sets only the host, append /api so routes match FastAPI
  if (!base.endsWith("/api")) {
    base = `${base}/api`;
  }
  return base;
}

export const API_BASE = resolveApiBase();
export const AGENTS_API_BASE = `${API_BASE}/agents`;
