# แบบบันทึกการตัดสินใจอัตราค่าตอบแทนและแหล่งข้อมูลกรรมการจ่ายข้อสอบ

**English title**: Rate And Paper Distribution Decision Capture
**วันที่จัดทำ**: 2026-06-05
**Current gate**: `PENDING_FINANCE_ADMIN_REVIEW`
**Current decision status**: `DECISION_PENDING`

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
| selected_rate_option |  |
| weekday_rate |  |
| weekend_rate |  |
| applies_to_term |  |
| effective_from |  |
| effective_to |  |
| confirmed_by |  |
| confirmed_at |  |
| notes |  |

## 2. การจัดการอัตรา active ในระบบ / Active System Rate Handling

โปรดตอบคำถามต่อไปนี้ก่อนเปลี่ยนอัตราในระบบ:

- Should current active `300/500` be replaced?
- Should `300/500` remain demo/test only?
- Should rates be term-specific?
- Should system support historical rates per term?

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
| selected_source_option |  |
| source_owner |  |
| source_file_or_system |  |
| validation_required |  |
| notes |  |

## 4. ขอบเขตเอกสารที่จะออกในอนาคต / Document Output Scope

โปรดตอบคำถามต่อไปนี้ก่อนสร้างเอกสารหรือ export:

- Should official document include both invigilation and paper-distribution categories?
- Should output group by date/time slot exactly like 2/2568 sample?
- Should document be Excel-first, PDF-first, or both later?
- Should it remain draft until supervisor/finance review?

## 5. สถานะการตัดสินใจปัจจุบัน / Current Decision Status

Allowed values:

- `DECISION_PENDING`
- `RATE_CONFIRMED_SOURCE_PENDING`
- `RATE_AND_SOURCE_CONFIRMED`
- `HOLD_FOR_FINANCE_CONFIRMATION`

Default:

`DECISION_PENDING`

## หมายเหตุสำคัญ / Important Note

This decision capture does not authorize payment.

Until an authorized finance/admin owner confirms the rate, effective scope, paper-distribution source, document grouping, and reviewer chain, EMS must not implement official document output/export or payment approval from this decision capture.
