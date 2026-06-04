# ชุดเอกสารตรวจสอบยอดตัวอย่างค่าคุมสอบสำหรับฝ่ายการเงิน/ผู้ดูแลระบบ

**English title**: Advance Batch Finance/Admin Validation Packet
**วันที่จัดทำ**: 2026-06-04
**สถานะการตรวจสอบ**: `PENDING_FINANCE_ADMIN_REVIEW`
**คำเตือน**: เอกสารนี้เป็นการตรวจสอบยอดตัวอย่างเท่านั้น ไม่ใช่การอนุมัติจ่ายเงินจริง ไม่ใช่รายงานเบิกจ่ายอย่างเป็นทางการ และไม่ใช่หลักฐานการโอนเงิน

## 1. วัตถุประสงค์

ใช้สำหรับให้ฝ่ายการเงิน/ผู้ดูแลระบบตรวจสอบว่า ตรรกะการแสดงยอดตัวอย่างค่าคุมสอบจากรายชื่อผู้ได้รับมอบหมายหน้าที่ สอดคล้องกับหลักเกณฑ์ที่ได้รับอนุมัติหรือไม่ ก่อนออกแบบขั้นตอนอนุมัติหรือส่งออกเอกสารอย่างเป็นทางการ

ขณะนี้ยังไม่พบตัวอย่างยอดที่ได้รับอนุมัติจากฝ่ายการเงิน หรือผลคำนวณอิสระสำหรับใช้เปรียบเทียบใน repository ดังนั้นผลการตรวจสอบยังคงเป็น `PENDING_FINANCE_ADMIN_REVIEW`

## 2. หลักการคำนวณตัวอย่างปัจจุบัน

- วันจันทร์-ศุกร์ ใช้อัตรา weekday
- วันเสาร์-อาทิตย์ ใช้อัตรา weekend
- ใช้วันที่สอบเป็นตัวตัดสินประเภทวัน
- ปี พ.ศ. เช่น `2569` ถูก normalize เป็นปี ค.ศ. ก่อนจำแนกวัน
- คำนวณตัวอย่างเฉพาะแถวที่มีสถานะ `READY_FOR_BATCH_REVIEW`
- หากอัตรา weekday หรือ weekend ขาดอย่างใดอย่างหนึ่ง ระบบจะไม่คำนวณบางส่วน
- check-in ไม่ใช่เงื่อนไขก่อนรวมในรายชื่อเบิกล่วงหน้า
- การขาดงาน no-show การเปลี่ยนตัว และหลักฐานหลังปฏิบัติหน้าที่ เป็นขั้นตอน post-duty reconciliation

## 3. ผลตัวอย่างจากระบบปัจจุบัน

| รายการ | ค่าที่ระบบแสดง |
|---|---:|
| จำนวนรายชื่อหน้าที่ทั้งหมด | 23 |
| จำนวนวันจันทร์-ศุกร์ | 21 |
| จำนวนวันเสาร์-อาทิตย์ | 2 |
| อัตราวันจันทร์-ศุกร์ | 300 THB / ครั้ง |
| อัตราวันเสาร์-อาทิตย์ | 500 THB / ครั้ง |
| จำนวนแถว pending/blocked | 0 |
| ยอดรวมตัวอย่าง | 7,300 THB |

หลักฐานหน้าจอ:

- `docs/operations/demo-smoke-screenshots/advance-batch-preview-amounts-admin.png`

**ข้อจำกัดสำคัญ**: ผลข้างต้นเป็น `SYSTEM PREVIEW SNAPSHOT - NOT OFFICIAL PAYMENT EXPORT` และไม่ใช่ยอดที่ได้รับอนุมัติให้จ่าย

## 4. รายการที่ฝ่ายการเงิน/ผู้ดูแลระบบต้องยืนยัน

โปรดตรวจสอบและบันทึกผลในแบบเปรียบเทียบและทะเบียนข้อแตกต่าง:

- [ ] อัตรา weekday ถูกต้องและมีแหล่งอนุมัติ
- [ ] อัตรา weekend ถูกต้องและมีแหล่งอนุมัติ
- [ ] การนับต่อหน้าที่/ครั้งสอบถูกต้อง
- [ ] การจำแนก weekday/weekend ถูกต้อง
- [ ] การ normalize ปี พ.ศ. ถูกต้อง
- [ ] รายชื่อที่รวมในยอดตัวอย่างถูกต้อง
- [ ] รายชื่อที่ถูก block หรือไม่รวม ถูกต้อง
- [ ] ข้อความ preview-only ชัดเจนและไม่ทำให้เข้าใจว่าอนุมัติจ่ายแล้ว
- [ ] ระบุกฎที่ยังขาดก่อนออกแบบ approval/export

เอกสารประกอบ:

- แบบเปรียบเทียบ: `docs/operations/ADVANCE_BATCH_PREVIEW_MANUAL_COMPARISON_TEMPLATE.md`
- ทะเบียนข้อแตกต่าง: `docs/operations/ADVANCE_BATCH_PREVIEW_DISCREPANCY_REGISTER.md`
- สรุป snapshot: `docs/operations/ADVANCE_BATCH_PREVIEW_VALIDATION_SNAPSHOT.md`

## 5. ตัวเลือกผลการพิจารณา

โปรดเลือกโดยผู้มีอำนาจตรวจสอบเท่านั้น:

- `APPROVE_PREVIEW_LOGIC`
- `APPROVE_WITH_CORRECTIONS`
- `HOLD_PENDING_RULE_CLARIFICATION`
- `REJECT_PREVIEW_LOGIC`

ระบบและเอกสารนี้ไม่เลือกผลการพิจารณาแทนผู้ตรวจสอบ

## 6. Sign-Off

| Field | Value |
|---|---|
| reviewed_by |  |
| role |  |
| reviewed_at |  |
| decision |  |
| notes |  |

## Safety Confirmation

- Payment authorization: **NOT ENABLED**
- Final payment calculation: **NOT IMPLEMENTED**
- Final approval workflow: **NOT IMPLEMENTED**
- Official export: **NOT IMPLEMENTED**
- Check-in as pre-payment gate: **NO**
- Overall gate: `PENDING_FINANCE_ADMIN_REVIEW`

## 7. หลังการตรวจสอบ: วิธีส่งผล / After Review: How to Submit Result

เมื่อการตรวจสอบเสร็จแล้ว ให้ส่งหลักฐานต่อไปนี้:

1. กรอกและลงชื่อใน `docs/operations/ADVANCE_BATCH_FINANCE_VALIDATION_RESPONSE_INTAKE.md`
2. กรอกผลเปรียบเทียบอิสระใน `docs/operations/ADVANCE_BATCH_PREVIEW_MANUAL_COMPARISON_TEMPLATE.md`
3. บันทึกข้อแตกต่างทั้งหมดใน `docs/operations/ADVANCE_BATCH_PREVIEW_DISCREPANCY_REGISTER.md`
4. หากเลือก `APPROVE_WITH_CORRECTIONS` ให้สร้างรายการใน `docs/operations/ADVANCE_BATCH_PREVIEW_CORRECTION_BACKLOG.md`
5. หากเลือก `HOLD_PENDING_RULE_CLARIFICATION` ให้ตอบหรือเพิ่มคำถามใน `docs/operations/ADVANCE_BATCH_FINANCE_FOLLOWUP_QUESTIONS.md`

ผลการตรวจสอบนี้ยืนยันเฉพาะตรรกะ preview เท่านั้น แม้เลือก `APPROVE_PREVIEW_LOGIC` ก็อนุญาตเพียงให้เริ่มออกแบบ approval workflow ใน pass แยกต่างหาก ไม่ใช่การอนุมัติจ่ายเงินจริง และไม่อนุญาต official export

## 8. ตัวอย่างสรุปทางการรูปแบบเดิม 2/2568 / Historical 2/2568 Official-Style Summary Sample

ได้รับข้อมูลที่ผู้ใช้ถอดความจากภาพตัวอย่างสรุปเดิม โดยยังไม่มีไฟล์ภาพต้นฉบับใน attachment directory สำหรับตรวจสอบ provenance:

- ชื่อเอกสาร: `สรุปจำนวนกรรมการและค่าตอบแทน รายวัน/ช่วงเวลา`
- ภาคการศึกษา: `2/2568`
- อัตราตามตัวอย่าง: วันจันทร์-ศุกร์ `120 บาท/คน/ครั้ง`; วันเสาร์-อาทิตย์ `200 บาท/คน/ครั้ง`
- กรรมการคุมสอบ: 145 ครั้ง รวม `20,280 THB`
- กรรมการจ่ายข้อสอบ: 29 ครั้ง รวม `3,960 THB`
- รวมทั้งหมด: `24,240 THB`

ตัวอย่างมีสองหมวด:

- `INVIGILATION_COMMITTEE` / กรรมการคุมสอบ
- `PAPER_DISTRIBUTION_COMMITTEE` / กรรมการจ่ายข้อสอบ

### Rate Conflict Requiring Confirmation

| แหล่งอัตรา | วันธรรมดา | วันเสาร์-อาทิตย์ | สถานะ |
|---|---:|---:|---|
| ตัวอย่างเดิม 2/2568 ที่ผู้ใช้ถอดความ | 120 | 200 | รอตรวจสอบต้นฉบับ/provenance |
| draft เดิมที่ผู้ใช้ระบุ | 150 | 200 | ไม่พบหลักฐานใน repository |
| active local EMS ปัจจุบัน | 300 | 500 | demo/preview configuration เท่านั้น |

โปรดเลือกหรือระบุคำตอบ:

- [ ] ใช้ `120/200` จากตัวอย่างเดิม 2/2568
- [ ] ใช้ `150/200` จาก draft เดิม
- [ ] ใช้ `300/500` จาก active local EMS ปัจจุบัน
- [ ] ใช้อัตราแยกตามภาคการศึกษา
- [ ] อัตราอื่น พร้อมแนบหลักฐานอนุมัติ

โปรดยืนยันด้วยว่า EMS ควรใช้แหล่งใดในการนับ `PAPER_DISTRIBUTION_COMMITTEE` เนื่องจากระบบมีข้อมูลปฏิบัติการหลายแหล่ง แต่ยังไม่มีแหล่งใดได้รับการยืนยันเป็น payable source

ข้อมูลอ้างอิง:

- `docs/operations/OFFICIAL_2_2568_PAYMENT_SUMMARY_SAMPLE_REFERENCE.md`
- `docs/architecture/INVIGILATION_RATE_DECISION_AFTER_2_2568_SAMPLE.md`
- `docs/architecture/INVIGILATION_PAYMENT_DUTY_CATEGORY_MODEL.md`
- `docs/architecture/OFFICIAL_PAYMENT_DOCUMENT_DATA_GAP_AUDIT.md`

ส่วนนี้ยังคงใช้ตรวจสอบ preview/document-output logic เท่านั้น ไม่เปลี่ยนอัตรา active ไม่อนุมัติจ่ายเงินจริง และไม่สร้าง official export
