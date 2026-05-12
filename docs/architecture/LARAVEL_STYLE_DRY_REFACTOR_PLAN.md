# Laravel-Style DRY Refactor Plan
## EMS Academic Operations Platform - 2026-05-12

> Goal: reduce duplication by translating Laravel-style architectural discipline into FastAPI/React patterns without rewriting the system.

---

## 1. Plan Table

| Area | Current duplication | Target structure | Safe fix | Risky fix | Recommended phase |
|---|---|---|---|---|---|
| Route DRY | Large routers repeat response shaping, `db.query()` blocks, and endpoint-local ownership checks | One router per domain with small handlers and shared response helpers | Add repositories/services first; keep routes stable | Moving many endpoints at once | Phase B-C |
| Middleware / auth DRY | `auth_utils.py` and `permissions.py` both own parts of auth semantics | `auth_utils.py` for session mechanics, `permissions.py` plus policies for authorization | Keep compatibility wrappers; add auth integration service; continue semantic helper reuse | Removing old auth helpers too early | Phase B-D |
| Controller / router DRY | Router handlers repeat validation, ORM loading, and audit calls | Thin routers calling service methods | Expand services one domain at a time | Broad router rewrites across multiple domains | Phase B-C |
| Service DRY | Current service layer covers only a few domains | Named service per bounded workflow | Continue additive service creation | Mixing repository and router logic inside services without boundaries | Phase B-C |
| Repository DRY | ORM query patterns are duplicated across routers | `backend/repositories/*` owns repeated joins, filters, and lookup paths | Start with user and student repositories | Moving all queries at once without tests | Phase A-C |
| Model DRY | Some duplicated derived logic still lives outside models; models file is large | ORM models keep only persistence and light computed properties | Keep small computed properties only | Pushing business workflows into ORM models | Ongoing guardrail |
| View / React DRY | Several pages still mix controller logic and view rendering | Page -> hook -> service -> component pattern | Expand hook usage on heavy pages | Rebuilding page architecture and UI together | Phase E |
| Validation DRY | Pydantic is centralized, but domain validation still leaks into routers | `schemas.py` + domain validators | Add validator modules beside future services | Splitting schemas and validators too aggressively before service extraction | Phase B-D |
| Audit DRY | Many routers still call `log_action()` directly | `audit_service` as the semantic audit entry point | Use `audit_service` for all new/changed workflows | Backfilling every old route in one pass | Phase B-D |
| PDPA DRY | Sensitivity and masking choices live in docs and router comments | `policies/pdpa_policy.py` as the canonical helper layer | Use central classification helpers for new work | Retrofitting every public/export path immediately without tests | Phase A-D |

---

## 2. Current Duplication by Layer

### Route duplication
- `backend/routers/schedule.py`, `documents.py`, `submissions.py`, and `exports*.py` repeat large ORM loading blocks with similar `joinedload()` chains.
- Student-schedule data access logic is duplicated conceptually between `public.py` and document/export paths.

### Auth duplication
- Session resolution is in `auth_utils.py`.
- Permission guards are in `permissions.py`.
- Semantic checks are partly in `services/permission_service.py`.
- Some frontend hooks/pages still derive role behavior manually.

### Audit duplication
- Older routers use `auth_utils.log_action()` directly.
- Newer changes use `services/audit_service.py`.
- The semantic action names are not yet consistently routed through one abstraction.

### Frontend duplication
- Large pages still bundle fetch orchestration, state shaping, and view rendering.
- Inline role branching remains in a few pages/hooks such as `Optimizer.tsx`, `ExportCenter.tsx`, `ExamManager.tsx`, and `useSwapsData.ts`.

---

## 3. Safe Refactor Principles

- Preserve URL structure and existing auth/session behavior.
- Keep compatibility imports in place while new layers are introduced.
- Extract read-only query code before mutation workflows when possible.
- Add tests around pure logic before moving business-critical code.
- Prefer “new service + one call site” over “rename everything.”

---

## 4. Recommended Phases

### Phase A - scaffolding and contracts
- Completed in this pass:
  - `backend/repositories/*`
  - `backend/policies/pdpa_policy.py`
  - `backend/services/auth_integration_service.py`
  - architecture guidance docs

### Phase B - submissions and auth
- Expand `submission_service.py`
- Add `submission_repository.py`
- Route submission approve/reject/release/message flows through service methods
- Add `auth_policy.py` and use it beside `permissions.py`

### Phase C - schedule and workflow
- Add `schedule_service.py`, `schedule_repository.py`, `room_repository.py`
- Move list/update/copy-count logic out of `schedule.py`
- Separate workflow-lock and signature logic from `optimize_workflow.py`

### Phase D - exports, PDPA, and policies
- Add `export_policy.py`
- Centralize export sensitivity decisions
- Move more `log_action()` usage through `audit_service`
- Introduce audit repository only if query reuse justifies it

### Phase E - frontend MVC cleanup
- Turn heavy pages into page + hook + section-component splits
- Keep services as the only API callers
- Route all role gating through `permissions.ts`
- Continue i18n extraction and table/layout standardization

---

## 5. What Was Implemented Now

### Safe fixes completed
- Repository package scaffolding for users and students
- PDPA policy module with centralized field classification and masking helpers
- Auth integration service skeleton for `callback/authen` compatibility
- Pure-function tests for the new modules
- Documentation for backend and frontend Laravel-style alignment

### Intentionally deferred
- No broad router extraction
- No token/session format change
- No schema migration for external identity tables
- No change to current username/password login
- No frontend behavioral change beyond documentation guidance

---

## 6. Decision Summary

EMS should adopt Laravel-style discipline through layering, naming, and separation of concerns. EMS should not adopt Laravel by rewriting the runtime stack.
