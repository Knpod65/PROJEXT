# Advance Batch Rate Rule Integration Decision

**Date**: 2026-06-04
**Status**: PREVIEW ONLY - NOT PAYMENT AUTHORIZATION

## Decision

`ENABLE_ONLY_IF_BOTH_RATES_CONFIGURED`

## Gate Result

The preview-only integration gate passes because:

- The simple-rate API and UI have been validated.
- The active simple pair provides both weekday and weekend `PER_SESSION` amounts.
- `ExamSchedule.exam_date` is available for all 23 current assigned duties.
- Gregorian and Buddhist Era dates can be deterministically normalized before weekday classification.
- The response and UI can preserve preview-only safety flags.

## Required Behavior

- Calculate preview amounts only when both configured rates are available.
- Treat the current active simple pair as global preview configuration; do not apply internal effective dates.
- Normalize years greater than or equal to `2400` by subtracting `543` for weekday classification.
- Calculate only rows with `advance_inclusion_status = READY_FOR_BATCH_REVIEW`.
- Keep blocked roster rows out of the preview total.
- Keep reconciliation separate and never use check-in as an advance amount gate.

## Safety Invariants

- `preview_amount_enabled` indicates preview arithmetic only.
- Legacy `amount_calculation_enabled` remains `false`.
- `payment_authorization_enabled` remains `false`.
- `final_export_enabled` remains `false`.
- No final payment, approval, official export, refund, or offset logic is introduced.
