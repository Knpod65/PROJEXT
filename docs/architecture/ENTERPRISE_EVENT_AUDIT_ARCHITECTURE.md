# Enterprise Event & Immutable Audit Architecture
## EMS Academic Operations Platform
**Date:** 2026-05-14
**Phase:** D1 — Enterprise Event & Immutable Audit Infrastructure

---

## 1. Overview

This document describes the enterprise event and audit infrastructure added in
Phase D1. All components are **pure logic** (no DB, no ORM, no HTTP) and additive
— they do not change any existing service behavior.

The existing `DomainEvent` / `InMemoryEventBus` / `EventDispatcher` infrastructure
remains unchanged. D1 adds richer envelope fields, an outbox pattern, immutable
audit records, a transaction bridge, a lifecycle timeline, and a PDPA safety policy
on top of that foundation.

---

## 2. Component Map

```
D1.1  events/event_envelope.py          — Canonical enterprise event envelope (18 fields)
D1.2  services/event_outbox_service.py  — In-memory outbox: stage/dispatch/query
D1.3  services/immutable_audit_service.py — Hashed, PII-safe audit event records
D1.4  services/transaction_event_bridge_service.py — Bundle: envelope + audit + outbox
D1.5  services/lifecycle_timeline_service.py — Mixed-source event normalization + summary
D1.6  policies/event_pdpa_policy.py     — Classify, assert, mask PII in payloads
```

Existing infrastructure (unchanged):
```
events/domain_event.py              — DomainEvent frozen dataclass (wire format)
events/base_event.py                — EventDomain, EventSeverity enums
services/event_service.py           — InMemoryEventBus singleton, emit()
services/event_dispatcher_service.py — EventDispatcher, type-based routing
services/transaction_audit_service.py — execute_with_audit() transactional pattern
services/audit_event_service.py     — Coupled DB audit row + in-memory event
```

---

## 3. Event Envelope (D1.1)

### Why a New Envelope?

`DomainEvent` is the existing wire format used throughout the codebase. It has
8 fields and remains unchanged. `EventEnvelope` adds 10 more fields for enterprise
compliance, auditability, and PDPA requirements — without modifying `DomainEvent`
or any code that uses it.

### Fields Added by EventEnvelope

| Field | Type | Purpose |
|---|---|---|
| `severity` | str | INFO / WARNING / HIGH_RISK / CRITICAL |
| `actor_role` | str\|None | Role at time of action (not in DomainEvent) |
| `causation_id` | str\|None | event_id that triggered this event |
| `aggregate_type` | str\|None | Aggregate root type (e.g. "OptimizeSession") |
| `aggregate_id` | str\|None | Aggregate root PK |
| `metadata` | dict | Operational metadata (source, env, etc.) |
| `pdpa_classification` | str | public / internal / confidential / restricted |
| `contains_pii` | bool | Explicit PII flag |
| `retention_hint` | str\|None | e.g. "7y", "90d" |
| `schema_version` | str | "1.0" (allows future migrations) |

### PII Sanitization

`create_event_envelope()` automatically sanitizes both `payload` and `metadata`
via `sanitize_event_payload()` before storing them. The following key names
(case-insensitive) are replaced with `[REDACTED]`:

```
student_name, student_id, citizen_id, national_id,
email, phone, token, qr_payload, qr_code, password, secret
```

---

## 4. Event Outbox (D1.2)

### Current Implementation

In-memory thread-safe list with full outbox API. No DB writes.

```
stage_event(envelope)         → add to staging list
list_staged_events()          → copy of all staged records
mark_event_dispatched(id)     → set status=DISPATCHED
clear_staged_events()         → empty the list
get_staged_event(id)          → single record lookup
```

### Deferred: DB Outbox Table

When DBA approves a migration:

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
```

See `EVENT_OUTBOX_FOUNDATION.md` for the full DDL and relay process design.

---

## 5. Immutable Audit Event Model (D1.3)

`build_immutable_audit_event()` produces a tamper-evident audit record:

- `before_hash` / `after_hash`: SHA-256 of PII-sanitized JSON (sort_keys=True)
- `immutable: True`: structural marker — storage layer must not UPDATE or DELETE
- PII sanitization applied to snapshots before hashing and storage

See `IMMUTABLE_AUDIT_EVENT_MODEL.md` for the full design.

---

## 6. Transaction Audit Event Bridge (D1.4)

`build_transaction_event_bundle()` composes all three components into one call:

```python
bundle = build_transaction_event_bundle(
    event_type="SCHEDULE_PUBLISHED",
    domain="governance",
    audit_action="SCHEDULE_PUBLISHED",
    resource_type="OptimizeSession",
    resource_id=session.id,
    actor_id=current_user.id,
    actor_role="admin",
    before_snapshot={"status": "APPROVED"},
    after_snapshot={"status": "PUBLISHED"},
)

# Inspect, log, or stage:
stage_transaction_events(bundle)
```

This is additive — it does not change `execute_with_audit()`. Callers opt in.

---

## 7. Lifecycle Timeline Reconstruction (D1.5)

`build_lifecycle_timeline()` normalizes events from any source into a uniform
shape. Accepted formats: EventEnvelope dicts, DomainEvent asdict, governance
trace events, custom dicts.

`summarize_lifecycle_timeline()` provides:
- `event_count`, `first_event_at`, `last_event_at`
- `has_rollback`, `has_override`, `has_publication`
- `highest_severity` (INFO < WARNING < HIGH_RISK < HARD_FAIL < CRITICAL)

See `LIFECYCLE_TIMELINE_RECONSTRUCTION.md` for field fallback table and usage.

---

## 8. PDPA Event Safety Policy (D1.6)

Three functions for event payload safety:

| Function | Purpose |
|---|---|
| `classify_event_payload(payload)` | Detect PII keys, recommend classification |
| `assert_event_payload_safe(payload, strict=True)` | Raise if PII found (strict mode) |
| `mask_event_payload(payload)` | Deep-copy + recursive PII key masking |

Classification levels:
- **public** — no PII
- **internal** — only operational tokens/QR codes
- **confidential** — personal data (name, email, phone)
- **restricted** — high-sensitivity IDs (citizen_id, national_id, student_id)

---

## 9. What Is NOT Yet Implemented (Deferred)

All deferred items require DBA/IT approval and/or DB migrations:

| Item | Blocker |
|---|---|
| DB event_outbox table | DBA approval + Alembic migration |
| Persistent event store (append-only audit_events table) | DBA approval |
| Outbox relay process / dispatcher worker | DB outbox table prerequisite |
| Event replay and read-model projections | Persistent event store prerequisite |
| Cross-session correlation timeline | Persistent event store prerequisite |
| Retention policy enforcement (archive by retention_hint) | DBA + ops approval |
| EventEnvelope as primary wire format (replacing DomainEvent) | Gradual migration plan |

---

## 10. Test Coverage

| Phase | File | Tests |
|---|---|---|
| D1.1 | `test_event_envelope.py` | 22 |
| D1.2 | `test_event_outbox_service.py` | 16 |
| D1.3 | `test_immutable_audit_service.py` | 20 |
| D1.4 | `test_transaction_event_bridge_service.py` | 11 |
| D1.5 | `test_lifecycle_timeline_service.py` | 17 |
| D1.6 | `test_event_pdpa_policy.py` | 20 |
| **Total** | | **106** |
