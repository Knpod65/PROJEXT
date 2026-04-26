# EXPORT SYSTEM

## Purpose

The export system turns operational EMS data into printable and shareable outputs for exam-day use and reporting.

## Main Entry Points

- Frontend export hub:
  - `frontend/src/pages/ExportCenter.tsx`
- Backend export/document routes:
  - `backend/routers/exports.py`
  - `backend/routers/exports_excel.py`
  - `backend/routers/documents.py`

## Export Categories

### Exam Documents

- participant codes
- signature sheets
- envelope cover sheets
- bundled/all-document export

These are linked from `buildDocumentExportUrl(...)`.

### Schedule Exports

- schedule PDF
- schedule Excel

### Workload Exports

- workload summary PDF
- workload summary Excel
- workload detail Excel

### Paper Distribution Exports

- paper distribution PDF
- paper distribution Excel

## QR Usage In Exports

- QR X is used for operational pickup confirmation
- QR X lifecycle matters for document/pickup coordination
- QR Y remains separate from pickup confirmation and is treated as document-side support metadata

## Templates / Generation Notes

- Document generation is backed by backend-side document utilities
- Relevant implementation areas include:
  - `backend/gen_docs.py`
  - `backend/operational_documents.py`
  - `backend/routers/pdf.py`
  - `backend/routers/documents.py`

The exact rendering path differs by output type, but the frontend should treat exports as backend-owned artifacts.

## Document Types To Expect

- room/exam participant lists
- signature sheets
- envelope/cover sheets
- schedule reports
- workload summaries
- paper distribution reports
- print-preparation artifacts

## Operational Constraints

- Export availability depends on upstream data quality
- Missing room assignment, unresolved workflow status, or ungenerated QR state can reduce export usefulness even if the endpoint still exists
- Export Center should remain a launcher/hub, not a place where business rules are duplicated
