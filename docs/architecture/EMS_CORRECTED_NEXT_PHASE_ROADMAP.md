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

## Payment Document Settings Roadmap Update (2026-06-08)

- Configurable payment-document settings are now implemented for term-specific draft rates and paper-distribution responsible group/person.
- The settings layer is separate from active simple demo/test rates, review records, payment truth, and export logic.
- The next safe branch is connecting approved settings as the source for the official draft preview, if supervisor/finance approves.
- Official payment approval, final authorization, PDF/Excel/export, active-rate changes, and production/payment readiness remain unchanged.

## Settings-Backed Draft Integration Roadmap Update (2026-06-08)

- The selected term's complete active settings now drive official draft-preview amounts.
- Missing/incomplete settings block monetary calculation without using demo/simple-rate fallback.
- Review remains required and the next gate is draft-export design only after review acceptance.
- Approval, final authorization, official export/PDF/Excel, active-rate changes, and readiness remain unchanged.

## Draft Export Design Gate Roadmap Update (2026-06-08)

- Draft export design gate is now defined: `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md`.
- Current gate status: `DRAFT_EXPORT_DESIGN_PENDING`; recommended decision: `HOLD_PENDING_REVIEW_ACCEPTANCE`.
- Stage 7 (Export And Report Package) in this roadmap may only begin after the gate advances to `ALLOW_DRAFT_EXPORT_DESIGN`.
- The gate requires: review status `ACCEPTED_FOR_DRAFT_EXPORT` set by human reviewer, paper-distribution source confirmed, export format decided, and 10 preconditions met.
- Export is not implemented. Final authorization is still blocked. Payment approval is not added.
- Production readiness, payment readiness, and active rates unchanged.
- Next human action: reviewer sets `ACCEPTED_FOR_DRAFT_EXPORT` if appropriate.

## Draft Export Gate Re-Evaluation Roadmap Update (2026-06-08)

- Gate re-evaluation completed. All 10 preconditions passed. Gate advanced to `ALLOW_DRAFT_EXPORT_DESIGN`.
- Stage 7 (Export And Report Package — draft-only) may now begin for DRAFT EXPORT ONLY.
- Official payment export, final authorization, payment approval, and payment release remain blocked.
- Next safe roadmap action: implement backend draft export endpoint + frontend export trigger; write all 57 gate test cases; validate before merging.
- Production readiness, payment readiness, and active rates unchanged.

## Draft Payment Document Export Implementation Note (2026-06-11)

- Draft export endpoint implemented: `POST /api/invigilation-advance-batch/official-document-draft-export`
- Format: xlsx (openpyxl, no new dependency added)
- Gate enforced: 8 preconditions checked before any bytes generated
- Review acceptance required: `ACCEPTED_FOR_DRAFT_EXPORT` + non-empty comment
- Role guard: `require_view_all` (admin/esq_head/secretary only)
- Frontend: export button added, gated behind `latestReviewStatus === ACCEPTED_FOR_DRAFT_EXPORT` and `canManageReview`
- Backend tests: 21 new tests, all pass; full suite 1552/1552
- Frontend build: PASS; i18n EN/TH parity 1953/1953
- Safety flags: `payment_authorization_enabled=false`, `final_export_enabled=false` — unchanged
- Export is read-only: no DB writes, no status mutations
- Final payment approval, final authorization, official export, payment release: still blocked
- Production readiness: unchanged

## Demo/Review Release Candidate RC1 Roadmap Note (2026-06-12)

- `EMS_DEMO_REVIEW_RC_1` is frozen and validated for supervisor/finance demonstration within documented constraints.
- The existing settings-backed draft, persistent review workflow, and review-gated draft XLSX are included.
- Final approval, final authorization, official-final export, payment release, production deployment claims, and workload-presentation work remain outside RC1.
- Exact next gate: run the supervisor/finance demo and capture the human decision on the draft XLSX format.
- Readiness scores remain unchanged.

## RC1 Checklist Completion Routing (2026-06-12)

- Checklist infrastructure and XLSX evidence preparation are complete.
- Saved human checklist findings are not present; effective completion is `0/7`.
- No explicit reviewer decision or identity is recorded.
- Current route remains `HOLD_PENDING_ADDITIONAL_REVIEW`.
- Next safe action: reviewer inspects and saves all relevant checklist findings, reviews the real XLSX, and supplies an explicit decision.
- Final authorization design, final payment approval, and official-final export remain blocked.

## RC1 Draft XLSX Human Decision Hold (2026-06-12)

- No post-RC1 supervisor/finance decision or reviewer identity is recorded.
- Draft XLSX produced-format gate is `HOLD_PENDING_ADDITIONAL_REVIEW`.
- Existing `ACCEPTED_FOR_DRAFT_EXPORT` permits the gated draft workflow only and does not accept the produced RC1 format.
- Final-authorization design remains blocked.
- Exact next action: rerun the supervisor/finance RC1 demo and capture an explicit format decision.
- Readiness scores remain unchanged.

## RC1 Draft XLSX Format Accepted + Supporting Roster Design Opened (2026-06-12)

- Human decision `ACCEPT_DRAFT_XLSX_FORMAT` recorded. Draft XLSX format gate: `DRAFT_XLSX_FORMAT_ACCEPTED`.
- Reviewer identity: `NOT_PROVIDED`. No identity was fabricated.
- Acceptance of the draft XLSX summary format is not payment authorization.
- New requirement opened: `SUPPORTING_FINANCE_INVIGILATION_ROSTER_REQUIRED`.
- A supporting finance invigilation roster export (`DRAFT_FINANCE_INVIGILATION_ROSTER_XLSX`) is required before finance can verify signatures and headcounts.
- 4 design docs created:
  - `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_REVIEW.md`
  - `PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md`
  - `PAYMENT_SUPPORTING_FINANCE_ROSTER_ALGORITHM.md`
  - `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md`
- Supporting roster implementation gate: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`
- 5 items must be confirmed by admin/finance before implementation begins.
- Final authorization design remains `FINAL_AUTHORIZATION_DESIGN_BLOCKED`.
- Payment approval, final authorization, official-final export, payment release: still blocked.
- Production readiness: unchanged.
