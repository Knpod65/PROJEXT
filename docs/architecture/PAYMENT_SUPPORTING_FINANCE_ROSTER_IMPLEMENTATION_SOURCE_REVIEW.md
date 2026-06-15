# Payment Supporting Finance Roster Implementation Source Review

**Date**: 2026-06-15  
**Gate**: `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`

## Exact Sources

- Live payable invigilation assignments: `Supervision`, joined to `ExamSchedule`, `User`, `Room`, `Section`, and `Course`.
- Paper-distribution assignments: `PaperDistributionAssignment`, scoped through matching `ExamPeriod`.
- Rates and responsible group: active, complete, term-specific `PaymentDocumentSettings`.
- Physical room rule: `Room.e_room_code IS NULL`; online rooms remain trace-only.
- Historical `SupervisionBaseline`, teaching assignments, and `ExamSchedule.paper_distributor` are not payment-name sources.

## Files And Reuse

- New aggregation/workbook service: `backend/services/payment_supporting_finance_roster_service.py`.
- New request schema and routes: `backend/schemas.py`, `backend/routers/invigilation_advance_batch.py`.
- Reuses accepted-review lookup and document ID from `payment_document_draft_export_service.py`.
- Reuses Buddhist Era date and time-slot normalization from `official_payment_document_draft_service.py`.
- Reuses openpyxl banner, formatting, and `get_column_letter` patterns from the accepted RC1 export.

## Safety Invariants

- Read-only export with no database writes.
- `payment_authorization_enabled=false`, `final_export_enabled=false`.
- Every sheet displays `DRAFT_NOT_AUTHORIZED` and draft/non-authorizing warnings.
- Live `Supervision` only; one payable count per reliable user ID/date/normalized slot.
- Cross-source duplicates use supervision as the primary finance category and retain all trace sources.
- Paper assignments without an eligible physical-room mapping remain trace/review-only.

## Test Plan

- Verify gates, role access, authoritative sources, room keeper inclusion, deterministic room ranking, cross-source and multi-room deduplication, single/all-online behavior, missing/extra paper assignments, five sheets, Thai warnings, metadata safety flags, zero persistence, and unchanged RC1 export behavior.
