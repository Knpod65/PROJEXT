# EMS_100_PERCENT_IMPROVEMENT_BACKLOG.md

**Date**: 2026-05-25  
**Derived from**: All 100% scorecards + MISSING_WORK_REGISTER + HARDENING_TRIAGE + source review

## Prioritized Backlog (P0 = blocks demo, P1 = blocks pilot, P2 = blocks prod, P3 = post-pilot, P4 = nice-to-have)

## Scope Reset Note (2026-06-02)

This backlog is now constrained by `EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md`.

- EMS payment means invigilation or exam-supervision payment only.
- EMS workload means exam duty workload only.
- Teaching workload compensation, excess teaching pay, co-teaching payment, thesis/advisor workload, base workload, and course eligibility for teaching pay are explicitly out of scope.
- Payment implementation work must wait until invigilation rate, evidence, exception, period, and approval rules are confirmed in `docs/operations/INVIGILATION_PAYMENT_RULE_QUESTIONS.md`.

## Payment Intake Backlog Note (2026-06-02)

- Rule intake and preview scaffolding docs are available for finance/admin review.
- Add no payment code until `INVIGILATION_PAYMENT_RULE_DECISION_REGISTER.md` has the required decisions closed.
- Treat any future payment work as preview-first, with no official report/export until evidence and approval rules are confirmed.

## Payment Validation Gate Backlog Note (2026-06-02)

- Rule validation found all required payment rule answers still missing.
- Payment preview implementation is blocked until the follow-up questions are answered.
- Final payment remains blocked until answers are approved and data gaps are closed.
- No payment implementation task should start from the current register state.

| Task ID | Area | Task | Current % Impact | Required For | Owner | Dependency | Effort | Risk | Acceptance Criteria |
|---------|------|------|------------------|--------------|-------|------------|--------|------|---------------------|
| T001 | Auth | Send LARAVEL_AUTH_CONTRACT_QUESTIONS.md + closure tracker to real Laravel/IT owner and obtain verified answers | 25 → 70 (pilot) | Pilot 100 | EMS + IT/Laravel owner | None | 1-3 days | Low | All 20+ questions answered + code-verified |
| T002 | DB | Confirm + provision real Faculty LAN PostgreSQL target (separate EMS DB recommended) + credentials + backup owner | 62 → 80 | Pilot 100 | IT/DBA + EMS | T001 (mount path) | 1-2 days | Low | Working DATABASE_URL on target; no sqlite fallback |
| T003 | Ops | Execute backup + restore on target DB; attach evidence to BACKUP_RESTORE_TEST_EVIDENCE.md + PILOT_BLOCKER_DASHBOARD | 35 → 75 | Pilot 100 | IT/Ops | T002 | 0.5-1 day | Low | Timings + logs + success proof signed |
| T004 | PDPA | Obtain DPO sign-off on data processing (incl. CMU email via Laravel) using DPO_RETENTION_SIGNOFF_TEMPLATE | 70 → 85 | Pilot 100 | DPO + EMS owner | T001 | 1-3 days | Medium | Signed template attached |
| T005 | Backend | Unify all remaining ENV vs ENVIRONMENT checks (pdpa_runtime_guard_service etc.); remove login body token | 78 → 88 (security) | Pilot 100 | Backend | None | 0.5 day | Low | grep clean; tests pass; security audit sign-off |
| T006 | Frontend | Hide all legacy (non-V2) pages from demo navigation; fix real raw strings in AdminIntelligence/AuditExplorer/Checkins | 76 → 90 (demo) | Demo 100 | Frontend | None | 1 day | Low | Demo script + build + i18n raw scan clean for demo paths |
| T007 | Frontend | Expand manualChunks or route splitting to bring main bundle <500 kB + add bundle analyzer to CI | 65 → 80 (perf) | Demo/Pilot | Frontend | None | 1-2 days | Low | Build warning gone; analyzer report in CI |
| T008 | Testing | Add frontend unit/component tests for 5 critical role flows + basic E2E smoke for demo journeys | 71 → 82 | Pilot 100 | FE + QA | None | 3-5 days | Medium | Tests in CI; >80% of key paths covered |
| T009 | Backend | Adopt Alembic (or equivalent) + formal migration ownership contract with Faculty DBA | 45 → 80 (DB) | Production 100 | Backend + DBA | T002 | 2-4 days | Medium | First migration via tool; DBA sign-off |
| T010 | Security | Integrate secret manager (or Faculty vault) + prove rotation for pilot+ | 72 → 90 (security) | Production 100 | Security + IT | T001 | 3-5 days | High | No env secrets in prod; rotation runbook + evidence |
| T011 | UX | Workload fairness humanization pass + mobile/responsive hardening on top 5 heavy pages + a11y audit | 74 → 88 (UX) | Pilot 100 | UX + Product | None | 5-8 days | Low | Usability test with 3 real users per role; a11y gate |
| T012 | Demo | Full local rehearsal using LOCAL_REHEARSAL_PREFLIGHT + update screenshot atlas + DEMO_USER_JOURNEY_SCRIPT | 87 → 100 (demo) | Demo 100 | EMS team | T006 | 1-2 days | Low | Rehearsal report + updated assets + no crashes |
| T013 | Pilot | Execute UAT with real faculty users on target env; update UAT_GO_NO_GO + PILOT_BLOCKER_DASHBOARD | 42 → 95 (pilot) | Pilot 100 | Pilot coordinator | T001-T004, T012 | 2-4 days | Medium | Signed Go/No-Go + all blockers closed |
| T014 | Post-pilot | Usage-based cleanup of legacy pages + archive historical docs (after 4 weeks pilot traffic) | 55 → 85 (cleanup) | Post-pilot | All | Pilot data | 3-5 days | Low | Zero-traffic pages archived; docs consolidated |
| T015 | Production | Full hardening, CI/CD on real infra, load test, monitoring, incident response drill, external security audit, rollback proven | 28 → 95 (prod) | Production 100 | All + auditors | All prior | 4-8 weeks | High | Production env live + all evidence + sign-offs |

**P0 (Demo blockers)**: T006, T007 (partial), T012  
**P1 (Pilot blockers)**: T001–T005, T008, T011, T013  
**P2 (Production)**: T009, T010, T015 + all P1  
**P3**: T014  
**P4**: Nice-to-haves (bundle size further, extra a11y, etc.)

**Total actionable tasks identified in this pass**: 15 (prioritized above). More will emerge after T001 answers arrive.

---
*This backlog is the single prioritized list. Do not start work outside it without updating this doc.*

## Invigilation Advance/Reconciliation Model Reset (2026-06-02)

- Future payment backlog work must separate advance batch preview from post-duty reconciliation.
- Do not use check-in as an automatic pre-payment gate unless finance/admin explicitly approves that policy.
- Add future work for absence explanation, force majeure review, refund/offset tracking, and reconciliation reporting.
- Keep final calculation blocked until rate, unit, refund/offset, approval, period, and export rules are answered.

## Advance Roster Preview Scaffold Backlog Note (2026-06-02)

- Backend preview scaffold may show roster inclusion only.
- No amount, approval, export, refund, or offset task should be added until finance/admin rules are closed.
- Frontend page was deferred during the scaffold pass until endpoint validation could be completed.

## Advance Batch Preview Validation Backlog Note (2026-06-02)

- Endpoint validation is complete and the frontend preview page is implemented.
- Keep the page read-only and preview-only until rate, approval, export, and reconciliation rules are approved.
- Next backlog item is policy closure, not amount calculation.
- Do not add official export, approve, refund, or offset actions from this page without a new rule-confirmation pass.

## Advance Batch Live Smoke Backlog Note (2026-06-02)

- The preview page is now live-smoke verified in the browser for admin and staff.
- Teacher and print shop were blocked from the direct route as intended.
- Screenshot evidence exists in `docs/operations/demo-smoke-screenshots/`.
- No backlog reprioritization is needed; policy closure remains the next step.
## Invigilation Rate Rule Setup Backlog Note (2026-06-02)

- Completed: configuration-only setup for invigilation payment rate rules.
- Remaining: connect active `PER_SESSION` rate to preview-only advance batch amounts in a later integration pass.
- Remaining: final payment approval, official export, reconciliation/refund/offset closure, and production deployment evidence.
- Excluded: teaching workload compensation, Work H, real teaching hours, opencourse/coinstruc import, and extra-teaching payment rules.

## Invigilation Rate Rule Live Smoke Backlog Note (2026-06-02)

- Completed: local authenticated smoke for rate-rule setup.
- Verified: admin lifecycle, staff read-only, teacher/print-shop blocking, invalid-input rejection.
- Remaining: browser screenshot capture when authenticated browser tooling is available.
- Remaining: later integration pass to connect an active `PER_SESSION` rate to preview-only Advance Batch amounts.

## Advance Batch Finance/Admin Validation Backlog Note (2026-06-04)

- Completed: finance/admin validation packet, blank comparison template, discrepancy register, and summary-only preview snapshot.
- Next required human action: finance/admin independently compares an approved sample, records discrepancies, and signs one decision option.
- Do not design final approval or official export while the gate remains `PENDING_FINANCE_ADMIN_REVIEW`.
- No readiness score increase applies to preparation of review evidence.

## Advance Batch Finance Response Intake Backlog Note (2026-06-04)

- Completed: response intake, decision gate, correction backlog template, and follow-up question register.
- Current blocking item: obtain a completed signed response with independent comparison evidence.
- Any corrections must be validated before approval-workflow design can proceed.
- Official export and payment authorization remain outside the backlog until the gate genuinely advances.

## Official 2/2568 Sample Alignment Backlog Note (2026-06-04)

- Completed: historical sample reference, three-way rate conflict record, duty-category model, document-output requirements, and data-gap audit.
- Obtain the original sample image or approved row-level source for provenance and comparison.
- Finance/admin must select the applicable rate rule and authoritative paper-distribution payable source.
- Do not implement official output, approval, or payment authorization until the validation gate advances.

## Rate And Paper-Distribution Decision Capture Backlog Note (2026-06-05)

- Completed: rate/source decision source review, Thai-first decision capture form, and next implementation options note.
- Current gate remains `PENDING_FINANCE_ADMIN_REVIEW`; the decision capture defaults to `DECISION_PENDING`.
- Active rates are unchanged, including the current local `300/500` demo/system rate.
- Official document output remains blocked until finance/admin confirms both rate and paper-distribution payable source.
- Payment approval/export remains outside the backlog until the gate advances; readiness scores remain unchanged.

## Official Payment Document Draft Preview Backlog Note (2026-06-05)

- Completed: draft-only in-app preview path for the 2/2568 official-style payment table.
- The preview uses fixed term-specific `120/200`; active `300/500` remains demo/test data and is not read for this draft.
- Paper-distribution counts are manual/staff-confirmed request input and non-persistent.
- Remaining: supervisor/finance review, authoritative paper-source validation, final approval workflow, official export, and production payment evidence.
- Do not touch teaching workload, Work H, opencourse, or coinstruc logic from this backlog item.

## Official Payment Document Draft Validation Backlog Note (2026-06-05)

- Completed: dirty-tree review, validation log, dependency declaration for `httpx`, focused tests, full backend suite, frontend build, and required i18n checks.
- Remaining: optional i18n coverage tooling repair as a separate non-feature debt item.
- Browser screenshot capture remains unavailable in this session; route serving was checked by HTTP fallback.
- No final approval, authorization, export, or readiness uplift is created by validation.

## Official Payment Document Draft Manual Smoke Package Backlog Note (2026-06-05)

- Completed: manual smoke results doc, Thai-first supervisor/finance review checklist, and decision gate.
- Verified by HTTP fallback: backend health and the draft route are reachable.
- Remaining: authenticated visual browser smoke and screenshot capture after Chrome/browser automation is available.
- Next required human action: supervisor/finance review selects one allowed decision and validates the authoritative paper-distribution source.
- No approval, authorization, official export, active-rate change, teaching workload, Work H, opencourse, or coinstruc work is added.

## Supervisor / Finance Review Package Backlog Note (2026-06-08)

- Completed: Thai-first one-pager, decision form, talking script, quick checklist, and source review for supervisor/finance review.
- Current gate remains `PENDING_SUPERVISOR_FINANCE_REVIEW`; no reviewer decision is prefilled.
- Remaining: reviewer completes the decision form, confirms rate set, validates the authoritative paper-distribution source, and decides whether draft-export design may proceed later.
- Official payment approval, final authorization, PDF/Excel/export, active-rate change, and readiness uplift remain blocked.

## Supervisor / Finance Decision Intake And Review Model Backlog Note (2026-06-08)

- Completed: decision intake source review, payment-document review workflow model, configurable settings model, and implementation decision gate.
- Recorded decision: `ACCEPT_DRAFT_FORMAT`, with review/comment required before official use.
- Current recommended implementation gate is `DOCS_ONLY_MODEL_NOW`.
- Remaining: choose persistent review storage, reviewer identity/permissions, settings UI/API, and audit behavior before runtime implementation.
- Final payment approval, official export, final authorization, and readiness uplift remain blocked.

## Persistent Payment Document Review Records Backlog Note (2026-06-08)

- Completed: persistent review table/API, draft-page review panel, API contract, source review, and focused review tests.
- Review records support comments, reviewer identity, review history, and non-authorizing statuses.
- Remaining: supervisor/finance validates the workflow in use, then separately decides whether draft-export design should proceed.
- Still blocked: final payment approval, final authorization, official PDF/Excel/export, authoritative paper-distribution source truth, and readiness uplift.

## Payment Document Settings Implementation Backlog Note (2026-06-08)

- Completed: persistent configurable settings for term-specific draft rates and paper-distribution responsible group/person.
- Staff can read settings; reviewer-level roles can save draft-preparation settings.
- Remaining: approved connection of settings into the official payment draft preview calculation/source selection.
- Still blocked: final payment approval, final authorization, official PDF/Excel/export, final payment truth, and readiness uplift.

## Settings-Backed Draft Integration Backlog Note (2026-06-08)

- Completed: connect complete active term settings into official draft-preview calculations.
- Missing/incomplete settings now block money fields while preserving grouped duty counts.
- Remaining: supervisor/finance review acceptance and a separate decision on draft-export design.
- Approval, authorization, official export/PDF/Excel, final truth, and readiness uplift remain blocked.

## Draft Export Design Gate Backlog Note (2026-06-08)

- Completed: draft export design gate defined in `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md`; source review in `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_GATE_SOURCE_REVIEW.md`; requirements checklist in `docs/operations/PAYMENT_DOCUMENT_DRAFT_EXPORT_REQUIREMENTS_CHECKLIST.md`; test matrix in `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_TEST_MATRIX.md`.
- Current gate status: `DRAFT_EXPORT_DESIGN_PENDING`; recommended decision: `HOLD_PENDING_REVIEW_ACCEPTANCE`.
- Remaining: human reviewer sets `ACCEPTED_FOR_DRAFT_EXPORT`, paper-distribution source is confirmed, export format is decided, then all 10 gate preconditions can be re-evaluated.
- Export is not implemented. Final authorization is still blocked. Payment approval is not added.
- Readiness uplift not applied. Production, pilot, and payment readiness scores unchanged.

## Draft Export Gate Re-Evaluation Backlog Note (2026-06-08)

- Completed: gate re-evaluation pass. All 10 preconditions verified via live API. Review acceptance confirmed (review_id 4). Gate advanced to `ALLOW_DRAFT_EXPORT_DESIGN`. Re-evaluation in `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_GATE_REEVALUATION.md`.
- Remaining: implement backend draft export endpoint + frontend export button/trigger; write and pass all 57 tests in the test matrix; produce validation log.
- Export is NOT yet implemented. Final authorization still blocked. Payment approval NOT added.
- Readiness uplift not applied. Production, pilot, and payment readiness scores unchanged.

## Draft Export Implementation Backlog Note (2026-06-08)

- Completed: draft payment document Excel export endpoint + frontend trigger + 21 backend tests + validation log.
- Backend: `POST /api/invigilation-advance-batch/official-document-draft-export`; 8-gate check; openpyxl workbook with Thai draft labels on all sheets; stateless; no DB writes.
- Frontend: export button visible to admin/esq_head/secretary; gated on `ACCEPTED_FOR_DRAFT_EXPORT` review status; `exportOfficialPaymentDraftExcel()` service function.
- All safety invariants confirmed: `payment_authorization_enabled=false`, `final_export_enabled=false`, `document_status=DRAFT_NOT_AUTHORIZED`.
- Full backend test suite: 1552 PASS. Frontend build: PASS. i18n: 1953/1953 parity PASS.
- Remaining: official payment export, final authorization, payment approval, and payment release remain blocked by separate future gate.
- Readiness uplift not applied. Production, pilot, and payment readiness scores unchanged.
