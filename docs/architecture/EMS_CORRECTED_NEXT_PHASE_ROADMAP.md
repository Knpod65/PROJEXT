# EMS Corrected Next-Phase Roadmap

**Date**: 2026-06-02  
**Scope**: Exam scheduling plus invigilation payment only

## Stage 1 - Scope Reset And Terminology Cleanup

- Adopt `EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md` as the mandatory payment/workload guardrail.
- Keep historical docs but mark generic compensation language as invigilation-payment only.
- Do not delete or move files until a later archive review.

## Stage 2 - Confirm Invigilation Payment Rules

- Answer `docs/operations/INVIGILATION_PAYMENT_RULE_QUESTIONS.md`.
- Confirm payment unit, role rates, evidence, exception rules, approval owner, and export format.
- Decide whether current `compensation` fields remain or need compatibility aliases.
- Use `docs/operations/INVIGILATION_PAYMENT_RULE_ANSWER_INTAKE.md` and `docs/operations/INVIGILATION_PAYMENT_RULE_DECISION_REGISTER.md` as the working intake package.
- Current validation gate result: still blocked because all required answers remain pending. Use `docs/operations/INVIGILATION_PAYMENT_RULE_FOLLOWUP_QUESTIONS.md` for the next owner request.

## Stage 3 - Audit Current Duty Assignment And Check-In Data

- Verify exam schedule, room assignment, supervision assignment, role, confirmation, substitution, and cancellation data quality.
- Confirm whether current check-in and attendance records are sufficient for payment evidence.
- Use `docs/architecture/INVIGILATION_PAYMENT_CURRENT_DATA_AUDIT.md` and `docs/architecture/INVIGILATION_PAYMENT_DATA_READINESS_CHECKLIST.md` as the baseline data-readiness package.

## Stage 4 - Build Payment Calculation Preview

- Build read-only preview first.
- Use only confirmed invigilation duty and approved rate rules.
- Include exception list and audit trace.
- Do not write final payment batches in this stage.
- Follow `docs/architecture/INVIGILATION_PAYMENT_PREVIEW_MODEL_SPEC.md`; it is preview-only and not payment authorization.
- Do not begin implementation until `docs/architecture/INVIGILATION_PAYMENT_MODEL_SELECTION_GATE.md` changes from `READY_FOR_PREVIEW_IMPLEMENTATION = NO`.

## Stage 5 - Validate With Sample Exam Period

- Run the preview against a real or approved sample exam period.
- Compare with finance/admin expected outputs.
- Record mismatches and rule adjustments.

## Stage 6 - Payment Approval Workflow

- Add approval status and approval owner workflow.
- Require clear evidence before approval.
- Support reopen/correction rules only if approved by admin/finance.

## Stage 7 - Export And Report Package

- Produce approved Excel and/or PDF outputs.
- Include person-level totals, payable units, amounts, exceptions, and audit references.
- Keep export access role-scoped and audited.

## Stage 8 - Faculty Web Portal Integration

- Faculty web portal/auth can proceed later.
- Invigilation payment rules can be prepared now without auth.
- Do not block rule confirmation on Laravel/POLSCI integration.

## Stage 9 - Production Readiness

- Require pilot evidence, backup/restore evidence, DPO sign-off, monitoring, rollback, and external approvals.
- Do not claim production readiness from a docs-only payment scope reset.

## Guardrails

- Do not continue any teaching workload workbook workflow inside EMS.
- Do not use teaching compensation data as EMS payment input.
- Do not implement payment calculation until rules and tests exist.
- Do not change readiness scores unless backed by validation evidence.

## 2026-06-02 Advance/Reconciliation Correction

- Stage 4 must split future work into advance payment batch preview and post-duty reconciliation preview.
- Check-in/evidence is not a mandatory pre-payment gate by default.
- Evidence is used after duty for reconciliation, absence explanation, refund/offset, and audit closure.
- Payment calculation remains blocked until rate, unit, approval, refund/offset, period, and export rules are answered.

## 2026-06-02 Advance Roster Preview Scaffold

- Add and validate a backend advance roster preview endpoint before any frontend page.
- Keep all amount fields `PENDING_RATE_RULE`.
- Keep post-duty reconciliation separate from advance inclusion.
- Do not proceed to official export or approval workflow until rules are approved.

## 2026-06-02 Advance Batch Preview Validation

- Backend endpoint validation passed with 23 local demo roster rows.
- A preview-only frontend page is now available at `/invigilation-advance-batch-preview`.
- The page does not authorize payment, calculate amounts, or export official reports.
- Next phase remains finance/admin rule confirmation for rates, approval owner, export format, and reconciliation policy.
## Rate Rule Setup Roadmap Update (2026-06-02)

- Current pass: implement configurable invigilation rate-rule setup.
- Decision: do not integrate amount preview into Advance Batch Preview in this pass.
- Next payment phase: validate rate-rule UI/API, then connect active `PER_SESSION` rates to preview-only advance roster amounts.
- Final payment authorization/export remains blocked until approval and reconciliation rules are confirmed.

## Rate Rule Live Smoke Roadmap Update (2026-06-02)

- Rate-rule UI/API validation has now passed authenticated local smoke for the backend contract.
- The next safe implementation phase is a preview-only Advance Batch amount integration using an active `PER_SESSION` rate.
- That next phase must still avoid final payment approval, official export, refund/offset amount logic, and production-readiness claims.

## Advance Batch Finance/Admin Validation Roadmap Update (2026-06-04)

- Preview-only amount integration and its system-side demo evidence are complete.
- The validation packet is ready for independent finance/admin comparison against an approved sample.
- Current gate: `PENDING_FINANCE_ADMIN_REVIEW`; no decision option is preselected.
- Do not begin final approval or official export design until discrepancies are resolved and an authorized reviewer signs the packet.

## Advance Batch Finance Response Intake Roadmap Update (2026-06-04)

- The response-intake and decision-gate path is ready for an authorized finance/admin reviewer.
- The next step is human completion of the comparison, discrepancy register, and signed response intake.
- Gate outcomes route to approval-workflow design, correction and revalidation, clarification, or redesign.
- Current status remains `PENDING_FINANCE_ADMIN_REVIEW`; no approval/export implementation may begin yet.

## Official 2/2568 Sample Alignment Roadmap Update (2026-06-04)

- The future official-style document shape is now modeled with invigilation and paper-distribution committee categories.
- Next human decisions: confirm the applicable rate set, payable paper-distribution source, category unit, and exact grouping rule.
- Current and historical EMS data must be reconciled with an approved row-level source before output implementation.
- Current gate remains `PENDING_FINANCE_ADMIN_REVIEW`; no active rate change, approval workflow, or official export proceeds.

## Rate And Paper-Distribution Decision Capture Roadmap Update (2026-06-05)

- Decision-source review, Thai-first decision capture, and next implementation options are now prepared.
- Current gate remains `PENDING_FINANCE_ADMIN_REVIEW`; decision status remains `DECISION_PENDING`.
- Active rates are not changed; current `300/500` remains unconfirmed for official use.
- Official document output is still blocked until the rate set and paper-distribution payable source are confirmed.
- Payment approval/export is not implemented, and production readiness is unchanged.

## Official Payment Document Draft Preview Roadmap Update (2026-06-05)

- Next implementation is now the in-app 2/2568 official-style draft preview.
- Use term-specific `120/200` and treat active `300/500` as demo/test only.
- Include both invigilation and paper-distribution categories; paper-distribution counts are manual/staff-confirmed and non-persistent.
- Keep the route draft-only with no final payment approval, payment authorization, official export, PDF, or Excel.
- Supervisor/finance review remains the next human gate before final-truth or export work.

## Official Payment Document Draft Validation Roadmap Update (2026-06-05)

- Validation confirms the draft preview is ready to commit with required backend and frontend checks passing.
- `httpx` is declared for reproducible FastAPI `TestClient` coverage.
- Optional i18n coverage script repair is deferred as tooling debt.
- Screenshot evidence is absent because browser tooling was unavailable; route serving was confirmed by HTTP fallback.
- The next roadmap gate remains supervisor/finance review, not payment approval or export.

## Official Payment Document Draft Manual Smoke Roadmap Update (2026-06-05)

- The manual smoke package and supervisor/finance review checklist are ready.
- HTTP fallback confirms the backend and draft route are reachable; authenticated visual smoke and screenshot capture remain blocked by unavailable Chrome automation.
- Current status moves through `PENDING_SUPERVISOR_FINANCE_REVIEW`, with allowed outcomes documented in the decision gate.
- The next phase is human review and authoritative paper-source validation, not final approval, payment authorization, or official export.

## Supervisor / Finance Review Package Roadmap Update (2026-06-08)

- Supervisor/finance review package is prepared for the 2/2568 draft payment document.
- The package is docs-only and supports human decisions on format, rates, paper-distribution source, and whether draft-export design may be planned later.
- Current gate remains `PENDING_SUPERVISOR_FINANCE_REVIEW`; no official approval/export work may start without a real reviewer decision.
- Production readiness, payment readiness, active rates, approval, authorization, and official export remain unchanged.

## Supervisor / Finance Decision Intake And Review Model Roadmap Update (2026-06-08)

- Draft format is accepted for now as `ACCEPT_DRAFT_FORMAT`.
- Next safe roadmap branch is review/comment workflow and configurable payment-document settings, not final authorization or export.
- Rates remain configurable and term-specific; paper-distribution responsible group/person remains configurable with default `Education_Student_Quality`.
- Runtime implementation is deferred until persistent review records, reviewer permissions, and settings ownership are selected.
- Production readiness, payment readiness, active rates, approval, authorization, and official export remain unchanged.

## Persistent Payment Document Review Records Roadmap Update (2026-06-08)

- Persistent review records and the draft-page review panel are now implemented for `ADVANCE_PAYMENT_DRAFT_SUMMARY`.
- The next safe roadmap branch is supervisor/finance use of the review workflow and a later decision on draft-export design.
- `ACCEPTED_FOR_DRAFT_EXPORT` can route to draft-export design only; it is not final authorization.
- Official payment approval, final authorization, PDF/Excel/export, active-rate changes, and production/payment readiness remain unchanged.
