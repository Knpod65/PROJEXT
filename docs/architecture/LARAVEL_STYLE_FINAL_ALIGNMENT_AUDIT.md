# Laravel-style Final Alignment Audit

This document summarizes the Phase L1 readiness audit for aligning the EMS platform to a Laravel-style architecture (controller/router, services, repositories, policies, validators, serializers) while keeping the FastAPI + React stack.

## Progress Summary

### L2.3 Import/Export Boundary Extraction — COMPLETED

| Slice | Status | Router Line Reduction |
|-------|--------|----------------------|
| L2.3-s1: Import domain boundary | ✅ Done | imports.py thinned |
| L2.3-s2: Export domain boundary | ✅ Done | exports.py thinned |
| L2.3-s3: Excel export specialization | ✅ Done | exports_excel.py: 711 → ~260 lines |

### L2.4 Analytics/Governance Router Thinning — COMPLETED

| Slice | Status | Router Line Reduction |
|-------|--------|----------------------|
| L2.4-s1: Analytics router boundary | ✅ Done | analytics.py: 223 → ~90 lines |
| L2.4-s2: Dashboard router boundary | ✅ Done | dashboard.py: 154 → ~50 lines |
| L2.4-s3: Governance endpoint boundary | ✅ Done | optimize_workflow.py: 1507 → ~1330 lines |

New Laravel-style layers created in L2.4:
- `services/analytics_service.py`, `services/dashboard_service.py`, `services/governance_endpoint_service.py`
- `policies/analytics_policy.py`, `policies/dashboard_policy.py`, `policies/governance_policy.py`
- `validators/analytics_validator.py`, `validators/dashboard_validator.py`, `validators/governance_validator.py`
- `serializers/analytics_serializer.py`, `serializers/dashboard_serializer.py`, `serializers/governance_serializer.py`

---

Summary
- Location: `opt/ems_system`
- Backend: fat routers thinned to Laravel-style thin controllers
- Frontend: modern React/Vite app with i18n files present, but lacking parity checks
- Tests: 1264 passing

Completed Extractions
- `exports.py` — thinned, uses ExportService
- `exports_excel.py` — thinned, uses ExportExcelService
- `imports.py` — thinned, uses ImportService
- `analytics.py` — thinned, uses AnalyticsService
- `dashboard.py` — thinned, uses DashboardService
- `optimize_workflow.py` — governance endpoints extracted to GovernanceEndpointService

Remaining Fat Routers
- `documents.py` — PDF generation, envelope assembly, QR lifecycle (VERY FAT)
- `submissions.py` — versioning, print queue (FAT)
- `exam_manager.py` (FAT)
- `schedule.py` — L2.2 extraction done, but still has remaining inline helpers

Missing / Partial layers
- `backend/validators/` — ✅ partial (export/import/analytics/dashboard/governance validators added)
- `backend/serializers/` — ✅ partial (export/import/analytics/dashboard/governance serializers added)
- `backend/repositories/` — ✅ partial; export/import repositories added
- `backend/policies/` — ✅ partial; export/import/analytics/dashboard/governance policies added

Key findings
- Numerous inline role checks (`user.role`, `is_admin`, `effective_role`) should be moved to `policies/*` predicates.
- Configuration and label-like constants (Thai day names, export strings, thresholds) are scattered and should be centralized under `backend/config/` or frontend i18n where appropriate.
- Frontend i18n exists (`src/i18n/en.ts` and `src/i18n/th.ts`) but there is no parity check script.

Recommendations (Phase L1 priorities)
1. ✅ Add `backend/serializers/` and `backend/validators/` and migrate Pydantic schemas and response transformers into those folders.
2. ✅ Thin the top 8 fat routers by extracting services and policies: documents, schedule, submissions, exports, exports_excel, exam_manager, optimize_workflow, checkins.
3. Centralize RBAC predicates into `backend/policies/` and replace inline checks with named functions.
4. Add a frontend i18n parity checker and `npm run check:i18n` script.
5. Keep all changes non-breaking: no endpoint path changes, no response shape changes, no auth/session/token behavior changes.

Quick wins
- Add a serializer example for `user` and a validator example for schedule filter requests.
- Add `frontend/scripts/check-i18n.js` to detect missing translation keys.

Next steps
- L3: Introduce serializer layer and migrate inline transformations.
- L4: Introduce FormRequest-style validators (Pydantic per-request classes).
- L5: Consolidate policies and replace inline role logic.
- I1: Full i18n audit and raw string cleanup