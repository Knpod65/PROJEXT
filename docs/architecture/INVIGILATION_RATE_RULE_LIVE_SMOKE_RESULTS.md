# Invigilation Rate Rule Live Smoke Results

**Date**: 2026-06-02  
**Scope**: EMS invigilation payment rate-rule configuration only.

## Server Status

| Item | Result | Notes |
| --- | --- | --- |
| Backend initial port check | STALE_PROCESS_FOUND | Port `8000` was held by `C:\Python314\python.exe -m uvicorn main:app --port 8000`; OpenAPI exposed only `/api/health`. |
| Backend corrective action | PASS | Stopped only the stale Python listener and restarted backend from `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system\backend` using `backend\.venv\Scripts\python.exe`. |
| Backend route check after restart | PASS | OpenAPI included `/api/auth/login` and all `/api/invigilation-payment/rate-rules` routes. |
| Backend health | PASS | `GET /api/health` returned `200`. |
| Frontend route | PASS | `GET http://127.0.0.1:3000/invigilation-rate-rules` returned `200`. |

## Authenticated Role Smoke

| Role | Account | Expected | Result | Notes |
| --- | --- | --- | --- | --- |
| Admin | `mathawee.m / admin123`, role `admin` | Can access and mutate | PASS | Login `200`; list `200`; create, activate, archive all `200`. |
| Staff | `araya.fa / staff123`, role `staff` | Can access read-only | PASS | Login `200`; list `200`; create blocked with `403`. |
| Teacher | `kiancheng.lee / teacher123`, role `teacher` | Blocked | PASS | Login `200`; list blocked with `403`. |
| Print shop | `printshop.ops / print123`, role `print_shop` | Blocked | PASS | Login `200`; list blocked with `403`. |

## Admin Rate Lifecycle Smoke

| Step | Result | Evidence |
| --- | --- | --- |
| List existing rules | PASS | Admin list returned `200`; safety flags were `preview_only=true`, `payment_authorization_enabled=false`, `final_export_enabled=false`. |
| Create DRAFT | PASS | Created local demo rule id `2`, `payment_unit=PER_SESSION`, `rate_amount=300.00`, `status=DRAFT`. |
| Activate | PASS | Demo rule id `2` changed to `ACTIVE`. |
| Archive | PASS | Demo rule id `2` changed to `ARCHIVED`; archived record remains as local audit evidence. |
| Safety flags | PASS | Create/activate/archive responses retained preview-only safety flags. |

## Invalid Input Smoke

| Case | Expected | Result |
| --- | --- | --- |
| Missing `rate_name` | Reject | PASS, `422` |
| Missing `rate_amount` | Reject | PASS, `400`, `rate_amount is required` |
| Zero `rate_amount` | Reject | PASS, `400`, `rate_amount must be positive` |
| Negative `rate_amount` | Reject | PASS, `400`, `rate_amount must be positive` |
| Unsupported `payment_unit=PER_HOUR` | Reject | PASS, `400`, unsupported unit |

No invalid `ACTIVE` rate was created.

## Browser And Screenshot Evidence

- In-app Browser tooling was attempted, but the required Node browser execution tool was not exposed in this session after discovery.
- The frontend project does not include local Playwright dependencies.
- Chrome plugin instructions also require the same unavailable Node browser execution surface.
- Screenshots were therefore **not captured** in this pass.
- The frontend route was still verified as live by HTTP, and authenticated behavior was verified against the live backend API.

## Safety Confirmation

- Code changed: **NO**
- Payment calculation implemented: **NO**
- Advance Batch amount integration changed: **NO**
- Final payment approval/export added: **NO**
- Teaching workload logic touched: **NO**
- Production deployment attempted: **NO**
- Laravel/POLSCI auth bridge implemented: **NO**

## Bugs Found

- No rate-rule feature bug was found.
- Environmental finding: a stale/non-current backend process initially occupied port `8000`. It was replaced with the current EMS backend before smoke execution.

