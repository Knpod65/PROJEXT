# ดัชนีภาพหน้าจอ — EMS IT/Supervisor Briefing (20260701)

**สถานะ:** รอถ่ายภาพด้วยตนเอง (PENDING — MANUAL CAPTURE)

เครื่องมือถ่ายภาพหน้าจอผ่านเบราว์เซอร์อัตโนมัติ (Playwright/Puppeteer) ไม่ได้ติดตั้งไว้ในระบบนี้ และตามนโยบายของรอบงานนี้จะไม่มีการเพิ่ม dependency ใหม่เพื่อจุดประสงค์นี้ ผู้ดูแล pilot จึงเป็นผู้ถ่ายภาพด้วยตนเองตามรายการด้านล่าง

**ปลายทางไฟล์:** `docs/operations/ems-it-supervisor-brief-screenshots/20260701/`

**Base URL (frontend):** `http://127.0.0.1:3000`
**Backend:** `http://127.0.0.1:8000`

**กติกาการถ่ายภาพ:**
- Viewport หลัก 1440x900 พิกเซล; ถ่ายเพิ่มที่ความกว้าง 1024px เฉพาะจุดที่มีความเสี่ยงเรื่อง layout
- ห้ามยืด/บีบภาพ (คงสัดส่วนเดิม), ห้ามครอปจนบัง UI สำคัญ
- ภาพต้องพอดีภายใน 1 หน้าเอกสารหากนำไปแทรกใน Word/PDF ภายหลัง
- บันทึกเป็น PNG เท่านั้น ตั้งชื่อไฟล์ตามคอลัมน์ "Screenshot file" ด้านล่างเป๊ะ ๆ
- **ห้ามใช้ Admin View As** — ต้องล็อกอินด้วยบัญชีจริงของแต่ละบทบาทตามตารางด้านล่างเท่านั้น

---

## บัญชีที่ใช้ถ่ายภาพ (บัญชีจริงจาก `RUNBOOK.md` / `backend/seed.py`)

| Role | Username | Password |
|---|---|---|
| Admin | `mathawee.m` | `admin123` |
| ESQ Head | `napaporn.ph` | `esq123` |
| Dept Supervisor | `phusanisa.sai` | `staff123` |
| Staff | `araya.fa` | `staff123` |
| Teacher | `pailin.phu` | `teacher123` |
| Print Shop | `printshop.ops` | `print123` |

**หมายเหตุสำคัญเรื่องบัญชี Teacher:** `pailin.phu` คือบัญชีสาธิตอย่างเป็นทางการใน `RUNBOOK.md` ให้ลองใช้บัญชีนี้ก่อน หากเข้าหน้า Check-ins → แท็บ QR Pickup แล้วไม่พบตารางสอบที่มอบหมายให้ในวันที่เลือก (จึงไม่มีปุ่ม "มารับข้อสอบแล้ว" ให้กด) ให้เปลี่ยนไปใช้บัญชี `sirada.khe / teacher123` แทน (พบใน `backend/seed.py` ว่ามีตารางสอนที่ผูกกับตารางสอบจริง) แล้วบันทึกในเอกสารนี้ว่าใช้บัญชีใดจริง

---

## รายการภาพหน้าจอ

| Role | Screenshot file | Page/URL | What it proves |
|---|---|---|---|
| Admin | `admin-01-dashboard-sidebar.png` | `/dashboard` | ภาพรวม dashboard และเมนู sidebar ของ admin |
| Admin | `admin-02-payment-draft-warning.png` | `/invigilation-payment-document-draft` | แสดงข้อความเตือน "Draft only - not payment authorization" บนหน้าเอกสารการเงิน |
| Admin | `admin-03-payment-export-no-final-auth.png` | `/invigilation-payment-document-draft` (ส่วน export/checklist) | แสดงว่าไม่มีปุ่ม/ฟอร์มสำหรับ final authorization ในส่วนส่งออกเอกสาร |
| ESQ Head | `esqhead-01-dashboard-sidebar.png` | `/dashboard` | ภาพรวม dashboard และเมนู sidebar ของ ESQ Head |
| ESQ Head | `esqhead-02-payment-review-area.png` | `/payment-document-settings` หรือหน้าตรวจเอกสารประกอบที่เข้าถึงได้ | แสดงมุมมองการตรวจเอกสารประกอบของ ESQ Head |
| Dept Supervisor | `deptsupervisor-01-dashboard-no-403.png` | `/dashboard` | ยืนยันว่า dashboard โหลดสำเร็จ (200) ไม่ขึ้น 403 อีกต่อไป |
| Dept Supervisor | `deptsupervisor-02-sidebar-scope.png` | เมนู sidebar เต็ม | แสดงขอบเขตเมนูของ Dept Supervisor (ไม่มีเครื่องมือ admin-only) |
| Staff | `staff-01-dashboard.png` | `/dashboard` | หน้า dashboard/หน้าลงจอดของ staff |
| Staff | `staff-02-checkins-operations.png` | `/checkins` | หน้าปฏิบัติการ Check-ins ของ staff |
| Teacher | `teacher-01-checkins-qr-pickup-tab.png` | `/checkins` (แท็บ QR Pickup) | แสดงปุ่ม "มารับข้อสอบแล้ว" (Picked up exam papers) ก่อนกด |
| Teacher | `teacher-02-checkins-pickup-confirmed.png` | `/checkins` (แท็บ QR Pickup หลังกดยืนยัน) | แสดงป้าย "ยืนยันแล้ว" (Confirmed) หลังกดปุ่มสำเร็จ |
| Print Shop | `printshop-01-print-queue.png` | `/print-queue` | หน้าคิวพิมพ์ของ Print Shop |

**ภาพเสริม (ถ่ายเฉพาะถ้าจำเป็น ไม่บังคับ):**

| Role | Screenshot file | Page/URL | What it proves |
|---|---|---|---|
| ใดก็ได้ | `optional-th-en-toggle.png` | หน้าใดก็ได้ที่มีปุ่มสลับภาษา | แสดงการสลับภาษาไทย/อังกฤษ |
| ใดก็ได้ | `optional-1024-layout.png` | หน้าใดก็ได้ที่มีความเสี่ยง layout ที่ 1024px | แสดงว่า layout ไม่พังที่หน้าจอแคบลง |

---

## หลังถ่ายภาพเสร็จ

1. วางไฟล์ PNG ทั้งหมดไว้ที่ `docs/operations/ems-it-supervisor-brief-screenshots/20260701/` ตามชื่อไฟล์ในตารางด้านบน
2. อัปเดตคอลัมน์สถานะที่หัวเอกสารนี้จาก "PENDING — MANUAL CAPTURE" เป็น "CAPTURED"
3. หากใช้บัญชี `sirada.khe` แทน `pailin.phu` สำหรับภาพ Teacher ให้จดบันทึกไว้ในเอกสารนี้ด้วย
4. แจ้งทีมพัฒนาเพื่อ commit ไฟล์ภาพเข้า repo (ไม่ใช้ `git add .` — commit เฉพาะไฟล์ในโฟลเดอร์นี้)
