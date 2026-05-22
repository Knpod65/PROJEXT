# SECURITY_PDPA_AUTHORIZATION_AUDIT.md

**Date**: 2026-05-22

---

## Summary

EMS has real security structure in place: secret checks, request logging, RBAC, revocable sessions, PDPA-oriented documentation, and guarded routes. The main remaining security risks are **environment hardening consistency**, **unverified external auth integration**, **operational proof gaps**, and **a few runtime behaviors that remain more permissive than the surrounding docs imply**.

---

## Critical Risks

| Risk | Evidence | Why Critical |
|---|---|---|
| Laravel session / `cmu_at` / CMU identity contract is still unverified | Integration docs explicitly mark these as draft-only | Auth bridge implementation would be unsafe without verified contract facts |
| Production secret enforcement is split across inconsistent env assumptions | `ENVIRONMENT` vs `ENV`; different minimum lengths; compose uses `change-me` defaults | Misconfiguration could bypass intended hardening or confuse ops |

---

## High Risks

| Risk | Evidence | Impact |
|---|---|---|
| Login returns bearer token in response body | `backend/routers/auth.py` | Increases exposure of tokens that could otherwise remain cookie-only |
| DB fallback to SQLite when `DATABASE_URL` missing | `backend/database.py` | Can hide broken production config and undermine pilot-data governance |
| Readiness endpoint access policy is not enforced as documented | `backend/routers/health.py` docstring says admin/internal; implementation does not enforce that boundary | Information exposure or policy drift on Faculty LAN |
| Startup creates schema and seeds data | `backend/main.py` | Deploy/runtime boundary is too permissive for hardened environments |
| Compose defaults still advertise `change-me` placeholders | `.env.example`, `docker-compose.yml` | Safe only if ops replaces them correctly every time |

---

## Medium Risks

| Risk | Evidence | Impact |
|---|---|---|
| Raw string debt remains in frontend | `check:i18n:raw` warning output | UX and message consistency risk, not direct auth bypass |
| Backup and DPO controls are documented but not yet evidenced | ops docs still track blockers | Pilot cannot claim full operational readiness yet |
| Frontend has no strong automated test coverage | no meaningful app tests found | More chance of UI-level authorization regressions slipping through |

---

## Accepted Pilot Risks

These may be tolerable for a controlled internal pilot, but not as final-production standards:

- noisy raw-string candidate scan
- bundle-size warning
- monolithic model and route files
- partial platform-config UI wiring that is not on the core pilot path

They should remain documented and visible, not silently ignored.

---

## Authorization Assessment

### Strong

- backend owns role enforcement
- View-As is limited to base admin
- role-aware route guards exist on frontend
- backend object-level authorization helpers exist

### Weak / Watchlist

- some auth and permission logic still spans both `auth_utils.py` and `permissions.py`
- frontend should never be treated as the real authority; backend must stay authoritative during any Laravel bridge work

---

## PDPA Observations

Positive:

- PDPA is treated explicitly in docs and architecture materials
- audit logging exists
- export and operational workflows are role-aware

Open gaps:

- DPO sign-off is still operationally open
- backup and restore evidence is still open
- Laravel / CMU identity data flow has not been contract-verified with faculty stakeholders

---

## Must-Fix Before Production

1. unify environment and secret-hardening logic
2. remove startup schema/seed mutation from normal runtime
3. verify and design the Laravel bridge without trusting client-side claims
4. complete backup / DPO operational evidence
5. decide whether login should continue returning bearer tokens in response bodies

---

## Must-Verify Before Faculty LAN Pilot

1. faculty-side auth contract
2. database target and ownership
3. route mount path and cookie/domain behavior
4. real secret / DB env config on target host
5. backup and restore proof
6. DPO sign-off

---

## Audit Judgment

Security and PDPA posture is **stronger than average for an internal faculty system**, but it is not yet fully hardened for integrated pilot operation because the external auth contract and operational evidence chain are still incomplete.
