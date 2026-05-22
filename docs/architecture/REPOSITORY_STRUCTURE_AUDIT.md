# REPOSITORY_STRUCTURE_AUDIT.md

**Date**: 2026-05-22  
**Tracked file count**: `923`

---

## Summary

EMS is a real full-stack repository with substantial backend, frontend, documentation, and deployment assets.

- `backend/` is the primary runtime and the largest tracked area (`338` tracked files).
- `docs/` is extensive (`300` tracked files) and contains both active and historical architecture/operations material.
- `frontend/` is also substantial (`262` tracked files) and mixes active runtime code, migration-era V2 pages, and internal frontend docs.
- The repository also contains local/generated directories that are not production source and must not be confused with runtime assets.

---

## Top-Level Structure

| Path | Classification | Notes |
|---|---|---|
| `.github/` | CI / governance | Workflow automation for backend, frontend, and architecture checks |
| `backend/` | Production runtime | FastAPI, SQLAlchemy, services, routers, tests, policies, validators |
| `docs/` | Documentation | Architecture, operations, deployment, humanization, exam-operation notes |
| `frontend/` | Production runtime | React SPA, hooks, services, pages, i18n, styles |
| `opt/` | Unknown / external context | Present under repo root but not part of active runtime surfaced in audit |
| `scripts/` | Deployment / support | Small support script area |
| `static/` | Runtime static assets | Shared top-level static directory |
| `.pytest_cache/` | Generated | Test cache, not source |
| `.vscode/` | Local editor config | Local tooling only |
| root `Dockerfile`, compose files, `nginx.conf` | Deployment | Faculty LAN / container deployment inputs |
| root `README-DEV.md`, `RUNBOOK.md`, status markdowns | Historical / support docs | Mixed guidance and earlier progress artifacts |

---

## Backend Structure

Key backend directories by file count:

| Directory | File Count | Classification | Notes |
|---|---:|---|---|
| `backend/tests` | 251 | Tests | Strong service/policy/router coverage |
| `backend/services` | 178 | Production runtime | Main application orchestration layer |
| `backend/routers` | 83 | Production runtime | HTTP route layer |
| `backend/policies` | 46 | Production runtime | Permission and policy logic |
| `backend/serializers` | 40 | Production runtime | Response shaping |
| `backend/validators` | 20 | Production runtime | Domain validation helpers |
| `backend/repositories` | 20 | Production runtime | Partial repository layer |
| `backend/contracts` | 14 | Production/runtime-support | Internal contracts and typed registries |
| `backend/import_v2` | 12 | Production runtime | Structured import pipeline |
| `backend/event_handlers` / `backend/events` | 10 / 14 | Production runtime | Event-driven support layer |
| `backend/config` / `backend/config_models` | 12 / 12 | Production runtime | Config and typed config models |
| `backend/.venv` | 12996 | Generated / local environment | Not repository source |
| `backend/__pycache__`, `backend/logs` | generated | Generated | Not source |

Notable backend top-level files:

- `main.py` is the runtime entrypoint and also contains substantial middleware and routing setup.
- `models.py` is a very large monolithic ORM model file.
- `database.py` owns DB initialization and fallback behavior.
- multiple `migrate_*.py` scripts exist instead of a single migration framework such as Alembic.

---

## Frontend Structure

Key frontend directories by file count:

| Directory | File Count | Classification | Notes |
|---|---:|---|---|
| `frontend/src/components` | 87 | Production runtime | Shared UI and feature components |
| `frontend/src/pages` | 45 | Production runtime + legacy surfaces | Route-level pages, including active V2 and legacy pages |
| `frontend/src/hooks` | 36 | Production runtime | Data hooks and domain hooks |
| `frontend/src/services` | 33 | Production runtime | API wrappers and service modules |
| `frontend/src/utils` | 23 | Production runtime | Formatting, presenters, helpers |
| `frontend/src/types` | 9 | Production runtime | Shared TS contracts |
| `frontend/src/i18n` | 3 | Production runtime | Translation dictionaries and provider |
| `frontend/src/docs` | 2 | Internal docs | Not runtime; can drift from actual App routing |
| `frontend/node_modules` | generated | Generated | Not source |
| `frontend/dist` | generated | Generated build output | Not source of truth |
| `frontend/test-results` | generated / suspicious | Generated test artifact area; `.last-run.json` is tracked |

---

## Docs Structure

| Directory | File Count | Classification | Notes |
|---|---:|---|---|
| `docs/humanization` | 129 | Humanization / manuals | Role manuals, screenshot atlas, journeys |
| `docs/architecture` | 105 | Architecture / audits | Largest planning and audit archive |
| `docs/operations` | 27 | Active operations docs | Runbooks, blockers, UAT, evidence templates |
| `docs/deployment` | 9 | Deployment / integration | Faculty LAN + Laravel integration docs |
| `docs/exam_operation` | 7 | Historical / domain analysis | Legacy process comparison and modernization framing |

---

## Deployment Assets

Production and pilot deployment files found at repo root:

- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.local.yml`
- `docker-compose.dev.yml`
- `nginx.conf`
- `.env.example`

These are real deployment assets, but they still include development or placeholder defaults and should not be treated as fully hardened production configuration.

---

## Test Structure

| Area | Evidence |
|---|---|
| Backend tests | `backend/tests/` contains `251` files; `pytest` passed `1422` tests in this audit pass |
| Frontend tests | No real app-level frontend test suite was found in repo source; only a tracked `frontend/test-results/.last-run.json` artifact exists |
| CI workflows | `.github/workflows/` contains backend, frontend, and architecture validation workflows |

---

## Prototype / Research Structure

| Path | Classification | Notes |
|---|---|---|
| `docs/architecture/prototypes/README.md` | Prototype / research | Explicit non-production guidance |
| `docs/humanization/dashboard-guides/futures-intelligence.md` and related future-intelligence docs | Research / future-state documentation | Valuable, but not current pilot runtime requirements |
| older roadmap / futures docs under `docs/architecture` | Historical / concept | Should not be mistaken for active pilot contract documents |

---

## Generated And Suspicious Files

| Path | Classification | Why It Matters |
|---|---|---|
| `backend/.venv/` | Generated | Local Python environment, not source |
| `backend/__pycache__/` | Generated | Python bytecode cache |
| `backend/ems.db`, `ems.db-shm`, `ems.db-wal` | Local generated data | Signals SQLite dev usage exists locally |
| root `backend-runtime*.log`, `frontend-runtime*.log`, `localhost-backend*.log`, `probe-backend*.log`, `auth-probe*.log` | Generated local logs | Not production source; easy to misread as deploy evidence |
| `frontend/dist/` | Generated build output | Build result, not source |
| `frontend/test-results/.last-run.json` | Generated artifact, but tracked | Candidate cleanup item because it is machine-generated |
| `frontend/src/docs/EMS_SYSTEM_OVERVIEW.md` | Documentation-only but stale | Conflicts with current `App.tsx` route behavior |

---

## Files Outside Expected Conventions

These are not necessarily wrong, but they deserve review:

- root progress/status docs dated `2026-04-16` / `2026-04-17`
- many standalone migration scripts in `backend/`
- local DB and log artifacts living near runtime code
- tracked generated test artifact `frontend/test-results/.last-run.json`
- internal frontend docs under `frontend/src/docs/` that can drift from the live route map

---

## Repository Classification Rule

For future audits and cleanup:

- treat `backend/`, `frontend/`, deployment files, and active operations docs as primary runtime sources
- treat `.venv`, `node_modules`, `dist`, caches, DB files, and runtime logs as generated or local context
- treat older readiness and migration docs as historical unless they agree with the current code and newer operational documents
