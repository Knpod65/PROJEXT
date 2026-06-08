# PAYMENT_DOCUMENT_DRAFT_EXPORT_API_CONTRACT.md

**Date**: 2026-06-08
**Pass**: EMS DRAFT PAYMENT DOCUMENT EXPORT IMPLEMENTATION PASS — Phase 4
**Gate status**: `ALLOW_DRAFT_EXPORT_DESIGN`
**Purpose**: Authoritative API contract for the draft export endpoint before implementation.

---

## Endpoint

```
POST /api/invigilation-advance-batch/official-document-draft-export
```

---

## Authentication and Authorization

| Requirement | Value |
|---|---|
| Authentication required | YES — JWT Bearer or HttpOnly `ems_session` cookie |
| Unauthenticated | HTTP 401 |
| Role guard | `require_view_all` |
| Allowed roles | admin, esq_head, secretary |
| Blocked roles | staff (403), teacher (403), print_shop (403), dept_supervisor (403) |

---

## Request

**Content-Type**: `application/json`

**Body schema**: reuses `OfficialPaymentDocumentDraftRequest` from `schemas.py`

```json
{
  "period_id": null,
  "academic_year": "2568",
  "semester": "2",
  "exam_type": "final",
  "paper_distribution_rows": [
    {
      "exam_date": "2568-02-14",
      "exam_time": "09:00-12:00",
      "committee_count": 3,
      "notes": "main building"
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `period_id` | int or null | No | Used to scope term context if provided |
| `academic_year` | string | No | Default "2568" |
| `semester` | string | No | Default "2" |
| `exam_type` | string | No | Default "final" |
| `paper_distribution_rows` | array | No | Same as draft preview; non-persistent |

---

## Gate Checks (Before Generating Output)

The backend derives `document_id` from the request payload:
```
ADVANCE_PAYMENT_DRAFT_SUMMARY:{academic_year}:{semester}:{exam_type}:{period_id|"all"}
```

The following checks are performed in order. The first failure returns an error and no file is generated.

| # | Check | Error Code | Error Detail |
|---|---|---|---|
| 1 | `PaymentDocumentReviewRecord` with `review_status=ACCEPTED_FOR_DRAFT_EXPORT` exists for `document_id` | 400 | export gate: no ACCEPTED_FOR_DRAFT_EXPORT review record for this document |
| 2 | That review record has a non-empty `comment` | 400 | export gate: reviewer comment is required |
| 3 | `settings_source_status == CONFIGURED` | 400 | export gate: settings_source_status must be CONFIGURED |
| 4 | `settings_status == ACTIVE_FOR_DRAFT_PREVIEW` | 400 | export gate: settings_status must be ACTIVE_FOR_DRAFT_PREVIEW |
| 5 | `calculation_status == CALCULATED_FROM_SETTINGS` | 400 | export gate: calculation_status must be CALCULATED_FROM_SETTINGS |
| 6 | `paper_distribution_responsible_group` is non-empty | 400 | export gate: paper_distribution_responsible_group is required |
| 7 | `payment_authorization_enabled == false` | 400 | export gate: payment_authorization_enabled invariant violated |
| 8 | `final_export_enabled == false` | 400 | export gate: final_export_enabled invariant violated |

---

## Success Response

**HTTP 200**
**Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
**Content-Disposition**: `attachment; filename="EMS_DRAFT_PAYMENT_DOCUMENT_{semester}-{academic_year}_{YYYYMMDD_HHMM}.xlsx"`

Example: `attachment; filename="EMS_DRAFT_PAYMENT_DOCUMENT_2-2568_20260608_1430.xlsx"`

**Body**: Binary xlsx stream

---

## Error Responses

| HTTP Code | Condition |
|---|---|
| 400 | Any gate check fails (detail describes which gate) |
| 401 | Not authenticated |
| 403 | Role not in admin/esq_head/secretary |
| 500 | Unexpected server error during workbook generation |

---

## Excel Workbook Structure

**Sheet 1: "ร่างเอกสาร"** (Draft document — main data)

| Row | Content |
|---|---|
| 1 | Thai draft banner: `ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย` (merged, yellow bg, bold) |
| 2 | English draft label: `Draft for review only. Not payment authorization.` (merged, yellow bg) |
| 3 | `DRAFT_NOT_AUTHORIZED` status label (merged, bold) |
| 4 | blank |
| 5 | Document title + term label (e.g., `ภาคการศึกษาที่ 2/2568`) |
| 6 | Rates info: weekday rate / weekend rate / calculation status |
| 7 | Paper distribution responsible group |
| 8 | blank |
| 9 | Column headers (bold, blue background) |
| 10+ | Data rows (alternating fill); sorted by normalized exam date, then time slot |
| N-1 | Totals row (bold, red text) |
| N | Export generation timestamp |

**Columns** (Sheet 1):
1. วันที่สอบ
2. ช่วงเวลา
3. ประเภทวัน (WEEKDAY/WEEKEND/UNKNOWN)
4. จำนวนกรรมการคุมสอบ (int)
5. ค่าตอบแทนคุมสอบ (บาท) (decimal 2dp)
6. จำนวนกรรมการจ่ายข้อสอบ (int)
7. ค่าตอบแทนจ่ายข้อสอบ (บาท) (decimal 2dp)
8. รวมค่าตอบแทน (บาท) (decimal 2dp)

**Sheet 2: "การตรวจร่าง"** (Review record)

| Row | Content |
|---|---|
| 1 | Thai draft banner (same as Sheet 1) |
| 2 | English draft label |
| 3 | blank |
| 4 | Headers: ผู้ตรวจ / บทบาท / สถานะการตรวจ / เวลาตรวจ |
| 5 | Values from the ACCEPTED_FOR_DRAFT_EXPORT review record |
| 6 | blank |
| 7 | Label: ความเห็นผู้ตรวจ |
| 8 | Comment text from review record |
| 9 | blank |
| 10 | แหล่งที่มาการตั้งค่า (settings term, settings status) |
| 11 | เวลาสร้างไฟล์ส่งออก (export generation timestamp) |

---

## What This Endpoint Does NOT Do

| Action | Status |
|---|---|
| Mutate `payment_authorization_enabled` | NEVER — remains false |
| Mutate `final_export_enabled` | NEVER — remains false |
| Mutate `document_status` | NEVER — remains DRAFT_NOT_AUTHORIZED |
| Persist manual paper-distribution rows | NEVER — non-persistent |
| Authorize payment | NEVER |
| Trigger approval workflow | NEVER |
| Write to any database table | NEVER — stateless read-only operation |
| Create official finance record | NEVER |

---

## Frontend Trigger

The export button is visible in `OfficialPaymentDocumentDraft.tsx` only when ALL of:
1. `latestReviewStatus === "ACCEPTED_FOR_DRAFT_EXPORT"`
2. `data !== undefined` (preview has been loaded and returned rows)
3. User role is admin/esq_head/secretary (checked via `canManagePaymentDocumentReview`)

Button is disabled (not just hidden) when `latestReviewStatus !== "ACCEPTED_FOR_DRAFT_EXPORT"`.

**Service function**: `exportOfficialPaymentDraftExcel(payload)` → `post<Blob>(...)`

**Download trigger**: `URL.createObjectURL(blob)` + programmatic anchor click + `URL.revokeObjectURL`

---

## Invariant Confirmation

All invariants from `PAYMENT_DOCUMENT_DRAFT_EXPORT_DESIGN_GATE.md` are enforced:
- Gate check blocks export if any precondition is missing.
- Every sheet in the output contains the Thai + English draft label.
- `DRAFT_NOT_AUTHORIZED` is shown in every sheet header.
- No authorization wording in any output field.
- Export action is stateless — no DB writes.
