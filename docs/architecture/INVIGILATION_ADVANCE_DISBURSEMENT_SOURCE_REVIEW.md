# Invigilation Advance Disbursement Source Review

**Date**: 2026-06-02  
**Scope**: EMS invigilation payment only. Teaching workload compensation remains out of scope.

## Documents Read

- `docs/architecture/EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md`
- `docs/architecture/EMS_INVIGILATION_PAYMENT_MODEL.md`
- `docs/architecture/EMS_INVIGILATION_PAYMENT_DATA_REQUIREMENTS.md`
- `docs/architecture/INVIGILATION_PAYMENT_RULE_INTAKE_SOURCE_REVIEW.md`
- `docs/architecture/INVIGILATION_PAYMENT_CURRENT_DATA_AUDIT.md`
- `docs/architecture/INVIGILATION_PAYMENT_PREVIEW_MODEL_SPEC.md`
- `docs/architecture/INVIGILATION_PAYMENT_RULE_COMPLETENESS_AUDIT.md`
- `docs/architecture/INVIGILATION_PAYMENT_MODEL_SELECTION_GATE.md`
- `docs/architecture/INVIGILATION_PAYMENT_PREVIEW_IMPLEMENTATION_READINESS_PLAN.md`
- `docs/architecture/INVIGILATION_PAYMENT_TEST_CASE_MATRIX.md`
- `docs/architecture/EMS_100_PERCENT_MASTER_SCORECARD.md`
- `docs/architecture/EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md`

The requested `INVIGILATION_DUTY_EVIDENCE_*` documents were not present at the start of this pass, so equivalent evidence-ledger documents were created.

## Old Assumption Found

Several payment scaffold documents framed check-in, attendance, or evidence as a prerequisite for payment eligibility or model selection. That framing is incomplete for the current operating model.

Affected documents:

| Document | Old framing to correct | Required reframing |
|---|---|---|
| `INVIGILATION_PAYMENT_PREVIEW_MODEL_SPEC.md` | Preview counted confirmed sessions and treated missing evidence as a payment exception. | Split preview into advance batch preview and post-duty reconciliation preview. |
| `INVIGILATION_PAYMENT_MODEL_SELECTION_GATE.md` | Evidence requirement was a hard gate before preview implementation. | Evidence is still a rule gap, but primarily determines reconciliation and final closure. |
| `INVIGILATION_PAYMENT_PREVIEW_IMPLEMENTATION_READINESS_PLAN.md` | Payment preview blocked by evidence-before-payment assumptions. | Preview remains blocked by missing rates/rules, not by check-in alone. |
| `INVIGILATION_PAYMENT_TEST_CASE_MATRIX.md` | No-show cases implied non-payment could be the immediate outcome. | No-show becomes explanation, review, refund, offset, or waiver workflow. |
| `INVIGILATION_PAYMENT_RULE_FOLLOWUP_QUESTIONS.md` | Asked whether evidence is required before payment eligibility. | Ask whether payment is normally advanced before attendance confirmation and what evidence is reconciled after duty. |
| `INVIGILATION_PAYMENT_RULE_DECISION_REGISTER.md` | PAY-004 described check-in as a payment requirement. | PAY-004 now distinguishes advance roster basis from post-duty evidence review. |
| readiness/demo docs | Stated payment requires confirmed evidence. | State payment calculation still requires rules, while evidence is a reconciliation input. |

## What Remains Valid

- EMS payment means invigilation payment only.
- Teaching workload compensation is excluded.
- No final payment calculation is implemented.
- Existing `compensation` fields and exports are provisional and not payment-authoritative.
- Rate, unit, period, approval, refund, and export rules remain open.
- No production/payment readiness can be claimed.

## Corrected Operational Model

EMS invigilation payment is a two-stage process:

1. **Advance disbursement**: an initial payment or claim batch is prepared from an approved invigilation assignment roster. Check-in or attendance proof is not a mandatory pre-disbursement gate by default.
2. **Post-duty reconciliation**: after the exam duty date, attendance, check-in, substitution, absence, no-show, and explanation evidence are reviewed. Exceptions may lead to explanation requests, finance review, refund tracking, offset against a later payment, waiver, or closure.

## What Must Be Reframed

- Missing check-in should trigger reconciliation, not automatic non-payment.
- No-show should trigger investigation and explanation workflow, not automatic non-payment.
- `DISBURSED_PENDING_RECONCILIATION` must not be interpreted as proof that the person actually invigilated.
- Refund and offset amounts remain pending until rate and finance rules are approved.

