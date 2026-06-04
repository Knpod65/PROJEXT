# Advance Batch Preview Correction Backlog

**Status**: Blank template
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Purpose**: Track corrections required by an actual finance/admin validation response.

Allowed `status` values:

- `OPEN`
- `IN_PROGRESS`
- `FIXED_PENDING_VALIDATION`
- `VALIDATED`
- `DEFERRED`
- `REJECTED`

| correction_id | source_decision | discrepancy_id | issue_type | severity | description | expected_change | owner | status | validation_required | notes |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |

## Backlog Rules

- Create entries only from a genuine finance/admin response or recorded discrepancy.
- Corrections must not silently redefine finance policy.
- `FIXED_PENDING_VALIDATION` does not permit approval/export design.
- A correction may become `VALIDATED` only after independent rerun evidence.
- This backlog does not authorize payment or official export.
