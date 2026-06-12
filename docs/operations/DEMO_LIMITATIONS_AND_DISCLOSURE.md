# DEMO_LIMITATIONS_AND_DISCLOSURE.md

## 2026-06-11 UI Alignment Disclosure

- The payment document remains `DRAFT_NOT_AUTHORIZED`.
- `ACCEPTED_FOR_DRAFT_EXPORT` permits only gated draft XLSX output for review.
- Draft XLSX is not official/final export, payment approval, final authorization, or final truth.
- Workload routes were visually inventoried but not changed in this alignment pass.
- Production readiness scores remain unchanged.

**Date**: 2026-05-25  
**Audience**: All internal and external stakeholders for standalone EMS demo.

## What This Demo Proves

- EMS is a **substantial, mature institutional platform** (not a prototype).
- Core operational flows (schedule, submissions, print, checkins, import) work for multiple roles.
- Rich intelligence layer (Admin Intelligence, Workload fairness, Governance, Audit, Operational Health, Executive Analytics) is functional and data-driven.
- Role-based access, Thai/English i18n (1688 keys), and modern React architecture are production-grade.
- Recent polish (legacy hidden from demo nav, bundle improved to 560 kB, clean validation) makes it suitable for controlled stakeholder walkthroughs.
- Demo readiness: **96/100** (standalone).
- Workload screens, if shown, demonstrate exam duty workload only: invigilation, paper distribution, and related exam-operation duties.

## What This Demo Does NOT Prove

- **Faculty LAN / Laravel integration**: 0% implemented. Contract questions (203-line document) remain completely unanswered. Auth bridge not started (correctly — per all prior audits).
- **Real PostgreSQL + backup/restore**: Using local SQLite for this demo. No target Faculty DB, no executed backup evidence.
- **DPO / PDPA sign-off**: Policies and templates exist. No signed retention or CMU email flow approval for external auth.
- **Production readiness**: 28/100. No live environment, no load testing, no monitoring, no incident response proof.
- **Pilot readiness**: 42/100. Blocked by the above external items.
- **Full data volume / scale**: Seeded data only. Real semester + historical data not present.
- **Final invigilation payment calculation**: Not proven in this demo. Payment requires confirmed rate, evidence, exception, approval, and export rules.
- **Teaching workload compensation**: Explicitly out of scope. EMS does not calculate excess teaching pay, course eligibility for teaching payment, base workload, co-teaching payment, or thesis/advisor workload payment.
- **Payment rule intake**: Documentation scaffolding exists for rule collection and preview design only. It does not authorize payment or produce real payable amounts.
- **Payment preview readiness**: Current validation says payment preview implementation is not ready because all required rule answers remain pending.

## Explicit Scope Statement (Must Be Said in Every Demo)

"This is a **standalone EMS demo** using local seeded data and local authentication.  
Faculty LAN deployment, POLSCI OAuth / Laravel integration, real PostgreSQL, backup evidence, and DPO sign-off are **out of scope** for today's session and remain open items requiring IT and owner responses.  
Payment in EMS means invigilation payment only; teaching workload compensation is not part of this system.  
Any payment discussion today is preview/intake only until finance/admin confirms the rules.  
Current rule validation found no approved payment answers, so no payment preview or final payment claim should be made.  
We are not claiming pilot or production readiness."

## Why This Demo Is Still Valuable

- Proves the platform depth and architecture quality.
- Allows stakeholders to experience the new intelligence dashboards and role journeys.
- Demonstrates transparency: we show exactly what is ready (96/100 demo) and what is not (external dependencies).
- Provides a clean baseline before any future redesign or integrated pilot work.

## Con-1 / External Issues

Any external system integration issues (con-1) are explicitly excluded from this demo scope unless the stakeholder session specifically includes them (in which case they will be called out separately).

---
*Use this note as a handout or slide. Honesty builds trust.*

## Invigilation Payment Model Correction (2026-06-02)

- Payment model documentation has been corrected to advance disbursement plus post-duty reconciliation.
- Missing check-in is a reconciliation trigger, not an automatic pre-payment block.
- No real amount, official payment report, refund, or offset decision is implemented for demo.
- Advance roster preview, if shown, must be described as no-amount roster review, not payment authorization.

## Advance Batch Preview Demo Disclosure (2026-06-02)

- The advance batch roster page is now available as a preview-only operational view.
- It may be shown to demonstrate roster review, blockers, warnings, and unresolved rule gaps.
- `PENDING_RATE_RULE` is intentional and means no payment amount has been calculated.
- The page must not be presented as payment authorization, final export, or production-ready finance output.

## Advance Batch Live Smoke Disclosure (2026-06-02)

- The preview page was live-smoke verified in the browser for admin and staff.
- Teacher and print shop were blocked from the direct route as intended.
- Screenshot evidence was captured in `docs/operations/demo-smoke-screenshots/`.
- This pass does not implement payment calculation, approval, or official export.
## Invigilation Rate Rule Demo Limitation (2026-06-02)

- Rate-rule setup may be shown as configuration only.
- A saved or active rate does not authorize real payment.
- Advance Batch Preview may still show `PENDING_RATE_RULE` until a later integration pass.
- No final payment report, approval, or export should be demonstrated as complete.

## Invigilation Rate Rule Live Smoke Disclosure (2026-06-02)

- Local authenticated smoke verified admin can create, activate, and archive a demo rate rule.
- Staff can view but not mutate; teacher and print shop are blocked.
- The demo rate is configuration evidence only and is not payment authorization.
- No official export, final approval, or final payment calculation is available.

## Simple Weekday/Weekend Rate UI Disclosure (2026-06-04)

- The main rate page now accepts only one weekday and one weekend amount per invigilation session.
- Genuine browser smoke verified admin save/persistence, staff read-only mode, and teacher/print-shop blocking.
- The configured `300/500` local demo pair is configuration evidence only.
- No Advance Batch amount calculation, payment authorization, final approval, or official export is available.

## Advance Batch Preview Amount Disclosure (2026-06-04)

- The Advance Batch page may now show preview-only amounts from the configured weekday/weekend pair.
- The current local demo total is `7,300 THB` across 23 ready roster rows; it is not payment authorization or a final payable amount.
- Buddhist Era dates are normalized only for weekday/weekend classification.
- Missing/incomplete rates and blocked roster rows do not receive preview amounts.
- No final approval, official export, refund/offset amount, or production payment workflow is available.

## Advance Batch Finance/Admin Validation Disclosure (2026-06-04)

- A finance/admin validation packet and independent comparison template are prepared, but no finance/admin reviewer has approved the preview logic or total.
- The `7,300 THB` result is a system-side demo snapshot only and must not be presented as an official payment list.
- The validation gate remains `PENDING_FINANCE_ADMIN_REVIEW`.
- Final payment approval, authorization, official export, and production readiness remain unavailable.

## Advance Batch Finance Response Intake Disclosure (2026-06-04)

- Response intake and gate-routing templates are ready, but they contain no submitted finance/admin response or signature.
- Any future acceptance validates preview logic only and does not authorize payment.
- Approval-workflow design and official export remain blocked while the gate is `PENDING_FINANCE_ADMIN_REVIEW`.
- Demo, pilot, production, and payment readiness remain unchanged.

## Official 2/2568 Payment Sample Alignment Disclosure (2026-06-04)

- A historical official-style summary was supplied as a user transcription; the original source image is not available for provenance verification.
- The sample uses `120/200`, while a user-stated prior draft uses `150/200` and the active local demo uses `300/500`.
- Paper-distribution operational data exists, but it is not validated as an official payable source.
- No rate was changed, no official document was generated, and payment approval/export remain unavailable.

## Rate And Paper-Distribution Decision Capture Disclosure (2026-06-05)

- A decision capture form now exists for selecting the rate and paper-distribution source before any official output work.
- The gate remains `PENDING_FINANCE_ADMIN_REVIEW`, and the decision status is still `DECISION_PENDING`.
- Active rates are unchanged; the current `300/500` demo/system rate is not confirmed as official.
- Official document output remains blocked until both rate and paper-distribution source are confirmed.
- Payment approval/export is still not implemented, and production readiness is unchanged.

## Official Payment Document Draft Preview Disclosure (2026-06-05)

- The new in-app preview may show a 2/2568 official-style draft table using fixed term-specific `120/200`.
- Active `300/500` remains demo/test data and is not the official reference for this draft.
- Paper-distribution counts are manual/staff-confirmed draft inputs and are not saved.
- The preview status is `DRAFT_NOT_AUTHORIZED`; it must not be demonstrated as final payment, official truth, or export readiness.
- No final approval, payment authorization, official export, PDF, Excel, or production payment workflow is available.

## Official Payment Document Draft Validation Disclosure (2026-06-05)

- The draft preview passed backend and frontend validation for commit readiness.
- Demo presentation may cite test/build readiness, but must also disclose that screenshot evidence was not captured because browser tooling was unavailable.
- The optional i18n coverage script remains tooling debt and is not evidence of payment feature failure.
- The feature is still a draft preview only and must not be presented as approved payment output.

## Official Payment Document Draft Manual Smoke Disclosure (2026-06-05)

- A supervisor/finance review checklist and decision gate are now available for the draft preview.
- Backend health and draft route HTTP checks passed, but authenticated visual smoke and screenshot capture remain unavailable because Chrome automation could not attach.
- The preview must still be disclosed as `DRAFT_NOT_AUTHORIZED` and `PENDING_SUPERVISOR_FINANCE_REVIEW`.
- No payment approval, payment authorization, official export, PDF, Excel, or production payment readiness is available.

## UI System Alignment Disclosure (2026-06-05)

- EMS pages have been visually aligned around a shared minimal institutional template.
- This is a presentation consistency pass only; it does not add payment approval, final authorization, PDF/Excel/export, rate changes, or production readiness.
- Build and required i18n checks passed, but screenshot evidence was not captured in this pass.
- Demo operators should still disclose draft/preview status on payment and document pages.

## UI Screenshot Review Disclosure (2026-06-05)

- Automated screenshot evidence for 10 aligned routes was reviewed after capture.
- Result: `HUMAN_VISUAL_QA_PASSED_WITH_MINOR_ISSUES`; P0 `0`, P1 `0`, P2 `3`.
- Remaining P2 items did not block demo review and were later handled in the 2026-06-08 targeted P2 pass.
- Payment/document pages must still be presented as preview/draft only; no final payment approval, payment authorization, official export, PDF, or Excel output is available.
- No code, payment logic, rate logic, approval/export, or production readiness changed.

## Targeted P2 UI Polish Disclosure (2026-06-08)

- The three known raw-looking label/status P2 items were fixed and validated by frontend build plus required i18n checks.
- Reconciliation route smoke passed for the three affected pages; final UI QA state is `HUMAN_VISUAL_QA_PASSED_ACCEPTED_FOR_SUPERVISOR_REVIEW`.
- This was a display/i18n polish pass only; no backend, payment logic, rate logic, approval/export, final authorization, or production readiness changed.
- Payment/document pages must still be presented as preview/draft only.

## Supervisor / Finance Review Package Disclosure (2026-06-08)

- A Thai-first supervisor/finance review package is prepared for the draft payment document.
- The package supports review and decision capture only; it does not approve payment, export, PDF, Excel, final truth, or production readiness.
- The draft remains `DRAFT_NOT_AUTHORIZED`; reviewer decision and authoritative paper-distribution source validation remain the next human gates.

## Supervisor / Finance Decision Intake And Review Model Disclosure (2026-06-08)

- The draft format has been accepted for now, but every payment-related document still requires review/comment before official use.
- Rates and paper-distribution responsibility must remain configurable; `Education_Student_Quality` is a configurable default, not a permanent hardcoded source.
- No payment approval, final authorization, official export/PDF/Excel, rate change, or production readiness is added.

## Persistent Payment Document Review Records Disclosure (2026-06-08)

- The official payment draft page can now store persistent review comments and review status history.
- Stored review records are draft-review evidence only and remain separate from payment calculation and paper-distribution truth.
- `DRAFT_NOT_AUTHORIZED` remains the visible document status; `ACCEPTED_FOR_DRAFT_EXPORT` does not authorize payment.
- No approval, final authorization, official PDF/Excel/export, active-rate change, or production readiness is added.

## Payment Document Review Panel Live Smoke Disclosure (2026-06-08)

- Live API and browser smoke verified the draft-page review panel, review history, and screenshot evidence.
- Admin can record reviewer status; staff can record preparer/comment review notes but cannot accept the draft for export design.
- `ACCEPTED_FOR_DRAFT_EXPORT` must be explained as draft-export-design readiness only, not payment authorization.
- No final payment approval, official export, PDF, Excel, final authorization, final truth, rate change, or production readiness is added.

## Payment Document Settings Disclosure (2026-06-08)

- EMS now has configurable term-specific settings for draft payment-document rates and paper-distribution responsible group/person.
- `Education_Student_Quality` is a configurable default suggestion, not a permanent hardcoded sole source.
- Settings support draft preparation and traceability only; they do not authorize payment, final truth, official PDF/Excel/export, or review bypass.
- Active simple demo/test rates remain unchanged, and production/payment readiness is not increased.

## Payment Document Settings Live Smoke Disclosure (2026-06-08)

- Live API and browser smoke verified settings persistence, role access, and three real screenshot evidence files.
- Admin can edit draft settings; staff can review saved settings without a save action; unrelated roles remain blocked.
- The official draft displays settings as context only and remains `DRAFT_NOT_AUTHORIZED`.
- No payment calculation, approval, final authorization, official export/PDF/Excel, active simple-rate, or production-readiness change is introduced.

## Settings-Backed Draft Integration Disclosure (2026-06-08)

- The official draft preview now calculates from complete active term-specific payment-document settings.
- Missing/incomplete settings display counts but block monetary amounts; demo rates are not used as fallback.
- The page remains `DRAFT_NOT_AUTHORIZED` and review-required.
- No approval, final authorization, official export/PDF/Excel, final truth, or production-readiness increase is available.

## Draft Export Design Gate Disclosure (2026-06-08)

- A draft export design gate document has been created to define the exact conditions and boundaries for a future draft export workflow.
- Current gate status: `DRAFT_EXPORT_DESIGN_PENDING`; recommended decision: `HOLD_PENDING_REVIEW_ACCEPTANCE`.
- Draft export is NOT implemented. No export button, PDF generation, Excel generation, or export endpoint has been added.
- Payment approval is NOT added. Final authorization is NOT added.
- Production, pilot, and payment readiness scores are unchanged.
- Demo operators must disclose: export is not available; the page remains `DRAFT_NOT_AUTHORIZED`; final authorization is still blocked.
- Next human action: authorized supervisor/finance reviewer sets review status to `ACCEPTED_FOR_DRAFT_EXPORT` at `/invigilation-payment-document-draft` if the draft format is appropriate.

## Draft Export Gate Re-Evaluation Disclosure (2026-06-08)

- Gate re-evaluation completed. Review acceptance confirmed via live API (review_id 4, reviewer `นางสาว มาธวี เมืองศรี`). Gate advanced to `ALLOW_DRAFT_EXPORT_DESIGN`.
- Draft export is STILL NOT implemented. No export button, PDF, Excel, or export endpoint has been added.
- Payment approval is NOT added. Final authorization is NOT added.
- `DRAFT_NOT_AUTHORIZED` remains the document status.
- Demo operators must still disclose: export is not yet available; page is `DRAFT_NOT_AUTHORIZED`; final authorization still blocked.
- Production, pilot, and payment readiness scores are unchanged.

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

## Narrow P2 Payment UI And Role Evidence Disclosure (2026-06-11)

- Real screenshots confirm admin and staff payment-document states, staff read-only settings, and blocked teacher/print-shop states.
- Demo operators must continue to describe XLSX output as a gated review draft only.
- `DRAFT_NOT_AUTHORIZED` remains required; official/final export, payment approval, and final authorization remain unavailable.
- Broad legacy/custom operational-page polish and workload-route presentation remain deferred.
- No backend, payment, settings, review, permission, export-gate, or readiness change is introduced.

## Targeted Legacy Operational Polish Disclosure (2026-06-11)

- Submissions, swaps, print review, external exams, rooms, and periods now have improved localized presentation and clearer route states.
- Six real screenshots support the visual result.
- Workload routes and larger data-sensitive legacy routes remain deferred.
- Demo operators must continue to present the payment document as `DRAFT_NOT_AUTHORIZED`; draft XLSX is review-gated and non-authorizing.
- No backend, permission, business-logic, payment/export/review/settings, workload-domain, or readiness change is introduced.

## EMS Demo/Review RC1 Disclosure (2026-06-12)

- `EMS_DEMO_REVIEW_RC_1` is validated for a supervised demo/review only.
- The demo may show term settings, settings-backed draft calculation, review history, and a review-gated XLSX draft export.
- Every operator must state that the payment document remains `DRAFT_NOT_AUTHORIZED`.
- Draft XLSX is not official-final export, payment approval, final authorization, or payment release.
- Workload presentation remains deferred; production deployment and production-auth readiness are not claimed.
- Readiness scores remain unchanged.
- Next human action: run the supervisor/finance demo and capture the decision on the draft XLSX format.

## RC1 Draft XLSX Decision Hold Disclosure (2026-06-12)

- No post-RC1 supervisor/finance decision or reviewer identity has been supplied.
- The produced draft XLSX format remains `HOLD_PENDING_ADDITIONAL_REVIEW`.
- `ACCEPTED_FOR_DRAFT_EXPORT` must not be presented as acceptance of the produced RC1 file format.
- Final-authorization design, final approval, official-final export, and payment release remain blocked.
- Next human action: rerun the demo and capture an explicit decision with reviewer identity.

## Full UI Regression Closure Disclosure (2026-06-11)

- Full route regression completed with `44/44` renderable URLs returning HTTP `200` and eight new real screenshots.
- No P0/P1 UI blockers remain; residual P2 presentation work is documented and non-blocking.
- Workload presentation remains excluded and product-sensitive routes remain deferred.
- Payment documents remain `DRAFT_NOT_AUTHORIZED`; draft XLSX remains review-gated and non-authorizing.
- No backend, permission, business-logic, payment/export/review/settings, workload-domain, or readiness change is introduced.

## In-System XLSX Review Checklist Disclosure (2026-06-12)

- The payment draft page now includes a persistent seven-step inspection checklist for supervisor/finance review evidence.
- Checklist completion does not accept the XLSX format, authorize payment, enable final authorization, or change the existing draft-export gate.
- A real gated RC1 XLSX sample and structural visual evidence are available for the next demo.
- The produced-format decision remains `HOLD_PENDING_ADDITIONAL_REVIEW`; reviewer identity remains `NOT_PROVIDED`.
- Readiness scores remain unchanged.
