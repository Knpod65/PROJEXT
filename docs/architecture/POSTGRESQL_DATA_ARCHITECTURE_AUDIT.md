# POSTGRESQL_DATA_ARCHITECTURE_AUDIT.md

**Date**: 2026-05-22

---

## Summary

EMS is designed to run on PostgreSQL in serious environments, but it still carries a development-friendly fallback path and a manual migration style that are acceptable for internal development yet weaker than desired for Faculty LAN pilot governance.

---

## Current Database Architecture

Confirmed from code and deployment assets:

- SQLAlchemy ORM with a large unified `models.py`
- `database.py` configures PostgreSQL pooling when `DATABASE_URL` is non-SQLite
- Docker Compose provisions PostgreSQL 16
- many tables include meaningful uniqueness constraints and indexes
- repository layer exists, but only partially across domains
- no visible Alembic-style migration framework; instead, many `migrate_*.py` scripts exist

---

## Strengths

- non-SQLite pool settings are present
- many domain tables are explicitly indexed
- repository usage exists in important domains
- backend tests pass at scale, which raises confidence in current DB-facing behavior
- backup-related operations docs exist

---

## Risks

| Priority | Finding | Evidence | Impact |
|---|---|---|---|
| High | Missing `DATABASE_URL` falls back to local SQLite | `backend/database.py` | Can hide broken deploy config and split operational data from intended PostgreSQL target |
| High | Schema creation runs at app startup | `Base.metadata.create_all(bind=engine)` in `main.py` | Runtime node is doing deployment-time DB mutation |
| High | Seeding runs at app startup | `seed_data(db)` in `main.py` | Startup side effects are risky in shared or production-like environments |
| High | Migration ownership is not clearly standardized | many standalone `migrate_*.py` scripts | Harder DB governance and repeatability |
| Medium | Current model is monolithic | `models.py` is large and cross-domain | Harder schema review and ownership |
| Medium | Laravel docs assume future email/identity mapping changes | EMS current `users` table has `email`, not a separate `cmu_email` field | Bridge design needs a schema decision before rollout |

---

## Transaction And Repository Assessment

### Positive

- `get_db()` correctly rolls back on exceptions and always closes sessions
- repository modules exist for several high-value domains
- service layer carries much of the orchestration instead of pushing everything into routers

### Gaps

- repository pattern is not uniformly applied across all domains
- migration scripts suggest schema evolution is still partly manual
- startup-time seeding makes transactional lifecycle harder to reason about in production

---

## Backup / Restore Compatibility

Deployment and operations docs indicate a real backup strategy exists:

- PostgreSQL in Docker Compose
- cron backup service
- backup and restore runbooks
- evidence templates for restore testing

Current audit judgment:

- strategy exists
- real operational proof is still missing
- backup architecture is more ready than backup evidence

---

## Faculty PostgreSQL Compatibility Recommendation

### Recommended for pilot

Use a **separate EMS database** on the faculty PostgreSQL server.

### Acceptable if infrastructure requires it

Use a **separate EMS schema** in faculty PostgreSQL with explicit ownership boundaries.

### Avoid

- sharing Laravel application tables
- mixing EMS migration ownership with Laravel migration ownership
- using SQLite anywhere in Faculty LAN pilot execution

---

## Migration Ownership Recommendation

Before Faculty LAN pilot:

1. define who owns DB schema change approval
2. define one migration process
3. remove runtime dependency on `create_all()` for normal startup
4. record whether first-login Laravel bridge work needs a schema change for email identity handling

---

## Audit Judgment

PostgreSQL readiness is **moderate**:

- technically compatible
- operationally plausible
- governance and migration discipline still need tightening

The most important DB decision is not technical connectivity. It is **clear ownership and separation from the faculty Laravel schema**.
