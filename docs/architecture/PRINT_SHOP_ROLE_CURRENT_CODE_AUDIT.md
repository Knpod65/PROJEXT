# PRINT_SHOP_ROLE_CURRENT_CODE_AUDIT.md

**Date**: 2026-05-25
**Purpose**: Record the confirmed current-code state of the `print_shop` role and related print routes without changing any implementation.

---

## Files Reviewed

- `backend/models.py`
- `backend/auth_utils.py`
- `backend/routers/printing.py`
- `frontend/src/App.tsx`
- `frontend/src/utils/roles.ts`
- `frontend/src/pages/PrintQueue.tsx`
- `frontend/src/pages/PrintReview.tsx`

---

## Confirmed Current State

| Area | Confirmed finding |
|---|---|
| Role model | `print_shop` exists in backend `UserRole` and frontend role types |
| Default route | Frontend maps `print_shop` to `/print-queue` |
| Frontend route guard | `/print-queue` is protected for `print_shop` |
| Backend guard | `require_print_shop` exists in `backend/auth_utils.py` |
| Backend printing API | `backend/routers/printing.py` exposes `/queue`, `/queue/{id}`, and status-transition endpoints guarded by `require_print_shop` |
| Print review | `/printreview` exists, but it is not the print-shop route family described by current frontend routing |
| Existing auth model | EMS currently uses native EMS login plus a dormant `backend/cmu_sso.py` stub; no verified Laravel bridge exists yet |

---

## Current Auth Assumptions in Code

- EMS login is still username/password based for runtime use.
- Frontend includes an SSO button that redirects to `/api/auth/sso/login`.
- `backend/cmu_sso.py` is still a stub and returns not-configured behavior unless env vars are present.
- Current code does not establish a verified external partner identity owner for `print_shop`.

---

## What Would Need to Change Later

- Decide who owns external print-shop identity.
- Decide whether print-shop login is EMS-local, Laravel-owned, signed-link based, or another approved model.
- Keep `print_shop` backend enforcement authoritative regardless of login source.
- Ensure print-shop access stays separated from student-facing and internal CMU route families.

---

## Non-Conclusion Rule

This audit confirms that `print_shop` already exists as a real EMS role and workflow surface. It does **not** approve any current external authentication design for that role.

---

**End of PRINT_SHOP_ROLE_CURRENT_CODE_AUDIT.md**
