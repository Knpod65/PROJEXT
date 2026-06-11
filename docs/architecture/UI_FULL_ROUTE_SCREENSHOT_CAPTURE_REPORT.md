# UI Full Route Screenshot Capture Report

**Date**: 2026-06-11  
**Status**: `AUTHENTICATED_ADMIN_CAPTURE_COMPLETED`

## Method And Coverage

- Backend health: HTTP `200`.
- Renderable route HTTP smoke: `44/44` returned HTTP `200`.
- In-app Browser: unavailable for this session.
- Chrome extension browser client: authenticated admin capture succeeded.
- Real screenshots retained: `38`.
- Output pattern: `docs/operations/demo-smoke-screenshots/full-ui-audit-<route-name>.png`.

## Blocked Or Redirected

| Route | Result | Reason |
|---|---|---|
| `/duty-workload` | AUTH_BLOCKED | Admin session does not have staff-only route access; workload is audit-only in this pass. |
| `/my-workload` | AUTH_BLOCKED | Admin session does not have teacher-only route access; workload is audit-only in this pass. |
| `/print-queue` | AUTH_BLOCKED | Admin session does not have print-shop-only route access. |
| `/myexam` | AUTH_BLOCKED | Admin session does not have teacher-only route access. |
| `/role-selection` | REDIRECTED | Active authenticated session redirected to dashboard; misleading screenshot discarded. |
| `/login` | REDIRECTED | Active authenticated session redirected to dashboard; misleading screenshot discarded. |

## Visual Review Result

- Changed pages reviewed: official payment document draft, payment document settings, and platform configuration.
- Payment draft shows localized review/settings/calculation statuses and a visible draft-export gate.
- Payment settings shows localized status controls and consistent helper/error field structure.
- Platform configuration renders without symbolic check/em-dash display drift.
- No fabricated or redirected screenshots are counted as evidence.
