# เอกสารสรุประบบ EMS สำหรับ IT และหัวหน้างาน

**วันที่จัดทำ:** 2026-07-01
**สถานะระบบล่าสุด:** พร้อมนำไปทดลองใช้งานแบบมีข้อจำกัด (Launch-ready with limitations)
**Commit อ้างอิง:** `71dd6a1` — fix(ui): simplify launch wording and add simple paper pickup confirmation
**ผู้จัดทำ:** ทีมพัฒนา EMS

---

## บทนำ

เอกสารนี้จัดทำขึ้นเพื่ออธิบายระบบ EMS (Exam Management System) ให้ทีม IT และหัวหน้างานเข้าใจภาพรวมได้เร็ว โดยไม่จำเป็นต้องมีพื้นฐานด้านการเขียนโปรแกรม เนื้อหาครอบคลุม เทคโนโลยีที่ใช้ โครงสร้างฐานข้อมูล ขั้นตอนการทำงานของระบบ หน้าที่ของแต่ละบทบาทผู้ใช้งาน สถานะความคืบหน้าปัจจุบัน และข้อจำกัดที่ยังไม่ได้ทำในรอบเปิดใช้งานนี้

**ข้อความสำคัญที่สุดที่ต้องทราบก่อนอ่านต่อ:**

> ระบบนี้ยังไม่ใช่ระบบอนุมัติจ่ายเงินขั้นสุดท้าย และไม่มีปุ่ม Final Authorization ส่วนงานการเงินในระบบทำหน้าที่เป็น "การตรวจหลักฐานประกอบ" เท่านั้น ไม่ใช่การอนุมัติเบิกจ่ายจริง

---

## 1. ระบบนี้ใช้ภาษา/เทคโนโลยีอะไรบ้าง

| ส่วนของระบบ | ภาษา/เทคโนโลยี | ใช้ทำอะไร | ผู้ดูแลควรรู้อะไร |
|---|---|---|---|
| หน้าเว็บ (Frontend) | React + TypeScript (Vite) | หน้าจอที่ผู้ใช้งานเห็นและกดใช้งานทั้งหมด | Build ด้วยคำสั่ง `npm run build`; ไม่มีเซิร์ฟเวอร์ฝั่งหน้าเว็บแยกต่างหาก เป็นไฟล์ static ที่ backend เสิร์ฟได้ |
| การจัดหน้า/สไตล์ | CSS ธรรมดา + Design Tokens (`styles/tokens.css`, `styles/layout.css`) | กำหนดสี ระยะห่าง ธีมของแต่ละบทบาท (`theme/roleThemes.ts`) | ไม่ได้ใช้ Tailwind หรือ UI framework สำเร็จรูป เป็นระบบ CSS ที่เขียนเองภายในทีม |
| หลังบ้าน (Backend) | Python + FastAPI | ประมวลผลตรรกะทางธุรกิจ สิทธิ์การเข้าถึง ตารางสอบ การเช็กอิน | รันด้วย `uvicorn`; โค้ดหลักอยู่ใน `backend/main.py`, `backend/routers/`, `backend/services/` |
| ฐานข้อมูล | SQLite (โหมดพัฒนา/เดโม) หรือ PostgreSQL (สำหรับ pilot/production) | เก็บข้อมูลผู้ใช้ ตารางสอบ การเช็กอิน เอกสารประกอบการเบิก ฯลฯ | ปัจจุบันใช้ SQLite เป็นค่าเริ่มต้นถ้าไม่ตั้งค่า `DATABASE_URL`; ระบบเตือนชัดเจนว่าต้องเปลี่ยนเป็น PostgreSQL ก่อนใช้งานจริง |
| ชั้นเชื่อมฐานข้อมูล (ORM) | SQLAlchemy | แปลงตาราง SQL เป็นโค้ด Python (`backend/models.py`) | ตารางหลักกว่า 50 ตาราง ครอบคลุมผู้ใช้ ตารางสอบ การเช็กอิน เอกสารการเงิน |
| การสื่อสารหน้าเว็บ ↔ หลังบ้าน | REST API (HTTP + JSON) | หน้าเว็บเรียกข้อมูล/ส่งข้อมูลผ่าน endpoint เช่น `/api/checkins`, `/api/dashboard/` | endpoint ทั้งหมดขึ้นต้นด้วย `/api/` |
| การยืนยันตัวตน/สิทธิ์ | JWT (python-jose) + bcrypt (เข้ารหัสรหัสผ่าน) | ล็อกอินแล้วได้ token ใช้ยืนยันสิทธิ์ในทุก request | ระบบมี rate-limiter ป้องกันการล็อกอินถี่เกินไป (10 ครั้ง/300 วินาที) |
| หลายภาษา (i18n) | ไฟล์ dictionary `frontend/src/i18n/th.ts` และ `en.ts` | สลับภาษาไทย/อังกฤษได้ทั้งระบบ | มีสคริปต์ตรวจสอบอัตโนมัติว่าไทย/อังกฤษมีคีย์ครบตรงกัน (`npm run check:i18n`) — ปัจจุบันมี 2,509 คีย์ ตรงกันทั้งสองภาษา |
| การส่งออกเอกสาร | pandas, openpyxl (Excel), python-docx (Word), reportlab/weasyprint/pypdf (PDF) | สร้างไฟล์ Excel/PDF/Word เพื่อเป็นหลักฐานประกอบ | เอกสารที่ export ออกมาทุกไฟล์มีลายน้ำ/ข้อความกำกับว่า "Draft for review only. Not payment authorization." |
| การตรวจสอบคุณภาพ | `npm run build`, `npm run check:i18n`, `python -m compileall`, `pytest` | ตรวจว่าโค้ดคอมไพล์ผ่าน ไม่มีคำแปลขาดหาย และ logic backend ทำงานถูกต้อง | ใช้เป็นเช็คลิสต์ก่อนส่งมอบทุกรอบ |

**อธิบายง่าย ๆ ว่า "ภาษาไหนทำงานตอนไหน":**

```text
ผู้ใช้เปิดหน้าเว็บ (browser)
        │
        ▼
React / TypeScript แสดงหน้าจอ
        │  (เรียกข้อมูลผ่าน REST API เป็น JSON)
        ▼
Python / FastAPI ตรวจสอบสิทธิ์ผู้ใช้ ประมวลผลตรรกะ
        │
        ▼
SQLAlchemy อ่าน/เขียนข้อมูลใน
Database (SQLite ตอนพัฒนา / PostgreSQL ตอนใช้งานจริง)
        │
        ▼
เมื่อผู้ใช้ต้องการหลักฐาน/รายงาน
        │
        ▼
Export service (openpyxl / python-docx / pypdf)
สร้างไฟล์ Excel / Word / PDF พร้อมลายน้ำ "Draft only"
```

---

## 2. ฐานข้อมูลมีโครงสร้างอย่างไร (สรุปเชิงปฏิบัติ)

ฐานข้อมูลมีมากกว่า 50 ตาราง แต่กลุ่มที่หัวหน้างานและ IT ควรรู้จักแบ่งได้เป็น 6 กลุ่มตามงานจริง

| กลุ่มข้อมูล | ตาราง/โมเดลหลัก | เก็บข้อมูลอะไร | ใช้ในหน้าจอไหน |
|---|---|---|---|
| 1. ผู้ใช้และบทบาท | `users`, `printshop_users` | ชื่อ อีเมล บทบาท (role) รหัสผ่าน (เข้ารหัส) | หน้า Login, หน้า Users (admin เท่านั้น) |
| 2. รายวิชา/ตอนเรียน/ตารางสอบ | `courses`, `sections`, `exam_schedules`, `rooms`, `exam_periods` | รายวิชา ตอนเรียน วันเวลาสอบ ห้องสอบ ภาคการศึกษา | หน้า Schedule, Sections, Rooms, Exam Periods |
| 3. ผู้คุมสอบ/ผู้เกี่ยวข้อง | `supervisions`, `supervision_baselines`, `section_coordinators`, `section_exam_managers`, `paper_distribution_assignments`, `external_supervisions` | ใครคุมสอบวิชาไหน ห้องไหน ใครรับผิดชอบการนำส่งข้อสอบ | หน้า Schedule, Exam Manager (Course Ownership) |
| 4. การรับข้อสอบ/เช็กอิน/รายงานการปฏิบัติงาน | `checkin_events`, `exam_pickup_qr_tokens`, `exam_pickup_checkins`, `swap_requests`, `staff_unavailability` | การกด "มารับข้อสอบแล้ว" การเช็กอินเข้าห้องสอบ (`at_room`) คำขอสลับเวร | หน้า Check-ins (แท็บ QR Pickup และ Room Operations) |
| 5. คิวพิมพ์ข้อสอบ | `print_queue_jobs` | สถานะงานพิมพ์ข้อสอบ คิวงาน | หน้า Print Queue (เฉพาะ Print Shop) |
| 6. เอกสารประกอบ/หลักฐานการเงิน | `invigilation_payment_rate_rules`, `payment_document_review_records`, `payment_document_review_checklist_items`, `payment_document_settings` | อัตราค่าตอบแทนคุมสอบ (preview เท่านั้น) บันทึกการตรวจเอกสาร checklist ยืนยันว่ายังไม่มีการอนุมัติขั้นสุดท้าย | หน้า Official Payment Draft, Payment Document Settings |
| อื่น ๆ ที่เกี่ยวข้อง | `import_sessions`, `import_row_logs`, `enrollment_records`, `historical_schedule_batches`, `audit_logs` | ประวัติการนำเข้าข้อมูล บันทึกการตรวจสอบย้อนหลัง (audit trail) | หน้า Import Data, Import Audit, Audit Explorer |

**Database flow (ภาพรวมการไหลของข้อมูล):**

```text
ข้อมูลตั้งต้น (นำเข้ารายวิชา/ตอนเรียน)
        │
        ▼
ตารางสอบ (exam_schedules + rooms)
        │
        ▼
มอบหมายคน (supervisions, paper_distribution_assignments)
        │
        ▼
รับข้อสอบ/ปฏิบัติงาน (checkin_events: receive_papers, at_room)
        │
        ▼
ตรวจหลักฐาน (payment_document_review_records + checklist)
        │
        ▼
ส่งออกเอกสารประกอบ (Excel/PDF แบบ draft — มีลายน้ำ "not payment authorization")
```

---

## 3. Flow การทำงานของระบบ

1. **ตั้งค่าข้อมูลพื้นฐาน** — ผู้ดูแลระบบตั้งค่าภาคการศึกษา (Exam Periods), ห้องสอบ (Rooms), อัตราค่าตอบแทน (Invigilation Rate Settings)
2. **นำเข้าข้อมูลรายวิชา/ตอนเรียน/ตารางสอบ** — ผ่านหน้า Import Data (รองรับไฟล์ Excel) พร้อมบันทึกทุกแถวที่นำเข้าไว้ใน Import Audit
3. **ตรวจ/จัดตารางสอบและห้องสอบ** — ใช้ตัวช่วยจัดตาราง (Optimizer) หรือปรับด้วยมือผ่านหน้า Schedule
4. **มอบหมายผู้คุมสอบ/เจ้าหน้าที่/การรับข้อสอบ** — กำหนดผู้รับผิดชอบแต่ละตอนเรียนผ่านหน้า Exam Manager (Course Ownership) และ Sections
5. **โรงพิมพ์ดูคิวพิมพ์ข้อสอบ** — บทบาท Print Shop เข้าหน้า Print Queue เพื่อดูสถานะงานพิมพ์
6. **อาจารย์หรือผู้เกี่ยวข้องกด "มารับข้อสอบแล้ว"** — ในหน้า Check-ins แท็บ QR Pickup มีปุ่มยืนยันแบบง่าย (ไม่ต้องสแกน QR หรือใช้กล้อง) สำหรับตารางสอบที่ตนได้รับมอบหมายในวันนั้น
7. **เจ้าหน้าที่/อาจารย์บันทึกการปฏิบัติงานตามหน้าที่ที่มีในระบบ** — ใช้แท็บ Room Operations ในหน้า Check-ins เดียวกัน บันทึกจำนวนผู้เข้าสอบ จำนวนมาสาย และหมายเหตุ
8. **ผู้เกี่ยวข้องตรวจเอกสารประกอบการเบิก** — ผ่านหน้า Official Payment Draft และ Payment Document Settings พร้อม checklist ยืนยันความถูกต้อง
9. **การเงินตรวจหลักฐานเท่านั้น** — ฝ่ายการเงินดูรายงาน/ไฟล์ประกอบ ไม่มีปุ่มอนุมัติจ่ายเงินในระบบ
10. **ส่งออกเอกสารประกอบแบบ draft/supporting evidence** — ไฟล์ที่ export ออกทุกไฟล์มีข้อความกำกับชัดเจนว่าเป็น draft ไม่ใช่การอนุมัติ

> **ข้อควรระวัง:** ระบบนี้ยังไม่ใช่ระบบอนุมัติจ่ายเงินขั้นสุดท้าย และไม่มีปุ่ม Final Authorization การอนุมัติจ่ายเงินจริงยังคงเป็นกระบวนการนอกระบบ (offline) ตามปกติของหน่วยงาน

---

## 4. หน้าที่ความรับผิดชอบตามบทบาทผู้ใช้งาน

| Role | ใช้ทำอะไร | เห็นเมนูหลักประมาณไหน | สิ่งที่ไม่ควรเห็น/ไม่ควรทำ |
|---|---|---|---|
| **Admin** | ดูภาพรวมทั้งระบบ จัดการข้อมูลหลัก (ผู้ใช้ ห้อง ภาคการศึกษา) ตรวจระบบ ดู draft เอกสารการเงิน | Dashboard, Schedule, Import Data, Users, Settings, Rooms, Optimizer, Export Center, Payment Draft/Settings, Historical Schedules | ไม่มีปุ่มอนุมัติจ่ายเงินขั้นสุดท้าย (final payment approval ไม่ถูก implement ในระบบเลย ไม่ใช่แค่ admin มองไม่เห็น) |
| **ESQ Head** | ดูแล/ตรวจภาพรวมเชิงงานสอบและหลักฐาน ตรวจเอกสารประกอบ | Dashboard, Schedule, Submissions, Print Review, Workflow, Payment Document Settings, Operational Health, Audit Explorer | ไม่ใช่ผู้กดอนุมัติจ่ายเงินขั้นสุดท้าย (ไม่มีปุ่มนี้อยู่แล้ว) |
| **Secretary** | บทบาทเดียวกลุ่มเดียวกับ ESQ Head ในหลายเมนู (governance/สนับสนุนงานสอบ) | Dashboard, Schedule, Submissions, Print Review, Workflow, Payment Document Settings | บัญชีสาธิต (demo credential) ยังไม่ได้ใส่ไว้ใน RUNBOOK และยังไม่ได้ทดสอบในรอบ smoke test — ถือเป็นข้อจำกัดของรอบนี้ |
| **Dept Supervisor** | ดู dashboard/ข้อมูลในขอบเขตกลุ่มวิชาของตน (academic group) ตรวจภาพรวมของภาควิชา มอบหมาย Course Ownership | Dashboard, Schedule, Sections, Check-ins, Swap Requests, Duty Workload, Exam Manager | ไม่เห็นเครื่องมือ admin-only เช่น Import Data, Users, Optimizer, Settings |
| **Staff** | ทำงานปฏิบัติการรายวัน ดู/บันทึกงานที่เกี่ยวกับตารางสอบ การรับข้อสอบ Copy Count เอกสารการเงินแบบ draft | Dashboard, Schedule, Check-ins, Swap Requests, Copy Count, External Exams, Export Center, Payment Draft/Settings, Duty Workload | ไม่เห็นเครื่องมือ admin-only เช่น Import Data, Users, Optimizer, Rooms |
| **Teacher** | ดูหน้าที่/ตารางที่เกี่ยวข้อง กด "มารับข้อสอบแล้ว" เมื่อรับข้อสอบ บันทึก Room Operations | Dashboard, Schedule, My Exam Work, Check-ins, Swap Requests, My Workload, Submissions | ไม่เห็น Audit Explorer, Operational Health, Platform Configuration, Optimizer Trace, Invigilation Rate Settings, Payment Draft/Settings |
| **Print Shop** | เห็น Print Queue เป็นหลัก ดูงานพิมพ์และสถานะที่เกี่ยวกับการพิมพ์ | Print Queue เท่านั้น (ไม่มี Dashboard/เมนูอื่นในกลุ่ม) | ไม่เห็นข้อมูล admin หรือ dashboard ที่ไม่เกี่ยวข้อง; เรียก endpoint `/api/schedule/copy-count` ไม่ได้ (403 ตามการออกแบบ — หน้าเว็บข้ามการเรียกนี้ให้อัตโนมัติ ไม่ใช่บั๊ก) |

---

## 5. ตอนนี้ระบบทำถึงจุดไหนแล้ว

| หมวด | สถานะ | หลักฐาน/หมายเหตุ |
|---|---|---|
| Role login/scope review | ผ่าน (แก้ไขจุดที่พบแล้ว) | Manual Role UI Review (`3c8f59b`) + fix (`431a6dc`) |
| Dept Supervisor dashboard 403 | แก้ไขแล้ว | `GET /api/dashboard/` เดิม 403 → ปัจจุบัน 200 พร้อมข้อมูลตามขอบเขตภาควิชา |
| Staff demo account | แก้ไขแล้ว | เปลี่ยนเป็น `araya.fa / staff123` (ยืนยัน effective_role=staff) |
| Print Shop queue | ผ่าน | `GET /api/printing/queue` → 200; หน้าเว็บข้าม copy-count call ให้อัตโนมัติ |
| ถ้อยคำหน้าเอกสารการเงิน (finance wording) | ปรับให้ชัดเจนขึ้น | เปลี่ยนข้อความสถานะและคำอธิบายให้สื่อว่า "ยังไม่ใช่การอนุมัติ" ชัดเจนกว่าเดิม (EN/TH) |
| การรับข้อสอบ (paper pickup) | เพิ่มปุ่มยืนยันแบบง่ายแล้ว | ปุ่ม "มารับข้อสอบแล้ว" ในหน้า Check-ins แท็บ QR Pickup ไม่ต้องสแกน QR/กล้อง |
| การอนุมัติจ่ายเงินขั้นสุดท้าย (final payment approval) | ตั้งใจไม่ทำในรอบนี้ | `payment_authorization_enabled` และ `final_export_enabled` ถูก hardcode เป็น `False` ในทุก response ของ service การเงิน |
| Admin View As | ใช้ไม่ได้/ไม่ควรใช้ | endpoint มีอยู่แต่ให้มุมมองแบบ admin-scoped ไม่ใช่การจำลองบทบาทจริง ห้ามใช้เพื่อรีวิว role |
| Browser smoke (ทดสอบผ่านเบราว์เซอร์จริง) | พร้อมใช้งานแบบมีข้อจำกัด | ทดสอบผ่าน API ครบ 6 บทบาท (200 ทุกบทบาท) แต่การตรวจผ่านเบราว์เซอร์จริงยังไม่ได้ทำในรอบอัตโนมัติ — ต้องทำโดยผู้ดูแล pilot ก่อนส่งมอบผู้ใช้ทดสอบ |
| Build/i18n/backend compile | ผ่าน | `npm run build` ✓ (301 modules), `check:i18n` ✓ (2,509 คีย์ตรงกัน), `python -m compileall` ✓, `pytest` 10/10 ผ่าน |
| Thai export/font (ฟอนต์ไทยในเอกสารส่งออก) | รอดำเนินการ | ต้องทำเพิ่มถ้าจำเป็นต้องใช้เอกสารทางการ (PDF/Excel) ที่มีฟอนต์ไทยถูกต้องก่อน pilot จริง |
| การยอมรับของฝ่ายการเงิน (Finance stakeholder acceptance) | รอดำเนินการ | ฝ่ายการเงินยังไม่ได้ยืนยันตอบรับรายงาน supporting roster (ไฟล์ 5 ชีต) |
| บัญชีสาธิต Secretary | ข้อจำกัด | มีบัญชีอยู่ใน `seed.py` แต่ยังไม่ได้ทดสอบใน role smoke และยังไม่อยู่ใน RUNBOOK |

**สรุปสถานะ:** ระบบ **พร้อมนำไปทดลองใช้งานแบบมีข้อจำกัด (Launch-ready with limitations)**

---

## ภาคผนวก: ภาพหน้าจอตามกลุ่มผู้ใช้งาน

ภาพหน้าจอสำหรับเอกสารฉบับนี้ **ยังไม่ได้ถ่ายในรอบนี้** — เนื่องจากเครื่องมือถ่ายภาพหน้าจอผ่านเบราว์เซอร์อัตโนมัติ (Playwright/Puppeteer) ไม่ได้ติดตั้งไว้ในระบบ และตามนโยบายรอบนี้จะไม่มีการเพิ่ม dependency ใหม่

ผู้ดูแล pilot จะเป็นผู้ถ่ายภาพหน้าจอด้วยตนเองตามรายการ บัญชี และชื่อไฟล์ที่กำหนดไว้ใน:

**`docs/operations/EMS_IT_SUPERVISOR_SCREENSHOT_INDEX_20260701.md`**

เมื่อถ่ายภาพและวางไฟล์ไว้ที่ `docs/operations/ems-it-supervisor-brief-screenshots/20260701/` ตามชื่อไฟล์ที่กำหนดแล้ว ภาพจะถูกอ้างอิงในเอกสารฉบับนี้โดยไม่ต้องแก้ไขโครงสร้างเอกสาร

**กติกาการถ่ายภาพ (สำหรับผู้ถ่าย):**
- ขนาดหน้าจอหลัก 1440x900 พิกเซล (ถ่ายเพิ่มที่ 1024px กว้างเฉพาะจุดที่เสี่ยง layout เพี้ยน)
- ห้ามยืด/บีบภาพ ต้องคงสัดส่วนเดิม (aspect ratio)
- ห้ามครอปภาพจนบัง UI ส่วนสำคัญ
- ภาพต้องพอดีภายใน 1 หน้าเอกสารเมื่อนำไปแทรกใน Word/PDF
- บันทึกเป็นไฟล์ PNG เท่านั้น
- **ห้ามใช้ Admin View As ในการถ่ายภาพบทบาทอื่นโดยเด็ดขาด** ต้องล็อกอินด้วยบัญชีจริงของแต่ละบทบาทเท่านั้น

---

## เอกสารอ้างอิงที่เกี่ยวข้อง (สำหรับผู้ต้องการรายละเอียดเพิ่มเติม)

- `docs/operations/EMS_LAUNCH_SCOPE_SIMPLIFICATION_20260701.md` — บันทึกการตัดสินใจลดขอบเขตระบบให้ปลอดภัยที่สุดสำหรับการเปิดใช้งานครั้งแรก
- `docs/operations/EMS_PILOT_READINESS_FINAL_SMOKE_20260701.md` — รายงานทดสอบระบบรอบสุดท้ายก่อน pilot (API smoke ครบ 6 บทบาท)
- `docs/operations/EMS_MANUAL_ROLE_UI_REVIEW_FINDINGS_20260701.md` — ผลการตรวจสอบสิทธิ์การเข้าถึงแต่ละบทบาทแบบละเอียด
- `RUNBOOK.md` — คู่มือเริ่มต้นใช้งานระบบ พร้อมตารางบัญชีสาธิต
