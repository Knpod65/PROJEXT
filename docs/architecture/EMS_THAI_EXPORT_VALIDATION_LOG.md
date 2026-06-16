# EMS Thai Export Validation Log

Date: 2026-06-16

## Completed Validation

- `backend\.venv\Scripts\python.exe -m compileall backend -q` passed.
- Focused tests passed: `46 passed, 12 warnings`.
- Router import check passed: imported `main`, `invigilation_advance_batch`, `exports_excel`, `historical_schedules`, and `exports`; app route count was 245.
- Full backend suite passed: `1588 passed, 17 warnings`.
- Backend health check passed: `GET http://127.0.0.1:8000/api/health` returned HTTP 200.
- Frontend root check passed: `GET http://127.0.0.1:3000/` returned HTTP 200.
- `cd frontend; npm run build` passed. Vite reported the existing chunk-size warning.
- `cd frontend; npm run check:i18n` passed with `en=2509`, `th=2509`.
- `cd frontend; npm run check:i18n:raw` exited 0. It reported existing raw-string scan candidates in `AdminIntelligenceDashboard.tsx`; frontend source was not changed in this pass.
- `git diff --check` passed. Git reported expected CRLF normalization warnings for touched text files.
- Tested files:
  - `backend/tests/test_thai_export_service.py`
  - `backend/tests/test_payment_document_draft_export.py`
  - `backend/tests/test_payment_supporting_finance_roster.py`

## New Assertions

- `Content-Disposition` includes an ASCII `filename` fallback and RFC 5987 `filename*`.
- CSV bytes start with UTF-8 BOM and decode with `utf-8-sig`.
- XLSX Thai cells reopen with exact Thai values.
- XLSX titles, headers, and body cells use `TH Sarabun New` font names.
- Supporting roster still emits exactly five sheets.
- RC1 draft payment workbook still preserves draft-only safety metadata.
- Mojibake/replacement-character guard rejects known corrupted markers.

## Evidence Artifacts

Generated safe evidence artifacts under `docs/operations/thai-export-evidence/`:

- `sample-rc1-draft-payment-summary.xlsx`
- `sample-supporting-finance-roster.xlsx`
- `sample-historical-schedule.csv`
- `THAI_EXPORT_CELL_ROUNDTRIP_REPORT.md`
- `THAI_EXPORT_FONT_INSPECTION.md`

These are generated samples using the backend workbook/CSV helpers and do not contain credentials. Authenticated browser export smoke was not performed in this backend-focused pass; HTTP health and automated endpoint/workbook tests were used instead.

## Scope Confirmation

No payment calculations, roster counting, room mapping, optimization logic, permissions, review/checklist/export gates, RC1 behavior, supporting roster behavior, or final-authorization behavior were intentionally changed.
