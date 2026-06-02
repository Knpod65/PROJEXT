# Invigilation Rate Rule Setup Source Review

**Date**: 2026-06-02  
**Scope**: EMS invigilation payment / ค่าคุมสอบ only.

## Docs Read

- `EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md`
- `INVIGILATION_ADVANCE_DISBURSEMENT_MODEL.md`
- `INVIGILATION_POST_DUTY_RECONCILIATION_MODEL.md`
- `ADVANCE_INVIGILATION_BATCH_ROSTER_RECORD_SPEC.md`
- `ADVANCE_INVIGILATION_BATCH_INCLUSION_RULES.md`
- `ADVANCE_BATCH_FRONTEND_LIVE_SMOKE_RESULTS.md`
- `ADVANCE_BATCH_LIVE_SMOKE_VALIDATION_LOG.md`
- `ADVANCE_BATCH_PREVIEW_RESPONSE_CONTRACT.md`
- `INVIGILATION_PAYMENT_PREVIEW_MODEL_SPEC.md`
- `INVIGILATION_PAYMENT_PREVIEW_UI_API_ROADMAP.md`
- `UI_RESIDUAL_AUDIT_EXPLORER_HOTFIX_REPORT.md`
- `EMS_100_PERCENT_MASTER_SCORECARD.md`
- `EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md`

## Confirmed Current State

- EMS payment means invigilation payment only.
- Advance batch roster preview already exists at `GET /api/invigilation-advance-batch/preview`.
- Frontend preview page exists at `/invigilation-advance-batch-preview`.
- Live smoke evidence confirmed 23 roster rows, admin/staff access, teacher/print-shop blocking, and all amount fields remaining `PENDING_RATE_RULE`.
- No final payment calculation, final approval, official export, or production payment workflow exists.

## Why Rate Setup Is Next

The current advance roster can answer who would be included in an advance invigilation batch, but it cannot produce even preview amounts until finance/admin enters a rate rule. A rate-rule setup page and API are therefore the next safe configuration step.

## Must Remain Blocked

- Final payable amount.
- Official payment report or export.
- Final payment approval.
- Advance batch amount integration until a later validated integration pass.
- Any check-in-as-pre-payment gate.
- Any teaching workload, Work H, real teaching hours, opencourse, coinstruc, or excess teaching payment logic.

## Teaching Workload Exclusion

This pass explicitly excludes ค่าสอนเกินภาระงาน, teaching workload compensation, Work H, real teaching hours, course eligibility for teaching pay, co-teaching, thesis/advisor workload, and all extra-teaching workbook workflows.

