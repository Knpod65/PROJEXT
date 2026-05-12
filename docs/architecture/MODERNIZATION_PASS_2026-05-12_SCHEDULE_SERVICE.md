# Modernization Pass Report
## 2026-05-12 - Schedule Query Service Foundation (Pass 02)

## Scope

- Repository: `opt/ems_system`
- Stack preserved: FastAPI + React/TypeScript + Python data stack
- Endpoint paths preserved
- DB schema unchanged
- Frontend untouched

## Implemented Changes

### 1) Repository Layer

New file:
- `backend/repositories/schedule_repository.py`

Added reusable helpers for:
- schedule base query assembly with eager loading
- unavailability map loading for optimizer inputs

### 2) Policy Layer

New file:
- `backend/policies/schedule_policy.py`

Added reusable scope logic for:
- admin/global access
- teacher scoped access
- department-scoped access

### 3) Service Layer

New file:
- `backend/services/schedule_query_service.py`

Added reusable orchestration for:
- building filtered schedule queries
- serializing schedule rows
- grouping schedules by date
- room unavailability helpers

### 4) Router Wiring

Updated:
- `backend/routers/schedule.py`

The router now delegates grouped/list query assembly and schedule serialization to shared service helpers while preserving the current route paths and response shapes.

## Validation / Risk

This pass is intentionally small and non-destructive:
- no endpoint path changes
- no response shape changes intended
- no schema migrations
- no frontend behavior changes

Residual risk:
- `schedule.py` still contains optimizer and mutation logic beyond the thin query/serialization slice.

## Next Highest-Risk Target

Continue schedule thinning by extracting the remaining optimizer-adjacent mutation helpers and room/paper distribution orchestration into service methods, then start the optimization recheck engine.
