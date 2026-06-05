# Official Payment Document Draft Validation Log

**Date**: 2026-06-05
**Feature**: 2/2568 official-style payment document draft preview
**Document status**: `DRAFT_NOT_AUTHORIZED`
**Finance/supervisor gate**: review still required

## Dependency And Tooling

- `backend\.venv` contains `pytest` and `httpx`.
- `backend/requirements.txt` now declares `httpx>=0.27.0` because FastAPI/Starlette `TestClient` is used by committed router tests.
- `npm run check:i18n:coverage` remains blocked by pre-existing tooling debt: `check-i18n-coverage.js` uses `require()` under frontend `"type": "module"`.
- The coverage script blocker is documented as non-gating for this feature because required frontend build and i18n checks pass, and the script/package configuration was not introduced by this pass.

## Backend Validation

| Check | Result |
|---|---|
| `backend\.venv\Scripts\python.exe -m compileall backend -q` | PASS |
| `backend\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'backend'); import main; print(repr(main.IMPORT_ROUTERS_ERROR))"` | PASS, returned `None` |
| `backend\.venv\Scripts\python.exe -m pytest backend\tests\test_official_payment_document_draft_service.py backend\tests\test_official_payment_document_draft_router.py -q` | PASS, `10 passed` |
| `backend\.venv\Scripts\python.exe -m pytest backend\tests -q` | PASS, `1496 passed` |

Warnings were limited to existing development secret/database fallback, SQLAlchemy deprecation, and Pydantic deprecation warnings.

## Frontend Validation

| Check | Result |
|---|---|
| `npm run build` | PASS |
| `npm run check:i18n` | PASS |
| `npm run check:i18n:raw` | PASS, raw-string scan is warning-mode and reported existing broad candidates |
| `npm run check:i18n:coverage` | BLOCKED, pre-existing CommonJS/ESM script mismatch |

## Browser And Route Smoke

- Visual browser smoke: BLOCKED. The in-app browser target returned `Browser is not available: iab`.
- Screenshot captured: NO.
- Screenshot path: not created.
- HTTP fallback: PASS. Vite served `http://127.0.0.1:3000/invigilation-payment-document-draft` with status `200`.

## Safety Boundary Confirmation

- Payment approval added: NO.
- Final authorization added: NO.
- Official export added: NO.
- Official PDF/Excel output added: NO.
- Manual paper-distribution rows persisted: NO.
- Active `300/500` demo rates changed: NO.
- Teaching workload / Work H / opencourse / coinstruc touched: NO.
- Draft output status remains `DRAFT_NOT_AUTHORIZED`.
- Next human decision: supervisor/finance review must validate the draft table and authoritative paper-distribution source before final-truth, approval, authorization, or export work.
