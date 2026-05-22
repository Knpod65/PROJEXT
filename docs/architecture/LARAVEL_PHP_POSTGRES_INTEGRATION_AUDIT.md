# LARAVEL_PHP_POSTGRES_INTEGRATION_AUDIT.md

**Date**: 2026-05-22  
**Audit Rule**: Laravel-side claims were treated as unverified unless supported by repository docs or EMS code

---

## Executive Summary

EMS is **conceptually ready** to integrate with a Laravel / PHP / PostgreSQL faculty stack, but it is **not implementation-ready** for that bridge today.

Why:

- EMS current auth model is coherent and self-contained.
- The faculty-side contract is still draft-only.
- The current EMS data model and current auth routes do not yet implement the documented bridge assumptions.
- The safest integration path is still Option B (short-lived server-side bridge code), but it must remain blocked until the Laravel owner answers the contract questions.

---

## 1. Current EMS Auth Model

Confirmed from code:

- EMS currently authenticates through `POST /api/auth/login`
- backend issues JWT tokens
- session cookie `ems_session` is HttpOnly and scoped to `/api`
- backend still also returns the bearer token in the login response body
- role resolution remains EMS-database authoritative
- `backend/cmu_sso.py` is present but inactive unless CMU env vars are provided

This means EMS is already structured to own its own post-login session state, which is helpful for a Laravel bridge.

---

## 2. Verified Compatibility Points

| Area | Current EMS State | Compatibility |
|---|---|---|
| Backend-issued session after identity verification | Already supported | Strong |
| HttpOnly cookie pattern | Already supported | Strong |
| DB-authoritative role resolution | Already supported | Strong |
| Audit logging on auth events | Present | Strong |
| Reverse proxy / Nginx deployment model | Present conceptually | Medium |
| PostgreSQL deployment support | Present | Medium |
| Current direct CMU OAuth stub | Present but inactive | Medium |

---

## 3. Verified Gaps Or Mismatches

| Area | Evidence | Audit Meaning |
|---|---|---|
| `cmu_email` field assumption | Current `User` model exposes `email`, not a dedicated `cmu_email` column | Integration docs describe a future-state mapping, not an implemented one |
| Laravel contract data | Docs repeatedly mark `session("USS")`, `cmu_at`, route names, controller names, and payload structure as preliminary | No safe implementation should be derived from these as facts |
| Faculty config / integration admin pages | frontend and backend expose partial integration/config views, but not a verified bridge workflow | Support tooling exists, but bridge runtime does not |
| Cookie/domain behavior | Nginx and route mapping docs are conceptual only | Must be tested on the real Faculty LAN topology |

---

## 4. Risk Assessment

| Topic | Status | Risk |
|---|---|---|
| `session("USS")` payload | Unverified | Critical |
| `cmu_at` meaning and lifecycle | Unverified | Critical |
| callback route and controller names | Unverified | High |
| session driver / cookie domain / SameSite | Unverified | High |
| EMS mount path and reverse-proxy routing | Unverified | High |
| CMU email field name | Unverified | Critical |
| logout and expiry coordination | Unverified | Medium |
| DB ownership between Laravel and EMS | Not contracted | High |

---

## 5. Recommended Integration Option

### Recommended: Option B

Laravel issues a short-lived one-time bridge code, and EMS exchanges that code server-to-server for verified identity.

Why this is still the safest option:

- keeps raw CMU token handling out of the EMS frontend
- avoids cross-framework shared-session complexity
- fits EMS current model of issuing its own internal session after identity verification
- preserves EMS role authority in EMS DB

### Acceptable fallback

- Option D only as a temporary pilot fallback if the Laravel contract is not available in time

### Not recommended as the default

- Option A unless the shared-session contract becomes very explicit
- Option C unless IT proves that header spoofing is impossible and backend access is fully isolated

---

## 6. What Must Not Be Implemented Yet

Do **not** implement any of the following until the contract is verified:

- direct trust in `session("USS")`
- any parsing logic for Laravel session payloads
- any assumption about the `cmu_at` variable shape
- any fixed callback route or middleware chain
- any shared-table design with Laravel auth tables
- any reverse-proxy header trust path without network isolation proof

---

## 7. Required IT / Laravel Answers

Before implementation, the faculty owner must confirm:

1. exact route and controller names
2. exact `session("USS")` payload structure
3. exact CMU email field name
4. session driver and cookie policy
5. whether Laravel can issue and validate one-time bridge codes
6. route mount path for EMS on Faculty LAN
7. whether EMS gets a separate PostgreSQL database
8. logout / expiry coordination rules

---

## 8. PostgreSQL / Ownership Compatibility

Audit recommendation:

- **Preferred**: separate EMS database on the same PostgreSQL server
- **Acceptable second choice**: separate EMS schema only if IT cannot provide a separate DB
- **Do not do**: mix EMS tables into Laravel application tables without an explicit contract and ownership model

Rationale:

- EMS uses its own SQLAlchemy model and migration style
- Laravel ownership is different
- schema evolution boundaries should remain explicit

---

## 9. Pilot Recommendation

### Ready for local rehearsal?

Yes. EMS standalone auth and current deployment model can support local rehearsal.

### Ready for Faculty LAN pilot with Laravel bridge?

Not yet.

What must happen first:

1. Laravel contract answers returned
2. route/mount decision made
3. database ownership decided
4. bridge option confirmed
5. backup / DPO / prod env blockers closed

Until then, the safest pilot fallback is EMS standalone auth on Faculty LAN, not an assumed Laravel bridge.
