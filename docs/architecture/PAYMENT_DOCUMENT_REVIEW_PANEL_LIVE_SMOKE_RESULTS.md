# Payment Document Review Panel Live Smoke Results

**Date**: 2026-06-08  
**Result**: `LIVE_SMOKE_PASSED_WITH_SCREENSHOT_EVIDENCE`  
**Document status preserved**: `DRAFT_NOT_AUTHORIZED`

## Preflight

| Check | Result |
|---|---|
| EMS root | PASS, `C:/Users/DELL/Desktop/PROJEXT/opt/ems_system` |
| Branch | PASS, `main` |
| History includes implementation | PASS, latest history includes `6320218`, `ae7cd9c`, and `fadc161` |
| Worktree before smoke | PASS, clean |
| Local DB tracking | PASS, `backend/ems.db*` is ignored |

## Server Smoke

| Endpoint | Result |
|---|---|
| `http://127.0.0.1:8000/api/health` | HTTP `200` |
| `http://127.0.0.1:3000` | HTTP `200` |
| `http://127.0.0.1:3000/invigilation-payment-document-draft` | HTTP `200` |

## API Smoke

Document id:

`ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all`

Timestamp used in comments:

`20260608-135337`

| Scenario | Result |
|---|---|
| Admin login `mathawee.m` / `admin123`, `selected_role=admin` | PASS |
| Admin list review records | PASS |
| Admin create review comment | PASS, `review_id=1` |
| Admin update to `UNDER_REVIEW` | PASS |
| Admin update to `REVISIONS_REQUESTED` | PASS |
| Admin update to `ACCEPTED_FOR_DRAFT_EXPORT` | PASS |
| Admin safety flags on every response | PASS, `payment_authorization_enabled=false`, `final_export_enabled=false` |
| Staff login `araya.fa` / `staff123`, `selected_role=staff` | PASS |
| Staff create preparer/comment record | PASS, `review_id=2` |
| Staff attempts `ACCEPTED_FOR_DRAFT_EXPORT` | PASS, blocked with HTTP `403` |
| Teacher login `pailin.phu` / `teacher123`, review API access | PASS, blocked with HTTP `403` |
| Print shop login `printshop.ops` / `print123`, review API access | PASS, blocked with HTTP `403` |
| Student live smoke | NOT LIVE-SMOKED; no seeded login account exists. Covered by focused backend tests. |

## Browser Smoke

| Item | Result |
|---|---|
| In-app Browser | BLOCKED, `iab` browser backend unavailable in this session |
| Fallback browser | PASS, Chrome headless with temporary profile and Chrome DevTools Protocol |
| User Chrome profile modified | NO |
| Real UI login | PASS, role-selection card and login form were driven through browser input |
| Draft page loads | PASS |
| Review panel visible | PASS |
| Status chip visible | PASS |
| Comment box visible | PASS |
| Review history visible | PASS |
| Save comment works | PASS |
| Admin status update to `ACCEPTED_FOR_DRAFT_EXPORT` works | PASS |
| `DRAFT_NOT_AUTHORIZED` remains visible | PASS |
| Safety warning says accepting draft does not authorize payment | PASS |
| Final payment button | ABSENT |
| Official export button | ABSENT |
| PDF/Excel export button | ABSENT |
| Payment authorization / final-truth control | ABSENT |
| Teaching workload / Work H / opencourse / coinstruc wording | ABSENT |

## Screenshot Evidence

- `docs/operations/demo-smoke-screenshots/payment-document-review-panel.png`
- `docs/operations/demo-smoke-screenshots/payment-document-review-history.png`
- `docs/operations/demo-smoke-screenshots/payment-document-review-accepted-draft-export.png`

## Safety Confirmation

- Code changed: NO.
- Payment calculation changed: NO.
- Rate logic changed: NO.
- Manual paper-distribution rows persisted as payment truth: NO.
- Payment approval added: NO.
- Final authorization added: NO.
- Official PDF/Excel/export added: NO.
- `ACCEPTED_FOR_DRAFT_EXPORT` remains non-authorizing only.
- Readiness scores are unchanged.

## Next Action

Implement the configurable settings page for term-specific rates and paper-distribution responsible group/person after supervisor/finance confirms the settings workflow.
