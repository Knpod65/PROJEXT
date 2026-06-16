# EMS Thai Export Encoding And Font Audit

Date: 2026-06-16

## Scope

This audit covers current backend export generators and response helpers for XLSX, CSV, PDF, DOCX, and ZIP downloads:

- RC1 draft payment summary XLSX.
- Supporting finance roster XLSX.
- Export center XLSX workbooks.
- Historical schedule CSV.
- Schedule/workload PDF downloads.
- Operational document DOCX/PDF/ZIP downloads.
- Exam PDF header stamping.

Payment calculations, roster aggregation, optimizer/workload calculations, permissions, review gates, payment settings gates, and final-authorization boundaries are out of scope and were not changed.

## Source Findings

Python UTF-8 reads confirmed that the active backend Thai literals are stored as valid UTF-8 strings. Some PowerShell terminal output renders Thai as mojibake because of console code-page behavior, but the file bytes are not corrupted.

The actual implementation risks were:

- Download headers used only `filename="..."`, which is fragile for Thai names.
- XLSX exports did not consistently assign Thai-capable font names.
- CSV exports already used UTF-8 BOM, but the response header did not declare charset or RFC 5987 filename metadata.
- PDF font discovery was duplicated and did not expose a clear embedding/fallback contract.
- DOCX/PDF/ZIP document downloads repeated simple Content-Disposition construction.

## Implemented Controls

- Added `backend/services/thai_export_service.py`.
- Centralized RFC 5987 `filename*` plus ASCII fallback handling.
- Centralized UTF-8 BOM CSV bytes and `text/csv; charset=utf-8`.
- Added XLSX Thai style helpers using `TH Sarabun New` font names, wrapping, and mojibake guards.
- Added ReportLab local Thai font discovery with explicit `embedded` status.
- Wired XLSX/CSV/PDF/DOCX/ZIP response generation through the shared helpers.
- Added focused regression tests for headers, CSV round trip, XLSX font names, Thai sheet/cell values, and payment/supporting roster safety.

## Preserved Safety Strings

The following strings remain literal and unchanged:

- `DRAFT_NOT_AUTHORIZED`
- `DRAFT_SUPPORTING_EXPORT_ONLY`
- `ACCEPTED_FOR_DRAFT_EXPORT`
- `payment_authorization_enabled=false`
- `final_export_enabled=false`

No official-final export, payment approval, or final authorization path was introduced.
