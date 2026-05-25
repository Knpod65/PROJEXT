# FACULTY_WEB_SUBPATH_SMOKE_SOURCE_REVIEW.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL SUBPATH BUILD + ROUTE COMPATIBILITY SMOKE PASS  
**Pre-flight**: Confirmed real root, main at 635e5f8 (includes safe VITE_APP_BASE_PATH / VITE_API_BASE_URL support), clean tree.

## 1. Documents Read

- FACULTY_WEB_PORTAL_PIVOT_SOURCE_REVIEW.md (full pivot from LAN to Faculty Web Portal, 38/100 integration score)
- FRONTEND_FACULTY_WEB_COMPATIBILITY_AUDIT.md (Vite base missing in older audit; API_BASE hardcoded; recommends env vars)
- BACKEND_FACULTY_WEB_COMPATIBILITY_AUDIT.md (proxy/root_path, CORS, cookie notes)
- FACULTY_WEB_PORTAL_100_PERCENT_READINESS_SCORE.md (38/100)
- FACULTY_WEB_PORTAL_DEPLOYMENT_ARCHITECTURE.md (Options A/B/C/D; recommends A or B)
- FACULTY_WEB_ROUTE_AND_API_MAPPING.md (proposed /ems + /ems-api)
- FACULTY_WEB_PORTAL_DEPLOYMENT_CHECKLIST.md and IMPLEMENTATION_ROADMAP.md
- FACULTY_WEB_POSTGRESQL_DEPLOYMENT_PLAN.md and PRINT_SHOP_ACCESS_PLAN.md
- FINAL_DEMO_READINESS_CERTIFICATE.md (98/100 standalone)
- EMS_100_PERCENT_MASTER_SCORECARD.md and EXECUTIVE_SUMMARY.md (Demo 98, Web Portal Integration ~38, Pilot 42, Production 28)

## 2. Current Portal Assumptions

- Faculty Web Portal target (portal.mis.pol.cmu.ac.th ecosystem) instead of pure LAN server.
- EMS likely mounted under subpath like /ems with API under /ems-api (or similar) via reverse proxy.
- Auth still pending full contract (Laravel central handler preferred).
- Print shop remains separate external lane.

## 3. Current Base Path / API Path Support (from previous pass)

- Vite: supports VITE_APP_BASE_PATH (build base + dev)
- BrowserRouter: supports basename from VITE_APP_BASE_PATH
- API service: supports VITE_API_BASE_URL (defaults to /api)
- Local dev / root deployment remains default and unchanged.

## 4. Known Unknowns (Still Require IT Answers)

- Exact mount path (e.g. /ems vs /ems-app)
- Exact API proxy prefix
- Reverse proxy rewrite vs pass-through behavior
- OAuth ServiceUrl / callback final model
- Cookie domain / SameSite policy under faculty web domain

## 5. What This Pass Can Validate

- Root/default build remains working and identical.
- Subpath build with VITE_APP_BASE_PATH=/ems + VITE_API_BASE_URL=/ems-api produces correct asset paths.
- No hard-coded localhost or root assumptions break the build.
- Route navigation and API calls are configurable.
- SPA fallback requirements for real reverse proxy.

## 6. What This Pass Cannot Fully Validate

- Actual faculty web reverse proxy (Nginx/Laravel) behavior.
- Live OAuth under subpath.
- Cookie / session issues in real portal domain.
- Performance under faculty hosting.

This pass focuses on making the frontend build and route compatibility **provably configurable** for the documented web portal target.

**Next**: PHASE 2 — root build baseline.
