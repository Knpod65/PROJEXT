# Invigilation Payment Rule Answer Intake

**Date**: 2026-06-02  
**Purpose**: Human-fillable rule intake for EMS invigilation payment (`ค่าคุมสอบ`) only.  
**Important**: This is not a payment report and does not authorize payment.

## 1. Payment Unit

Please answer:

- Pay per exam session?
- Pay per hour?
- Pay per day?
- Pay by role?
- Minimum session duration?
- Rounding rule?

Owner answer:

```text
Pending.
```

## 2. Rate Table

Please answer:

- Same rate for all?
- Different rate for lecturer/staff/external?
- Different rate for chief/assistant/runner?
- Rate effective date?
- Who approves rate?

Owner answer:

```text
Pending.
```

## 3. Duty Roles

Possible roles to confirm:

- Chief invigilator
- Assistant invigilator
- Staff invigilator
- Room supervisor
- Exam paper runner
- Print shop / paper handling
- Other

For each role, confirm whether it is payable in EMS and which rate rule applies.

Owner answer:

```text
Pending.
```

## 4. Evidence Required

Please answer:

- Schedule assignment enough?
- Check-in required?
- QR confirmation required?
- Signature required?
- Supervisor approval required?
- Print-shop handoff proof required?

Owner answer:

```text
Pending.
```

## 5. Exceptions

Please answer the payment effect for:

- No-show
- Late arrival
- Replacement
- Substitution
- Cancelled exam
- Room change
- Merged rooms
- Split sections
- Online exam
- Emergency reassignment

Owner answer:

```text
Pending.
```

## 6. Approval Workflow

Please answer:

- Who verifies attendance?
- Who approves payment?
- Who exports payment?
- Who signs final report?

Owner answer:

```text
Pending.
```

## 7. Output Format

Please answer:

- Excel report?
- PDF sign-off?
- Finance import file?
- Person summary?
- Exam-session detail?
- Audit trail?

Owner answer:

```text
Pending.
```

## 8. Payment Period

Please answer:

- Per exam day?
- Per exam period?
- Per semester?
- Per fiscal month?
- Cutoff date?

Owner answer:

```text
Pending.
```

## 9. Required Fields

Please confirm whether each source field is required for payment calculation, evidence, approval, or export:

| Field | Required? | Purpose | Notes |
|---|---|---|---|
| exam_id | Pending | Calculation / audit | |
| course_code | Pending | Export / review | |
| section | Pending | Export / review | |
| exam_date | Pending | Calculation / period | |
| start_time | Pending | Calculation / evidence | |
| end_time | Pending | Calculation / evidence | |
| room_id | Pending | Evidence / exception | |
| room_name | Pending | Export / review | |
| assigned_invigilator_id | Pending | Calculation | |
| assigned_invigilator_name | Pending | Export / review | |
| person_type | Pending | Rate | |
| duty_role | Pending | Rate | |
| assignment_status | Pending | Evidence | |
| checkin_status | Pending | Evidence | |
| checkin_time | Pending | Evidence | |
| confirmed_by | Pending | Approval / evidence | |
| substitution_from | Pending | Exception | |
| substitution_to | Pending | Exception | |
| cancellation_status | Pending | Exception | |
| no_show_flag | Pending | Exception | |
| late_flag | Pending | Exception | |
| approved_for_payment | Pending | Approval | |
| payment_period | Pending | Batch | |
| rate_code | Pending | Calculation | |
| amount_preview | Pending | Preview only | |
| approval_status | Pending | Approval | |
| export_status | Pending | Export lock | |

## 10. Open Decisions

| Decision | Owner | Due Date | Status | Notes |
|---|---|---|---|---|
| Payment unit | TBD | TBD | OPEN | |
| Rate table | TBD | TBD | OPEN | |
| Payable roles | TBD | TBD | OPEN | |
| Evidence rule | TBD | TBD | OPEN | |
| Exception rules | TBD | TBD | OPEN | |
| Approval workflow | TBD | TBD | OPEN | |
| Output format | TBD | TBD | OPEN | |
| Payment period | TBD | TBD | OPEN | |

