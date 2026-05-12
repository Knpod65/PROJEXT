# Exam Operation Workflow Engine
## Design Specification

**Date:** 2026-05-12  
**Derived from:** Steps 1–20 of CMU operational manual (pp. 27–73)  
**Status:** Proposed — extending existing workflow system

---

## 1. Current EMS Workflow vs Required Workflow

### Current EMS Workflow (Admin → ESQ → Secretary)
```
Draft → [Admin confirms optimization] → [ESQ approves] → [Secretary approves] → Announced
```

This is an **internal administrative approval chain** for publishing the schedule.

### What the Reference Document Describes
The 20-step reference process is an **operational execution workflow** — a checklist of operational tasks that must be completed before, during, and after the exam period. It is parallel to but distinct from the approval chain.

**Key insight:** EMS needs BOTH:
1. The existing **Approval Workflow** (approval chain, unchanged)
2. A new **Operational Execution Workflow** (task completion tracking)

These run in parallel. The approval chain cannot advance until operational tasks are complete.

---

## 2. Workflow States (Extended)

### Exam Period Operational States

```
SETUP          → Data imported, period created
CONFIGURED     → Courses, rooms, staff configured
OPTIMIZED      → Optimizer has run, schedule generated  
REVIEWING      → Draft circulated to departments for review
REVISED        → Changes incorporated post-review
APPROVED       → Internal approval chain complete
ANNOUNCED      → Schedule publicly visible
EXAMINING      → Active exam days
POST_EXAM      → Exams complete, post-exam review
CLOSED/LOCKED  → Term closed
```

### Integration with Approval Chain
The approval chain gates `REVISED → APPROVED`. Operational tasks gate each state transition.

---

## 3. Operational Task Types

Based on Steps 1–20 of the reference document:

```python
class OperationalTaskType(Enum):
    # Setup phase
    IMPORT_COURSES          = "import_courses"
    IMPORT_PERSONNEL        = "import_personnel"
    IMPORT_STUDENTS         = "import_students"
    SET_EXAM_SCHEDULE       = "set_exam_schedule"           # Step 1
    
    # Configuration phase
    SET_COURSE_CONDITIONS   = "set_course_conditions"       # Step 4
    BOOK_ROOMS              = "book_rooms"                  # Step 6
    REQUEST_LEAVE_DATA      = "request_leave_data"          # Step 8
    ASSIGN_SUPERVISORS      = "assign_supervisors"          # Step 9
    CALC_CO_SUPERVISORS     = "calc_co_supervisors"         # Step 10
    MANAGE_CO_SUPERVISORS   = "manage_co_supervisors"       # Steps 13-14
    
    # Optimization phase
    RUN_OPTIMIZER           = "run_optimizer"
    CONFIRM_OPTIMIZER       = "confirm_optimizer"
    
    # Review phase
    CIRCULATE_DRAFT         = "circulate_draft"             # Step 16
    COLLECT_FEEDBACK        = "collect_feedback"            # Step 16-17
    APPLY_REVISIONS         = "apply_revisions"             # Step 17
    
    # Publication phase
    APPROVAL_WORKFLOW       = "approval_workflow"           # Steps 18 (existing)
    GENERATE_DOCUMENTS      = "generate_documents"          # Step 18
    ANNOUNCE_SCHEDULE       = "announce_schedule"           # Step 19
    
    # Execution phase
    EXAM_DAY_CHECKIN        = "exam_day_checkin"
    PICKUP_VERIFICATION     = "pickup_verification"
    
    # Post-exam phase
    COLLECT_INCIDENTS       = "collect_incidents"           # Step 20
    GENERATE_SUMMARY        = "generate_summary"            # Step 20
    SUBMIT_TO_COMMITTEE     = "submit_to_committee"         # Step 20
```

---

## 4. Draft Circulation Workflow (Critical Gap)

This is the most operationally significant gap — the reference process describes circulating the draft schedule to all departments for review. EMS has no equivalent.

### State Machine

```
OPTIMIZED
  ↓ [admin initiates circulation]
CIRCULATING
  ↓ [all departments submit feedback OR deadline passes]
FEEDBACK_COLLECTED
  ↓ [admin applies revisions]
REVISED
  ↓ [approval workflow]
APPROVED
```

### Database Schema

```sql
CREATE TABLE draft_circulation (
    id              SERIAL PRIMARY KEY,
    period_id       INT NOT NULL REFERENCES exam_period(id),
    initiated_by    INT NOT NULL REFERENCES users(id),
    initiated_at    TIMESTAMP NOT NULL,
    deadline        TIMESTAMP NOT NULL,
    status          VARCHAR(20) DEFAULT 'active',   -- active, closed, cancelled
    notes           TEXT
);

CREATE TABLE draft_circulation_department (
    id              SERIAL PRIMARY KEY,
    circulation_id  INT NOT NULL REFERENCES draft_circulation(id),
    department_code VARCHAR(50) NOT NULL,
    department_name VARCHAR(200),
    assigned_reviewer INT REFERENCES users(id),
    submitted_at    TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending, submitted, acknowledged
    has_issues      BOOLEAN DEFAULT FALSE,
    issue_count     INT DEFAULT 0
);

CREATE TABLE draft_circulation_feedback (
    id              SERIAL PRIMARY KEY,
    circulation_department_id INT NOT NULL 
        REFERENCES draft_circulation_department(id),
    feedback_type   VARCHAR(30),   -- wrong_time, wrong_room, wrong_supervisor, other
    course_id       INT REFERENCES courses(id),
    section         VARCHAR(10),
    description     TEXT NOT NULL,
    priority        VARCHAR(10) DEFAULT 'normal',   -- low, normal, high
    status          VARCHAR(20) DEFAULT 'open',     -- open, in_progress, resolved, rejected
    resolved_by     INT REFERENCES users(id),
    resolved_at     TIMESTAMP,
    resolution_note TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Backend Service

```python
class DraftCirculationService:
    
    def initiate_circulation(
        self, period_id: int, deadline: datetime, initiated_by: int
    ) -> DraftCirculation:
        """
        Creates circulation + per-department review tasks.
        Sends notification to all department reviewers.
        Period moves to CIRCULATING state.
        """
        ...
    
    def submit_department_feedback(
        self, circulation_id: int, department_code: str,
        feedback_items: List[FeedbackCreate], submitted_by: int
    ) -> DraftCirculationDepartment:
        """Department reviewer submits feedback. Audited."""
        ...
    
    def close_circulation(
        self, circulation_id: int, closed_by: int
    ) -> DraftCirculation:
        """
        Admin closes circulation (deadline reached or all submitted).
        Period moves to FEEDBACK_COLLECTED state.
        """
        ...
    
    def get_circulation_summary(self, circulation_id: int) -> dict:
        """
        Returns: total depts, submitted count, open issues, 
        resolved issues, pending issues
        """
        ...
    
    def resolve_feedback_item(
        self, feedback_id: int, resolution: str, resolved_by: int
    ) -> DraftCirculationFeedback:
        """Mark a feedback item resolved. Audited."""
        ...
```

### Router

```python
POST /api/draft-circulation/{period_id}/initiate
GET  /api/draft-circulation/{period_id}/status
POST /api/draft-circulation/{circulation_id}/feedback
GET  /api/draft-circulation/{circulation_id}/feedback
PATCH /api/draft-circulation/feedback/{feedback_id}/resolve
POST /api/draft-circulation/{circulation_id}/close
```

### Frontend

New component: `WorkflowDraftCirculation.tsx`
- List of departments with status badges (pending/submitted/acknowledged)
- Issue count per department
- Feedback item list with resolution status
- Admin can mark items resolved inline

---

## 5. Post-Exam Review Module

### Purpose
After all exams in a period are complete, collect and summarize:
- Incident reports from supervisors
- Issues with rooms, students, papers
- Recommendations for improvement

### Database Schema

```sql
CREATE TABLE post_exam_incident (
    id              SERIAL PRIMARY KEY,
    period_id       INT NOT NULL REFERENCES exam_period(id),
    schedule_id     INT REFERENCES exam_schedule(id),    -- optional: specific exam slot
    reported_by     INT NOT NULL REFERENCES users(id),
    incident_type   VARCHAR(30) NOT NULL,
    -- Types: student_absent, late_arrival, paper_shortage, room_issue,
    --        supervisor_conflict, suspected_cheating, student_complaint,
    --        equipment_failure, other
    severity        VARCHAR(10) DEFAULT 'normal',        -- low, normal, high, critical
    title           VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    resolution      TEXT,
    resolved        BOOLEAN DEFAULT FALSE,
    resolved_by     INT REFERENCES users(id),
    resolved_at     TIMESTAMP,
    reported_at     TIMESTAMP DEFAULT NOW(),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE post_exam_summary (
    id              SERIAL PRIMARY KEY,
    period_id       INT NOT NULL UNIQUE REFERENCES exam_period(id),
    total_incidents INT DEFAULT 0,
    resolved_incidents INT DEFAULT 0,
    key_issues      TEXT,           -- JSON array of summarized issues
    recommendations TEXT,           -- JSON array
    submitted_by    INT REFERENCES users(id),
    submitted_at    TIMESTAMP,
    approved_by     INT REFERENCES users(id),
    approved_at     TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'draft',  -- draft, submitted, approved
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Integration with QR System

The reference document mentions QR codes on OMR envelopes link to incident reporting forms. EMS can extend the existing QR/check-in infrastructure:

```python
# Existing: exam_pickup.py generates QR tokens for paper pickup
# Extension: add QR link to post-exam incident form per schedule slot

def generate_incident_qr_token(schedule_id: int, period_id: int) -> str:
    """
    Generate a time-limited QR token linking to the incident report form
    for a specific exam slot. Printed on exam envelope.
    """
    ...
```

The QR token encodes: `schedule_id` + `period_id` + signed hash. Supervisor scans → opens pre-filled incident form in browser. No auth required (token-based access, read-only schedule data).

---

## 6. Invigilator Rule Set Integration

The optimizer currently assigns invigilators using fairness objectives. The reference document reveals additional hard constraints:

### Required Optimizer Extensions

```python
class InvigilationConstraints:
    # From reference document, Step 9
    base_per_room: int = 2
    large_room_student_threshold: int = 80
    large_per_room: int = 3
    
    # From reference document, Step 9
    allow_consecutive_sessions: bool = False
    consecutive_exception_allowed: bool = True   # can override per case
    
    # From reference document, Step 9
    senior_roles_own_dept_only: List[str] = ["dept_head", "special_professor"]
    
    # From reference document, Step 10
    co_supervisor_ratio_formula: str = "other_faculty_students / total_students"
```

These constraints should be loaded per-period from `InvigilationRuleSet` DB table, not hardcoded in `optimize_workflow.py`.

### Migration Path

1. Add `InvigilationRuleSet` model to `models.py`
2. Create migration
3. Seed default values
4. Modify `optimize_workflow.py` to load from DB instead of hardcoded values
5. Add UI in Settings/Period for admin to configure per-period

---

## 7. Exam Slot Policy Table

The reference document shows that final exam scheduling follows a deterministic mapping from class pattern to exam slot (the Special/Regular exam table).

### Integration with Optimizer

```python
class ExamSlotPolicyEngine:
    
    def get_required_slot(
        self, 
        course_id: int, 
        class_pattern: str,   # e.g. "MTh", "TuF", "We"
        class_start_time: str # e.g. "09:30"
    ) -> Optional[ExamSlotPolicy]:
        """
        Returns the required exam slot for this course based on university policy.
        Returns None if no policy applies (free assignment).
        """
        ...
    
    def load_constraints_for_optimizer(
        self, period_id: int
    ) -> List[OptimizerSlotConstraint]:
        """
        Returns hard constraints for CP-SAT optimizer:
        "course X must be scheduled in slot Y (date D, time T-T)"
        """
        ...
```

This is particularly important for final exams where university-wide conflicts must be avoided.

---

## 8. Course Exam Condition Service

```python
class CourseExamConditionService:
    
    def set_condition(
        self,
        course_id: int,
        period_id: int,
        condition: CourseExamConditionCreate,
        set_by: int
    ) -> CourseExamCondition:
        """Set exam condition flags for a course. Audited."""
        ...
    
    def get_conditions_for_period(
        self, period_id: int
    ) -> List[CourseExamCondition]:
        """Load all course conditions for optimizer constraint building."""
        ...
    
    def validate_optimizer_constraints(
        self, period_id: int
    ) -> List[ConstraintViolation]:
        """
        Pre-optimizer validation:
        - oral_only courses have oral room available
        - separate_room courses have sufficient rooms
        - no_co_exam pairs don't share time slots (check after optimization)
        """
        ...
```

---

## 9. Workflow Dependency Map

```
Period Created
    ↓
[CALENDAR_ENGINE]: Generate operation calendar
    ↓
Import Data (courses, personnel, students)
    ↓
Set Course Conditions + Exam Policy Constraints
    ↓
Book Rooms (system-assisted via optimizer preview)
    ↓
Set Staff Unavailability
    ↓
[OPTIMIZER]: Generate schedule + invigilator assignment
    |
    ↓ (using InvigilationRuleSet + ExamSlotPolicy + CourseExamConditions)
    ↓
Admin reviews optimization result
    ↓
Upload Student Names (after enrollment stabilizes)
    ↓
[DRAFT_CIRCULATION]: Send to departments
    ↓
Collect department feedback
    ↓
Apply revisions
    ↓
[APPROVAL_WORKFLOW]: Admin → ESQ → Secretary
    ↓
Generate Documents (orders, OMR, attendance)
    ↓
Announce schedule (public endpoint live)
    ↓
[EXAM_DAYS]: QR check-in + pickup verification
    ↓
[POST_EXAM]: Collect incidents
    ↓
Generate post-exam summary
    ↓
Submit to committee
    ↓
[TERM_CLOSE]: Period → LOCKED
```

---

## 10. Implementation Roadmap

### Phase 4 — Sprint 1 (After current Phase 3 completion)
- `ExamOperationCalendar` DB + service + basic router
- `InvigilationRuleSet` DB model + optimizer integration

### Phase 4 — Sprint 2
- `CourseExamCondition` DB + service + router + UI
- `ExamSlotPolicyTable` DB + integration with optimizer

### Phase 5
- `DraftCirculationService` + router + frontend
- `PostExamIncidentService` + QR token extension
- Workload calendar view (frontend component)

### Phase 6
- Public exam lookup API
- Notification engine (email)
- Co-supervisor count calculation service
- Full workflow dependency enforcement (gate transitions on task completion)

---

## 11. Architecture Rules

- All new services extend `backend/services/` (never add to routers directly)
- All mutations are audit logged via `audit_service.py`
- All new models follow existing SQLAlchemy patterns in `models.py`
- All new endpoints use `permissions.py` guards
- PDPA: no personal student data exposed through operational workflow endpoints
- DRY: reuse existing `ExamPeriod`, `User`, `AuditLog` models; don't duplicate
