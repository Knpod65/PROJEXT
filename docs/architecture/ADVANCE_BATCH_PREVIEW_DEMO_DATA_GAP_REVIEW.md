# Advance Batch Preview Demo Data Gap Review

Date: 2026-06-02

## Classification

Current demo data produces meaningful roster rows.

| Data Signal | Result |
|---|---|
| Endpoint returns meaningful rows | Yes |
| Endpoint returns empty state | No |
| Endpoint returns blockers | No blockers in current default response |
| Endpoint needs seed data improvement | Not required for this pass |
| Endpoint works only with tests | No; local development data returns 23 rows |

## Observed Demo Response

- `roster_rows`: 23
- `ready_for_batch_review`: 23
- `blocked_rows`: 0
- `warning_count`: 0
- `pending_rate_rule_count`: 23

## Data Notes

- Rows are based on existing demo `ExamSchedule.supervisions`.
- Current sample includes semester `2`, academic year `2568`, exam type `final`.
- No real personal data was inserted or modified in this pass.

## Seed Plan Decision

No separate demo seed plan is needed in this pass because the endpoint returns meaningful preview rows.
