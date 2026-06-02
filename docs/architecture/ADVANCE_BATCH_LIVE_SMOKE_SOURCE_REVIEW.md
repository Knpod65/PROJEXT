# Advance Batch Live Smoke Source Review

Date: 2026-06-02

## Docs Read

- `docs/architecture/ADVANCE_BATCH_PREVIEW_ENDPOINT_VALIDATION_SOURCE_REVIEW.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_BACKEND_IMPLEMENTATION_AUDIT.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_ENDPOINT_VALIDATION_LOG.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_RESPONSE_CONTRACT.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_DEMO_DATA_GAP_REVIEW.md`
- `docs/architecture/ADVANCE_BATCH_FRONTEND_PAGE_DECISION_GATE.md`
- `docs/architecture/ADVANCE_INVIGILATION_BATCH_PREVIEW_TEST_MATRIX.md`
- `docs/architecture/INVIGILATION_ADVANCE_DISBURSEMENT_MODEL.md`
- `docs/architecture/INVIGILATION_POST_DUTY_RECONCILIATION_MODEL.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`

## Expected Endpoint Behavior

- `GET /api/invigilation-advance-batch/preview` returns HTTP 200 for authenticated admin/staff users.
- The response stays preview-only and keeps `amount_calculation_enabled = false`.
- Every roster row keeps `amount_status = PENDING_RATE_RULE` and `amount_preview = PENDING_RATE_RULE`.
- The live demo data returns 23 roster rows with no blockers and no warnings.

## Expected Frontend Behavior

- Route: `/invigilation-advance-batch-preview`.
- Page title and banner must clearly say preview-only and not payment authorization.
- Summary cards should mirror the endpoint totals.
- The roster table should render the 23 preview rows.
- No approve, final payment, or official export action should be present.

## Previous Limitation

- Earlier smoke attempts were blocked because port 8000 was occupied by an older backend process that did not expose the current preview route in the live browser path.
- This pass replaced that process with the current repo backend and verified the route in the browser.

## Live Smoke Plan

1. Identify and stop only the stale backend process if it is clearly the EMS uvicorn instance.
2. Restart the backend from the current repository on `127.0.0.1:8000`.
3. Start the frontend dev server on `127.0.0.1:3000`.
4. Log in as admin and staff using documented seed accounts.
5. Open `/invigilation-advance-batch-preview` and verify the live 23-row preview.
6. Confirm amounts remain `PENDING_RATE_RULE` and no final payment actions exist.
7. Validate role access for teacher and print shop.
8. Capture screenshot evidence if browser tooling is available.
