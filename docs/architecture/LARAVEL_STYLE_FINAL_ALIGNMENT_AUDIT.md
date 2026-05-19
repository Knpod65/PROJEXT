# Laravel-style Final Alignment Audit

This document summarizes the Phase L1 readiness audit for aligning the EMS platform to a Laravel-style architecture (controller/router, services, repositories, policies, validators, serializers) while keeping the FastAPI + React stack.

Summary
- Location: `opt/ems_system`
- Backend: mixed maturity; several "fat" routers with business logic
- Frontend: modern React/Vite app with i18n files present, but lacking parity checks
- Tests: ~74 pytest files, strong service unit coverage; a few integration tests

Top fat routers (candidates for thinning)
- `documents.py` — PDF generation, envelope assembly, QR lifecycle (VERY FAT)
- `schedule.py` — complex schedule queries and state transitions (FAT)
- `submissions.py` — versioning, print queue (FAT)
- `exports.py` / `exports_excel.py` — export logic mixed with query and formatting (FAT)
- `exam_manager.py` (FAT)
- `optimize_workflow.py` (MEDIUM)

Missing / Partial layers
- `backend/validators/` — missing (Pydantic schemas currently co-located)
- `backend/serializers/` — missing (inline dict transformations used instead)
- `backend/repositories/` — partial; many routers still query ORM directly
- `backend/policies/` — partial; ~50+ inline role checks remain across routers

Key findings
- Numerous inline role checks (`user.role`, `is_admin`, `effective_role`) should be moved to `policies/*` predicates.
- Configuration and label-like constants (Thai day names, export strings, thresholds) are scattered and should be centralized under `backend/config/` or frontend i18n where appropriate.
- Frontend i18n exists (`src/i18n/en.ts` and `src/i18n/th.ts`) but there is no parity check script.

Recommendations (Phase L1 priorities)
1. Add `backend/serializers/` and `backend/validators/` and migrate Pydantic schemas and response transformers into those folders.
2. Thin the top 8 fat routers by extracting services and policies: documents, schedule, submissions, exports, exports_excel, exam_manager, optimize_workflow, checkins.
3. Centralize RBAC predicates into `backend/policies/` and replace inline checks with named functions (e.g., `can_publish_schedule(user, schedule)`).
4. Add a frontend i18n parity checker and `npm run check:i18n` script.
5. Keep all changes non-breaking: no endpoint path changes, no response shape changes, no auth/session/token behavior changes.

Quick wins
- Add a serializer example for `user` and a validator example for schedule filter requests.
- Add `frontend/scripts/check-i18n.js` to detect missing translation keys.

Next steps
- L2: Backend router thinning pass — implement service extraction for the top routers.
- L3: Introduce serializer layer and migrate inline transformations.
- L4: Introduce FormRequest-style validators (Pydantic per-request classes).
- L5: Consolidate policies and replace inline role logic.

Audit completed and initial scaffolding added to repository.
