# Advance Invigilation Batch Roster Source Review

**Date**: 2026-06-02  
**Status**: PREVIEW ONLY - NO AMOUNT CALCULATION

## Docs Read

- `EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md`
- `INVIGILATION_ADVANCE_DISBURSEMENT_MODEL.md`
- `INVIGILATION_POST_DUTY_RECONCILIATION_MODEL.md`
- `INVIGILATION_PAYMENT_PREVIEW_MODEL_SPEC.md`
- `INVIGILATION_PAYMENT_DATA_READINESS_CHECKLIST.md`
- `INVIGILATION_PAYMENT_RULE_COMPLETENESS_AUDIT.md`
- `INVIGILATION_PAYMENT_MODEL_SELECTION_GATE.md`
- `INVIGILATION_PAYMENT_PREVIEW_IMPLEMENTATION_READINESS_PLAN.md`
- `INVIGILATION_REFUND_OFFSET_TRACKING_MODEL.md`
- `INVIGILATION_ABSENCE_EXPLANATION_WORKFLOW.md`
- `INVIGILATION_PAYMENT_RULE_DECISION_REGISTER.md`
- `INVIGILATION_PAYMENT_RULE_FOLLOWUP_QUESTIONS.md`
- `EMS_CURRENT_PAYMENT_AND_WORKLOAD_CODE_AUDIT.md`
- `EMS_100_PERCENT_MASTER_SCORECARD.md`
- `EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md`

## Corrected Model

EMS invigilation payment is a two-stage flow:

1. Advance roster/batch preview from approved invigilation assignment records.
2. Post-duty reconciliation after the exam date using attendance, check-in, substitution, absence, explanation, refund, and offset evidence.

Check-in is not a default pre-payment gate. Missing check-in should create reconciliation work after duty, not automatic exclusion from an advance roster.

## Can Be Implemented Without Rates

- A read-only roster preview of assigned invigilation duties.
- Inclusion/blocker/warning statuses.
- Amount placeholders set to `PENDING_RATE_RULE`.
- Post-duty reconciliation status placeholders.
- Rule-gap reporting for rate, period, approval, and reconciliation decisions.

## Still Blocked By Finance/Admin

- Payment unit and rates.
- Official batch approval owner.
- Payment period/cutoff rule.
- Substitute/original payee handling.
- Refund/offset rules.
- Official report/export format.

## Why Amount Must Stay `PENDING_RATE_RULE`

The current EMS has provisional `compensation` fields, but no approved rate source, payment unit, rate code, or finance authorization. Any numeric amount would encode an unapproved policy assumption.

