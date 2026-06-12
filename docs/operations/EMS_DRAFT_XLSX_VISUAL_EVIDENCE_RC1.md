# หลักฐานภาพและโครงสร้าง XLSX ฉบับร่าง EMS RC1

**วันที่สร้างหลักฐาน**: 2026-06-12
**รุ่น**: `EMS_DEMO_REVIEW_RC_1`
**สถานะการตัดสินใจรูปแบบ**: `HOLD_PENDING_ADDITIONAL_REVIEW`

## หลักฐานที่สร้าง

| หลักฐาน | เส้นทาง |
|---|---|
| ไฟล์ XLSX จริงจาก gated export endpoint | `docs/operations/demo-smoke-screenshots/draft-xlsx-sample-rc1.xlsx` |
| ภาพตัวอย่างชีตหลัก | `docs/operations/demo-smoke-screenshots/draft-xlsx-layout-preview.png` |
| ตารางตัวอย่างโครงสร้าง | `docs/operations/demo-smoke-screenshots/draft-xlsx-layout-preview.md` |
| แผนที่เซลล์และ merged ranges | `docs/operations/demo-smoke-screenshots/draft-xlsx-cell-map.md` |

## วิธีสร้าง

- ล็อกอินด้วยบัญชีผู้ดูแลระบบสำหรับข้อมูลสาธิตในเครื่อง
- เรียก existing gated endpoint `POST /api/invigilation-advance-batch/official-document-draft-export`
- ใช้ภาคเรียน `2/2568`, ประเภทสอบ `final`, การตั้งค่า `120/200`, และ review gate ที่มีอยู่เดิม
- ได้ HTTP `200` และไฟล์ XLSX จริงขนาด `7,591` ไบต์
- ใช้ `openpyxl` อ่าน workbook จริงเพื่อสร้าง Markdown และ cell map
- ใช้ `openpyxl` ร่วมกับ Pillow วาด PNG จากค่าเซลล์ merged ranges ความกว้างคอลัมน์ และสีพื้นของ workbook จริง

LibreOffice ไม่มีอยู่ในสภาพแวดล้อมนี้ ดังนั้น PNG เป็นภาพจำลองโครงสร้างจาก workbook จริง ไม่ใช่ภาพจาก Excel/LibreOffice renderer ผู้ตรวจควรเปิดไฟล์ XLSX จริงร่วมด้วยก่อนตัดสินใจ

## ผลการตรวจหลักฐาน

| รายการ | ผล |
|---|---|
| ชีต `ร่างเอกสาร` และ `การตรวจร่าง` | พบ |
| ชื่อเรื่องและภาคเรียน `2/2568` | พบ |
| อัตรา `120/200 THB` | พบ |
| แหล่งผู้รับผิดชอบงานจ่ายข้อสอบ | พบ |
| ตารางหลัก จำนวน และยอดรวม | พบ |
| ข้อความ `DRAFT_NOT_AUTHORIZED` | พบ |
| ข้อความ `Draft for review only. Not payment authorization.` | พบ |
| `payment_authorization_enabled=false` | พบ |
| `final_export_enabled=false` | พบ |
| ข้อความอนุมัติจ่ายเงินจริง | ไม่พบ |
| ข้อความ Final Authorization | ไม่พบ |

## ข้อจำกัดและสถานะ

- หลักฐานนี้ช่วยให้ผู้ตรวจเห็นรูปแบบก่อนให้คำตัดสิน แต่ไม่ใช่การยอมรับรูปแบบอัตโนมัติ
- Checklist ในระบบเป็นหลักฐานการตรวจเท่านั้น ไม่ใช่ payment approval หรือ final authorization
- Human decision และ reviewer identity ยังไม่ได้รับการบันทึก
- Gate ยังคง `HOLD_PENDING_ADDITIONAL_REVIEW`
- Final authorization design ยังคง `FINAL_AUTHORIZATION_DESIGN_BLOCKED`
