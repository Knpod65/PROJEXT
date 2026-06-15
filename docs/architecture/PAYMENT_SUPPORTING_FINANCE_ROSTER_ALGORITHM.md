# Payment Supporting Finance Roster — Algorithm Specification

**Date**: 2026-06-12 (updated 2026-06-15)
**Status**: DESIGN — not yet implemented
**Implementation gate**: `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`

---

## Draft Label (Required on Every Sheet)

`ร่างเอกสารประกอบการตรวจนับค่าตอบแทน ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย`
`Draft supporting roster for payment checking only. Not payment authorization.`

---

## Inputs

| Input | Source | Notes |
|-------|--------|-------|
| Invigilation assignments | `Supervision` table | Post-optimize roster (live, post-swap). `SupervisionBaseline` NOT used — historical stats only |
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
- Rows with a `Room` assignment (`room_id` is not null)

**Physical room filter** (for paper-to-room assignment purposes):
- Physical room: `Room.e_room_code IS NULL` — eligible for paper-distribution mapping
- Online room: `Room.e_room_code IS NOT NULL` — excluded from paper mapping; kept in Sheet 5 trace

**Exclude** from payment mapping but keep in trace (Sheet 5, flag `TRACE_ONLY_ONLINE_ROW`):
- ExamSchedule rows whose `Room.e_room_code IS NOT NULL` (online rooms)

**Exclude entirely** (no trace entry needed):
- ExamSchedule rows with `room_id = null`
- ExamSchedule rows with status `draft` or `cancelled`

**Online exam note**: Online exams (`ExamSubmission.exam_type_choice = "online"`) do not create
ExamSchedule rows — automatically absent. If ExternalExam rows exist for the scope, document
separately. Online rooms via `Room.e_room_code IS NOT NULL` DO produce ExamSchedule rows but
must not be assigned as paper-distribution targets. Flag `TRACE_ONLY_ONLINE_ROW` in Sheet 5.

If ALL rooms in a slot are online: flag `NO_ELIGIBLE_PHYSICAL_ROOM_FOR_PAPER_MAPPING` in Sheet 4.

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
2. Include `role_in_exam` values: `supervisor`, `chief`, `room_keeper`, `distributor` (if present)
3. Deduplicate by `user_id` within the group

**Role handling**:
- `supervisor` → บทบาท = กรรมการคุมสอบ; counted for payment
- `chief` → บทบาท = กรรมการคุมสอบ (หัวหน้า); counted for payment
- `room_keeper` (`slot_order=99`) → บทบาท = ผู้เปิดห้อง/คุมสอบ; counted for payment (included in headcount for this roster)
- `distributor` → บทบาท = กรรมการคุมสอบ (distributor); treat as invigilation person if present; document in Sheet 2 notes (enum exists, no creation code found in optimization logic — may appear from manual/legacy data)

**Duplicate-person-in-slot policy** (CONFIRMED — business rule B):
- Count = 1 per person per slot, regardless of room count
- If person linked to multiple rooms in same slot: list all rooms in Sheet 2 column G; count column I = 1
- Flag `DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT` in map_status (Sheet 2 column N)

**Actual-name rule** (CONFIRMED — business rule C):
- `user_name` from `User.full_name` via `Supervision.user_id` ONLY
- Do NOT derive payment names from instructor/teaching assignment fields
- If `user_id` is null or name not resolvable: flag `SOURCE_NAME_REQUIRED` in map_status

**Output per person**:
- `user_name` from User record (never fabricated)
- `role_in_exam` → Thai label
- `room_codes` = list of rooms from the person's Supervision rows
- `section_labels` = abbreviated course/section labels
- `pay_count` = 1
- `map_status` = `DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT` if >1 room, else blank

---

## Step D — Assign Paper-Distribution Staff to Rooms

For each `(exam_date, time_slot)` group:

1. Collect `PaperDistributionAssignment` rows where `exam_date` and `exam_time` match the slot
   - Source: `PaperDistributionAssignment` ONLY — `ExamSchedule.paper_distributor` string field is NOT used
   - Name: `User.full_name` via `PaperDistributionAssignment.user_id`
2. Collect physical rooms from Step A for this slot: `Room.e_room_code IS NULL` only
   - Online rooms (`Room.e_room_code IS NOT NULL`) are excluded from assignment; they appear in Sheet 5 as `TRACE_ONLY_ONLINE_ROW`

**Room ranking** (physical rooms only):
1. Sort by `Section.num_students DESC`
2. Tie-break: `Room.code ASC` → `Section.course_code ASC` → `Section.section ASC`
3. Select top 2 rooms

**Assignment with map_status**:
| Case | Assignment | map_status |
|------|-----------|-----------|
| 2+ physical rooms, 2+ persons | Person 1 → rank-1; person 2 → rank-2 | `MAPPED_TO_TOP_ROOM` |
| 1 physical room, 1+ persons | Person 1 → that room only | `MAPPED_TO_ONLY_ELIGIBLE_ROOM` |
| 0 physical rooms (all online) | No assignment | `NO_ELIGIBLE_PHYSICAL_ROOM_FOR_PAPER_MAPPING` |
| Persons > 2 | First 2 assigned; extras flagged | `EXTRA_PAPER_DISTRIBUTION_REVIEW_REQUIRED` |
| Persons < required | Available assigned; gap flagged | `MISSING_PAPER_DISTRIBUTION_ASSIGNMENT` |

Online rooms must NEVER be silently used as paper-distribution targets.

**Output per assignment**:
- `exam_date`, `time_slot`, `room_rank`, `room_code`, `num_students`, `section_labels`
- `person_name`, `assignment_reason`, `map_status`

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

**Sheet 1** — `สรุปตามวันและช่วงเวลา`
Slot summary row per `(exam_date, time_slot)` from Step E

**Sheet 2** — `รายชื่อประกอบการเบิก`
Person row per person per slot from Steps C + D combined:
- Invigilation/open-room persons: role from Supervision (supervisor/chief/room_keeper/distributor)
- Paper-dist persons: role = กรรมการจ่ายข้อสอบ/เปิดห้อง
- `สถานะการแมพ` column (map_status) for each row
- Include sheet metadata block (export_status, safety flags, generation timestamp)

**Sheet 3** — `ใบลงลายมือชื่อประกอบการเบิก` (NEW)
Signature sheet — mirrors Sheet 2 with blank signature column for human use:
- One row per person per slot (same order as Sheet 2)
- Columns: ลำดับ / วันที่สอบ / ช่วงเวลา / ชื่อ-นามสกุล / บทบาท / จำนวนเงิน / ลายเซ็นผู้รับเงิน / หมายเหตุ

**Sheet 4** — `การผูกคนจ่ายข้อสอบกับห้อง` (was Sheet 3)
Paper-to-room mapping rows from Step D with `สถานะการแมพ` column

**Sheet 5** — `รายละเอียดอ้างอิงห้องและวิชา` (was Sheet 4)
Source trace rows from all eligible `ExamSchedule` rows (Step A):
- Physical rooms: normal trace row
- Online rooms (`e_room_code IS NOT NULL`): trace row with flag `TRACE_ONLY_ONLINE_ROW`

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

## Map Status Enum

```
MAPPED_TO_TOP_ROOM                          — paper-dist person assigned to rank-1 or rank-2 physical room
MAPPED_TO_ONLY_ELIGIBLE_ROOM               — only 1 physical room in slot; 1 person assigned
NO_ELIGIBLE_PHYSICAL_ROOM_FOR_PAPER_MAPPING — all rooms in slot are online; no physical mapping possible
MISSING_PAPER_DISTRIBUTION_ASSIGNMENT      — fewer PDA persons than eligible rooms requiring coverage
EXTRA_PAPER_DISTRIBUTION_REVIEW_REQUIRED   — more than 2 PDA persons for slot; extras flagged
DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT — same user_id linked to >1 room in slot; counted once
SOURCE_NAME_REQUIRED                       — name not resolvable from Supervision/PDA source
TRACE_ONLY_ONLINE_ROW                      — row in Sheet 5 is from online room; excluded from payment mapping
```

---

## Policy Items — ALL RESOLVED (2026-06-15)

| # | Item | Resolution | Evidence |
|---|------|-----------|---------|
| 1 | Active `Supervision` vs `SupervisionBaseline` | Use live `Supervision` | `SupervisionBaseline` is immutable historical stats; created by `_save_baseline_stats()`; not updated by swaps |
| 2 | Duplicate-person-in-slot counting | Count = 1 per person per slot | Confirmed by business rules B and C; flag `DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT` |
| 3 | Finance-preferred column order | Resolved by 5-sheet structure with Thai labels and map_status column | This document + contract doc |
| 4 | `PaperDistributionAssignment` vs legacy string | `PaperDistributionAssignment` is authoritative | `staff_workloads.py:assign_paper_distribution_for_period()` creates rows; legacy string inconsistently populated |
| 5 | `SupervisionBaseline` preference | No — use live `Supervision` | Same as item 1 |

**Gate advanced**: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION` → `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`

---

## Test Matrix (For Future Implementation Pass)

| Category | Tests | Description |
|---|---|---|
| Gate-block | 8 | One test per precondition failure → HTTP 400 |
| Role | 7 | admin/esq_head/secretary → 200+xlsx; staff/teacher/print_shop → 403; unauth → 401 |
| Sheet structure | 5 | Verify 5 sheets exist with correct names (updated from 4) |
| Safety flag | 4 | payment_authorization_enabled=false, final_export_enabled=false, DRAFT_NOT_AUTHORIZED label, no mutation |
| Paper-to-room | 5 | Top-2 selection, tie-break, MAPPED_TO_ONLY_ELIGIBLE_ROOM, NO_ELIGIBLE_PHYSICAL_ROOM flag, extra-persons flag |
| Person dedup | 3 | Same person 2 rooms counted once, DUPLICATE flag set, rooms listed |
| Online-room exclusion | 2 | Online rooms not assigned as paper targets; TRACE_ONLY_ONLINE_ROW flag in Sheet 5 |
| map_status enum | 4 | Correct status per mapping case; SOURCE_NAME_REQUIRED on null user_id |
| Signature sheet | 3 | Sheet 3 rows match Sheet 2; signature column is blank; banner present |
| Content type | 2 | Content-Type is xlsx, Content-Disposition matches filename pattern |
| **Total minimum** | **43** | |

---

## Related Documents

- `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_REVIEW.md`
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_POLICY_CLARIFICATION_SOURCE_REVIEW.md` — clarified rules A–G; all blockers resolved
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_MAPPING_DECISION.md` — per-source confidence table
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md`
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md` — gate: `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_PLAN_READY.md`
