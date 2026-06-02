# EMS Current Payment And Workload Code Audit

**Date**: 2026-06-02  
**Scope**: Code and docs audit only. No code changes in this pass.

## Search Basis

```powershell
rg "payment|pay|compensation|workload|duty|invigil|คุมสอบ|ค่าคุมสอบ|ภาระ|สอน" backend frontend docs -S
```

## Audit Summary

| Feature or area | Current meaning | Exam duty or teaching workload? | Safe for EMS? | Needs rename? | Needs logic correction? | Needs tests? |
|---|---|---|---:|---:|---:|---:|
| WorkloadDutyAnalytics | Role-aware fairness analytics for invigilation and paper distribution | Exam duty | Yes | No, if documented | No | Existing tests should remain; add payment tests later only if reused for payment |
| `/workload-duty-analytics` | Admin duty workload dashboard | Exam duty | Yes | No | No | Existing UI/API tests where available |
| `/duty-workload` | Staff/supervisor duty workload route | Exam duty | Yes | No | No | Existing UI/API tests where available |
| `/my-workload` | Teacher personal exam duty workload route | Exam duty | Yes | No | No | Existing role-scope tests |
| Dashboard workload metrics | Staff workload balance and invigilator balance signals | Exam duty | Yes | No | No | Keep analytics tests |
| `staff_workloads.py` | Period and historical counts for invigilation, paper distribution, external exams | Exam duty | Yes | Maybe later for clarity | No | Yes before payment reuse |
| `supervisions.compensation` | Existing amount field on exam supervision assignment | Invigilation payment candidate | Yes with caution | Maybe later | Unknown until rules confirmed | Yes before finance use |
| `external_supervisions.compensation` | Existing amount field on external exam supervision | Exam-supervision payment candidate | Yes with caution | Maybe later | Unknown until rules confirmed | Yes before finance use |
| `export_compensation` | Existing XLSX compensation export | Invigilation payment candidate | Yes with caution | Maybe later | Unknown until rules confirmed | Yes before final payment use |
| Export center workload summary | Exports duty workload counts | Exam duty | Yes | No | No | Existing export tests plus future payment tests |
| Audit logs for export compensation | Audit event for compensation export | Invigilation payment candidate | Yes with caution | Maybe later | No unless semantics change | Yes if export semantics change |
| Cross-system finance contract | Generic finance/workload compensation outbound contract | Mixed wording | Needs clarification | Yes in docs | Unknown | Yes before integration |
| PDPA compensation retention wording | Staff compensation sensitivity | Mixed wording | Needs clarification | Yes in docs | No | No code tests |

## Special Clarifications

`WorkloadDutyAnalytics` is EMS-valid only if it measures exam duty workload. The valid duty sources are invigilation, paper distribution, external exam duty, and related exam-operation duty records.

It is not valid for teaching workload, excess teaching compensation, base workload hours, course eligibility, co-teaching, thesis/advisor workload, or any teaching payment formula.

## Current Payment Risk

Payment-related fields and exports exist, but the repository does not yet contain a confirmed finance-approved invigilation payment rule model. Therefore:

- Do not present current compensation export as final payroll authority.
- Do not derive payment from teaching workload fields.
- Do not implement new payment logic until rate/evidence/approval rules are confirmed.
- Do not delete or rename existing code without compatibility tests.

## Recommended Next Code Phase

After rules are confirmed:

1. Add tests around current `compensation` export behavior.
2. Decide whether current `compensation` field names remain as compatibility names or receive clearer aliases.
3. Add a payment preview that uses confirmed duty and approved rate rules.
4. Add exception reporting for no-show, late arrival, substitution, and cancellation.
5. Add payment batch approval and audit trail.

