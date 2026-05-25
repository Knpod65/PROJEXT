# FRONTEND_FACULTY_WEB_COMPATIBILITY_AUDIT.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL DEPLOYMENT + SYSTEM COMPLETION PASS

## Files Inspected

- frontend/vite.config.ts (no `base` defined)
- frontend/src/services/api.ts (hardcoded `const API_BASE = "/api"`)
- frontend/src/App.tsx (BrowserRouter at root, lazy routes)
- frontend/src/main.tsx (standard React root render)
- frontend/src/config/navigation.ts (path definitions are relative)
- frontend/src/store/auth.store.tsx (redirects and login flows)
- frontend/src/components/layout/ProtectedRoute.tsx and utils/roles.ts (route guards)

## Key Findings

### Positive (Already Compatible or Low Risk)
- Most routes and navigation use relative paths.
- Lazy loading and React Router v6 are flexible.
- Asset references in built output are usually relative when Vite is configured correctly.
- i18n, state, and most components do not hardcode origin.

### Risks / Gaps for Faculty Web Portal

1. **Vite base path**
   - No `base` option in vite.config.ts.
   - If EMS is mounted under `/ems`, all asset URLs and router base must be `/ems/`.
   - Current local dev (root) would break if we hardcode without env support.

2. **API base URL**
   - Hardcoded `"/api"` in api.ts.
   - For web portal, this will likely become `/ems-api` or a full origin behind the faculty reverse proxy.
   - No environment variable or config abstraction for API base (only local proxy in vite dev server).

3. **BrowserRouter root assumption**
   - `<BrowserRouter>` at root in App.tsx.
   - For sub-path deployment, needs `<BrowserRouter basename={import.meta.env.VITE_APP_BASE_PATH || "/"}>` (or equivalent).

4. **Login / logout / redirect flows**
   - Some redirects and post-login navigation assume root (`/dashboard`, `/login`, etc.).
   - Must preserve base path when constructing URLs.

5. **Language toggle and other client-side navigation**
   - Generally safe, but any hardcoded `window.location` or absolute links need review.

## Recommended Safe Fixes (Implement in This Pass if Time Allows)

- Add support for `VITE_APP_BASE_PATH` in vite.config.ts (for build `base` and dev server).
- Make API base configurable via `VITE_API_BASE_URL` (default "/api" for local dev).
- Update api.ts to read from env (non-breaking for current root deployment).
- Update App.tsx / main.tsx to support `basename` from env (default "/").
- Add clear comments and .env.example entries.
- Ensure `npm run dev` and `npm run build` continue to work exactly as before when no env vars are set (root deployment).

These changes are low-risk, reversible, and required for any non-root web portal deployment.

## Blocked Items (Require IT Answers)

- Exact base path (e.g. /ems vs /ems-app)
- Exact API proxy prefix (e.g. /ems-api)
- Whether the faculty web reverse proxy will rewrite paths or pass them through
- Cookie / origin behavior when frontend lives under faculty web domain

## Test Plan After Changes

- Local dev (no env vars) → still works at http://localhost:3000
- Build with `VITE_APP_BASE_PATH=/ems VITE_API_BASE_URL=/ems-api` → produces correct asset paths and API calls
- Manual verification that login → dashboard flow works under simulated base path (can use Vite preview with base)

---
*Frontend is mostly ready; the gaps are standard sub-path deployment concerns that have safe, well-known solutions.*
