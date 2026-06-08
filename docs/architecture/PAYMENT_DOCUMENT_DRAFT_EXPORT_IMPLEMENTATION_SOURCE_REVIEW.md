# PAYMENT_DOCUMENT_DRAFT_EXPORT_IMPLEMENTATION_SOURCE_REVIEW.md

**Date**: 2026-06-08
**Pass**: EMS DRAFT PAYMENT DOCUMENT EXPORT IMPLEMENTATION PASS — Phase 2
**Gate status at review time**: `ALLOW_DRAFT_EXPORT_DESIGN` (confirmed in PAYMENT_DOCUMENT_DRAFT_EXPORT_GATE_REEVALUATION.md)
**Purpose**: Authoritative source review before any export code is written. Records every constraint, invariant, and API fact that governs implementation.

---

## Source Documents Reviewed

| Document | Key Fact Extracted |
|---|---|
| `PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md` | Gate `ALLOW_DRAFT_EXPORT_DESIGN`; 10 preconditions all PASS; export format Excel `.xlsx` primary |
| `PAYMENT_DOCUMENT_DRAFT_EXPORT_GATE_REEVALUATION.md` | All 10 preconditions PASS via live API; review_id 4 is the authoritative acceptance record |
| `PAYMENT_DOCUMENT_DRAFT_EXPORT_TEST_MATRIX.md` | 57 tests across 8 categories; Categories 1 and 5 are the gate-blocking backend tests |
| `PAYMENT_DOCUMENT_DRAFT_EXPORT_REQUIREMENTS_CHECKLIST.md` | Thai-first labels required; draft watermark mandatory on every sheet; settings metadata required in output |
| `PAYMENT_DOCUMENT_SETTINGS_DRAFT_INTEGRATION_CONTRACT.md` | `settings_source_status=CONFIGURED` + `settings_status=ACTIVE_FOR_DRAFT_PREVIEW` → `CALCULATED_FROM_SETTINGS` |
| `PAYMENT_DOCUMENT_REVIEW_WORKFLOW_MODEL.md` | `ACCEPTED_FOR_DRAFT_EXPORT` is non-authorizing; review_id must have a non-empty comment |
| `ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md` | 8 output columns; group-by exam_date + time_slot; DRAFT watermark in header |

---

## Code Inspection Findings

### Backend

| Component | Finding | Implication for Export |
|---|---|---|
| `official_payment_document_draft_service.py` | `build_official_payment_document_draft_preview(db, payload)` returns complete metadata, rows, totals, warnings | Export service calls this and builds workbook from result |
| `payment_document_review_service.py` | `list_payment_document_reviews` queries by `document_id`; `ACCEPTED_FOR_DRAFT_EXPORT` is a valid status | Gate check queries for any record with this status + non-empty comment |
| `routers/invigilation_advance_batch.py` | 44 lines; 2 endpoints; `require_staff_or_admin` on both | New export endpoint uses `require_view_all` (admin/esq_head/secretary) |
| `auth_utils.py` | `require_view_all` allows admin/esq_head/secretary; blocks staff/teacher/print_shop | Correct role guard for export (matches test matrix T-ROLE-001 to T-ROLE-007) |
| `requirements.txt` | `openpyxl >= 3.1.0` confirmed | Excel generation confirmed available |
| `services/export_excel_service.py` | openpyxl with styled headers, PatternFill, Font, merged cells, BytesIO → StreamingResponse | Export service follows same pattern |
| `schemas.py` | `OfficialPaymentDocumentDraftRequest` already exists and matches export input requirements | Reuse existing request schema; no new input schema needed |

### Frontend

| Component | Finding | Implication for Export |
|---|---|---|
| `OfficialPaymentDocumentDraft.tsx` | 496 lines; `latestReviewStatus` from `reviewRecords.latestRecord?.review_status` | Export button visible only when `latestReviewStatus === "ACCEPTED_FOR_DRAFT_EXPORT"` AND `data !== undefined` |
| `officialPaymentDraft.service.ts` | 9 lines; single `previewOfficialPaymentDraft` function using `post<T>` | New `exportOfficialPaymentDraftExcel` function using `post<Blob>` |
| `services/api.ts` | `parseResponse` falls through to `response.blob()` for non-JSON/text content | `post<Blob>(...)` correctly returns a Blob for xlsx response |
| `i18n/en.ts` + `th.ts` | `paymentDraft.actions.preview` exists; no export keys yet | 4 new i18n keys needed |
| `canManagePaymentDocumentReview` in `permissions.ts` | Restricts to admin/esq_head/secretary | Reuse for export button visibility check |

---

## Document ID Construction

Both backend and frontend construct the document ID identically:

```
ADVANCE_PAYMENT_DRAFT_SUMMARY:{academic_year}:{semester}:{exam_type}:{period_id|"all"}
```

Backend export gate check constructs this from the request payload to query review records.

---

## Safety Invariants (Must Never Change)

These values must be verified before generating any export output and must never appear as `true` in exported data:

| Invariant | Source | Check Location |
|---|---|---|
| `payment_authorization_enabled = false` | Draft response from service | Backend gate check |
| `final_export_enabled = false` | Draft response from service | Backend gate check |
| `document_status = DRAFT_NOT_AUTHORIZED` | Metadata from service | Included in every sheet header |
| `calculation_status = CALCULATED_FROM_SETTINGS` | Metadata from service | Backend gate check |
| `settings_source_status = CONFIGURED` | Metadata from service | Backend gate check |
| `settings_status = ACTIVE_FOR_DRAFT_PREVIEW` | Metadata from service | Backend gate check |

---

## Export Gate Checks (Backend — Per Test Matrix Category 1)

| Check | Test ID | Error Code | Error Message |
|---|---|---|---|
| Review record with `ACCEPTED_FOR_DRAFT_EXPORT` exists for document_id | T-EXP-001 | 400 | export gate: no ACCEPTED_FOR_DRAFT_EXPORT review record for this document |
| Reviewer comment is non-empty in that record | T-EXP-005 | 400 | export gate: reviewer comment is required |
| `settings_source_status == CONFIGURED` | T-EXP-002 | 400 | export gate: settings_source_status must be CONFIGURED |
| `settings_status == ACTIVE_FOR_DRAFT_PREVIEW` | T-EXP-003 | 400 | export gate: settings_status must be ACTIVE_FOR_DRAFT_PREVIEW |
| `calculation_status == CALCULATED_FROM_SETTINGS` | T-EXP-004 | 400 | export gate: calculation_status must be CALCULATED_FROM_SETTINGS |
| `paper_distribution_responsible_group` non-empty | T-EXP-006 | 400 | export gate: paper_distribution_responsible_group is required |
| `payment_authorization_enabled == false` | T-EXP-007 | 400 | export gate: payment_authorization_enabled invariant violated |
| `final_export_enabled == false` | T-EXP-008 | 400 | export gate: final_export_enabled invariant violated |

---

## Required Export Output Content (Per Design Gate)

### Excel Workbook Sheets

**Sheet 1 — "ร่างเอกสาร" (Draft Document)**
- Row 1: Thai draft banner (merged, yellow background, bold)
- Row 2: English draft label
- Row 3: `DRAFT_NOT_AUTHORIZED` status
- Row 5: Document title + term label
- Row 6: Weekday rate, weekend rate, calculation status
- Row 7: Paper distribution responsible group
- Row 8: blank
- Row 9: Column headers (bold, blue background)
- Row 10+: Data rows (alternating fill)
- Totals row (red bold)
- Generation timestamp row at bottom

**Columns** (per ADVANCE_BATCH_OFFICIAL_DOCUMENT_OUTPUT_REQUIREMENTS.md):
1. วันที่สอบ
2. ช่วงเวลา
3. ประเภทวัน
4. จำนวนกรรมการคุมสอบ
5. ค่าตอบแทนคุมสอบ (บาท)
6. จำนวนกรรมการจ่ายข้อสอบ
7. ค่าตอบแทนจ่ายข้อสอบ (บาท)
8. รวมค่าตอบแทน (บาท)

**Sheet 2 — "การตรวจร่าง" (Review Record)**
- Thai draft banner
- Reviewer name, role, review status, reviewed_at
- Review comment
- Review decision
- Settings source reference
- Export generation timestamp

---

## Filename Convention

```
EMS_DRAFT_PAYMENT_DOCUMENT_{semester}-{academic_year}_{YYYYMMDD_HHMM}.xlsx
```

Example: `EMS_DRAFT_PAYMENT_DOCUMENT_2-2568_20260608_1430.xlsx`

---

## Role Permissions for Export (Per Test Matrix Category 5)

| Role | Allowed | HTTP Code |
|---|---|---|
| admin | YES | 200 |
| esq_head | YES | 200 |
| secretary | YES | 200 |
| staff | NO | 403 |
| teacher | NO | 403 |
| print_shop | NO | 403 |
| unauthenticated | NO | 401 |

Role guard: `require_view_all` from `auth_utils.py` (admin/esq_head/secretary).

---

## What This Review Confirms

1. The `build_official_payment_document_draft_preview` function provides all required data for export.
2. The `require_view_all` role guard matches the test matrix role requirements exactly.
3. `openpyxl` is available in requirements.txt.
4. The `post<Blob>` pattern works in the frontend API service via `parseResponse` blob fallback.
5. No new database models are needed; export is stateless (no write operations on export action).
6. `OfficialPaymentDocumentDraftRequest` schema can be reused for the export endpoint without modification.
7. All 8 gate checks from the test matrix can be implemented against the draft response metadata.

---

## Hard Rules Carried Forward

- Export must NOT mutate `payment_authorization_enabled`, `final_export_enabled`, `document_status`.
- Export must NOT persist manual paper-distribution rows.
- Export must NOT succeed if gate check fails.
- Export file must display Thai draft label on every sheet.
- Export file must include review metadata.
- Export file must include settings source metadata.
- Role guard must block staff, teacher, and print_shop.
