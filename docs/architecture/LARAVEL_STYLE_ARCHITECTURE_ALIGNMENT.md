# Laravel-Style Architecture Alignment
## EMS Academic Operations Platform - 2026-05-12

> Purpose: align EMS with the discipline shown in the Laravel/PHP handwritten reference while preserving the current FastAPI + React stack.
> Constraint: this is an architecture-shaping pass, not a framework rewrite.

---

## 1. Translation Map

| Laravel reference | EMS equivalent | Current status |
|---|---|---|
| `route.php` | `backend/routers/*.py` | Present |
| `AuthMiddleware` | FastAPI dependencies in `auth_utils.py` and `permissions.py` | Present but split |
| `AuthenController` / thin controller | FastAPI router handlers | Present but uneven |
| Model | SQLAlchemy ORM in `backend/models.py` | Present |
| Repository | `backend/repositories/*` | Added as scaffolding in this pass |
| Service | `backend/services/*` | Present but still small |
| FormRequest / validator | Pydantic schemas in `backend/schemas.py` | Present but not fully separated by domain |
| View | React pages/components | Present |
| Session auth | JWT + HttpOnly cookie + auth store | Present |

---

## 2. Architecture Gap Audit

| Layer | Alignment | Current EMS implementation | Laravel-style target | Gap | Risk | Recommended fix |
|---|---|---|---|---|---|---|
| Route mapping | Already disciplined | Route modules are cleanly split under `backend/routers/*.py` with stable URL grouping such as `auth.py`, `schedule.py`, `submissions.py`, `public.py` | Keep route modules small and URL-focused | Main gap is route size, not route existence | Low | Preserve route grouping and thin the largest routers through services |
| Middleware / auth guard | Partially aligned | `auth_utils.py` handles token/session resolution; `permissions.py` exposes `require_*` guards; many routers already use `Depends(require_admin)` style guards | Central policy/middleware layer before controller logic | Auth/session and permission logic are still split across two modules | Medium | Keep current guards, add auth integration service, gradually move semantic checks into services/policies |
| Controller / router handler | Partially aligned | Thin handlers exist in `auth.py`, `health.py`, parts of `pdf.py`; `submissions.py` now has a first extraction slice for list/detail/file-access/message helpers, but large handlers still perform ORM and workflow logic directly in `schedule.py`, `documents.py`, `optimize_workflow.py`, and the remaining submission mutations | Thin router: parse request, call service, return response | High concentration of business workflow inside routers | High | Keep extracting high-value use cases into services first; avoid broad rewrites in one pass |
| Service layer | Partially aligned | `services/permission_service.py`, `audit_service.py`, `health_service.py`, `submission_service.py` exist and now cover submission list/detail access, message validation, access watermarking, and rollback helpers | Named use-case services per domain | Coverage is improving, but still narrow compared with router surface area | Medium | Add service slices by domain and continue moving mutation workflows incrementally |
| Repository layer | Partially aligned | `user_repository.py`, `student_repository.py`, and `submission_repository.py` now exist, but most router query composition still lives inline | `backend/repositories/*` owns query composition and persistence lookup | ORM access is still duplicated across many routers | Medium | Expand repositories around the heaviest routers, starting with `schedule.py` next |
| Policy layer | Partially aligned | `pdpa_policy.py` and `submission_policy.py` centralize some access and exposure rules, but many authorization branches still live inline in routers | `backend/policies/*` for auth, export, schedule, PDPA decisions | Policy coverage is still incomplete across schedule/export/workflow paths | Medium | Add `auth_policy.py`, `schedule_policy.py`, and `export_policy.py` in later phases |
| Validation layer | Partially aligned | `backend/schemas.py` centralizes many request models; some routers still use inline validation and ad hoc checks | Domain validators beside services or schemas | Validation is centralized technically, but not yet domain-organized | Low | Keep Pydantic as the canonical request layer; split domain validators when service extraction begins |
| Model / ORM layer | Already disciplined with limits | `backend/models.py` is ORM-centric with a few lightweight computed properties such as `Course.academic_group` and `ExamSchedule.computed_sheets` | Keep models mostly persistence-focused | Some legacy tables and broad model file size remain, but workflow logic is still mostly outside the models | Low | Keep ORM-only direction; avoid moving heavy workflow into models |
| Audit logging | Partially aligned | `auth_utils.log_action()` is widely used; `services/audit_service.py` now wraps semantic audit paths | Controllers/services call centralized audit service | Old direct `log_action()` usage still dominates, and transaction coupling is incomplete | Medium | Route new work through `audit_service`; migrate router call sites opportunistically |
| Auth integration compatibility | Partially aligned | Current login is username/password with JWT + HttpOnly cookie; docs already point toward callback/authen compatibility | `AuthMiddleware`-style external identity adapter feeding EMS session issuance | No runtime auth integration service existed before this pass | Medium | Add non-breaking `auth_integration_service.py` and keep existing login untouched |
| Frontend page/controller split | Partially aligned | Services exist and are widely used; hooks exist for some routes; heavy pages like `Checkins.tsx`, `Optimizer.tsx`, `MyExam.tsx` still mix orchestration and view | Page = layout/gate, hook = controller, service = data client, component = presentation | Several pages remain “fat controllers + view” combined | Medium | Expand hook-based orchestration on the heaviest pages first |
| Frontend role/UI policy | Partially aligned | `frontend/src/utils/permissions.ts` and `utils/roles.ts` already exist | Central permission helpers for all role-driven UI | Some pages/hooks still use inline role branching | Low | Continue replacing inline checks with permission helpers |
| Risky areas that should not move now | Risky / should not change now | `optimize_workflow.py`, `schedule.py`, `documents.py`, `exam_manager.py`, `external_exams.py`, and the remaining mutation-heavy parts of `submissions.py` hold business-critical logic | Stepwise service extraction with strong regression coverage | Direct broad movement would be high-diff and high-regression | High | Plan extraction in phases; keep using small additive slices like the current `submissions.py` pass |

---

## 3. Current Backend Structure Target

```text
backend/
  routers/
  services/
  repositories/
  policies/
  validators/
  config/
```

### Alignment notes
- `routers/` already exists and remains the HTTP entry layer.
- `services/` already exists and remains the business workflow layer.
- `repositories/` was added in this pass as scaffolding.
- `policies/` was added in this pass as scaffolding.
- `validators/` is a target folder, but request validation should remain backward-compatible with `schemas.py` until domain splits are justified.
- `config/` already acts as the centralized runtime/policy constants layer.

---

## 4. Current Router Fatness Ranking

### Top 10 routers to thin

| Rank | Router | Lines | Endpoints | Primary issue |
|---|---|---:|---:|---|
| 1 | `backend/routers/optimize_workflow.py` | 1331 | 26 | Workflow state, optimizer orchestration, locks, signatures, and exports mixed together |
| 2 | `backend/routers/schedule.py` | 1088 | 9 | Heavy scheduling, validation, optimizer setup, room and copy-count logic |
| 3 | `backend/routers/documents.py` | 1020 | 9 | Document assembly, schedule lookup, student data joins, and file generation |
| 4 | `backend/routers/exam_manager.py` | 907 | 11 | Ownership workflow, import review, policy logic, and materials updates |
| 5 | `backend/routers/submissions.py` | 872 | 16 | First extraction slice landed; upload/approval/release/print mutations are still mixed in the router |
| 6 | `backend/routers/imports.py` | 865 | 6 | Import parsing, preview, commit logic, and row transformation |
| 7 | `backend/routers/exports_excel.py` | 734 | 6 | Export data assembly with repeated joined queries |
| 8 | `backend/routers/swaps_v2.py` | 672 | 9 | Swap workflow state mixed with response shaping |
| 9 | `backend/routers/external_exams.py` | 638 | 11 | External exam CRUD plus allocation workflow |
| 10 | `backend/routers/exports.py` | 617 | 6 | Multiple export shapes and business filtering in one router |

### Routers already close to the target shape
- `backend/routers/auth.py`
- `backend/routers/health.py`
- `backend/routers/pdf.py`

These are not perfect, but they are closer to “route -> guard -> service/helper -> response” than the larger routers.

---

## 5. Suggested Service / Repository / Policy Split

| Router | Service split | Repository split | Policy split | Validator split |
|---|---|---|---|---|
| `optimize_workflow.py` | `workflow_service.py`, `workflow_lock_service.py`, `signature_service.py` | `schedule_repository.py`, `room_repository.py`, `audit_repository.py` | `schedule_policy.py`, `export_policy.py` | `schedule_validators.py` |
| `schedule.py` | `schedule_service.py`, `optimizer_service.py` | `schedule_repository.py`, `room_repository.py` | `schedule_policy.py` | `schedule_validators.py` |
| `documents.py` | `document_service.py`, `document_export_service.py` | `student_repository.py`, `schedule_repository.py`, `submission_repository.py` | `pdpa_policy.py`, `export_policy.py` | `document_validators.py` |
| `exam_manager.py` | `exam_manager_service.py`, `ownership_service.py` | `user_repository.py`, `schedule_repository.py`, `submission_repository.py` | `auth_policy.py`, `schedule_policy.py` | `exam_manager_validators.py` |
| `submissions.py` | continue expanding `submission_service.py`, add `print_queue_service.py` | `submission_repository.py`, `user_repository.py` | `submission_policy.py`, `auth_policy.py`, `pdpa_policy.py` | `submission_validators.py` |
| `imports.py` | `import_service.py`, `import_commit_service.py` | `student_repository.py`, `schedule_repository.py`, `room_repository.py` | `pdpa_policy.py` | `import_validators.py` |
| `exports_excel.py` | `export_service.py` | `schedule_repository.py`, `audit_repository.py` | `export_policy.py`, `pdpa_policy.py` | `export_validators.py` |
| `swaps_v2.py` | `swap_service.py` | `schedule_repository.py`, `user_repository.py` | `schedule_policy.py` | `swap_validators.py` |
| `exports.py` | `export_service.py` | `schedule_repository.py`, `submission_repository.py` | `export_policy.py`, `pdpa_policy.py` | `export_validators.py` |
| `external_exams.py` | `external_exam_service.py` | `user_repository.py`, `schedule_repository.py` | `schedule_policy.py` | `external_exam_validators.py` |

---

## 6. Thin Router / Fat Service Translation

### Safe interpretation for EMS

The handwritten Laravel note uses “Fat Model / Thin Controller.” For EMS, the safest translation is:

- Thin router
  - parse request
  - apply dependency guard
  - call service
  - return response
- Rich service
  - orchestrate workflow
  - enforce domain rules
  - coordinate repositories
  - call audit service
  - own transactions
- Focused repository
  - encapsulate query composition
  - load aggregates and related ORM data
  - support service orchestration
- Lightweight model
  - persist state
  - allow small computed properties
  - avoid heavy workflow logic

### Why not literal “fat model”

Python + SQLAlchemy can support domain-rich models, but EMS already stores most workflow logic in routers. Moving all that logic straight into ORM models now would create a harder-to-test and harder-to-migrate codebase. Service-first extraction is the safer translation of the Laravel intent.

---

## 7. Before / After Example

### Before

```python
@router.post("/approve")
def approve_submission(...):
    submission = db.query(models.ExamSubmission).filter(...).first()
    if current_user.role != models.UserRole.admin:
        raise HTTPException(403, "admin required")
    submission.status = models.SubmissionStatus.approved
    db.commit()
    log_action(db, current_user, "SUBMISSION_APPROVED", ...)
    return {"success": True}
```

### Target

```python
@router.post("/approve")
def approve_submission(...):
    result = submission_service.approve_submission(
        db=db,
        actor=current_user,
        submission_id=payload.submission_id,
    )
    return schemas.SubmissionActionResult.model_validate(result)
```

```python
def approve_submission(db: Session, actor: models.User, submission_id: int):
    submission = submission_repository.get_for_approval(db, submission_id)
    auth_policy.require_submission_approval(actor, submission)
    submission_repository.mark_approved(db, submission, actor.id)
    audit_service.audit_mutation(...)
    return submission
```

This is the architectural direction. It is not the implementation scope of this pass.

---

## 8. Auth Flow Target

### Current EMS flow
1. React calls `/api/auth/login`
2. `backend/routers/auth.py` verifies username/password
3. `auth_utils.create_token()` issues JWT
4. `security.set_auth_cookie()` writes HttpOnly cookie
5. `permissions.py` / `auth_utils.py` guards protect routes

### Laravel-style compatible EMS flow
1. User opens EMS
2. EMS redirects or receives Faculty IT callback
3. Faculty IT sends `callback/authen` payload or `cmu_at` proof
4. `services/auth_integration_service.py` normalizes external identity
5. Repository resolves local `User`
6. EMS issues its own JWT + HttpOnly cookie
7. Existing permission guards continue to control access
8. React auth store continues to use `/auth/me` and cookie-backed session state

### This pass
- added `backend/services/auth_integration_service.py`
- kept current username/password login unchanged
- did not change token/session format

---

## 9. Migration Order

### Phase A - now complete in this pass
- Add repository scaffolding
- Add PDPA policy scaffolding
- Add auth integration service scaffolding
- Document the Laravel-style target

### Phase B - low-risk backend extraction
- Expand `submission_service.py` for list/detail access, file access, and message helpers
- Introduce `submission_repository.py` and wire the first router call sites to it
- Route new submission mutations through `audit_service`
- Add submission policy helpers and keep validator extraction incremental
- Next backend router recommendation after this slice: `backend/routers/schedule.py`

### Phase C - schedule and workflow extraction
- Add `schedule_service.py`
- Add `schedule_repository.py` and `room_repository.py`
- Move query-heavy list and update logic from `schedule.py`
- Extract lock/signature orchestration from `optimize_workflow.py`

### Phase D - policy consolidation
- Create `auth_policy.py`, `schedule_policy.py`, `export_policy.py`
- Move router-local authorization branches into policy helpers
- Reduce direct role-string branching in routers and pages

### Phase E - frontend controller discipline
- Move page orchestration into hooks for `Checkins.tsx`, `Optimizer.tsx`, `MyExam.tsx`
- Standardize page -> hook -> service -> component flow
- Continue permission and i18n cleanup

---

## 10. Safe First Slice Implemented

- Added `backend/repositories/__init__.py`
- Added `backend/repositories/user_repository.py`
- Added `backend/repositories/student_repository.py`
- Added `backend/policies/__init__.py`
- Added `backend/policies/pdpa_policy.py`
- Added `backend/services/auth_integration_service.py`
- Added pure-function tests for the new repository helpers, PDPA policy, and auth integration service

These files are additive scaffolding only. No current router behavior or auth behavior was broken to make room for them.
