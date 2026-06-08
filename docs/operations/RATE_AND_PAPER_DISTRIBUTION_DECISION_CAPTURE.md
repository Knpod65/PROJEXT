# แบบบันทึกการตัดสินใจอัตราค่าตอบแทนและแหล่งข้อมูลกรรมการจ่ายข้อสอบ

**English title**: Rate And Paper Distribution Decision Capture
**วันที่จัดทำ**: 2026-06-05
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Current decision status**: `RATE_AND_SOURCE_CONFIRMED` for draft-output purposes only

เอกสารนี้ใช้บันทึกการตัดสินใจก่อนออกแบบหรือสร้างเอกสารทางการเท่านั้น ไม่ใช่การอนุมัติการจ่ายเงินจริง ไม่ใช่การอนุมัติ export และไม่เปลี่ยนอัตรา active ในระบบ

## 1. การตัดสินใจเรื่องอัตราค่าตอบแทน / Rate Decision

### ตัวเลือกที่อนุญาต

- `USE_SAMPLE_RATE_120_200_FOR_2_2568`
- `USE_DRAFT_RATE_150_200`
- `USE_CURRENT_ACTIVE_RATE_300_500`
- `TERM_SPECIFIC_RATE_REQUIRED`
- `HOLD_FOR_FINANCE_CONFIRMATION`

### ช่องบันทึกคำตอบ

| Field | Value |
|---|---|
| selected_rate_option | `USE_SAMPLE_RATE_120_200_FOR_2_2568` |
| weekday_rate | `120 THB per person/session` |
| weekend_rate | `200 THB per person/session` |
| applies_to_term | `2/2568` |
| effective_from | `TERM_2_2568_ONLY` |
| effective_to | `TERM_2_2568_ONLY` |
| confirmed_by | User decision for draft-output pass |
| confirmed_at | 2026-06-05 |
| notes | Rates are term-specific for 2/2568. Current active `300/500` must be treated as demo/test data only and not used as the official reference. |

## 2. การจัดการอัตรา active ในระบบ / Active System Rate Handling

โปรดตอบคำถามต่อไปนี้ก่อนเปลี่ยนอัตราในระบบ:

- Should current active `300/500` be replaced?
- Should `300/500` remain demo/test only?
- Should rates be term-specific?
- Should system support historical rates per term?

Draft-output answers captured 2026-06-05:

- Do not replace active `300/500` in this pass; treat it as demo/test data only.
- Rates are term-specific.
- The 2/2568 draft preview must hardcode the confirmed sample rate `120/200` for this draft path and must not read active `300/500`.
- Historical/term-specific rates should remain separated by term for future official processing.

## 3. แหล่งข้อมูลกรรมการจ่ายข้อสอบ / Paper Distribution Committee Source

### ตัวเลือกที่อนุญาต

- `USE_EXISTING_EMS_DATA_IF_VALIDATED`
- `MANUAL_INPUT_BY_STAFF`
- `IMPORT_FROM_OFFICIAL_SUMMARY`
- `EXTERNAL_SOURCE_REQUIRED`
- `HOLD_FOR_SOURCE_CONFIRMATION`

### ช่องบันทึกคำตอบ

| Field | Value |
|---|---|
| selected_source_option | `MANUAL_INPUT_BY_STAFF` |
| source_owner | Staff-confirmed/manual-confirmed draft input |
| source_file_or_system | In-app draft preview request body; non-persistent |
| validation_required | Supervisor/finance review still required before final truth, approval, or export |
| notes | Paper-distribution committee data is usable for document draft purposes only until an authoritative EMS source is fully validated. |

## 4. ขอบเขตเอกสารที่จะออกในอนาคต / Document Output Scope

โปรดตอบคำถามต่อไปนี้ก่อนสร้างเอกสารหรือ export:

- Should official document include both invigilation and paper-distribution categories?
- Should output group by date/time slot exactly like 2/2568 sample?
- Should document be Excel-first, PDF-first, or both later?
- Should it remain draft until supervisor/finance review?

Draft-output answers captured 2026-06-05:

- Include both `INVIGILATION_COMMITTEE` / กรรมการคุมสอบ and `PAPER_DISTRIBUTION_COMMITTEE` / กรรมการจ่ายข้อสอบ.
- Match the 2/2568 sample-style grouping by exam date and time slot.
- Implement in-app draft preview first; do not add Excel/PDF/export in this pass.
- Keep the document status as draft/not authorized until supervisor/finance review.

## 5. สถานะการตัดสินใจปัจจุบัน / Current Decision Status

Allowed values:

- `DECISION_PENDING`
- `RATE_CONFIRMED_SOURCE_PENDING`
- `RATE_AND_SOURCE_CONFIRMED`
- `HOLD_FOR_FINANCE_CONFIRMATION`

Default before the 2026-06-05 human decision:

`DECISION_PENDING`

Current captured status for draft-output implementation:

`RATE_AND_SOURCE_CONFIRMED`

This status is limited to in-app draft preview generation. It is not `ANSWERED_APPROVED`, does not close the finance gate, and does not authorize payment.

## หมายเหตุสำคัญ / Important Note

This decision capture does not authorize payment.

The 2026-06-05 decision permits only an in-app official-style draft preview using term-specific `120/200` and manual staff paper-distribution input. EMS must still not implement final payment approval, official payment authorization, or official export from this decision capture.

## 2026-06-08 Supervisor / Finance Review Package Reference

The next human review package is prepared in:

- `docs/operations/EMS_PAYMENT_DOCUMENT_DRAFT_REVIEW_ONE_PAGER.md`
- `docs/operations/SUPERVISOR_FINANCE_REVIEW_DECISION_FORM.md`
- `docs/operations/SUPERVISOR_FINANCE_REVIEW_TALKING_SCRIPT.md`
- `docs/operations/SUPERVISOR_FINANCE_QUICK_REVIEW_CHECKLIST.md`

This package asks reviewers to confirm the rate set, authoritative paper-distribution committee source, document format, and safe next step. It does not upgrade `RATE_AND_SOURCE_CONFIRMED` beyond draft-output purposes and does not authorize payment or export.
