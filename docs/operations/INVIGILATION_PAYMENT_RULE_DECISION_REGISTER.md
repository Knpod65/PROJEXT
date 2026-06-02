# Invigilation Payment Rule Decision Register

**Date**: 2026-06-02  
**Status**: All decisions are OPEN until finance/admin/academic office answers them.  
**Scope**: Invigilation payment only. Teaching workload compensation is excluded.

| decision_id | topic | decision_needed | options | recommended_default | owner | status | answer | evidence_source | affects_calculation | affects_approval | notes |
|---|---|---|---|---|---|---|---|---|---:|---:|---|
| PAY-001 | Payment unit | Choose the unit used for payment preview and later calculation | per session; per hour; per day; per exam block; hybrid | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | Yes | Do not infer from existing compensation fields |
| PAY-002 | Base rate | Confirm whether a base rate exists and where it is stored | one base rate; table by period; table by person type; no base rate | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | No | Current 200/300 values are provisional only |
| PAY-003 | Role-based rate | Confirm whether role changes rate | same all roles; chief/assistant; staff runner; paper handling | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | No | Must map to duty role |
| PAY-004 | Check-in requirement | Decide whether check-in is required for payment | assignment only; check-in required; QR required; signature required; supervisor approval | No default until owner confirms | Admin/Academic Office | OPEN | Pending | Pending | Yes | Yes | Evidence rule drives exceptions |
| PAY-005 | No-show rule | Define payment effect of no-show | no payment; reduced payment; manual review; other | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | Yes | Current data lacks explicit invigilator no-show flag |
| PAY-006 | Substitution rule | Decide whether payment transfers to replacement | transfer to substitute; split; original remains; manual review | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | Yes | Use swap/emergency records as candidate evidence |
| PAY-007 | Cancelled exam rule | Define payment effect for cancelled exams | no payment; pay if present; pay partial; manual review | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | Yes | Current schedule has status but no dedicated cancellation rule |
| PAY-008 | Late arrival rule | Define late-arrival effect | no effect; reduced payment; manual review; no payment | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | Yes | Current late count is for students, not invigilators |
| PAY-009 | Approval owner | Identify who approves payment batch | finance; exam office; academic office; department head; multiple | No default until owner confirms | Faculty leadership | OPEN | Pending | Pending | No | Yes | Blocks approval workflow |
| PAY-010 | Payment period | Define batch period | per day; per exam period; per semester; fiscal month; custom cutoff | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | Yes | Existing `ExamPeriod` may not equal payment batch |
| PAY-011 | Export format | Define official output | Excel; PDF; finance import file; all | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | No | Yes | Existing compensation export is not final report |
| PAY-012 | Print shop inclusion/exclusion | Decide whether print/paper handling is payable | excluded; included; separate rate; separate report | No default until owner confirms | Finance/Admin/Print Ops | OPEN | Pending | Pending | Yes | Yes | Important for QR/paper pickup evidence |
| PAY-013 | External user payment handling | Decide external exam/external person treatment | same batch; separate batch; excluded; manual review | No default until owner confirms | Finance/Admin | OPEN | Pending | Pending | Yes | Yes | External supervision has compensation field |
| PAY-014 | Audit evidence requirement | Decide audit records required before approval/export | assignment audit; check-in audit; QR audit; supervisor signoff; all | No default until owner confirms | DPO/Admin/Finance | OPEN | Pending | Pending | No | Yes | Required before payment readiness |

