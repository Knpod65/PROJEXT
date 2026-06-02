# Advance Batch Live Smoke Validation Log

Date: 2026-06-02

## Backend and Endpoint

- Backend restarted from the current EMS repo on `127.0.0.1:8000`.
- Authenticated browser fetch to `GET /api/invigilation-advance-batch/preview` returned HTTP `200`.
- Summary values:
  - `total_rows = 23`
  - `total_assignments = 23`
  - `ready_for_batch_review = 23`
  - `included_in_advance_batch = 0`
  - `amount_calculation_enabled = false`
  - `pending_rate_rule_count = 23`
  - `blocked_rows = 0`
  - `warning_count = 0`
  - `rule_gaps = 3`
- Every roster row kept `amount_status = PENDING_RATE_RULE` and `amount_preview = PENDING_RATE_RULE`.

## Browser Smoke

- Admin login succeeded with the documented seed account.
- Staff login succeeded with the documented seed account.
- The preview page loaded and displayed the 23-row roster in both roles.
- The preview-only warning banner was visible.
- No approve, final payment, or official export button was present.

## Role Access

- Admin: allowed.
- Staff: allowed.
- Teacher: blocked with an access-denied page.
- Print shop: blocked with an access-denied page.

## Screenshot Evidence

- `docs/operations/demo-smoke-screenshots/advance-batch-preview-admin.png`
- `docs/operations/demo-smoke-screenshots/advance-batch-preview-staff.png`
- `docs/operations/demo-smoke-screenshots/advance-batch-preview-warning-banner.png`
