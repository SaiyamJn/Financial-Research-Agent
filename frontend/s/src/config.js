/**
 * Shared API base URL.
 *
 * Prefer same-origin `/api` so:
 * - local: Vite proxies /api → localhost:8000
 * - Vercel: rewrites /api → Render backend
 *
 * Optional override: VITE_API_BASE_URL=https://your-backend.onrender.com/api
 */
function resolveApiBase() {
  const raw = (import.meta.env.VITE_API_BASE_URL || "").trim();
  if (!raw) {
    return "/api";
  }
  let base = raw.replace(/\/$/, "");
  if (!base.endsWith("/api")) {
    base = `${base}/api`;
  }
  return base;
}

export const API_BASE = resolveApiBase();
export const AGENTS_API_BASE = `${API_BASE}/agents`;
