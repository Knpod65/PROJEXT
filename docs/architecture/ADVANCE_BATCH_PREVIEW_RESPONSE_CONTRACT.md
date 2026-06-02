# Advance Batch Preview Response Contract

Status: preview-only contract for `GET /api/invigilation-advance-batch/preview`.

## Summary

`summary` contains:

- `preview_only`
- `amount_calculation`
- `amount_calculation_enabled`
- `amount_status`
- `total_rows`
- `total_assignments`
- `ready_for_batch_review`
- `included_in_advance_batch`
- `blocked_missing_assignment_data`
- `blocked_duplicate_duty`
- `blocked_rule_gap`
- `blocked_rows`
- `pending_rate_rule_count`
- `warning_count`

Required invariant:

- `amount_calculation_enabled` must be `false`.
- `amount_status` must be `PENDING_RATE_RULE`.

## Roster Rows

`roster_rows` contains one row per assigned invigilation duty considered by the advance roster preview.

Important fields:

- `duty_id`
- `exam_id`
- `schedule_id`
- `course_code`
- `course_title`
- `section`
- `exam_date`
- `start_time`
- `end_time`
- `room_name`
- `person_id`
- `person_name`
- `person_type`
- `department`
- `duty_role`
- `advance_inclusion_status`
- `inclusion_reason`
- `blocked_reason`
- `rate_rule_status`
- `amount_status`
- `amount_preview`
- `reconciliation_status`
- `post_duty_evidence_status`
- `warnings`

Required invariants:

- `amount_status` must not be `FINAL`, `APPROVED`, or `CALCULATED`.
- `amount_preview` must be `PENDING_RATE_RULE`.
- Missing check-in must not block advance inclusion.
- Reconciliation remains post-duty.

## Blockers, Warnings, Rule Gaps

- `blockers`: string list of blocking issues found in source rows.
- `warnings`: string list of non-blocking review signals.
- `rule_gaps`: string list of finance/admin rules still required before any amount calculation.

## Prohibited Claims

The response must not claim:

- official payment approval
- final payable amount
- final report/export readiness
- production payment readiness
