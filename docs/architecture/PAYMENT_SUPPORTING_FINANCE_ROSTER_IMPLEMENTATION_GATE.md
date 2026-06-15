# Payment Supporting Finance Roster — Implementation Gate

**Date**: 2026-06-12 (updated 2026-06-15)
**Current gate**: `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`
**Context**: Draft XLSX format accepted (`DRAFT_XLSX_FORMAT_ACCEPTED`). Supporting finance roster
export design complete. All 5 implementation blockers resolved. Implementation may proceed.

---

## Gate Decision Options

| Decision | Meaning | Current |
|---|---|---|
| `DOCS_ONLY_DESIGN_NOW` | Contract + algorithm docs produced; no implementation yet | APPLIED (prior pass 2026-06-12) |
| `IMPLEMENT_SUPPORTING_ROSTER_EXPORT` | All 5 confirmations received; implementation may proceed | **CURRENT (2026-06-15)** |
| `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION` | 5 open items not yet confirmed | CLOSED — all 5 resolved |
| `HOLD_PENDING_FINANCE_FORMAT_CONFIRMATION` | Finance-preferred column order/labels not confirmed | RESOLVED — 5-sheet structure defined |
| `HOLD_PENDING_DATA_SOURCE_MAPPING` | Which model table is authoritative is unclear | RESOLVED — Supervision + PDA confirmed |

---

## Source Confirmations Resolved by Code Inspection (2026-06-12)

The following were confirmed by direct inspection of `backend/models.py` and related services:

| # | Item | Confirmed |
|---|------|-----------|
| ✓ | `Supervision` is the post-optimize invigilation roster source | YES — `supervisions` table, `schedule_id + user_id + role_in_exam` |
| ✓ | `PaperDistributionAssignment` stores paper-dist staff by date/time in a separate table | YES — `paper_distribution_assignments` table, `exam_date + exam_time + user_id` |
| ✓ | `ExamSchedule` has room + student data via Section and Room joins | YES — `section_id → Section.num_students`, `room_id → Room.code` |
| ✓ | Online exams are excluded automatically | YES — no ExamSchedule or Supervision rows created for `exam_type_choice = "online"` |
| ✓ | Online exam flag exists | YES — `ExamSubmission.exam_type_choice` Enum: online/onsite/outside_sched |

---

## Confirmations — ALL 5 RESOLVED (2026-06-15)

| # | Question | Resolution | Evidence |
|---|----------|-----------|---------|
| 1 | Live `Supervision` vs `SupervisionBaseline`? | **Use live `Supervision`** | `SupervisionBaseline` is immutable historical stats; not updated by swaps; created by `_save_baseline_stats()` in `optimize_workflow.py` |
| 2 | Same person, 2 rooms, same slot = 1 or 2 paid sessions? | **1 per person per slot** | Confirmed business rule B/C; flag `DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT` |
| 3 | Finance-preferred column order / Thai labels? | **Resolved** by 5-sheet structure | See `PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md` (updated 2026-06-15) |
| 4 | `PaperDistributionAssignment` rows active in DB? | **YES — PDA is authoritative** | `staff_workloads.py:assign_paper_distribution_for_period()` creates rows; `ExamSchedule.paper_distributor` string is legacy, NOT used |
| 5 | `SupervisionBaseline` preferred for payment? | **No — use live `Supervision`** | Same as item 1 |

**Gate update**: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION` → `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`

---

## Minor Non-Blocking Item

`role_in_exam = "distributor"` exists in the `SupervisionRole` enum (`backend/models.py`) but no
code path was found that creates `Supervision` rows with this role during optimization. If such
rows exist in production data (possible from manual or legacy imports), they should be treated as
invigilation persons and included in the payment count. The algorithm handles this gracefully.

---

## Implementation Path (Gate Open — Ready to Implement)

Gate is now `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`. Full implementation plan in:
`PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_PLAN_READY.md`

Summary:

1. **Backend service**: `backend/services/payment_supporting_finance_roster_service.py`
   - Pattern: same as `payment_document_draft_export_service.py`
   - Implements Steps A–G from `PAYMENT_SUPPORTING_FINANCE_ROSTER_ALGORITHM.md`
   - Uses `get_column_letter()` from `openpyxl.utils` (MergedCell safety)

2. **Endpoint**: `POST /official-finance-support-roster-export`
   in `backend/routers/invigilation_advance_batch.py`
   Auth: `require_view_all` — Response: `StreamingResponse` (xlsx)

3. **Tests**: `backend/tests/test_payment_supporting_finance_roster.py`
   Minimum 43 tests per updated test matrix

4. **Frontend service**: `exportFinanceSupportRosterExcel()` in
   `frontend/src/services/officialPaymentDraft.service.ts`

5. **Frontend page**: second export button in `OfficialPaymentDocumentDraft.tsx`
   (gated by `ACCEPTED_FOR_DRAFT_EXPORT`, after existing export button)

6. **i18n**: 4 keys per language in `frontend/src/i18n/en.ts` and `th.ts`

7. Run full backend test suite, frontend build, i18n parity check

---

## Safety Invariants (Must Never Change)

| Flag | Required value |
|------|---------------|
| `payment_authorization_enabled` | `false` |
| `final_export_enabled` | `false` |
| `document_status` | `DRAFT_NOT_AUTHORIZED` |
| `export_status` | `DRAFT_SUPPORTING_EXPORT_ONLY` |

---

## Blocked Items (Unaffected by This Gate)

| Item | Status |
|------|--------|
| Final payment approval | BLOCKED — requires separate final authorization gate |
| Official final export | BLOCKED |
| Payment release workflow | BLOCKED |
| Final authorization design | `FINAL_AUTHORIZATION_DESIGN_BLOCKED` (unchanged) |
| Production readiness | UNCHANGED |

---

## What This Gate Does NOT Do

- Does not implement the supporting roster export.
- Does not authorize payment.
- Does not change `payment_authorization_enabled` or `final_export_enabled`.
- Does not open final authorization design.
- Does not substitute for admin/finance confirmation of items 1–5.
