# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EMS** (Exam Management System) — ระบบจัดการข้อสอบ คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มหาวิทยาลัยเชียงใไม่

A full-stack exam scheduling and supervision management system for Chiang Mai University. Key capabilities: constraint-based exam scheduling (Google OR-Tools), supervision assignment, PDF generation, bulk data imports, role-based access (8 roles), and audit logging.

---

## Commands

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev          # dev server on port 3000
npm run build        # tsc -b && vite build
```

### Docker (recommended for full stack)

```bash
# Development (hot reload, SQLite)
docker compose -f docker-compose.dev.yml up --build

# Production (PostgreSQL + Nginx)
docker compose up --build -d
```

### Type-check frontend (no test suite exists yet)

```bash
cd frontend && npx tsc --noEmit
```

> There is currently **no automated test suite** (no pytest, no vitest). Manual testing credentials and cURL examples are documented in `RUNBOOK.md`.

---

## Architecture

### Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (async) + SQLAlchemy ORM |
| Database | PostgreSQL (prod) / SQLite (dev, `ems.db`) |
| Server | Uvicorn dev / Gunicorn + UvicornWorker prod |
| Frontend | React 18 + TypeScript + Vite 5 |
| Routing | React Router v6 |
| State | Context API (`store/`) |
| Proxy | Nginx (prod) |
| PDF | WeasyPrint (requires GTK; use Docker on Windows) |
| Scheduler | Google OR-Tools constraint solver |

### Backend Layout

- **`main.py`** — App entry point. Registers all routers, middleware stack, and runs `seed_data()` on startup.
- **`models.py`** — All SQLAlchemy ORM models in one file (16 tables).
- **`schemas.py`** — All Pydantic v2 request/response models in one file.
- **`routers/`** — One file per feature domain, each mounted in `main.py` under `/api/<domain>`.
- **`permissions.py`** — RBAC logic; use `Depends(require_admin)` etc. in router functions.
- **`auth_utils.py`** — Bcrypt password hashing, JWT token creation.
- **`security.py`** — Cookie helpers, `validate_production_secrets()` (called at startup).
- **`database.py`** — Engine, session factory, `get_db` dependency.
- **`seed.py`** — Dev data seeded on every startup (must remain idempotent).

### Middleware Order (main.py)

1. `CORSMiddleware` (ALLOWED_ORIGINS env var)
2. `RequestLoggingMiddleware` — injects `X-Request-ID`, structured JSON logs
3. `SecurityHeadersMiddleware` — X-Frame-Options, X-Content-Type-Options, etc.
4. `LoginRateLimitMiddleware` — 10 attempts / 5 min per IP

### Frontend Layout

- **`pages/`** — Top-level route components (one per URL).
- **`components/`** — Feature-scoped subdirectories (`layout/`, `schedule/`, `submissions/`, etc.) plus generic `ui/`.
- **`services/`** — One file per API domain; all calls go through `services/api.ts` with `credentials: "include"`.
- **`store/`** — Three Context providers: `auth.store.tsx` (user + impersonation), `period.store.tsx` (active semester), `ui.store.tsx` (toasts).
- **`types/`** — TypeScript interfaces mirroring backend Pydantic schemas.
- **`utils/roles.ts`** — Frontend RBAC helpers.

### Auth Flow

- **HttpOnly session cookies** are the primary auth mechanism (XSS-safe). Bearer token also returned in body for legacy clients.
- `ProtectedRoute` component enforces role-based access in the router.
- Admin can impersonate any role via "view-as" (tracked in `AuditLog`).

### Key Feature: Exam Scheduler

`routers/optimize_workflow.py` — wraps Google OR-Tools CP-SAT solver. Takes courses, rooms, and constraints as input; emits `ExamSchedule` rows. This is the most complex module; constraint logic lives in a separate solver class invoked by the router.

---

## Conventions

### Backend

- Router functions use `Depends(get_db)` and RBAC dependencies (e.g., `Depends(require_admin)`); never open a raw session inside a handler.
- Commit inside the endpoint, rely on FastAPI's exception handler for rollback.
- Error messages may be in Thai for user-facing 4xx responses.
- `swaps_v2.py` is the active implementation; `swaps.py` is the legacy version kept for reference during migration.

### Frontend

- All API calls use `credentials: "include"` (cookies); never store tokens in `localStorage`.
- 401 responses automatically clear auth state (handled in `services/api.ts`).
- TypeScript strict mode is on — no `any` unless unavoidable.

### Environment Variables

Defined in `.env` (copy from `.env.example`). Key vars:

```
POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB
SECRET_KEY          # JWT signing key — generate with secrets.token_hex(32)
CRON_SECRET         # Cron job auth
APP_URL             # Public base URL
ALLOWED_ORIGINS     # Comma-separated CORS origins
TOKEN_EXPIRE_HOURS
```

Dev uses SQLite by default (no Postgres needed). Prod requires `SECRET_KEY` to pass `validate_production_secrets()` or the app will refuse to start.

---

## Known Tech Debt

- `migrate.py`, `migrate_local.py`, `migrate_v2.py` are ad-hoc migration scripts — no Alembic workflow is in place.
- `ems.db-shm` / `ems.db-wal` (SQLite WAL artifacts) should not be committed.
- No automated test suite exists for either backend or frontend.
