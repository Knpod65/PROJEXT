# Advance Batch Preview Manual Comparison Template

**Status**: Blank independent-review template
**Gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Important**: Finance/admin must enter or paste an independently approved/manual reference. Do not treat system preview rows as the expected answer.

## Instructions

1. Enter the approved/manual reference rows independently.
2. Compare each reference row with the preview-only system result.
3. Select one `match_status` for each reviewed row.
4. Record every mismatch in `ADVANCE_BATCH_PREVIEW_DISCREPANCY_REGISTER.md`.
5. Do not use this template as an official payment export or payment authorization.

Allowed `match_status` values:

- `MATCH`
- `MISMATCH_RATE`
- `MISMATCH_DAY_TYPE`
- `MISMATCH_ROSTER`
- `MISSING_FROM_SYSTEM`
- `EXTRA_IN_SYSTEM`
- `NEEDS_REVIEW`

| row_no | duty_id | person_name | exam_date | normalized_exam_date | day_type | expected_day_type | system_rate | expected_rate | system_preview_amount | expected_amount | match_status | discrepancy_reason | reviewer_note |
|---:|---|---|---|---|---|---|---:|---:|---:|---:|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Comparison Summary

| Metric | Value |
|---|---|
| reviewed_rows |  |
| match_count |  |
| mismatch_count |  |
| needs_review_count |  |
| system_preview_total |  |
| approved_manual_total |  |
| total_difference |  |
| reviewer |  |
| reviewed_at |  |

**Result remains pending until completed and signed by an authorized finance/admin reviewer.**
