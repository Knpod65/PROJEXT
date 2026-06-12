# Payment Supporting Finance Roster — Algorithm Specification

**Date**: 2026-06-12
**Status**: DESIGN — not yet implemented
**Implementation gate**: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`

---

## Draft Label (Required on Every Sheet)

`ร่างเอกสารประกอบการตรวจนับค่าตอบแทน ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย`
`Draft supporting roster for payment checking only. Not payment authorization.`

---

## Inputs

| Input | Source | Notes |
|-------|--------|-------|
| Invigilation assignments | `Supervision` table | Post-optimize roster; or `SupervisionBaseline` — pending confirmation |
| Paper distribution staff | `PaperDistributionAssignment` table | Per date/time slot |
| Exam schedule rows | `ExamSchedule` | With `Room` and `Section` joins |
| Room identity | `Room` | `code`, `capacity` |
| Student counts | `Section.num_students` | Via ExamSchedule → Section |
| Payment settings | `PaymentDocumentSettings` | Weekday/weekend rates from active settings |
| Review/gate status | `PaymentDocumentReviewRecord` | Must be `ACCEPTED_FOR_DRAFT_EXPORT` |
| Request scope | API payload | `academic_year`, `semester`, `exam_type`, `period_id` |

---

## Step A — Filter Eligible Exam Rows

**Input**: All `ExamSchedule` rows matching the request scope.

**Include**:
- `ExamSchedule.status` in (`published`, `locked`)
- Rows with a physical `Room` assignment (`room_id` is not null)

**Exclude** (document in Sheet 4 trace with reason):
- Online exams: `ExamSubmission.exam_type_choice = "online"` — these do not create ExamSchedule rows,
  so they are excluded automatically. If ExternalExam rows exist for the scope, document them
  separately in the trace.
- ExamSchedule rows with `room_id = null`
- ExamSchedule rows with status `draft` or `cancelled`

**Online exam note**: No ExamSchedule or Supervision rows are created for online exams. This is
not a filtering step at runtime — it is a structural property of the data model. Document this
in the trace sheet for transparency.

---

## Step B — Group By Date/Time

**Key**: `(normalized_exam_date, normalized_time_slot)`

For each group:
- Collect all eligible `ExamSchedule` rows
- `room_count` = count of distinct `room_id` values
- `section_count` = count of distinct `ExamSchedule` rows
- `total_students` = sum of `Section.num_students` across all rows in group
- `day_of_week` = weekday name from `exam_date` (Monday–Sunday, Thai label)
- `day_type` = `weekday` if Mon–Fri, `weekend` if Sat–Sun
- `rate` = weekday rate or weekend rate from active payment settings

**Normalization**: `exam_date` must be compared as date (not datetime). `time_slot` is constructed
from `ExamSchedule.exam_time` (or `exam_time_start`/`exam_time_end` if available).

---

## Step C — Identify Invigilation / Open-Room Persons

For each `(exam_date, time_slot)` group:

1. Collect all `Supervision` rows where `Supervision.schedule_id` is in the group's ExamSchedule ids
2. `role_in_exam` values: `supervisor`, `chief`, `distributor`
3. Deduplicate by `user_id` within the group

**Duplicate-person-in-slot policy** (PENDING CONFIRMATION):
- Default design: one paid session per person per slot, regardless of number of rooms supervised
- If a person has multiple rooms in the same slot, list all rooms in Sheet 2 column G
- Count column I = 1 (pending policy confirmation item #2)
- Flag "multi-room-single-count" in notes if the person covers >1 room

**Output per person**:
- `user_name` from User record
- `role_in_exam` 
- `room_codes` = list of rooms from the person's Supervision rows
- `section_labels` = abbreviated course/section labels
- `pay_count` = 1 (pending confirmation)

---

## Step D — Assign Paper-Distribution Staff to Rooms

For each `(exam_date, time_slot)` group:

1. Collect `PaperDistributionAssignment` rows where `exam_date` and `exam_time` match the slot
2. Collect eligible physical rooms from Step B for this slot

**Room ranking**:
1. Sort rooms by `Section.num_students DESC`
2. Tie-break: `Room.code ASC` → `Section.course_code ASC` → `Section.section ASC`

**Assignment**:
- Person 1 (first in PaperDistributionAssignment, ordered by id ASC) → rank 1 room
- Person 2 → rank 2 room (must be a different room when 2+ rooms exist)

**Edge cases**:
- `room_count < 2`: assign person 1 to rank 1 room, flag "insufficient-physical-rooms"
- `room_count = 0`: flag "no-eligible-rooms — online-only slot?"
- `len(paper_dist_persons) > 2`: assign first 2, flag extra persons "extra-paper-dist-person-review-required"
- `len(paper_dist_persons) = 0`: flag "no-paper-dist-assignment-found"
- `len(paper_dist_persons) = 1 and room_count >= 2`: assign to rank 1 room only

**Output per assignment**:
- `exam_date`, `time_slot`, `room_rank`, `room_code`, `num_students`, `section_labels`
- `person_name`, `assignment_reason`, `notes`

---

## Step E — Compute Payment Headcount and Amounts

For each `(exam_date, time_slot)`:

```
inv_count   = count of distinct persons from Step C
paper_count = count of paper-dist persons with room binding from Step D
total_heads = inv_count + paper_count
rate        = weekday_rate if day_type == "weekday" else weekend_rate
inv_amount  = inv_count × rate
paper_amount = paper_count × rate
slot_total  = inv_amount + paper_amount
```

All amounts carry label `DRAFT_SUPPORTING_EXPORT_ONLY — not authorizing`.

**Safety**: Do not write `payment_authorization_enabled = True`. Do not write `final_export_enabled = True`.

---

## Step F — Produce Sheets

**Sheet 1** — slot summary row per `(exam_date, time_slot)` from Step E

**Sheet 2** — person row per person per slot from Steps C + D combined:
- Invigilation persons: role from Supervision
- Paper-dist persons: role = "กรรมการจ่ายข้อสอบที่ผูกห้อง"
- Include sheet metadata block (export_status, safety flags, generation timestamp)

**Sheet 3** — paper-to-room mapping rows from Step D

**Sheet 4** — source trace rows from all eligible `ExamSchedule` rows (Step A)

**Column widths**: Use `get_column_letter(col_idx)` from `openpyxl.utils` — do NOT use
`ws.cell(1, col_idx).column_letter` on merged cells (causes `AttributeError: 'MergedCell'`).

---

## Step G — Safety Flags

Enforce in export service (hard-coded, not derived from input):

```python
export_status = "DRAFT_SUPPORTING_EXPORT_ONLY"
payment_authorization_enabled = False   # never True
final_export_enabled = False            # never True
document_status = "DRAFT_NOT_AUTHORIZED"
```

Gate rejects (`HTTP 400`) if draft response has `payment_authorization_enabled=True` or
`final_export_enabled=True` — same pattern as the existing summary XLSX gate.

---

## Unresolved Policy Items (Gate Blockers)

| # | Item | Default assumption | Needed from |
|---|------|--------------------|-------------|
| 1 | Active `Supervision` rows vs `SupervisionBaseline` snapshot | Use `Supervision` (live post-optimize) | Admin/finance |
| 2 | Duplicate-person-in-slot counting | Count = 1 per person per slot | Admin/finance |
| 3 | Finance-preferred column order | As specified in contract doc | Finance |
| 4 | `PaperDistributionAssignment` vs `ExamSchedule.paper_distributor` string | Use `PaperDistributionAssignment` where rows exist | Admin |
| 5 | `SupervisionBaseline` preference for payment | No (use live `Supervision`) | Admin |

---

## Test Matrix (For Future Implementation Pass)

| Category | Tests | Description |
|---|---|---|
| Gate-block | 8 | One test per precondition failure → HTTP 400 |
| Role | 7 | admin/esq_head/secretary → 200+xlsx; staff/teacher/print_shop → 403; unauth → 401 |
| Sheet structure | 4 | Verify 4 sheets exist with correct names |
| Safety flag | 4 | payment_authorization_enabled=false, final_export_enabled=false, DRAFT_NOT_AUTHORIZED label, no mutation |
| Paper-to-room | 5 | Top-2 selection, tie-break, insufficient-rooms flag, 0-rooms flag, extra-persons flag |
| Person dedup | 3 | Same person 2 rooms counted once, role correct, rooms listed |
| Content type | 2 | Content-Type is xlsx, Content-Disposition matches filename pattern |
| **Total minimum** | **33** | |

---

## Related Documents

- `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_REVIEW.md`
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md`
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md`
