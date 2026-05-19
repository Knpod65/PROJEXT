# Laravel-style Final Alignment Audit

This document summarizes the Phase L1 readiness audit for aligning the EMS platform to a Laravel-style architecture (controller/router, services, repositories, policies, validators, serializers) while keeping the FastAPI + React stack.

## Progress Summary

### L2.3 Import/Export Boundary Extraction — COMPLETED

| Slice | Status | Router Line Reduction |
|-------|--------|----------------------|
| L2.3-s1: Import domain boundary | ✅ Done | imports.py thinned |
| L2.3-s2: Export domain boundary | ✅ Done | exports.py thinned |
| L2.3-s3: Excel export specialization | ✅ Done | exports_excel.py: 711 → ~260 lines |

New Laravel-style layers created:
- `services/import_service.py`, `services/export_service.py`, `services/export_excel_service.py`
- `repositories/import_repository.py`, `repositories/export_repository.py`
- `policies/import_policy.py`, `policies/export_policy.py`
- `validators/import_validator.py`, `validators/export_validator.py`, `validators/export_excel_validator.py`
- `serializers/import_serializer.py`, `serializers/export_serializer.py`

### L2.4 Governance Docs — IN PROGRESS

| Doc | Status |
|-----|--------|
| LARAVEL_STYLE_FINAL_ALIGNMENT_AUDIT.md | Updated |
| IMPORT_EXPORT_GOVERNANCE.md | Updated |
| FINAL_PLATFORM_READINESS_REPORT.md | Pending |
| EMS_COMPLETION_GAP_REPORT.md | Pending |
| RENOVATION_PHASE_TRACKER.md | Pending |

---

Summary
- Location: `opt/ems_system`
- Backend: mixed maturity; several "fat" routers with business logic
- Frontend: modern React/Vite app with i18n files present, but lacking parity checks
- Tests: ~1264 pytest files, strong service unit coverage

Top fat routers (candidates for thinning)
- `documents.py` — PDF generation, envelope assembly, QR lifecycle (VERY FAT)
- `schedule.py` — complex schedule queries and state transitions (FAT)
- `submissions.py` — versioning, print queue (FAT)
- `exam_manager.py` (FAT)
- `optimize_workflow.py` (MEDIUM)

### Completed Extractions
- `exports.py` — thinned, uses ExportService
- `exports_excel.py` — thinned, uses ExportExcelService
- `imports.py` — thinned, uses ImportService

Missing / Partial layers
- `backend/validators/` — ✅ partial (export/import validators added)
- `backend/serializers/` — ✅ partial (export/import serializers added)
- `backend/repositories/` — ✅ partial; export/import repositories added
- `backend/policies/` — ✅ partial; export/import policies added

Key findings
- Numerous inline role checks (`user.role`, `is_admin`, `effective_role`) should be moved to `policies/*` predicates.
- Configuration and label-like constants (Thai day names, export strings, thresholds) are scattered and should be centralized under `backend/config/` or frontend i18n where appropriate.
- Frontend i18n exists (`src/i18n/en.ts` and `src/i18n/th.ts`) but there is no parity check script.

Recommendations (Phase L1 priorities)
1. ✅ Add `backend/serializers/` and `backend/validators/` and migrate Pydantic schemas and response transformers into those folders.
2. ✅ Thin the top 8 fat routers by extracting services and policies: documents, schedule, submissions, exports, exports_excel, exam_manager, optimize_workflow, checkins.
3. Centralize RBAC predicates into `backend/policies/` and replace inline checks with named functions (e.g., `can_publish_schedule(user, schedule)`).
4. Add a frontend i18n parity checker and `npm run check:i18n` script.
5. Keep all changes non-breaking: no endpoint path changes, no response shape changes, no auth/session/token behavior changes.

Quick wins
- Add a serializer example for `user` and a validator example for schedule filter requests.
- Add `frontend/scripts/check-i18n.js` to detect missing translation keys.

Next steps
- L2.4: analytics/governance router thinning
- L3: Introduce serializer layer and migrate inline transformations.
- L4: Introduce FormRequest-style validators (Pydantic per-request classes).
- L5: Consolidate policies and replace inline role logic.
