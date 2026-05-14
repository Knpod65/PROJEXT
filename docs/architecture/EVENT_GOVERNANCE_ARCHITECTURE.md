# Event Governance Architecture
## EMS Academic Operations Platform — Enterprise Maturity Phases T2–T3
**Date:** 2026-05-14

---

## 1. Purpose

This document describes the typed event infrastructure, event dispatcher, and
transaction audit coupling that govern how domain events are published, routed,
and persisted in the EMS system.

---

## 2. Architecture Overview

```
Mutation (e.g., approve override)
    │
    ▼
execute_with_audit(db, mutation_fn=..., event_type=..., ...)
    │
    ├── mutation_fn(db)          ← runs in transaction
    ├── audit_mutation(db, ...)  ← writes audit row, same transaction
    ├── db.commit()
    └── event_service.emit(...)  ← post-commit, best-effort, exceptions swallowed
                │
                ▼
        InMemoryEventBus.publish(event)
                │
                ▼
        EventDispatcher._route(event)
                │
        ┌───────┴──────────────┐
        ▼                      ▼
  handler_A(event)       handler_B(event)
```

---

## 3. Typed Event Domains

### 3.1 EventDomain (base_event.py)

```python
class EventDomain(str, Enum):
    OPTIMIZATION = "optimization"
    GOVERNANCE = "governance"
    AUDIT = "audit"
    WORKFLOW = "workflow"
    SUBMISSION = "submission"
    SYSTEM = "system"
```

### 3.2 EventSeverity

```python
class EventSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"
```

### 3.3 GovernanceEventType (governance_events.py)

11 values: GOVERNANCE_DECISION_CREATED, GOVERNANCE_DECISION_UPDATED,
OVERRIDE_REQUESTED, OVERRIDE_APPROVED, OVERRIDE_REJECTED, GOVERNANCE_ESCALATED,
ESCALATION_RESOLVED, REVIEW_ASSIGNED, REVIEW_COMPLETED, AUTO_APPROVED,
AUTO_APPROVAL_BLOCKED

### 3.4 AuditEventType (audit_events.py)

14 values: MUTATION_COMMITTED, MUTATION_ROLLED_BACK, SENSITIVE_ACCESS,
UNAUTHORIZED_ACCESS_ATTEMPT, EXPORT_INITIATED, EXPORT_COMPLETED, TOKEN_ISSUED,
TOKEN_REVOKED, TOKEN_EXPIRED, SESSION_STARTED, SESSION_ENDED, SESSION_EXPIRED,
RETENTION_CLEANUP_INITIATED, RETENTION_CLEANUP_COMPLETED

---

## 4. EventDispatcher

`services/event_dispatcher_service.py`

```python
class EventDispatcher:
    def __init__(self, bus: InMemoryEventBus) -> None
    def register(self, event_type: str, handler: Callable) -> None
    def on(self, event_type: str) -> Callable           # decorator
    def dispatch(self, event: DomainEvent) -> None
    def dispatch_many(self, events: Iterable[DomainEvent]) -> None
    def handler_count(self, event_type: str) -> int
    def registered_event_types(self) -> list[str]

dispatcher = EventDispatcher(event_bus)  # module-level singleton
```

**Design invariants:**
- Subscribes ONE routing callback to the bus. All subsequent events are routed via that callback.
- Handler exceptions are always swallowed — dispatcher never crashes the bus.
- Thread-safe: `threading.Lock` protects the `_handlers` dict.
- Unregistered event types are silently ignored (no-op).

**Usage:**
```python
from services.event_dispatcher_service import dispatcher

@dispatcher.on("GOVERNANCE_ESCALATED")
def handle_escalation(event: DomainEvent) -> None:
    ...
```

---

## 5. execute_with_audit

`services/transaction_audit_service.py`

```python
def execute_with_audit(
    db: Session,
    *,
    mutation_fn: Callable[[Session], Any],
    actor: Any,                   # User ORM object
    audit_action: str,
    audit_table_name: str,
    audit_record_id: int | None = None,
    audit_old_values: dict | None = None,
    audit_new_values: dict | None = None,
    event_type: str,
    event_domain: str,
    event_payload: dict | None = None,
    session_id: str | None = None,
    correlation_id: str | None = None,
    request: Any = None,
) -> Any
```

**Transaction protocol:**
1. `result = mutation_fn(db)` — runs inside transaction
2. `audit_mutation(db, actor, audit_action, ...)` — same transaction
3. `db.commit()`
4. `event_service.emit(...)` — post-commit, best-effort
5. On any exception: `db.rollback(); raise`

**Guarantee:** Domain event is NEVER emitted unless the database commit succeeds.

---

## 6. InMemoryEventBus (existing)

- Ring buffer, max 500 events
- Thread-safe via `threading.Lock`
- `publish(event)` → calls all subscribers
- `subscribe(callback)` → registers a callback for all events
- Singleton: `from services.event_service import event_bus`

The EventDispatcher wraps this bus — it does NOT replace it. Existing code that
calls `emit()` or `event_bus.publish()` continues to work unchanged.

---

## 7. Files

| File | Role |
|---|---|
| `events/base_event.py` | EventDomain, EventSeverity, BaseEventProtocol |
| `events/governance_events.py` | GovernanceEventType enum |
| `events/audit_events.py` | AuditEventType enum |
| `events/optimization_events.py` | OptimizationEventType enum |
| `services/event_dispatcher_service.py` | EventDispatcher class + module singleton |
| `services/event_service.py` | InMemoryEventBus, event_bus singleton, emit() |
| `services/transaction_audit_service.py` | execute_with_audit(), execute_readonly_with_event() |
| `tests/test_event_dispatcher_service.py` | 16 tests |
| `tests/test_transaction_audit_service.py` | 15 tests |
