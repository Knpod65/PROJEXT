# Advance Batch Preview Discrepancy Register

**Status**: Open template
**Purpose**: Record differences found during independent finance/admin comparison of preview-only invigilation amounts.

Allowed `issue_type` values:

- `RATE_MISMATCH`
- `DAY_TYPE_MISMATCH`
- `ROSTER_INCLUSION_MISMATCH`
- `MISSING_EXAM_DATE`
- `INVALID_EXAM_DATE`
- `BE_NORMALIZATION_ISSUE`
- `DUPLICATE_DUTY`
- `OTHER`

Allowed `status` values:

- `OPEN`
- `UNDER_REVIEW`
- `RESOLVED`
- `DEFERRED`
- `NOT_AN_ISSUE`

| discrepancy_id | severity | duty_id | person_name | issue_type | system_value | expected_value | likely_cause | owner | status | resolution_note |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |

## Register Rules

- Keep unresolved differences visible.
- Do not change preview logic solely to make totals match without confirming the approved rule.
- A resolved discrepancy must include its evidence and reviewer.
- Closing this register does not authorize payment; separate approval and export workflows remain unimplemented.
