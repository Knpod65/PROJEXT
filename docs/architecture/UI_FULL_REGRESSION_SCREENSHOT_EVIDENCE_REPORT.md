# UI Full Regression Screenshot Evidence Report

**Date**: 2026-06-11  
**Result**: `FULL_UI_REGRESSION_PASSED_WITH_DEFERRED_P2`

## Method And Coverage

- Local backend health: HTTP `200`.
- Frontend base: HTTP `200`.
- Renderable route HTTP smoke: `44/44` returned HTTP `200`.
- Visual destinations assessed: `43/43`, using current live captures plus existing full-route and role evidence.
- Real regression screenshots captured through the authenticated Chrome browser client: `8`.
- No redirected or fabricated screenshots are counted.

## New Regression Screenshots

| Route | Screenshot | Result |
|---|---|---|
| `/submissions` | `regression-submissions.png` | PASS |
| `/swaps` | `regression-swaps.png` | PASS |
| `/printreview` | `regression-printreview.png` | PASS |
| `/external` | `regression-external.png` | PASS |
| `/rooms-v2` | `regression-rooms-v2.png` | PASS |
| `/period` | `regression-period.png` | PASS |
| `/invigilation-payment-document-draft` | `regression-payment-draft.png` | PASS |
| `/payment-document-settings` | `regression-payment-settings.png` | PASS |

All files are stored under `docs/operations/demo-smoke-screenshots/`.

## Evidence Notes

- The six recently polished routes remain aligned with the institutional page template and show no visible raw i18n keys.
- Print review and external exams currently render empty states; deeper localized states were validated by build/i18n/static review because no safe non-mutating data path exposed them.
- Workload routes were rechecked as route destinations but remain implementation-excluded.
- Print-shop and teacher-only destination states rely on existing role evidence where the admin live session could not render them.

## Payment Safety Result

- `DRAFT_NOT_AUTHORIZED`: visible.
- Settings source and review panel: visible.
- Draft XLSX control: visible, disabled until its gate is met, and described as draft/review-only.
- Final payment approval: absent.
- Final authorization: absent.
- Official-final export control: absent.
- Payment/export/review/settings behavior changed: NO.
