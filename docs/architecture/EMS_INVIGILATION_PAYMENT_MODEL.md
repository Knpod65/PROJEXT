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
- Approved duty roster
- Advance payment batch
- Attendance or check-in confirmation for post-duty reconciliation
- Replacement or substitution
- Absence explanation
- Rate rule
- Payment period
- Refund or offset case
- Payment approval
- Reconciliation closure

## Advance Disbursement May Be Based On

- Approved invigilation assignment roster
- Assigned exam session
- Role and rate
- Approved payment period
- Payment batch approval status

## Post-Duty Reconciliation May Be Based On

- Attendance or check-in confirmation
- Supervisor confirmation
- Substitution or replacement evidence
- Cancellation and no-show/absence rules
- Explanation note or document
- Force majeure review
- Refund or offset decision

Missing check-in is not automatic non-payment. It triggers reconciliation unless policy explicitly says otherwise.

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
3. Approve invigilation roster for payment batch review.
4. Apply approved invigilation rate rules if available.
5. Generate advance payment batch preview for the approved period.
6. Approve advance batch and disburse if policy permits.
7. After duty, record attendance, check-in, signature, QR confirmation, supervisor note, or other evidence.
8. Resolve substitution, cancellation, late arrival, absence, and no-show reconciliation cases.
9. Collect explanation and finance/admin decision where needed.
10. Track refund, waiver, or offset if required.
11. Close reconciliation and retain audit trail.

## Existing EMS Surfaces

The current codebase already contains payment-like surfaces:

- `supervisions.compensation`
- `external_supervisions.compensation`
- `export_compensation`
- `compensation_rate_internal`
- `compensation_rate_external`

These are not final finance rules. Treat them as existing EMS invigilation or exam-supervision payment candidates until admin/finance confirms the rate, advance batch, evidence, reconciliation, refund/offset, exception, and approval rules.

## Open Questions

1. Is payment per session, per hour, or per exam block?
2. Are rates different for staff, lecturer, and external invigilators?
3. Are chief invigilator and assistant invigilator paid differently?
4. Is payment normally disbursed before post-duty attendance confirmation?
5. What roster approval is required before advance disbursement?
6. What evidence is reviewed after duty for reconciliation?
7. Does no-show require explanation, refund, offset, waiver, or another review outcome?
8. Does substitution transfer payment, trigger refund/offset, or require manual review?
9. Are print shop staff paid in this system, or only invigilators?
10. Who verifies roster, approves advance batch, reviews reconciliation, and signs refund/offset decisions?

## Implementation Gate

Do not modify payment code until:

- The questions in `docs/operations/INVIGILATION_PAYMENT_RULE_QUESTIONS.md` are answered.
- Existing payment/export tests are reviewed or new tests are added.
- A human owner confirms whether current `compensation` fields should be renamed, wrapped, or retained for compatibility.
