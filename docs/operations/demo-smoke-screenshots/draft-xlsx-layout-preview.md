# RC1 Draft XLSX Layout Preview

- Source workbook: `docs/operations/demo-smoke-screenshots/draft-xlsx-sample-rc1.xlsx`
- Preview method: direct `openpyxl` inspection of the generated workbook.
- This Markdown is structural evidence, not a substitute for opening the XLSX in Excel or LibreOffice.

## Sheet: ร่างเอกสาร

| Row | A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ร่างเอกสารเพื่อการตรวจทานเท่านั้น ยังไม่ใช่เอกสารอนุมัติเบิกจ่าย |  |  |  |  |  |  |  |  |
| 2 | Draft for review only. Not payment authorization. |  |  |  |  |  |  |  |  |
| 3 | DRAFT_NOT_AUTHORIZED |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |
| 5 | สรุปจำนวนกรรมการและค่าตอบแทน รายวัน/ช่วงเวลา |  |  |  |  |  |  |  |  |
| 6 | ภาคการศึกษา: 2/2568 |  |  |  |  |  |  |  |  |
| 7 | อัตราวันธรรมดา: 120.00 THB  \|  อัตราวันหยุด: 200.00 THB |  |  |  |  |  |  |  |  |
| 8 | หน่วยงานรับผิดชอบจ่ายข้อสอบ: Education_Student_Quality |  |  |  |  |  |  |  |  |
| 9 | วันที่สอบ | ช่วงเวลา | ประเภทวัน | จำนวนกรรมการคุมสอบ | ค่าตอบแทนคุมสอบ | จำนวนกรรมการจ่ายข้อสอบ | ค่าตอบแทนจ่ายข้อสอบ | รวมค่าตอบแทน | อัตรา |
| 10 | 2569-03-19 | 15:30-18:30 | WEEKDAY | 4 | 480 | 0 | 0 | 480 | 120 |
| 11 | 2569-03-20 | 15:30-18:30 | WEEKDAY | 1 | 120 | 0 | 0 | 120 | 120 |
| 12 | 2026-03-23 | 12:00-15:00 | WEEKDAY | 5 | 600 | 0 | 0 | 600 | 120 |
| 13 | 2569-03-23 | 15:30-18:30 | WEEKDAY | 1 | 120 | 0 | 0 | 120 | 120 |
| 14 | 2026-03-24 | 08:00-11:00 | WEEKDAY | 2 | 240 | 0 | 0 | 240 | 120 |
| 15 | 2026-03-26 | 12:00-15:00 | WEEKDAY | 4 | 480 | 0 | 0 | 480 | 120 |
| 16 | 2569-03-26 | 15:30-18:30 | WEEKDAY | 2 | 240 | 0 | 0 | 240 | 120 |
| 17 | 2569-03-27 | 12:00-15:00 | WEEKDAY | 2 | 240 | 0 | 0 | 240 | 120 |
| 18 | 2569-03-28 | 12:00-15:00 | WEEKEND | 2 | 400 | 0 | 0 | 400 | 200 |
| 19 | รวม |  |  | 23 | 2920 | 0 | 0 | 2920 |  |
| 20 |  |  |  |  |  |  |  |  |  |
| 21 | เอกสารนี้เป็นร่างเพื่อการตรวจทาน ไม่ใช่เอกสารอนุมัติเบิกจ่าย |  |  |  |  |  |  |  |  |

## Sheet: การตรวจร่าง

| Row | A | B |
|---|---|---|
| 1 | ผู้ตรวจ (Reviewer) | นางสาว มาธวี เมืองศรี |
| 2 | บทบาท (Role) | admin |
| 3 | สถานะการตรวจ (Review Status) | ACCEPTED_FOR_DRAFT_EXPORT |
| 4 | วันที่ตรวจ (Reviewed At) | 2026-06-08 09:52:32.123376 |
| 5 | หมายเหตุ (Comment) | รูปแบบร่างเอกสารใช้ได้สำหรับการออกแบบ draft export ต่อ อัตราค่าตอบแทน 120/200 บาท และหน่วยงานผู้รับผิดชอบจ่ายข้อสอบได้รับการยืนยันแล้ว โดยยังไม่ถือเป็นการอนุมัติเบิกจ่ายจริง |
| 6 |  |  |
| 7 | แหล่งที่มาของการตั้งค่า (Settings Source) | PAYMENT_DOCUMENT_SETTINGS:payment-document-settings-2-2568 |
| 8 | สถานะการตั้งค่า (Settings Status) | ACTIVE_FOR_DRAFT_PREVIEW |
| 9 | สถานะการคำนวณ (Calculation Status) | CALCULATED_FROM_SETTINGS |
| 10 |  |  |
| 11 | สถานะเอกสาร (Document Status) | DRAFT_NOT_AUTHORIZED |
| 12 | payment_authorization_enabled | false |
| 13 | final_export_enabled | false |
| 14 |  |  |
| 15 | สร้างเมื่อ (Generated At) | 2026-06-12T08:21:37.759069+00:00 |
