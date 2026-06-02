# EMS Wrong-Scope Teaching Workload Audit

**Date**: 2026-06-02  
**Purpose**: Classify teaching-workload and generic payment/workload language so EMS remains exam scheduling plus invigilation payment only.

## Search Basis

Primary wrong-scope search:

```powershell
rg "ค่าสอน|สอนเกิน|ภาระงานสอน|teaching workload|excess teaching|Course_Eligibility|base workload|co-teaching|thesis|advisor|Payment_Report_PENDING" docs backend frontend -S
```

Payment/workload search:

```powershell
rg "payment|pay|compensation|workload|duty|invigil|คุมสอบ|ค่าคุมสอบ|ภาระ|สอน" backend frontend docs -S
```

## Action Labels

- `KEEP_AS_HISTORICAL`: preserve with context.
- `RENAME_CONTEXT_ONLY`: rename in docs or labels later, without changing behavior.
- `MOVE_TO_ARCHIVE_LATER`: candidate for later archive after human review.
- `UPDATE_TERMINOLOGY`: clarify wording now or in a narrow docs pass.
- `DO_NOT_USE_FOR_EMS_PAYMENT`: not a source for invigilation payment.
- `NEEDS_HUMAN_REVIEW`: business owner must confirm before use.

## Matched File Classification

| File path | Matched terms | Issue type | EMS-valid? | Wrong-scope? | Mixed? | Action |
|---|---|---|---:|---:|---:|---|
| `frontend/src/docs/import-data-v2-spec.md` | thesis, advisor | Import compatibility for thesis/advisor placeholders | Yes | No | No | KEEP_AS_HISTORICAL |
| `backend/models.py` | `is_thesis`, `Supervision.compensation`, `ExternalSupervision.compensation` | Import flag plus EMS payment fields | Yes | No | Yes | UPDATE_TERMINOLOGY, NEEDS_HUMAN_REVIEW |
| `backend/migrate_v2_import.py` | `is_thesis` | Import migration | Yes | No | No | KEEP_AS_HISTORICAL |
| `backend/services/recommendation_service.py` | advisory | False positive | Yes | No | No | KEEP_AS_HISTORICAL |
| `backend/services/pdpa_runtime_guard_service.py` | advisor_notes | PDPA sensitive-data term | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/AI_RECOMMENDATION_LAYER.md` | advisory | False positive | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/DEMO_100_POLISH_VALIDATION_LOG.md` | advisory | Build warning wording | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/operations/DEMO_GO_NO_GO_REPORT.md` | advisory | Build warning wording | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/FINAL_PDPA_SECURITY_SWEEP.md` | advisor_notes | PDPA sensitive-data term | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/I18N_AUDIT_REPORT.md` | advisory | Tooling wording | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/OPTIMIZATION_EXPLAINABILITY_MODEL.md` | advisory | Governance wording | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/SYSTEM_100_PERCENT_READINESS_SOURCE_REVIEW.md` | synthesis | False positive from search term fragment | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/SYSTEM_REPOSITORY_HEALTH_AUDIT.md` | synthesis | False positive from search term fragment | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/SYSTEM_VALIDATION_BASELINE_REPORT.md` | advisory | Build warning wording | Yes | No | No | KEEP_AS_HISTORICAL |
| `docs/architecture/WORKLOAD_DUTY_ANALYTICS.md` | workload, duty, invigilation | EMS exam duty analytics | Yes | No | No | UPDATE_TERMINOLOGY only if future ambiguity appears |
| `backend/services/workload_duty_analytics_service.py` | workload duty analytics | EMS exam duty analytics | Yes | No | No | KEEP_AS_HISTORICAL |
| `backend/repositories/workload_duty_analytics_repository.py` | normalized duty records | EMS exam duty records | Yes | No | No | KEEP_AS_HISTORICAL |
| `backend/staff_workloads.py` | workload, invigilation, paper distribution, external exam | EMS duty workload | Yes | No | Yes | UPDATE_TERMINOLOGY in docs, NEEDS_HUMAN_REVIEW for payment use |
| `backend/routers/exports_excel.py` | compensation export | Existing EMS payment export | Yes | No | Yes | DO_NOT_USE_FOR_EMS_PAYMENT until rules confirmed |
| `backend/repositories/export_repository.py` | compensation rates | Existing EMS payment calculation surface | Yes | No | Yes | DO_NOT_USE_FOR_EMS_PAYMENT until rules confirmed |
| `backend/services/export_excel_service.py` | compensation workbook | Existing EMS payment report surface | Yes | No | Yes | DO_NOT_USE_FOR_EMS_PAYMENT until rules confirmed |
| `docs/architecture/CROSS_SYSTEM_INTEGRATION_CONTRACTS.md` | Finance / Workload Compensation System | Generic finance wording | Partly | No | Yes | UPDATE_TERMINOLOGY, NEEDS_HUMAN_REVIEW |
| `docs/PDPA_SECURITY_GUIDE.md` | staff compensation | Generic compensation wording | Partly | No | Yes | UPDATE_TERMINOLOGY |
| `docs/PILOT_DEPLOYMENT_READINESS_CHECKLIST.md` | Compensation Excel | Existing export checklist | Yes | No | Yes | UPDATE_TERMINOLOGY later |
| `docs/PRODUCTION_READINESS_CHECKLIST.md` | Compensation Excel | Existing export checklist | Yes | No | Yes | UPDATE_TERMINOLOGY later |

## Findings

- No direct teaching compensation workflow files were found by the exact forbidden terms.
- No `Course_Eligibility_Classification` or `Payment_Report_PENDING` source-of-truth files were found in EMS.
- The repository has valid exam-operation workload features that must not be confused with teaching workload.
- Existing compensation fields and exports should be treated as historical or provisional invigilation-payment surfaces until finance rules are confirmed.

## Required Action

Do not delete, move, or rewrite files in this pass. Preserve historical material, add scope clarification, and require human review before using any generic compensation surface as final invigilation payment logic.

