# ใบรับรองความปลอดภัยการส่งออกร่างเอกสารค่าตอบแทน EMS

**วันที่ตรวจสอบ**: 2026-06-12  
**รุ่นสำหรับสาธิต/ตรวจทาน**: `EMS_DEMO_REVIEW_RC_1`  
**ผลการรับรอง**: `DRAFT_EXPORT_SAFETY_VALIDATED`

## ขอบเขตที่รับรอง

เอกสาร XLSX ที่ระบบสร้างเป็น **ร่างสำหรับการตรวจทานเท่านั้น** ไม่ใช่เอกสารเบิกจ่ายทางการ ไม่ใช่การอนุมัติจ่ายเงิน และไม่ใช่การอนุมัติขั้นสุดท้าย

| รายการ | สถานะ |
|---|---|
| มีการส่งออก XLSX ฉบับร่าง | YES |
| ต้องผ่านสถานะตรวจทาน `ACCEPTED_FOR_DRAFT_EXPORT` ก่อนส่งออก | YES |
| ต้องมีการตั้งค่าภาคเรียนที่พร้อมคำนวณ | YES |
| สถานะเอกสาร `DRAFT_NOT_AUTHORIZED` ยังแสดงอยู่ | YES |
| `payment_authorization_enabled=false` | YES |
| `final_export_enabled=false` | YES |
| การอนุมัติจ่ายเงินจริง | NO |
| การอนุมัติขั้นสุดท้าย | NO |
| การส่งออกเอกสารทางการขั้นสุดท้าย | NO |
| กระบวนการปล่อยจ่ายเงิน | NO |

## หลักฐาน

- การส่งออกผ่าน API และปุ่มในหน้าจอสำเร็จหลังผ่านเงื่อนไขตรวจทาน
- ไฟล์มีข้อความ `Draft for review only. Not payment authorization.`
- ไฟล์มี `DRAFT_NOT_AUTHORIZED`, `ACCEPTED_FOR_DRAFT_EXPORT`, `payment_authorization_enabled = false`, และ `final_export_enabled = false`
- จำนวน review records ไม่เปลี่ยนแปลงจากการส่งออก
- จำนวนกรรมการจ่ายข้อสอบที่กรอกเองไม่ถูกบันทึกเป็นความจริงสำหรับการจ่ายเงินจริง

## ข้อจำกัด

ใบรับรองนี้รองรับการสาธิตและการตรวจทานรูปแบบร่างเท่านั้น ไม่รับรอง production deployment, final finance authorization, official-final export หรือ payment release

