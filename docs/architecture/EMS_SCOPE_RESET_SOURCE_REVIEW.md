# EMS Scope Reset Source Review

**Date**: 2026-06-02  
**Pass**: EMS Scope Reset + Invigilation Payment Realignment  
**Root reviewed**: `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`

## Preflight Confirmation

- `git rev-parse --show-toplevel`: `C:/Users/DELL/Desktop/PROJEXT/opt/ems_system`
- Current branch: `main`
- `git pull origin main`: already up to date
- Working tree before edits: clean
- `wip/ems-orphan-services-transfer` exists as a separate branch only; it was not checked out or merged in this pass.
- No production deployment was attempted.
- No Laravel/POLSCI auth bridge was implemented.
- No visual redesign was attempted.
- No `git add .` is allowed for this pass.

## Source Documents Read

All requested source documents were present:

- `docs/architecture/EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md`
- `docs/architecture/EMS_100_PERCENT_MASTER_SCORECARD.md`
- `docs/architecture/FRONTEND_100_PERCENT_READINESS_SCORE.md`
- `docs/architecture/BACKEND_100_PERCENT_READINESS_SCORE.md`
- `docs/architecture/UX_USABILITY_100_PERCENT_READINESS_SCORE.md`
- `docs/architecture/TESTING_QA_100_PERCENT_READINESS_SCORE.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`
- `docs/operations/DEMO_GO_NO_GO_REPORT.md`
- `docs/operations/DEMO_ROUTE_SMOKE_MAP.md`
- `docs/operations/DEMO_USER_JOURNEY_SCRIPT.md`
- `docs/deployment/FACULTY_WEB_PORTAL_DEPLOYMENT_ARCHITECTURE.md`
- `docs/deployment/FACULTY_WEB_ROUTE_AND_API_MAPPING.md`

Additional relevant files surfaced by search:

- `docs/architecture/WORKLOAD_DUTY_ANALYTICS.md`
- `docs/architecture/CROSS_SYSTEM_INTEGRATION_CONTRACTS.md`
- `docs/architecture/D4_ANALYTICS_INTEGRATION_AUDIT.md`
- `docs/PDPA_SECURITY_GUIDE.md`
- `docs/PILOT_DEPLOYMENT_READINESS_CHECKLIST.md`
- `docs/PRODUCTION_READINESS_CHECKLIST.md`
- `backend/models.py`
- `backend/services/export_excel_service.py`
- `backend/repositories/export_repository.py`
- `backend/routers/exports_excel.py`
- `backend/staff_workloads.py`
- `backend/repositories/workload_duty_analytics_repository.py`
- `backend/services/workload_duty_analytics_service.py`
- `frontend/src/pages/WorkloadDutyAnalytics.tsx`
- `frontend/src/hooks/domain/useExportCenterPage.ts`
- `frontend/src/i18n/th.ts`

## Wrong-Scope Search Results

Search command:

```powershell
rg "ค่าสอน|สอนเกิน|ภาระงานสอน|teaching workload|excess teaching|Course_Eligibility|base workload|co-teaching|thesis|advisor|Payment_Report_PENDING" docs backend frontend -S
```

Confirmed findings:

- No matches were found for the exact teaching compensation markers `ค่าสอน`, `สอนเกิน`, `ภาระงานสอน`, `teaching workload`, `excess teaching`, `Course_Eligibility`, `base workload`, `co-teaching`, or `Payment_Report_PENDING`.
- Matches for `thesis` and `advisor` exist in import specifications and schema fields. These are course-import compatibility terms, not EMS payment logic.
- Matches for `advisory` were false positives from documentation describing recommendation/advisory layers.

## Payment And Workload Search Results

Search command:

```powershell
rg "payment|pay|compensation|workload|duty|invigil|คุมสอบ|ค่าคุมสอบ|ภาระ|สอน" backend frontend docs -S
```

Key findings:

- `WorkloadDutyAnalytics` and routes `/workload-duty-analytics`, `/duty-workload`, and `/my-workload` are EMS-valid if interpreted only as exam duty workload.
- `backend.models.Supervision.compensation`, `ExternalSupervision.compensation`, and `/exports-excel/compensation` are existing EMS payment-related surfaces. They must be treated as invigilation or exam-supervision payment candidates, not final finance rules.
- `staff_workloads.py`, workload exports, and historical workload reports combine invigilation, paper distribution, and external exam duty counts. This is EMS-valid exam-operation workload.
- `CROSS_SYSTEM_INTEGRATION_CONTRACTS.md` uses "Finance / Workload Compensation System" and "Monthly workload compensation summary". This is mixed terminology because it does not explicitly say invigilation payment.
- `PDPA_SECURITY_GUIDE.md` says workload data forms the basis for staff compensation. This is mixed terminology unless clarified as invigilation or exam-operation duty payment only.

## File Classification Summary

| File or area | Terms | Classification | Risk if unchanged |
|---|---|---:|---|
| `docs/architecture/WORKLOAD_DUTY_ANALYTICS.md` | workload, duty, invigilation, paper distribution | EMS-valid | Low. Valid if future readers keep workload tied to exam duty only. |
| `frontend/src/pages/WorkloadDutyAnalytics.tsx` and related hooks/types/i18n | workload, invigilation, paper distribution | EMS-valid | Low. UI wording is mostly exam duty oriented. |
| `backend/services/workload_duty_analytics_service.py` and repository | workload, duty records | EMS-valid | Low. Aggregates exam duty records, not teaching workload. |
| `backend/staff_workloads.py` | workload, invigilation, paper distribution, external exam | EMS-valid | Medium. Needs documentation that counts are exam duty units, not teaching workload units. |
| `backend/models.py` supervision compensation fields | compensation | Mixed but EMS-relevant | Medium. Could be mistaken as teaching compensation unless payment boundary is documented. |
| `backend/routers/exports_excel.py` compensation export | compensation | Mixed but EMS-relevant | Medium. Existing export must not become final payment authority until rules are confirmed. |
| `backend/repositories/export_repository.py` compensation rates | compensation_rate_internal, compensation_rate_external | Mixed but EMS-relevant | Medium. Default rates exist; finance rules still need confirmation. |
| `docs/architecture/CROSS_SYSTEM_INTEGRATION_CONTRACTS.md` | Finance / Workload Compensation System | Mixed | High. Generic wording could invite teaching compensation integration. |
| `docs/PDPA_SECURITY_GUIDE.md` | staff compensation | Mixed | Medium. Needs invigilation-payment clarification. |
| import V2 spec and `sections.is_thesis` fields | thesis, advisor | EMS-valid import context | Low. Not payment scope. |

## Source Review Conclusion

The repository does not appear to contain the previous wrong-scope teaching workload workbook workflow by exact name. The actual risk is terminology drift: EMS already has valid exam-duty workload and compensation/payment surfaces, but some docs and names use generic "workload compensation" language. From this pass forward, those surfaces must be interpreted and documented only as invigilation or exam-operation duty payment, never as teaching workload compensation.

