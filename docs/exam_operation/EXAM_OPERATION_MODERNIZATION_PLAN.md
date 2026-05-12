# Exam Operation Modernization Plan
## Safe Implementation Roadmap

**Date:** 2026-05-12  
**Prerequisite:** Phase 3 architecture renovation completion (currently 20%, Week 2 pending)  
**Stack:** FastAPI + React/TypeScript — no stack changes

---

## 1. Guiding Principles

1. **Preserve EMS superiority.** Where EMS already beats the legacy process, make no changes.
2. **Convert, don't copy.** Every valuable operational rule becomes a configurable service, not a hardcoded behavior.
3. **No destructive migrations.** All new DB tables are additive. Existing tables are not modified destructively.
4. **Audit first.** Every new service routes mutations through `audit_service.py`.
5. **PDPA by default.** No new endpoint exposes personal student data without explicit policy check.
6. **DRY always.** New logic reuses existing `ExamPeriod`, `User`, `AuditLog`, optimizer infrastructure.
7. **Phase 3 must complete first.** Fat routers (`schedule.py` 1087L, `optimize_workflow.py` 1331L, `submissions.py` 911L) must be extracted before adding new features to them.

---

## 2. Prerequisites (Phase 3, Week 2 — current sprint)

These must complete before Phase 4 begins:

- [ ] Extract `services/submission_service.py` from `submissions.py` (911 lines)
- [ ] Extract `services/schedule_service.py` from `schedule.py` (1087 lines)
- [ ] Auth unification Steps 1–2 (`permissions.py` missing guards, `auth_utils.py` shims)
- [~] `optimize_workflow.py` service extraction (in progress: workflow lock lifecycle extracted to service layer)

**Rationale:** Adding course condition hooks into a 1331-line monolithic router is dangerous. Service extraction first ensures new features have clean injection points.

---

## 3. Phase 4 — Operational Foundation (Proposed: 4–6 weeks)

### Sprint 4.1 — Calendar & Rules Engine (2 weeks)

**Goal:** Configurable operation calendar + invigilator rules in optimizer

**Tasks:**
1. Add to `models.py`:
   - `ExamOperationActivityType`
   - `ExamOperationCalendar`
   - `ExamOperationNotification`
   - `InvigilationRuleSet`

2. Create migration (additive only, no table changes)

3. Seed `ExamOperationActivityType` with CMU Humanities template

4. Create `backend/services/calendar_service.py`:
   - `generate_calendar_for_period()`
   - `mark_activity_complete()`
   - `get_overdue_activities()`
   - `get_dashboard_summary()`

5. Create `backend/routers/operation_calendar.py` (thin — delegates to service)

6. Wire `generate_calendar_for_period()` into `period.py` on `draft → active` transition

7. Load `InvigilationRuleSet` from DB in `optimize_workflow.py` (extract to `schedule_service.py` first)

8. Create `frontend/src/pages/OperationCalendar.tsx` — list view only

9. Add overdue-count widget to `DashboardHighlights.tsx`

**Tests:** Add `tests/test_calendar_service.py` (minimum 10 test cases)

**Safe:** No existing router changes. No existing model changes. Additive only.

---

### Sprint 4.2 — Course Conditions + Exam Policy (2 weeks)

**Goal:** Optimizer respects course exam conditions and university slot policy

**Tasks:**
1. Add to `models.py`:
   - `CourseExamCondition`
   - `ExamSlotPolicy`

2. Create migration

3. Create `backend/services/course_condition_service.py`:
   - `set_condition()`
   - `get_conditions_for_period()`
   - `validate_optimizer_constraints()`

4. Create `backend/services/exam_slot_policy_service.py`:
   - `load_constraints_for_optimizer()`
   - `get_required_slot()` 

5. Add constraint loading to `optimize_workflow.py` → `schedule_service.py`:
   - Load course conditions as optimizer hard constraints
   - Load slot policy as optimizer hard constraints

6. New router endpoints:
   - `GET/POST /api/course-conditions/{period_id}`
   - `GET/POST/PUT /api/exam-slot-policy/{period_id}`

7. Frontend: Course condition editor (modal in `ExamManager.tsx` or `Submissions.tsx`)

8. Frontend: Exam slot policy table editor in `SettingsV2.tsx` or new `Period.tsx` section

**Tests:** Add `tests/test_course_condition_service.py`, `tests/test_exam_slot_policy.py`

**Risk:** Optimizer constraint changes could affect existing behavior. Mitigation: feature-flag the new constraints (enabled only when `InvigilationRuleSet` exists for period).

---

## 4. Phase 5 — Review & Post-Exam (Proposed: 3–4 weeks)

### Sprint 5.1 — Draft Circulation (2 weeks)

**Tasks:**
1. Add to `models.py`:
   - `DraftCirculation`
   - `DraftCirculationDepartment`
   - `DraftCirculationFeedback`

2. Create `backend/services/draft_circulation_service.py`

3. Create `backend/routers/draft_circulation.py`

4. Frontend: `WorkflowDraftCirculation.tsx` component

5. Wire into period state machine: `OPTIMIZED → CIRCULATING → FEEDBACK_COLLECTED → REVISED`

6. Email notifications (via `email_notifications.py`) on circulation initiation

**Tests:** `tests/test_draft_circulation_service.py`

---

### Sprint 5.2 — Post-Exam Incidents + Workload Calendar (2 weeks)

**Tasks:**
1. Add to `models.py`:
   - `PostExamIncident`
   - `PostExamSummary`

2. Create `backend/services/post_exam_service.py`

3. Extend `exam_pickup.py` with `generate_incident_qr_token()`

4. Create `backend/routers/post_exam.py`

5. Frontend: `WorkloadCalendarView.tsx` (extend existing `WorkflowCalendarView.tsx`)
   - Calendar grid: date × time slot × assigned supervisors
   - Color-coded by load
   - PDF export

6. Frontend: Post-exam incident list view (new page)

**Tests:** `tests/test_post_exam_service.py`

---

## 5. Phase 6 — Public Access & Reporting (Proposed: 2–3 weeks)

### Tasks:
1. Extend `routers/public.py`:
   - `/api/public/student/{student_id}/exams` (rate-limited, PDPA-safe)
   - `/api/public/courses/{course_id}/exam`
   - No auth required, PDPA: only schedule info, no personal data

2. `CoSupervisorCalculationService`:
   - Load enrollment by faculty from import data
   - Apply formula: `(other_faculty_students / total) × required_invigilators`
   - Generate co-supervisor request document (extends `gen_docs.py`)

3. Post-period summary report generation:
   - Template-driven (extends `gen_docs.py`)
   - Inputs: incident data + workload stats + schedule stats
   - Output: DOCX/PDF for committee meeting

4. Notification engine (background):
   - Daily job checking `ExamOperationCalendar` for approaching/overdue deadlines
   - Email via `email_notifications.py`

5. `RoomLendingRequest` model + basic approval flow (optional, lower priority)

---

## 6. DRY Refactor Opportunities Found

### R1. Thai Date Formatting (DUPLICATE)

Found in both `gen_docs.py` and `operational_documents.py`:
- `THAI_MONTHS` dict
- `THAI_DAYS` dict
- `thai_date_long()` / `thai_date_short()` functions
- `_THAI_MONTHS_SHORT` list

**Fix:** Extract to `backend/utils/thai_dates.py`. Both files import from there.

```python
# backend/utils/thai_dates.py
THAI_MONTHS = {...}
THAI_MONTHS_SHORT = {...}
THAI_DAYS = {...}

def thai_date_long(exam_date: str) -> str: ...
def thai_date_short(exam_date: str) -> str: ...
```

**Impact:** Low risk, high cleanliness. Do immediately.

---

### R2. Font Registration (DUPLICATE)

`operational_documents.py` and potentially `gen_docs.py` both manage Thai font registration. Extract to `backend/utils/pdf_fonts.py`:

```python
def ensure_thai_fonts() -> tuple[str, str]:
    """Register Thai fonts once, return (regular_name, bold_name)."""
    ...
```

---

### R3. Time Range Parsing

`staff_workloads.py` uses `time_ranges.py` functions. Any new service dealing with exam scheduling should import from `time_ranges.py` — do not duplicate time parsing logic.

---

### R4. Audit Logging Pattern

Every router currently calls `log_action(db, user, action, ...)` directly. Some routers are inconsistent. Phase 3 service extraction should route all audit calls through `audit_service.py`. New services must use `audit_service.audit(db, actor_id, action, entity_type, entity_id, metadata)`.

---

### R5. Period Scoping

Many queries filter by `period_id`. There is no shared utility for "get active period for user's role". New services should use a shared `get_active_period(db, period_id_or_default)` utility to avoid duplicating this lookup across 6+ router files.

---

## 7. Audit & PDPA Improvements Required

### A1. New Endpoints Must Be Audited

Every new service method that mutates data must call `audit_service`. This includes:
- `calendar_service.mark_activity_complete()`
- `course_condition_service.set_condition()`
- `draft_circulation_service.initiate_circulation()`
- `post_exam_service.report_incident()`

### A2. Public Endpoints Are PDPA-Sensitive

The public exam search endpoint must:
- Return only schedule data (course code, date, time, room)
- Never return: student names, student IDs, supervisor personal details beyond name
- Apply rate limiting (existing `security.py` rate limiter)
- Log all queries with IP (for abuse monitoring, not personal tracking)

### A3. Incident Reports Contain Sensitive Data

`PostExamIncident` may contain student IDs (for absent student records). Access must be:
- Restricted to admin, ESQ, department supervisors for their own department
- Masked for staff role
- PDPA policy applied at API layer via `pdpa_policy.py`

### A4. Draft Circulation Feedback is Department-Confidential

`DraftCirculationFeedback` should be visible:
- To the department that submitted it
- To admin (who resolves it)
- NOT to other departments (prevents cross-department visibility of internal scheduling data)

---

## 8. What NOT To Do

These are explicit prohibitions based on this analysis:

| Prohibited Action | Reason |
|------------------|--------|
| Add Excel export of student enrollment for email sharing | PDPA violation |
| Add manual room booking flow (5-step wizard) | Replaced by optimizer |
| Add manual supervisor entry form | Replaced by optimizer |
| Add CSV→XLS file conversion utility | Obsolete, import_v2 handles this |
| Bypass audit logging in new services | Violates audit-first principle |
| Add paper leave request workflow | StaffUnavailability already handles this |
| Soft-lock term lifecycle | Locked must remain fully read-only |
| Add per-department shared login | Auth security regression |
| Add hardcoded CMU-specific semester dates | Config must be flexible |
| Store post-exam incident QR tokens in localStorage | Security regression (IDOR risk) |

---

## 9. Success Metrics

After Phase 4–6 completion, EMS should achieve:

| Metric | Current | Target |
|--------|---------|--------|
| Operational steps covered in EMS | 8/20 | 18/20 |
| Manual steps requiring paper | 7 | 1 (cross-faculty room — optional) |
| Audit coverage of new mutations | 100% (maintained) | 100% |
| PDPA-controlled endpoints | All existing | All new |
| Optimizer constraint completeness | ~60% | ~90% |
| Test coverage on new services | 0% | ≥80% |

---

## 10. Deferred / Risky Items

| Item | Risk | Deferral Reason |
|------|------|-----------------|
| REG system auto-fetch | External API dependency — CMU may not have one | Phase 7+ or external integration |
| CMU SSO integration (`cmu_sso.py`) | Existing file but untested | Depends on CMU IT cooperation |
| Formal document format legal validation | Requires official document templates | Legal review needed first |
| Real-time mobile check-in app | New client surface | Frontend stability first |
| Cross-faculty room lending | Requires inter-faculty system access | Governance decision needed |
| HR system leave data sync | Requires CMU HR API | External dependency |

---

## 11. Commit Hash

No code changes were made in this session. This document set is architecture-only.

**Next action:** Complete Phase 3 Week 2 sprint (service extractions), then begin Phase 4 Sprint 4.1.
