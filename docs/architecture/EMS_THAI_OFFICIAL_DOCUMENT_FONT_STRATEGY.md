# EMS Thai Official Document Font Strategy

Date: 2026-06-16

## Font Stack

EMS export code now treats the following as the official Thai-capable font stack:

1. `TH Sarabun New`
2. `Sarabun`
3. `Noto Sans Thai`
4. `Tahoma`
5. `Arial Unicode MS`
6. `sans-serif`

## XLSX

XLSX files do not embed font binaries. The export generators assign `TH Sarabun New` as the preferred workbook font name for titles, headers, and body cells. Excel, LibreOffice, or another spreadsheet viewer must have a compatible Thai font installed to match the intended official appearance.

The workbook XML stores real UTF-8 Thai strings. Tests reopen generated workbooks with `openpyxl` and verify exact Thai cell values, Thai sheet names, wrapping, and font names.

## CSV

CSV files are emitted with UTF-8 BOM (`utf-8-sig`) for Excel compatibility and with `text/csv; charset=utf-8`. Tests decode with `utf-8-sig` and verify Thai text round trips exactly.

## DOCX

Generated DOCX content remains UTF-8 ZIP/XML content. Download headers now preserve Thai filenames using RFC 5987 metadata. Existing DOCX generation behavior is otherwise unchanged.

## Local Setup Note

For best XLSX visual rendering on a fresh clone, install either `TH Sarabun New`, `Sarabun`, or `Noto Sans Thai` on the workstation. The repository does not commit proprietary or local Windows font files.
