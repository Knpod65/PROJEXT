# Supervisor / Finance Decision Intake Source Review

**Date**: 2026-06-08  
**Scope**: docs-only decision intake and payment-document review workflow scaffold  
**Implementation mode**: `DOCS_ONLY_MODEL_NOW`  
**Current document status**: `DRAFT_NOT_AUTHORIZED`

## Source Documents Read

- `docs/operations/SUPERVISOR_FINANCE_REVIEW_DECISION_FORM.md`
- `docs/operations/SUPERVISOR_FINANCE_QUICK_REVIEW_CHECKLIST.md`
- `docs/operations/EMS_PAYMENT_DOCUMENT_DRAFT_REVIEW_ONE_PAGER.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DRAFT_REVIEW_DECISION_GATE.md`
- `docs/operations/RATE_AND_PAPER_DISTRIBUTION_DECISION_CAPTURE.md`
- `docs/architecture/NEXT_IMPLEMENTATION_OPTIONS_AFTER_2_2568_SAMPLE.md`
- `docs/architecture/ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md`
- `docs/architecture/INVIGILATION_PAYMENT_DUTY_CATEGORY_MODEL.md`
- `docs/architecture/INVIGILATION_RATE_DECISION_AFTER_2_2568_SAMPLE.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`
- Current frontend/backend draft preview files were inspected only to confirm there is no existing persistent review table/API.

## Human Decision Summary

- Document format decision: `ACCEPT_DRAFT_FORMAT`.
- Current official-style draft format is acceptable for now and may be adjusted later.
- Every payment-related document must support review/comment before it is used for official work.
- Compensation rates must remain configurable and term-specific; rates must not be permanently hardcoded.
- Paper-distribution responsibility conceptually defaults to `Education_Student_Quality`, but responsible group/person must remain configurable because staff and ownership can change.
- Proceed toward a document review workflow and configurable settings model.
- Do not implement final payment approval, final authorization, or official export as final truth.

## Accepted Draft Format

The current 2/2568 official-style draft format may be used as the baseline for future review workflow design. Acceptance is format-level only and does not validate all data sources, authorize payment, approve official export, or make the draft final truth.

## Review / Comment Requirement

Future payment-related draft documents must carry a review status and reviewer comment/note path before they can become usable for official work. Review comments must be stored as review evidence and must not overwrite payment truth or source data.

## Configurable Rate Requirement

Rates must remain configurable by term/effective period. The current draft uses the 2/2568 sample direction (`120/200`) for draft output only. Future rate changes require a controlled configuration path and authorized evidence.

## Configurable Paper-Distribution Responsibility Requirement

`Education_Student_Quality` is recorded as the default conceptual responsible group. It must not be treated as the only possible source forever. Future settings must allow responsible group/person updates with effective dates, change reason, and audit fields.

## Safety Boundaries

- Payment authorization added: NO.
- Final authorization added: NO.
- Official PDF/Excel/export added: NO.
- Active rate changed: NO.
- Manual paper-distribution rows made final payable truth: NO.
- Check-in used as pre-disbursement gate: NO.
- Teaching workload / Work H / opencourse / coinstruc touched: NO.

## Recommended Implementation Gate

`DOCS_ONLY_MODEL_NOW`

Reason: the current repository has a draft preview route and configurable paper-distribution division setting, but no persistent payment-document review record/table/API. Adding non-persistent page comments now would risk implying durable review support. The safe next implementation pass should first choose a persistent review storage model, permission rules, and settings surface.
