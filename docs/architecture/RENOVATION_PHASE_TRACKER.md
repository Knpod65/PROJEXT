# EMS Renovation Phase Tracker

## Overview

Tracks progress on the EMS platform renovation from fat routers to Laravel-style architecture.

---

## Phase L2 — Router Thinning

### L2.1 Query/List/Group Boundary Extraction
- **Status**: ✅ COMPLETED
- **Files**: schedule.py, submissions.py query methods extracted
- **Service**: schedule_query_service.py created

### L2.2 CRUD + Supervision Boundary Extraction
- **Status**: ✅ COMPLETED
- **Files**: schedule.py CRUD methods extracted
- **Service**: schedule_service.py, supervision_service.py

### L2.3 Import/Export Boundary Extraction
- **Status**: ✅ COMPLETED
- **Files**: imports.py, exports.py, exports_excel.py thinned
- **Services**: import_service.py, export_service.py, export_excel_service.py
- **Repositories**: import_repository.py, export_repository.py
- **Policies**: import_policy.py, export_policy.py
- **Validators**: import_validator.py, export_validator.py, export_excel_validator.py
- **Serializers**: import_serializer.py, export_serializer.py

### L2.4 Analytics/Governance Router Thinning
- **Status**: ⏳ IN PROGRESS
- **Target Files**: analytics.py, governance.py, audit_logs.py
- **Next Steps**: Extract analytics_service.py, governance_service.py

---

## Phase L3 — Serializer/Resource Layer

### L3.1 Response Transformer Layer
- **Status**: ⏳ PENDING
- **Target**: Extract inline dict transformations

### L3.2 Full i18n Audit
- **Status**: ⏳ PENDING
- **Target**: Centralize all strings, add parity checker

---

## Phase L4 — FormRequest Validators

### L4.1 Request Validation Classes
- **Status**: ⏳ PENDING
- **Target**: Pydantic per-request classes

---

## Phase L5 — Policy Consolidation

### L5.1 Authorization Pass
- **Status**: ⏳ PENDING
- **Target**: Replace inline role checks with named predicates

---

## Progress Dashboard

| Phase | Target | Status | Progress |
|-------|--------|--------|----------|
| L2.1 | 8 routers | 1/8 | 12.5% |
| L2.2 | 8 routers | 1/8 | 12.5% |
| L2.3 | 3 routers | 3/3 | 100% |
| L2.4 | 3 routers | 0/3 | 0% |
| L3 | Serializers | 0/1 | 0% |
| L4 | Validators | 0/1 | 0% |
| L5 | Policies | 0/1 | 0% |

---

## Quick Links

- [Laravel-style Audit](LARAVEL_STYLE_FINAL_ALIGNMENT_AUDIT.md)
- [Import/Export Governance](IMPORT_EXPORT_GOVERNANCE.md)
- [Final Readiness Report](FINAL_PLATFORM_READINESS_REPORT.md)
- [Completion Gap Report](EMS_COMPLETION_GAP_REPORT.md)