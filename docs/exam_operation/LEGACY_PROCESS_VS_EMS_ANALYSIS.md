# Legacy Process vs EMS Analysis
## Brutally Honest Comparative Assessment

**Date:** 2026-05-12  
**Analyst:** Architectural synthesis pass against CMU Humanities operational manual (pp. 1–47)

---

## Category A: EMS_ALREADY_BETTER
### Where EMS architecture is objectively superior — preserve as-is

---

### A1. Import Pipeline

**Legacy:** Download CSV from REG → rename to .XLS → import to e-humanities system  
**EMS:** Import V2: preview → validate → prepare → confirm-check → confirm  
Features: row-level selection, override-with-reason, `ImportRowLog` audit, normalizers, validators

**Why EMS wins:**
- Row-level validation catches bad data before DB write
- Audit trail on every import row
- No file format manipulation required
- Preview-first prevents blind bulk mutations
- Override system with mandatory reason

**Action:** Do NOT import legacy file-handling logic. Optionally add REG-compatible file format parser as an `import_v2/parsers.py` extension.

---

### A2. Room Assignment

**Legacy:** Manual Excel room booking → 5-day process per semester, paper cross-checks, capacity mismatches discovered late  
**EMS:** CP-SAT optimizer assigns rooms respecting capacity, unavailability, and conflict constraints in minutes

**Why EMS wins:**
- Eliminates 5-day manual process
- Capacity constraint is a hard optimizer constraint (not a post-hoc check)
- Room unavailability modeled at DB level (`RoomUnavailability`)
- Preview before confirm = safe rollback

**Action:** Add room condition flags (oral, lab, no-mixing) as optimizer constraints. Do NOT reintroduce manual Excel room booking.

---

### A3. Auth & Access Control

**Legacy:** Shared system login to e-humanities online system, no role separation at API level  
**EMS:** JWT/HttpOnly cookie auth, role-based `permissions.py`, `ProtectedRoute`, role-gated API endpoints

**Why EMS wins:**
- Individual accountability via JWT
- Audit logs tied to specific users
- PDPA-safe: staff cannot access admin data
- Semantic permission helpers (`permissions.ts`)

**Action:** Continue Phase 3 auth unification. Do NOT share credentials or reduce role granularity.

---

### A4. Audit Trail

**Legacy:** No audit trail. Changes to room/supervisor/schedule in the e-humanities system are unrecorded  
**EMS:** `audit_service.py` + `log_action()` throughout all critical endpoints + `ImportRowLog`

**Why EMS wins:**
- Every mutation is traceable to user + timestamp
- Import changes have row-level audit
- Admin audit log restricted to admin role
- Foundation for compliance and dispute resolution

**Action:** Ensure all new modules use `audit_service.py`. Never add unaudited mutations.

---

### A5. Staff Unavailability

**Legacy:** Paper/email leave request to HR → data manually compiled → manually excluded from invigilator list  
**EMS:** `StaffUnavailability` DB model, `build_staff_unavailability_map()`, time-range overlap detection, integrated into optimizer

**Why EMS wins:**
- Structured unavailability data
- Automatic optimizer exclusion
- No manual cross-reference required
- Supports partial-day unavailability via time ranges

**Action:** Add leave data import adapter if CMU HR provides an export. Keep current architecture.

---

### A6. Term Lifecycle

**Legacy:** Implicit semester calendar (nothing formally locks old data)  
**EMS:** Explicit `lifecycle_status: draft → active → archived → locked`. Locked = fully read-only.

**Why EMS wins:**
- Historical data is protected
- No accidental mutation of past semester data
- Clear operational state visibility

**Action:** Do NOT soften lifecycle enforcement. Locked must mean locked.

---

### A7. PDPA-Aware Student Data

**Legacy:** Student enrollment data in uncontrolled Excel sheets, forwarded by email, printed freely  
**EMS:** `pdpa_policy.py`, role-gated student endpoints, controlled exports only

**Why EMS wins:**
- Student personal data is not freely printable
- Export governance is enforced at API level
- Masked where role doesn't need full data

**Action:** Do NOT create uncontrolled student data exports. Any new export endpoint must go through PDPA policy check.

---

### A8. Swap System

**Legacy:** No formalized swap process; ad-hoc phone/email arrangements between supervisors  
**EMS:** `swaps.py` / `swaps_v2.py` — request, select target, pending approval, conflict detection, auto-removal of conflicting swaps

**Why EMS wins:**
- Swaps are formally tracked
- Conflict detection prevents double-assignment
- Rejection generates notification
- Audit trail

**Action:** Keep swap system. Enhance with calendar view.

---

### A9. QR Check-In

**Legacy:** Paper attendance sheets, manual signature collection, no digital record  
**EMS:** `checkins.py` + `exam_pickup.py` — QR token system, time-window scan enforcement, multi-party confirmation, `CheckinEvent` audit

**Why EMS wins:**
- Tamper-resistant QR tokens with expiry
- Real-time digital attendance record
- Duplicate scan prevention
- Pickup verification chain

**Action:** Extend QR system with incident reporting (see gap analysis). Do NOT replace with paper.

---

## Category B: LEGACY_PROCESS_STILL_VALUABLE
### Operational knowledge EMS must absorb — convert, don't copy

---

### B1. Exam Scheduling Policy Table (Class-Time → Exam-Time Mapping)

**What it is:** The document shows a formal table (Figure 4.1):  
`MTh 0800 → TUE MAR 18, 1200–1500`  
`TuF 0930 → THU MAR 20, 0800–1100` etc.

This table determines which class meeting pattern maps to which final exam slot. It's a university-wide policy used to avoid student conflicts.

**EMS gap:** The CP-SAT optimizer has no concept of this mapping. It optimizes room/staff but doesn't use CMU's official class-pattern → exam-slot rule.

**Conversion:** Become `ExamSlotPolicyTable` — a configurable database table (`exam_slot_policy`):

```
exam_slot_policy(
  id, period_id, class_pattern,  -- e.g. "MTh", "TuF"
  class_start_time,              -- e.g. "08:00"
  exam_date, exam_start, exam_end,
  exam_type,                     -- REGULAR, SPECIAL
  created_by, created_at
)
```

Optimizer reads this table as hard constraints when `exam_type=REGULAR`.

---

### B2. Course Exam Conditions (เงื่อนไขกระบวนวิชา)

**What it is:** Per-course flags governing how a course must be examined:
- `NO_EXAM` — course has no exam
- `ORAL_ONLY` — oral exam, needs separate oral room
- `SEPARATE_ROOM` — must not share room with any other course
- `NO_CO_EXAM` — cannot be in same exam slot as specific other courses
- `SPECIAL_ROOM_REQUIRED` — needs room with specific equipment (projector, computer lab)
- `LAB_REQUIRED` — requires computer/language lab
- `FOREIGN_NATIONAL_LECTURER_FIRST_SLOT` — lecturer must supervise first slot of exam day (documented in reference)

**EMS gap:** `ExamSubmission.exam_type` only covers online/onsite/no_exam. No room requirement flags. No co-exam restriction.

**Conversion:** Extend `Submission` model or create `CourseExamCondition`:

```python
class CourseExamCondition(Base):
    course_id: int
    period_id: int
    no_exam: bool = False
    oral_only: bool = False
    separate_room: bool = False
    no_co_exam_with: List[int]  # course_ids
    special_room_required: bool = False
    lab_required: bool = False
    notes: str
    created_by: int
    created_at: datetime
```

Optimizer reads these as constraints.

---

### B3. Invigilator Assignment Rules (กฎการจัดกรรมการคุมสอบ)

**What it is:**
- 2 invigilators per room (base rule)
- ≥80 students → 3 invigilators
- Very large room (multiple courses) → 3 invigilators
- Senior staff (faculty head, special professors, admin) → only supervise own department courses
- No consecutive sessions (avoid A-B scheduling where one person covers back-to-back time slots)
- Consecutive allowed only if necessary (configurable exception)
- Each person's workload must be equalized

**EMS gap:** Optimizer has fairness objective but no explicit 2-vs-3 rule tied to student count. No seniority-based constraint. No consecutive-session avoidance rule.

**Conversion:** Create `InvigilationRuleSet` — configurable policy table:

```python
class InvigilationRuleSet(Base):
    period_id: int
    base_per_room: int = 2
    large_room_threshold: int = 80
    large_room_per_room: int = 3
    allow_consecutive: bool = False
    senior_roles: List[str]  # roles restricted to own department
    created_at: datetime
```

Optimizer loads this per-period as constraint parameters.

---

### B4. Co-Supervisor Count Calculation

**What it is:** Formula to determine how many supervisors to request from other faculties:  
`co_supervisors = (students_from_other_faculties / total_students) × required_supervisors`

This was calculated from REG Report #42 data. Result used to formally request invigilators from partner faculties.

**EMS gap:** `co_exam.py` exists but has no calculation engine for co-supervisor counts.

**Conversion:** Create `CoSupervisorCalculationService`:
- Input: period_id + enrollment data per faculty
- Output: per-faculty co-supervisor request counts
- Generate formal request document

---

### B5. Draft Schedule Circulation Workflow

**What it is:** After initial schedule generation, draft is sent to all departments for review:
- Each department checks their courses for date/time/room/supervisor errors
- Feedback collected per department
- Changes made and re-circulated if significant
- No formal tracking in legacy system (ad-hoc email)

**EMS gap:** Current workflow (Admin → ESQ → Secretary) is an internal approval chain. No department-level draft review round exists.

**Conversion:** Add `DraftCirculationRound` workflow step:
- After optimization confirmed: system → `CIRCULATION` state
- Per-department review task created
- Department submits feedback via form (structured)
- Admin processes feedback and marks resolved
- System proceeds to `ANNOUNCED` state when all departments confirmed

---

### B6. Supervisor Workload Calendar

**What it is:** Print-based report showing each supervisor's exam duties across all dates. Used to verify even distribution and catch over-assignment.

**EMS gap:** `staff_workloads.py` tracks counts but no calendar-format view exists in frontend.

**Conversion:** Add `WorkloadCalendarView` component:
- Calendar grid: dates × time slots
- Each cell shows assigned supervisor's name
- Color-coded by load (green = balanced, amber = approaching limit, red = over)
- Exportable as PDF/Excel

---

### B7. Post-Exam Issue Reporting

**What it is:** After each exam session:
- Supervisors report issues via QR code → incident form
- Faculty compiles issues
- Presented at department committee meeting
- Used for process improvement

**EMS gap:** QR check-in exists but no incident/issue reporting flow. No post-exam summary module.

**Conversion:** Create `PostExamIncidentService`:
- `ExamIncident` model: schedule_id, reported_by, incident_type, description, resolved, resolution_notes
- `incident_types`: student_absent, late_student, paper_shortage, room_issue, supervisor_issue, cheating_suspected, other
- Summary report per exam period

---

### B8. Public Student Exam Lookup

**What it is:** Public website search at `human.cmu.ac.th/ตารางสอบออนไลน์`:
- Search by student ID → show all exam dates/times/rooms
- Search by course code → show exam schedule
- Search by supervisor name → show supervision assignments

**EMS gap:** `routers/public.py` exists but limited. No proper public exam lookup. `StudentSearch.tsx` is internal only.

**Conversion:** Expand `public.py` router with:
- `/api/public/student/{student_id}/exams` — no auth required, returns anonymized schedule
- `/api/public/courses/{course_id}/exam` — public exam date/room
- Rate limited, no personal data beyond schedule info (PDPA compliant)

---

### B9. Operation Calendar (แผนปฏิบัติงาน)

**What it is:** Monthly activity schedule showing which tasks happen in which months across all 3 semesters. Each activity has an owner and timing dependency.

**EMS gap:** No operation calendar concept at all. EMS has period lifecycle but no deadline/activity planning layer.

**Conversion:** Create `ExamOperationCalendar` engine — see dedicated document.

---

## Category C: LEGACY_PROCESS_SHOULD_NOT_BE_IMPORTED
### Manual workarounds, paper-first flows, unsafe patterns

---

### C1. CSV → XLS Manual File Conversion

**Why not:** Technical workaround for legacy system limitation (e-humanities required XLS, REG exported CSV). EMS Import V2 accepts any supported format via parsers.

**Risk if imported:** Adds format-specific brittleness, maintenance burden.

---

### C2. Manual Room Booking (5-day process)

**Why not:** This entire step is replaced by the CP-SAT optimizer. Reimporting it would mean reverting to O(n×m) manual matching.

**Risk if imported:** Loses optimization quality, wastes 5+ person-days per semester.

---

### C3. Manual Supervisor Entry (step-by-step system form)

**Why not:** The e-humanities system requires manual entry of each supervisor per room per date. EMS optimizer generates this automatically.

**Risk if imported:** Revertion to manual O(n) data entry per exam slot.

---

### C4. Paper Leave Data Request

**Why not:** Paper/email request chain for leave data has no audit trail and creates data lag. EMS `StaffUnavailability` model accepts direct entry.

**Risk if imported:** Introduces manual data pipeline with no auditability.

---

### C5. Uncontrolled Excel Student Data Distribution

**Why not:** Reference document describes emailing/sharing Excel files of enrolled students between administrative units. This is a PDPA violation — uncontrolled personal data distribution.

**Risk if imported:** Data breach risk, regulatory non-compliance, loss of data governance.

---

### C6. Paper-Based Attendance Sheets as Primary Record

**Why not:** Paper attendance is superseded by EMS QR check-in system. Paper cannot be audited, deduplicated, or cross-referenced programmatically.

**Risk if imported:** Loses tamper-resistant digital audit. No real-time visibility.

---

### C7. Hardcoded REG File Format Dependencies

**Why not:** The manual describes very specific REG download menu paths and file naming conventions. These change with REG system updates. EMS should abstract behind a parser interface.

**Risk if imported:** System breaks when REG changes export format.

---

### C8. No-Consecutive-Session Rule as Manual Check

**Why not:** In the legacy system, this is manually verified by reviewing printed supervisor schedules. Should be an optimizer constraint, not a post-generation manual check.

**Risk if imported:** Errors in manual verification, inconsistent enforcement.

---

### C9. Cross-Faculty Room Requests via Paper

**Why not:** Paper forms for room borrowing from other faculties have no tracking. EMS should support digital cross-unit room sharing requests.

**Risk if imported:** Untracked room commitments, scheduling conflicts.

---

## Summary Matrix

| Process | Category | EMS Action |
|---------|----------|-----------|
| REG data import | EMS_ALREADY_BETTER | Add format adapter |
| Room assignment | EMS_ALREADY_BETTER | Add condition flags |
| Auth/access control | EMS_ALREADY_BETTER | Continue Phase 3 |
| Audit trail | EMS_ALREADY_BETTER | Extend to new modules |
| Staff unavailability | EMS_ALREADY_BETTER | Add HR sync option |
| Term lifecycle | EMS_ALREADY_BETTER | Keep strict |
| PDPA student data | EMS_ALREADY_BETTER | Block new uncontrolled exports |
| Swap system | EMS_ALREADY_BETTER | Keep + enhance |
| QR check-in | EMS_ALREADY_BETTER | Extend with incidents |
| Scheduling policy table | LEGACY_STILL_VALUABLE | → ExamSlotPolicyTable |
| Course exam conditions | LEGACY_STILL_VALUABLE | → CourseExamConditionService |
| Invigilator rules | LEGACY_STILL_VALUABLE | → InvigilationRuleSet |
| Co-supervisor count | LEGACY_STILL_VALUABLE | → CoSupervisorCalculationService |
| Draft circulation | LEGACY_STILL_VALUABLE | → DraftCirculationWorkflow |
| Workload calendar | LEGACY_STILL_VALUABLE | → WorkloadCalendarView |
| Post-exam incidents | LEGACY_STILL_VALUABLE | → PostExamIncidentService |
| Public exam lookup | LEGACY_STILL_VALUABLE | → Public API expansion |
| Operation calendar | LEGACY_STILL_VALUABLE | → ExamOperationCalendar |
| CSV→XLS conversion | SHOULD_NOT_IMPORT | Obsolete |
| Manual room booking | SHOULD_NOT_IMPORT | Replaced by optimizer |
| Manual supervisor entry | SHOULD_NOT_IMPORT | Replaced by optimizer |
| Paper leave request | SHOULD_NOT_IMPORT | Replaced by StaffUnavailability |
| Excel student distribution | SHOULD_NOT_IMPORT | PDPA violation |
| Paper attendance as primary | SHOULD_NOT_IMPORT | Replaced by QR |
| Hardcoded REG paths | SHOULD_NOT_IMPORT | Abstract behind parser |
| Manual consecutive check | SHOULD_NOT_IMPORT | → Optimizer constraint |
| Paper room borrowing | SHOULD_NOT_IMPORT | → Digital request system |
