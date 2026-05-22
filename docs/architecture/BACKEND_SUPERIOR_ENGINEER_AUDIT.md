# BACKEND_SUPERIOR_ENGINEER_AUDIT.md

**Date**: 2026-05-22  
**Scope**: `backend/main.py`, routers, services, repositories, models, config, auth, security, tests

---

## What The Backend Currently Is

EMS backend is a substantial FastAPI + SQLAlchemy application with:

- a broad route surface (`30` router files)
- a deep service layer (`178` service files)
- a partial repository pattern (`20` repository files)
- extensive test coverage (`1422` passing tests in this audit pass)
- strong internal policy, analytics, audit, and workflow capabilities

It is not a toy backend. It is a mature application with real operational structure, but it still carries several deployment-hardening and maintainability risks.

---

## Confirmed Strengths

- **Strong automated backend coverage**: `pytest` passed `1422` tests.
- **Structured auth baseline**: current auth uses JWT + HttpOnly cookie with token revocation support.
- **Role-aware permission infrastructure**: `permissions.py` centralizes many RBAC decisions and object-level authorization helpers exist.
- **Operational layering exists**: services, repositories, serializers, validators, and event handlers are real subsystems, not empty placeholders.
- **Health and observability surfaces exist**: health router, request logging middleware, request IDs, security headers, and rate limiting are present.
- **Database model discipline is better than average**: `models.py` includes meaningful indexes and uniqueness constraints across key tables.
- **Import pipeline is modularized**: `backend/import_v2/` is separated from the route layer and validated by health checks and tests.

---

## High-Priority Findings

| Priority | Finding | Evidence | Risk |
|---|---|---|---|
| Critical | Startup mutates schema and seeds data on every app boot | `backend/main.py` runs `Base.metadata.create_all(bind=engine)` and `seed_data(db)` inside lifespan | Unsafe for production startup; blurs deploy vs. runtime responsibilities |
| High | Database misconfiguration can silently fall back to local SQLite | `backend/database.py` uses `backend/ems.db` when `DATABASE_URL` is missing | Can mask broken production config and produce false-positive local readiness |
| High | Secret enforcement is split across two different env-name conventions | `config/settings.py` uses `ENVIRONMENT`; `security.py` uses `ENV` | Hardening behavior may differ by environment naming and produce inconsistent safety |
| High | Secret policy thresholds differ across modules | `config/settings.py` requires 50+ chars in production; `security.py` only checks 32+ chars | Confusing and potentially inconsistent deployment expectations |
| High | Readiness endpoint documentation and implementation are misaligned | `backend/routers/health.py` says admin/internal only, but current code does not enforce that boundary | Health surface may expose more than intended on pilot infrastructure |
| High | Login still returns bearer token in response body | `backend/routers/auth.py` returns `access_token` alongside HttpOnly cookie | Increases token exposure risk for browser clients |
| High | Laravel / CMU integration is not implemented, only documented | `backend/cmu_sso.py` remains a stub and current auth is still internal EMS auth | Faculty LAN integration readiness is operationally blocked |

---

## Maintainability Findings

| Area | Evidence | Impact | Recommendation |
|---|---|---|---|
| Monolithic entrypoint | `backend/main.py` mixes startup, middleware, router registration, exception handling, SPA serving, and health route | Harder to reason about and test | Split app factory, middleware registration, and route wiring |
| Monolithic ORM file | `backend/models.py` is ~71 KB and covers many unrelated domains | Schema evolution and review friction | Partition models by bounded context or domain modules |
| Permission wiring brittleness | `permissions.py` starts with stub guards and depends on `build_dependencies()` at startup | Runtime correctness depends on startup ordering | Replace stub rebinding with direct dependencies or explicit app factory injection |
| Mixed migration strategy | Many standalone `migrate_*.py` scripts, no visible Alembic-style migration chain | Change tracking and DB ownership are harder to manage | Standardize migration ownership and toolchain before pilot DB cutover |
| Dual health surfaces | `/api/health/*` and root `/health` both exist | Not wrong, but policy and ownership can drift | Document authoritative probe endpoints clearly |

---

## Auth / Permission / PDPA Observations

- Current EMS auth is coherent for standalone use:
  - login
  - `/me`
  - logout
  - View-As for base admin
- `resolve_request_auth()` prefers the session cookie and falls back to bearer token.
- Revoked-token support exists.
- Backend role enforcement is real and should remain the authority during any Laravel bridge work.

Risks:

- returning a bearer token in response body weakens the otherwise cleaner cookie-first model
- Laravel docs assume future `cmu_email` mapping, but current `User` model only exposes `email`
- current bridge design remains additive only; no faculty contract has been verified in code

---

## Test Coverage Assessment

Backend coverage is a major strength.

Validated in this audit:

- compile check passed
- import smoke of `main` passed
- `1422` tests passed

Observed warning debt:

- SQLAlchemy `declarative_base()` deprecation warning
- multiple Pydantic class-based config deprecation warnings
- development fallback warning for `SECRET_KEY`

These are not immediate blockers for pilot, but they are real technical debt.

---

## Production Readiness Assessment

### Strong

- test coverage
- core auth flow
- route breadth
- policy / analytics / audit structure
- non-SQLite pool tuning when PostgreSQL is configured

### Weak

- startup mutation behavior
- environment hardening consistency
- migration governance
- unverified external auth bridge
- local SQLite fallback in the same runtime path as production

---

## Recommended Refactors

### Must fix before Faculty LAN pilot

1. remove schema creation and seed execution from normal app startup
2. unify secret / environment detection (`ENV` vs `ENVIRONMENT`)
3. decide whether bearer token in login response remains allowed for browsers
4. clarify and lock down readiness endpoint access policy

### Should fix after pilot

1. split `main.py`
2. split `models.py`
3. formalize migrations
4. reduce auth / permission overlap between `auth_utils.py` and `permissions.py`

### Leave as is for now

- service layer depth
- repository partial adoption
- import pipeline separation
- test suite structure
