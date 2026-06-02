# Advance Batch Preview Endpoint Validation Source Review

Date: 2026-06-02

## Docs Read

- `docs/architecture/ADVANCE_INVIGILATION_BATCH_ROSTER_SOURCE_REVIEW.md`
- `docs/architecture/ADVANCE_BATCH_ASSIGNMENT_DATA_AUDIT.md`
- `docs/architecture/ADVANCE_INVIGILATION_BATCH_ROSTER_RECORD_SPEC.md`
- `docs/architecture/ADVANCE_INVIGILATION_BATCH_INCLUSION_RULES.md`
- `docs/architecture/ADVANCE_BATCH_IMPLEMENTATION_DECISION_GATE.md`
- `docs/architecture/ADVANCE_INVIGILATION_BATCH_PREVIEW_TEST_MATRIX.md`
- `docs/architecture/INVIGILATION_ADVANCE_DISBURSEMENT_MODEL.md`
- `docs/architecture/INVIGILATION_POST_DUTY_RECONCILIATION_MODEL.md`
- `docs/architecture/INVIGILATION_PAYMENT_PREVIEW_MODEL_SPEC.md`
- `docs/architecture/INVIGILATION_PAYMENT_PREVIEW_UI_API_ROADMAP.md`
- `docs/architecture/EMS_100_PERCENT_MASTER_SCORECARD.md`
- `docs/architecture/EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md`

## Current Endpoint

- Endpoint: `GET /api/invigilation-advance-batch/preview`
- Router prefix: `/api/invigilation-advance-batch`
- Purpose: preview-only roster of assigned invigilation duties considered for advance batch review.
- Authorization: staff/admin guarded route.

## Expected Behavior

- Use assigned invigilation roster as the source of truth for advance inclusion.
- Return one row per assigned supervision duty.
- Keep `amount_status` and `amount_preview` as `PENDING_RATE_RULE`.
- Keep `amount_calculation_enabled = false`.
- Treat check-in/evidence as post-duty reconciliation data, not an advance inclusion gate.

## Prohibited Behavior

- No payment amount calculation.
- No final payment authorization.
- No official export.
- No check-in prerequisite for advance inclusion.
- No teaching workload or excess teaching compensation logic.

## Validation Plan

1. Run backend compile/import/test validation.
2. Call the endpoint through FastAPI TestClient with a staff/admin dependency override.
3. Record status, response keys, summary counts, roster rows, blockers, warnings, rule gaps, and amount statuses.
4. Add a frontend page only after the endpoint returns a stable preview contract with meaningful rows.
