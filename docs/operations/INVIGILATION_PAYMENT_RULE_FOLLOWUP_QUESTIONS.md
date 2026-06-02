# Invigilation Payment Rule Follow-up Questions

**Date**: 2026-06-02  
**Purpose**: Ask only unanswered rule questions needed for preview/final readiness.  
**Scope**: Invigilation payment only. No secrets, personal data, or payment execution requested.

| question_id | topic | question | why needed | answer options | owner | urgency | blocks preview? | blocks final payment? |
|---|---|---|---|---|---|---|---:|---:|
| FUP-001 | Payment unit | What is the payment unit for invigilation duty? | Required to choose Model A/B/C/D. | per exam session; per hour; per day; per exam block; hybrid; other | Finance/Admin | Critical | Yes | Yes |
| FUP-002 | Rate source | Where do approved rates come from, and who approves them? | Existing EMS values are provisional only. | approved rate table; official memo; finance system; other | Finance/Admin | Critical | Yes | Yes |
| FUP-003 | Role rates | Do rates differ by role or person type? | Required for role mapping and preview model. | same all; chief/assistant; staff/lecturer/external; paper roles; other | Finance/Admin | Critical | Yes | Yes |
| FUP-004 | Payable roles | Which exam-operation roles are payable in EMS? | Required to include/exclude duty records. | invigilators only; invigilators + runners; include print/paper; external separately; other | Finance/Admin/Academic Office | Critical | Yes | Yes |
| FUP-005 | Evidence | What roster approval is required before advance batch, and what evidence is reviewed after duty? | Required to distinguish advance disbursement from reconciliation. | approved assignment only for advance; check-in after duty; QR after duty; signature after duty; supervisor approval; combination | Admin/Academic Office | Critical | Yes | Yes |
| FUP-006 | No-show | What reconciliation action is required if an assigned invigilator does not attend after advance disbursement? | Required for absence/refund/offset behavior. | explanation required; refund review; offset review; waiver review; other | Finance/Admin | Critical | Yes | Yes |
| FUP-007 | Late arrival | What happens if an invigilator arrives late? | Required for exception behavior and data capture. | no effect; reduced; manual review; no payment; other | Finance/Admin | High | Yes | Yes |
| FUP-008 | Substitution | If duty is substituted, who receives payment? | Required for swap/emergency cases. | substitute; original; split; manual review; other | Finance/Admin | Critical | Yes | Yes |
| FUP-009 | Cancelled exam | What happens when an exam is cancelled? | Required for cancellation exception behavior. | no payment; pay if present; partial; manual review; other | Finance/Admin | High | Yes | Yes |
| FUP-010 | Room/section changes | Do room changes, merged rooms, or split sections affect payment? | Required for room/section exception behavior. | no effect; new unit; manual review; other | Finance/Admin/Academic Office | Medium | Yes | Yes |
| FUP-011 | Approval owner | Who verifies, approves, exports, and signs payment? | Required for approval workflow. | exam office; finance; academic office; department head; multiple | Faculty leadership/Admin/Finance | Critical | Yes | Yes |
| FUP-012 | Payment period | What is the payment period/cutoff? | Required for batching and summary. | exam day; exam period; semester; fiscal month; custom cutoff | Finance/Admin | Critical | Yes | Yes |
| FUP-013 | Export format | What output format is required? | Required before final report/export design. | Excel; PDF; finance import; person summary; session detail; audit trail | Finance/Admin | High | Yes | Yes |
| FUP-014 | Print shop inclusion | Are print shop or paper-handling duties payable in this EMS payment flow? | Required to include/exclude QR/paper duty evidence. | excluded; included; separate rate; separate report; manual review | Finance/Admin/Print Ops | High | Yes | Yes |
| FUP-015 | External users | How should external exam or external-person payments be handled? | Required for external supervision records. | same batch; separate batch; excluded; manual review | Finance/Admin | High | Yes | Yes |
| FUP-016 | Audit evidence | What audit evidence must be retained before approval/export? | Required for auditable payment workflow. | assignment audit; check-in audit; QR audit; supervisor signoff; all; other | DPO/Admin/Finance | Critical | Yes | Yes |

## Advance Disbursement And Reconciliation Questions Added 2026-06-02

These questions correct the model from evidence-before-payment to advance disbursement plus post-duty reconciliation.

| question_id | topic | question | why needed | answer options | owner | urgency | blocks preview? | blocks final payment? |
|---|---|---|---|---|---|---|---:|---:|
| FUP-017 | Advance timing | Is invigilation payment normally disbursed before post-duty attendance confirmation? | Required to confirm advance batch behavior. | yes; no; sometimes; depends on period; other | Finance/Admin | Critical | Yes | Yes |
| FUP-018 | Roster approval | What roster approval is required before advance disbursement? | Required to decide batch inclusion basis. | exam office approval; department approval; finance approval; multiple; other | Admin/Finance | Critical | Yes | Yes |
| FUP-019 | Post-duty evidence | What evidence is reviewed after the exam? | Required for reconciliation queue design. | check-in; signature; supervisor note; QR; substitution record; all; other | Admin/Academic Office | Critical | Yes | Yes |
| FUP-020 | Explanation deadline | How long after duty should absence explanation be submitted? | Required for absence workflow deadlines. | same day; 1 working day; 3 working days; 7 days; other | Admin/Finance | High | Yes | Yes |
| FUP-021 | Explanation reviewer | Who reviews absence/no-show explanation? | Required for case routing and authority. | exam office; supervisor; department head; finance; committee; other | Faculty leadership/Admin | Critical | Yes | Yes |
| FUP-022 | Force majeure | What counts as force majeure or unavoidable absence? | Required for accepted absence labels. | illness; emergency; official duty conflict; admin error; case-by-case; other | Faculty leadership/Admin/Finance | Critical | Yes | Yes |
| FUP-023 | Refund trigger | When is refund required after advance disbursement? | Required for reconciliation outcome. | unaccepted absence; no explanation; late beyond threshold; substitute paid; other | Finance/Admin | Critical | Yes | Yes |
| FUP-024 | Offset allowed | Can refund be offset against a next payment? | Required for finance tracking model. | yes; no; case-by-case; only with written approval | Finance/Admin | High | Yes | Yes |
| FUP-025 | Refund/offset signer | Who signs refund or offset decision? | Required for audit and authority. | finance; department head; exam office; committee; other | Finance/Admin/Faculty leadership | Critical | Yes | Yes |
| FUP-026 | Substitute after advance | How should substitute invigilation affect the original payee if original was already paid? | Required for original/substitute reconciliation. | original refunds; substitute paid separately; offset; manual review; other | Finance/Admin | Critical | Yes | Yes |
| FUP-027 | Unrecorded substitute | If a substitute was not recorded before exam, how is it handled? | Required for emergency/manual cases. | accept supervisor confirmation; require letter; finance review; reject; other | Admin/Finance | High | Yes | Yes |
| FUP-028 | Reconciliation report | What report is needed for reconciliation? | Required for future report/export design. | exception list; person summary; refund tracker; offset tracker; audit report; all; other | Finance/Admin | High | Yes | Yes |
