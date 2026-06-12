# Payment Document In-System Review Checklist Model

**Date**: 2026-06-12
**Decision gate**: `HOLD_PENDING_ADDITIONAL_REVIEW`

## Purpose

The checklist guides a supervisor/finance reviewer through the evidence required to decide on the RC1 draft XLSX format. It creates an auditable inspection trail while remaining separate from payment authorization and the explicit XLSX format decision.

## Ordered Default Items

| Order | Item key | English label | Thai label |
|---:|---|---|---|
| 1 | `CHECK_PAYMENT_DOCUMENT_SETTINGS` | Check Payment Document Settings | ตรวจสอบหน้าตั้งค่าเอกสารค่าตอบแทน |
| 2 | `CHECK_OFFICIAL_PAYMENT_DOCUMENT_DRAFT` | Check Official Payment Document Draft | ตรวจสอบหน้าร่างเอกสารเบิกจ่าย |
| 3 | `CHECK_REVIEW_PANEL_STATUS` | Check Review Panel and draft-export review status | ตรวจสอบ Review Panel และสถานะการตรวจเพื่อส่งออกร่าง |
| 4 | `CHECK_DRAFT_XLSX_FILE_LAYOUT` | Check exported draft XLSX layout | ตรวจสอบหน้าตาไฟล์ XLSX ฉบับร่าง |
| 5 | `CHECK_DRAFT_ONLY_LABEL` | Check draft-only label | ตรวจสอบข้อความกำกับว่าเป็นร่างเพื่อการตรวจเท่านั้น |
| 6 | `CHECK_NOT_PAYMENT_AUTHORIZATION` | Confirm this file is not payment authorization | ยืนยันว่าไฟล์นี้ไม่ใช่การอนุมัติเบิกจ่ายจริง |
| 7 | `CHECK_FINAL_AUTHORIZATION_DISABLED` | Confirm Final Authorization is not enabled | ยืนยันว่า Final Authorization ยังไม่เปิดใช้งาน |

## Item Statuses

- `NOT_STARTED`
- `IN_PROGRESS`
- `CHECKED`
- `NEEDS_ATTENTION`
- `BLOCKED`

## Persistence And API

- One row per `(document_id, item_key)`.
- Missing rows are returned as default `NOT_STARTED` items.
- `GET /api/payment-document-review-checklist/{document_id}` returns the ordered merged checklist and derived progress.
- `PUT /api/payment-document-review-checklist/{document_id}/items/{item_key}` upserts only the item status and optional comment.
- `checked_at` is set only while status is `CHECKED` and cleared for any other status.

## Permissions

- `admin`, `esq_head`, `secretary`: read and update.
- `staff`: read-only.
- `teacher`, `print_shop`, `student`, and unrelated roles: blocked.

## Invariants

- Checklist completion does not authorize payment.
- Checklist completion does not accept the XLSX format.
- Checklist completion does not change `PaymentDocumentReviewRecord`.
- Checklist completion does not open or close the existing draft-export gate.
- `payment_authorization_enabled` and `final_export_enabled` are always false.
- The explicit human decision remains `HOLD_PENDING_ADDITIONAL_REVIEW` until separately recorded.
