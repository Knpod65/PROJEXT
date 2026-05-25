# FACULTY_WEB_PORTAL_DEPLOYMENT_ARCHITECTURE.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL DEPLOYMENT + SYSTEM COMPLETION PASS

## Target Environment Shift

EMS is no longer planned as a pure "Faculty LAN Server" application.

New target: Integrate or deploy EMS as part of (or alongside) the existing **Faculty Web Portal** (PHP/Laravel-based faculty website at portal.mis.pol.cmu.ac.th and related domains).

Key known patterns from faculty web:
- Central OAuth entry: https://account.pol.cmu.ac.th/oauth/login?ServiceUrl=...
- Existing callback: https://portal.mis.pol.cmu.ac.th/oauth/callback
- CMU email as primary identity for authenticated users
- PostgreSQL as the central database technology
- Print shop / external partner users (non-CMU) must remain a separate lane

## Deployment Options for Faculty Web Portal

### Option A — EMS Frontend Served Under Laravel Route (Recommended for tight integration)
- Faculty web (Laravel) serves the built React assets at paths such as:
  - /ems
  - /ems/admin-intelligence-dashboard
  - /ems/teacher (etc.)
- Laravel acts as the shell / auth gateway for CMU users.
- EMS backend (FastAPI) runs as a separate service, exposed via internal reverse proxy (e.g. /ems-api/*).
- Pros: Users stay inside the familiar faculty web experience; central auth possible at Laravel layer.
- Cons: Requires base-path support in frontend, API proxy config, cookie domain handling.

### Option B — EMS as Separate Sub-Application Behind Reverse Proxy
- portal.mis.pol.cmu.ac.th/ems → React frontend
- portal.mis.pol.cmu.ac.th/ems-api → FastAPI backend
- Or dedicated subdomain ems.pol.cmu.ac.th (requires DNS + certificate coordination)
- Pros: Cleaner separation of concerns, easier independent lifecycle for EMS.
- Cons: Cookie / session domain and SameSite issues must be solved; OAuth ServiceUrl routing must be decided.

### Option C — EMS Wrapped as Laravel Module / Blade Shell
- Laravel provides a thin wrapper that embeds or links to the EMS React app.
- Pros: Easiest auth handoff for CMU users.
- Cons: Tighter coupling, more complex frontend build pipeline inside Laravel asset system.

### Option D — Separate Subdomain (ems.pol.cmu.ac.th)
- Clean ownership boundary.
- Pros: Simplest deployment for EMS team.
- Cons: Requires faculty web to approve and configure OAuth redirect + any cross-origin needs; may feel less "integrated".

## Recommendation

Prefer **Option A** or **Option B** depending on IT's preference for integration depth vs operational separation.

Do **not** choose or implement until:
- Exact mount path (e.g. /ems) is confirmed by faculty web team.
- API proxy prefix is decided.
- OAuth ServiceUrl / callback strategy is contractually verified (see updated auth questions).

## High-Level Component View (Faculty Web Portal Context)

Faculty Web (Laravel/PHP):
- Central login / OAuth handling for CMU users
- Possible thin shell for /ems routes (Option A)
- Reverse proxy rules for /ems-api (or equivalent)

EMS Frontend (React, built with Vite):
- Must support configurable base path (e.g. /ems)
- Must use configurable API base URL (e.g. /ems-api or full origin)
- Routes and asset references must be relative to base path

EMS Backend (FastAPI + PostgreSQL):
- Runs as independent service (Uvicorn/Gunicorn)
- Exposed only via trusted reverse proxy from faculty web tier
- Must respect X-Forwarded-* headers for correct URL generation and cookies
- PostgreSQL connection via faculty web hosting environment (dedicated EMS DB or schema recommended)

External Print Shop Lane:
- Must remain separate from CMU OAuth flow
- Options: Laravel external partner accounts, EMS-managed external accounts, or time-limited signed links (see separate print shop plan)

## Cookie / Session / Proxy Considerations (Critical)

- Secure + SameSite cookies required for production web portal.
- If EMS frontend lives under faculty web domain, cookies can be shared or isolated depending on path.
- Reverse proxy must forward Host, X-Forwarded-Proto, X-Forwarded-For, etc.
- FastAPI must be configured with root_path or trusted proxy middleware when behind the faculty web reverse proxy.

These details are still pending IT confirmation (see updated contract questions).

## When to Revisit This Document

- After receiving answers to the reframed Laravel/Faculty Web contract questions.
- When faculty web team provides concrete mount path, proxy rules, and OAuth redirect policy.
- Before any production or staging deployment under the web portal.

---
*This document replaces previous "Faculty LAN Server" deployment thinking. All prior standalone demo validation (98/100) remains fully valid and is the current baseline.*
