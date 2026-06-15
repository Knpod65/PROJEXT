# Payment Supporting Finance Roster — Implementation Plan (READY)

**Date**: 2026-06-15
**Gate**: `IMPLEMENT_SUPPORTING_ROSTER_EXPORT`
**Status**: IMPLEMENTED AND VALIDATED
**Reviewer identity**: NOT_PROVIDED

---

## Gate Confirmation

All 5 implementation blockers resolved as of 2026-06-15. See:
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_POLICY_CLARIFICATION_SOURCE_REVIEW.md`
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md`
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_MAPPING_DECISION.md`

Safety flags unchanged:
- `payment_authorization_enabled = false`
- `final_export_enabled = false`
- `document_status = DRAFT_NOT_AUTHORIZED`
- `export_status = DRAFT_SUPPORTING_EXPORT_ONLY`

---

## Workbook Output: 5 Sheets

| # | Sheet name | Granularity |
|---|-----------|-------------|
| 1 | `สรุปตามวันและช่วงเวลา` | One row per date+time slot |
| 2 | `รายชื่อประกอบการเบิก` | One row per person per slot |
| 3 | `ใบลงลายมือชื่อประกอบการเบิก` | One row per person per slot (signature sheet) |
| 4 | `การผูกคนจ่ายข้อสอบกับห้อง` | One row per paper-dist-to-room assignment |
| 5 | `รายละเอียดอ้างอิงห้องและวิชา` | One row per source ExamSchedule row |

---

## Backend Service

**File**: `backend/services/payment_supporting_finance_roster_service.py`

**Pattern**: Same as `payment_document_draft_export_service.py` (StreamingResponse + BytesIO + openpyxl)

**Key functions**:

| Function | Purpose |
|----------|---------|
| `_build_slot_groups(db, scope)` | Step A+B: Filter eligible ExamSchedule rows; group by date/time |
| `_build_person_rows(db, slot_groups)` | Step C: Collect Supervision rows per slot; dedup by user_id; map_status |
| `_build_paper_to_room_rows(db, slot_groups)` | Step D: PDA rows per slot; rank physical rooms; assign; map_status |
| `_build_signature_rows(person_rows)` | Derive Sheet 3 from Step C+D output (blank signature col) |
| `_build_trace_rows(db, slot_groups)` | Step A: All eligible ExamSchedule rows including online (TRACE_ONLY_ONLINE_ROW) |
| `_compute_headcount_and_amounts(person_rows, paper_rows, settings)` | Step E: inv_count, paper_count, rates, amounts |
| `_build_workbook(slot_summary, person_rows, signature_rows, paper_rows, trace_rows)` | Step F: Build 5-sheet xlsx workbook |
| `generate_finance_support_roster_xlsx(db, scope, batch_review)` | Top-level entry point: gate check → steps A–G → StreamingResponse |

**Critical rules**:
- `get_column_letter(col_idx)` from `openpyxl.utils` — do NOT use `ws.cell(1, col).column_letter` on merged cells
- `payment_authorization_enabled = False` hard-coded — never derive from input
- `final_export_enabled = False` hard-coded — never derive from input
- `DRAFT_NOT_AUTHORIZED` banner on every sheet rows 1–3
- Physical room: `Room.e_room_code IS NULL`
- Online room: `Room.e_room_code IS NOT NULL` → excluded from mapping, `TRACE_ONLY_ONLINE_ROW` in Sheet 5
- Person names from `User.full_name` via FK only — never derived from instructor/course fields
- Dedup invigilation persons by `user_id` within slot — count = 1 per person per slot

**Paper distribution source**: `PaperDistributionAssignment` ONLY
- `ExamSchedule.paper_distributor` string field is NOT used
- `PaperDistributionAssignment` rows created by `staff_workloads.py:assign_paper_distribution_for_period()`

**Invigilation source**: `Supervision` (live, post-optimize)
- `SupervisionBaseline` is NOT used (historical stats snapshot only)

**Role mapping** (`Supervision.role_in_exam` → Thai label):
| role_in_exam | บทบาทในช่วงเวลานี้ |
|---|---|
| supervisor | กรรมการคุมสอบ |
| chief | กรรมการคุมสอบ (หัวหน้า) |
| room_keeper | ผู้เปิดห้อง/คุมสอบ |
| distributor | กรรมการคุมสอบ (distributor) |

Paper-dist persons (PDA source): บทบาท = กรรมการจ่ายข้อสอบ/เปิดห้อง

---

## Endpoint

**File**: `backend/routers/invigilation_advance_batch.py`

**Location**: After the existing `official-document-draft-export` endpoint

```
POST /api/invigilation-advance-batch/finance-support-roster-export
```

**Auth**: `require_view_all` (admin/esq_head/secretary → pass; staff/teacher/print_shop → 403)

**Request body**: same schema as draft export (academic_year, semester, exam_type, period_id)

**Response**: `StreamingResponse` with `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

**Filename**: `EMS_DRAFT_FINANCE_ROSTER_{semester}-{academic_year}_{YYYYMMDD_HHMM}.xlsx`

**Gate check** (same 8 preconditions as contract doc):
1. Review status = `ACCEPTED_FOR_DRAFT_EXPORT` with non-empty comment
2. Settings source status = `CONFIGURED`
3. Settings status = `ACTIVE_FOR_DRAFT_PREVIEW`
4. Calculation status = `CALCULATED_FROM_SETTINGS`
5. Paper distribution responsible group non-empty
6. `payment_authorization_enabled = false`
7. `final_export_enabled = false`
8. At least one `Supervision` row for the scope

Any failure → HTTP 400 with specific error message. Do not generate partial xlsx.

---

## Tests

**File**: `backend/tests/test_payment_supporting_finance_roster.py`

**Pattern**: Same as `test_payment_document_draft_export.py`

**Minimum 43 tests** per updated test matrix:

| Category | Count | Key scenarios |
|----------|-------|--------------|
| Gate-block | 8 | One per precondition failure → HTTP 400 |
| Role access | 7 | admin/esq_head/secretary → 200+xlsx; staff/teacher/print_shop → 403; unauth → 401 |
| Sheet structure | 5 | Verify 5 sheets with correct Thai names |
| Safety flags | 4 | payment_authorization_enabled=false, final_export_enabled=false, DRAFT_NOT_AUTHORIZED banner, no mutation |
| Paper-to-room | 5 | MAPPED_TO_TOP_ROOM (2 rooms), MAPPED_TO_ONLY_ELIGIBLE_ROOM (1 room), NO_ELIGIBLE_PHYSICAL_ROOM (0 rooms), extra persons, missing persons |
| Person dedup | 3 | Same user_id, 2 rooms → count=1, DUPLICATE flag, rooms listed |
| Online-room exclusion | 2 | Online rooms not mapped; TRACE_ONLY_ONLINE_ROW in Sheet 5 |
| map_status | 4 | Correct status per case; SOURCE_NAME_REQUIRED on null user_id |
| Signature sheet | 3 | Sheet 3 rows match Sheet 2; signature column blank; banner present |
| Content type | 2 | Content-Type xlsx; Content-Disposition matches filename pattern |

---

## Frontend Service

**File**: `frontend/src/services/officialPaymentDraft.service.ts`

**Add function**:
```typescript
exportFinanceSupportRosterExcel(params: DraftExportParams): Promise<Blob>
```

Pattern: same as existing `exportDraftDocumentExcel()` — POST to the new endpoint, return blob.

---

## Frontend Page

**File**: `frontend/src/pages/OfficialPaymentDocumentDraft.tsx`

**Change**: Add a second export button after the existing draft-export button.

- Label (from i18n): "ดาวน์โหลดรายชื่อประกอบการเบิก (ร่าง)"
- Enabled condition: same as first button (`ACCEPTED_FOR_DRAFT_EXPORT` status, non-null batch)
- Click handler: calls `exportFinanceSupportRosterExcel()`, triggers file download
- Loading state: separate from existing button

---

## i18n Keys

**Files**: `frontend/src/i18n/en.ts` and `frontend/src/i18n/th.ts`

| Key | English | Thai |
|-----|---------|------|
| `payment.financeRosterExport.button` | Download Finance Roster (Draft) | ดาวน์โหลดรายชื่อประกอบการเบิก (ร่าง) |
| `payment.financeRosterExport.loading` | Generating roster... | กำลังสร้างรายชื่อ... |
| `payment.financeRosterExport.success` | Finance roster downloaded | ดาวน์โหลดรายชื่อสำเร็จ |
| `payment.financeRosterExport.error` | Failed to download roster | ดาวน์โหลดรายชื่อไม่สำเร็จ |

---

## Map Status Enum (reference)

```
MAPPED_TO_TOP_ROOM
MAPPED_TO_ONLY_ELIGIBLE_ROOM
NO_ELIGIBLE_PHYSICAL_ROOM_FOR_PAPER_MAPPING
MISSING_PAPER_DISTRIBUTION_ASSIGNMENT
EXTRA_PAPER_DISTRIBUTION_REVIEW_REQUIRED
DUPLICATE_PERSON_COLLAPSED_TO_ONE_PAYMENT_COUNT
SOURCE_NAME_REQUIRED
TRACE_ONLY_ONLINE_ROW
```

---

## Safety Invariants (Must Never Change)

| Flag | Value | Enforcement |
|------|-------|-------------|
| `payment_authorization_enabled` | `false` | Hard-coded in service; gate rejects if True |
| `final_export_enabled` | `false` | Hard-coded in service; gate rejects if True |
| `document_status` | `DRAFT_NOT_AUTHORIZED` | Banner row on every sheet |
| `export_status` | `DRAFT_SUPPORTING_EXPORT_ONLY` | Sheet 2 metadata block |

---

## Blocked Items (Not Implemented Here)

| Item | Status |
|------|--------|
| Final payment approval | BLOCKED |
| Official final export | BLOCKED |
| Payment authorization | BLOCKED |
| Teaching workload / Work H / opencourse / coinstruc | Out of scope |
| Changing rate/settings logic | Out of scope |
| Changing review gate logic | Out of scope |

---

## Related Documents

- `PAYMENT_SUPPORTING_FINANCE_ROSTER_EXPORT_CONTRACT.md` — full sheet specification
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_ALGORITHM.md` — step-by-step algorithm with map_status enum
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_IMPLEMENTATION_GATE.md` — gate status: IMPLEMENT
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_POLICY_CLARIFICATION_SOURCE_REVIEW.md` — clarified rules A–G
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_MAPPING_DECISION.md` — per-source confidence table
- `PAYMENT_SUPPORTING_FINANCE_ROSTER_SOURCE_REVIEW.md` — original source table review
