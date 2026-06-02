# Invigilation Absence Explanation Requirements

**Date**: 2026-06-02  
**Scope**: Operational requirements for post-duty absence explanation. Not a payment approval.

## When Explanation Is Required

- Assigned person did not invigilate.
- No check-in and no supervisor confirmation.
- Late attendance beyond accepted threshold.
- Substitute was not recorded in advance.
- Conflict exists between schedule and actual duty.

## Possible Evidence

- Explanation letter.
- Email explanation.
- Supervisor note.
- Medical certificate if applicable.
- Official duty conflict note.
- Substitute confirmation.
- Staff/admin incident note.

## Required Fields

| Field | Description |
|---|---|
| `person_name` | Assigned person name. |
| `duty_date` | Exam duty date. |
| `exam_session` | Exam/session identifier. |
| `room` | Room or venue. |
| `reason` | Explanation reason. |
| `evidence_document_ref` | Reference to letter, note, email, certificate, or incident record. |
| `submitted_at` | Submission timestamp. |
| `reviewed_by` | Reviewer name/role. |
| `decision` | Decision label. |
| `refund_required` | Whether refund/offset is required. |
| `notes` | Reviewer or finance notes. |

## Decision Labels

- `ACCEPTED_NO_REFUND`
- `ACCEPTED_WITH_OFFSET`
- `REFUND_REQUIRED`
- `REJECTED_PENDING_FINANCE`
- `NEEDS_MORE_INFO`

## Safety Note

The system records the explanation and decision trail. It must not auto-approve force majeure, auto-waive refunds, or auto-calculate refund amounts until finance/admin policy is confirmed.

