# Event Outbox Foundation
## EMS Academic Operations Platform
**Date:** 2026-05-14
**Phase:** D1.2

---

## 1. Purpose

The transactional outbox pattern ensures that domain events are never lost even if
the event bus is temporarily unavailable. Instead of emitting events directly to the
bus inside a DB transaction (which risks partial failure), the event is first written
to an "outbox" table in the same transaction. A relay process then picks up staged
events and dispatches them.

This document describes the foundation layer implemented in D1.2 and what is
deferred to a future DB-backed implementation.

---

## 2. Current Implementation (D1.2)

**File:** `backend/services/event_outbox_service.py`

The current implementation is an **in-memory outbox** — a module-level thread-safe
list protected by a `threading.Lock`. It provides the full API surface for the
outbox pattern without any DB schema changes.

### API

| Function | Purpose |
|---|---|
| `build_outbox_record(envelope)` | Serialize EventEnvelope → outbox record dict |
| `stage_event(envelope)` | Add to staging list, return record |
| `list_staged_events()` | Return copy of all staged records |
| `clear_staged_events()` | Empty the staging list |
| `mark_event_dispatched(event_id)` | Set status=DISPATCHED + dispatched_at |
| `get_staged_event(event_id)` | Retrieve a single record by event_id |

### Outbox Record Shape

```python
{
    "event_id":      str,            # from EventEnvelope.event_id
    "event_type":    str,
    "domain":        str,
    "aggregate_type": str | None,
    "aggregate_id":  str | None,
    "payload_json":  str,            # json.dumps(payload, sort_keys=True)
    "metadata_json": str,            # json.dumps(metadata, sort_keys=True)
    "status":        "STAGED" | "DISPATCHED" | "FAILED",
    "created_at":    str,            # UTC ISO at stage time
    "dispatched_at": str | None,     # UTC ISO when dispatched, or None
}
```

---

## 3. What Is Deferred

The following requires DBA/IT approval and a DB migration before it can be
implemented:

### DB Outbox Table

```sql
CREATE TABLE event_outbox (
    event_id       VARCHAR(36)  PRIMARY KEY,
    event_type     VARCHAR(128) NOT NULL,
    domain         VARCHAR(64)  NOT NULL,
    aggregate_type VARCHAR(128),
    aggregate_id   VARCHAR(128),
    payload_json   TEXT         NOT NULL,
    metadata_json  TEXT         NOT NULL,
    status         VARCHAR(16)  NOT NULL DEFAULT 'STAGED',
    created_at     TIMESTAMPTZ  NOT NULL,
    dispatched_at  TIMESTAMPTZ
);

CREATE INDEX idx_event_outbox_status ON event_outbox(status);
CREATE INDEX idx_event_outbox_created_at ON event_outbox(created_at);
```

### Outbox Relay Process

A background worker (periodic task or Celery job) that:
1. Queries `WHERE status='STAGED' ORDER BY created_at`
2. Attempts to dispatch each event to the InMemoryEventBus (or a real message broker)
3. Updates `status='DISPATCHED'` on success, `status='FAILED'` on repeated failure
4. Supports retry with exponential backoff

### Transactional Write

The current `execute_with_audit()` in `transaction_audit_service.py` emits to the
in-memory bus post-commit. When the DB outbox table is available, the flow changes:

```
BEGIN TRANSACTION
  → mutation_fn(db)
  → audit_mutation(db, ...)
  → INSERT INTO event_outbox (staged record)
COMMIT
→ relay worker picks up and dispatches later
```

---

## 4. Integration with D1.1 EventEnvelope

The outbox works exclusively with `EventEnvelope` objects from
`events/event_envelope.py`. The `build_outbox_record()` function serializes the
envelope's payload and metadata to JSON strings for storage.

The `EventEnvelope` fields `aggregate_type` and `aggregate_id` map directly to
the outbox table columns, enabling future read-model projections and aggregate
event replay.

---

## 5. Security Notes

- `payload_json` and `metadata_json` are serialized from already-sanitized payloads
  (the `EventEnvelope` factory calls `sanitize_event_payload()` before storing).
- The outbox table itself should be append-only with restricted UPDATE/DELETE grants.
- Dispatched records should be retained for the `retention_hint` period from the
  envelope before archival.
