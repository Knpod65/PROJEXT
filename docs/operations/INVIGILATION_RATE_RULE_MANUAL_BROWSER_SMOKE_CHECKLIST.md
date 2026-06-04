# Invigilation Rate Rule Manual Browser Smoke Checklist

**Date**: 2026-06-04  
**Target**: `http://127.0.0.1:3000/invigilation-rate-rules`  
**Scope**: Configuration/preview-only invigilation rate rules.

## Preconditions

- [ ] Work from `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`.
- [ ] Confirm `main` is current and the worktree is clean.
- [ ] Start backend from `backend`:
  - `.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000`
- [ ] Start frontend from `frontend`:
  - `npm run dev`
- [ ] Confirm `http://127.0.0.1:8000/api/health` returns `200`.
- [ ] Confirm the browser is using local demo accounts only.

## Admin Smoke

Use `mathawee.m / admin123`, selected role `admin`.

- [ ] Log in through the normal app flow.
- [ ] Open `/invigilation-rate-rules`.
- [ ] Page title shows `Invigilation Rate Rules` or `ตั้งค่าอัตราค่าคุมสอบ`.
- [ ] Configuration/preview-only warning is visible.
- [ ] Warning clearly states rate setup does not authorize payment.
- [ ] Page uses EMS-styled hero, cards, controls, badges, and table.
- [ ] No raw/scaffold browser controls are visible.
- [ ] No final payment, approval, official export, finalize, or payment-report action exists.

Create a local demo DRAFT:

- [ ] `rate_name = ค่าคุมสอบปกติ - ทดสอบ`
- [ ] `payment_unit = PER_SESSION`
- [ ] `rate_amount = 300`
- [ ] `currency = THB`
- [ ] `role_scope = ALL`
- [ ] `person_type_scope = ALL`
- [ ] `note = Demo/local smoke only. Not final payment authorization.`
- [ ] Save and confirm the row appears with status `DRAFT`.
- [ ] Activate and confirm status becomes `ACTIVE`.
- [ ] Archive and confirm status becomes `ARCHIVED`.
- [ ] Confirm no payment report/export is generated during the lifecycle.

## Invalid Input Smoke

- [ ] Missing amount is rejected with a visible safe error.
- [ ] Zero amount is rejected with a visible safe error.
- [ ] Negative amount is rejected with a visible safe error.
- [ ] Page remains usable after each rejection.
- [ ] No invalid `ACTIVE` rate is created.

## Role Access Smoke

### Staff

Use `araya.fa / staff123`, selected role `staff`.

- [ ] Staff can access the page.
- [ ] Staff can view configured rate rules.
- [ ] Create/edit/activate/archive actions are unavailable or safely rejected.

### Teacher

Use `kiancheng.lee / teacher123`, selected role `teacher`.

- [ ] Rate-rule navigation item is absent.
- [ ] Direct access to `/invigilation-rate-rules` is blocked or redirected.

### Print Shop

Use `printshop.ops / print123`, selected role `print_shop`.

- [ ] Rate-rule navigation item is absent.
- [ ] Direct access to `/invigilation-rate-rules` is blocked or redirected.

## Screenshot Evidence

Capture if possible:

- [ ] `docs/operations/demo-smoke-screenshots/invigilation-rate-rules-admin.png`
- [ ] `docs/operations/demo-smoke-screenshots/invigilation-rate-rules-active-rate.png`
- [ ] `docs/operations/demo-smoke-screenshots/invigilation-rate-rules-invalid-input.png`

## Final Safety Check

- [ ] Payment calculation remains unimplemented.
- [ ] Advance Batch Preview remains disconnected from rate amounts.
- [ ] No final payment approval exists.
- [ ] No official payment export exists.
- [ ] No teaching workload / Work H / opencourse / coinstruc logic was used.
- [ ] Record browser smoke as PASS only when every required browser check above passes.

