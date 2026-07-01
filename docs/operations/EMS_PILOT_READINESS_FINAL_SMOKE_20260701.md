# EMS Pilot Readiness — Final Smoke Report

**Date:** 2026-07-01  
**Pass type:** Final smoke + localhost normalization  
**Follows:** Manual role UI review (commit `3c8f59b`) and role fix (`431a6dc`)

---

```text
RESULT: PILOT_READY_WITH_LIMITATIONS

HEAD:
3c8f59b docs(ops): record manual role UI review findings

Repo status:
clean (before this pass's doc commits)

Services:
- Backend:  http://127.0.0.1:8000   PID: 32708
- Frontend: http://127.0.0.1:3000   PID: 13432
- Extra frontend stopped: YES (PID 23864 was on port 3001 — duplicate EMS Vite instance
  launched with --port 3000 but auto-bumped to 3001; stopped with Stop-Process)

Role smoke:
- Admin:           PASS  (200, effective_role=admin)
- ESQ Head:        PASS  (200, effective_role=esq_head)
- Dept Supervisor: PASS  (200, effective_role=dept_supervisor)
- Staff:           PASS  (200, effective_role=staff, araya.fa)
- Teacher:         PASS  (200, effective_role=teacher)
- Print Shop:      PASS  (200, effective_role=print_shop)

Note: Login rate-limiter (10 req / 300 s) was triggered during the API smoke because
6 malformed requests (missing selected_role) consumed 6 of the 10 allowed slots before
the corrected batch began. Teacher and Print Shop were re-verified after the window
expired. This is expected security behavior, not a system fault.

Regression checks:
- Dept dashboard:      PASS  (GET /api/dashboard/ → 200; was 403 before fix 431a6dc)
                             Response scoped to dept_supervisor's academic group.
- Staff demo:          PASS  (araya.fa → effective_role=staff; not esq_head)
- Print queue:         PASS  (GET /api/printing/queue → 200 for print_shop)
                             GET /api/schedule/copy-count → 403 by design (not shown in UI;
                             frontend skips call when effectiveRole === "print_shop")
- Teacher nav:         PASS  (navigation.ts confirmed: teacher role absent from
                             audit-explorer, operational-health, platform-config,
                             optimizer-trace, invigilation-rate-rules, payment draft,
                             payment settings)
- Admin payment safety: PASS (FINAL_AUTHORIZATION_REQUIRED exists only as a status label;
                             checklist item CHECK_FINAL_AUTHORIZATION_DISABLED actively
                             asserts final auth is not enabled; no action button present)

Admin View As:
NOT USED / NOT VALID

Build/i18n/backend focused tests:
PASS
- npm run build:          ✓ (301 modules, 1.35 s; chunk size advisory non-blocking)
- npm run check:i18n:     ✓ (2509 keys, en/th identical)
- npm run check:i18n:raw: ✓ (warning mode, no blocking errors)
- python -m compileall:   ✓ (exit 0)
- pytest (3 files, 10 tests): ✓ (10 passed, 0 failed)
    test_dashboard_policy.py     — 2 passed
    test_dashboard_service.py    — 1 passed
    test_schedule_query_service.py — 7 passed

Known limitations:
- Admin View As is not valid and must not be used for role review (endpoint exists
  but produces an admin-scoped view, not a true role simulation).
- Secretary demo credential is not included in the quick-start demo table. A secretary
  account exists in seed.py but was not tested in this pass.
- Print Shop direct copy-count endpoint (/api/schedule/copy-count) returns 403 by design.
  Frontend skips this call for print_shop. Not a bug.
- Thai export/font pass remains pending if Thai official document exports (PDF/Excel with
  Thai fonts) are required before pilot.
- Finance review of supporting roster (5-sheet workbook) remains pending. Finance
  stakeholder has not confirmed acceptance.
- Browser-based manual recheck (admin, dept supervisor, staff, teacher, print shop) was
  not captured in this automated pass. This must be performed by the pilot operator
  before handing off to test users.

Docs updated:
YES
- RUNBOOK.md: replaced ketsinee.s with araya.fa as confirmed staff demo;
              added Print Shop entry (printshop.ops / print123)
- docs/operations/EMS_PILOT_READINESS_FINAL_SMOKE_20260701.md: this file

Real commits:
- (see commit created by this pass)

Push status:
PUSHED

Final git status:
clean

Services left running:
YES
Backend PID: 32708  (http://127.0.0.1:8000)
Frontend PID: 13432 (http://127.0.0.1:3000)
```

---

## Findings Detail

### Frontend Instance Normalization

Two identical EMS Vite processes were running when this pass began:

| PID   | Port | Command |
|-------|------|---------|
| 13432 | 3000 | `node vite.js --host 0.0.0.0 --port 3000` |
| 23864 | 3001 | `node vite.js --host 0.0.0.0 --port 3000` (auto-bumped to 3001) |

PID 23864 was stopped. Only 3000 remains active.

### Role Smoke — API Evidence

All 6 roles returned `200` with correct `effective_role`:

```
Admin:           200  effective_role=admin           base_role=admin
ESQ Head:        200  effective_role=esq_head        base_role=esq_head
Dept Supervisor: 200  effective_role=dept_supervisor base_role=dept_supervisor
Staff:           200  effective_role=staff           base_role=staff
Teacher:         200  effective_role=teacher         base_role=teacher
Print Shop:      200  effective_role=print_shop      base_role=print_shop
```

### Dept Supervisor Dashboard — Regression Confirmed

Before fix `431a6dc`: `GET /api/dashboard/` returned 403 for `dept_supervisor`.  
After fix: Returns 200 with scoped aggregate fields:

```
copy_cost, recent_logs, rooms_in_use, scheduled_sections, total_sections,
total_sheets, total_students, total_teachers, unscheduled_sections
```

Data is scoped by `academic_group` (implemented in `DashboardService.get_dashboard_stats`).

### Print Shop Copy-Count — Graceful Skip Confirmed

`frontend/src/hooks/usePrintQueueData.ts` (line 53–54):

```typescript
const copyCountPromise =
  effectiveRole === "print_shop" ? Promise.resolve(null) : getCopyCount().catch(() => null);
```

When the user is `print_shop`, the supplemental call is skipped. The page renders without
hitting the unauthorized endpoint. The backend correctly returns 403 if called directly.

### Payment Page Safety Confirmed

`/invigilation-payment-document-draft` contains:

- Status labels only — `FINAL_AUTHORIZATION_REQUIRED` is a display string
- Checklist item `CHECK_FINAL_AUTHORIZATION_DISABLED` asserts final authorization is
  NOT enabled, as a review safeguard
- No action button, form, or API call for final authorization exists

### Hidden Diagnostics Confirmed Hidden

All 8 de-scoped pages carry `hidden: true` in `navigation.ts`:

```
admin-intelligence-dashboard, analytics (executive), governance-cockpit,
operational-health, audit-explorer, optimizer-trace, platform-configuration, import-audit
```

Routes remain accessible by direct URL for authorized roles but do not appear in any
role's sidebar navigation.

---

## Pre-Pilot Actions Required

| # | Action | Owner | Blocking? |
|---|--------|-------|-----------|
| 1 | Browser manual recheck (5 roles) | Pilot operator | YES — before handing to test users |
| 2 | Thai export/font validation | Dev | YES — if Thai official documents are needed |
| 3 | Finance review of supporting roster | Finance stakeholder | YES — before real payment processing |
| 4 | Secretary demo credential added to RUNBOOK | Dev | NO — low priority |
| 5 | Chunk size refactor (index.js 673 kB) | Dev | NO — advisory only, runtime functional |
