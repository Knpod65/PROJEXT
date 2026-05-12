# EMS Architectural Synthesis — Executive Report
## CMU Operational Reference vs Current EMS

**Date:** 2026-05-12  
**Reference analyzed:** CMU Faculty of Humanities exam operation manual, pp. 1–47  
**EMS state at analysis:** Phase 3 renovation in progress (readiness 75/100)  
**Pages 48–54 explicitly excluded from analysis.**

---

## 1. Executive Summary

This analysis compared the CMU Faculty of Humanities' 20-step exam management process against the current EMS system architecture. The conclusion is unambiguous:

**EMS already surpasses the legacy manual process in 9 critical dimensions.** The legacy process relies on manual Excel operations, paper circulation, ad-hoc communication, and uncontrolled student data distribution. These should not be reimported.

However, the reference document contains **9 valuable operational knowledge items** that EMS has no equivalent for. These represent real institutional knowledge — invigilator ratio rules, exam slot policy tables, draft circulation workflows, post-exam incident management, and an operation activity calendar — that should be converted into configurable digital services.

**3 CRITICAL gaps** require immediate attention in Phase 4. **6 HIGH gaps** follow in Phase 5. **4 MEDIUM gaps** can be deferred to Phase 6.

No code changes were made in this session. This is a pure architectural synthesis and planning exercise.

---

## 2. What EMS Already Does Better

| Area | Legacy | EMS | Verdict |
|------|--------|-----|---------|
| Data import | Manual CSV→XLS rename | Import V2: preview→validate→confirm | EMS WINS |
| Room assignment | 5-day manual Excel process | CP-SAT optimizer | EMS WINS |
| Auth/access | Shared system login | JWT + role-based, per-user | EMS WINS |
| Audit trail | None | audit_service.py, ImportRowLog | EMS WINS |
| Staff unavailability | Paper HR request | StaffUnavailability DB model | EMS WINS |
| Term lifecycle | Implicit semester calendar | draft→active→archived→locked | EMS WINS |
| PDPA/student data | Uncontrolled Excel distribution | pdpa_policy.py, controlled exports | EMS WINS |
| Swap management | Ad-hoc phone/email | Formal swap system with conflict detection | EMS WINS |
| QR check-in | Paper attendance | Token-based, time-window, multi-party | EMS WINS |

---

## 3. Valuable Legacy Operational Knowledge (Convert, Don't Copy)

| Knowledge Item | EMS Module Required |
|---------------|---------------------|
| Monthly operation activity calendar | `ExamOperationCalendar` engine |
| Class-pattern → exam-slot mapping table | `ExamSlotPolicyTable` + optimizer |
| Course exam condition flags (oral, lab, etc.) | `CourseExamCondition` model + service |
| Invigilator ratio rules (2 base, 3 if ≥80 students) | `InvigilationRuleSet` in optimizer |
| No-consecutive-session constraint | Optimizer constraint (configurable) |
| Draft schedule circulation to departments | `DraftCirculationService` |
| Supervisor workload calendar visualization | `WorkloadCalendarView` frontend |
| Post-exam incident reporting | `PostExamIncidentService` |
| Public student exam search | Extend `public.py` router |

---

## 4. Legacy Logic That Must NOT Be Imported

| Legacy Pattern | Why Rejected |
|---------------|-------------|
| CSV → XLS manual rename | EMS Import V2 is format-agnostic |
| 5-step manual room booking in system | Replaced by optimizer |
| Manual supervisor entry form | Replaced by optimizer |
| Paper leave request chain | StaffUnavailability handles this |
| Excel student data email distribution | PDPA violation |
| Paper attendance as primary record | QR check-in supersedes |
| No-consecutive-session manual paper check | Must be optimizer constraint |
| Cross-faculty room borrowing via paper | Needs digital tracking |

---

## 5. Critical Operational Gaps in EMS

### Gap 1 — No Exam Operation Activity Calendar (CRITICAL)
EMS has period lifecycle but no monthly/weekly activity tracking with deadlines, owners, and completion status. Administrators operate on institutional memory.

**Fix:** `ExamOperationCalendar` engine — configurable activity templates, per-period instantiation, deadline notifications.

### Gap 2 — No Course Exam Condition Flags (CRITICAL)
EMS only has `exam_type: online|onsite|no_exam`. Missing: oral, lab_required, separate_room, no_co_exam_with, special_room_required.

**Fix:** `CourseExamCondition` model + optimizer constraint loading.

### Gap 3 — No Draft Schedule Circulation (CRITICAL)
After optimization, EMS goes straight to internal approval. No department-level error checking round.

**Fix:** `DraftCirculationService` — per-department review tasks, structured feedback, resolution tracking.

---

## 6. Recommended New Modules

| Module | Priority | Extends |
|--------|----------|---------|
| `ExamOperationCalendar` | Phase 4.1 | `period.py` lifecycle |
| `InvigilationRuleSet` | Phase 4.1 | `optimize_workflow.py` |
| `CourseExamCondition` | Phase 4.2 | `models.py`, optimizer |
| `ExamSlotPolicyTable` | Phase 4.2 | `models.py`, optimizer |
| `DraftCirculationService` | Phase 5.1 | Workflow engine |
| `PostExamIncidentService` | Phase 5.2 | `exam_pickup.py` QR |
| `WorkloadCalendarView` | Phase 5.2 | `WorkflowCalendarView.tsx` |
| `CoSupervisorCalculationService` | Phase 6 | `co_exam.py` |
| Public exam search | Phase 6 | `public.py` |

---

## 7. DRY Refactor Opportunities Identified

1. **Thai date formatting** — duplicated in `gen_docs.py` AND `operational_documents.py` → extract to `utils/thai_dates.py`
2. **PDF font registration** — duplicated → extract to `utils/pdf_fonts.py`
3. **Period scoping** — repeated `db.query(Period).filter(id==period_id)` pattern across 6+ routers → `get_active_period()` utility
4. **Audit logging call pattern** — inconsistent across routers → standardize via `audit_service.audit()` method
5. **Time range parsing** — `time_ranges.py` functions not consistently imported → establish as canonical source

---

## 8. Audit/PDPA Improvements Required

1. All new services must route mutations through `audit_service.py` — no exceptions
2. Public exam search must expose ONLY schedule data (no student names, no personal info)
3. Post-exam incidents may contain student IDs — apply `pdpa_policy.py` at API layer
4. Draft circulation feedback is department-confidential — access controls enforced
5. Incident QR tokens must not be stored in localStorage (prevent IDOR)

---

## 9. Calendar & Deadline Engine Proposal (Summary)

- **DB:** `ExamOperationActivityType` (templates) + `ExamOperationCalendar` (per-period instances)
- **Service:** `calendar_service.py` — generate from template, mark complete, get overdue
- **Integration:** Wire into period `draft → active` lifecycle transition
- **Frontend:** `OperationCalendar.tsx` page + dashboard overdue widget
- **Notifications:** Daily background job via email for approaching/overdue items

---

## 10. Workflow Engine Proposal (Summary)

Extend current 3-stage approval chain with:
- **Operational pre-conditions** (calendar tasks must complete before state advances)
- **Draft circulation state** (`CIRCULATING` before `FEEDBACK_COLLECTED`)
- **Post-exam state** (`POST_EXAM` before `CLOSED`)
- **Configurable invigilator rules** (loaded from `InvigilationRuleSet` DB)
- **Exam slot policy constraints** (loaded from `ExamSlotPolicy` DB into optimizer)

---

## 11. Safe Implementation Plan

```
NOW:    Complete Phase 3 Week 2 (service extractions, auth unification)
Phase 4.1: Calendar engine + InvigilationRuleSet (additive, safe)
Phase 4.2: CourseExamCondition + ExamSlotPolicy (optimizer constraint additions)
Phase 5.1: DraftCirculationService (new workflow state)
Phase 5.2: PostExamIncidents + WorkloadCalendar
Phase 6:  Public search + CoSupervisor + Summary reports + Notifications
```

**Safety rules:** No destructive migrations. No existing router rewrites. No auth architecture changes. All new features are additive and behind role guards.

---

## 12. Deferred/Risky Items

| Item | Reason |
|------|--------|
| REG system auto-fetch | Requires external CMU IT cooperation |
| CMU SSO integration | `cmu_sso.py` exists but untested in production |
| Legal document format validation | Requires official templates from CMU legal |
| Cross-faculty room lending | Inter-faculty governance decision needed |
| HR leave data sync | Requires CMU HR API access |
| Real-time mobile supervisor app | New client surface — defer to stability phase |

---

## 13. Validation Results

**Architecture preservation check:**
- ✅ FastAPI backend preserved
- ✅ React + TypeScript frontend preserved
- ✅ Service/repository/policy architecture preserved
- ✅ JWT/cookie auth preserved
- ✅ PDPA-aware design preserved
- ✅ Audit-first principle preserved
- ✅ DRY orientation maintained
- ✅ No optimizer behavior broken
- ✅ No existing submission/schedule flows modified
- ✅ Pages 48–54 of reference document excluded from analysis

**Legacy pattern rejection check:**
- ✅ No Excel-driven workflows proposed
- ✅ No paper-first flows proposed
- ✅ No manual data entry flows proposed to replace optimizer
- ✅ No shared login patterns proposed
- ✅ No uncontrolled student data exports proposed
- ✅ No hardcoded semester dates proposed

---

## 14. Documents Created This Session

1. `docs/exam_operation/EXAM_OPERATION_REFERENCE_COMPARISON.md` — Step-by-step mapping
2. `docs/exam_operation/LEGACY_PROCESS_VS_EMS_ANALYSIS.md` — Classification of all legacy items
3. `docs/exam_operation/EXAM_OPERATION_CALENDAR_ENGINE.md` — Calendar engine design
4. `docs/exam_operation/EXAM_OPERATION_WORKFLOW_ENGINE.md` — Workflow extension design
5. `docs/exam_operation/EXAM_OPERATION_GAP_ANALYSIS.md` — 14 identified gaps with severity
6. `docs/exam_operation/EXAM_OPERATION_MODERNIZATION_PLAN.md` — Phase-by-phase roadmap
7. `docs/exam_operation/EXECUTIVE_REPORT_2026-05-12.md` — This document

**Commit hash:** No code changes committed. Documents only.

---

*Architecture synthesis complete. Next step: Complete Phase 3 Week 2 sprint, then begin Phase 4 Sprint 4.1 (ExamOperationCalendar + InvigilationRuleSet).*
