# EMS Scope Boundary - Exam And Invigilation Only

**Date**: 2026-06-02  
**Status**: Authoritative scope boundary for EMS payment and workload features

## Rule For Future Agents

Any future agent must read this file before touching EMS payment, compensation, workload, duty analytics, export, or finance-integration features.

## Correct EMS Scope

EMS is only about exam operations:

- Exam scheduling
- Exam room assignment
- Student exam timetable
- Teacher exam schedule
- Staff and invigilator assignment
- Staff availability
- Exam duty workload and fairness
- Check-in, attendance, and confirmation of invigilation duty
- Exam paper distribution and print shop handling where already present in EMS
- Invigilation payment calculation and payment reporting

## Explicitly Out Of Scope

EMS is not about:

- Excess teaching compensation
- Teaching workload calculation
- Course eligibility for teaching pay
- Co-teaching workload payment
- Thesis or advisor workload payment
- Base workload hours
- Special teaching program payment
- Course eligibility classification for teaching compensation
- `Payment_Report_PENDING` or equivalent teaching compensation workbook outputs

## Terminology

- `payment` in EMS means invigilation payment only.
- `compensation` in EMS means invigilation or exam-supervision payment only, unless a historical document is explicitly marked otherwise.
- `workload` in EMS means exam duty workload only.
- `eligibility` in EMS means eligibility to receive invigilation payment after confirmed exam duty, not teaching-course payment eligibility.
- `rate` in EMS means an invigilation duty rate or exam-operation duty rate.
- `confirmed duty` means an assigned exam duty that has the required attendance, check-in, signature, QR, supervisor, or approval evidence defined by admin/finance rules.

## Source Of Truth Rule

Do not use teaching workload records, teaching course eligibility, base workload hours, co-teaching ratios, thesis/advisor workload, or any teaching compensation workbook as an EMS payment source of truth.

EMS invigilation payment can only be derived from:

- Exam schedules
- Rooms
- Assigned invigilators or exam-operation duty staff
- Duty roles
- Duty date/time/duration/session unit
- Check-in or attendance confirmation
- Substitution/replacement records
- Cancellation/no-show records
- Approved invigilation rate rules
- Approved payment period and payment batch

## Safe Handling Of Existing Names

The current codebase contains generic names such as `compensation`, `workload`, and `export_compensation`. These are not automatically wrong. They are EMS-valid only when they refer to invigilation or exam-operation duty payment and workload.

Do not rename or rewrite those code surfaces without tests and a migration/compatibility plan. Prefer documentation clarification first.

