# Advance Batch Preview Validation Snapshot

**Evidence date**: 2026-06-04
**Snapshot type**: `SYSTEM PREVIEW SNAPSHOT - NOT OFFICIAL PAYMENT EXPORT`
**Finance/admin gate**: `PENDING_FINANCE_ADMIN_REVIEW`

## System Summary

| Field | Value |
|---|---:|
| weekday_rate | 300 THB / session |
| weekend_rate | 500 THB / session |
| total_roster_rows | 23 |
| preview_calculated_rows | 23 |
| weekday_rows | 21 |
| weekend_rows | 2 |
| pending_rate_rows | 0 |
| blocked_amount_rows | 0 |
| preview_total | 7,300 THB |

## Evidence Sources

- Validation log: `docs/architecture/ADVANCE_BATCH_PREVIEW_AMOUNT_VALIDATION_LOG.md`
- Response contract: `docs/architecture/ADVANCE_BATCH_PREVIEW_RESPONSE_CONTRACT.md`
- Screenshot: `docs/operations/demo-smoke-screenshots/advance-batch-preview-amounts-admin.png`

## Safety Flags

- `amount_calculation_enabled = false`
- `preview_amount_enabled = true`
- `payment_authorization_enabled = false`
- `final_export_enabled = false`

## Interpretation

- The snapshot records the current system-side demo preview only.
- It intentionally does not duplicate person-level rows or create an official payment roster.
- No independent approved finance/manual expected result is currently available in the repository.
- The total must not be treated as payable, approved, exported, or final.
- Finance/admin must complete the blank comparison template and sign the validation packet before any approval/export design proceeds.
