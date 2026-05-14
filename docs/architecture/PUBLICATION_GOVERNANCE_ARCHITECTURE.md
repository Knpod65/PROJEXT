# Publication Governance Architecture
## EMS Academic Operations Platform — Domain Stabilization Phase
**Date:** 2026-05-14

---

## 1. Overview

The **publication domain** owns all decisions about whether a schedule can be published, whether a rollback is safe, and what audit evidence must be captured at publication time. It is a pure-logic layer — no DB calls, no ORM, no HTTP.

**Service:** `backend/services/publication_governance_service.py`

**API endpoint:** `GET /workflow/sessions/{session_id}/publication-readiness`

---

## 2. Responsibilities

| Concern | Function |
|---------|----------|
| Publication readiness assessment | `assess_publication_readiness()` |
| Rollback safety evaluation | `assess_rollback_safety()` |
| Publish audit payload construction | `build_publish_audit_payload()` |
| Emergency override payload construction | `build_emergency_override_payload()` |

---

## 3. Publication Readiness Assessment

### Entry Point

```python
def assess_publication_readiness(
    quality_report: dict,
    governance: dict,
    recheck_summary: dict,
    schedule_state: str,
) -> PublicationReadiness
```

### Risk Scoring

Risk is computed on a 0–100 scale where **lower = safer to publish**.

| Condition | Deduction |
|-----------|-----------|
| `governance_state == "AUTO_APPROVED"` | −40 |
| `hard_fail_count == 0` | −20 |
| `overall_score >= 80` | −10 |
| `schedule_state == "APPROVED"` | −10 |

Base risk: **100**. Minimum achievable: **20** (fully clean schedule).

### Publication Gate

```python
can_publish = (risk_score < 60.0) AND (no HARD_FAIL blockers)
```

A schedule can be published only if both conditions hold simultaneously.

### Blockers

| Code | Severity | Can Override | Trigger |
|------|----------|--------------|---------|
| `GOVERNANCE_BLOCKED` | `HARD_FAIL` | No | `governance_state == "BLOCKED"` |
| `HARD_FAILURES_PRESENT` | `HARD_FAIL` | No | `hard_fail_count > 0` |
| `ESCALATION_REQUIRED` | `WARNING` | Yes | `governance_state == "ESCALATION_REQUIRED"` |
| `SCHEDULE_NOT_APPROVED` | `WARNING` | Yes | State not in APPROVED/GOVERNANCE_REVIEW/RECHECKED/PUBLISHED/LOCKED |

`HARD_FAIL` blockers are absolute — they cannot be overridden without an emergency override payload.

---

## 4. Rollback Safety Evaluation

### Entry Point

```python
def assess_rollback_safety(
    schedule_state: str,
    published_at: str | None,
    actor_id: int | None,
    rollback_reason: str | None,
) -> RollbackAssessment
```

### Recommendation Matrix

| Schedule State | can_rollback | recommendation | data_loss_risk |
|----------------|-------------|----------------|----------------|
| `LOCKED` | False | `HIGH_RISK` | True |
| `PUBLISHED` | True | `CAUTION` | False |
| `APPROVED` | True | `CAUTION` | False |
| Any other | True | `SAFE` | False |
| (no reason) | False | `HIGH_RISK` | False |
| (no actor) | False | — (added risk) | — |

**Invariants:**
- Rollback always requires a non-empty `rollback_reason`.
- Rollback always requires an `actor_id` — all rollbacks must have an accountable user.
- `LOCKED` schedules cannot be rolled back — they require administrator action outside this service.

---

## 5. Audit Payloads

### Publish Audit Payload

```python
def build_publish_audit_payload(
    readiness: PublicationReadiness,
    actor_id: int | None,
    session_id: str | None,
) -> dict
```

Returns a dict suitable for passing to `execute_with_audit()` in the transaction audit service. Always includes: `action`, `actor_id`, `session_id`, `published_at`, `governance_state`, `risk_score`, `can_publish`, `blocker_codes`, `warning_count`, `approval_metadata`.

### Emergency Override Payload

```python
def build_emergency_override_payload(
    actor_id: int | None,
    reason: str,
    blockers_overridden: list[str],
) -> dict
```

Raises `ValueError` if `reason` is empty or `blockers_overridden` is empty. The returned payload always sets `requires_post_incident_review: True` — emergency overrides must be reviewed after the fact.

---

## 6. Emergency Override Protocol

An emergency override allows a HARD_FAIL blocker to be bypassed in exceptional circumstances (e.g., a board directive to publish despite pending governance review). The protocol:

1. **Build the override payload** via `build_emergency_override_payload()`.
2. **Record the override** in the audit trail (callers must persist this).
3. **Proceed with publication** and record `EMERGENCY_PUBLICATION_OVERRIDE` as the action.
4. **Post-incident review** is mandatory — the `requires_post_incident_review: True` flag triggers this obligation.

Override authority is not granted by this service — it is a caller responsibility. This service only validates that the override is properly formed (non-empty reason, named blockers) and returns the audit payload.

---

## 7. Data Flow

```
Caller (router or workflow service)
  │
  ├─→ assess_publication_readiness(quality_report, governance, recheck_summary, schedule_state)
  │     │
  │     ├─ _compute_risk_score()
  │     ├─ _collect_blockers()
  │     └─ _collect_warnings()
  │     → returns PublicationReadiness
  │
  ├─→ (if can_publish) schedule_state_machine.transition("APPROVED", "PUBLISHED", ...)
  │
  └─→ build_publish_audit_payload(readiness, actor_id, session_id)
        → pass to execute_with_audit() or save to audit trail
```

---

## 8. Dataclasses

```python
@dataclass(frozen=True)
class PublicationBlocker:
    code: str
    severity: str       # "HARD_FAIL" | "WARNING"
    message: str
    can_override: bool

@dataclass(frozen=True)
class PublicationReadiness:
    can_publish: bool
    risk_score: float   # 0–100, lower = safer
    blockers: tuple     # tuple of dicts (JSON-serialisable)
    warnings: tuple     # tuple of strings
    approval_metadata: dict
    governance_state: str

@dataclass(frozen=True)
class RollbackAssessment:
    can_rollback: bool
    rollback_risks: tuple       # tuple of strings
    data_loss_risk: bool
    recommendation: str         # "SAFE" | "CAUTION" | "HIGH_RISK"
```

Frozen dataclasses are used to ensure immutability after construction. `blockers` and `rollback_risks` are tuples (not lists) so they remain hashable.

---

## 9. Test Coverage

Tests are in `backend/tests/test_publication_governance_service.py` (27 tests):
- Clean schedule can publish
- BLOCKED governance cannot publish
- Hard failures block publication
- Risk score boundaries (0–100 clamped)
- Schedule state not approved adds blocker
- Escalation required adds WARNING blocker
- Low quality score adds warning
- Empty dicts handled gracefully
- Approval metadata has required keys
- PUBLISHED/LOCKED skip state blocker
- hard_error_count alias supported
- Rollback from PUBLISHED is CAUTION
- Rollback from LOCKED is HIGH_RISK
- Rollback without reason/actor blocked
- Rollback from DRAFT is SAFE
- RollbackAssessment is frozen
- Audit payload has required keys
- Emergency override requires reason and blockers
- Override strips whitespace from reason
