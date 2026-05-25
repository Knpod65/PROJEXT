# FACULTY_WEB_PORTAL_PIVOT_SOURCE_REVIEW.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL DEPLOYMENT + SYSTEM COMPLETION PASS  
**Pre-flight**: Confirmed real root C:/Users/DELL/Desktop/PROJEXT/opt/ems_system, main at 296b98e (post-demo + Laravel dispatch package), clean tree, no WIP merged.

## 1. Documents Read (Key Sources for Pivot)

- EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md (updated to 98/100 Demo, still uses "Controlled Faculty LAN Pilot")
- EMS_100_PERCENT_MASTER_SCORECARD.md (has "Laravel / Faculty LAN" column)
- LARAVEL_FACULTY_LAN_100_PERCENT_READINESS_SCORE.md (title and content heavily LAN-oriented)
- PILOT_100_PERCENT_READINESS_SCORE.md (defines "Controlled Faculty LAN Pilot 100%")
- PRODUCTION_100_PERCENT_READINESS_SCORE.md (references Faculty LAN env)
- DATABASE_POSTGRES_100_PERCENT_READINESS_SCORE.md (Faculty LAN DB integration)
- SECURITY_PDPA_100_PERCENT_READINESS_SCORE.md (Faculty LAN env)
- BACKEND_100_PERCENT_READINESS_SCORE.md (Faculty LAN references)
- PERFORMANCE_SCALABILITY_100_PERCENT_READINESS_SCORE.md (Faculty LAN PostgreSQL load test)
- POST_DEMO_SOURCE_REVIEW.md, POST_DEMO_48_HOUR_ACTION_TRACKER.md, POST_DEMO_NEXT_PHASE_OPTIONS.md, POST_DEMO_DECISION_MATRIX.md, POST_DEMO_DECISION_CAPTURE.md (mix of LAN and contract language)
- DEMO_DAY_RUNBOOK.md, DEMO_LIMITATIONS_AND_DISCLOSURE.md, EMS_STAKEHOLDER_DEMO_ONE_PAGER.md, STAKEHOLDER_DEMO_SCRIPT.md, FINAL_DEMO_READINESS_CERTIFICATE.md, DEMO_GO_NO_GO_REPORT.md (many "Faculty LAN" mentions)
- LARAVEL_AUTH_CONTRACT_QUESTIONS.md, LARAVEL_AUTH_CONTRACT_CLOSURE_TRACKER.md, LARAVEL_IT_DISPATCH_PACKET_INDEX.md, LARAVEL_IT_REQUEST_MESSAGE_READY_TO_SEND.md (still use "Faculty LAN" in context)
- FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md, POLSCI_OAUTH_FLOW_ANALYSIS.md, HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md, AUTH_BRIDGE_IMPLEMENTATION_GATE.md, EMS_AUTH_BRIDGE_DESIGN.md (LAN Server language)
- PILOT_ROUTE_AND_AUTH_MAPPING.md (Faculty LAN Server, Nginx on LAN)
- LARAVEL_OWNER_REQUEST_MEMO_TH_EN.md (Faculty LAN deployment)
- Various design handoff docs (CLAUDE_DESIGN_*, EMS_DESIGN_*) referencing LAN deployment and routes
- UAT_GO_NO_GO_REPORT.md, PILOT_BLOCKER_DASHBOARD.md, DEMO_AUTH_AND_PRINT_SHOP_SCOPE.md (LAN target)

## 2. Documents That Still Mention Faculty LAN (Need Reframing)

Almost all operational, deployment, architecture, and design docs use "Faculty LAN", "LAN Server", "Faculty LAN Pilot", "LAN-only" as the target environment.

High-impact files requiring updates in this pass:
- All readiness scorecards and summaries (Executive, Master, Pilot, Production, Laravel score, DB, Security, etc.)
- Post-demo decision and tracker docs
- Deployment specs (FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC, PILOT_ROUTE_AND_AUTH_MAPPING, etc.)
- Auth bridge design and gate docs
- Demo limitation and stakeholder materials
- Design handoff sources

## 3. Documents That Remain Valid (Core Content)

- Standalone demo evidence (98/100 interactive GUI smoke)
- Current auth model (standalone JWT + cookie, fallback)
- Print shop external lane isolation
- PostgreSQL pooling and fallback hardening
- Service/repository layering, RBAC, i18n, etc.
- Contract questions themselves (the questions are still valid; only the "LAN Server" framing needs update to "Faculty Web Portal / Faculty Web Deployment Target")

## 4. Documents That Are Outdated or Need Historical Note

- Any pre-2026-05-25 "Faculty LAN Server" as the only target
- Old PILOT_ROUTE_AND_AUTH_MAPPING.md (assumes LAN Server topology)
- Some design sources that draft LAN-specific routes

These should be kept as historical references with a note that the target has pivoted to Faculty Web Portal integration.

## 5. Risks Created by the Target Change (LAN → Faculty Web Portal)

- Mount path / base path assumptions in frontend (Vite base, router, assets) must now support nesting under faculty web (e.g. /ems)
- API proxy path ( /ems-api or similar) becomes critical
- Cookie domain / Secure / SameSite policy must align with faculty web domain (portal.mis.pol.cmu.ac.th or similar)
- Reverse proxy / Nginx config on the faculty web side (not "LAN server")
- OAuth ServiceUrl / callback now tied to faculty web's existing /oauth/callback pattern
- Potential same-origin or CORS considerations when EMS frontend lives under Laravel-served paths
- Print shop external users must not be forced into CMU identity just because deployment target changed
- PostgreSQL target may still be shared or dedicated, but now under faculty web hosting governance rather than pure LAN

## 6. What Is Still Blocked by IT/Laravel Answers

- Exact ServiceUrl / callback contract
- session("USS") and cmu_at structure + lifecycle
- CMU email field mapping
- Whether EMS can be mounted under /ems or must use separate subdomain
- Whether Laravel remains the central OAuth handler or EMS can receive direct callbacks
- Print shop external account model in the faculty web ecosystem
- PostgreSQL target, ownership, backup owner under faculty web hosting
- Reverse proxy / header forwarding rules (X-Forwarded-*, root_path support)

The contract questions in LARAVEL_AUTH_CONTRACT_QUESTIONS.md remain the authoritative list; they just need minor reframing from "Faculty LAN" to "Faculty Web Portal deployment".

## 7. Recommended Immediate Actions in This Pass

1. Create terminology audit (PHASE 2)
2. Define new deployment architecture options for Faculty Web Portal (PHASE 3)
3. Audit frontend for base-path / API-base compatibility (PHASE 4) — implement safe Vite/env support if missing
4. Audit backend for proxy/CORS/root_path compatibility (PHASE 5)
5. Create route/API mapping for web portal (PHASE 6)
6. Update all auth boundary and contract docs (PHASE 7)
7. Create dedicated PostgreSQL and print-shop plans for web portal (PHASES 8-9)
8. Reframe readiness scores (PHASE 10)
9. Produce deployment checklist and roadmap (PHASES 12-13)
10. Safe config updates only (PHASE 11)
11. Full validation + explicit-path commits (PHASES 14-15)

**No auth bridge code. No production claims. Preserve standalone demo 98/100.**

---
*This pivot is a strategic re-orientation based on the provided Faculty web callback patterns and ecosystem. All previous standalone demo validation remains valid and valuable.*
