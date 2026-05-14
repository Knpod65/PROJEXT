# Optimization Event Stream

**Status:** Implemented — Phase 1B  
**Date:** 2026-05-14  
**Files:** `backend/events/domain_event.py`, `backend/events/__init__.py`, `backend/services/event_service.py`

---

## Purpose

Provides a lightweight, in-memory domain event bus for the optimizer lifecycle.
Events are structured envelopes that future consumers (audit, notification,
analytics, WebSocket, report builder) can subscribe to without coupling to
the optimizer internals.

---

## Event Envelope

```python
DomainEvent(
    event_id:       str,            # UUID4 — globally unique
    event_type:     str,            # e.g. "OPTIMIZATION_STARTED"
    domain:         str,            # "optimization" | "audit" | ...
    actor_id:       int | None,     # user.id who triggered the event
    session_id:     str | None,     # workflow session correlation
    correlation_id: str | None,     # cross-service trace correlation
    payload:        dict,           # domain-specific data (no PII)
    timestamp:      str,            # ISO 8601 UTC
)
```

---

## API

```python
# Create and publish in one call
from services.event_service import emit

evt = emit(
    "GOVERNANCE_DECISION_CREATED",
    "optimization",
    actor_id=user.id,
    session_id=session.session_id,
    correlation_id=request_id,
    payload={"governance_state": "BLOCKED", "period_id": period.id},
)
# evt.event_id available for downstream correlation

# Subscribe a consumer
from services.event_service import event_bus

event_bus.subscribe(lambda e: print(e.event_type))

# Read recent events (e.g. for a WebSocket push)
recent = event_bus.recent(n=20)

# Drain all events (e.g. for batch report builder)
all_events = event_bus.drain()
```

---

## Design Decisions

| Decision | Rationale |
|---|---|
| In-memory only (Phase 1B) | No DB schema change needed; events are ephemeral in this phase |
| Ring buffer (deque maxlen=500) | Oldest events drop silently; prevents unbounded memory growth |
| Thread-safe via `threading.Lock` | FastAPI uses a thread pool; concurrent publishers are safe |
| Subscriber exceptions swallowed | A buggy analytics subscriber must never crash an optimizer run |
| Module-level singleton | One bus per process; no DI needed until persistence is added |

---

## Future Consumers

| Consumer | How to Wire |
|---|---|
| Audit persistence | `event_bus.subscribe(lambda e: audit_event(db, e))` |
| Notification hook | `event_bus.subscribe(notification_service.on_event)` |
| Analytics | `event_bus.subscribe(analytics.ingest)` |
| WebSocket push | `event_bus.subscribe(ws_manager.broadcast)` |
| Report builder | Poll `event_bus.recent()` at report generation time |

---

## No DB Persistence (Phase 1B)

Events are lost on process restart. Persistence (e.g., an `AuditEventLog` table)
requires schema migration approval and is deferred to a future phase. The bus
API is designed so adding persistence requires only a new subscriber — no
changes to emitters.

---

## Test Coverage

22 tests cover: UUID assignment, ISO timestamp, immutability, max-size eviction,
drain-clears, subscriber callbacks, subscriber-exception isolation,
module-level `emit()`, and all `make_domain_event()` parameters.
