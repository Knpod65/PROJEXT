# EMS — UI Design Specification
## ระบบจัดการข้อสอบ คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มช.

**Version:** 1.0 | **Date:** April 2026 | **Designer Target:** Stitch / v0 / Lovable / Figma

---

# 🧭 1. USER FLOWS

## 1.1 Admin Flow

```
LOGIN
  └─> DASHBOARD (stats + charts + audit log)
        ├─> PERIOD MANAGEMENT (สร้างรอบสอบ / activate)
        ├─> IMPORT DATA (นำเข้านักศึกษา / sections จาก Excel)
        ├─> SECTIONS LIST (ดู/แก้ไข sections ทั้งหมด)
        │     └─> EXAM MANAGER ASSIGN (มอบหมายผู้รับผิดชอบ section)
        ├─> OPTIMIZER (จัดตารางสอบอัตโนมัติ)
        │     ├─> กำหนด constraints
        │     ├─> Run optimizer
        │     └─> Review + confirm result
        ├─> CO-EXAM (จัดกลุ่มวิชาสอบร่วม)
        ├─> SCHEDULE (ตารางสอบทั้งหมด)
        ├─> WORKFLOW (ยืนยันตาราง / ลงนาม)
        ├─> SUBMISSIONS (ดูทุก submission ทุกอาจารย์)
        ├─> SWAPS (อนุมัติ/ปฏิเสธ คำขอสลับกะ)
        ├─> CHECKINS (ดู check-in ทุกห้อง)
        ├─> PRINT REVIEW (ตรวจก่อนพิมพ์ตาราง)
        ├─> COPY COST (คำนวณค่าถ่ายเอกสาร)
        ├─> USERS (จัดการผู้ใช้งาน)
        ├─> SETTINGS (ตั้งค่าระบบ)
        └─> EXTERNAL EXAMS (สอบพิเศษ)
```

**Entry:** `/login` → redirect to `/dashboard`
**View-As:** Admin สามารถสลับ view เป็น staff / teacher / student

---

## 1.2 Teacher Flow

```
LOGIN
  └─> SCHEDULE (ตารางสอบวิชาของตัวเอง) ← entry point
        ├─> MY EXAM (จัดการสอบ — เพิ่มผู้รับผิดชอบ, ดูสถานะ)
        │     └─> SUBMISSION DETAIL (ส่งข้อสอบ + ส่งไฟล์)
        ├─> SUBMISSIONS LIST (ดูสถานะ submission ของตัวเอง)
        │     ├─> SUBMISSION FORM (กรอกข้อมูล + อัพโหลดไฟล์)
        │     └─> MESSAGE THREAD (ส่งข้อความถึง staff)
        ├─> SWAPS (ขอสลับกะ / ดูสถานะคำขอ)
        ├─> CHECKINS (check-in วันสอบ)
        └─> STUDENT SEARCH (ค้นหาตารางสอบนักศึกษา)
```

**Entry:** `/login` → redirect to `/schedule`

---

## 1.3 Staff Flow

```
LOGIN
  └─> DASHBOARD (สถิติงานของฉัน + notification สลับกะ)
        ├─> SCHEDULE (ตารางสอบทั้งหมด — read mode)
        ├─> SWAPS (ตอบรับ/ปฏิเสธ คำขอสลับ)
        ├─> CHECKINS (check-in ก่อนสอบ + GPS)
        ├─> COPY COST (คำนวณค่าถ่ายต่อ section)
        ├─> SECTIONS (ดูรายวิชา)
        └─> STUDENT SEARCH (ค้นหาตารางสอบนักศึกษา)
```

**Entry:** `/login` → redirect to `/dashboard`
**Alert:** badge แจ้งคำขอสลับรอตอบ

---

## 1.4 ESQ Head / Secretary Flow

```
LOGIN
  └─> SCHEDULE (read-only ตารางทั้งหมด) ← entry point
        ├─> WORKFLOW (ยืนยันตาราง / ลงนาม)
        ├─> SUBMISSIONS (ดู submissions ทั้งหมด)
        └─> STUDENT SEARCH
```

**Badge:** "ดูในฐานะ: ESQ Head" แสดงใน topbar เสมอ
**Restriction:** ไม่สามารถแก้ไขข้อมูล — view only

---

## 1.5 Dept Supervisor Flow

```
LOGIN
  └─> SCHEDULE (ตารางสอบแผนกของตัวเอง) ← entry point
        ├─> MY EXAM (ดูและ confirm งานของแผนก)
        ├─> SUBMISSIONS (อนุมัติ submission)
        ├─> SWAPS
        └─> CHECKINS
```

---

## 1.6 Student Flow

```
STUDENT SEARCH (no login required for public search)
  └─> กรอกรหัสนักศึกษา หรือชื่อ
        └─> แสดงตารางสอบของนักศึกษาคนนั้น
              └─> QR Code สำหรับ check-in (ถ้า implement)
```

---

# 🧱 2. PAGE STRUCTURES

## P01 — Login Page

```
┌─────────────────────────────────────────┐
│  [University Logo]                      │
│  EMS — ระบบจัดการข้อสอบ มช.            │
│  คณะรัฐศาสตร์และรัฐประศาสนศาสตร์       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Username (CMU account)         │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Password              [👁]    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [        เข้าสู่ระบบ         ]        │
│  ─────────────── หรือ ──────────────   │
│  [  เข้าสู่ระบบด้วย CMU SSO   ]       │
│                                         │
│  © 2026 คณะรัฐศาสตร์ มช.              │
└─────────────────────────────────────────┘
```

**States:**
- Default
- Loading (spinner on button, fields disabled)
- Error (red border + error message under fields)
- Rate limit (countdown timer: "กรุณารอ X วินาที")

---

## P02 — Admin Dashboard

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: แดชบอร์ด         ● ปลายภาค 2/2568  │
│          ├──────────────────────────────────────────────┤
│ 📊 แดชบอร์ด│ [STAT CARD] [STAT CARD] [STAT CARD] [STAT]  │
│ 📅 ตาราง  │                                              │
│ ...      │ ┌──────────────────────────────────────────┐ │
│          │ │  📊 ANALYTICS CHARTS (2×2 grid)          │ │
│          │ │  [Submission Donut] [Supervision Donut]  │ │
│          │ │  [Swap Status Donut] [Copy Cost Bar]     │ │
│          │ └──────────────────────────────────────────┘ │
│          │                                              │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │  📋 ประวัติการใช้งาน         [9 รายการ] │ │
│          │ │  [timestamp] [ACTION BADGE] [user]       │ │
│          │ │  ...                                     │ │
│          │ └──────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

**Stat Cards (4):**
1. Sections ทั้งหมด + progress bar (จัดแล้ว %)
2. นักศึกษาทั้งหมด + จำนวนอาจารย์
3. แผ่นถ่ายเอกสารรวม + ค่าใช้จ่าย
4. ห้องสอบที่ใช้ + sections ยังไม่ได้จัด

**Charts:**
1. สถานะ submission (donut: draft/pending/approved/rejected/ยังไม่ส่ง)
2. การยืนยัน supervision (donut: ยืนยันแล้ว/รอ)
3. Swap requests (donut: by status)
4. ค่าถ่ายเอกสารต่อห้อง (horizontal bar)

---

## P03 — Staff Dashboard

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: แดชบอร์ด                            │
│          ├──────────────────────────────────────────────┤
│          │ [⚠ ALERT: มีคำขอสลับรอตอบ X รายการ] [ดูคำขอ]│
│          │                                              │
│          │ [STAT] วันสอบที่กำกับ   [STAT] ยืนยันแล้ว  │
│          │ [STAT] คะแนน compensation  [STAT] Swap รอ   │
│          │                                              │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │  📅 ตารางสอบวันนี้ / ใกล้ถึง            │ │
│          │ │  [exam card] [exam card] [exam card]     │ │
│          │ └──────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

---

## P04 — Schedule (ตารางสอบ)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: ตารางสอบ                            │
│          ├──────────────────────────────────────────────┤
│          │ FILTER BAR: [วันที่] [ห้อง] [อาจารย์] [🔍] │
│          │             [ส่งออก Excel ↓] [พิมพ์ PDF]   │
│          ├──────────────────────────────────────────────┤
│          │                                              │
│          │  DATE GROUP: วันจันทร์ที่ 19 มีนาคม 2569   │
│          │  ┌────────────────────────────────────────┐ │
│          │  │ [128305] สื่อสารมวลชน      08.00-11.00 │ │
│          │  │ 📍 PSB 1101   👤 30 คน   🖨 90 แผ่น   │ │
│          │  │ [อ.อุดมโชค] + [ผศ.ศิริมา]            │ │
│          │  │ [BADGE: published]  [⋮ เมนู]          │ │
│          │  └────────────────────────────────────────┘ │
│          │  ┌────────────────────────────────────────┐ │
│          │  │ [128305-2] สื่อสารมวลชน  15.30-18.30  │ │
│          │  │ ...                                    │ │
│          │  └────────────────────────────────────────┘ │
│          │                                              │
│          │  DATE GROUP: วันอังคาร ...                 │
└──────────┴──────────────────────────────────────────────┘
```

**Schedule Card States:**
- `draft` — gray badge
- `published` — blue badge
- `confirmed` — green badge
- `cancelled` — red badge + strikethrough

---

## P05 — Submissions (ส่งข้อสอบ)

### Teacher view:
```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: ส่งข้อสอบ                           │
│          ├──────────────────────────────────────────────┤
│          │ [วิชาของฉัน ▼]  [ปีการศึกษา 2568/2 ▼]      │
│          ├──────────────────────────────────────────────┤
│          │ ┌─────────────────────────────────────────┐ │
│          │ │ 📚 วิชา 126201 การเมืองการปกครอง      │ │
│          │ │ ตอน 1 — 30 นักศึกษา                  │ │
│          │ │ [● pending] ส่งเมื่อ 7 เม.ย. 09:34    │ │
│          │ │ [ดูรายละเอียด] [ส่งอีกครั้ง]          │ │
│          │ └─────────────────────────────────────────┘ │
│          │ ┌─────────────────────────────────────────┐ │
│          │ │ 📚 วิชา 127100 ทฤษฎีการเมือง          │ │
│          │ │ ตอน 1 — 71 นักศึกษา                  │ │
│          │ │ [○ ยังไม่ส่ง]                         │ │
│          │ │ [+ ส่งข้อสอบ]                         │ │
│          │ └─────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

### Submission Detail Modal:
```
┌─────────────────────────────────────────────┐
│ ส่งข้อสอบ — 126201 การเมืองการปกครอง  [×] │
├─────────────────────────────────────────────┤
│ ประเภทข้อสอบ: [ปรนัย ▼]                   │
│ จำนวนข้อ: [____] ข้อ                      │
│ ระยะเวลา: [____] นาที                     │
│ ไฟล์ข้อสอบ: [เลือกไฟล์ PDF/DOCX]         │
│                                             │
│ หมายเหตุ: [textarea]                      │
│                                             │
│ ── ข้อความถึง Staff ───────────────────── │
│ [ส่งข้อความ...]                  [ส่ง]   │
│ [thread ข้อความ]                          │
│                                             │
│ [ยกเลิก]              [ส่งข้อสอบ →]      │
└─────────────────────────────────────────────┘
```

---

## P06 — Swap Requests (สลับกะ)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: การสลับกะ            [+ ขอสลับ]    │
│          ├──────────────────────────────────────────────┤
│          │ TABS: [รอตอบ (3)] [อนุมัติแล้ว] [ทั้งหมด] │
│          ├──────────────────────────────────────────────┤
│          │ ┌─────────────────────────────────────────┐ │
│          │ │ [INCOMING] อ.สมชาย → ฉัน               │ │
│          │ │ 📅 23 มี.ค. 2569  08.00-11.00  PSB 1101│ │
│          │ │ "ติดธุระ ขอสลับกับคุณ"                  │ │
│          │ │ [✓ ยอมรับ]  [✗ ปฏิเสธ]  [💬 ข้อความ] │ │
│          │ └─────────────────────────────────────────┘ │
│          │ ┌─────────────────────────────────────────┐ │
│          │ │ [OUTGOING] ฉัน → อ.สมหญิง  ● pending   │ │
│          │ │ 📅 24 มี.ค. 2569  12.00-15.00          │ │
│          │ │ [ยกเลิกคำขอ]                           │ │
│          │ └─────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

---

## P07 — Check-in (วันสอบ)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: Check-in วันสอบ                     │
│          ├──────────────────────────────────────────────┤
│          │ ┌──────────────────── วันนี้ ─────────────┐ │
│          │ │  📍 PSB 1101                            │ │
│          │ │  126201 การเมือง 08.00-11.00  30 คน   │ │
│          │ │  [● ยังไม่ check-in]                   │ │
│          │ │  [📍 Check-in ด้วย GPS]                │ │
│          │ └────────────────────────────────────────┘ │
│          │ ┌────────────────────────────────────────┐ │
│          │ │  🏫 Auditorium 50ปี                    │ │
│          │ │  126211 ... 15.30-18.30   105 คน      │ │
│          │ │  [✅ Check-in แล้ว 14:52]              │ │
│          │ └────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

**Check-in Modal:**
```
┌──────────────────────────────────────────┐
│  ยืนยัน Check-in                    [×] │
├──────────────────────────────────────────┤
│  📍 ตำแหน่งของคุณ: กำลังตรวจสอบ...     │
│  📍 ห้องสอบ: PSB 1101                   │
│  ระยะห่าง: ~45 เมตร ✅                  │
│                                          │
│  [ยืนยัน Check-in]                     │
└──────────────────────────────────────────┘
```

---

## P08 — Student Search (ค้นหาตารางสอบ)

```
┌─────────────────────────────────────────────┐
│  [LOGO]  ค้นหาตารางสอบนักศึกษา             │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  🔍 รหัสนักศึกษา หรือ ชื่อ-นามสกุล │   │
│  └─────────────────────────────────────┘   │
│  [ค้นหา]                                   │
│                                             │
│  ── ผลการค้นหา ──────────────────────────  │
│  ┌───────────────────────────────────────┐ │
│  │  640310001 นายสมชาย ใจดี             │ │
│  │  ┌───────────────────────────────┐   │ │
│  │  │ 126201 | 19 มี.ค. | 08.00-11 │   │ │
│  │  │ PSB 1101  | ห้องที่นั่ง: A3  │   │ │
│  │  └───────────────────────────────┘   │ │
│  │  ┌───────────────────────────────┐   │ │
│  │  │ 127100 | 26 มี.ค. | 12.00-15 │   │ │
│  │  │ PSB 1204  | ห้องที่นั่ง: B7  │   │ │
│  │  └───────────────────────────────┘   │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## P09 — Users Management

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: จัดการผู้ใช้งาน       [+ เพิ่มผู้ใช้]│
│          ├──────────────────────────────────────────────┤
│          │ FILTER: [Role ▼] [แผนก ▼] [สถานะ ▼] [🔍]   │
│          ├──────────────────────────────────────────────┤
│          │ TABLE:                                       │
│          │ ชื่อ-สกุล | Username | Role | แผนก | สถานะ │
│          │ ─────────────────────────────────────────── │
│          │ อติกานต์ | atikant.s | admin | — | ● active │
│          │ มาธวี    | mathawee.m| admin | — | ● active │
│          │ ปัยลิน   | pailin.phu| teacher|รัฐ| ● active│
│          │ ...                                          │
│          │ [deactivate] [แก้ไข role]                   │
└──────────┴──────────────────────────────────────────────┘
```

---

## P10 — Optimizer (จัดตารางสอบ)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: จัดตารางสอบอัตโนมัติ               │
│          ├──────────────────────────────────────────────┤
│          │ STEPPER: [1.ข้อมูล] → [2.Constraints] → [3.Run] → [4.ผล]│
│          ├──────────────────────────────────────────────┤
│          │                                              │
│          │  STEP 1: ยืนยันข้อมูล                      │
│          │  • Sections: 13 รายการ                     │
│          │  • Rooms: 8 ห้อง                           │
│          │  • Staff: 30 คน                            │
│          │                                              │
│          │  STEP 2: Constraints                        │
│          │  ☑ ไม่ให้อาจารย์คนเดียวสอบ 2 ห้องพร้อมกัน │
│          │  ☑ จำนวนนักศึกษา ≤ ความจุห้อง             │
│          │  ☑ เจ้าหน้าที่คนเดียวต่อวัน ≤ 2 ช่วงเวลา │
│          │                                              │
│          │  [← ย้อนกลับ]        [ถัดไป →]            │
└──────────┴──────────────────────────────────────────────┘
```

---

## P11 — Period Management (รอบสอบ)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: รอบสอบ               [+ สร้างรอบ]   │
│          ├──────────────────────────────────────────────┤
│          │ ┌──────────────────────────────────────────┐ │
│          │ │  ● ACTIVE — ปลายภาค 2/2568              │ │
│          │ │  Final · Semester 2 · Academic Year 2568 │ │
│          │ │  [Rollover →] [แก้ไข]                   │ │
│          │ └──────────────────────────────────────────┘ │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │  ○ ARCHIVED — กลางภาค 2/2568            │ │
│          │ │  Midterm · ...                           │ │
│          │ │  [Restore] [ลบ]                         │ │
│          │ └──────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

---

# 🧩 3. COMPONENT DEFINITIONS

## 3.1 Stat Card

```json
{
  "component": "StatCard",
  "props": {
    "icon": "emoji | svg",
    "icon_bg": "color (CSS var)",
    "value": "number | string",
    "label": "string",
    "sub_label": "string",
    "progress": {
      "value": 0.75,
      "color": "var(--crimson)"
    }
  },
  "variants": ["default", "with-progress", "with-badge"]
}
```

## 3.2 Badge

```json
{
  "component": "Badge",
  "variants": {
    "badge-navy":   { "bg": "#0f1b35", "text": "#fff" },
    "badge-crimson":{ "bg": "#c41230", "text": "#fff" },
    "badge-gold":   { "bg": "#b8860b", "text": "#fff" },
    "badge-green":  { "bg": "#198754", "text": "#fff" },
    "badge-gray":   { "bg": "#6c757d", "text": "#fff" },
    "badge-blue":   { "bg": "#0d6efd", "text": "#fff" }
  },
  "size": ["sm", "md"],
  "pill": true
}
```

## 3.3 Button

```json
{
  "component": "Button",
  "variants": {
    "btn-primary":  { "bg": "var(--crimson)", "hover": "var(--crimson-dk)" },
    "btn-navy":     { "bg": "var(--navy)", "hover": "var(--navy-mid)" },
    "btn-gold":     { "bg": "var(--gold)", "text": "#fff" },
    "btn-outline":  { "border": "var(--border)", "bg": "transparent" },
    "btn-danger":   { "bg": "#dc3545" },
    "btn-ghost":    { "bg": "transparent", "hover": "var(--surface2)" }
  },
  "sizes": ["btn-sm", "btn-md (default)", "btn-lg"],
  "states": ["default", "loading (spinner)", "disabled"]
}
```

## 3.4 Schedule Card

```json
{
  "component": "ScheduleCard",
  "props": {
    "course_code": "string",
    "course_name": "string",
    "section_no": "string",
    "exam_date": "date",
    "exam_time": "string (HH.MM-HH.MM)",
    "room": "string",
    "num_students": "number",
    "total_sheets": "number",
    "teacher": "User",
    "supervisors": "User[]",
    "status": "draft | published | confirmed | cancelled",
    "actions": ["view", "edit", "cancel"]
  },
  "status_colors": {
    "draft":     "var(--text-muted)",
    "published": "var(--blue)",
    "confirmed": "var(--green)",
    "cancelled": "var(--crimson)"
  }
}
```

## 3.5 Submission Card

```json
{
  "component": "SubmissionCard",
  "props": {
    "section": "Section",
    "status": "draft | pending | approved | rejected | revision",
    "submitted_at": "datetime | null",
    "reviewer": "User | null",
    "file_count": "number",
    "has_messages": "boolean"
  },
  "actions": {
    "not_submitted": ["+ ส่งข้อสอบ"],
    "draft":         ["แก้ไขร่าง", "ส่ง"],
    "pending":       ["ดูรายละเอียด", "💬 ข้อความ"],
    "approved":      ["ดูไฟล์"],
    "rejected":      ["แก้ไขและส่งใหม่", "💬 ข้อความ"],
    "revision":      ["แก้ไข", "💬 ข้อความ"]
  }
}
```

## 3.6 Swap Request Card

```json
{
  "component": "SwapCard",
  "types": ["incoming", "outgoing"],
  "props": {
    "requester": "User",
    "target": "User",
    "from_schedule": "ExamSchedule",
    "to_schedule": "ExamSchedule",
    "reason": "string",
    "status": "pending | approved | rejected | cancelled",
    "created_at": "datetime"
  },
  "actions": {
    "incoming_pending": ["✓ ยอมรับ", "✗ ปฏิเสธ", "💬 ข้อความ"],
    "outgoing_pending": ["ยกเลิกคำขอ"],
    "resolved":         ["ดูประวัติ"]
  }
}
```

## 3.7 Data Table

```json
{
  "component": "DataTable",
  "props": {
    "columns": [
      { "key": "string", "label": "string", "sortable": true, "width": "string" }
    ],
    "rows": "array",
    "selectable": true,
    "pagination": { "page": 1, "per_page": 20, "total": "number" },
    "empty_state": { "icon": "emoji", "message": "string", "action": "Button?" }
  }
}
```

## 3.8 Toast Notification

```json
{
  "component": "Toast",
  "variants": ["success", "error", "warning", "info"],
  "props": {
    "message": "string",
    "duration": 3000,
    "position": "bottom-right"
  }
}
```

## 3.9 Modal

```json
{
  "component": "Modal",
  "sizes": ["sm (400px)", "md (560px)", "lg (720px)", "fullscreen"],
  "props": {
    "title": "string",
    "closable": true,
    "footer": { "cancel": "Button", "confirm": "Button" }
  }
}
```

## 3.10 Analytics Chart (Canvas-based)

```json
{
  "component": "DonutChart",
  "props": {
    "segments": "number[]",
    "labels": "string[]",
    "colors": "string[]",
    "center_label": "string",
    "legend": true
  }
},
{
  "component": "BarChart",
  "props": {
    "labels": "string[]",
    "values": "number[]",
    "color": "string",
    "orientation": "vertical | horizontal"
  }
}
```

---

# 🎨 4. DESIGN SYSTEM

## 4.1 Color Tokens

```css
/* Brand */
--navy:        #0f1b35   /* Primary brand — sidebar, headers */
--navy-mid:    #1a2d52   /* Hover state */
--navy-light:  #2a4278   /* Active nav item */
--crimson:     #c41230   /* Primary action, brand accent */
--crimson-dk:  #9a0d24   /* Hover crimson */
--crimson-lt:  rgba(196,18,48,0.08)   /* Icon backgrounds */
--gold:        #b8860b   /* Warning, premium states */
--gold-lt:     rgba(184,134,11,0.10)  /* Gold background tint */

/* Semantic */
--success:     #198754   /* Approved, confirmed, check-in done */
--success-lt:  rgba(26,122,74,0.10)
--warning:     #b8860b   /* Pending, draft */
--error:       #c41230   /* Rejected, danger */
--info:        #0d6efd   /* Published, informational */

/* Surface */
--bg:          #f5f4f0   /* Page background (warm off-white) */
--surface:     #ffffff   /* Card surface */
--surface2:    #f9f8f5   /* Nested surface */
--border:      #e8e6e0   /* Dividers, card borders */

/* Text */
--text:        #1a1a1a   /* Primary */
--text-mid:    #4a4a4a   /* Secondary */
--text-muted:  #888880   /* Placeholder, disabled */
```

## 4.2 Typography

```
Font Family (Thai+Latin): IBM Plex Sans Thai
Font Monospace:           IBM Plex Mono

Scale:
  --text-xs:   11px / line-height 1.4
  --text-sm:   13px / line-height 1.5
  --text-base: 14px / line-height 1.6  ← default
  --text-md:   15px / line-height 1.6
  --text-lg:   18px / line-height 1.5
  --text-xl:   22px / line-height 1.3
  --text-2xl:  28px / line-height 1.2
  --text-3xl:  36px / line-height 1.1

Weights:
  300 — Light (body long-form)
  400 — Regular (default)
  500 — Medium (labels, nav items)
  600 — Semibold (card titles, headings)
  700 — Bold (stat values, emphasis)
```

## 4.3 Spacing System

```
Base unit: 4px
  --sp-1:  4px
  --sp-2:  8px
  --sp-3:  12px
  --sp-4:  16px
  --sp-5:  20px
  --sp-6:  24px
  --sp-8:  32px
  --sp-10: 40px
  --sp-12: 48px

Component spacing:
  Card padding:        20px 24px
  Card header height:  52px
  Sidebar width:       220px (collapsed: 60px)
  Topbar height:       56px
  Border radius:       8px (cards), 6px (buttons), 4px (badges)
```

## 4.4 Shadow Scale

```
--shadow-sm: 0 1px 4px rgba(15,27,53,0.06)
--shadow:    0 2px 12px rgba(15,27,53,0.08)
--shadow-lg: 0 8px 32px rgba(15,27,53,0.14)
--shadow-xl: 0 16px 48px rgba(15,27,53,0.18)
```

## 4.5 Status Color Map

```
Submission Status:
  draft     → gray    (#6c757d)
  pending   → gold    (#b8860b)
  approved  → green   (#198754)
  rejected  → crimson (#c41230)
  revision  → orange  (#fd7e14)

Schedule Status:
  draft     → gray
  published → blue   (#0d6efd)
  confirmed → green
  cancelled → crimson + strikethrough

Swap Status:
  pending   → gold
  approved  → green
  rejected  → crimson
  cancelled → gray
```

---

# 🔁 5. INTERACTION PATTERNS

## 5.1 Navigation

```
Trigger: Click nav item
Action:  navigate(route) → load page content into #content
State:   nav item gets .active class
         previous content replaced (SPA, no reload)
Feedback: none (instant)
```

## 5.2 Form Submit

```
Trigger:  Click submit button
Actions:
  1. Disable button + show spinner
  2. Validate client-side → show inline errors if fail
  3. POST to API
  4. On success:
     - Close modal (if modal)
     - Toast success message (3s, bottom-right)
     - Refresh data (reload page section)
  5. On error:
     - Re-enable button
     - Toast error with message from API
     - Highlight fields if field-specific error
```

## 5.3 Destructive Action (Delete / Deactivate)

```
Trigger:  Click destructive button
Action:
  1. Show confirm dialog:
     "คุณแน่ใจหรือไม่? การกระทำนี้ไม่สามารถยกเลิกได้"
     [ยกเลิก] [ยืนยัน (crimson)]
  2. On confirm: proceed with DELETE request
  3. On success: toast + remove item from list
```

## 5.4 Check-in Flow

```
Trigger: Click [Check-in ด้วย GPS]
Step 1: Browser geolocation request
Step 2: Show modal with:
        - Current coordinates (loading → found)
        - Distance to exam room
        - ✅ if within 200m, ⚠️ if too far
Step 3: Confirm → POST /checkins/{schedule_id}/checkin
Step 4: Card updates to "✅ Check-in แล้ว HH:MM"
```

## 5.5 Swap Request Flow

```
Teacher/Staff initiates:
  1. Click [+ ขอสลับ]
  2. Select: กะที่ฉันต้องการสลับออก
  3. Select: กะที่ต้องการ (ของคนอื่น) หรือ ค้นหาชื่อ
  4. กรอกเหตุผล
  5. Submit → status: pending
  
Target receives:
  1. Badge +1 บน nav swap
  2. Toast notification
  3. Incoming card → [ยอมรับ] / [ปฏิเสธ]
  4. On accept → status: approved → both schedules swap
```

## 5.6 View-As (Admin only)

```
Trigger: Click role pill / "เปลี่ยนมุมมอง" button
Action:
  1. Show role selector overlay
  2. Select role (staff / teacher / student)
  3. POST /auth/view-as {role}
  4. Navigate to dashboard
  5. Show "ดูในฐานะ: [role]" banner (persistent)
  6. Nav redraws to match selected role

Reset: Click "✖ มุมมองตัวเอง"
```

## 5.7 Loading States

```
Page load:   Skeleton screens (gray pulse animations)
API call:    Spinner overlay on component
Button:      Inline spinner, text changes to "กำลังโหลด..."
Table:       Row shimmer effect
Chart:       Placeholder rectangle → fade in when data ready
```

## 5.8 Empty States

```
Pattern: Icon (large, muted) + message + optional CTA button

Examples:
  Schedule empty: 📅 "ยังไม่มีตารางสอบในรอบนี้" [+ จัดตาราง]
  Submissions empty: 📤 "ยังไม่มี submission" [+ ส่งข้อสอบ]
  Swap empty: 🔄 "ไม่มีคำขอสลับ" [+ ขอสลับ]
  Search no result: 🔍 "ไม่พบข้อมูล กรุณาลองใหม่"
```

## 5.9 Error States

```
Network error:    Toast "ไม่สามารถเชื่อมต่อ server ได้" (error)
401 Unauthorized: Auto logout → redirect to login
403 Forbidden:    Toast "คุณไม่มีสิทธิ์ดำเนินการนี้"
404 Not Found:    Inline "ไม่พบข้อมูลที่ต้องการ"
422 Validation:   Inline field errors below each input
500 Server Error: Toast "เกิดข้อผิดพลาดของระบบ กรุณาลองอีกครั้ง"
```

---

# 🧾 6. UI JSON (STITCH READY)

```json
{
  "app": "EMS — ระบบจัดการข้อสอบ มช.",
  "version": "2.0.0",
  "locale": "th-TH",
  "auth": {
    "type": "cookie_session",
    "login_endpoint": "/api/auth/login",
    "logout_endpoint": "/api/auth/logout",
    "me_endpoint": "/api/auth/me",
    "cookie_name": "ems_session"
  },
  "design_system": {
    "font_primary": "IBM Plex Sans Thai",
    "font_mono": "IBM Plex Mono",
    "colors": {
      "primary": "#0f1b35",
      "accent": "#c41230",
      "warning": "#b8860b",
      "success": "#198754",
      "error": "#c41230",
      "info": "#0d6efd",
      "background": "#f5f4f0",
      "surface": "#ffffff",
      "border": "#e8e6e0",
      "text": "#1a1a1a",
      "text_muted": "#888880"
    },
    "border_radius": "8px",
    "spacing_unit": "4px"
  },
  "layout": {
    "type": "sidebar_fixed",
    "sidebar_width": 220,
    "topbar_height": 56,
    "sidebar_collapsible": true
  },
  "roles": ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher", "student"],
  "pages": [
    {
      "id": "login",
      "name": "Login",
      "route": "/login",
      "layout": "centered",
      "public": true,
      "components": [
        {
          "type": "logo",
          "src": "/static/logo.png",
          "alt": "มช. คณะรัฐศาสตร์"
        },
        {
          "type": "heading",
          "text": "EMS — ระบบจัดการข้อสอบ",
          "sub": "คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มช."
        },
        {
          "type": "form",
          "id": "login-form",
          "action": "POST /api/auth/login",
          "fields": [
            { "name": "username", "type": "text", "label": "ชื่อผู้ใช้ (CMU Account)", "placeholder": "firstname.lastname", "required": true },
            { "name": "password", "type": "password", "label": "รหัสผ่าน", "show_toggle": true, "required": true }
          ],
          "submit": { "label": "เข้าสู่ระบบ", "variant": "btn-primary", "full_width": true },
          "on_success": "redirect_by_role",
          "error_states": {
            "401": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง",
            "429": "เกินจำนวนครั้ง กรุณารอ {retry_after} วินาที"
          }
        },
        {
          "type": "divider", "text": "หรือ"
        },
        {
          "type": "button",
          "label": "เข้าสู่ระบบด้วย CMU SSO",
          "variant": "btn-outline",
          "action": "GET /api/auth/sso/login",
          "full_width": true
        }
      ]
    },
    {
      "id": "dashboard",
      "name": "แดชบอร์ด",
      "route": "/dashboard",
      "roles": ["admin", "esq_head", "secretary", "dept_supervisor", "staff"],
      "layout": {
        "type": "main_content",
        "sections": ["stat_grid", "analytics", "audit_log"]
      },
      "components": [
        {
          "type": "stat_grid",
          "columns": 4,
          "data_source": "GET /api/dashboard",
          "query_params": { "semester": "2", "academic_year": "2568" },
          "cards": [
            { "key": "total_sections", "label": "Sections ทั้งหมด", "icon": "📚", "icon_bg": "var(--crimson-lt)", "sub_key": "scheduled_sections", "sub_template": "{scheduled_sections} จัดแล้ว ({pct}%)", "progress_key": "pct" },
            { "key": "total_students", "label": "นักศึกษาทั้งหมด", "icon": "👨‍🎓", "icon_bg": "rgba(13,110,253,.08)", "sub_key": "total_teachers", "sub_template": "{total_teachers} อาจารย์" },
            { "key": "total_sheets", "label": "แผ่นถ่ายเอกสารรวม", "icon": "🖨️", "icon_bg": "var(--gold-lt)", "format": "number", "sub_key": "copy_cost", "sub_template": "฿{copy_cost}" },
            { "key": "rooms_in_use", "label": "ห้องสอบที่ใช้", "icon": "🏫", "icon_bg": "var(--green-lt)", "sub_key": "unscheduled_sections", "sub_template": "{unscheduled_sections} sections ยังไม่ได้จัด" }
          ]
        },
        {
          "type": "chart_grid",
          "columns": 2,
          "data_source": "GET /api/dashboard/analytics",
          "roles": ["admin"],
          "charts": [
            {
              "id": "chart-submission",
              "title": "📤 สถานะการส่งข้อสอบ (อาจารย์)",
              "type": "donut",
              "data_keys": ["submission_status", "teacher_stats"],
              "segments": ["draft","pending","approved","rejected","revision","not_submitted"],
              "colors": ["#6c757d","#b8860b","#198754","#c41230","#fd7e14","#dee2e6"]
            },
            {
              "id": "chart-supervision",
              "title": "✅ การยืนยันกำกับสอบ (เจ้าหน้าที่)",
              "type": "donut",
              "data_keys": ["supervision_stats"],
              "segments": ["confirmed","pending"],
              "colors": ["#198754","#6c757d"]
            },
            {
              "id": "chart-swap",
              "title": "🔄 คำขอสลับกะ",
              "type": "donut",
              "data_keys": ["swap_status"],
              "colors": { "pending":"#b8860b","approved":"#198754","rejected":"#c41230","cancelled":"#6c757d" }
            },
            {
              "id": "chart-copy",
              "title": "🖨️ ค่าถ่ายเอกสารต่อห้องสอบ",
              "type": "bar",
              "data_keys": ["copy_per_room"],
              "x_key": "room",
              "y_key": "sheets",
              "color": "#8b0000"
            }
          ]
        },
        {
          "type": "activity_log",
          "title": "📋 ประวัติการใช้งาน",
          "data_source": "GET /api/dashboard",
          "data_key": "recent_logs",
          "roles": ["admin"],
          "max_height": 320,
          "item_template": {
            "timestamp": "datetime",
            "action": "badge",
            "actor": "text"
          }
        }
      ]
    },
    {
      "id": "schedule",
      "name": "ตารางสอบ",
      "route": "/schedule",
      "roles": ["admin", "esq_head", "secretary", "dept_supervisor", "staff", "teacher"],
      "layout": { "type": "main_content" },
      "components": [
        {
          "type": "filter_bar",
          "filters": [
            { "name": "date", "type": "date_range", "label": "วันที่" },
            { "name": "room", "type": "select", "label": "ห้องสอบ", "data_source": "GET /api/schedule/rooms" },
            { "name": "teacher", "type": "search_select", "label": "อาจารย์" },
            { "name": "status", "type": "multi_select", "label": "สถานะ", "options": ["draft","published","confirmed","cancelled"] }
          ],
          "actions": [
            { "label": "ส่งออก Excel", "icon": "↓", "action": "GET /api/exports/schedule.xlsx" },
            { "label": "พิมพ์ PDF", "icon": "🖨️", "action": "GET /api/pdf/schedule" }
          ]
        },
        {
          "type": "schedule_list",
          "data_source": "GET /api/schedule/",
          "group_by": "exam_date",
          "item_component": "ScheduleCard",
          "empty_state": {
            "icon": "📅",
            "message": "ยังไม่มีตารางสอบในรอบนี้",
            "action": { "label": "+ จัดตาราง", "roles": ["admin"], "navigate": "optimizer" }
          }
        }
      ]
    },
    {
      "id": "submissions",
      "name": "ส่งข้อสอบ",
      "route": "/submissions",
      "roles": ["admin", "teacher", "dept_supervisor"],
      "components": [
        {
          "type": "tab_bar",
          "tabs": [
            { "label": "วิชาของฉัน", "roles": ["teacher"], "filter": "my_sections" },
            { "label": "ทั้งหมด", "roles": ["admin", "dept_supervisor"] }
          ]
        },
        {
          "type": "submission_list",
          "data_source": "GET /api/submissions/",
          "item_component": "SubmissionCard",
          "empty_state": { "icon": "📤", "message": "ยังไม่มี submission", "action": { "label": "+ ส่งข้อสอบ" } }
        }
      ],
      "modals": [
        {
          "id": "submission-form",
          "title": "ส่งข้อสอบ",
          "size": "md",
          "trigger": "SubmissionCard[status=not_submitted] → click",
          "form": {
            "action": "POST /api/submissions/",
            "fields": [
              { "name": "exam_type", "type": "select", "label": "ประเภทข้อสอบ", "options": ["ปรนัย","อัตนัย","ปรนัย+อัตนัย"] },
              { "name": "num_questions", "type": "number", "label": "จำนวนข้อ" },
              { "name": "duration_minutes", "type": "number", "label": "ระยะเวลา (นาที)" },
              { "name": "file", "type": "file", "label": "ไฟล์ข้อสอบ", "accept": ".pdf,.doc,.docx" },
              { "name": "note", "type": "textarea", "label": "หมายเหตุ" }
            ]
          }
        },
        {
          "id": "message-thread",
          "title": "ข้อความ",
          "size": "md",
          "data_source": "GET /api/submissions/{id}/messages",
          "send_action": "POST /api/submissions/{id}/messages"
        }
      ]
    },
    {
      "id": "swaps",
      "name": "การสลับกะ",
      "route": "/swaps",
      "roles": ["admin", "staff", "teacher"],
      "components": [
        {
          "type": "tab_bar",
          "tabs": [
            { "label": "รอตอบ", "badge_count": true, "filter": "pending" },
            { "label": "อนุมัติแล้ว", "filter": "approved" },
            { "label": "ทั้งหมด", "filter": "all" }
          ]
        },
        {
          "type": "swap_list",
          "data_source": "GET /api/swaps2/",
          "item_component": "SwapCard"
        }
      ],
      "actions": [
        { "type": "fab", "label": "+ ขอสลับ", "roles": ["staff","teacher"], "modal": "swap-request-form" }
      ],
      "modals": [
        {
          "id": "swap-request-form",
          "title": "ขอสลับกะ",
          "size": "md",
          "form": {
            "action": "POST /api/swaps2/",
            "fields": [
              { "name": "my_schedule_id", "type": "select", "label": "กะที่ฉันต้องการสลับออก", "data_source": "GET /api/schedule/my" },
              { "name": "target_schedule_id", "type": "search_select", "label": "กะที่ต้องการ", "data_source": "GET /api/schedule/" },
              { "name": "reason", "type": "textarea", "label": "เหตุผล", "required": true }
            ]
          }
        }
      ]
    },
    {
      "id": "checkins",
      "name": "Check-in วันสอบ",
      "route": "/checkins",
      "roles": ["admin", "staff", "teacher"],
      "components": [
        {
          "type": "section_header",
          "title": "📍 วันนี้",
          "subtitle": "datetime:today"
        },
        {
          "type": "checkin_list",
          "data_source": "GET /api/checkins/my-schedule",
          "item_component": "CheckinCard",
          "empty_state": { "icon": "✅", "message": "ไม่มีกำหนดสอบวันนี้" }
        }
      ],
      "modals": [
        {
          "id": "checkin-confirm",
          "title": "ยืนยัน Check-in",
          "size": "sm",
          "steps": [
            { "label": "ตรวจสอบ GPS", "async": true },
            { "label": "ยืนยัน", "action": "POST /api/checkins/{schedule_id}/checkin" }
          ]
        }
      ]
    },
    {
      "id": "student",
      "name": "ค้นหาตารางสอบ",
      "route": "/student-search",
      "public": true,
      "layout": "centered_search",
      "components": [
        {
          "type": "search_bar",
          "placeholder": "รหัสนักศึกษา หรือ ชื่อ-นามสกุล",
          "action": "GET /api/public/student-schedule",
          "param": "q"
        },
        {
          "type": "student_schedule_result",
          "data_key": "schedules",
          "empty_state": { "icon": "🔍", "message": "ไม่พบข้อมูล กรุณาลองใหม่" },
          "item_fields": ["course_code", "course_name", "exam_date", "exam_time", "room", "seat"]
        }
      ]
    },
    {
      "id": "users",
      "name": "จัดการผู้ใช้งาน",
      "route": "/users",
      "roles": ["admin"],
      "components": [
        {
          "type": "filter_bar",
          "filters": [
            { "name": "role", "type": "select", "options": ["admin","staff","teacher","student","esq_head","secretary","dept_supervisor"] },
            { "name": "dept", "type": "select", "label": "แผนก" },
            { "name": "is_active", "type": "toggle", "label": "เฉพาะ active" },
            { "name": "q", "type": "search", "placeholder": "ค้นชื่อหรือ username" }
          ]
        },
        {
          "type": "data_table",
          "data_source": "GET /api/users/",
          "columns": [
            { "key": "full_name", "label": "ชื่อ-สกุล", "sortable": true },
            { "key": "username", "label": "Username" },
            { "key": "role", "label": "Role", "render": "badge" },
            { "key": "dept_code", "label": "แผนก" },
            { "key": "is_active", "label": "สถานะ", "render": "status_dot" },
            { "key": "actions", "label": "", "render": "action_menu" }
          ],
          "row_actions": [
            { "label": "แก้ไข Role", "action": "modal:edit-user" },
            { "label": "Deactivate", "variant": "danger", "action": "POST /api/users/{id}/deactivate", "confirm": true }
          ]
        }
      ],
      "modals": [
        {
          "id": "edit-user",
          "title": "แก้ไขข้อมูลผู้ใช้",
          "size": "sm",
          "form": {
            "action": "PUT /api/users/{id}",
            "fields": [
              { "name": "role", "type": "select", "options": ["admin","staff","teacher","student","esq_head","secretary","dept_supervisor"] },
              { "name": "dept_code", "type": "text", "label": "รหัสแผนก" },
              { "name": "special_role", "type": "select", "label": "Special Role", "options": ["", "room_keeper", "esq_staff"] }
            ]
          }
        }
      ]
    },
    {
      "id": "period",
      "name": "รอบสอบ",
      "route": "/period",
      "roles": ["admin"],
      "components": [
        {
          "type": "period_list",
          "data_source": "GET /api/period/",
          "item_fields": ["label","academic_year","semester","exam_type","is_active"],
          "actions_per_item": [
            { "label": "Activate", "condition": "!is_active", "action": "POST /api/period/{id}/activate" },
            { "label": "Rollover →", "condition": "is_active", "action": "modal:rollover" }
          ]
        }
      ],
      "header_actions": [
        { "label": "+ สร้างรอบ", "modal": "create-period" }
      ],
      "modals": [
        {
          "id": "create-period",
          "title": "สร้างรอบสอบใหม่",
          "size": "sm",
          "form": {
            "action": "POST /api/period/",
            "fields": [
              { "name": "academic_year", "type": "text", "label": "ปีการศึกษา", "placeholder": "2568" },
              { "name": "semester", "type": "select", "options": ["1","2","summer"] },
              { "name": "exam_type", "type": "select", "options": ["midterm","final"] },
              { "name": "label", "type": "text", "label": "ชื่อรอบ (optional)", "placeholder": "ปลายภาค 2/2568" }
            ]
          }
        }
      ]
    },
    {
      "id": "optimizer",
      "name": "จัดตารางสอบ",
      "route": "/optimizer",
      "roles": ["admin"],
      "layout": { "type": "stepper", "steps": 4 },
      "steps": [
        { "index": 1, "title": "ยืนยันข้อมูล", "data_source": "GET /api/dashboard" },
        { "index": 2, "title": "Constraints", "form_fields": ["no_teacher_overlap","capacity_constraint","max_shifts_per_staff"] },
        { "index": 3, "title": "Run", "action": "POST /api/scheduler/run", "shows_progress": true },
        { "index": 4, "title": "ผลลัพธ์", "data_source": "GET /api/scheduler/result", "actions": ["confirm","re-run","export"] }
      ]
    },
    {
      "id": "settings",
      "name": "ตั้งค่าระบบ",
      "route": "/settings",
      "roles": ["admin"],
      "components": [
        {
          "type": "settings_group",
          "title": "การส่งข้อสอบ",
          "settings": [
            { "key": "exam_submission_deadline", "label": "Deadline ส่งข้อสอบ", "type": "datetime" },
            { "key": "allow_late_submission", "label": "อนุญาตส่งช้า", "type": "toggle" }
          ],
          "data_source": "GET /api/settings/",
          "save_action": "PUT /api/settings/{key}"
        },
        {
          "type": "settings_group",
          "title": "ความปลอดภัย",
          "settings": [
            { "key": "session_timeout_hours", "label": "Session timeout (ชั่วโมง)", "type": "number" }
          ]
        }
      ]
    }
  ],
  "global_components": {
    "sidebar": {
      "type": "fixed_sidebar",
      "logo": { "text": "EMS", "sub": "คณะรัฐศาสตร์ มช." },
      "nav_groups": [
        {
          "label": "ภาพรวม",
          "items": [
            { "id": "nav-dashboard", "icon": "📊", "label": "แดชบอร์ด", "route": "dashboard" },
            { "id": "nav-schedule-all", "icon": "📅", "label": "ตารางสอบ", "route": "schedule" }
          ]
        },
        {
          "label": "งานของฉัน",
          "items": [
            { "id": "nav-my-exam", "icon": "📋", "label": "จัดการสอบ", "route": "myexam", "roles": ["teacher"] },
            { "id": "nav-submissions", "icon": "📤", "label": "ส่งข้อสอบ", "route": "submissions", "roles": ["teacher","admin"] },
            { "id": "nav-swap", "icon": "🔄", "label": "สลับคุมสอบ", "route": "swaps", "badge": "swap_pending_count" },
            { "id": "nav-checkin", "icon": "✅", "label": "Check-in วันสอบ", "route": "checkins" },
            { "id": "nav-student-search", "icon": "🔍", "label": "ค้นหาตารางสอบ", "route": "student" }
          ]
        },
        {
          "label": "ข้อมูล",
          "items": [
            { "id": "nav-sections", "icon": "📚", "label": "รายวิชา / Sections", "route": "sections", "roles": ["admin","teacher"] },
            { "id": "nav-copy", "icon": "🖩", "label": "คำนวณค่าถ่าย", "route": "copy", "roles": ["admin","staff"] }
          ]
        },
        {
          "label": "วางแผนสอบ",
          "roles": ["admin"],
          "items": [
            { "id": "nav-optimizer", "icon": "🎯", "label": "จัดตารางสอบ", "route": "optimizer" },
            { "id": "nav-coexam", "icon": "🔗", "label": "Co-Exam", "route": "coexam" },
            { "id": "nav-workflow", "icon": "📋", "label": "ยืนยันตาราง", "route": "workflow" },
            { "id": "nav-external", "icon": "🏛️", "label": "สอบพิเศษ", "route": "external" }
          ]
        },
        {
          "label": "ระบบ",
          "roles": ["admin"],
          "items": [
            { "id": "nav-import", "icon": "📥", "label": "นำเข้าข้อมูล", "route": "import" },
            { "id": "nav-period", "icon": "🗓️", "label": "รอบสอบ", "route": "period" },
            { "id": "nav-settings", "icon": "⚙️", "label": "ตั้งค่าระบบ", "route": "settings" },
            { "id": "nav-users", "icon": "👥", "label": "ผู้ใช้งาน", "route": "users" }
          ]
        }
      ],
      "footer": [
        { "label": "ออกจากระบบ", "icon": "🚪", "action": "POST /api/auth/logout" }
      ]
    },
    "topbar": {
      "left": "page_title",
      "center": "period_badge (active period label)",
      "right": {
        "user_pill": {
          "name": "currentUser.full_name",
          "role": "effective_role_label",
          "on_click": "toggle_viewas_panel (admin only)"
        },
        "view_as_banner": {
          "show_when": "currentUser.view_as_role != null",
          "text": "ดูในฐานะ: {view_as_role}",
          "reset_action": "POST /api/auth/view-as {role: null}"
        }
      }
    },
    "toast": {
      "position": "bottom-right",
      "duration": 3000,
      "variants": ["success", "error", "warning", "info"]
    },
    "mobile_bottom_nav": {
      "show_breakpoint": "768px",
      "items": [
        { "icon": "📊", "label": "หน้าหลัก", "route": "dashboard" },
        { "icon": "📅", "label": "ตาราง", "route": "schedule" },
        { "icon": "📤", "label": "ส่งงาน", "route": "submissions" },
        { "icon": "🔄", "label": "สลับ", "route": "swaps", "badge": true },
        { "icon": "✅", "label": "Check-in", "route": "checkins" }
      ]
    }
  }
}
```

---

# 📁 7. FRONTEND STRUCTURE

## 7.1 Recommended Folder Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── Sidebar.js
│   │   ├── Topbar.js
│   │   ├── MobileBottomNav.js
│   │   └── ViewAsBanner.js
│   ├── ui/
│   │   ├── Badge.js
│   │   ├── Button.js
│   │   ├── Modal.js
│   │   ├── Toast.js
│   │   ├── StatCard.js
│   │   ├── DataTable.js
│   │   ├── FilterBar.js
│   │   ├── Tabs.js
│   │   ├── Skeleton.js
│   │   └── EmptyState.js
│   ├── charts/
│   │   ├── DonutChart.js
│   │   ├── BarChart.js
│   │   └── ChartGrid.js
│   ├── schedule/
│   │   ├── ScheduleCard.js
│   │   ├── ScheduleList.js
│   │   └── ScheduleFilter.js
│   ├── submissions/
│   │   ├── SubmissionCard.js
│   │   ├── SubmissionForm.js
│   │   └── MessageThread.js
│   ├── swaps/
│   │   ├── SwapCard.js
│   │   └── SwapRequestForm.js
│   └── checkins/
│       ├── CheckinCard.js
│       └── CheckinModal.js
│
├── pages/
│   ├── Login.js
│   ├── Dashboard/
│   │   ├── AdminDashboard.js
│   │   └── StaffDashboard.js
│   ├── Schedule.js
│   ├── Submissions.js
│   ├── Swaps.js
│   ├── Checkins.js
│   ├── StudentSearch.js
│   ├── Users.js
│   ├── Settings.js
│   ├── Period.js
│   ├── Optimizer.js
│   ├── CoExam.js
│   ├── Workflow.js
│   ├── Import.js
│   └── External.js
│
├── services/
│   ├── api.js              ← base fetch wrapper (credentials: 'include')
│   ├── auth.service.js     ← login, logout, me, view-as
│   ├── dashboard.service.js
│   ├── schedule.service.js
│   ├── submission.service.js
│   ├── swap.service.js
│   ├── checkin.service.js
│   ├── user.service.js
│   ├── period.service.js
│   └── settings.service.js
│
├── store/
│   ├── auth.store.js       ← currentUser, effective_role
│   ├── ui.store.js         ← toast queue, modal state, nav state
│   └── period.store.js     ← active period (cached)
│
├── utils/
│   ├── esc.js              ← HTML escape (XSS defense)
│   ├── format.js           ← date, number, currency formatters
│   ├── roles.js            ← role checks (isAdmin, isTeacher etc.)
│   └── gps.js              ← geolocation wrapper
│
└── styles/
    ├── tokens.css          ← CSS custom properties (design tokens)
    ├── layout.css
    ├── components.css
    └── utilities.css
```

## 7.2 API Integration Pattern

```javascript
// services/api.js
const BASE = '/api';

async function request(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    credentials: 'include',       // HttpOnly cookie auth
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401) {
    authStore.logout();            // clear state + redirect /login
    return null;
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new ApiError(res.status, data.detail || 'เกิดข้อผิดพลาด');
  }

  return data;
}

export const get  = (path)       => request('GET', path);
export const post = (path, body) => request('POST', path, body);
export const put  = (path, body) => request('PUT', path, body);
export const del  = (path)       => request('DELETE', path);
```

## 7.3 Role Guard Pattern

```javascript
// utils/roles.js
export const ROLE_HIERARCHY = {
  admin: 5, esq_head: 4, secretary: 3,
  dept_supervisor: 3, staff: 2, teacher: 2, student: 1
};

export function can(user, action) {
  const role = user?.view_as_role || user?.role;
  const guards = {
    'view:all_submissions':  ['admin','esq_head','secretary','dept_supervisor'],
    'write:schedule':        ['admin'],
    'approve:submission':    ['admin','dept_supervisor'],
    'view:audit_logs':       ['admin'],
    'checkin:confirm':       ['admin','staff','teacher'],
  };
  return guards[action]?.includes(role) ?? false;
}
```

## 7.4 Toast Usage Pattern

```javascript
// Called anywhere in app
import { toast } from '@/store/ui.store';

// Success
toast('ส่งข้อสอบเรียบร้อย', 'success');

// Error (from catch)
toast(err.message || 'เกิดข้อผิดพลาด', 'error');

// Warning
toast('กรุณากรอกข้อมูลให้ครบ', 'warning');
```

## 7.5 Page Skeleton Pattern

```javascript
// Every page follows this pattern:
async function loadPage() {
  showSkeleton();             // render gray placeholder
  try {
    const data = await PageService.getData();
    render(data);             // replace skeleton with real content
  } catch (err) {
    renderError(err.message); // show error state
  }
}
```

---

## P12 — Sections (รายวิชา / Sections)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: รายวิชา / Sections    [+ เพิ่ม]     │
│          ├──────────────────────────────────────────────┤
│          │ FILTER: [รหัสวิชา 🔍] [ปีการศึกษา ▼] [ภาค ▼]│
│          ├──────────────────────────────────────────────┤
│          │ TABLE:                                       │
│          │ รหัสวิชา | ชื่อวิชา | ตอน | อาจารย์ | นศ. │
│          │ ──────────────────────────────────────────── │
│          │ 126201 | การเมืองการปกครอง | 1 | อ.ปัยลิน | 30│
│          │ 126211 | การเมืองเปรียบเทียบ| 1 | อ.นฤทธ์ |105│
│          │ ...                                          │
│          │                                              │
│          │ ROW ACTIONS: [ดูตาราง] [แก้ไข] [มอบหมาย]   │
└──────────┴──────────────────────────────────────────────┘
```

**Section Detail Expand (inline):**
```
  ▼ 126201 การเมืองการปกครอง — ตอน 1
    ห้องสอบ: PSB 1101   |   วันสอบ: 19 มี.ค. 08.00-11.00
    ผู้คุมสอบ: อ.ปัยลิน + เจ้าหน้าที่สุดา
    Submission: ● pending (ส่งแล้ว 5 เม.ย.)
    [ดู Submission] [แก้ไขห้อง] [มอบหมายผู้รับผิดชอบ]
```

**States:**
- Empty: "ยังไม่มี sections — กรุณา Import ข้อมูลก่อน" → [นำเข้าข้อมูล]
- Loading: table row skeletons (5 rows)

---

## P13 — Copy Cost Calculator (คำนวณค่าถ่าย)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: คำนวณค่าถ่ายเอกสาร                 │
│          ├──────────────────────────────────────────────┤
│          │ SUMMARY BAR:                                 │
│          │ แผ่นรวม: 10,361  |  ค่าใช้จ่ายรวม: ฿5,180.50│
│          │ [Export Excel ↓]  [พิมพ์รายงาน]            │
│          ├──────────────────────────────────────────────┤
│          │ TABLE:                                       │
│          │ วิชา | ตอน | ห้อง | นศ. | หน้า | แผ่น | ค่า│
│          │ ─────────────────────────────────────────── │
│          │ 126201 | 1 | PSB1101 | 30 | 3 | 90 | ฿45   │
│          │ 126211 | 1 | AUD50ปี | 105| 10 |1050| ฿525  │
│          │ ...                                          │
│          │ ──────────────────────── รวม | 10,361|฿5,180│
│          │                                              │
│          │ ┌──────────────────────────────────────────┐│
│          │ │  ⚙ ปรับราคาต่อแผ่น: [0.50] บาท  [บันทึก]││
│          │ └──────────────────────────────────────────┘│
└──────────┴──────────────────────────────────────────────┘
```

**Inline Calculation:**
- แผ่น = num_students × num_pages
- ค่า = แผ่น × ราคาต่อแผ่น (default 0.50 บาท, configurable)
- แบบฟอร์มทุจริต +150 แผ่น (fixed overhead, shown separately)

---

## P14 — Workflow (ยืนยันตาราง / ลงนาม)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: ยืนยันตารางสอบ                      │
│          ├──────────────────────────────────────────────┤
│          │ PROGRESS STEPPER:                            │
│          │ [1.จัดตาราง ✓]→[2.Optimize ✓]→[3.Sign ●]→[4.Open Swap]│
│          ├──────────────────────────────────────────────┤
│          │ ┌──────────────────────────────────────────┐ │
│          │ │  📋 ลายเซ็นดิจิทัล                      │ │
│          │ │  ─────────────────────────────────────── │ │
│          │ │  ✅ Admin: อติกานต์ แสงวิลัย  (7 เม.ย.) │ │
│          │ │  ⏳ ESQ Head: นภาพร  (รอลงนาม)         │ │
│          │ │  ⏳ Secretary: (รอ)                     │ │
│          │ │                                          │ │
│          │ │  [🖊 ลงนามตาราง]  (ถ้าเป็น role ที่ต้อง)│ │
│          │ └──────────────────────────────────────────┘ │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │  📅 ภาพรวมตารางสอบ (read-only preview)  │ │
│          │ │  [filter: date / room]                   │ │
│          │ │  [schedule cards — compact view]         │ │
│          │ └──────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

**Signer Roles:** admin → esq_head → secretary (sequential)
**After all signed:** ปุ่ม [เปิด Swap] ปรากฏสำหรับ admin

---

## P15 — Co-Exam (จัดกลุ่มวิชาสอบร่วม)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: Co-Exam Groups         [+ สร้างกลุ่ม]│
│          ├──────────────────────────────────────────────┤
│          │ [🔍 ตรวจหากลุ่มอัตโนมัติ]                  │
│          │                                              │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │ 🔗 กลุ่ม: 126201+126202 (วิชาเดียวกัน) │ │
│          │ │ 19 มี.ค. 08.00-11.00 | PSB 1101          │ │
│          │ │ Sections: [126201-1] [126202-1]           │ │
│          │ │ นักศึกษารวม: 73 คน                      │ │
│          │ │ [+ เพิ่ม Section] [แก้ไข] [ลบกลุ่ม]    │ │
│          │ └──────────────────────────────────────────┘ │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │ 🔗 กลุ่ม: อ.นฤทธ์ (อาจารย์เดียว)       │ │
│          │ │ 26 มี.ค. 12.00-15.00 | AUD 50ปี         │ │
│          │ │ Sections: [126211-1] [127100-1]           │ │
│          │ │ นักศึกษารวม: 176 คน                     │ │
│          │ │ [+ เพิ่ม Section] [แก้ไข] [ลบกลุ่ม]    │ │
│          │ └──────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

**Auto-Detect Panel (slide-in):**
```
┌──────────────────────────────────────────┐
│  🔍 ตรวจพบกลุ่มที่ควรรวม           [×] │
├──────────────────────────────────────────┤
│  [✓] 126201+126202 — วันเดียว อ.เดียว  │
│  [✓] 127100-1 + 127100-801 — วิชาเดียว │
│  [ ] 126324+128305 — ห้องเดียว (manual)│
│                                          │
│  [สร้างกลุ่มที่เลือก]                  │
└──────────────────────────────────────────┘
```

---

## P16 — Print Review (ตรวจก่อนพิมพ์)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: ตรวจก่อนพิมพ์                      │
│          ├──────────────────────────────────────────────┤
│          │ FILTER: [ห้อง ▼] [วันที่ ▼] [สถานะ ▼]      │
│          ├──────────────────────────────────────────────┤
│          │ TABLE:                                       │
│          │ วิชา | ห้อง | วันที่ | แผ่น | Submission | ✓│
│          │ ──────────────────────────────────────────── │
│          │ 126201|PSB1101|19มี.ค.|90|✅approved|[พิมพ์]│
│          │ 126211|AUD50ปี|19มี.ค.|1050|⏳pending|[รอ] │
│          │ 127100|PSB1204|26มี.ค.|710|✅approved|[พิมพ์]│
│          │                                              │
│          │ BATCH ACTIONS:                               │
│          │ [☑ เลือกทั้งหมดที่ approved]                │
│          │ [🖨 พิมพ์ที่เลือก (PDF)]                    │
└──────────┴──────────────────────────────────────────────┘
```

**Per-row actions:**
- `approved` → [🖨 พิมพ์ PDF] [👁 Preview]
- `pending` → [รอ Submission] (disabled, gold)
- `rejected` → [⚠ ต้องแก้ไขก่อน] (red)

---

## P17 — Import (นำเข้าข้อมูล)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: นำเข้าข้อมูล                       │
│          ├──────────────────────────────────────────────┤
│          │ TABS: [นักศึกษา] [Sections] [ห้องสอบ]      │
│          ├──────────────────────────────────────────────┤
│          │                                              │
│          │  TAB: นักศึกษา                              │
│          │  ┌────────────────────────────────────────┐ │
│          │  │  📥 ลากไฟล์ Excel ที่นี่               │ │
│          │  │  หรือ [เลือกไฟล์]                      │ │
│          │  │  รองรับ: .xlsx, .csv (max 10MB)        │ │
│          │  └────────────────────────────────────────┘ │
│          │                                              │
│          │  PREVIEW (หลังเลือกไฟล์):                  │
│          │  ┌────────────────────────────────────────┐ │
│          │  │ รหัสนศ. | ชื่อ | วิชา | ตอน          │ │
│          │  │ 640310001| สมชาย | 126201 | 1         │ │
│          │  │ ...    (แสดง 10 แถวแรก)               │ │
│          │  │ รวม: 1,023 แถว  ⚠ ซ้ำ: 3 แถว         │ │
│          │  └────────────────────────────────────────┘ │
│          │  [ยกเลิก]        [นำเข้า (1,020 แถว)]     │
│          │                                              │
│          │  IMPORT HISTORY:                            │
│          │  7 เม.ย. 09:20 — students.xlsx — 1,023 rows│
└──────────┴──────────────────────────────────────────────┘
```

**Import Progress Modal:**
```
┌──────────────────────────────────────┐
│  กำลังนำเข้าข้อมูล...          [×] │
├──────────────────────────────────────┤
│  ████████████░░░░  780 / 1,023      │
│  ✅ บันทึกแล้ว: 780                 │
│  ⚠ ซ้ำ ข้าม: 3                     │
│  ⏳ เหลือ: 240                      │
└──────────────────────────────────────┘
```

---

## P18 — External Exams (สอบพิเศษ)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: สอบพิเศษ (External)  [+ เพิ่ม]     │
│          ├──────────────────────────────────────────────┤
│          │ ┌──────────────────────────────────────────┐ │
│          │ │ 🏛️ ONET / PAT — 15 มี.ค. 2569           │ │
│          │ │ ห้อง: AUD 50ปี  |  ผู้คุม: เจ้าหน้าที่  │ │
│          │ │ จำนวน: 200 คน                           │ │
│          │ │ [แก้ไข] [ลบ]                            │ │
│          │ └──────────────────────────────────────────┘ │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │ 🏛️ ทดสอบภาษาอังกฤษ — 20 มี.ค. 2569     │ │
│          │ │ ห้อง: PSB 1101  |  ผู้คุม: อ.สมชาย      │ │
│          │ │ จำนวน: 45 คน                            │ │
│          │ │ [แก้ไข] [ลบ]                            │ │
│          │ └──────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

**Add/Edit Modal:**
```
┌──────────────────────────────────────────┐
│  เพิ่มสอบพิเศษ                      [×] │
├──────────────────────────────────────────┤
│  ชื่อการสอบ: [________________]         │
│  วันที่: [date picker]                  │
│  เวลา: [HH:MM] ถึง [HH:MM]            │
│  ห้องสอบ: [select]                     │
│  จำนวนผู้เข้าสอบ: [number]            │
│  ผู้คุมสอบ: [search_select (multi)]    │
│  หมายเหตุ: [textarea]                 │
│  [ยกเลิก]  [บันทึก]                   │
└──────────────────────────────────────────┘
```

---

## P19 — My Exam (Teacher — จัดการสอบของฉัน)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: จัดการสอบของฉัน                     │
│          ├──────────────────────────────────────────────┤
│          │ ┌──────────────────────────────────────────┐ │
│          │ │ 📚 126201 การเมืองการปกครอง — ตอน 1     │ │
│          │ │ 📅 19 มี.ค. 08.00-11.00  📍 PSB 1101    │ │
│          │ │ นักศึกษา: 30 คน  |  แผ่น: 90            │ │
│          │ │                                          │ │
│          │ │ ── ผู้รับผิดชอบ ─────────────────────── │ │
│          │ │ ผู้คุมสอบ 1: อ.ปัยลิน (ฉัน) ✅          │ │
│          │ │ ผู้คุมสอบ 2: คุณเกตสินี ✅              │ │
│          │ │ ผู้แจกกระดาษ: คุณสัพพัญญู              │ │
│          │ │                                          │ │
│          │ │ ── Submission ───────────────────────── │ │
│          │ │ ● pending — ส่งเมื่อ 7 เม.ย. 09:34      │ │
│          │ │ [ดู Submission] [💬 ข้อความ (2)]        │ │
│          │ └──────────────────────────────────────────┘ │
│          │ ┌──────────────────────────────────────────┐ │
│          │ │ 📚 127100 ทฤษฎีการเมือง — ตอน 1        │ │
│          │ │ ○ ยังไม่ได้ส่งข้อสอบ                   │ │
│          │ │ [+ ส่งข้อสอบ]                           │ │
│          │ └──────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

---

## P20 — Exam Manager (มอบหมายผู้รับผิดชอบ)

```
┌──────────┬──────────────────────────────────────────────┐
│ SIDEBAR  │ TOPBAR: มอบหมายผู้รับผิดชอบ                 │
│          ├──────────────────────────────────────────────┤
│          │ FILTER: [แผนก ▼] [สถานะมอบหมาย ▼] [🔍]    │
│          ├──────────────────────────────────────────────┤
│          │ TABLE (admin view):                          │
│          │ Section | อาจารย์ | Exam Manager | สถานะ   │
│          │ ─────────────────────────────────────────── │
│          │ 126201-1 | อ.ปัยลิน | อ.ปัยลิน ✅ | active │
│          │ 126211-1 | อ.นฤทธ์  | (ยังไม่มอบ)| [+ มอบ]│
│          │ ...                                          │
│          │                                              │
│          │ Assign Modal:                               │
│          │  เลือกผู้รับผิดชอบ: [search teacher/staff] │
│          │  [มอบหมาย]                                  │
└──────────┴──────────────────────────────────────────────┘
```

---

# 🧾 6. UI JSON — COMPLETE PAGES (ต่อ)

หน้าต่อจาก Section 6 ด้านบน ที่เพิ่มเข้ามา:

```json
{
  "pages_extended": [
    {
      "id": "sections",
      "name": "รายวิชา / Sections",
      "route": "/sections",
      "roles": ["admin", "teacher", "staff"],
      "components": [
        {
          "type": "filter_bar",
          "filters": [
            { "name": "q", "type": "search", "placeholder": "รหัสวิชา หรือ ชื่อวิชา" },
            { "name": "academic_year", "type": "select", "label": "ปีการศึกษา", "options": ["2568","2567"] },
            { "name": "semester", "type": "select", "label": "ภาคเรียน", "options": ["1","2","summer"] }
          ]
        },
        {
          "type": "data_table",
          "data_source": "GET /api/courses/sections",
          "expandable_rows": true,
          "columns": [
            { "key": "course_code", "label": "รหัสวิชา", "sortable": true },
            { "key": "course_name", "label": "ชื่อวิชา" },
            { "key": "section_no", "label": "ตอน" },
            { "key": "teacher.full_name", "label": "อาจารย์" },
            { "key": "num_students", "label": "นศ." },
            { "key": "submission_status", "label": "Submission", "render": "badge" },
            { "key": "actions", "label": "", "render": "action_menu" }
          ],
          "row_expand": {
            "component": "SectionDetail",
            "shows": ["room","exam_date","exam_time","supervisors","submission_status"]
          },
          "row_actions": [
            { "label": "ดูตาราง", "navigate": "schedule?section={id}" },
            { "label": "แก้ไข", "modal": "edit-section", "roles": ["admin"] },
            { "label": "มอบหมายผู้รับผิดชอบ", "navigate": "exammanager?section={id}", "roles": ["admin"] }
          ],
          "empty_state": {
            "icon": "📚",
            "message": "ยังไม่มี sections — กรุณานำเข้าข้อมูลก่อน",
            "action": { "label": "นำเข้าข้อมูล", "navigate": "import", "roles": ["admin"] }
          }
        }
      ]
    },
    {
      "id": "copy",
      "name": "คำนวณค่าถ่ายเอกสาร",
      "route": "/copy",
      "roles": ["admin", "staff"],
      "components": [
        {
          "type": "summary_bar",
          "data_source": "GET /api/exports/copy-summary",
          "items": [
            { "key": "total_sheets", "label": "แผ่นรวม", "format": "number" },
            { "key": "total_cost", "label": "ค่าใช้จ่ายรวม", "format": "currency_thb" }
          ],
          "actions": [
            { "label": "Export Excel", "icon": "↓", "action": "GET /api/exports/copy.xlsx" },
            { "label": "พิมพ์รายงาน", "icon": "🖨️", "action": "GET /api/pdf/copy-report" }
          ]
        },
        {
          "type": "data_table",
          "data_source": "GET /api/exports/copy-breakdown",
          "columns": [
            { "key": "course_code", "label": "วิชา" },
            { "key": "section_no", "label": "ตอน" },
            { "key": "room_name", "label": "ห้อง" },
            { "key": "num_students", "label": "นศ." },
            { "key": "num_pages", "label": "หน้า" },
            { "key": "total_sheets", "label": "แผ่น", "sortable": true },
            { "key": "cost", "label": "ค่า (฿)", "format": "currency" }
          ],
          "footer_row": { "label": "รวม", "sum_keys": ["total_sheets","cost"] }
        },
        {
          "type": "inline_setting",
          "label": "ราคาต่อแผ่น",
          "setting_key": "copy_price_per_sheet",
          "type": "number",
          "unit": "บาท",
          "default": 0.50,
          "save_action": "PUT /api/settings/copy_price_per_sheet"
        }
      ]
    },
    {
      "id": "workflow",
      "name": "ยืนยันตาราง",
      "route": "/workflow",
      "roles": ["admin", "esq_head", "secretary"],
      "components": [
        {
          "type": "workflow_stepper",
          "data_source": "GET /api/workflow/session/",
          "steps": [
            { "index": 1, "key": "has_schedule",     "label": "จัดตารางแล้ว",   "icon": "📅" },
            { "index": 2, "key": "has_submissions",  "label": "ส่งข้อสอบแล้ว", "icon": "📤" },
            { "index": 3, "key": "is_signed",        "label": "ลงนามแล้ว",      "icon": "🖊" },
            { "index": 4, "key": "swap_open",        "label": "เปิด Swap",       "icon": "🔄" }
          ]
        },
        {
          "type": "signer_list",
          "data_source": "GET /api/workflow/session/signers",
          "title": "📋 ลายเซ็นดิจิทัล",
          "signers": ["admin", "esq_head", "secretary"],
          "item_template": {
            "role": "badge",
            "user": "full_name",
            "signed_at": "datetime | ยังไม่ลงนาม"
          },
          "action": {
            "label": "🖊 ลงนามตาราง",
            "condition": "current_user_role_must_sign AND !already_signed",
            "action": "POST /api/workflow/session/sign",
            "confirm": true,
            "confirm_message": "ยืนยันการลงนามตารางสอบ ปลายภาค 2/2568?"
          }
        },
        {
          "type": "schedule_preview",
          "title": "📅 ภาพรวมตารางสอบ (read-only)",
          "data_source": "GET /api/schedule/",
          "compact": true,
          "filterable": ["date","room"]
        },
        {
          "type": "action_button",
          "label": "🔄 เปิด Swap",
          "variant": "btn-gold",
          "roles": ["admin"],
          "condition": "all_signed AND !swap_open",
          "action": "POST /api/workflow/session/open-swap",
          "confirm": true
        }
      ]
    },
    {
      "id": "coexam",
      "name": "Co-Exam",
      "route": "/coexam",
      "roles": ["admin"],
      "components": [
        {
          "type": "action_bar",
          "actions": [
            { "label": "🔍 ตรวจหากลุ่มอัตโนมัติ", "action": "POST /api/co-exam/auto-detect", "opens_panel": "auto-detect-panel" },
            { "label": "+ สร้างกลุ่ม", "modal": "create-coexam" }
          ]
        },
        {
          "type": "coexam_list",
          "data_source": "GET /api/co-exam/",
          "item_component": "CoExamGroupCard",
          "empty_state": {
            "icon": "🔗",
            "message": "ยังไม่มีกลุ่ม Co-Exam",
            "action": { "label": "🔍 ตรวจหาอัตโนมัติ", "action": "POST /api/co-exam/auto-detect" }
          }
        }
      ],
      "panels": [
        {
          "id": "auto-detect-panel",
          "type": "slide_in",
          "title": "🔍 ตรวจพบกลุ่มที่ควรรวม",
          "data_key": "suggestions",
          "selectable": true,
          "action": { "label": "สร้างกลุ่มที่เลือก", "action": "POST /api/co-exam/" }
        }
      ],
      "modals": [
        {
          "id": "create-coexam",
          "title": "สร้างกลุ่ม Co-Exam",
          "size": "md",
          "form": {
            "action": "POST /api/co-exam/",
            "fields": [
              { "name": "label", "type": "text", "label": "ชื่อกลุ่ม" },
              { "name": "exam_date", "type": "date", "label": "วันสอบ" },
              { "name": "exam_time", "type": "text", "label": "เวลา (HH.MM-HH.MM)" },
              { "name": "exam_type", "type": "select", "options": ["midterm","final"] },
              { "name": "section_ids", "type": "multi_search_select", "label": "Sections", "data_source": "GET /api/courses/sections" }
            ]
          }
        }
      ]
    },
    {
      "id": "printreview",
      "name": "ตรวจก่อนพิมพ์",
      "route": "/printreview",
      "roles": ["admin"],
      "components": [
        {
          "type": "filter_bar",
          "filters": [
            { "name": "room", "type": "select", "label": "ห้อง" },
            { "name": "date", "type": "date", "label": "วันที่" },
            { "name": "status", "type": "select", "label": "สถานะ Submission", "options": ["approved","pending","rejected"] }
          ]
        },
        {
          "type": "data_table",
          "data_source": "GET /api/exports/print-review",
          "selectable": true,
          "columns": [
            { "key": "course_code", "label": "วิชา" },
            { "key": "room_name", "label": "ห้อง" },
            { "key": "exam_date", "label": "วันที่" },
            { "key": "total_sheets", "label": "แผ่น" },
            { "key": "submission_status", "label": "Submission", "render": "badge" },
            { "key": "actions", "label": "", "render": "print_action" }
          ],
          "row_actions": [
            { "label": "👁 Preview", "condition": "submission_status === 'approved'", "action": "GET /api/pdf/submission/{submission_id}/preview" },
            { "label": "🖨 พิมพ์ PDF", "condition": "submission_status === 'approved'", "action": "GET /api/pdf/submission/{submission_id}" }
          ],
          "batch_actions": [
            { "label": "🖨 พิมพ์ที่เลือก", "condition": "selected.length > 0 AND all_approved", "action": "GET /api/pdf/batch" }
          ]
        }
      ]
    },
    {
      "id": "import",
      "name": "นำเข้าข้อมูล",
      "route": "/import",
      "roles": ["admin"],
      "components": [
        {
          "type": "tab_bar",
          "tabs": [
            { "label": "นักศึกษา", "key": "students" },
            { "label": "Sections", "key": "sections" },
            { "label": "ห้องสอบ", "key": "rooms" }
          ]
        },
        {
          "type": "file_upload_zone",
          "accepts": [".xlsx", ".csv"],
          "max_size_mb": 10,
          "upload_action": "POST /api/import/preview",
          "shows_preview": true,
          "preview_rows": 10,
          "preview_columns": ["รหัสนศ.", "ชื่อ", "วิชา", "ตอน"],
          "confirm_action": "POST /api/import/commit",
          "confirm_label": "นำเข้า ({valid_count} แถว)"
        },
        {
          "type": "import_history",
          "data_source": "GET /api/import/sessions",
          "columns": ["วันที่", "ไฟล์", "จำนวน", "สถานะ", "ผู้นำเข้า"]
        }
      ],
      "modals": [
        {
          "id": "import-progress",
          "title": "กำลังนำเข้าข้อมูล...",
          "size": "sm",
          "auto_open": true,
          "shows_progress": true,
          "progress_source": "GET /api/import/status/{session_id}",
          "poll_interval_ms": 800
        }
      ]
    },
    {
      "id": "external",
      "name": "สอบพิเศษ",
      "route": "/external",
      "roles": ["admin"],
      "components": [
        {
          "type": "card_list",
          "data_source": "GET /api/external/",
          "item_fields": ["name","exam_date","exam_time","room","num_students","supervisors"],
          "item_actions": [
            { "label": "แก้ไข", "modal": "edit-external" },
            { "label": "ลบ", "variant": "danger", "action": "DELETE /api/external/{id}", "confirm": true }
          ],
          "empty_state": { "icon": "🏛️", "message": "ยังไม่มีสอบพิเศษ" }
        }
      ],
      "header_actions": [
        { "label": "+ เพิ่มสอบพิเศษ", "modal": "add-external" }
      ],
      "modals": [
        {
          "id": "add-external",
          "title": "เพิ่มสอบพิเศษ",
          "size": "md",
          "form": {
            "action": "POST /api/external/",
            "fields": [
              { "name": "name",           "type": "text",          "label": "ชื่อการสอบ",        "required": true },
              { "name": "exam_date",      "type": "date",          "label": "วันที่",             "required": true },
              { "name": "exam_time_start","type": "time",          "label": "เริ่ม",              "required": true },
              { "name": "exam_time_end",  "type": "time",          "label": "สิ้นสุด",            "required": true },
              { "name": "room_id",        "type": "select",        "label": "ห้องสอบ",           "data_source": "GET /api/schedule/rooms" },
              { "name": "num_students",   "type": "number",        "label": "จำนวนผู้เข้าสอบ" },
              { "name": "supervisor_ids", "type": "multi_select",  "label": "ผู้คุมสอบ",         "data_source": "GET /api/users/?role=staff,teacher" },
              { "name": "note",           "type": "textarea",      "label": "หมายเหตุ" }
            ]
          }
        }
      ]
    },
    {
      "id": "myexam",
      "name": "จัดการสอบของฉัน",
      "route": "/myexam",
      "roles": ["teacher"],
      "components": [
        {
          "type": "card_list",
          "data_source": "GET /api/exam-manager/my-sections",
          "item_component": "MyExamCard",
          "empty_state": { "icon": "📋", "message": "ไม่มีวิชาที่มอบหมาย" }
        }
      ],
      "modals": [
        {
          "id": "submission-form",
          "title": "ส่งข้อสอบ",
          "size": "md",
          "form": {
            "action": "POST /api/submissions/",
            "fields": [
              { "name": "exam_format",     "type": "select",   "label": "ประเภทข้อสอบ",  "options": ["ปรนัย","อัตนัย","ปรนัย+อัตนัย"] },
              { "name": "num_questions",   "type": "number",   "label": "จำนวนข้อ" },
              { "name": "duration_minutes","type": "number",   "label": "ระยะเวลา (นาที)" },
              { "name": "file",            "type": "file",     "label": "ไฟล์ข้อสอบ",   "accept": ".pdf,.doc,.docx", "required": true },
              { "name": "answer_file",     "type": "file",     "label": "ไฟล์เฉลย (ถ้ามี)", "accept": ".pdf" },
              { "name": "note",            "type": "textarea", "label": "หมายเหตุ" }
            ],
            "submit_label": "ส่งข้อสอบ"
          }
        },
        {
          "id": "message-thread",
          "title": "💬 ข้อความ",
          "size": "md",
          "data_source": "GET /api/submissions/{id}/messages",
          "send_action": "POST /api/submissions/{id}/messages",
          "validation": { "max_length": 2000, "required": true }
        }
      ]
    },
    {
      "id": "exammanager",
      "name": "มอบหมายผู้รับผิดชอบ",
      "route": "/exammanager",
      "roles": ["admin"],
      "components": [
        {
          "type": "filter_bar",
          "filters": [
            { "name": "dept", "type": "select", "label": "แผนก" },
            { "name": "assigned", "type": "toggle", "label": "ยังไม่มอบหมาย" },
            { "name": "q", "type": "search", "placeholder": "ค้นหา section" }
          ]
        },
        {
          "type": "data_table",
          "data_source": "GET /api/exam-manager/",
          "columns": [
            { "key": "course_code",         "label": "Section" },
            { "key": "teacher.full_name",    "label": "อาจารย์ประจำวิชา" },
            { "key": "manager.full_name",    "label": "Exam Manager",   "render": "user_or_empty" },
            { "key": "assignment_status",    "label": "สถานะ",          "render": "badge" },
            { "key": "actions",              "label": "",               "render": "action_menu" }
          ],
          "row_actions": [
            { "label": "มอบหมาย",  "modal": "assign-manager" },
            { "label": "ยกเลิก",   "condition": "manager != null", "action": "DELETE /api/exam-manager/{id}", "confirm": true }
          ]
        }
      ],
      "modals": [
        {
          "id": "assign-manager",
          "title": "มอบหมายผู้รับผิดชอบ",
          "size": "sm",
          "form": {
            "action": "POST /api/exam-manager/",
            "fields": [
              { "name": "section_id", "type": "hidden" },
              { "name": "manager_id", "type": "search_select", "label": "ผู้รับผิดชอบ", "data_source": "GET /api/users/?role=teacher,staff", "required": true }
            ]
          }
        }
      ]
    }
  ]
}
```

---

# ♿ 8. ACCESSIBILITY & RESPONSIVE DESIGN

## 8.1 Accessibility Standards (WCAG 2.1 AA)

```
Focus Management:
  - All interactive elements reachable via Tab key
  - Focus ring: 2px solid var(--crimson) with 2px offset
  - Modal: trap focus inside when open, restore on close
  - Sidebar collapse: keyboard accessible via Enter/Space

ARIA Labels:
  - Nav buttons: aria-label="แดชบอร์ด", aria-current="page" when active
  - Badge counts: aria-label="3 คำขอรอตอบ"
  - Form fields: aria-describedby pointing to error message elements
  - Charts: aria-label with data summary (e.g., "ส่งข้อสอบแล้ว 8 จาก 13 sections")
  - Loading states: aria-busy="true" on containers
  - Modals: role="dialog", aria-modal="true", aria-labelledby="modal-title"

Color Contrast:
  - Text on --navy bg: white → 14.5:1 ✅
  - Text on --surface:  #1a1a1a → 16.1:1 ✅
  - --crimson badges: white text → 5.8:1 ✅
  - --gold badges: white text → 3.2:1 (AA for large text only)
  - Error text on white: #c41230 → 5.8:1 ✅

Screen Reader:
  - Skip-to-content link at page top
  - Table headers with scope="col"
  - Status changes: aria-live="polite" on toast container
  - Form submission results: aria-live="assertive" for errors
```

## 8.2 Responsive Breakpoints

```
xs:  < 480px   — Mobile portrait
sm:  480–767px — Mobile landscape
md:  768–1023px — Tablet
lg:  1024–1279px — Desktop small
xl:  ≥ 1280px  — Desktop full
```

## 8.3 Responsive Layout Rules

```
Sidebar:
  xl/lg: Fixed 220px wide, always visible
  md:    Collapsed to 60px (icons only), expandable on hover
  sm/xs: Hidden — replaced by MobileBottomNav (56px fixed bottom)

Top Bar:
  lg+: Show full: [Title] [Period badge] [User pill]
  md:  Hide period badge (shown in page body instead)
  sm:  Show: [Hamburger] [Title] [Avatar only]

Stat Grid:
  xl:  4 columns
  lg:  4 columns
  md:  2 columns
  sm:  1 column (stacked)

Charts Grid:
  lg+: 2 × 2
  md:  1 × 2 (stacked pairs)
  sm:  1 column (single column)

Data Table:
  lg+: All columns visible
  md:  Hide low-priority columns (dept, created_at)
  sm:  Card-mode (each row becomes a stacked card)

Modals:
  lg+: Centered, max-width as spec
  sm:  Bottom sheet (slides up from bottom, 90% viewport height)
```

## 8.4 Mobile-Specific Patterns

```
Bottom Navigation (≤ 768px):
  5 items: หน้าหลัก | ตาราง | ส่งงาน | สลับ | Check-in
  Active item: white + crimson underline bar
  Badge: red dot on Swap item when pending > 0

Touch Targets:
  Minimum 44×44px for all tappable elements
  Buttons: min-height 44px
  Table rows: min-height 52px (tap to expand)

Swipe Gestures:
  Modal bottom sheet: swipe down to close
  Schedule list: swipe left on card → quick actions (edit, cancel)

Mobile Check-in:
  Large GPS button (full-width, 56px height)
  Map preview optional (MapKit / Google Maps embed)
  One-tap confirm after GPS lock
```

---

# 📊 9. DATA MODELS (UI Binding Reference)

## 9.1 Core Models

```typescript
interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: 'admin' | 'esq_head' | 'secretary' | 'dept_supervisor' | 'staff' | 'teacher' | 'student';
  effective_role: string;      // may differ if view_as_role set
  view_as_role: string | null;
  dept_code: string | null;
  special_role: 'room_keeper' | 'esq_staff' | null;
  is_active: boolean;
  title_th: string;           // คำนำหน้า
  ext: string | null;         // เบอร์ภายใน
  mobile: string | null;
}

interface ExamSchedule {
  id: number;
  section_id: number;
  room_id: number | null;
  exam_date: string;           // "2569-03-19"
  exam_time: string;           // "08.00-11.00"
  exam_type: 'midterm' | 'final';
  status: 'draft' | 'published' | 'confirmed' | 'cancelled';
  num_pages: number;
  total_sheets: number;
  paper_distributor: number | null;
  section: Section;
  room: Room | null;
  supervisors: Supervision[];
}

interface Section {
  id: number;
  course_id: number;
  section_no: string;
  teacher_id: number;
  num_students: number;
  semester: string;
  academic_year: string;
  course: Course;
  teacher: User;
}

interface Course {
  id: number;
  code: string;                // "126201"
  name_th: string;
  name_en: string | null;
  credits: number;
  dept_code: string;
}

interface ExamSubmission {
  id: number;
  section_id: number;
  submitted_by: number;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'revision';
  exam_format: string;
  num_questions: number | null;
  duration_minutes: number | null;
  note: string | null;
  submitted_at: string | null;
  reviewed_at: string | null;
  reviewed_by: number | null;
  files: SubmissionFile[];
  messages: SubmissionMessage[];
}

interface SwapRequest {
  id: number;
  requester_id: number;
  target_user_id: number;
  from_schedule_id: number;
  to_schedule_id: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  created_at: string;
  resolved_at: string | null;
  requester: User;
  target_user: User;
  from_schedule: ExamSchedule;
  to_schedule: ExamSchedule;
}

interface CheckinEvent {
  id: number;
  schedule_id: number;
  user_id: number;
  checked_in_at: string;
  lat: number | null;
  lng: number | null;
  confirmed: boolean;
  user: User;
}

interface ExamPeriod {
  id: number;
  academic_year: string;      // "2568"
  semester: string;           // "2"
  exam_type: string;          // "final"
  label: string;              // "ปลายภาค 2/2568"
  is_active: boolean;
}

interface AuditLog {
  id: number;
  action: string;             // "LOGIN", "PROPOSE_EXAM_MANAGER", etc.
  actor_id: number | null;
  actor: User | null;
  table_name: string | null;
  record_id: number | null;
  detail: string | null;
  timestamp: string;
  ip_hash: string | null;
}
```

## 9.2 API Response Envelopes

```typescript
// List responses
interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

// Dashboard
interface DashboardStats {
  total_sections: number;
  total_students: number;
  total_sheets: number;
  total_teachers: number;
  scheduled_sections: number;
  unscheduled_sections: number;
  rooms_in_use: number;
  copy_cost: number;
  recent_logs: AuditLogSummary[];
}

// Analytics (charts)
interface DashboardAnalytics {
  submission_status: Record<string, number>;  // { pending: 5, approved: 8 }
  teacher_stats: { submitted: number; not_submitted: number };
  supervision_stats: { confirmed: number; pending: number };
  swap_status: Record<string, number>;
  copy_per_room: { room: string; sheets: number; cost: number }[];
  checkin_by_date: { date: string; count: number }[];
}

// Auth
interface AuthResponse {
  access_token: string;       // also set as HttpOnly cookie
  token_type: 'bearer';
  user: User;
}
```

## 9.3 Status Badge Mapping (UI Layer)

```typescript
const SUBMISSION_STATUS_LABELS: Record<string, { label: string; badge: string }> = {
  draft:    { label: 'ร่าง',          badge: 'badge-gray' },
  pending:  { label: 'รออนุมัติ',     badge: 'badge-gold' },
  approved: { label: 'อนุมัติแล้ว',  badge: 'badge-green' },
  rejected: { label: 'ปฏิเสธ',        badge: 'badge-crimson' },
  revision: { label: 'ต้องแก้ไข',    badge: 'badge-orange' },
};

const SCHEDULE_STATUS_LABELS: Record<string, { label: string; badge: string }> = {
  draft:     { label: 'ร่าง',        badge: 'badge-gray' },
  published: { label: 'เผยแพร่แล้ว', badge: 'badge-blue' },
  confirmed: { label: 'ยืนยันแล้ว',  badge: 'badge-green' },
  cancelled: { label: 'ยกเลิก',      badge: 'badge-crimson' },
};

const SWAP_STATUS_LABELS: Record<string, { label: string; badge: string }> = {
  pending:   { label: 'รอตอบ',       badge: 'badge-gold' },
  approved:  { label: 'อนุมัติ',     badge: 'badge-green' },
  rejected:  { label: 'ปฏิเสธ',      badge: 'badge-crimson' },
  cancelled: { label: 'ยกเลิก',      badge: 'badge-gray' },
};
```

## 9.4 Navigation Permission Matrix

```
Page          │ admin │ esq_head │ secretary │ dept_sup │ staff │ teacher │ student
──────────────┼───────┼──────────┼───────────┼──────────┼───────┼─────────┼────────
dashboard     │   ✅  │    ✅    │    ✅     │    ✅    │  ✅   │   ❌    │   ❌
schedule      │   ✅  │    ✅    │    ✅     │    ✅    │  ✅   │   ✅    │   ❌
submissions   │   ✅  │    ✅    │    ✅     │    ✅    │  ❌   │   ✅    │   ❌
swaps         │   ✅  │    ❌    │    ❌     │    ✅    │  ✅   │   ✅    │   ❌
checkins      │   ✅  │    ❌    │    ❌     │    ✅    │  ✅   │   ✅    │   ❌
student       │   ✅  │    ✅    │    ✅     │    ✅    │  ✅   │   ✅    │   ✅
sections      │   ✅  │    ✅    │    ✅     │    ❌    │  ✅   │   ✅    │   ❌
copy          │   ✅  │    ❌    │    ❌     │    ❌    │  ✅   │   ❌    │   ❌
myexam        │   ❌  │    ❌    │    ❌     │    ❌    │  ❌   │   ✅    │   ❌
optimizer     │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
coexam        │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
workflow      │   ✅  │    ✅    │    ✅     │    ❌    │  ❌   │   ❌    │   ❌
printreview   │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
import        │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
period        │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
settings      │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
users         │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
external      │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
exammanager   │   ✅  │    ❌    │    ❌     │    ❌    │  ❌   │   ❌    │   ❌
```

---

*Generated for: EMS v2.0 — คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มช.*
*Target tools: Stitch, v0, Lovable, Figma (via JSON import)*
*Total pages: 20 | Total roles: 7 | Total API endpoints: 40+*
