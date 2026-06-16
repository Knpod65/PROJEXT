# EMS Full Route Visual Defect Register

Date: 2026-06-16

## Summary

| Severity | Count | Status |
| --- | ---: | --- |
| P0 | 0 | None found |
| P1 | 2 | Fixed |
| P2 | 1 | Documented, accepted |

## Fixed Defects

| ID | Severity | Route / Evidence | Defect | Fix | Verification |
| --- | --- | --- | --- | --- | --- |
| FRVA-P1-001 | P1 | `/schedule`, admin, `390x844` | Mobile layout had document-level horizontal overflow caused by narrow viewport grid/flex minimums and bottom navigation label width. | Added shared `min-width: 0` and mobile one-column controls; bounded mobile nav columns with `minmax(0, 1fr)` and ellipsis. | `admin-schedule-390-th.png`, overflow `0`, one visible `h1`. |
| FRVA-P1-002 | P1 | `/invigilation-payment-document-draft`, admin, `1024x768` | Payment draft page had 14px horizontal overflow at laptop width. | Added shared card/table/filter minimum-width containment and two-column `form-grid--paper` behavior below 1200px. | `admin-invigilation-payment-document-draft-1024-th.png`, overflow `0`, draft-only safety text preserved. |

## Accepted P2

| ID | Severity | Route / Evidence | Observation | Decision |
| --- | --- | --- | --- | --- |
| FRVA-P2-001 | P2 | `/print-queue`, print_shop, `1600`, `1366`, `1024`, Thai/English representative screenshots | Automated browser sweep recorded a browser log event. A focused live probe reproduced only normal Vite/React development console chatter and no application `console.error`, page crash, raw key, overflow, or theme failure. | Accepted as documented P2. No code change applied because visible acceptance passed and broadening scope would exceed this certification pass. |

## Changed Files For Fixes

- `frontend/src/styles/components.css`
- `frontend/src/styles/layout.css`
- `frontend/src/styles/utilities.css`

## Prohibited Scope Check

No backend files, route declarations, authorization helpers, payment/export/review/settings services, optimizer/workload calculations, or final authorization controls were changed for these defects.
