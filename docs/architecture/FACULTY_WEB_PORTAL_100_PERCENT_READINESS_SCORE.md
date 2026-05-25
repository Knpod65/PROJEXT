# FACULTY_WEB_PORTAL_100_PERCENT_READINESS_SCORE.md

**Date**: 2026-05-25  
**Pass**: EMS FACULTY WEB PORTAL DEPLOYMENT + SYSTEM COMPLETION PASS

## Faculty Web Portal Integration Readiness (0–100)

This score replaces the previous pure "Faculty LAN" framing.

| Dimension | Score | Evidence / Status | Why Not 100 | Demo Impact | Web Portal Pilot Impact | Production Impact |
|-----------|-------|-------------------|-------------|-------------|-------------------------|-------------------|
| 1. Route / Mount Path Readiness | 30 | Proposed mapping exists (see FACULTY_WEB_ROUTE_AND_API_MAPPING.md). No confirmed path from IT. | Exact /ems (or other) mount path TBD | None (standalone) | Critical | Critical |
| 2. OAuth / Callback Contract Readiness | 20 | Questions updated for web portal. Zero verified answers. | session("USS"), cmu_at, ServiceUrl behavior unknown | None | 0% | 0% |
| 3. Laravel Session / Identity Readiness | 15 | Analysis documents exist. No verified payload. | How EMS receives verified CMU identity still open | None | 0% | 0% |
| 4. Frontend Base Path + API Proxy Readiness | 85 | Audit complete. Safe Vite + env support implemented (635e5f8). Root + /ems subpath builds validated in this pass. | Remaining direct /api and window.location calls documented | Low | High | High |
| 5. Backend Proxy / CORS / Headers Readiness | 70 | Audit complete. Good PostgreSQL + startup hardening. Reverse proxy header support and root_path need documentation + config. | Not yet proven behind actual faculty web proxy | Low | High | High |
| 6. PostgreSQL Web Hosting Readiness | 55 | Dedicated EMS DB/schema recommended. Plan exists. No confirmed target or ownership from faculty web team. | Backup/restore evidence and connection details pending | None | Critical | Critical |
| 7. Print Shop External Lane Readiness (Web Context) | 60 | Solid standalone lane + hybrid model documented. Web portal specific access model (Laravel external vs standalone) still open. | Final model TBD with IT | Partial (current demo works) | Medium-High | High |
| 8. Deployment Evidence & Checklist Readiness | 25 | New checklist and roadmap created in this pass. No real faculty web hosting evidence yet. | Actual deployment has not occurred | None | High | Critical |
| 9. Auth Bridge Design Readiness (Web Portal) | 40 | Design updated for web portal target. Gate still firmly in place. | Cannot implement without verified contract | None | 0% until answers | 0% |
| 10. Overall Faculty Web Portal Integration Readiness | **38 / 100** | Significant analysis and planning now reframed for web portal. Core blocker remains unverified Laravel/Faculty Web auth contract. | Same fundamental unknowns as before, now in web portal context | N/A | Blocked | Blocked |

**Overall Faculty Web Portal Integration Score: 38 / 100**

## Comparison to Previous LAN Framing

- Previous "Laravel / Faculty LAN" score was 25/100.
- Reframing to web portal raises the planning maturity slightly (better architecture options, clearer proxy thinking) but does not change the fundamental blocker (contract answers still zero).

Demo readiness (98/100 standalone) is unaffected.

Pilot and Production readiness remain low (42/100 and 28/100) until real faculty web hosting + verified auth contract evidence exists.

---
*This score reflects honest current state after the strategic pivot from LAN to Faculty Web Portal.*
