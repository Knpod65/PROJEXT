# Invigilation Payment Preview Model Spec

**Date**: 2026-06-02  
**Label**: PREVIEW ONLY - NOT PAYMENT AUTHORIZATION  
**Scope**: Invigilation payment (`ค่าคุมสอบ`) only.

## Hard Rule

This document describes possible preview models only. It does not choose a final payment model, does not set rates, does not calculate official payable amounts, and does not authorize payment.

## 2026-06-02 Model Correction

Preview must now produce two separate outputs:

### A. Advance Payment Batch Preview

- Shows who is included in the initial payment or claim batch.
- Uses the approved assignment roster as the starting point.
- Does not require completed attendance/check-in evidence before batch inclusion by default.
- Shows symbolic amount/rate placeholders only until rate rules are approved.
- Marks included rows as pending post-duty reconciliation.

### B. Post-Duty Reconciliation Preview

- Shows who attended.
- Shows who did not attend or lacks evidence.
- Shows who substituted or was replaced.
- Shows who needs explanation.
- Shows who may require refund, waiver, or offset.
- Does not become final payment truth without finance/admin decision.

These outputs must not be merged into one final payment report.

## Required Inputs

- `person_id`
- `person_name`
- `role`
- `exam_id`
- `exam_date`
- `start_time`
- `end_time`
- `room`
- `assignment_status`
- `checkin_status`
- `confirmation_status`
- `substitution_status`
- `cancellation_status`
- `approved_for_payment`
- `rate_code`
- `payment_period`
- `advance_payment_batch_id`
- `advance_disbursement_status`
- `reconciliation_status`
- `explanation_required`
- `refund_status`
- `offset_next_payment_flag`

## Conceptual Model Options

### Model A - Per Session

```text
advance_amount_preview = approved_roster_session_count x session_rate
```

Preview interpretation:

- Count approved roster sessions for advance batch preview.
- Show rate as a symbolic `session_rate` or `rate_code` only until finance confirms values.
- Missing post-duty evidence creates reconciliation work, not automatic exclusion from advance disbursement.

### Model B - Per Hour

```text
advance_amount_preview = roster_duration_hours x hourly_rate
```

Preview interpretation:

- Derive duration from start/end time only when both are reliable.
- Show rate as symbolic `hourly_rate` or `rate_code`.
- Require rounding rule before any amount preview or final calculation.
- Post-duty attended duration can be reconciled later if policy requires it.

### Model C - Role-Based

```text
advance_amount_preview = approved_roster_unit x role_rate
```

Preview interpretation:

- Use duty role to choose symbolic `role_rate`.
- Chief, assistant, runner, staff, external, and paper-handling roles remain open decisions.
- Post-duty role changes or substitutions are reconciliation cases.

### Model D - Hybrid

```text
payable_amount = sum(role/session/hour rules by duty record)
```

Preview interpretation:

- Applies different symbolic formulas by duty record.
- Most flexible but requires the most rule confirmation.
- Must not be implemented until rule answers are complete.

## Preview Output

- Person-level summary
- Duty-detail ledger
- Exception list
- Audit evidence list
- Approval pending list
- Advance batch inclusion list
- Post-duty reconciliation queue
- Absence explanation list
- Refund/offset candidate list

## Exception Categories

- Missing assignment
- Missing check-in/evidence after duty
- Substitution pending rule
- No-show or absence pending explanation
- Late-arrival pending rule
- Cancelled exam pending rule
- Room change pending rule
- Split/merged room pending rule
- Missing rate code
- Missing payment period
- Missing approval owner
- Refund/offset rule missing

## Existing Data Sources

- `ExamSchedule`
- `Supervision`
- `SwapRequest`
- `CheckinEvent`
- `ExamPickupQrToken`
- `ExamPickupCheckin`
- `PaperDistributionAssignment`
- `ExternalExam`
- `ExternalSupervision`
- Workload duty analytics normalized records

## Implementation Gate

Before code implementation:

- `INVIGILATION_PAYMENT_RULE_ANSWER_INTAKE.md` must be completed.
- `INVIGILATION_PAYMENT_RULE_DECISION_REGISTER.md` must have required decisions closed.
- Data readiness gaps must be resolved or explicitly accepted.
- Tests must cover normal, exception, approval, and export-lock scenarios.
- Advance disbursement and post-duty reconciliation must remain separate views.
- Check-in must not be used as a mandatory pre-payment gate unless finance/admin policy explicitly approves that rule.
