# Payment Document Draft Export — API Contract

**Date**: 2026-06-11

## Endpoint

```
POST /api/invigilation-advance-batch/official-document-draft-export
```

## Authentication

`require_view_all` — admin / esq_head / secretary allowed. All other roles receive HTTP 403.

## Request Body

Reuses `OfficialPaymentDocumentDraftRequest` (same as preview endpoint):

```json
{
  "period_id": null,
  "academic_year": "2568",
  "semester": "2",
  "exam_type": "final",
  "paper_distribution_rows": []
}
```

| Field | Type | Notes |
|---|---|---|
| `period_id` | int \| null | Optional; `null` → document_id uses `"all"` |
| `academic_year` | string | Buddhist Era year, e.g. `"2568"` |
| `semester` | string | `"1"` or `"2"` |
| `exam_type` | string | `"final"`, `"midterm"`, etc. |
| `paper_distribution_rows` | array | Optional manual rows (draft-labeled, not persisted) |

## Response — Success (HTTP 200)

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="EMS_DRAFT_PAYMENT_DOCUMENT_2-2568_20260611_1430.xlsx"
```

Binary xlsx stream. No JSON body.

## Response — Error (HTTP 400 / 403)

```json
{ "detail": "<reason string>" }
```

## Gate Checks (8 preconditions, checked in order)

| # | Check | Fail → HTTP 400 detail |
|---|---|---|
| 1 | `PaymentDocumentReviewRecord` with `document_id` matching request and `review_status = ACCEPTED_FOR_DRAFT_EXPORT` exists | `"No ACCEPTED_FOR_DRAFT_EXPORT review record found..."` |
| 2 | Review record `comment` is non-empty | `"Review record comment is required for export but is empty."` |
| 3 | `draft.metadata.settings_source_status == CONFIGURED` | `"settings_source_status must be CONFIGURED"` |
| 4 | `draft.metadata.settings_status == ACTIVE_FOR_DRAFT_PREVIEW` | `"settings_status must be ACTIVE_FOR_DRAFT_PREVIEW"` |
| 5 | `draft.metadata.calculation_status == CALCULATED_FROM_SETTINGS` | `"calculation_status must be CALCULATED_FROM_SETTINGS"` |
| 6 | `draft.metadata.paper_distribution_responsible_group` is non-empty | `"paper_distribution_responsible_group must be set in settings"` |
| 7 | `draft.payment_authorization_enabled == False` | `"payment_authorization_enabled must be false"` |
| 8 | `draft.final_export_enabled == False` | `"final_export_enabled must be false"` |

## Document ID Construction

The service constructs `document_id` from request payload — same formula as frontend:

```
ADVANCE_PAYMENT_DRAFT_SUMMARY:{academic_year}:{semester}:{exam_type}:{period_id|"all"}
```

Example: `ADVANCE_PAYMENT_DRAFT_SUMMARY:2568:2:final:all`

## Workbook Structure

### Sheet 1 — "ร่างเอกสาร"

| Row | Content |
|---|---|
| 1 | Thai draft banner (YELLOW background, bold): `ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย` |
| 2 | English draft banner: `Draft for review only. Not payment authorization.` |
| 3 | Status: `DRAFT_NOT_AUTHORIZED` |
| 5 | Document title: `สรุปจำนวนกรรมการและค่าตอบแทน รายวัน/ช่วงเวลา` |
| 6 | Academic term |
| 7 | Weekday / weekend rates from settings |
| 8 | Paper-distribution responsible group |
| 9 | Column headers (bold) |
| 10+ | Data rows: วันที่สอบ, ช่วงเวลา, ประเภทวัน, จำนวนกรรมการคุมสอบ, ค่าตอบแทนคุมสอบ, จำนวนกรรมการจ่ายข้อสอบ, ค่าตอบแทนจ่ายข้อสอบ, รวมค่าตอบแทน, อัตรา |
| last data+1 | Totals row (bold) |
| last+3 | Footer draft label (YELLOW): `เอกสารนี้เป็นร่างเพื่อการตรวจทาน ไม่ใช่เอกสารอนุมัติเบิกจ่าย` |

### Sheet 2 — "การตรวจร่าง"

Review metadata: reviewer name, role, review status, reviewed_at, comment, settings source reference, settings status, calculation status, safety flags, generation timestamp.

## Filename Convention

```
EMS_DRAFT_PAYMENT_DOCUMENT_{semester}-{academic_year}_{YYYYMMDD_HHMM}.xlsx
```

Example: `EMS_DRAFT_PAYMENT_DOCUMENT_2-2568_20260611_1430.xlsx`

## Role Access Table

| Role | Access |
|---|---|
| admin | HTTP 200 — export allowed |
| esq_head | HTTP 200 — export allowed |
| secretary | HTTP 200 — export allowed |
| staff | HTTP 403 |
| teacher | HTTP 403 |
| print_shop | HTTP 403 |
| unauthenticated | HTTP 401 / 422 |

## Safety Invariants

- `payment_authorization_enabled` is never set to `true` by this endpoint.
- `final_export_enabled` is never set to `true` by this endpoint.
- No DB writes occur during export.
- `document_status` remains `DRAFT_NOT_AUTHORIZED`.
- Manual paper-distribution rows are not persisted.
- Export does not create or modify any review record.
