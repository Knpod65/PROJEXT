# Exam Operation Calendar Engine
## Design Specification

**Date:** 2026-05-12  
**Derived from:** CMU Faculty of Humanities operational manual Table 4.1 (pp. 27–28)  
**Status:** Proposed — not yet implemented

---

## 1. Problem Statement

The reference document defines a precise monthly activity calendar covering all exam operations across 3 semesters. Currently, EMS has:

- `ExamPeriod` with start/end dates
- Term lifecycle (draft/active/archived/locked)
- No planned activity deadlines
- No cross-task dependency tracking
- No automated reminders for operational milestones

This means administrators rely on institutional memory and paper calendars to know when to perform which tasks. This is a single point of failure and a source of missed deadlines.

---

## 2. Design Goals

1. Replace paper/mental calendar with a configurable digital operation calendar
2. Each activity type has a deadline relative to semester start
3. Deadlines auto-generate per exam period based on template
4. Notification engine fires alerts when deadlines approach
5. Activity completion is tracked and audited
6. Calendar is configurable — institutions with different timelines can customize
7. Do NOT hardcode CMU-specific dates — use relative offsets from semester start

---

## 3. Database Schema

```sql
-- Template: defines activity types and their relative timing
CREATE TABLE exam_operation_activity_type (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(50) UNIQUE NOT NULL,    -- e.g. 'SET_CENTRAL_SCHEDULE'
    name_th         VARCHAR(200) NOT NULL,
    name_en         VARCHAR(200),
    description     TEXT,
    default_offset_days  INT NOT NULL,              -- days from semester_start
    deadline_offset_days INT,                       -- days from semester_start (can differ from start)
    owner_roles     VARCHAR(200),                   -- comma-separated roles
    depends_on      VARCHAR(200),                   -- comma-separated activity codes
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Per-period calendar: instantiated from template when period is created
CREATE TABLE exam_operation_calendar (
    id              SERIAL PRIMARY KEY,
    period_id       INT NOT NULL REFERENCES exam_period(id),
    activity_type_id INT NOT NULL REFERENCES exam_operation_activity_type(id),
    planned_start   DATE NOT NULL,
    planned_deadline DATE NOT NULL,
    actual_start    DATE,
    actual_end      DATE,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, completed, overdue, skipped
    completed_by    INT REFERENCES users(id),
    completed_at    TIMESTAMP,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Notifications: fired by deadline engine
CREATE TABLE exam_operation_notification (
    id              SERIAL PRIMARY KEY,
    calendar_id     INT NOT NULL REFERENCES exam_operation_calendar(id),
    notification_type VARCHAR(30),                  -- approaching, overdue, completed
    fire_at         TIMESTAMP NOT NULL,
    fired_at        TIMESTAMP,
    recipients      TEXT,                           -- JSON array of user_ids or roles
    message         TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

## 4. Activity Type Seed Data (CMU Humanities Template)

Based on Table 4.1 of the reference document:

```python
ACTIVITY_TYPES = [
    # Code, name_th, offset_days (from sem start), deadline_offset, depends_on
    ("SET_CENTRAL_SCHEDULE",  "กำหนดตารางสอบกลางภาค",   -14,  -7,   None),
    ("PREPARE_DATA",          "เตรียมข้อมูล",             -14,  -7,   "SET_CENTRAL_SCHEDULE"),
    ("CREATE_PROFILE",        "สร้างโปรไฟล์/นำข้อมูลเข้า", 7,   21,  "PREPARE_DATA"),
    ("SET_COURSE_CONDITIONS", "กำหนดเงื่อนไขกระบวนวิชา",   7,   21,  "CREATE_PROFILE"),
    ("CHANGE_EXAM_STATUS",    "เปลี่ยนสถานะการสอบ",        14,  35,  "SET_COURSE_CONDITIONS"),
    ("BOOK_ROOMS",            "จัดห้องสอบ",               14,  35,  "SET_COURSE_CONDITIONS"),
    ("UPLOAD_ROOMS",          "กรอกข้อมูลห้องสอบในระบบ",  21,  70,  "BOOK_ROOMS"),
    ("REQUEST_LEAVE_DATA",    "ขอข้อมูลการลา",            -14,  -7,  None),
    ("ASSIGN_SUPERVISORS",    "จัดกรรมการคุมสอบ",          21,  35,  "BOOK_ROOMS"),
    ("CALC_CO_SUPERVISORS",   "คำนวณกรรมการคุมสอบร่วม",   21,  35,  "ASSIGN_SUPERVISORS"),
    ("UPLOAD_SUPERVISORS",    "กรอกรายชื่อกรรมการคุมสอบ", 21,  70,  "ASSIGN_SUPERVISORS"),
    ("CHECK_WORKLOAD",        "ตรวจสอบภาระงานคุมสอบ",      21,  70,  "UPLOAD_SUPERVISORS"),
    ("MANAGE_CO_SUPERVISORS", "จัดกรรมการคุมสอบร่วม",      21,  70,  "CALC_CO_SUPERVISORS"),
    ("UPLOAD_STUDENTS",       "นำข้อมูลนักศึกษาเข้าระบบ", 21,  70,  "BOOK_ROOMS"),
    ("CIRCULATE_DRAFT",       "เวียนร่างตารางสอบ",         56,  63,  "UPLOAD_STUDENTS"),
    ("REVISE_SCHEDULE",       "เปลี่ยนแปลงร่างตารางสอบ",   63,  70,  "CIRCULATE_DRAFT"),
    ("GENERATE_DOCUMENTS",    "ออกรายงาน/เอกสาร",          70,  77,  "REVISE_SCHEDULE"),
    ("SEARCH_VERIFICATION",   "การสืบค้น",                  77,  90,  "GENERATE_DOCUMENTS"),
    ("POST_EXAM_SUMMARY",     "สรุปผลการดำเนินการสอบ",     120, 130, "SEARCH_VERIFICATION"),
]
```

---

## 5. Backend Service Design

### File: `backend/services/calendar_service.py`

```python
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
import models

class ExamOperationCalendarService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_calendar_for_period(
        self, 
        period_id: int, 
        semester_start: date,
        template_codes: Optional[List[str]] = None
    ) -> List[models.ExamOperationCalendar]:
        """
        Instantiate activity calendar from templates for a given period.
        Called when period transitions from draft → active.
        """
        ...
    
    def get_period_calendar(self, period_id: int) -> List[models.ExamOperationCalendar]:
        """Return full activity calendar for a period, ordered by planned_start."""
        ...
    
    def mark_activity_complete(
        self, 
        calendar_id: int, 
        completed_by: int,
        notes: Optional[str] = None
    ) -> models.ExamOperationCalendar:
        """Mark an activity as completed. Audit logged."""
        ...
    
    def get_overdue_activities(self, period_id: int) -> List[models.ExamOperationCalendar]:
        """Return activities past their deadline and not completed."""
        ...
    
    def schedule_notifications(self, period_id: int) -> List[models.ExamOperationNotification]:
        """
        Generate notification records for approaching/overdue deadlines.
        Run by scheduler (CronJob or FastAPI background task).
        """
        ...
    
    def get_dashboard_summary(self, period_id: int) -> dict:
        """
        Returns:
          - total activities
          - completed count
          - overdue count  
          - upcoming (next 7 days)
          - completion percentage
        """
        ...
```

---

## 6. Router Design

### File: `backend/routers/operation_calendar.py`

```python
GET  /api/operation-calendar/{period_id}          # Full calendar
GET  /api/operation-calendar/{period_id}/summary   # Dashboard summary
POST /api/operation-calendar/{period_id}/generate  # Generate from template (admin)
PATCH /api/operation-calendar/{calendar_id}/complete  # Mark complete
GET  /api/operation-calendar/templates             # List activity type templates
POST /api/operation-calendar/templates             # Create/update template (admin)
GET  /api/operation-calendar/{period_id}/overdue   # Overdue activities
```

---

## 7. Frontend Component Design

### `WorkflowCalendarView.tsx` (extend existing)

The existing `WorkflowCalendarView.tsx` component should be extended to show:

1. **Timeline view:** Gantt-style horizontal bar chart (dates × activities)
2. **Status badges:** pending (gray), in_progress (blue), completed (green), overdue (red)
3. **Dependency arrows:** Visual linking between dependent activities
4. **Quick actions:** Mark complete, add notes, view details
5. **Filter by:** status, owner role, time range

New page: `pages/OperationCalendar.tsx`  
Role access: Admin, ESQ, Secretary (read); Admin (write)

---

## 8. Integration with Term Lifecycle

When `ExamPeriod` transitions from `draft → active`:
1. `calendar_service.generate_calendar_for_period()` is called automatically
2. Calendar entries are created with computed dates based on `semester_start`
3. Notification schedule is generated
4. Admin sees calendar immediately on dashboard

When `ExamPeriod` transitions to `locked`:
- Calendar is frozen (no more updates)
- Final completion state is preserved for historical reference

---

## 9. Notification Engine

The notification engine runs as a scheduled task (FastAPI `BackgroundTasks` or APScheduler):

```
Daily at 08:00:
  For each active period:
    For each calendar entry with planned_deadline within 7 days and status=pending:
      Fire "approaching" notification → admin + role owners
    For each calendar entry with planned_deadline < today and status=pending:
      Fire "overdue" notification → admin + role owners + department head
```

Notification delivery: initially email (using existing `email_notifications.py`). Future: in-app notification bell.

---

## 10. PDPA & Audit Considerations

- Calendar activities are operational metadata only — no personal student data
- `mark_activity_complete` is audit logged (who marked, when, notes)
- Notification recipients are role-based, not individual student data
- Export of calendar (PDF) contains no personal data — just activity schedule

---

## 11. Configuration

All timing offsets are configurable via `exam_operation_activity_type` table:

```
# Institution-specific timing can be adjusted without code changes
# Example: if another faculty has shorter semester, offset_days can be compressed
```

Admins can:
- Adjust planned dates per period (override template)
- Add institution-specific activities
- Deactivate activities not relevant to their workflow

---

## 12. Implementation Priority

**Phase 4, Sprint 1** (next major sprint):
1. Create DB models (`ExamOperationActivityType`, `ExamOperationCalendar`, `ExamOperationNotification`)
2. Run migration
3. Seed activity types from CMU template
4. Create `calendar_service.py`
5. Create `operation_calendar.py` router
6. Wire into period lifecycle (`period.py` on status change)
7. Create `OperationCalendar.tsx` page (basic list view)

**Phase 4, Sprint 2:**
1. Notification engine (email-based)
2. Gantt timeline view component
3. Dashboard integration (overdue count widget)
4. Admin template management UI
