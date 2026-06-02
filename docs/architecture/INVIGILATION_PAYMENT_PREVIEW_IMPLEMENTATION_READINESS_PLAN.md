# Invigilation Payment Preview Implementation Readiness Plan

**Date**: 2026-06-02  
**Status**: BLOCKED - PREVIEW ONLY - NOT PAYMENT AUTHORIZATION

## 1. Current Decision

Current decision: `BLOCKED`

- `READY_FOR_PREVIEW_IMPLEMENTATION = NO`
- Final payment readiness: `NO`
- Recommended model: none selected
- Reason: all required finance/admin rule answers are missing.

## 2. If Ready

This section is not active yet. If the decision later becomes ready, EMS would need:

- Backend preview service to build a duty-detail ledger.
- Schema/data fields for evidence status, exception status, rate code, payment period, and approval status.
- Preview endpoint clearly labeled as not authorization.
- Frontend preview page clearly labeled `PREVIEW ONLY - NOT PAYMENT AUTHORIZATION`.
- Preview export, if allowed by owner, watermarked as draft/preview.
- Tests for normal, exception, substitution, approval, and export-lock scenarios.

## 3. If Conditional

This section is not active yet. A conditional future state could allow:

- Duty inventory with no amount fields.
- Symbolic rate-code placeholders only.
- Exception discovery without payable totals.
- Disabled export and approval actions.

Any conditional implementation must label assumptions explicitly and keep final payment disabled.

## 4. If Blocked

Current blocked questions:

| Topic | Owner | Due Date | Impact |
|---|---|---|---|
| Payment unit | Finance/Admin | TBD | Blocks model selection and calculation basis |
| Rate source | Finance/Admin | TBD | Blocks any amount preview |
| Payable roles | Finance/Admin/Academic Office | TBD | Blocks role mapping |
| Evidence requirement | Admin/Academic Office | TBD | Blocks preview eligibility logic |
| No-show/late/substitution/cancellation rules | Finance/Admin | TBD | Blocks exception behavior |
| Approval owner | Faculty leadership/Admin/Finance | TBD | Blocks approval workflow |
| Payment period | Finance/Admin | TBD | Blocks batching |
| Export format | Finance/Admin | TBD | Blocks official/report output |
| Print shop/external handling | Finance/Admin/Print Ops | TBD | Blocks inclusion/exclusion decisions |
| Audit evidence requirement | DPO/Admin/Finance | TBD | Blocks audit-ready payment flow |

## 5. Safety Rules

- Preview only.
- Not payment authorization.
- No official export until approval workflow and export format are confirmed.
- No final payable amount until rates, units, evidence, exceptions, and approvals are confirmed.
- Audit evidence is required for every future calculation.
- Teaching workload compensation must remain excluded.

