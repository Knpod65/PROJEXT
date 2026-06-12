# Payment Supporting Finance Roster — Implementation Gate

**Date**: 2026-06-12
**Current gate**: `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION`
**Context**: Draft XLSX format accepted (`DRAFT_XLSX_FORMAT_ACCEPTED`). Supporting finance roster
export design is open. Implementation is blocked pending 5 confirmations from admin/finance.

---

## Gate Decision Options

| Decision | Meaning | Current |
|---|---|---|
| `DOCS_ONLY_DESIGN_NOW` | Contract + algorithm docs produced; no implementation yet | APPLIED (this pass) |
| `IMPLEMENT_SUPPORTING_ROSTER_EXPORT` | All 5 confirmations received; implementation may proceed | BLOCKED |
| `HOLD_PENDING_OPTIMIZE_ROSTER_SOURCE_CONFIRMATION` | 5 open items not yet confirmed | **CURRENT** |
| `HOLD_PENDING_FINANCE_FORMAT_CONFIRMATION` | Finance-preferred column order/labels not confirmed | Subsumed by #3 below |
| `HOLD_PENDING_DATA_SOURCE_MAPPING` | Which model table is authoritative is unclear | Partially resolved |

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

## Confirmations Still Required From Finance/Admin

All 5 must be answered before gate updates to `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`:

| # | Question | Default assumption in design | Who must confirm |
|---|----------|------------------------------|-----------------|
| 1 | Which rows to use for payment roster: live `Supervision` rows (post-optimize, may change until admin confirms) OR immutable `SupervisionBaseline` rows (snapshot after 4-signature admin confirm)? | Use live `Supervision` | Admin |
| 2 | If the same person is assigned to 2 rooms in the same date/time slot, do they count as 1 paid session or 2? | 1 paid session per person per slot | Finance |
| 3 | What is the finance-preferred column order and Thai heading text for the person roster (Sheet 2)? | As defined in PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md | Finance |
| 4 | Are `PaperDistributionAssignment` rows populated in the live database, or do paper-dist persons come only from the `ExamSchedule.paper_distributor` string field? | Use `PaperDistributionAssignment` where rows exist; fall back to `paper_distributor` string field | Admin |
| 5 | Should `SupervisionBaseline` be preferred over live `Supervision` for generating the payment roster? | No — use `Supervision` | Admin |

---

## Implementation Path (After Gate Opens)

Once all 5 confirmations are received and gate updates to `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`:

1. Create `backend/services/payment_supporting_finance_roster_service.py`
   - Implement Steps A–G from `PAYMENT_SUPPORTING_FINANCE_ROSTER_ALGORITHM.md`
   - Use `openpyxl` + `get_column_letter()` (same pattern as `payment_document_draft_export_service.py`)

2. Add endpoint to `backend/routers/invigilation_advance_batch.py`
   ```
   POST /official-finance-support-roster-export
   ```
   Auth: `require_view_all`
   Response: `StreamingResponse` (xlsx)

3. Create `backend/tests/test_payment_supporting_finance_roster.py`
   - Minimum 33 tests per test matrix in `PAYMENT_SUPPORTING_FINANCE_ROSTER_ALGORITHM.md`

4. Add frontend service function `exportFinanceSupportRosterExcel()` to
   `frontend/src/services/officialPaymentDraft.service.ts`

5. Add export button to `frontend/src/pages/OfficialPaymentDocumentDraft.tsx`
   (gated by `ACCEPTED_FOR_DRAFT_EXPORT` status, same as existing export button)

6. Add i18n keys to `frontend/src/i18n/en.ts` and `th.ts`

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
