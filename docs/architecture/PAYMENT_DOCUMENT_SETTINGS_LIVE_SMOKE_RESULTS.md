# Payment Document Settings Live Smoke Results

**Date**: 2026-06-08
**Result**: `LIVE_SMOKE_PASSED`
**Scope**: API, persistence, role access, browser rendering, and safety evidence

## Preflight And Servers

| Check | Result |
|---|---|
| EMS root | `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system` |
| Branch | clean `main` |
| Required history | includes `8a0bb26` |
| `git pull origin main` | already up to date |
| `backend/ems.db*` | ignored by Git |
| `GET /api/health` | HTTP `200` |
| Frontend base | HTTP `200` |
| `/payment-document-settings` | HTTP `200` |
| `/invigilation-payment-document-draft` | HTTP `200` |

## Live API Smoke

The admin smoke saved and re-read term `2/2568` with:

- weekday rate `120.00`
- weekend rate `200.00`
- responsible group `Education_Student_Quality`
- blank responsible person
- status `ACTIVE_FOR_DRAFT_PREVIEW`
- note `Draft settings only; not payment authorization.`

| Role / action | Result |
|---|---|
| Admin login, GET, PUT, GET | PASS; settings persisted |
| Staff login and GET | PASS |
| Staff PUT | blocked with HTTP `403` |
| Teacher GET and PUT | blocked with HTTP `403` |
| Print-shop GET and PUT | blocked with HTTP `403` |
| Student live login | not run; no seeded student credential was available |
| Student permission coverage | covered by focused backend settings tests |

Every relevant settings response kept:

- `payment_authorization_enabled=false`
- `final_export_enabled=false`

## Browser Smoke

The in-app browser was unavailable. Real screenshots were captured with installed Chrome in headless mode, a temporary profile, and short-lived local seed-session tokens. The temporary profile was removed after capture. No user Chrome profile or real CMU credential was used.

| Page | Result |
|---|---|
| Admin `/payment-document-settings` | PASS; saved term, rates, group, status, warning, and save/reset controls rendered |
| Staff `/payment-document-settings` | PASS; settings fields are read-only, status is disabled, term lookup remains selectable, and no save control is present |
| Admin `/invigilation-payment-document-draft` | PASS; settings-source context shows term/rates/group and `DRAFT_NOT_AUTHORIZED` remains visible |

No page-scoped final approval, payment authorization, official export, PDF, or Excel control was found. The draft page explicitly states that displayed settings do not change the draft calculation in this pass.

## Screenshot Evidence

- `docs/operations/demo-smoke-screenshots/payment-document-settings-admin.png`
- `docs/operations/demo-smoke-screenshots/payment-document-settings-readonly.png`
- `docs/operations/demo-smoke-screenshots/payment-document-draft-settings-context.png`

## Safety Confirmation

- Code changed: **NO**
- Payment approval added: **NO**
- Final authorization added: **NO**
- Official export/PDF/Excel added: **NO**
- Payment calculation changed: **NO**
- Active simple rates changed: **NO**
- Manual paper rows persisted as payable truth: **NO**
- Readiness scores changed: **NO**
- Settings remain draft-preparation configuration only: **YES**
- Draft status remains `DRAFT_NOT_AUTHORIZED`: **YES**

Live smoke settings may remain in the ignored local development database as persistence evidence.

## Next Action

Connect the approved settings source into official payment draft preview calculations only after supervisor/finance approval of that integration.
