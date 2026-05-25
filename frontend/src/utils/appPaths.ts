/**
 * Centralized helpers for VITE_APP_BASE_PATH-aware path construction.
 *
 * Purpose (Faculty Web Portal subpath support):
 * - Default behavior (no env): everything stays at root "/" + local "/api"
 * - When VITE_APP_BASE_PATH=/ems is set at build time:
 *     withAppBasePath("/dashboard") → "/ems/dashboard"
 * - Avoids double slashes and trailing-slash issues.
 *
 * Rules:
 * - Prefer React Router <Link>, <NavLink>, useNavigate() for normal SPA navigation (they already respect BrowserRouter basename).
 * - Use these helpers ONLY for the rare cases that require a full page load / window.location or raw href (error recovery links, certain export openers, post-auth resets).
 * - Never hardcode "/ems" or any specific subpath in source.
 *
 * Local dev / standalone demo: no env vars → identical behavior to before this pass.
 */

const RAW_BASE = import.meta.env.VITE_APP_BASE_PATH || "/";

// Normalize: ensure leading slash, remove trailing slash (except for root "/")
function normalizeBase(base: string): string {
  let b = base.trim();
  if (!b.startsWith("/")) b = "/" + b;
  if (b.length > 1 && b.endsWith("/")) b = b.slice(0, -1);
  return b;
}

const APP_BASE = normalizeBase(RAW_BASE);

/**
 * Returns the current application base path (e.g. "/" or "/ems").
 * Use for rare cases where you must know the prefix.
 */
export function getAppBasePath(): string {
  return APP_BASE;
}

/**
 * Prefixes an internal application path with the configured base path.
 * - withAppBasePath("/login") → "/login" (default) or "/ems/login"
 * - withAppBasePath("login") → same (leading slash added)
 * - withAppBasePath("/") → base (or "/ems")
 */
export function withAppBasePath(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (APP_BASE === "/") return p;
  // Avoid double slash when p === "/"
  if (p === "/") return APP_BASE;
  return `${APP_BASE}${p}`;
}

/**
 * Optional: re-export API base resolution for consistency in components that need it
 * (the authoritative implementation lives in @/services/api — this is a convenience mirror).
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
