# EMS Demo/Review Release Candidate Validation Log

**Date**: 2026-06-12  
**Release candidate**: `EMS_DEMO_REVIEW_RC_1`  
**Result**: `PASS_WITH_DOCUMENTED_NON_PRODUCTION_LIMITATIONS`

## Backend Validation

| Check | Result |
|---|---|
| `backend\.venv\Scripts\python.exe -m compileall backend -q` | PASS |
| Import `main`; inspect `IMPORT_ROUTERS_ERROR` | PASS; `None` |
| `backend\.venv\Scripts\python.exe -m pytest backend\tests -q` | PASS; `1552 passed`, `17 warnings` |

Warnings are existing development/upgrade warnings: insecure development secret fallback, SQLite fallback, SQLAlchemy deprecation, and Pydantic v2 migration notices. They do not support a production deployment claim.

## Frontend Validation

| Check | Result |
|---|---|
| `npm run build` | PASS |
| `npm run check:i18n` | PASS; EN/TH `2260/2260` |
| `npm run check:i18n:raw` | PASS in existing warning-only mode; `100` candidates across `4` files |
| Bundle warning | Existing large-chunk warning; non-blocking for RC demo/review |
| `git diff --check` | PASS |

## Live Data And Safety Validation

- Term `2/2568`: `ACTIVE_FOR_DRAFT_PREVIEW`.
- Rates: weekday `120.00`, weekend `200.00`.
- Responsible group: `Education_Student_Quality`.
- Latest review: `ACCEPTED_FOR_DRAFT_EXPORT` with a non-empty comment.
- Draft metadata: `CONFIGURED`, `CALCULATED_FROM_SETTINGS`, `DRAFT_NOT_AUTHORIZED`.
- Draft safety flags: authorization `false`, final export `false`.
- Draft rows returned: `9`.
- API-generated draft XLSX: HTTP `200`, `7,589` bytes.
- UI-generated draft XLSX: captured to temporary evidence storage, `7,589` bytes.
- Workbook contains `DRAFT_NOT_AUTHORIZED`, accepted review status, draft-review-only wording, and both safety flags set to `false`.
- Review-record count remained `4` before and after API export.

## Role Validation

| Role | Result |
|---|---|
| Admin | Settings, review, preview, and gated draft export work |
| Staff | Settings read `200`; review request/comment create `200`; accept and export attempts `403` |
| Teacher | Restricted settings/review API access `403`; blocked payment-route screenshot captured |
| Print shop | Restricted settings/review API access `403`; blocked payment-route screenshot captured |

## Change Boundaries

- Code changed: NO.
- Backend/payment/export/review/settings logic changed: NO.
- Permissions changed: NO.
- Workload routes or logic changed: NO.
- Readiness scores changed: NO.

