# Invigilation Payment Preview Implementation Readiness Plan

**Date**: 2026-06-02  
**Status**: BLOCKED - PREVIEW ONLY - NOT PAYMENT AUTHORIZATION

## 1. Current Decision

Current decision: `BLOCKED`

- `READY_FOR_PREVIEW_IMPLEMENTATION = NO`
- Final payment readiness: `NO`
- Recommended model: none selected.
- Corrected operating model: advance disbursement from approved roster plus post-duty reconciliation.
- Reason: core finance/admin rule answers are still missing, especially rate/unit/approval/refund/offset rules.

## 2. If Ready

This section is not active yet. If the decision later becomes ready, EMS would need:

- Backend preview service to build a duty-detail ledger.
- Schema/data fields for advance batch status, evidence status, reconciliation status, refund/offset status, rate code, payment period, and approval status.
- Preview endpoint clearly labeled as not authorization.
- Frontend preview page clearly labeled `PREVIEW ONLY - NOT PAYMENT AUTHORIZATION`.
- Preview export, if allowed by owner, watermarked as draft/preview.
- Tests for normal, exception, substitution, approval, and export-lock scenarios.

## 3. If Conditional

This section is not active yet. A conditional future state could allow:

- Duty inventory with no amount fields.
- Symbolic rate-code placeholders only.
- Advance batch roster preview without payable totals.
- Reconciliation queue discovery without refund totals.
- Disabled export and approval actions.

Any conditional implementation must label assumptions explicitly and keep final payment disabled.

## 4. If Blocked

Current blocked questions:

| Topic | Owner | Due Date | Impact |
|---|---|---|---|
| Payment unit | Finance/Admin | TBD | Blocks model selection and calculation basis |
| Rate source | Finance/Admin | TBD | Blocks any amount preview |
| Payable roles | Finance/Admin/Academic Office | TBD | Blocks role mapping |
| Advance roster approval | Admin/Academic Office | TBD | Blocks batch inclusion rule |
| Post-duty evidence/reconciliation requirement | Admin/Academic Office | TBD | Blocks reconciliation logic, not initial batch by default |
| No-show/late/substitution/cancellation rules | Finance/Admin | TBD | Blocks exception behavior |
| Refund/offset rules | Finance/Admin | TBD | Blocks reconciliation closure |
| Approval owner | Faculty leadership/Admin/Finance | TBD | Blocks approval workflow |
| Payment period | Finance/Admin | TBD | Blocks batching |
| Export format | Finance/Admin | TBD | Blocks official/report output |
| Print shop/external handling | Finance/Admin/Print Ops | TBD | Blocks inclusion/exclusion decisions |
| Audit evidence requirement | DPO/Admin/Finance | TBD | Blocks audit-ready payment flow |

## 5. Safety Rules

- Preview only.
- Not payment authorization.
- No official export until approval workflow and export format are confirmed.
- No final payable amount until rates, units, exception, refund/offset, period, and approvals are confirmed.
- Check-in/evidence is post-duty reconciliation input and must not be used as a mandatory pre-payment gate unless explicitly approved.
- Audit evidence is required for every future batch and reconciliation decision.
- Teaching workload compensation must remain excluded.

## 6. 2026-06-02 Model Reset Impact

- Future implementation must separate advance batch preview from post-duty reconciliation queue.
- Advance preview may use approved roster records before attendance evidence is complete, only after roster/rate/period/approval rules are confirmed.
- Reconciliation preview must handle missing check-in, no-show, substitution, explanation, force majeure, refund, waiver, and offset states.
- Current decision remains `BLOCKED` because core rules are still unanswered.
