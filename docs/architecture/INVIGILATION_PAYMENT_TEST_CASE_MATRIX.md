# Invigilation Payment Test Case Matrix

**Date**: 2026-06-02  
**Status**: PREVIEW ONLY - NOT PAYMENT AUTHORIZATION

Allowed readiness values:

- `READY`
- `NOT_READY`
- `BLOCKED_BY_RULE`
- `BLOCKED_BY_DATA`

No test case is ready because no rule answers are present.

| Test ID | Scenario | Required input | Expected preview behavior if rules are answered | Expected exception behavior | Approval requirement | Missing rule/data | Test status |
|---|---|---|---|---|---|---|---|
| TC-001 | Normal confirmed invigilation | Assigned supervision, confirmed evidence, period, role | Show duty as preview-eligible | No exception if evidence rule satisfied | Pending approval rule | PAY-001, PAY-002, PAY-004, PAY-009, PAY-010 | BLOCKED_BY_RULE |
| TC-002 | Assigned but no check-in | Assigned supervision, missing evidence | Show duty with missing evidence | Flag missing check-in/evidence if required | Manual review pending | PAY-004 evidence rule | BLOCKED_BY_RULE |
| TC-003 | Substitution before exam | Accepted swap before exam | Show final assignee and substitution marker | Flag substitution outcome per rule | PAY-006 required | PAY-006 substitution rule | BLOCKED_BY_RULE |
| TC-004 | Emergency replacement | Emergency substitution flag | Show replacement as emergency duty | Flag emergency reassignment | Manual review likely | PAY-006 and emergency rule | BLOCKED_BY_RULE |
| TC-005 | No-show | Assignment plus no-show evidence | Show non-payable or review state per rule | Flag no-show rule outcome | Required | PAY-005 and no explicit no-show field | BLOCKED_BY_DATA |
| TC-006 | Late arrival | Assignment plus invigilator late evidence | Show late exception state per rule | Flag late-arrival rule outcome | Required | PAY-008 and no invigilator late field | BLOCKED_BY_DATA |
| TC-007 | Cancelled exam | Cancelled schedule/exam status | Show cancelled exam duty per rule | Flag cancellation outcome | Required | PAY-007 and cancellation data semantics | BLOCKED_BY_RULE |
| TC-008 | Room changed | Room-change evidence | Show changed room in ledger | Flag room-change review if policy requires | Pending rule | PAY-010-style room/section exception answer | BLOCKED_BY_RULE |
| TC-009 | Split room | One exam split across rooms | Show separate duty records if assignments differ | Flag split-room rule outcome | Pending rule | Room/split payment rule | BLOCKED_BY_RULE |
| TC-010 | Merged rooms | Multiple sections/rooms merged | Show merged context | Flag merged-room rule outcome | Pending rule | Room/merge payment rule | BLOCKED_BY_RULE |
| TC-011 | Chief invigilator rate | Chief role assignment | Show symbolic/actual chief rate after approval | Missing role-rate rule if unanswered | PAY-003 required | PAY-003 role-rate rule | BLOCKED_BY_RULE |
| TC-012 | Assistant invigilator rate | Assistant role assignment | Show symbolic/actual assistant rate after approval | Missing role-rate rule if unanswered | PAY-003 required | PAY-003 role-rate rule | BLOCKED_BY_RULE |
| TC-013 | Staff vs lecturer rate | Person type mapping | Show person-type rate after approval | Missing person-type mapping | PAY-002/PAY-003 required | Finance person-type mapping | BLOCKED_BY_RULE |
| TC-014 | External partner / print shop excluded | External or print-shop duty | Show excluded/review status after rule | Flag inclusion/exclusion decision | PAY-012/PAY-013 required | PAY-012/PAY-013 | BLOCKED_BY_RULE |
| TC-015 | Duplicate assignment same time | Same person overlapping duties | Show duplicate/overlap exception | Flag conflict review | Required | Conflict behavior and approval rule | BLOCKED_BY_RULE |
| TC-016 | Two sessions same day | Two confirmed sessions | Show two duty ledger rows per unit rule | No exception unless limit/rule exists | Pending rule | PAY-001 payment unit and period | BLOCKED_BY_RULE |
| TC-017 | Cross-day exam period summary | Multiple days in one period | Show person summary grouped by period | Missing period rule if unanswered | PAY-010 required | PAY-010 payment period | BLOCKED_BY_RULE |
| TC-018 | Manual override with approval | Override record and approver | Show override marker | Flag missing approval evidence if absent | Required | PAY-009/PAY-014 approval/audit rule | BLOCKED_BY_RULE |
| TC-019 | Export locked after approval | Approved batch and export status | Show locked export state | Flag attempted rerun if locked | Approval/export rule required | PAY-011 and export lock data missing | BLOCKED_BY_DATA |
| TC-020 | Re-run preview after correction | Corrected assignment/evidence | Show refreshed preview version | Flag changed rows for audit | Required if approval started | PAY-014 audit/versioning rule | BLOCKED_BY_RULE |

