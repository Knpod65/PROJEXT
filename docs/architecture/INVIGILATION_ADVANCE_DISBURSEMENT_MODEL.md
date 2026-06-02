# Invigilation Advance Disbursement Model

**Date**: 2026-06-02  
**Label**: ADVANCE DISBURSEMENT MODEL - NOT FINAL POLICY APPROVAL  
**Scope**: EMS invigilation payment only.

## Core Principle

Initial payment or claim batch preparation is based on an approved invigilation assignment roster, not necessarily completed attendance confirmation.

Check-in, attendance, substitution, and no-show evidence are post-duty reconciliation inputs unless finance/admin policy explicitly says otherwise.

## Entities

- `approved_exam_duty_assignment`
- `invigilation_payment_period`
- `advance_payment_batch`
- `batch_line_item`
- `person`
- `duty_role`
- `payment_unit`
- `rate_code`
- `approval_record`
- `disbursement_status`
- `reconciliation_status`

## Required Data Before Initial Disbursement

- Exam assignment exists.
- Person is assigned.
- Exam date, time, and room exist.
- Duty role exists.
- Payment period is identified.
- Rate rule is answered.
- Batch is approved by the responsible office.

## Not Required Before Initial Disbursement

- Final attendance confirmation.
- Check-in proof.
- Post-duty explanation.
- Refund decision.

## Advance Disbursement Statuses

| Status | Meaning |
|---|---|
| `NOT_READY_FOR_BATCH` | Assignment exists but cannot enter batch review yet. |
| `READY_FOR_BATCH_REVIEW` | Assignment has enough roster data for review, subject to missing finance rules. |
| `INCLUDED_IN_ADVANCE_BATCH` | Assignment is included in a draft or review payment batch. |
| `ADVANCE_BATCH_APPROVED` | Responsible office approved the advance batch. |
| `DISBURSED_PENDING_RECONCILIATION` | Payment/disbursement happened and the duty must later be reconciled. |
| `REMOVED_BEFORE_DISBURSEMENT` | Assignment was removed before money was disbursed. |
| `BLOCKED_BY_RULE_GAP` | Missing rate, unit, period, approval, or other required rule blocks the batch. |

## Important Interpretation

`DISBURSED_PENDING_RECONCILIATION` does not mean duty was actually performed. It means the person was included in an approved payment batch and must later be reconciled against attendance, substitution, absence, and explanation evidence.

## Still Open

- Payment unit.
- Rate source and rate codes.
- Batch approval owner.
- Payment period and cutoff.
- Refund/offset authority.
- Whether paper handling, print shop, or external duties use the same batch.

