# Invigilation Payment Data Gap To Rule Map

**Date**: 2026-06-02  
**Status**: PREVIEW GATE REVIEW ONLY - NOT PAYMENT AUTHORIZATION

| Rule Decision | Required Data | Current Availability | Gap | Needed Before Preview | Needed Before Final Payment |
|---|---|---|---|---|---|
| PAY-001 payment unit | exam date/time, session/duration unit | Partial | Unit unknown; duration normalization partial | Unit decision | Approved unit and rounding/minimum rules |
| PAY-002 base rate | rate table, effective date, rate owner | Missing | Current defaults are provisional only | Rate source decision or symbolic preview deferral | Approved rate table/version |
| PAY-003 role-based rate | duty role, person type, role rate | Partial | EMS roles are not finance-approved | Role/rate mapping decision | Approved role/rate table |
| PAY-004 check-in requirement | assignment, check-in/QR/signature/supervisor evidence | Partial | Evidence channel not chosen | Evidence requirement decision | Approved evidence policy and audit link |
| PAY-005 no-show rule | no-show flag/evidence | Missing | No explicit invigilator no-show field | Rule decision plus data capture plan | No-show evidence and payment effect |
| PAY-006 substitution rule | baseline user, final user, swap/emergency record | Partial | Payment transfer rule missing | Substitution decision | Auditable original/final payer rule |
| PAY-007 cancelled exam rule | cancellation status/reason/time | Partial | No dedicated cancellation field/rule | Cancellation decision | Approved cancellation evidence and effect |
| PAY-008 late arrival rule | invigilator late flag/time | Missing | Existing late count is student late count | Late rule plus data capture plan | Late evidence, threshold, payment effect |
| PAY-009 approval owner | verifier/approver/exporter/signatory | Missing | No owner/authority in intake | Approval owner decision | Approved workflow and permissions |
| PAY-010 payment period | payment period/batch/cutoff | Partial | `ExamPeriod` may not equal payment period | Payment period decision | Approved batch entity/rule |
| PAY-011 export format | official output fields/format | Missing | Existing compensation export not authoritative | Preview export deferral or format decision | Approved final export/report |
| PAY-012 print shop inclusion/exclusion | paper/print duty records and evidence | Partial | Inclusion unknown | Include/exclude decision | Approved rate/evidence/report handling |
| PAY-013 external user payment handling | external exam/supervision/person type | Partial | External handling unknown | External inclusion decision | Approved external payment workflow |
| PAY-014 audit evidence requirement | audit log, evidence trail, approval trail | Partial | Required evidence set unknown | Audit evidence decision | Full auditable payment trail |

## Summary

The current EMS data is enough to identify many candidate duty records. It is not enough to implement payment preview behavior because each candidate data source depends on missing rule decisions.

## New Advance/Reconciliation Rule Gaps

| Rule Decision | Required Data | Current Availability | Gap | Needed Before Preview | Needed Before Final Payment |
|---|---|---|---|---|---|
| Advance disbursement normal timing | Approved roster, batch status | Assignment data exists; advance batch does not | Need confirmation that payment normally precedes post-duty evidence | Needed to design batch preview correctly | Required |
| Roster approval before advance batch | Roster approval owner/status | Not explicit | Need who approves roster and when | Required | Required |
| Post-duty evidence review | Check-in, supervisor confirmation, substitution, notes | Partial | Need evidence hierarchy and reviewer | Needed for reconciliation preview | Required |
| Explanation deadline | Explanation request/submission timestamps | Missing | Need deadline rule | Can be placeholder only | Required |
| Force majeure decision | Explanation type, reviewer, decision | Missing | Need accepted reasons and reviewer | Needed for status labels | Required |
| Refund/offset rule | Refund status, offset flag, finance owner | Missing | Need when refund/offset applies | Needed for queue labels | Required |
| Substitute after original paid | Original payee, substitute, batch link | Partial swap data only | Need finance treatment | Required for reconciliation cases | Required |
