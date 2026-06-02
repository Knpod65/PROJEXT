# EMS Invigilation Payment Data Requirements

**Date**: 2026-06-02  
**Status**: Requirements baseline. Payment calculation rules still require human confirmation.

## Required Inputs

- Exam schedule
- Room assignment
- Invigilator assignment
- Assigned role
- Duty time and date
- Duty duration or session unit
- Staff, lecturer, or external person identity
- Approved roster status
- Advance payment batch status
- Check-in or attendance confirmation for post-duty reconciliation
- Substitution records
- Cancellation and no-show records
- Absence explanation records
- Refund or offset records
- Payment rate table
- Approval status
- Export or payment batch period

## Required Outputs

- Invigilation duty summary
- Person-level duty count
- Payable session or hour count
- Advance batch preview
- Payment amount preview only when rates are approved
- Post-duty reconciliation queue
- Absence explanation list
- Refund/offset tracker
- Exception list
- Approval sheet
- Audit trail

## Missing Or Unknown

- Rate rule
- Approval owner
- Payment period rule
- Evidence requirement
- Deduction or no-show rule
- Advance disbursement roster approval rule
- Explanation deadline and reviewer
- Force majeure acceptance rule
- Refund or offset rule
- Late arrival rule
- Substitution transfer rule
- Whether print shop or exam-paper distribution duties are payable in EMS
- Whether external exam supervision uses the same payment batch as internal exam invigilation

## Data Quality Gates

Before advance batch preparation, EMS must be able to identify:

- Which duty was assigned.
- Which role and rate apply.
- Which roster approval permits batch inclusion.
- Which payment period is approved for batch review.

Before post-duty reconciliation closure, EMS must be able to identify:

- Who actually performed or confirmed the duty.
- Whether any replacement occurred.
- Whether absence/no-show requires explanation.
- Whether force majeure or unavoidable absence is accepted.
- Whether refund, waiver, or offset is required.
- Whether the exam was cancelled or changed.
- Whether the reconciliation case is approved for closure.

Check-in/attendance is not a default pre-disbursement gate. It is reconciliation evidence unless finance/admin policy explicitly changes that rule.

## Non-Sources

The following must not be used for invigilation payment:

- Teaching workload hours
- Course teaching eligibility
- Base workload
- Co-teaching ratio
- Thesis/advisor workload
- Special teaching program rules
- Any teaching compensation workbook
