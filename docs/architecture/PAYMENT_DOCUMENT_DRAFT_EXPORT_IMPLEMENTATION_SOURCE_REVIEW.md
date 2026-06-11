# Payment Document Draft Export — Implementation Source Review

**Date**: 2026-06-11

## Docs Read

- `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md`
- `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_GATE_REEVALUATION.md`
- `docs/architecture/PAYMENT_DOCUMENT_DRAFT_EXPORT_TEST_MATRIX.md`
- `docs/architecture/PAYMENT_DOCUMENT_SETTINGS_DRAFT_INTEGRATION_CONTRACT.md`
- `docs/architecture/PAYMENT_DOCUMENT_REVIEW_WORKFLOW_MODEL.md`
- `docs/operations/PAYMENT_DOCUMENT_DRAFT_EXPORT_REQUIREMENTS_CHECKLIST.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`

## Current Gate Status

| Field | Value |
|---|---|
| Gate decision | `ALLOW_DRAFT_EXPORT_DESIGN` |
| Review record id | 4 |
| Review status | `ACCEPTED_FOR_DRAFT_EXPORT` |
| Reviewer comment | Present (non-empty) |
| `payment_authorization_enabled` | `false` |
| `final_export_enabled` | `false` |

## Draft Endpoint Behavior (Pre-Export)

`POST /api/invigilation-advance-batch/official-document-draft-preview` returns:
- `metadata.settings_source_status` — `CONFIGURED` when term settings are active
- `metadata.settings_status` — `ACTIVE_FOR_DRAFT_PREVIEW` when active
- `metadata.calculation_status` — `CALCULATED_FROM_SETTINGS` when configured
- `metadata.paper_distribution_responsible_group` — from payment document settings
- `payment_authorization_enabled = False` (hard-coded)
- `final_export_enabled = False` (hard-coded)
- `draft_only = True` (hard-coded)
- `rows[]` — one row per exam date × time slot
- `totals` — aggregate counts and amounts

## Export Format Decision

| Format | Status | Reason |
|---|---|---|
| `.xlsx` | **CHOSEN** | `openpyxl>=3.1.0` already in `backend/requirements.txt`; no new dependency |
| PDF | Deferred | `weasyprint` present but Thai font rendering complex; deferred |
| HTML | Deferred | Can be added later without code changes to xlsx path |
| JSON | Not needed | Structured response already available via preview endpoint |

## Safety Boundaries

- Export endpoint uses `require_view_all` guard: admin / esq_head / secretary only.
- Gate check runs in service before any xlsx bytes are generated.
- `payment_authorization_enabled` and `final_export_enabled` are never set to true.
- Export is read-only: no DB writes, no status mutations, no review record changes.
- Manual paper-distribution rows are passed through as draft-labeled input only; not persisted as payment truth.
- Filename includes `DRAFT` prefix; workbook sheets include Thai + English draft banners.

## Available Libraries

- `openpyxl>=3.1.0` — xlsx generation; `from openpyxl.utils import get_column_letter` required for column widths on merged-cell sheets
- `io.BytesIO` + `fastapi.responses.StreamingResponse` — file streaming pattern

## Exact Files to Create / Modify

| File | Action |
|---|---|
| `backend/services/payment_document_draft_export_service.py` | CREATE |
| `backend/routers/invigilation_advance_batch.py` | MODIFY — add export endpoint |
| `backend/tests/test_payment_document_draft_export.py` | CREATE |
| `frontend/src/services/officialPaymentDraft.service.ts` | MODIFY — add `exportOfficialPaymentDraftExcel` |
| `frontend/src/pages/OfficialPaymentDocumentDraft.tsx` | MODIFY — add `submitExport` + export button |
| `frontend/src/i18n/en.ts` | MODIFY — add 4 export keys |
| `frontend/src/i18n/th.ts` | MODIFY — add 4 export keys |
