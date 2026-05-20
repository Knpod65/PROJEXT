# RENOVATION_PHASE_TRACKER

## Current Phase: U1 → L5 Transition

### U1 — Frontend ViewModel / MVC Cleanup: ✅ COMPLETE
- U1-s1: ViewModel Audit ✅
- U1-s2: Governance + Trace ViewModels ✅
- U1-s3: Analytics + Config + Health ViewModels ✅
- U1-s4: Export + Settings ViewModels ✅
- U1-s5: Shared Presenters ✅
- U1-s6: Docs + Final Validation ✅

**Deliverables:**
- 9 domain hooks in `frontend/src/hooks/domain/`
- 9 presenters in `frontend/src/utils/presenters/`
- FRONTEND_VIEWMODEL_COMPLETION_REPORT.md

---

## L5 — Final Policy-Only Authorization Alignment Pass: ✅ COMPLETE

**Goal:** Centralized authorization checks into unified policy helpers. No behavior changes.

### L5-s0 — Scattered Check Audit Document ✅
- Created `docs/architecture/POLICY_AUTHORIZATION_SCATTER_AUDIT.md`
- Identified 31+ inline checks across 5 routers, 2 frontend pages

### L5-s1 — Extend Backend Permission Service ✅
- Added `can_impersonate_admin` alias
- Added `can_run_optimization_recheck` helper
- Added `can_view_governance_report` helper

### L5-s2 — Adopt Policy Helpers in Backend Routers ✅
- `optimize_workflow.py`: Replaced inline role checks with `can_run_optimization_recheck`
- `exam_manager.py`: Replaced inline `current_user.role` check with `can_impersonate_admin`

### L5-s3 — Create Frontend usePermission Hook ✅
- Created `frontend/src/hooks/usePermission.ts`
- Wraps all permission helpers from `utils/permissions.ts`

### L5-s4 — Replace Inline Role Checks in Frontend ✅
- `Optimizer.tsx`: Replaced `role === "admin"` with `canManageExamPeriods(user)`

### L5-s5 — Documentation Final Report ✅
- Updated RENOVATION_PHASE_TRACKER.md (this file)

---

## P1 — Pilot Deployment Readiness: ✅ COMPLETE

**Goal:** Prepare EMS for controlled pilot deployment and IT/security review.
**Result:** System ready for pilot deployment (score: 85/100)

### Completed Documentation
| Slice | File | Status |
|-------|------|--------|
| P1-s0 | `docs/P1_FINAL_SYSTEM_STATE_AUDIT.md` | ✅ |
| P1-s1 | `docs/PILOT_DEPLOYMENT_READINESS_CHECKLIST.md` | ✅ |
| P1-s2 | `docs/IT_HANDOFF_PACKAGE.md` | ✅ |
| P1-s3 | `docs/PDPA_SECURITY_REVIEW_PACKAGE.md` | ✅ |
| P1-s4 | `docs/UAT_TEST_SCRIPT.md` | ✅ |
| P1-s5 | `docs/ROLLBACK_INCIDENT_RUNBOOK.md` | ✅ |
| P1-s6 | `docs/FINAL_PLATFORM_READINESS_REPORT.md` | ✅ |

### Remaining Non-Blocking Operational Items
- SECRET_KEY production generation (DevOps)
- PostgreSQL configuration (DevOps)
- Backup procedure implementation (Ops)
- DPO retention sign-off (Admin + DPO)
- UAT execution (pilot users)

---

*See I18N_FINAL_COVERAGE_REPORT.md for i18n status.*