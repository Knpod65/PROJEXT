# EMS Invigilation Payment Model

**Date**: 2026-06-02  
**Status**: Conceptual model only. Do not implement final calculation until rules are confirmed.

## Purpose

This document defines the correct EMS payment domain. EMS payment means invigilation payment only. It does not mean excess teaching compensation or teaching workload payment.

## Conceptual Entities

- Exam
- Exam date and time
- Room
- Course and section
- Invigilator or assigned person
- Role in exam duty
- Duty session
- Attendance or check-in confirmation
- Replacement or substitution
- Rate rule
- Payment period
- Payment batch
- Payment approval

## Payment May Be Based On

- Confirmed invigilation duty
- Actual assigned exam session
- Attendance or check-in confirmation
- Role and rate
- Substitution or replacement rules
- Cancellation and no-show rules
- Approved payment period
- Payment batch approval status

## Payment Must Not Be Based On

- Teaching workload hours
- Course eligibility for teaching compensation
- Base workload
- Co-teaching ratio
- Thesis or advisor workload
- Special teaching program payment rules
- Teaching compensation workbook formulas

## Draft Lifecycle

1. Build exam schedule and room assignment.
2. Assign invigilators and duty roles.
3. Record attendance, check-in, signature, QR confirmation, or other required evidence.
4. Resolve substitution, cancellation, late arrival, and no-show exceptions.
5. Apply approved invigilation rate rules.
6. Generate payment preview for the approved period.
7. Review exception list.
8. Approve payment batch.
9. Export payment report and retain audit trail.

## Existing EMS Surfaces

The current codebase already contains payment-like surfaces:

- `supervisions.compensation`
- `external_supervisions.compensation`
- `export_compensation`
- `compensation_rate_internal`
- `compensation_rate_external`

These are not final finance rules. Treat them as existing EMS invigilation or exam-supervision payment candidates until admin/finance confirms the rate, evidence, exception, and approval rules.

## Open Questions

1. Is payment per session, per hour, or per exam block?
2. Are rates different for staff, lecturer, and external invigilators?
3. Are chief invigilator and assistant invigilator paid differently?
4. Does no-show cancel payment?
5. Does substitution transfer payment?
6. Are print shop staff paid in this system, or only invigilators?
7. Who verifies and approves payment?
8. What evidence is required before payment?

## Implementation Gate

Do not modify payment code until:

- The questions in `docs/operations/INVIGILATION_PAYMENT_RULE_QUESTIONS.md` are answered.
- Existing payment/export tests are reviewed or new tests are added.
- A human owner confirms whether current `compensation` fields should be renamed, wrapped, or retained for compatibility.

