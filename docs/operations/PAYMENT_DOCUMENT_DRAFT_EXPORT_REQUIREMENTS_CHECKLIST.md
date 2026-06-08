# รายการตรวจสอบข้อกำหนดการส่งออกร่างเอกสารการจ่ายเงิน
# Payment Document Draft Export Requirements Checklist

**วันที่ / Date**: 2026-06-08
**สถานะ / Status**: `DRAFT_EXPORT_DESIGN_PENDING`
**การตัดสินใจที่แนะนำ / Recommended decision**: `HOLD_PENDING_REVIEW_ACCEPTANCE`

---

## หมายเหตุสำคัญ / Important Note

รายการตรวจสอบนี้ใช้สำหรับการเตรียมการออกแบบการส่งออกร่างในอนาคตเท่านั้น
ยังไม่ได้นำการส่งออกไปใช้งาน ยังไม่ได้เพิ่มการอนุมัติการจ่ายเงิน และยังไม่ได้เพิ่มการอนุมัติขั้นสุดท้าย

This checklist is for future draft export design preparation only.
Export is not implemented. Payment approval is not added. Final authorization is not added.

---

## หมวด 1 — สถานะการตรวจทาน / Section 1 — Review Status

| รายการ | สถานะ | หมายเหตุ |
|---|---|---|
| สถานะการตรวจทานอยู่ที่ `ACCEPTED_FOR_DRAFT_EXPORT` หรือสูงกว่า | ยังไม่ผ่าน / NOT YET | ต้องได้รับการดำเนินการจากผู้ตรวจสอบ |
| มีความคิดเห็นของผู้ตรวจสอบในระบบ | ยังไม่ผ่าน / NOT YET | ต้องกรอกข้อมูล |
| บันทึกชื่อและบทบาทของผู้ตรวจสอบแล้ว | ยังไม่ผ่าน / NOT YET | ต้องกรอกข้อมูล |

**เงื่อนไขที่จำเป็น / Required conditions:**

- [ ] ผู้ตรวจสอบที่ได้รับอนุญาตได้ตั้งสถานะการตรวจทานเป็น `ACCEPTED_FOR_DRAFT_EXPORT`
  (Authorized reviewer has set review status to `ACCEPTED_FOR_DRAFT_EXPORT`)
- [ ] บันทึกความคิดเห็นการตรวจทานในระบบแล้ว
  (Review comment is recorded in the persistent review system)
- [ ] บันทึกชื่อผู้ตรวจสอบแล้ว
  (Reviewer name is recorded)
- [ ] บันทึกบทบาทผู้ตรวจสอบแล้ว (เช่น หัวหน้าภาควิชา, เจ้าหน้าที่การเงิน)
  (Reviewer role is recorded, e.g., supervisor, finance officer)
- [ ] บันทึกวันเวลาที่ตรวจสอบแล้ว
  (Review timestamp is recorded)

---

## หมวด 2 — สถานะการตั้งค่า / Section 2 — Settings Status

| รายการ | สถานะ | หมายเหตุ |
|---|---|---|
| เลือกภาคการศึกษาแล้ว | ผ่าน / PASS | `2/2568` |
| ตั้งค่าอัตราวันธรรมดาแล้ว | ผ่าน / PASS | `120.00 THB` |
| ตั้งค่าอัตราวันหยุดแล้ว | ผ่าน / PASS | `200.00 THB` |
| ตั้งค่าหน่วยงานผู้รับผิดชอบแล้ว | ต้องยืนยัน / TO CONFIRM | ต้องยืนยันกับผู้ตรวจสอบ |
| สถานะการตั้งค่าใช้งานได้สำหรับการแสดงตัวอย่าง | ผ่าน / PASS | `ACTIVE_FOR_DRAFT_PREVIEW` |

**เงื่อนไขที่จำเป็น / Required conditions:**

- [ ] เลือกภาคการศึกษาใน `PaymentDocumentSettings` แล้ว
  (Academic term is selected in `PaymentDocumentSettings`)
- [ ] ตั้งค่าอัตราวันธรรมดาเป็นจำนวนบวกแล้ว
  (Weekday rate is configured as a positive value)
- [ ] ตั้งค่าอัตราวันหยุดเป็นจำนวนบวกแล้ว
  (Weekend rate is configured as a positive value)
- [ ] ตั้งค่าหน่วยงานผู้รับผิดชอบการแจกข้อสอบ หรือบันทึกเหตุผลที่เว้นว่างไว้อย่างชัดเจน
  (Paper-distribution responsible group is configured, or the reason it is intentionally blank is documented)
- [ ] สถานะการตั้งค่าเป็น `ACTIVE_FOR_DRAFT_PREVIEW`
  (Settings status is `ACTIVE_FOR_DRAFT_PREVIEW`)
- [ ] `calculation_status = CALCULATED_FROM_SETTINGS`
  (Calculation is driven by settings, not hardcoded or demo rates)

---

## หมวด 3 — เนื้อหาเอกสาร / Section 3 — Document Content

**เงื่อนไขที่จำเป็น / Required conditions:**

- [ ] คอลัมน์ตารางตรงกับรูปแบบที่ได้รับการยอมรับ (วันที่สอบ, ช่วงเวลา, ประเภทวัน, จำนวนกรรมการ, ค่าตอบแทน, รวม)
  (Table columns match accepted format: exam date, time slot, day type, committee counts, compensation amounts, totals)
- [ ] แสดงภาคการศึกษาในเอกสาร
  (Academic term is shown in the document)
- [ ] แสดงอัตราที่ใช้คำนวณ (วันธรรมดา/วันหยุด)
  (Calculation rates are shown: weekday/weekend)
- [ ] แสดงหน่วยงานผู้รับผิดชอบ
  (Responsible group/person is shown)
- [ ] แสดงยอดรวมทั้งหมด
  (Grand totals are shown)
- [ ] ระบุแถวการแจกข้อสอบที่กรอกด้วยตนเองอย่างชัดเจน (ไม่ใช่แหล่งข้อมูลที่ชำระเงินได้)
  (Manually-entered paper-distribution rows are clearly identified as not a confirmed payable source)
- [ ] แสดงข้อมูลเมตาการตรวจทาน (ชื่อผู้ตรวจสอบ, บทบาท, สถานะ, วันเวลา)
  (Review metadata is included: reviewer name, role, status, reviewed_at)
- [ ] แสดงแหล่งที่มาการคำนวณ (`CALCULATED_FROM_SETTINGS`)
  (Calculation source is shown: `CALCULATED_FROM_SETTINGS`)

---

## หมวด 4 — ป้ายกำกับความปลอดภัย / Section 4 — Safety Labels

**เงื่อนไขที่จำเป็น / Required conditions:**

- [ ] ป้ายกำกับ "ร่างเอกสาร" มองเห็นได้ชัดเจนบนเอกสารทุกหน้า
  (Draft label is clearly visible on every page/sheet)
- [ ] ป้ายกำกับ "ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย" มองเห็นได้
  (Not-payment-authorization label is visible)
- [ ] ไม่มีถ้อยคำที่บ่งบอกการอนุมัติขั้นสุดท้าย
  (No final-approval wording appears in the output)
- [ ] ไม่มีถ้อยคำที่บ่งบอกการเบิกจ่ายอย่างเป็นทางการ
  (No official payment release wording appears in the output)
- [ ] ป้ายกำกับภาษาไทย (หลัก): `ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย`
  (Thai label confirmed present)
- [ ] ป้ายกำกับภาษาอังกฤษ (รอง): `Draft for review only. Not payment authorization.`
  (English label confirmed present)
- [ ] `document_status = DRAFT_NOT_AUTHORIZED` ปรากฏในข้อมูลเมตาของไฟล์
  (Document status appears in file metadata or header)

---

## หมวด 5 — รูปแบบการส่งออก / Section 5 — Export Format

**เงื่อนไขที่จำเป็น / Required conditions:**

- [ ] รูปแบบ Excel ร่าง (`.xlsx`) — ป้ายกำกับร่างในทุกชีต
  (Excel draft format with draft label on every sheet)
- [ ] รูปแบบ PDF ร่าง — ลายน้ำร่างในทุกหน้า
  (PDF draft format with draft watermark on every page)
- [ ] รูปแบบ HTML สำหรับพิมพ์ — ป้ายกำกับร่างในส่วนหัว
  (Print-friendly HTML draft format with draft label in header)
- [ ] ชื่อไฟล์ตามรูปแบบ: `draft_payment_<term>_<timestamp>.<ext>`
  (Filename follows convention: `draft_payment_<term>_<timestamp>.<ext>`)
- [ ] ไม่มีรูปแบบ "official" หรือ "final" ในเส้นทางการส่งออกร่าง
  (No "official" or "final" format type in draft export path)
- [ ] การส่งออกไม่เปลี่ยน `document_status`, `payment_authorization_enabled`, หรือ `final_export_enabled`
  (Export does not mutate document_status, payment_authorization_enabled, or final_export_enabled)

---

## หมวด 6 — รายการที่ถูกบล็อก / Section 6 — Known Blocked Items

รายการต่อไปนี้ถูกบล็อกและต้องไม่รวมอยู่ในการส่งออกร่าง:

The following items are blocked and must NOT be included in any draft export:

| รายการ | สถานะ |
|---|---|
| การอนุมัติขั้นสุดท้าย | BLOCKED |
| การส่งออกอย่างเป็นทางการ | BLOCKED |
| การเบิกจ่ายเงิน | BLOCKED |
| กระบวนการเบิกจ่ายการจ่ายเงิน | BLOCKED |
| การสรุปผลการกระทบยอดหลังการปฏิบัติหน้าที่ | BLOCKED |
| การบันทึกแถวการแจกข้อสอบด้วยตนเองเป็นข้อมูลความจริงที่ชำระเงินได้ | BLOCKED |
| การเปลี่ยนแปลงอัตราการจ่ายเงินที่ใช้งานอยู่ | BLOCKED |
| สิทธิ์อนุมัติการจ่ายเงิน | BLOCKED |

---

## สรุปสถานะปัจจุบัน / Current Status Summary

| รายการ | สถานะ |
|---|---|
| การส่งออกร่างได้รับการนำไปใช้งานแล้ว | ไม่ / NO |
| การอนุมัติการจ่ายเงินได้รับการเพิ่มแล้ว | ไม่ / NO |
| การอนุมัติขั้นสุดท้ายได้รับการเพิ่มแล้ว | ไม่ / NO |
| การตัดสินใจด้านการออกแบบการส่งออกร่าง | `HOLD_PENDING_REVIEW_ACCEPTANCE` |
| การดำเนินการต่อไปของมนุษย์ | ผู้ตรวจสอบตั้งสถานะเป็น `ACCEPTED_FOR_DRAFT_EXPORT` ถ้าเหมาะสม |
