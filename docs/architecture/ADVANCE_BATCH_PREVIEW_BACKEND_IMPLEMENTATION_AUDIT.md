# Advance Batch Preview Backend Implementation Audit

Date: 2026-06-02

## Implementation Surface

| Area | Path | Finding |
|---|---|---|
| Router | `backend/routers/invigilation_advance_batch.py` | Defines `GET /preview` under `/api/invigilation-advance-batch`; read-only; guarded by `require_staff_or_admin`. |
| Service | `backend/services/invigilation_advance_batch_preview_service.py` | Builds preview rows from `ExamSchedule.supervisions`; does not calculate money; does not use check-in as an inclusion gate. |
| Schemas | `backend/schemas.py` | Defines summary, roster row, and response models. Summary now includes explicit validation counters and `amount_calculation_enabled = false`. |
| Tests | `backend/tests/test_invigilation_advance_batch_preview_service.py` | Covers normal inclusion, missing person, duplicate same slot, missing rate, missing check-in, missing room, and missing payment period. |
| Registration | `backend/main.py` | Includes the router with prefix `/api/invigilation-advance-batch`. |

## Data Source Used

- Internal invigilation assignments only: `ExamSchedule.supervisions`.
- Joins schedule, section/course, room, supervision user, and period lookup.
- Does not use `Supervision.compensation`, external compensation, teaching workload, or final payment fields.

## Response Shape

- Top-level keys: `summary`, `roster_rows`, `blockers`, `warnings`, `rule_gaps`.
- Monetary fields remain placeholders:
  - `amount_status = PENDING_RATE_RULE`
  - `amount_preview = PENDING_RATE_RULE`
  - `amount_calculation_enabled = false`

## Assumptions

- Missing rate rules should block amount calculation only, not roster inclusion.
- Missing check-in should trigger post-duty reconciliation later, not pre-payment exclusion.
- Current endpoint is a preview scaffold, not a final payment workflow.

## Limitations And Risks

- No persisted payment batch exists yet.
- No rate table or payment unit is confirmed.
- No official approval owner is configured.
- Blockers/warnings are currently string lists, not structured objects.
- Production/payment readiness is unchanged.
