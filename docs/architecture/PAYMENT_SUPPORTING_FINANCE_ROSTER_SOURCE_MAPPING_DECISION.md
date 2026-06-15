# Payment Supporting Finance Roster — Source Mapping Decision

**Date**: 2026-06-15
**Gate**: `SUPPORTING_ROSTER_EXPORT_IMPLEMENTED_VALIDATED`
**Method**: Backend model inspection (`backend/models.py`, `backend/services/staff_workloads.py`, `backend/services/invigilation_advance_batch_preview_service.py`)

---

## Source Mapping Table

| Source | Table / Field | Key Fields | Confidence | Implementation Blocker? | Use in Export |
|--------|--------------|-----------|-----------|------------------------|--------------|
| Invigilation assignments | `Supervision` | `schedule_id` FK→ExamSchedule, `user_id` FK→User, `role_in_exam` ∈ {supervisor, chief, room_keeper, distributor}, `slot_order`, `confirmed` | HIGH | NO | YES — Sheets 2, 3, 5 |
| Room opener | `Supervision` | `role_in_exam = "room_keeper"`, `slot_order = 99` | HIGH | NO | YES — Sheet 2 role "ผู้เปิดห้อง/คุมสอบ" |
| Paper distribution staff | `PaperDistributionAssignment` | `exam_period_id`, `exam_date`, `exam_time`, `user_id` FK→User, `duty_type=PAPER_DISTRIBUTION`, `workload_units`, `covered_schedule_count` | HIGH | NO | YES — Sheets 2, 3, 4 |
| Exam schedule rows | `ExamSchedule` | `exam_date`, `exam_time`, `exam_time_start`, `exam_time_end`, `exam_type`, `status`, `section_id` FK→Section, `room_id` FK→Room | HIGH | NO | YES — grouping key, trace |
| Student count | `Section.num_students` | via `ExamSchedule.section_id → Section` | HIGH | NO | YES — paper-to-room ranking |
| Course / section identity | `Section`, `Course` | `course_code`, `section` | HIGH | NO | YES — Sheet 5 trace |
| Physical room | `Room` where `e_room_code IS NULL` | `id`, `code`, `capacity`, `e_room_code` | HIGH | NO | YES — physical room filter for mapping |
| Online room (exclude) | `Room` where `e_room_code IS NOT NULL` | `e_room_code` — CMU e-room API identifier | HIGH | NO | EXCLUDE from physical mapping; TRACE ONLY in Sheet 5 |
| Person name | `User.full_name` or equivalent | via `Supervision.user_id` / `PaperDistributionAssignment.user_id` | HIGH | NO | YES — Sheets 2, 3, 4 |
| Post-confirm baseline | `SupervisionBaseline` | `user_id`, `schedule_id`, `role_in_exam`, `confirmed_at` | HIGH | NO | NOT USED — historical stats only |
| Legacy paper-dist string | `ExamSchedule.paper_distributor` | String(200), nullable | LOW — inconsistently populated | NO | NOT USED — use `PaperDistributionAssignment` instead |
| `role_in_exam = "distributor"` | `Supervision` | enum value exists in `SupervisionRole`; no creation code found in optimization logic | UNCERTAIN | MINOR | Treat as invigilation person if present; document in Sheet 2 notes |

---

## Source Usage Decisions

### Invigilation Persons (Sheets 2, 3, 5)

**Source**: `Supervision` table, joined via `schedule_id → ExamSchedule`

**Filter**: `ExamSchedule.exam_type = requested exam_type`, `ExamSchedule.exam_date` and `ExamSchedule.exam_time` match slot, `ExamSchedule.status` in {published, locked}

**Role mapping**:
| `role_in_exam` | Finance label | Counted for payment? |
|----------------|--------------|---------------------|
| `supervisor` | กรรมการคุมสอบ | YES |
| `chief` | กรรมการคุมสอบ (หัวหน้า) | YES |
| `room_keeper` | ผู้เปิดห้อง/คุมสอบ | YES |
| `distributor` | กรรมการคุมสอบ (distributor) | YES — if present; uncertain creation path |

**Name rule**: Use `User.full_name` from `Supervision.user_id`. Do NOT derive from instructor/course. If `user_id` is null or name not resolvable: flag `SOURCE_NAME_REQUIRED`.

**Dedup**: Within same `exam_date + time_slot`, deduplicate by `user_id`. Count = 1 per person regardless of room count. Flag `DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT` if collapsed.

---

### Paper Distribution Staff (Sheets 2, 3, 4)

**Source**: `PaperDistributionAssignment` table

**Filter**: `exam_date = slot.exam_date`, `exam_time = slot.exam_time` (or normalized time match), joined to `ExamPeriod` for scope matching

**Name rule**: Use `User.full_name` from `PaperDistributionAssignment.user_id`

**NOT USED**: `ExamSchedule.paper_distributor` (legacy string field — inconsistently populated, not authoritative)

---

### Physical Room Identification

**Source**: `Room` model

**Physical** (eligible for paper-to-room mapping): `Room.e_room_code IS NULL`

**Online** (excluded from mapping): `Room.e_room_code IS NOT NULL`

**No explicit `is_online` boolean exists** — `e_room_code` presence is the convention.

---

### Room Ranking for Paper-to-Room Assignment

For each `exam_date + time_slot`:
1. Collect `ExamSchedule` rows in slot with physical rooms only
2. `Section.num_students` per ExamSchedule row = student count for that room
3. Rank by: `num_students DESC` → `Room.code ASC` → `course_code ASC` → `section ASC`
4. Assign `PaperDistributionAssignment` person 1 → rank-1 room; person 2 → rank-2 room

---

### `SupervisionBaseline` — Not Used

`SupervisionBaseline` is an immutable snapshot created when admin completes 4-signature confirmation via `_save_baseline_stats()` in `backend/services/optimize_workflow.py`. It is used for historical fairness statistics only. It is NOT updated when swaps occur. The current payment roster should use live `Supervision` rows for accuracy.

---

## Minor Open Item (Non-Blocking)

`role_in_exam = "distributor"` exists in the `SupervisionRole` enum (`backend/models.py`) but no code path was found that creates `Supervision` rows with this role during optimization. If such rows exist in production data (possible from manual or legacy imports), they should be treated as invigilation persons and included in the payment count. The algorithm must handle this gracefully (not crash) and document the source in Sheet 2 notes.

---

## Decision Record

| Decision | Value | Rationale |
|----------|-------|-----------|
| Primary invigilation source | `Supervision` | Live, post-optimize, supports swaps |
| Paper distribution source | `PaperDistributionAssignment` | Actively created by assignment service; authoritative |
| Physical room filter | `Room.e_room_code IS NULL` | Convention in codebase |
| Baseline source | NOT USED | Historical stats only; immutable post-confirm |
| Legacy string field | NOT USED | Inconsistently populated |
| Dedup policy | 1 session per person per slot | Confirmed by business rule B/C |
| Name derivation | From User model only | Cannot fabricate from course/instructor |
