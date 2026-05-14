# Scheduling State Machine Architecture
## EMS Academic Operations Platform — Domain Stabilization Phase
**Date:** 2026-05-14

---

## 1. Overview

The `schedule_state_machine` tracks the lifecycle of a **generated exam schedule** — from initial CP-SAT output through governance approval, publication, locking, and archival. This is a **distinct concern** from the signing workflow managed by `workflow_signing_service.py`.

| Concern | Service | Tracks |
|---------|---------|--------|
| Schedule lifecycle | `schedule_state_machine.py` | WHAT state the SCHEDULE is in |
| Signing workflow | `workflow_signing_service.py` | WHO has signed off (department heads, faculty deans) |

These two machines operate independently and must never be merged.

---

## 2. States

```
DRAFT → OPTIMIZED → RECHECKED → (GOVERNANCE_REVIEW →) APPROVED → PUBLISHED → LOCKED → ARCHIVED
                                                      ↗
Any non-terminal state → ROLLED_BACK → DRAFT
```

| State | Meaning |
|-------|---------|
| `DRAFT` | Schedule record exists; CP-SAT has not yet run successfully |
| `OPTIMIZED` | CP-SAT completed; raw allocations are generated |
| `RECHECKED` | Recheck service validated the optimization output |
| `GOVERNANCE_REVIEW` | Human review required before approval can be granted |
| `APPROVED` | Governance-approved (auto or manual) — ready for publication |
| `PUBLISHED` | Released to exam participants |
| `LOCKED` | All signatures complete; schedule is immutable |
| `ARCHIVED` | Retained for records — **terminal state** (no exits) |
| `ROLLED_BACK` | Publication reverted; returns to DRAFT via recovery path |

---

## 3. Transition Table

| From | To | Guard |
|------|----|-------|
| `DRAFT` | `OPTIMIZED` | none |
| `OPTIMIZED` | `RECHECKED` | none |
| `OPTIMIZED` | `DRAFT` | none (reset) |
| `RECHECKED` | `GOVERNANCE_REVIEW` | none |
| `RECHECKED` | `APPROVED` | `hard_fail_count == 0` |
| `RECHECKED` | `ROLLED_BACK` | `rollback_reason` non-empty |
| `GOVERNANCE_REVIEW` | `APPROVED` | none |
| `GOVERNANCE_REVIEW` | `ROLLED_BACK` | `rollback_reason` non-empty |
| `APPROVED` | `PUBLISHED` | `governance_state != "BLOCKED"` |
| `APPROVED` | `ROLLED_BACK` | `rollback_reason` non-empty |
| `PUBLISHED` | `LOCKED` | none |
| `PUBLISHED` | `ROLLED_BACK` | `rollback_reason` non-empty |
| `LOCKED` | `ARCHIVED` | `actor_id` must be set |
| `ROLLED_BACK` | `DRAFT` | none (recovery) |

---

## 4. Guard Conditions

### 4.1 Rollback always requires a reason
Every transition to `ROLLED_BACK` must carry a non-empty `rollback_reason` string. An empty or whitespace-only reason raises `ScheduleTransitionError`.

### 4.2 Hard failures block RECHECKED → APPROVED
If the recheck service reports any hard failures (`hard_fail_count > 0`), the transition to `APPROVED` is blocked. All hard failures must be resolved or acknowledged before approval can proceed.

### 4.3 BLOCKED governance blocks APPROVED → PUBLISHED
If `governance_state == "BLOCKED"`, publication is denied. The governance gate must reach any non-BLOCKED state before the schedule can be published.

### 4.4 LOCKED → ARCHIVED requires an actor
Archiving a locked schedule is an accountable action. `actor_id` must be provided; a `None` actor raises `ScheduleTransitionError`.

---

## 5. API

```python
from services.schedule_state_machine import (
    ScheduleState,
    ScheduleStateMachine,
    ScheduleTransitionError,
    ScheduleTransitionResult,
    schedule_state_machine,   # module singleton
)

# Check if a transition is valid (no guards evaluated)
ok: bool = schedule_state_machine.can_transition("OPTIMIZED", "RECHECKED")

# Get reachable next states (no guards)
nexts: list[str] = schedule_state_machine.valid_next_states("APPROVED")

# Check terminal
is_done: bool = schedule_state_machine.is_terminal("ARCHIVED")

# Execute a transition (guards evaluated, raises on violation)
result: ScheduleTransitionResult = schedule_state_machine.transition(
    from_state="APPROVED",
    to_state="PUBLISHED",
    actor_id=42,
    governance_state="AUTO_APPROVED",
)
```

### ScheduleTransitionResult

```python
@dataclass(frozen=True)
class ScheduleTransitionResult:
    success: bool
    from_state: str
    to_state: str
    actor_id: int | None
    reason: str | None
    audit_metadata: dict    # always populated; suitable for audit logging
    timestamp: str          # ISO 8601 UTC
```

---

## 6. Design Rationale

**Pure logic, no DB.** The machine returns a result; callers own persistence. This ensures the machine is fully testable, deterministic, and reusable without mocking.

**Frozen result dataclass.** Prevents accidental mutation of transition results after they are returned.

**Module singleton.** `schedule_state_machine = ScheduleStateMachine()` provides a convenient import without requiring callers to instantiate.

**Distinct from signing workflow.** The signing workflow (in `workflow_signing_service.py`) tracks whether each department head and faculty dean has approved. The schedule state machine tracks the higher-level lifecycle state of the schedule object itself. These operate at different abstraction layers and must not be merged.

**ROLLED_BACK is not terminal.** Rolling back a publication is a recovery action, not a destruction action. ROLLED_BACK → DRAFT allows the schedule to re-enter the normal lifecycle after corrections.

**ARCHIVED is the only terminal state.** Once archived, a schedule cannot transition further. This enforces data retention integrity without deletion.

---

## 7. Relationship to Publication Governance

The `schedule_state_machine` owns lifecycle transitions. The `publication_governance_service` owns **readiness assessment** — it evaluates whether the current state of the schedule, quality report, and governance decision together satisfy publication safety criteria.

Typical call order:
1. `assess_publication_readiness(...)` → returns `PublicationReadiness` with `can_publish` flag
2. If `can_publish`, call `schedule_state_machine.transition("APPROVED", "PUBLISHED", ...)`
3. Store the `ScheduleTransitionResult.audit_metadata` in the audit trail

---

## 8. Test Coverage

Tests are in `backend/tests/test_schedule_state_machine.py` (37 tests):
- All valid transition edges
- All guard conditions (positive and negative)
- Rollback path and recovery
- Terminal state verification
- Result immutability
- Audit metadata population
- Module singleton
- All 9 ScheduleState enum values
