# Invigilation Payment Rule Intake Source Review

**Date**: 2026-06-02  
**Pass**: Invigilation payment rule intake + preview model scaffold  
**Status**: Docs-only foundation. No payment calculation implemented.

## Documents Read

- `docs/architecture/EMS_SCOPE_BOUNDARY_EXAM_AND_INVIGILATION_ONLY.md`
- `docs/architecture/EMS_INVIGILATION_PAYMENT_MODEL.md`
- `docs/architecture/EMS_INVIGILATION_PAYMENT_DATA_REQUIREMENTS.md`
- `docs/architecture/EMS_CURRENT_PAYMENT_AND_WORKLOAD_CODE_AUDIT.md`
- `docs/operations/INVIGILATION_PAYMENT_RULE_QUESTIONS.md`
- `docs/architecture/EMS_CORRECTED_NEXT_PHASE_ROADMAP.md`
- `docs/architecture/EMS_100_PERCENT_MASTER_SCORECARD.md`
- `docs/architecture/EMS_100_PERCENT_READINESS_EXECUTIVE_SUMMARY.md`
- `docs/operations/FINAL_DEMO_READINESS_CERTIFICATE.md`
- `docs/operations/DEMO_LIMITATIONS_AND_DISCLOSURE.md`

## Current Confirmed Scope

EMS payment means invigilation payment only. In-scope payment preparation may use exam schedules, exam rooms, supervision assignments, staff availability, exam duty workload, check-in or attendance confirmation, substitution records, cancellation/no-show evidence, approved rate rules, and approved payment periods.

Teaching workload compensation remains explicitly out of scope. EMS must not use excess teaching workload, teaching-course eligibility, base workload, co-teaching, thesis/advisor workload, or teaching compensation workbook logic.

## What Is Known

- `ExamSchedule` has exam date, time, room, section, exam type, status, and supervision relationships.
- `Supervision` has assigned user, role, slot order, provisional compensation, confirmed flag, swap flags, baseline user, and emergency substitution flag.
- `CheckinEvent` records room-operation check-ins with schedule, user, check-in type, timestamp, late student count, notes, and confirmation flags.
- `ExamPickupQrToken` and `ExamPickupCheckin` record exam-paper pickup QR state, scan status, scan time, role, duplicate flag, and token/window metadata.
- `PaperDistributionAssignment` records paper-distribution duty date/time, person, duty type, workload units, assignment mode, and covered schedule count.
- `SwapRequest` records requester/target supervision, status, response timestamp, rejection reason, and admin override.
- Existing `export_compensation` and `compensation` fields are provisional EMS invigilation/exam-supervision surfaces only; they are not final finance authority.

## What Is Unknown

- Payment unit: per session, hour, day, block, role unit, or hybrid.
- Rate table and whether current placeholder/default rates are valid.
- Whether rates differ by lecturer/staff/external, chief/assistant/runner, internal/external exam, or print-shop/paper handling role.
- Evidence rule: assignment only, check-in, QR, signature, supervisor approval, paper form, or combination.
- Exception rules for no-show, late arrival, substitutions, cancelled exams, room changes, merged/split rooms, online exams, and emergency reassignments.
- Approval owner, verification owner, export owner, and final signatory.
- Payment period and cutoff rule.
- Finance output format and required column names.

## Must Be Answered By Finance/Admin

- Official payment unit and rate rules.
- Which duty roles are payable.
- Required roster approval before advance batch and required evidence after duty for reconciliation.
- Exception outcomes and deduction/transfer rules.
- Payment period, cutoff, approval owner, and final sign-off.
- Official export/report format.
- Whether print shop, paper distribution, and external exam duties are included.

## Must Be Answered By System/Data Audit

- Whether existing check-in events are tied closely enough to the actual invigilator who performed duty.
- Whether QR pickup evidence is payment evidence or only paper-handling evidence.
- Whether `Supervision.confirmed` is assignment confirmation, attendance confirmation, or both.
- Whether late/no-show can currently be identified for invigilators.
- Whether accepted swaps reliably preserve original and final duty owner for payment.
- Whether payment period can be derived from `ExamPeriod` or needs a separate payment batch concept.

## What Remains Blocked

- Final payment calculation.
- Final payable amount output.
- Official payment report/export.
- Payment approval workflow.
- Production/payment readiness claims.

No blocker should be resolved by assumption. The rule intake and decision register must be completed by the responsible human owners first.
