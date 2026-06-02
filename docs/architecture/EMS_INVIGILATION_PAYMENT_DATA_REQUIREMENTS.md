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
- Check-in or attendance confirmation
- Substitution records
- Cancellation and no-show records
- Payment rate table
- Approval status
- Export or payment batch period

## Required Outputs

- Invigilation duty summary
- Person-level duty count
- Payable session or hour count
- Payment amount
- Exception list
- Approval sheet
- Audit trail

## Missing Or Unknown

- Rate rule
- Approval owner
- Payment period rule
- Evidence requirement
- Deduction or no-show rule
- Late arrival rule
- Substitution transfer rule
- Whether print shop or exam-paper distribution duties are payable in EMS
- Whether external exam supervision uses the same payment batch as internal exam invigilation

## Data Quality Gates

Before calculating payment, EMS must be able to identify:

- Which duty was assigned.
- Who actually performed or confirmed the duty.
- Which role and rate apply.
- Whether any replacement occurred.
- Whether the exam was cancelled or changed.
- Whether the payment period is approved for calculation.

## Non-Sources

The following must not be used for invigilation payment:

- Teaching workload hours
- Course teaching eligibility
- Base workload
- Co-teaching ratio
- Thesis/advisor workload
- Special teaching program rules
- Any teaching compensation workbook

