# Advance Invigilation Batch Roster Record Spec

**Date**: 2026-06-02  
**Label**: PREVIEW ONLY - NO AMOUNT CALCULATION

One row represents one assigned invigilation duty included in, or considered for, an advance batch roster preview.

## Fields

### Batch

- `advance_batch_id`
- `batch_period`
- `academic_year`
- `semester`
- `exam_period`
- `batch_status`
- `prepared_by`
- `prepared_at`
- `approved_by`
- `approved_at`

### Duty

- `duty_id`
- `exam_id`
- `schedule_id`
- `course_code`
- `course_title`
- `section`
- `exam_date`
- `start_time`
- `end_time`
- `room_id`
- `room_name`

### Person

- `person_id`
- `person_name`
- `person_type`
- `department`
- `duty_role`

### Advance Inclusion

- `advance_inclusion_status`
- `inclusion_reason`
- `blocked_reason`
- `rate_rule_status`
- `amount_status`
- `amount_preview`

### Reconciliation

- `reconciliation_status`
- `post_duty_evidence_status`
- `absence_explanation_status`
- `refund_offset_status`

### Audit

- `source_record_ref`
- `audit_note`

## Allowed Values

`advance_inclusion_status`:

- `READY_FOR_BATCH_REVIEW`
- `INCLUDED_IN_ADVANCE_BATCH`
- `BLOCKED_MISSING_ASSIGNMENT_DATA`
- `BLOCKED_DUPLICATE_DUTY`
- `BLOCKED_RULE_GAP`
- `REMOVED_BEFORE_DISBURSEMENT`

`rate_rule_status`:

- `PENDING_RATE_RULE`
- `RATE_RULE_AVAILABLE`
- `RATE_RULE_CONFLICTING`

`amount_status`:

- `NOT_CALCULATED`
- `PENDING_RATE_RULE`
- `PREVIEW_ONLY`
- `FINAL_BLOCKED`

`amount_preview`:

- blank or `PENDING_RATE_RULE` until rates are confirmed.

`reconciliation_status`:

- `NOT_STARTED`
- `PENDING_POST_DUTY_RECONCILIATION`
- `ATTENDED_CONFIRMED`
- `ABSENT_PENDING_EXPLANATION`
- `REFUND_OFFSET_REVIEW_REQUIRED`
- `CLOSED`

