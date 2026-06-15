# Payment Supporting Finance Roster — Policy Clarification Source Review

**Date**: 2026-06-15
**Pass**: Policy Clarification + Implementation Readiness
**Previous gate**: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`
**New gate**: `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`

---

## Docs Read In This Pass

| Document | Location |
|---|---|
| PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_REVIEW.md | docs/architecture/ |
| PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md | docs/architecture/ |
| PAYMENT_SUPPORTING_FINANCE_ROSTER_ALGORITHM.md | docs/architecture/ |
| PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md | docs/architecture/ |
| PAYMENT_DOCUMENT_DRAFT_XLSX_FORMAT_DECISION_GATE.md | docs/architecture/ |
| EMS_POST_RC1_NEXT_PHASE_DECISION_MATRIX.md | docs/architecture/ |
| EMS_SUPERVISOR_FINANCE_DRAFT_XLSX_DECISION_RECORD.md | docs/operations/ |
| EMS_PAYMENT_DRAFT_EXPORT_SAFETY_CERTIFICATE.md | docs/operations/ |
| DEMO_LIMITATIONS_AND_DISCLOSURE.md | docs/operations/ |
| FINAL_DEMO_READINESS_CERTIFICATE.md | docs/operations/ |

Backend code inspected:
- `backend/models.py` — Supervision, SupervisionBaseline, PaperDistributionAssignment, ExamSchedule, Room models
- `backend/services/staff_workloads.py` — `assign_paper_distribution_for_period()` function
- `backend/services/invigilation_advance_batch_preview_service.py` — current headcount logic

---

## Clarified Business Rules Received (2026-06-15)

### A. Main Purpose
Supporting finance roster helps finance verify:
- who is counted for payment
- which date/time slot they worked
- whether they are invigilator, room opener, or paper-distribution/open-room support
- how they connect to the signature/payment forms
- how the grouped summary relates back to rooms/courses/sections

### B. Grouping Unit
Main payment counting unit: `exam_date + time_slot + person`

A person is counted **once** per date/time slot even if linked to multiple rooms/courses/sections, unless an approved policy says otherwise.

### C. Actual-Name Rule for Instructors
- Use the name that appears in the actual invigilation field/source
- Do NOT count the same person name twice in the same date/time slot
- Keep all related rooms/courses/sections in trace detail (Sheet 5)
- Count one paid session for that instructor in that slot
- The system must NOT invent instructor names or derive payment names from teaching assignment alone if the name does not appear in the invigilation/source field

### D. Paper-Distribution / Open-Room Mapping Rule
1. Identify eligible physical rooms (non-online) in the slot
2. Rank rooms by student count descending
3. Select top 2 rooms with largest student counts
4. Assign different paper-distribution/open-room staff to different rooms when ≥2 eligible rooms exist
5. If only 1 eligible room: assign 1 person; flag as single-room case
6. Single-room/single-course case: paper-distribution/open-room staff treated as one of the invigilation/open-room persons
7. >2 paper-distribution people: assign first 2, flag rest `EXTRA_PAPER_DISTRIBUTION_REVIEW_REQUIRED`
8. <required people: assign available, flag `MISSING_PAPER_DISTRIBUTION_ASSIGNMENT`

### E. Tie-Breaker for Room Ranking
1. Higher student count (DESC)
2. Room code (ASC)
3. Course code (ASC)
4. Section (ASC)

### F. Online Room Rule
- Online exams must NOT be selected as physical room-opening targets
- Online rows may remain in trace detail (Sheet 5) with flag `TRACE_ONLY_ONLINE_ROW`
- If ALL rows in a date/time slot are online: flag `NO_ELIGIBLE_PHYSICAL_ROOM_FOR_PAPER_MAPPING`
- Do NOT silently attach paper-distribution/open-room staff to online rooms

### G. Finance Output Expectation
Main sheet groups by date/time — not by room/course/section. Trace sheets provide room/course/section detail. Finance avoids manually counting many course/room reimbursement pages.

---

## 5 Open Blockers — Resolution Table

| # | Blocker | Resolution | Evidence |
|---|---------|-----------|---------|
| 1 | Use `Supervision` vs `SupervisionBaseline`? | **Use `Supervision`** (live post-optimize) | `SupervisionBaseline` is immutable historical stats snapshot, created only after 4-signature admin confirm by `_save_baseline_stats()` in `optimize_workflow.py`. Not updated by swaps. Not the source for day-to-day payment roster. |
| 2 | Same person 2 rooms same slot = 1 or 2 paid sessions? | **1 paid session per person per slot** | Clarified by Business Rule B and C. Flag `DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT`. |
| 3 | Finance column order / Thai labels | **Resolved** by updated 5-sheet contract | 5-sheet structure defined with Thai column labels, `สถานะการแมพ` column, NEW signature sheet |
| 4 | `PaperDistributionAssignment` vs `ExamSchedule.paper_distributor` string? | **`PaperDistributionAssignment` is authoritative** | `staff_workloads.py:assign_paper_distribution_for_period()` creates rows per date/time slot. `ExamSchedule.paper_distributor` is a legacy string(200) field populated inconsistently in export code only — NOT used in core assignment logic. |
| 5 | `SupervisionBaseline` preferred over `Supervision`? | **No — use live `Supervision`** | Same as blocker 1. |

**All 5 blockers: RESOLVED. Gate: `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`.**

---

## Backend Source Mapping Summary

| Need | Authoritative Source | Confidence | Included in Export |
|------|---------------------|-----------|-------------------|
| Invigilator persons | `Supervision` — `role_in_exam` in {supervisor, chief} | HIGH | YES — Sheet 2, "กรรมการคุมสอบ" |
| Room opener persons | `Supervision` — `role_in_exam = "room_keeper"`, `slot_order = 99` | HIGH | YES — Sheet 2, "ผู้เปิดห้อง/คุมสอบ" |
| Paper distribution staff | `PaperDistributionAssignment` — `exam_date + exam_time + user_id` | HIGH | YES — Sheets 2, 4 |
| Exam schedule rows | `ExamSchedule` — `exam_date`, `exam_time`, `exam_type`, `status`, `section_id`, `room_id` | HIGH | YES — grouping/trace |
| Student count per section | `Section.num_students` | HIGH | YES — room ranking |
| Physical room identity | `Room.code` where `e_room_code IS NULL` | HIGH | YES — paper-to-room mapping |
| Online room (excluded) | `Room.e_room_code IS NOT NULL` | HIGH | TRACE ONLY — Sheet 5, `TRACE_ONLY_ONLINE_ROW` |
| Post-confirm baseline | `SupervisionBaseline` | HIGH | NOT USED in this export |
| Legacy paper-dist string | `ExamSchedule.paper_distributor` | LOW — legacy | NOT USED |
| `role_in_exam = "distributor"` | `Supervision` enum | UNCERTAIN — no creation code found | TREAT AS INVIGILATION if present; document in Sheet 2 notes |

---

## Updated Export Structure: 5 Sheets

| Sheet | Name | Granularity | Key change vs prior design |
|-------|------|-------------|---------------------------|
| 1 | `สรุปตามวันและช่วงเวลา` | One row per date+time | Unchanged |
| 2 | `รายชื่อประกอบการเบิก` | One row per person per slot | Added `สถานะการแมพ` column; updated role labels |
| 3 | `ใบลงลายมือชื่อประกอบการเบิก` | One row per person per slot | **NEW** — blank signature column for human use |
| 4 | `การผูกคนจ่ายข้อสอบกับห้อง` | One row per paper-dist mapping | Was Sheet 3; added `สถานะการแมพ` column |
| 5 | `รายละเอียดอ้างอิงห้องและวิชา` | One row per source schedule row | Was Sheet 4; renamed |

---

## Map Status Enum

```
MAPPED_TO_TOP_ROOM                         — paper-dist person assigned to rank-1 or rank-2 room
MAPPED_TO_ONLY_ELIGIBLE_ROOM               — only 1 physical room; 1 person assigned
NO_ELIGIBLE_PHYSICAL_ROOM_FOR_PAPER_MAPPING — all rooms in slot are online
MISSING_PAPER_DISTRIBUTION_ASSIGNMENT      — fewer paper-dist persons than needed
EXTRA_PAPER_DISTRIBUTION_REVIEW_REQUIRED   — more than 2 paper-dist persons for slot
DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT — same person across multiple rooms; counted once
SOURCE_NAME_REQUIRED                       — name not in Supervision/PaperDist source (cannot fabricate)
TRACE_ONLY_ONLINE_ROW                      — row excluded from physical mapping; kept in Sheet 5
```

---

## Safety Boundaries (Unchanged)

| Flag | Value |
|------|-------|
| `payment_authorization_enabled` | `false` — hard-coded, never change |
| `final_export_enabled` | `false` — hard-coded, never change |
| `document_status` | `DRAFT_NOT_AUTHORIZED` — every sheet banner |
| `export_status` | `DRAFT_SUPPORTING_EXPORT_ONLY` |
| Final payment approval | BLOCKED |
| Final authorization | BLOCKED |
| Official final export | BLOCKED |
| Teaching workload / Work H | OUT OF SCOPE |
