# Payment Document Settings Implementation Source Review

**Date**: 2026-06-08  
**Status**: implementation source review for configurable payment-document settings  
**Safety boundary**: draft preparation only; no payment authorization or official export

## Source Documents Read

- `docs/architecture/PAYMENT_DOCUMENT_CONFIGURABLE_SETTINGS_MODEL.md`
- `docs/architecture/PAYMENT_DOCUMENT_REVIEW_WORKFLOW_MODEL.md`
- `docs/architecture/PAYMENT_DOCUMENT_REVIEW_IMPLEMENTATION_VALIDATION_LOG.md`
- `docs/architecture/PAYMENT_DOCUMENT_REVIEW_API_CONTRACT.md`
- `docs/operations/RATE_AND_PAPER_DISTRIBUTION_DECISION_CAPTURE.md`
- `docs/architecture/ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`

## Current Review Workflow State

- Persistent payment-document review records exist for `ADVANCE_PAYMENT_DRAFT_SUMMARY`.
- `/invigilation-payment-document-draft` has a review panel and remains `DRAFT_NOT_AUTHORIZED`.
- `ACCEPTED_FOR_DRAFT_EXPORT` is implemented as a non-authorizing draft-review state only.
- Live smoke evidence exists at `docs/architecture/PAYMENT_DOCUMENT_REVIEW_PANEL_LIVE_SMOKE_RESULTS.md`.

## Settings Needed

- Term-specific weekday/weekend rates for draft payment-document preparation.
- Configurable paper-distribution responsible group and optional responsible person.
- Default suggested group: `Education_Student_Quality`.
- Traceability through updater, timestamp, note, term, and status.

## Storage And API Patterns Found

- Backend uses SQLAlchemy models in `backend/models.py` and FastAPI routers in `backend/routers/`.
- Local/test schemas are created through `Base.metadata.create_all`.
- Existing payment review service enforces role checks in the service layer and returns invariant safety flags.
- Existing simple invigilation rates are global preview configuration and must not be mutated by this term-specific document settings pass.

## Role And Permission Pattern

- Read: `admin`, `esq_head`, `secretary`, `staff`.
- Write: `admin`, `esq_head`, `secretary`.
- Blocked: `teacher`, `print_shop`, `student`, and unrelated roles.

## Implementation Plan Applied

- Add `PaymentDocumentSettings` storage separate from rate rules, review records, payment truth, and export logic.
- Add `/api/payment-document-settings` read/upsert endpoints with required validation.
- Add frontend route `/payment-document-settings` with staff read-only behavior.
- Add a read-only settings-source card to the official payment draft page for context only.

## Safety Boundaries

- Settings do not authorize payment.
- Settings do not enable official PDF/Excel/export.
- Settings do not create final payment truth.
- Settings do not mutate active simple `300/500` demo/test rates.
- Settings do not bypass the persistent review workflow.
- Settings do not persist manual paper-distribution draft rows as payable truth.
