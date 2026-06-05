# Official Payment Document Draft Manual Smoke Results

**Date/time**: 2026-06-05 11:30:44 +07:00
**Scope**: Manual smoke and supervisor/finance review package for `/invigilation-payment-document-draft`
**Status**: `PARTIAL_BLOCKED_BROWSER_AUTOMATION`

## Target

- EMS root: `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`
- Branch: `main`
- Starting commit: at/after `0eefeaf`
- Backend URL: `http://127.0.0.1:8000`
- Frontend URL: `http://127.0.0.1:3000/invigilation-payment-document-draft`
- Expected page status: `DRAFT_NOT_AUTHORIZED`

## Access Method

- Backend started with `backend\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000`.
- Frontend started with `npm run dev` from `frontend`.
- HTTP route fallback returned `200` for the draft page URL.
- Chrome automation was attempted. Local checks found Chrome installed/running, the Codex Chrome Extension installed/enabled, and the native host manifest present, but the browser client still returned `Browser is not available: chrome`.
- No authorization bypass or weakened login path was introduced.

## Smoke Checklist

| Check | Result | Evidence / note |
|---|---:|---|
| EMS root, branch, and clean preflight confirmed | PASS | Root was EMS, branch was `main`, and pull was already up to date. |
| Backend health reachable | PASS | `http://127.0.0.1:8000/api/health` returned `200`. |
| Frontend draft route reachable | PASS | `http://127.0.0.1:3000/invigilation-payment-document-draft` returned `200`. |
| Authenticated real-browser visual page load | BLOCKED | Chrome automation was unavailable after local extension/native-host checks. |
| EMS styling visible | NOT VERIFIED | Requires authenticated visual browser access. |
| Page title communicates official-style draft payment document | NOT VERIFIED | Requires authenticated visual browser access. |
| `DRAFT_NOT_AUTHORIZED` visible | NOT VERIFIED | Requires authenticated visual browser access. Existing implementation and prior tests keep this status in the draft path. |
| Grouped table resembles 2/2568 sample shape | NOT VERIFIED | Requires authenticated visual browser access. |
| Table includes date/time/day type, invigilation count/amount, paper-distribution count/amount, and total | NOT VERIFIED | Requires authenticated visual browser access. |
| Manual paper-distribution rows communicate draft-only/non-persistent handling | NOT VERIFIED | Requires authenticated visual browser access. |
| No approval, final authorization, official export, PDF, Excel, or payment-authorized wording | NOT VERIFIED | Requires authenticated visual browser access. Existing implementation keeps payment/export flags disabled. |
| No teaching workload / Work H / opencourse / coinstruc wording | NOT VERIFIED | Requires authenticated visual browser access. No code changes were made in those areas. |

## Screenshot

- Screenshot captured: NO
- Intended path if available: `docs/operations/demo-smoke-screenshots/official-payment-document-draft-preview.png`
- Blocker: browser automation could not attach to Chrome, and no in-app browser target was available in this session.

## Safety Confirmation

- Code changed: NO
- Approval/export/final authorization added: NO
- Payment authorization added: NO
- Official PDF/Excel/export added: NO
- Persistent paper-distribution rows added: NO
- Active rate changes: NO
- Teaching workload / Work H / opencourse / coinstruc changes: NO
- Current draft status remains: `DRAFT_NOT_AUTHORIZED`
- Current review gate: `PENDING_SUPERVISOR_FINANCE_REVIEW`

## Known Issues

- Authenticated real-browser visual smoke remains blocked until browser automation can attach to Chrome or a user-assisted manual browser session provides screenshot evidence.
- This package should be treated as HTTP-route and documentation readiness evidence only, not as final visual sign-off.
