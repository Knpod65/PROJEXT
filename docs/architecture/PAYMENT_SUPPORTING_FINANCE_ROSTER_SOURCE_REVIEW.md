# Payment Supporting Finance Roster — Source Review

**Date**: 2026-06-12
**Pass**: Accept RC1 Draft XLSX + Design Supporting Finance Roster Export
**Gate status applied**: `DRAFT_XLSX_FORMAT_ACCEPTED` (decision recorded 2026-06-12)

---

## Docs Read In This Pass

| Document | Location |
|---|---|
| EMS_SUPERVISOR_FINANCE_DRAFT_XLSX_DECISION_RECORD.md | docs/operations/ |
| PAYMENT_DOCUMENT_DRAFT_XLSX_FORMAT_DECISION_GATE.md | docs/architecture/ |
| EMS_POST_RC1_NEXT_PHASE_DECISION_MATRIX.md | docs/architecture/ |
| PAYMENT_DOCUMENT_IN_SYSTEM_REVIEW_CHECKLIST_MODEL.md | docs/architecture/ |
| EMS_RC1_IN_SYSTEM_CHECKLIST_COMPLETION_REPORT.md | docs/operations/ |
| EMS_DRAFT_XLSX_VISUAL_EVIDENCE_RC1.md | docs/operations/ |
| EMS_PAYMENT_DRAFT_EXPORT_SAFETY_CERTIFICATE.md | docs/operations/ |
| PAYMENT_DOCUMENT_DRAFT_EXPORT_API_CONTRACT.md | docs/architecture/ |
| PAYMENT_DOCUMENT_DRAFT_EXPORT_IMPLEMENTATION_VALIDATION_LOG.md | docs/architecture/ |
| ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md | docs/architecture/ |
| OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md | docs/architecture/ |
| DEMO_LIMITATIONS_AND_DISCLOSURE.md | docs/operations/ |

---

## Accepted RC1 Draft XLSX Decision

| Item | Value |
|---|---|
| Previous gate | `HOLD_PENDING_ADDITIONAL_REVIEW` |
| New decision | `ACCEPT_DRAFT_XLSX_FORMAT` |
| New format gate | `DRAFT_XLSX_FORMAT_ACCEPTED` |
| Reviewer identity | `NOT_PROVIDED` |
| Final authorization gate | `FINAL_AUTHORIZATION_DESIGN_BLOCKED` (unchanged) |
| Supporting requirement now open | `SUPPORTING_FINANCE_INVIGILATION_ROSTER_REQUIRED` |

Acceptance of the draft XLSX format is **not payment authorization**. The accepted RC1 summary
XLSX is a review-only draft. A supporting finance roster export is required before finance can
comfortably verify signatures and headcounts.

---

## Confirmed Source Tables (from backend code inspection)

| Need | Model / Table | Key fields | Notes |
|------|--------------|-----------|-------|
| Optimized invigilation assignments | `Supervision` | `schedule_id`, `user_id`, `role_in_exam` (supervisor/chief/distributor), `compensation` | Primary post-optimize roster source |
| Post-confirm immutable baseline | `SupervisionBaseline` | `user_id`, `schedule_id`, `confirmed_at` | Created after 4-signature admin confirm; immutable |
| Paper distribution staff | `PaperDistributionAssignment` | `exam_date`, `exam_time`, `user_id`, `duty_type=PAPER_DISTRIBUTION`, `workload_units` | Separate table; one person per date/time slot |
| Exam schedule + room + students | `ExamSchedule` | `section_id → Section.num_students`, `room_id → Room`, `exam_date`, `exam_time`, `exam_type`, `status` | Join to Section for num_students; join to Room for capacity |
| Room identity | `Room` | `id`, `code`, `capacity` | Physical room reference |
| Section / course | `Section` | `num_students`, `is_co_exam`, `course_id` | Course + section data |
| Online exam flag | `ExamSubmission.exam_type_choice = "online"` | Enum: online / onsite / outside_sched | No ExamSchedule or Supervision rows are created for online exams — excluded automatically |
| External exams | `ExternalExam` | `exam_date`, `exam_time`, `num_students`, `invigilators_needed` | CMU centralized / placement tests — handled separately |

**Key workflow**: After optimize runs → admin confirms with 4 signatures → `SupervisionBaseline`
snapshot is created. `Supervision` rows remain active for day-to-day use. The correct source for
the payment roster depends on which snapshot is authoritative for finance (see uncertainties below).

---

## Current Export / Draft Service Behavior

The existing RC1 summary XLSX endpoint (`POST /api/invigilation-advance-batch/official-document-draft-export`):
- Calls `build_official_payment_document_draft_preview` to produce aggregated day/time-slot totals
- Returns slot-level counts (inv_count, paper_count, amounts) aggregated by exam_date + time_slot
- Does NOT return person-level names or room-level detail
- Does NOT bind paper-distribution persons to specific rooms
- Safety flags: `payment_authorization_enabled=false`, `final_export_enabled=false`, `DRAFT_NOT_AUTHORIZED`

The new supporting roster export must go deeper: person names, room assignments, paper-to-room binding.

---

## Gap Analysis: RC1 Summary XLSX vs Finance Roster Need

| Finance need | In RC1 summary XLSX | In new supporting roster |
|---|---|---|
| Slot-level invigilation count | YES | YES (repeated) |
| Person names per slot | NO | YES — Sheet 2 |
| Role per person (chief/supervisor/distributor) | NO | YES — Sheet 2 |
| Room per person | NO | YES — Sheet 2, 3 |
| Paper-distribution person bound to specific room | NO | YES — Sheet 3 |
| Room-level student count for top-2 room selection | NO | YES — Sheet 3 |
| Source room/course/section trace | NO | YES — Sheet 4 |
| Signature check column per person | NO | YES — Sheet 2 |

---

## Online Exam Handling

- Online exams do not create `ExamSchedule` rows. No `Supervision` rows exist for online exams.
- Online exams are therefore excluded from the physical invigilation roster automatically.
- If source data includes `ExternalExam` or `ExamSubmission.exam_type_choice="online"` entries,
  document their exclusion in Sheet 4 trace with reason "online — no physical room assignment".
- This policy must be confirmed by finance/admin before implementation.

---

## Remaining Uncertainties Before Implementation

| # | Uncertainty | Impact |
|---|---|---|
| 1 | Which `Supervision` rows to use: live-draft rows vs `SupervisionBaseline` immutable snapshot? | Determines roster source query |
| 2 | Duplicate-person-in-slot policy: one paid session per person per slot, or per room? | Affects Sheet 2 payment count and Sheet 1 total |
| 3 | Finance-preferred column order and Thai heading labels (column structure confirmed in contract; ordering to be verified) | Sheet layout |
| 4 | `PaperDistributionAssignment` vs `ExamSchedule.paper_distributor` string field: which is authoritative for person identity? | Paper-dist person source |
| 5 | Whether `SupervisionBaseline` is preferred over live `Supervision` for payment roster generation | Roster query |

All five must be confirmed by admin/finance before implementation begins.

---

## Safety Boundaries

| Invariant | Status |
|---|---|
| `payment_authorization_enabled` | `false` — must never be changed |
| `final_export_enabled` | `false` — must never be changed |
| `document_status` | `DRAFT_NOT_AUTHORIZED` — must appear on every output sheet |
| Export type | `DRAFT_SUPPORTING_EXPORT_ONLY` — not final, not authorizing |
| Final payment approval | BLOCKED |
| Final authorization workflow | BLOCKED |
| Official final export | BLOCKED |
| Teaching workload / Work H / opencourse / coinstruc | OUT OF SCOPE — do not touch |

---

## Implementation Gate Status

Gate: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`

Five source/policy confirmations required from finance/admin before implementation begins.
See `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md` for full gate record.
