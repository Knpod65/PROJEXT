# Invigilation Payment Current Data Audit

**Date**: 2026-06-02  
**Status**: Data audit for preview scaffold only. Not payment authorization.

## Search Basis

```powershell
rg "invigil|คุมสอบ|duty|workload|payment|pay|attendance|checkin|check-in|substitution|replacement|no-show|room|schedule|exam" backend frontend docs -S
```

## Current Data Surface Matrix

| File/path | Data concept found | Exam scheduling relevant? | Invigilation assignment relevant? | Check-in evidence relevant? | Payment relevant? | Currently implemented? | Missing fields | Risk | Recommendation |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| `backend/models.py` `ExamSchedule` | Exam id, section, room, date, time, exam type, status, supervisions | Yes | Yes | Indirect | Yes | Yes | Payment period, cancellation reason, approval status | Schedule status is not payment status | Use as preview ledger anchor only |
| `backend/models.py` `Room` | Room id/name/building/capacity | Yes | Indirect | Indirect | Indirect | Yes | Room-change history for payment exceptions | Room changes may not be payment-visible | Flag room-change evidence as open |
| `backend/models.py` `Supervision` | Assigned user, role, slot order, compensation, confirmed, swap/emergency flags | Yes | Yes | Partial | Yes | Yes | rate_code, no_show, late_flag, approved_for_payment, evidence status | `confirmed` meaning may be assignment confirmation, not attendance | Treat as assignment record, not final payable record |
| `backend/models.py` `SwapRequest` | requester/target supervision, status, response time, admin override | No | Yes | No | Yes | Yes | payment-transfer rule, final payable owner | Accepted swaps mutate assignment; payment ownership needs policy | Use as substitution evidence candidate |
| `backend/models.py` `CheckinEvent` | schedule/user check-in, type, timestamp, late student count, notes, confirmations | Yes | Partial | Yes | Partial | Yes | invigilator no-show, invigilator late flag, payment evidence type | Late count is student late count, not invigilator late arrival | Use as evidence candidate only after rule confirmation |
| `backend/models.py` `ExamPickupQrToken` | QR token, schedule, room, exam date/time, active/confirmed state | Yes | Partial | Yes for paper pickup | Partial | Yes | payment role mapping, final evidence status | Paper pickup may not equal invigilation attendance | Keep separate from invigilation payment unless included by policy |
| `backend/models.py` `ExamPickupCheckin` | QR scan user, role, scanned time, status, duplicate/window metadata | Yes | Partial | Yes for paper pickup | Partial | Yes | payable role, evidence acceptance rule | Late override/outside window requires finance interpretation | Use for paper-handling evidence only until included |
| `backend/models.py` `PaperDistributionAssignment` | user, date/time, duty type, workload units, assignment mode | Yes | No | No | Possible | Yes | payable flag, rate code, evidence proof, approval status | Workload units are not payment units | Keep as exam duty workload, not payment source yet |
| `backend/models.py` `ExternalExam` / `ExternalSupervision` | external exam details, invigilators needed, assigned users, compensation, confirmed | Yes | Yes | No | Yes | Yes | external payment rule, evidence, period, approval | External exams may follow different finance policy | Track separately in rule decisions |
| `backend/repositories/export_repository.py` | compensation query and default internal/external rates | Yes | Yes | No | Yes | Yes | confirmed rate source, rule version, evidence filtering | Defaults may be placeholders | Mark current export as provisional only |
| `backend/services/export_excel_service.py` | compensation workbook generation | Yes | Yes | No | Yes | Yes | official format, preview labels, approval locks | Could be mistaken as final payment report | Do not reuse as final report without rules/tests |
| `backend/routers/exports_excel.py` | `/compensation` export route with audit log | No | Yes | No | Yes | Yes | preview/final distinction, approval gate | Existing route name is generic | Document as non-authoritative until rule confirmation |
| `backend/repositories/workload_duty_analytics_repository.py` | normalized duty records from supervision, paper distributor, QR, workload records | Yes | Yes | Partial | Possible | Yes | evidence status, rate code, payment eligibility | Analytics aggregates are not payment ledger | Good candidate for preview input design, not final calculation |
| `backend/services/workload_duty_analytics_service.py` | duty counts, fairness, per-person series | No | Yes | No | Indirect | Yes | payment detail ledger fields | Fairness counts are not payable units | Keep for workload only |
| `backend/routers/checkins.py` | room check-ins, confirmations, pickup scans, pickup monitor | Yes | Partial | Yes | Possible | Yes | payment evidence rule, no-show/late ownership | Operational check-in may not prove payable attendance | Use as evidence inventory |
| `backend/routers/swaps.py` and `backend/routers/swaps_v2.py` | swap request/create/respond/cancel, accepted assignment changes | No | Yes | No | Yes | Yes | substitution payment transfer policy | Assignment mutation may obscure original duty owner if not audited | Use baseline/final owner plus swap log in preview design |
| `frontend/src/pages/Checkins.tsx` | room operations and QR pickup UI | Yes | Partial | Yes | No direct | Yes | payment-specific evidence labeling | Users may confuse pickup with payment confirmation | Future payment UI must label evidence source clearly |
| `frontend/src/pages/RoomAttendance.tsx` | room attendance overview and invigilation coverage | Yes | Yes | Yes | No direct | Yes | payment eligibility state | Attendance UX is operational, not payment approval | Keep separate from payment preview |
| `frontend/src/pages/WorkloadDutyAnalytics.tsx` | exam duty workload analytics | No | Yes | No | Indirect | Yes | payable/approved fields | Workload can be misread as payment workload | Keep explicitly exam-duty only |
| `frontend/src/pages/SwapsV2.tsx` | invigilation swap coordination | No | Yes | No | Possible | Yes | payment-transfer visibility | Approved swaps affect final assignee | Payment preview should surface substitution status |
| `frontend/src/hooks/domain/useExportCenterPage.ts` | workload, schedule, paper distribution exports | Yes | Yes | No | Indirect | Yes | payment preview/export integration | Current export center has no preview/final distinction | Add future preview roadmap only |
| `frontend/src/services/external.service.ts` | external exam assignment with compensation parameter | Yes | Yes | No | Yes | Yes | external evidence and payment rule | Parameter can look like final amount | Treat as provisional until policy confirms |
| `frontend/src/config/navigation.ts` | workload, checkins, export center route inventory | No | Yes | Yes | No direct | Yes | payment preview routes | None currently | Future routes must be labeled preview/proposed |

## Data Gaps

- No confirmed `rate_code`.
- No payment-period or payment-batch entity.
- No `approved_for_payment` field.
- No final approval status or export lock status.
- No invigilator-specific no-show flag.
- No invigilator-specific late-arrival flag.
- No finance-approved evidence rule.
- No final distinction between payment preview and payment authorization.

## Recommendation

Build the next phase as a read-only preview model that inventories duty records and exceptions. Do not calculate final payable amounts or produce official reports until finance/admin answers the decision register and data readiness gaps are resolved.

