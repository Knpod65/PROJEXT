# Invigilation Payment Preview Model Spec

**Date**: 2026-06-02  
**Label**: PREVIEW ONLY - NOT PAYMENT AUTHORIZATION  
**Scope**: Invigilation payment (`ค่าคุมสอบ`) only.

## Hard Rule

This document describes possible preview models only. It does not choose a final payment model, does not set rates, does not calculate official payable amounts, and does not authorize payment.

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

## Conceptual Model Options

### Model A - Per Session

```text
payable_amount = confirmed_session_count x session_rate
```

Preview interpretation:

- Count confirmed sessions.
- Show rate as a symbolic `session_rate` or `rate_code` only until finance confirms values.
- Produce exceptions for missing confirmation/evidence.

### Model B - Per Hour

```text
payable_amount = confirmed_duration_hours x hourly_rate
```

Preview interpretation:

- Derive duration from start/end time only when both are reliable.
- Show rate as symbolic `hourly_rate` or `rate_code`.
- Require rounding rule before final calculation.

### Model C - Role-Based

```text
payable_amount = confirmed_unit x role_rate
```

Preview interpretation:

- Use duty role to choose symbolic `role_rate`.
- Chief, assistant, runner, staff, external, and paper-handling roles remain open decisions.

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

## Exception Categories

- Missing assignment
- Missing check-in/evidence
- Substitution pending rule
- No-show pending rule
- Late-arrival pending rule
- Cancelled exam pending rule
- Room change pending rule
- Split/merged room pending rule
- Missing rate code
- Missing payment period
- Missing approval owner

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

