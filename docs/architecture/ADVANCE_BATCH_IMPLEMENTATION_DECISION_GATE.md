# Advance Batch Implementation Decision Gate

**Date**: 2026-06-02  
**Decision**: `SAFE_BACKEND_PREVIEW_SERVICE`

## Options Reviewed

- `DOCS_ONLY`
- `SAFE_BACKEND_PREVIEW_SERVICE`
- `SAFE_FRONTEND_PREVIEW_PAGE`
- `BLOCKED_BY_DATA_MODEL`
- `BLOCKED_BY_MISSING_ASSIGNMENT_SOURCE`

## Decision Rationale

Existing EMS assignment/session data can support a computed, read-only backend preview:

- `ExamSchedule` provides exam session, date/time, room, status, and section.
- `Supervision` provides assigned person and duty role.
- `User` provides person identity.
- `Section` and `Course` provide course/section context.
- `ExamPeriod` can be used as a candidate period lookup.

No database migration is required. No final approval, export, refund, or amount logic is needed.

## Backend Criteria

Met:

- Existing assignment/session data can be read.
- Service can produce computed preview from existing data.
- Amount is always `PENDING_RATE_RULE`.
- No final approval or export logic.
- No check-in requirement for advance inclusion.

## Frontend Criteria

Not implemented in this pass:

- The endpoint should be validated first.
- No UI route is needed for this backend scaffold.
- Roadmap will remain the source for future UI work.

