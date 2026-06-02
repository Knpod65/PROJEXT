# Invigilation Payment Test Case Matrix

**Date**: 2026-06-02  
**Status**: PREVIEW ONLY - NOT PAYMENT AUTHORIZATION

Default test status: `NOT_READY_UNTIL_RULES_CONFIRMED`

| Test ID | Scenario | Required input | Expected preview behavior | Expected exception behavior | Approval requirement | Test status |
|---|---|---|---|---|---|---|
| TC-001 | Normal confirmed invigilation | Assigned supervision, confirmed evidence, period, role | Show duty as preview-eligible | No exception if evidence rule satisfied | Pending rule | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-002 | Assigned but no check-in | Assigned supervision, missing evidence | Show duty with missing evidence | Flag missing check-in/evidence if required | Manual review pending | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-003 | Substitution before exam | Accepted swap before exam | Show final assignee and substitution marker | Flag substitution rule pending | Approval depends on PAY-006 | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-004 | Emergency replacement | Emergency substitution flag | Show replacement as emergency duty | Flag emergency reassignment | Manual review likely | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-005 | No-show | Assignment plus no-show evidence | Show non-payable or review state only after rule | Flag no-show rule pending | Required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-006 | Late arrival | Assignment plus invigilator late evidence | Show late exception state | Flag late-arrival rule pending | Required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-007 | Cancelled exam | Cancelled schedule/exam status | Show cancelled exam duty | Flag cancellation rule pending | Required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-008 | Room changed | Room-change evidence | Show changed room in ledger | Flag room-change review if policy requires | Pending rule | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-009 | Split room | One exam split across rooms | Show separate duty records if assignments differ | Flag split-room rule pending | Pending rule | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-010 | Merged rooms | Multiple sections/rooms merged | Show merged context | Flag merged-room rule pending | Pending rule | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-011 | Chief invigilator rate | Chief role assignment | Show symbolic chief rate code only | Missing role-rate rule if unanswered | PAY-003 required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-012 | Assistant invigilator rate | Assistant role assignment | Show symbolic assistant rate code only | Missing role-rate rule if unanswered | PAY-003 required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-013 | Staff vs lecturer rate | Person type mapping | Show symbolic person-type rate only | Missing person-type mapping | PAY-002/PAY-003 required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-014 | External partner / print shop excluded | External or print-shop duty | Show excluded/review status after rule | Flag inclusion/exclusion decision pending | PAY-012/PAY-013 required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-015 | Duplicate assignment same time | Same person overlapping duties | Show duplicate/overlap exception | Flag conflict review | Required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-016 | Two sessions same day | Two confirmed sessions | Show two duty ledger rows | No exception unless limit/rule exists | Pending rule | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-017 | Cross-day exam period summary | Multiple days in one period | Show person summary grouped by period | Missing period rule if unanswered | PAY-010 required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-018 | Manual override with approval | Override record and approver | Show override marker | Flag missing approval evidence if absent | Required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-019 | Export locked after approval | Approved batch and export status | Show locked export state | Flag attempted rerun if locked | Approval/export rule required | NOT_READY_UNTIL_RULES_CONFIRMED |
| TC-020 | Re-run preview after correction | Corrected assignment/evidence | Show refreshed preview version | Flag changed rows for audit | Required if approval already started | NOT_READY_UNTIL_RULES_CONFIRMED |

