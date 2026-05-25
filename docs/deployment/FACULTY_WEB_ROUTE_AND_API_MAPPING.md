# FACULTY_WEB_ROUTE_AND_API_MAPPING.md

**Date**: 2026-05-25

## Proposed Faculty Web Portal Route Structure (Example — TBD by IT)

Faculty web (Laravel) primary domain: portal.mis.pol.cmu.ac.th (or equivalent)

### Frontend Routes (React app mounted under faculty web)
- /ems
- /ems/admin-intelligence-dashboard
- /ems/workload-duty-analytics (and role variants)
- /ems/schedule
- /ems/submissions
- /ems/operational-health
- /ems/audit-explorer
- /ems/governance
- /ems/print-queue
- /ems/my-workload (teacher)
- /ems/myexam (student/teacher)
- etc.

### API Routes (proxied to EMS backend)
Recommended prefix: /ems-api (to avoid collision with Laravel /api)

- /ems-api/health
- /ems-api/auth/login (standalone fallback)
- /ems-api/auth/refresh
- /ems-api/auth/logout
- /ems-api/dashboard/*
- /ems-api/schedule/*
- /ems-api/submissions/*
- /ems-api/workload/*
- /ems-api/audit/*
- /ems-api/print/*
- /ems-api/import/*
- /ems-api/export/*
- /ems-api/governance/*
- etc.

Alternative (if IT prefers): Keep /api under a sub-path or use full origin for EMS API.

## OAuth / Callback Considerations

Current faculty pattern:
- Login entry: https://account.pol.cmu.ac.th/oauth/login?ServiceUrl=...
- Callback example: https://portal.mis.pol.cmu.ac.th/oauth/callback

For EMS web portal integration, possible models (still require contract answers):
- Laravel remains the central OAuth handler and issues a short-lived token or session to EMS.
- Or direct ServiceUrl redirect to an EMS callback endpoint (then EMS validates and creates local session).
- Print shop external users bypass CMU OAuth entirely.

Exact model is blocked pending answers to the updated contract questions (see PHASE 7 updates).

## Cookie Domain / Path Notes

- If frontend is under portal.mis.pol.cmu.ac.th/ems, auth cookies can be scoped to / or /ems.
- Secure + SameSite=Strict/Lax required.
- Must be verified with actual faculty web reverse proxy behavior.

---
*This is a proposed mapping for planning. Final paths require confirmation from faculty web / IT team.*
