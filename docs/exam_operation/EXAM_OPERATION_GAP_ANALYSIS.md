# Exam Operation Gap Analysis
## What EMS Is Missing vs CMU Operational Requirements

**Date:** 2026-05-12  
**Severity ratings:** CRITICAL / HIGH / MEDIUM / LOW  
**Source:** CMU Faculty of Humanities operational manual (pp. 1–47)

---

## Summary

| Total gaps identified | 14 |
|----------------------|-----|
| CRITICAL gaps | 3 |
| HIGH gaps | 6 |
| MEDIUM gaps | 4 |
| LOW gaps | 1 |

---

## Gap 1 — No Exam Operation Activity Calendar

**Severity:** CRITICAL  
**Reference:** Table 4.1 (pp. 27–28), monthly activity plan

**What's missing:**
- No configurable activity/deadline calendar per exam period
- No tracking of which operational tasks have been completed
- No automated reminders when deadlines approach
- Administrators rely on institutional memory

**Impact:**
- Missed deadlines cause cascading delays across the 20-step process
- No visibility into current operational state at management level
- Cannot report exam operation readiness to leadership

**Resolution:** `ExamOperationCalendar` engine (see dedicated document)

**EMS files to modify:** `models.py`, new `services/calendar_service.py`, new `routers/operation_calendar.py`, new `pages/OperationCalendar.tsx`

---

## Gap 2 — No Course Exam Condition Flags

**Severity:** CRITICAL  
**Reference:** Step 4, pp. 47–49

**What's missing:**
EMS only has `exam_type: online | onsite | no_exam` on submissions.

Missing flags:
- `oral_only` — course uses oral examination (needs oral room)
- `separate_room` — must not share room with any other section
- `no_co_exam_with` — cannot share exam slot with specific course IDs  
- `special_room_required` — needs projector, overhead, computer
- `lab_required` — needs computer or language lab
- `own_lecturer_only` — must be supervised exclusively by course lecturer

**Impact:**
- Optimizer ignores room type requirements — courses may be assigned wrong rooms
- "No co-exam" constraint not enforced — section conflicts possible
- Admin must manually fix optimizer output for these cases

**Resolution:**
- New `CourseExamCondition` model in `models.py`
- New `CourseExamConditionService` in `services/`
- Optimizer reads conditions as hard constraints
- UI: course condition editor (modal in ExamManager or Submissions)

---

## Gap 3 — No Draft Schedule Circulation Workflow

**Severity:** CRITICAL  
**Reference:** Steps 16–17, p. 61

**What's missing:**
After optimizer runs and schedule is confirmed, the reference process requires circulating the draft to all departments for error checking. This catches:
- Wrong exam times for courses
- Wrong room assignments
- Supervisor conflicts not caught by optimizer
- Human errors in course data

Currently EMS has no department-level review round. The approval chain (Admin→ESQ→Secretary) is internal, not department-facing.

**Impact:**
- Errors in schedule discovered late (by students or on exam day)
- No structured feedback collection from departments
- No audit trail of who reviewed and confirmed their department's schedule

**Resolution:** `DraftCirculationService` + `DraftCirculationWorkflow` (see Workflow Engine doc)

---

## Gap 4 — No Exam Slot Policy Table (Class-Pattern → Exam Slot)

**Severity:** HIGH  
**Reference:** Step 1, Figure 4.1 (p. 36), Special/Regular exam tables

**What's missing:**
CMU uses a university-wide policy table that maps:
- Class meeting pattern (MTh, TuF, We, etc.)
- Class start time (08:00, 09:30, 11:00, etc.)
→ Specific exam date + time slot

The optimizer currently schedules exams freely without respecting this policy. This means:
- Final exam schedules may conflict with university central exam schedule
- Students registered in both faculty and cross-faculty courses may have conflicts

**Impact:**
- Serious student conflict risk for cross-faculty enrollees
- Manual post-optimization fixing required

**Resolution:**
- New `ExamSlotPolicy` DB table
- Policy engine that pre-loads constraints for optimizer
- Import from CMU REG policy or manual entry

---

## Gap 5 — No Invigilator Ratio Rules in Optimizer

**Severity:** HIGH  
**Reference:** Step 9, p. 53

**What's missing:**
The reference document specifies:
- **2 invigilators per room** (standard rule)
- **≥80 students → 3 invigilators** (capacity rule)
- **Large room (multi-course) → 3 invigilators** (complexity rule)
- **Senior staff → own department only** (seniority rule)
- **No consecutive sessions** (fatigue/fairness rule)

EMS optimizer has a fairness objective but no explicit ratio rules tied to student count. No seniority constraint. No consecutive-session avoidance.

**Impact:**
- Under-staffed rooms possible when >80 students assigned
- Senior professors may be assigned outside their department
- Supervisors may get back-to-back sessions unfairly

**Resolution:**
- `InvigilationRuleSet` configurable DB model
- Optimizer reads and applies these as constraints
- Admin configures per period

---

## Gap 6 — No Co-Supervisor Count Calculation

**Severity:** HIGH  
**Reference:** Step 10, pp. 56–57

**What's missing:**
When other faculties' students are enrolled in a faculty's courses (cross-faculty registration), co-supervisors must be provided by those faculties proportionally. The formula:

```
co_supervisors_from_faculty_X = 
  (students_from_X enrolled in our courses) / (total enrolled) × required_invigilators
```

EMS has `co_exam.py` for cross-faculty exams but no calculation engine for co-supervisor counts.

**Impact:**
- Manual spreadsheet calculation required
- Formal co-supervisor request letters cannot be auto-generated
- Proportional assignment errors are common

**Resolution:** `CoSupervisorCalculationService` — reads enrollment data, outputs formal request counts per faculty

---

## Gap 7 — No Post-Exam Incident Reporting

**Severity:** HIGH  
**Reference:** Step 20, p. 71

**What's missing:**
After exams, supervisors should be able to report:
- Absent students
- Late arrivals
- Paper shortages
- Room issues
- Suspected cheating incidents
- Any other operational issues

Reference mentions QR code on OMR envelope → report form. EMS has QR check-in but no incident reporting.

**Impact:**
- Issues go unreported or are reported informally
- No data for process improvement
- No audit trail of exam-day incidents
- Cannot generate post-exam summary for committee

**Resolution:** `PostExamIncidentService` + incident QR token (extension of `exam_pickup.py`)

---

## Gap 8 — No Supervisor Workload Calendar View

**Severity:** HIGH  
**Reference:** Step 12, p. 58

**What's missing:**
The reference describes printing a calendar-format report showing each supervisor's exam duties. Used to verify even distribution before finalizing.

EMS `staff_workloads.py` tracks workload counts but:
- No calendar-format visualization
- No per-supervisor day-by-day view
- No frontend component for workload overview

**Impact:**
- Workload imbalances not caught before announcement
- Supervisors with 8-session loads vs others with 2 sessions
- Admin cannot manually balance without visual overview

**Resolution:** `WorkloadCalendarView` frontend component (extends existing `WorkflowCalendarView.tsx`)

---

## Gap 9 — No Public Student Exam Search

**Severity:** MEDIUM  
**Reference:** Step 19, p. 70

**What's missing:**
The reference describes a public search interface at `human.cmu.ac.th`:
- Search by student ID → show all exam dates/times/rooms
- Search by course code → exam schedule
- Search by supervisor name → supervision schedule

EMS `routers/public.py` exists but is minimal. `StudentSearch.tsx` is internal (authenticated).

**Impact:**
- Students cannot self-serve exam schedule lookup
- Increases support burden on academic staff
- Students rely on printed schedules (which may be outdated)

**Resolution:** Extend `public.py` with rate-limited, PDPA-safe public search endpoints

---

## Gap 10 — No Operation Summary Report

**Severity:** MEDIUM  
**Reference:** Step 20, p. 71

**What's missing:**
Post-period summary for committee meetings:
- Total exams conducted
- Incidents by type
- Supervisor distribution statistics
- Issues resolved vs unresolved
- Recommendations for next period

**Impact:**
- No data-driven review of operations
- Institutional learning is informal only
- Cannot identify recurring problems

**Resolution:** Auto-generate summary report from `PostExamIncidentService` data + existing workload/schedule statistics

---

## Gap 11 — Import Enrollment Timing Policy

**Severity:** MEDIUM  
**Reference:** Step 15, p. 60

**What's missing:**
The reference specifies that student names should be uploaded to the scheduling system **after** enrollment stabilizes (after tuition payment deadline). Importing too early results in wrong student counts for room/invigilator assignment.

EMS allows import at any point in the workflow with no timing guard.

**Impact:**
- Room assignments based on incorrect student counts
- Invigilator assignments wrong if enrollment changes significantly

**Resolution:** Add configurable `enrollment_lock_date` to `ExamPeriod` model. Block student re-import after this date (or warn with override).

---

## Gap 12 — No Cross-Faculty Room Request System

**Severity:** MEDIUM  
**Reference:** Step 6, p. 51

**What's missing:**
When faculty room capacity is insufficient, rooms are borrowed from other faculties via paper forms. This is untracked.

**Impact:**
- Double-booking risk when multiple faculties borrow the same room
- No audit trail of room lending agreements
- Room conflicts discovered on exam day

**Resolution:** Add `RoomLendingRequest` model — faculty A requests room X from faculty B for date/time D. Digital approval flow. Room blocked in EMS for that slot when approved.

---

## Gap 13 — No REG System Data Auto-Fetch

**Severity:** LOW  
**Reference:** Step 2, p. 38

**What's missing:**
Data currently requires manual download from CMU REG website. No automated fetch.

**Impact:**
- Human error in downloading wrong data
- Stale data if forgot to re-download
- Manual filename management

**Resolution (optional):** REG API adapter in `import_v2/parsers.py` — if CMU REG provides an API, this can be automated. Otherwise: improved import UX with file format auto-detection.

---

## Gap 14 — No Exam Announcement Document Formal Format Validation

**Severity:** LOW  
**Reference:** Step 18.1, pp. 61–63

**What's missing:**
The exam appointment order (คำสั่งแต่งตั้งกรรมการคุมสอบ) is a formal government administrative order with specific required fields and formatting. `gen_docs.py` generates documents but format correctness is not validated.

**Impact:**
- Generated documents may not meet legal/formal requirements
- HR/payroll rejection of improperly formatted orders

**Resolution:** Validate against `ui_schema.json` template for this document type. Add schema version field to generated documents.

---

## Gap Priority Roadmap

### Phase 4 (High Priority)
1. `ExamOperationCalendar` (Gap 1) — CRITICAL
2. `CourseExamCondition` model + optimizer integration (Gap 2) — CRITICAL
3. `DraftCirculationService` (Gap 3) — CRITICAL
4. `ExamSlotPolicyTable` (Gap 4) — HIGH
5. `InvigilationRuleSet` in optimizer (Gap 5) — HIGH

### Phase 5
6. `PostExamIncidentService` (Gap 7) — HIGH
7. `WorkloadCalendarView` component (Gap 8) — HIGH
8. `CoSupervisorCalculationService` (Gap 6) — HIGH

### Phase 6
9. Public exam search (Gap 9) — MEDIUM
10. Post-period summary report (Gap 10) — MEDIUM
11. Enrollment timing policy (Gap 11) — MEDIUM
12. Cross-faculty room requests (Gap 12) — MEDIUM

### Deferred
13. REG auto-fetch (Gap 13) — LOW, external dependency
14. Document format validation (Gap 14) — LOW, polish
