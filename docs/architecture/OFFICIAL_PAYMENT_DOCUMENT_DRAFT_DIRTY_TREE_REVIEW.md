# Official Payment Document Draft Dirty Tree Review

**Date**: 2026-06-05
**Branch**: `main`
**Base commit at review start**: `cd82334`
**Scope**: Dirty-tree validation before committing the 2/2568 official-style payment document draft preview.

## Preflight

- EMS root confirmed: `C:/Users/DELL/Desktop/PROJEXT/opt/ems_system`.
- Current branch confirmed: `main`, tracking `origin/main`.
- History includes `84508ae` and later commit `cd82334`.
- Worktree was dirty before this pass only with the payment draft preview implementation, governance docs, frontend route/page work, and related tests.
- This review did not inspect or modify the outer project documentation index.
- This review did not run `git pull` while the tree was dirty.

## Dirty Files Reviewed

| Area | Files | Purpose | Expected |
|---|---|---|---|
| Backend API | `backend/routers/invigilation_advance_batch.py`, `backend/schemas.py`, `backend/services/official_payment_document_draft_service.py` | Adds staff/admin draft-preview endpoint, request/response schemas, fixed 2/2568 `120/200` draft calculation, non-persistent manual paper rows, warnings, and safety flags. | YES |
| Backend tests | `backend/tests/test_official_payment_document_draft_service.py`, `backend/tests/test_official_payment_document_draft_router.py` | Covers rate isolation, BE/weekend normalization, grouping, manual-only paper warnings, safety flags, RBAC, and validation rejection for negative paper counts. | YES |
| Dependency declaration | `backend/requirements.txt` | Adds `httpx>=0.27.0` for reproducible FastAPI/Starlette `TestClient` router tests. | YES |
| Frontend app | `frontend/src/App.tsx`, `frontend/src/config/navigation.ts`, `frontend/src/pages/OfficialPaymentDocumentDraft.tsx`, `frontend/src/services/officialPaymentDraft.service.ts`, `frontend/src/hooks/domain/useOfficialPaymentDraftPreview.ts`, `frontend/src/types/officialPaymentDraft.ts`, `frontend/src/i18n/en.ts`, `frontend/src/i18n/th.ts` | Adds staff/admin draft-preview route, API client, UI, manual paper input table, totals, warnings, and translations. | YES |
| Governance docs | payment architecture/readiness/operations docs | Records 2/2568 draft decision, `ANSWERED_DRAFT` status, non-authorization limits, and unchanged readiness. | YES |

## Safety Boundary Review

- Payment approval added: NO.
- Final payment authorization added: NO.
- Official PDF/Excel/export added: NO.
- Document final truth status added: NO.
- Active `300/500` demo rates changed: NO.
- Manual paper-distribution rows persisted as payable records: NO.
- Teaching workload / Work H / opencourse / coinstruc logic touched: NO.
- Check-in used as a pre-disbursement gate: NO.
- Draft status remains: `DRAFT_NOT_AUTHORIZED`.
- API flags remain: `draft_only: true`, `payment_authorization_enabled: false`, `final_export_enabled: false`, `supervisor_finance_review_required: true`.

## Validation Blockers Reviewed

- `httpx` was present in `backend\.venv` but missing from `backend/requirements.txt`; the committed router tests use `TestClient`, so `httpx>=0.27.0` is now declared.
- `npm run check:i18n:coverage` still fails because `frontend/scripts/check-i18n-coverage.js` uses CommonJS `require()` while `frontend/package.json` declares `"type": "module"`. The script and package setting were not changed by this feature, so this is documented as pre-existing non-gating tooling debt.
- Browser screenshot capture was not possible because the in-app browser target reported unavailable. A Vite HTTP fallback returned `200` for `/invigilation-payment-document-draft`.

## Commit Readiness

Status: `READY_TO_COMMIT_AFTER_VALIDATION`.

The reviewed dirty tree is scoped to the official payment document draft preview and its validation/dependency documentation. No unexpected approval, export, final authorization, persistence, or workload changes were found.
