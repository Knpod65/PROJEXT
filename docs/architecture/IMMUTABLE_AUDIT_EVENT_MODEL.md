# Immutable Audit Event Model
## EMS Academic Operations Platform
**Date:** 2026-05-14
**Phase:** D1.3

---

## 1. Purpose

The immutable audit event model provides a tamper-evident record of every
significant mutation in the EMS lifecycle. By hashing before/after snapshots,
it allows downstream verifiers to confirm that a stored audit record accurately
represents the state at the time of the action — without needing to re-run
the business logic.

---

## 2. Implementation

**File:** `backend/services/immutable_audit_service.py`

### Function Signature

```python
def build_immutable_audit_event(
    *,
    action: str,
    actor_id: int | None,
    actor_role: str | None,
    resource_type: str,
    resource_id: str | int | None,
    before_snapshot: dict | None = None,
    after_snapshot: dict | None = None,
    reason: str | None = None,
    metadata: dict | None = None,
) -> dict
```

### Output Shape

```python
{
    "audit_event_id":  str,          # UUID4
    "action":          str,          # e.g. "SCHEDULE_PUBLISHED"
    "actor_id":        int | None,
    "actor_role":      str | None,   # e.g. "admin"
    "resource_type":   str,          # e.g. "OptimizeSession"
    "resource_id":     str,          # str(resource_id) or "unknown"
    "before_hash":     str | None,   # SHA-256 hex of sanitized before_snapshot
    "after_hash":      str | None,   # SHA-256 hex of sanitized after_snapshot
    "before_snapshot": dict | None,  # PII-sanitized snapshot
    "after_snapshot":  dict | None,  # PII-sanitized snapshot
    "reason":          str | None,
    "metadata":        dict,
    "timestamp":       str,          # UTC ISO
    "immutable":       True,
    "schema_version":  "1.0",
}
```

---

## 3. Hashing

Snapshots are hashed using SHA-256 after:
1. PII sanitization (see section 4)
2. JSON serialization with `sort_keys=True` for determinism

```python
canonical = json.dumps(sanitized_snapshot, sort_keys=True, default=str)
digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

This means:
- The same snapshot always produces the same hash
- Any change to the snapshot (even key reordering) changes the hash
- Callers can verify a stored snapshot by rehashing and comparing

---

## 4. PII Sanitization

The following keys are replaced with `[REDACTED]` before hashing and storage:

```
student_name, student_id, citizen_id, national_id,
email, phone, token, qr_payload, qr_code, password, secret
```

Matching is case-insensitive against the key name. Input dicts are never
mutated — a new sanitized copy is created.

---

## 5. The `immutable: True` Flag

The `"immutable": True` field is a structural marker. It signals:
- This record is intended to be append-only in any storage layer
- Once written, the content must not be updated or deleted
- Any storage layer that receives these records should grant only INSERT,
  not UPDATE or DELETE, to normal application roles

This is a convention — it is not currently enforced at the DB layer (no table
exists yet). When the persistent audit event store is provisioned, the DDL
should reflect this intent.

---

## 6. Recommended Usage

```python
audit_event = build_immutable_audit_event(
    action="SCHEDULE_PUBLISHED",
    actor_id=current_user.id,
    actor_role=get_effective_role(current_user).value,
    resource_type="OptimizeSession",
    resource_id=session.id,
    before_snapshot={"status": "APPROVED", "session_id": session.id},
    after_snapshot={"status": "PUBLISHED", "session_id": session.id},
    reason="All governance checks passed.",
    metadata={"governance_state": "AUTO_APPROVED"},
)
```

---

## 7. What Is Deferred

- Persistent storage of audit events (requires new `audit_events` table, DBA approval)
- Audit event replay / read-model projections
- Cross-service audit event correlation via `correlation_id`
- Retention policy enforcement (archive after `retention_hint` period)
