# Advance Batch Frontend Page Decision Gate

Date: 2026-06-02

## Decision

`IMPLEMENT_PAGE_NOW`

## Rationale

| Criterion | Result |
|---|---|
| Endpoint validates | Yes |
| Response contract stable | Yes, after adding explicit summary counters |
| Meaningful roster rows available | Yes, 23 rows in local demo data |
| Amounts remain `PENDING_RATE_RULE` | Yes |
| No final approval/export action needed | Yes |
| Clear preview-only labels can be shown | Yes |

## Page Scope

The page may show:

- preview warning banner
- filters for period/year/semester/exam type
- summary counters
- roster table
- blockers
- warnings
- rule gaps

The page must not show:

- approve button
- final payment export
- calculated amount
- refund amount logic
- teaching workload compensation language

## Route And Visibility

- Route: `/invigilation-advance-batch-preview`
- Navigation label: `Advance Batch Preview` / `รายชื่อเตรียมเบิกค่าคุมสอบ`
- Roles: `admin`, `staff`

## Readiness Impact

Frontend implementation is safe as a preview-only operational page. Production/payment readiness remains unchanged until rate, approval, and reconciliation rules are approved.

## Live Smoke Confirmation

- The page rendered successfully in the live browser for admin and staff.
- The 23-row preview contract displayed with `PENDING_RATE_RULE` amounts only.
- Teacher and print shop were blocked from the direct route.
- No approve, final payment, or official export controls were present.
