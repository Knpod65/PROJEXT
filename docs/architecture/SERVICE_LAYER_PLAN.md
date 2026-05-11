# Service Layer Plan
## EMS — Extracting Business Logic from Route Handlers

> **Audience:** Backend engineers doing Phase 3 renovation work
> **Scope:** Technical specification for the service layer — contracts, exception hierarchy, module designs, migration pattern
> **Reference for good patterns:** `backend/term_lifecycle.py` — exemplary pure-function service code with zero HTTP concerns
> **Anti-examples (what to fix):** `backend/routers/schedule.py` (1087 lines), `backend/routers/submissions.py` (911 lines), `backend/routers/optimize_workflow.py` (1331 lines)

---

## 1. Why a Service Layer Is Needed

Evidence from direct codebase measurement:

| Router | Lines | Problem |
|--------|-------|---------|
| `optimize_workflow.py` | 1331 | Mixes: user CRUD, unavailability CRUD, workflow session management, CP-SAT optimizer, signing logic |
| `schedule.py` | 1087 | Mixes: CP-SAT optimizer, CRUD, conflict detection, room assignment, paper distribution, dept filtering |
| `submissions.py` | 911 | Mixes: 4-step wizard state machine, print priority, version snapshots, print queue, PDF tokens |
| `exports.py` | 26.8 KB | Duplicates `_resolve_period()` that also exists in `pdf.py` |
| `imports.py` | 33 KB | Legacy import logic mixed with validation |

Route handlers should be thin HTTP adapters: parse input → call service → format response.
Business logic, domain validation, and data access patterns belong in services.

**Reference implementation:** `term_lifecycle.py` shows the target style:
- Pure Python functions, no FastAPI imports
- No `HTTPException` (raises `ValueError` instead; router translates)
- Accepts `db: Session` as explicit argument
- Getters do not mutate; mutation functions are clearly named
- All timestamps use `datetime.now(timezone.utc)`

---

## 2. Service Layer Contract

All service functions must follow these rules without exception:

```python
# CORRECT — service function signature
def get_submission(
    db: Session,
    submission_id: int,
    user: models.User,
    *,
    create_if_missing: bool = False,
) -> models.ExamSubmission:
    ...  # raises EMSDomainError subclass, never HTTPException
    ...  # raises ValueError for invalid input
    ...  # never calls db.commit() — caller owns the transaction

# WRONG — never do this in a service
def bad_service(db: Session, submission_id: int):
    from fastapi import HTTPException
    raise HTTPException(status_code=404, ...)  # ← FORBIDDEN in service layer
    db.commit()                                 # ← FORBIDDEN in service layer
```

**Checklist for any new service function:**
- [ ] No `from fastapi import ...` imports
- [ ] No `Depends(...)` usage
- [ ] No `HTTPException` raised — use domain exceptions instead
- [ ] Accepts `db: Session` as first positional argument
- [ ] Never calls `db.commit()` — caller commits
- [ ] May call `db.flush()` for intermediate persistence within a request
- [ ] Returns typed objects, never raw dicts
- [ ] Raises specific `EMSDomainError` subclass, not bare `Exception`

---

## 3. Exception Hierarchy

Create `backend/services/exceptions.py`:

```python
class EMSDomainError(Exception):
    """Base class for all EMS domain exceptions."""
    pass

class ResourceNotFoundError(EMSDomainError):
    """Requested resource does not exist."""
    def __init__(self, resource: str, id: int | str):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} id={id} not found")

class PermissionDeniedError(EMSDomainError):
    """Caller lacks permission for this operation."""
    def __init__(self, reason: str = ""):
        super().__init__(reason or "Permission denied")

class TermLockedError(EMSDomainError):
    """Operation blocked because the exam period is locked."""
    pass

class ValidationError(EMSDomainError):
    """Domain-level validation failed (not Pydantic input validation)."""
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"{field}: {message}")

class ConflictError(EMSDomainError):
    """Operation would create a conflicting state (e.g., duplicate slot)."""
    pass
```

**Router translation pattern** (in every router's exception handler):
```python
try:
    result = submission_service.approve(db, submission_id, current_user)
    db.commit()
    return result
except ResourceNotFoundError as e:
    raise HTTPException(404, str(e))
except PermissionDeniedError as e:
    raise HTTPException(403, str(e))
except TermLockedError:
    raise HTTPException(409, term_lifecycle.LOCKED_TERM_MESSAGE)
except ValidationError as e:
    raise HTTPException(422, str(e))
except ConflictError as e:
    raise HTTPException(409, str(e))
```

---

## 4. Transaction Boundary Rule

**Rule: `db.commit()` lives only in route handlers. Services use `db.flush()`.**

```
Route Handler                Service
─────────────────────────    ─────────────────────────
try:                         def create_submission(...):
  result = svc.create(...)     sub = models.ExamSubmission(...)
  db.commit()                  db.add(sub)
  return result                db.flush()          # ← assigns sub.id, no commit
except ...:                    version = models.ExamSubmissionVersion(...)
  db.rollback()                db.add(version)
  raise HTTPException(...)     return sub
```

Rationale: if the router needs to perform multiple service calls in one request, they must be
atomic. The router is the only layer with enough context to decide when to commit.

---

## 5. Proposed Service Modules

### `backend/services/__init__.py`
Empty package marker.

---

### `backend/services/exceptions.py`
Domain exception hierarchy (see Section 3).

---

### `backend/services/submission_service.py`

Extract from `backend/routers/submissions.py`:

| Function to extract | Current location | Lines |
|---------------------|-----------------|-------|
| `_get_submission(db, section_id, exam_type, create_if_missing)` | submissions.py ~line 55 | ~25 lines |
| `_save_version(db, sub)` | submissions.py ~line 106 | ~14 lines |
| `_snapshot_submission(sub)` | submissions.py ~line 87 | ~17 lines |
| `_get_print_priority(num_students)` | submissions.py ~line 121 | ~14 lines |
| `_upsert_print_queue_job(db, sub, period)` | submissions.py ~line 137 | ~20 lines |
| Approval state transition logic | submissions.py approval handler | ~30 lines |

**Service API sketch:**
```python
# backend/services/submission_service.py

def get_or_create_submission(
    db: Session, section_id: int, exam_type: str, *,
    user: models.User, create_if_missing: bool = False
) -> models.ExamSubmission: ...

def save_version(db: Session, submission: models.ExamSubmission) -> models.ExamSubmissionVersion: ...

def get_print_priority(num_students: int) -> str:
    """Thresholds from config.settings.PRINT_PRIORITY_HIGH/MEDIUM/LOW."""
    ...

def upsert_print_queue_job(
    db: Session, submission: models.ExamSubmission, period: models.ExamPeriod
) -> models.PrintQueueJob: ...

def approve_submission(
    db: Session, submission: models.ExamSubmission, approver: models.User
) -> models.ExamSubmission: ...

def reject_submission(
    db: Session, submission: models.ExamSubmission, actor: models.User, reason: str
) -> models.ExamSubmission: ...
```

**After extraction:** `submissions.py` router drops from 911 → ~300 lines.

---

### `backend/services/schedule_service.py`

Extract from `backend/routers/schedule.py`:

| Function to extract | Notes |
|---------------------|-------|
| `_build_schedule_query(db, filters, user)` | Consolidate dept filtering with `permissions.get_dept_filter()` |
| `_load_unavailability_maps(db, period_id)` | Pure data query |
| Conflict detection logic | Check room/staff double-booking |
| Grouped schedule formatting | `_sch_to_dict()` equivalent |

⚠️ **CP-SAT optimizer extraction is last** (see Risk section). Extract it only after simpler
functions are proven and after transaction boundaries are explicitly designed.

**After extraction:** `schedule.py` drops from 1087 → ~400 lines.

---

### `backend/services/user_service.py`

Extract from `backend/routers/optimize_workflow.py` (user management section, lines ~87–147)
and `backend/routers/users.py`:

| Function | Notes |
|----------|-------|
| `create_user(db, data)` | Username/email uniqueness check + hash_password |
| `update_user(db, user_id, data)` | Role coercion via `permissions.coerce_user_role()` |
| `deactivate_user(db, user_id)` | Soft delete |

**After extraction:** User CRUD in `optimize_workflow.py` is removed (it does not belong there).

---

### `backend/services/period_service.py`

Thin wrapper over `term_lifecycle.py` that adds export-context resolution:

```python
# backend/services/period_service.py

from term_lifecycle import find_period, get_active_period, ensure_period_record_editable

def resolve_export_period(
    db: Session,
    semester: str | None,
    academic_year: str | None,
    exam_type: str | None,
) -> models.ExamPeriod:
    """
    Canonical period resolver for exports.
    Replaces duplicated _resolve_period() in exports.py and pdf.py.
    """
    if semester and academic_year:
        period = find_period(db, academic_year, semester, exam_type)
        if period:
            return period
        raise ResourceNotFoundError("ExamPeriod", f"{academic_year}/{semester}")
    active = get_active_period(db)
    if active:
        return active
    raise ResourceNotFoundError("ExamPeriod", "active")
```

---

### `backend/services/export_service.py`

Period-aware export query builders:

```python
def get_schedule_for_export(
    db: Session, period: models.ExamPeriod, dept_filter: str | None
) -> list[models.ExamSchedule]: ...

def get_workload_summary(
    db: Session, period: models.ExamPeriod
) -> dict: ...
```

---

### `backend/services/audit_service.py`

Wrap `auth_utils.log_action()` with guaranteed context fields:

```python
# backend/services/audit_service.py

from auth_utils import log_action as _log_action
from models import User, AuditLog
from sqlalchemy.orm import Session

def record(
    db: Session,
    actor: User,
    action: str,  # Must be from ACTION_REGISTRY
    *,
    table_name: str = "",
    record_id: int | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    http_status: int = 200,
) -> AuditLog:
    """
    Guaranteed audit log write. Action name must be in ACTION_REGISTRY.
    Raises ValueError if action is unknown.
    """
    if action not in ACTION_REGISTRY:
        raise ValueError(f"Unknown audit action: {action!r}. Add it to ACTION_REGISTRY.")
    return _log_action(
        db, actor=actor, action=action,
        table_name=table_name, record_id=record_id,
        old_values=old_values, new_values=new_values,
        http_status=http_status,
    )

ACTION_REGISTRY = frozenset({
    "LOGIN", "LOGOUT",
    "CREATE_USER", "UPDATE_USER", "DEACTIVATE_USER",
    "APPROVE_SUBMISSION", "REJECT_SUBMISSION", "SUBMIT_EXAM",
    "SIGN_WORKFLOW", "UNLOCK_SWAP_WINDOW",
    "CONFIRM_SWAP", "REJECT_SWAP",
    "GENERATE_EXAM_PDF", "EXPORT_SCHEDULE_PDF", "EXPORT_WORKLOAD_PDF",
    "IMPORT_COMMIT", "IMPORT_VALIDATE",
    "LOCK_PERIOD", "ARCHIVE_PERIOD",
    "GENERATE_QR", "CONFIRM_PICKUP",
    "UPDATE_ROOM", "UPDATE_USER_UNAVAILABILITY",
    # ... (full list in AUDIT_AND_EVENT_MODEL.md)
})
```

---

### `backend/services/print_service.py`

Extract print priority logic with config-driven thresholds:

```python
# backend/services/print_service.py
from config.settings import Settings

def compute_print_priority(num_students: int, settings: Settings) -> str:
    """
    Priority thresholds come from settings, not hardcode.
    Default: high≥120, medium≥70, normal≥15, low<15
    """
    if num_students >= settings.PRINT_PRIORITY_HIGH_THRESHOLD:
        return "high"
    if num_students >= settings.PRINT_PRIORITY_MEDIUM_THRESHOLD:
        return "medium"
    if num_students >= settings.PRINT_PRIORITY_NORMAL_THRESHOLD:
        return "normal"
    return "low"
```

---

## 6. Migration Pattern

Step-by-step guide for migrating any existing route handler to use a service.

**Before (existing pattern):**
```python
@router.put("/{section_id}/approve")
def approve_submission(
    section_id: int,
    exam_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    sub = db.query(models.ExamSubmission).filter(...).first()
    if not sub:
        raise HTTPException(404, "ไม่พบ submission")
    if sub.status not in ("submitted", "rejected"):
        raise HTTPException(409, "ไม่สามารถ approve ได้")
    sub.status = "approved"
    sub.approved_by = current_user.id
    sub.approved_at = datetime.now(timezone.utc)
    # save version snapshot
    version = models.ExamSubmissionVersion(...)
    db.add(version)
    log_action(db, current_user, "APPROVE_SUBMISSION", ...)
    db.commit()
    return {"status": "ok"}
```

**After (service pattern):**
```python
@router.put("/{section_id}/approve")
def approve_submission(
    section_id: int,
    exam_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    try:
        sub = submission_service.approve_submission(
            db, section_id=section_id, exam_type=exam_type, approver=current_user
        )
        audit_service.record(db, current_user, "APPROVE_SUBMISSION",
                             table_name="exam_submissions", record_id=sub.id)
        db.commit()
        return {"status": "ok", "id": sub.id}
    except ResourceNotFoundError as e:
        raise HTTPException(404, str(e))
    except ConflictError as e:
        raise HTTPException(409, str(e))
```

---

## 7. Audit Call Convention

**Old pattern (do NOT use going forward):**
```python
# Scattered inline calls in route handlers
log_action(db, current_user, "some_action")
db.commit()
```

**New pattern:**
1. Service performs the business mutation (no audit in service)
2. Router calls `audit_service.record(...)` AFTER the service call succeeds
3. Router calls `db.commit()` ONCE, covering both the mutation and the audit record
4. If service raises an exception, no commit happens → no orphaned audit records

Services do NOT call `audit_service.record()`. Routers do.

---

## 8. Phase 3 Sprint Breakdown

**Week 1 — Create foundations (no behavioral change)**
1. Create `backend/services/__init__.py`
2. Create `backend/services/exceptions.py`
3. Add `coerce_user_role()` as public function in `permissions.py`
4. Write router-level exception translation helper (reusable decorator or context manager)

**Week 2 — Extract submission_service (highest ROI, lowest risk)**
5. Create `backend/services/submission_service.py` with all functions from Section 5
6. Modify `backend/routers/submissions.py` to call services; verify behavior unchanged
7. Add unit tests in `tests/services/test_submission_service.py`

**Week 3 — Extract schedule_service (medium risk)**
8. Create `backend/services/schedule_service.py` (non-optimizer functions only)
9. Create `backend/services/period_service.py` (replaces `_resolve_period()` duplicates)
10. Update `exports.py` and `pdf.py` to use `period_service.resolve_export_period()`

**Week 4 — Extract audit + user services**
11. Create `backend/services/audit_service.py` with `ACTION_REGISTRY`
12. Audit sweep: add missing `audit_service.record()` calls in all 26 routers
13. Create `backend/services/user_service.py`; move user CRUD out of `optimize_workflow.py`

**⚠️ CP-SAT optimizer extraction — requires separate design session**
The optimizer in `schedule.py` directly manipulates SQLAlchemy model objects and has
unclear transaction boundaries. Extract it only after:
- All other schedule_service functions are proven in production
- A transaction scope design is reviewed with the team
- Seed data test passes end-to-end through the full optimizer cycle

---

## 9. Critical Risks

**Risk: Services accessing HTTPException through imported routers**
If a utility module (e.g., `exam_ownership.py`) is extracted into a service and imports
FastAPI, the service layer contract is broken. Audit all imports at extraction time.

**Risk: Implicit `db.commit()` in existing helpers**
Some existing helper functions (e.g., `_upsert_print_queue_job`) may call `db.commit()`
internally. Verify and remove before wrapping them in a service.

**Risk: CP-SAT optimizer transaction scope**
The CP-SAT optimizer assigns rooms and staff across hundreds of schedule rows in one pass.
If extraction wraps this in a service with multiple `db.flush()` calls, a partial failure
could leave the DB in an inconsistent state. Design explicit rollback semantics before
extracting the optimizer.
