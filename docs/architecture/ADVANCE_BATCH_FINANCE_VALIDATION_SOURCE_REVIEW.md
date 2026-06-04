# Advance Batch Finance/Admin Validation Source Review

**Date**: 2026-06-04
**Gate status**: `PENDING_FINANCE_ADMIN_REVIEW`
**Scope**: Preview-only EMS invigilation amounts

## Documents Read

- `docs/architecture/ADVANCE_BATCH_PREVIEW_AMOUNT_VALIDATION_LOG.md`
- `docs/architecture/ADVANCE_BATCH_PREVIEW_RESPONSE_CONTRACT.md`
- `docs/architecture/ADVANCE_BATCH_RATE_RULE_INTEGRATION_DECISION.md`
- `docs/architecture/INVIGILATION_RATE_RULE_SIMPLE_DAY_TYPE_MODEL.md`
- `docs/architecture/INVIGILATION_ADVANCE_DISBURSEMENT_MODEL.md`
- `docs/architecture/INVIGILATION_POST_DUTY_RECONCILIATION_MODEL.md`
- `docs/operations/INVIGILATION_PAYMENT_RULE_DECISION_REGISTER.md`
- `docs/operations/INVIGILATION_PAYMENT_RULE_ANSWER_INTAKE.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`

## Current Preview Behavior

- The advance roster is sourced from assigned invigilation duties.
- Ready roster rows receive a preview-only amount only when both weekday and weekend rates are configured.
- Monday-Friday exam dates use the weekday rate; Saturday-Sunday exam dates use the weekend rate.
- Buddhist Era years greater than or equal to `2400` are normalized by subtracting `543` before weekday/weekend classification.
- Original exam dates remain visible for auditability.
- Check-in is not an advance inclusion or preview-amount gate.
- Attendance, absence, no-show, and substitution evidence remain post-duty reconciliation inputs.

## Current System Evidence

The validated local demo evidence records:

- Total roster rows: `23`
- Preview-calculated rows: `23`
- Weekday rows: `21`
- Weekend rows: `2`
- Pending or blocked amount rows: `0`
- Weekday rate used: `300 THB` per session
- Weekend rate used: `500 THB` per session
- Preview total: `7,300 THB`
- Screenshot: `docs/operations/demo-smoke-screenshots/advance-batch-preview-amounts-admin.png`

This is system-side demo evidence only. It is not an approved manual finance result or an official payment list.

## Preview-Only Safeguards

- `amount_calculation_enabled = false`
- `payment_authorization_enabled = false`
- `final_export_enabled = false`
- Row authorization status remains `NOT_AUTHORIZED_PREVIEW_ONLY`
- No final payment calculation, approval, official export, refund amount, or offset amount is implemented.

## Known Constraints

- No independently approved finance/admin sample or expected total was found in the repository.
- The payment decision register and answer intake remain open.
- Finance/admin has not approved the rate source, payable-role scope, payment period, exception rules, approval owner, or official export format.
- The current local rates and total are validation inputs, not finance-approved payable values.

## Finance/Admin Validation Required

Finance/admin must independently confirm:

1. Whether weekday and weekend rates are correct and approved.
2. Whether payment per assigned duty/session is the correct unit.
3. Whether weekday/weekend classification and Buddhist Era normalization are correct.
4. Whether the roster includes and excludes the correct duties and people.
5. Whether blocked or exception rows are handled correctly.
6. Whether the preview wording is sufficiently distinct from payment authorization.
7. Which remaining rules must be closed before approval and official export design.

Until a human reviewer completes the comparison and sign-off, the gate remains `PENDING_FINANCE_ADMIN_REVIEW`.
