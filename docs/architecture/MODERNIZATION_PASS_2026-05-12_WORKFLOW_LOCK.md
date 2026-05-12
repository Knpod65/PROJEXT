# Modernization Pass Report
## 2026-05-12 - Workflow Lock Service Extraction (Safe Slice 01)

## Scope

- Repository: `opt/ems_system`
- Stack preserved: FastAPI + React/TypeScript + Python data stack
- Endpoint paths unchanged
- Auth/session token format unchanged
- DB schema unchanged

## Analysis Summary (This Pass)

Primary findings validated in code:

1. `backend/routers/optimize_workflow.py` contained lock lifecycle logic (`/session/lock`, `/session/unlock`, `/session/heartbeat`, `/session/lock-status`) mixed with HTTP routing and workflow orchestration.
2. Lock semantics were duplicated as endpoint-local helpers (`_is_lock_expired`, `_assert_editable`, `_acquire_lock`, `_release_lock`).
3. Lock lifecycle operations were not routed through `services/audit_service.py` semantic wrapper.

## Implemented Changes

### 1) Service Extraction

New file:
- `backend/services/workflow_lock_service.py`

Extracted reusable lock logic:
- `is_lock_expired()`
- `remaining_lock_seconds()`
- `assert_session_editable_for_lock()`
- `acquire_lock()`
- `release_lock()`
- `heartbeat_lock()`

Service behavior:
- Uses centralized TTL from `config.policy.WORKFLOW_LOCK_TTL_SECONDS`
- Raises `services.exceptions` domain errors for policy/validation conflicts
- Keeps router thin and transport-agnostic

### 2) Router Modernization (Non-breaking)

Updated:
- `backend/routers/optimize_workflow.py`

What changed:
- Lock helper behavior now delegates to `workflow_lock_service`
- Existing endpoints remain the same:
  - `POST /api/workflow/session/lock`
  - `POST /api/workflow/session/unlock`
  - `POST /api/workflow/session/heartbeat`
  - `GET /api/workflow/session/lock-status`
- Added semantic audit events for lock lifecycle:
  - `WORKFLOW_LOCK_ACQUIRED`
  - `WORKFLOW_LOCK_RELEASED`
  - `WORKFLOW_LOCK_HEARTBEAT`

Compatibility:
- Response shapes and endpoint paths preserved
- No runtime contract changes intended for frontend clients

### 3) Tests Added

New file:
- `backend/tests/test_workflow_lock_service.py`

Coverage includes:
- lock expiry math
- remaining time boundary behavior
- editable session validation
- signer-role enforcement
- active holder conflict behavior
- acquire/release/heartbeat flow

## DRY Impact

- Removed endpoint-local lock semantics as the canonical source.
- Established one reusable lock service for future workflow/calendar engines.

## Audit & Governance Impact

- Added explicit audit events for lock lifecycle actions.
- Improved operational traceability for concurrent workflow edits.

## PDPA Impact

- Neutral-positive: no new PII exposure introduced.
- Audit metadata uses operational identifiers (period/session ids), not student payloads.

## Risk Assessment

Low risk:
- Internal refactor of lock helpers only
- No schema migration
- No route contract changes

Residual risks:
1. `auth_utils.log_action()` commits separately from domain commits (transaction coupling still pending).
2. Other `optimize_workflow.py` domains remain fat (user CRUD, unavailability, signing/session orchestration).

## Next Highest-Risk Target

`backend/routers/optimize_workflow.py` session signing state machine extraction:
- move round-sign transition rules to `services/workflow_session_service.py`
- keep endpoint contracts stable
- add explicit transition tests and audit-coupled state events
