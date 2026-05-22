# PILOT_BLOCKER_DASHBOARD.md (Updated)

**Date**: 2026-05-22 (Updated — hardening triage and contract gate added)

---

## Pilot Blocker Status

| # | Blocker | Owner | Required Evidence | Current Status | Blocking Level | Next Action | Linked Document |
|---|---------|-------|------------------|----------------|----------------|-------------|----------------|
| 1 | Pilot target environment (Faculty LAN selected) | Faculty Leadership | Decision recorded in SETUP_RECORD | IN PROGRESS | Critical | Confirm IT owner and infrastructure details | PILOT_TARGET_DECISION_PACKAGE.md |
| 2 | IT owner assigned | Faculty Leadership | Name + contact in tracker | OPEN | Critical | Assign during decision meeting | PILOT_HUMAN_ACTION_TRACKER.md |
| 3 | Laravel auth contract verified | Laravel owner + IT | LARAVEL_AUTH_CONTRACT_QUESTIONS.md answers confirmed | OPEN | Critical | Send contract questions to Laravel owner | LARAVEL_AUTH_CONTRACT_QUESTIONS.md |
| 4 | CMU email field name confirmed | Laravel owner | Exact field name verified against real code | OPEN | Critical | Part of contract response | FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md |
| 5 | session("USS") payload verified | Laravel owner | Exact structure confirmed against real code | OPEN | Critical | Part of contract response | FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md |
| 6 | Auth bridge gate conditions met | EMS + Laravel owner | AUTH_BRIDGE_IMPLEMENTATION_GATE.md all checks MET | **BLOCKED on contract** | Critical | Contract first, then gate review | AUTH_BRIDGE_IMPLEMENTATION_GATE.md |
| 7 | PostgreSQL deployment target verified | IT / DBA | DB host, connection string confirmed | OPEN | High | Confirm after IT owner assigned | PRODUCTION_ENV_HANDOFF_CHECKLIST.md |
| 8 | EMS route/mount path decided | EMS + IT | Path agreed and documented | OPEN | High | Decide after Laravel owner consulted | PILOT_ROUTE_AND_AUTH_MAPPING.md |
| 9 | cmu_sso.py path decided | EMS team | Activate vs. bridge decision made | OPEN | High | After bridge option selected | EMS_AUTH_BRIDGE_DESIGN.md |
| 10 | Production SECRET_KEY configured | IT + Deployment owner | Confirmed in handoff checklist | OPEN | High | Configure after target provisioned | PRODUCTION_ENV_HANDOFF_CHECKLIST.md |
| 11 | DATABASE_URL configured | IT + DBA | Working connection + health check | OPEN | High | Provision after target chosen | PRODUCTION_ENV_HANDOFF_CHECKLIST.md |
| 12 | EMS backend deployed | Deployment owner | /health returns OK | OPEN | High | Execute after environment configured | FACULTY_LAN_PILOT_IMPLEMENTATION_PLAN.md |
| 13 | Backup scheduled and tested | IT / Ops | Completed BACKUP_RESTORE_TEST_EVIDENCE | OPEN | High | Execute after deployment | BACKUP_RESTORE_TEST_EVIDENCE.md |
| 14 | DPO retention sign-off | Admin + DPO | Signed DPO template + CMU email flow noted | OPEN | Medium | Send DPO communication package | DPO_RETENTION_SIGNOFF_TEMPLATE.md |
| 15 | Pilot accounts created | EMS team | Account list + role verification | OPEN | Medium | Create after target ready and auth bridge active | UAT_SESSION_EXECUTION_GUIDE.md |
| 16 | UAT execution | Pilot Coordinator | Checklists + observations | OPEN | Medium | Run after accounts + target confirmed | UAT_ROLE_WORKFLOW_CHECKLISTS.md |
| 17 | Go/No-Go approval | Faculty Leadership | Updated GO/NO-GO report with evidence | OPEN | High | Review after UAT complete | UAT_GO_NO_GO_REPORT.md |

---

## Hardening Blockers (Audit-Driven, Code-Level)

| # | Hardening Item | Owner | Targeted Fix | Status |
|---|---------------|-------|-------------|--------|
| H1 | `create_all()` + `seed_data()` on every startup | Backend owner | Gate on `settings.environment == "development"` | ✅ Fix committed (this pass) |
| H2 | SQLite fallback on missing DATABASE_URL | Backend owner | RuntimeError in non-development; loud dev-mode warning | ✅ Fix committed (this pass) |
| H3 | ENV vs ENVIRONMENT inconsistency | Backend owner | `_is_production()` helper uses ENVIRONMENT first, ENV as fallback | ✅ Fix committed (this pass) |
| H4 | Login token in response body | Backend owner | Defer — remove or add explicit warning after pilot | DEFER |
| H5 | /health access policy mismatch | Backend owner | Defer — enforce or update docstring | DEFER |
| H6 | cmu_sso.py path decision | Backend + Laravel owner | Defer — depends on bridge option | PENDING CONTRACT |

---

**End of PILOT_BLOCKER_DASHBOARD.md (Updated 2026-05-22)**
