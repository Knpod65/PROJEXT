# EMS Demo/Review Release Candidate Live Smoke Report

**Date**: 2026-06-12  
**Release candidate**: `EMS_DEMO_REVIEW_RC_1`  
**Result**: `LIVE_SMOKE_PASSED`

## Availability And Route Smoke

- Backend health: HTTP `200`.
- Frontend base: HTTP `200`.
- Registered renderable routes: `44/44` HTTP `200`.
- Not-found behavior: HTTP `200`.
- Twelve required authenticated routes rendered with expected URLs, non-empty content, and no browser page errors:
  `/dashboard`, `/submissions`, `/swaps`, `/printreview`, `/external`, `/rooms-v2`, `/period`, `/invigilation-payment-document-draft`, `/payment-document-settings`, `/invigilation-advance-batch-preview`, `/exports-center`, and `/staff-availability`.

## Payment And Role Smoke

- Admin settings, review panel, settings-backed draft, and enabled draft-export state rendered.
- Admin UI produced a real review-gated draft XLSX.
- Staff payment draft rendered with comment/request-review capability and no draft-export permission.
- Teacher and print shop rendered the localized blocked-route state.
- In-app browser capture was unavailable; authenticated screenshots were captured through a safe temporary headless Chrome session.

## Real Screenshots

All screenshots are under `docs/operations/demo-smoke-screenshots/`.

| Evidence | File | Result |
|---|---|---|
| Dashboard | `rc-dashboard.png` | PASS |
| Payment draft before preview | `rc-payment-draft.png` | PASS |
| Payment settings | `rc-payment-settings.png` | PASS |
| Calculated draft and export gate | `rc-draft-export.png` | PASS |
| Staff payment draft | `rc-role-staff.png` | PASS |
| Teacher blocked route | `rc-role-teacher-blocked.png` | PASS |
| Print-shop blocked route | `rc-role-printshop-blocked.png` | PASS |

Screenshots captured: `7`.

## Safety Result

- `DRAFT_NOT_AUTHORIZED` remains visible.
- Review and settings context remain visible.
- Draft XLSX is review-gated and non-authorizing.
- Final approval, final authorization, official-final export, and payment release controls are absent.
- No code, readiness, permission, workload, or business-logic change was made.

