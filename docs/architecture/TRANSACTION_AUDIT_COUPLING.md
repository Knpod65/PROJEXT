# Transaction + Audit Coupling Foundation

**Status:** Implemented — Phase 2C  
**Date:** 2026-05-14  
**Files:** `backend/services/unit_of_work.py`, `backend/services/audit_event_service.py`

---

## Purpose

1. **`UnitOfWork`** — Centralize commit/rollback ownership. Services call
   `db.flush()` (visible within the transaction); the UoW context manager
   owns the final `commit()` or `rollback()`.

2. **`audit_event_service`** — Couple an audit log write (DB) with a domain
   event emission (in-memory bus, Phase 1B) in a single function call, so the
   audit trail and event stream stay consistent.

---

## UnitOfWork

### Pattern

```python
from services.unit_of_work import UnitOfWork, atomic

# Class-based (access uow.db inside)
with UnitOfWork(db) as uow:
    service.create_something(uow.db)
# db.commit() called automatically on clean exit
# db.rollback() called automatically on any exception (then re-raises)

# Functional shorthand
with atomic(db) as session:
    session.add(new_record)
```

### Contract

| Exit condition | Action |
|---|---|
| No exception | `db.commit()` |
| `EMSDomainError` | `db.rollback()` + re-raise |
| Any other exception | `db.rollback()` + re-raise |

The UoW **never swallows exceptions**. `__exit__` always returns `False`.

### Additive Safety

Existing routers that call `db.commit()` directly continue to work unchanged.
The UoW is opt-in. Do not mass-migrate existing routers.

---

## audit_event_service

### API

```python
from services.audit_event_service import record_mutation_with_event, record_event_with_audit

# For CREATE/UPDATE/DELETE operations
record_mutation_with_event(
    db, actor, "CREATE", "schedules",
    record_id=schedule.id,
    old_values=None,
    new_values={"exam_date": "2026-10-01"},
    session_id=request_session_id,
    correlation_id=request_id,
)

# For named events (login, export, etc.)
record_event_with_audit(
    db, actor, "USER_LOGIN", "Admin logged in",
    domain="auth",
    session_id=None,
)
```

### Execution Order

1. `audit_service.audit_mutation()` → writes to DB (existing pattern)
2. `event_service.emit()` → publishes to in-memory bus (Phase 1B)

If the DB write fails, the event is never emitted (correct).  
If the emit fails, the exception is **swallowed** — event bus is best-effort in Phase 1B.

---

## Migration Guide for Existing Routers

Do **not** mass-migrate existing routers in this phase. Instead, apply the
pattern to new endpoints only:

1. Replace `db.commit()` at end of handler with `with atomic(db): ...`
2. Replace `log_action(...)` / `audit_mutation(...)` calls with `record_mutation_with_event(...)`

A router that uses both patterns correctly:

```python
from services.unit_of_work import atomic
from services.audit_event_service import record_mutation_with_event

@router.post("/api/schedule/")
async def create_schedule(data: ScheduleIn, db: Session = Depends(get_db), user = Depends(require_admin)):
    with atomic(db) as session:
        sched = models.ExamSchedule(**data.dict())
        session.add(sched)
        session.flush()  # sched.id is now available
        record_mutation_with_event(
            session, user, "CREATE_SCHEDULE", "exam_schedules",
            record_id=sched.id,
            new_values=data.dict(),
        )
    return sched
```

---

## Test Coverage

22 tests: UnitOfWork commit/rollback, re-raise propagation, `atomic()` shorthand,
`record_mutation_with_event()` audit + emit calls, emit-failure swallowed,
`record_event_with_audit()` domain pass-through.
