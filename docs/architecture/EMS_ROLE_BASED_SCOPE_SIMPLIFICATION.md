# EMS Role-Based Scope Simplification

**Date:** 2026-06-30
**Purpose:** Define exactly what each role should and should not see in the EMS pilot. This serves as the authoritative reference for Phase B navigation cleanup and future role access decisions.

---

## Design Principle

Each role should see **only the pages they need to complete their exam-period duties**. No role should need to navigate past unfamiliar pages to reach the ones they actually use.

---

## Role Definitions (from system)

| Role | Thai Name | Primary Responsibility |
|------|-----------|----------------------|
| `admin` | ผู้ดูแลระบบ | Full system administration; runs import, optimization, workflow |
| `esq_head` | หัวหน้างานสอบ | Exam scheduling governance; signs off workflow and payment |
| `secretary` | เลขานุการ | Administrative support; joins approval flow |
| `dept_supervisor` | หัวหน้าภาควิชา | Department-level oversight; manages dept submissions and attendance |
| `staff` | เจ้าหน้าที่ | Operations support; rooms, check-ins, exports |
| `teacher` | อาจารย์ | Submits exam materials; performs invigilation duty |
| `print_shop` | ร้านถ่ายเอกสาร | Manages print queue and document delivery |
| `student` | นักศึกษา | Public schedule lookup only |

---

## Role: Admin (`admin`)

### Should See (in sidebar)

| Module | Page | Route |
|--------|------|-------|
| หน้าหลัก | Dashboard | `/dashboard` |
| ตารางสอบ | Exam Schedule | `/schedule` |
| ตารางสอบ | Import Data | `/import` |
| ตารางสอบ | Rooms | `/rooms-v2` |
| ตารางสอบ | Exam Periods | `/period` |
| ตารางสอบ | Sections | `/sections` |
| ตารางสอบ | Exam Manager | `/exammanager` |
| จัดคนคุมสอบ | Staff Availability | `/staff-availability` |
| จัดคนคุมสอบ | Assign Invigilators | `/optimizer` |
| จัดคนคุมสอบ | Invigilation Workload | `/workload-duty-analytics` |
| จัดคนคุมสอบ | Swaps | `/swaps` |
| ส่งเอกสาร | Submissions | `/submissions` |
| ส่งเอกสาร | Print Review | `/printreview` |
| ส่งเอกสาร | Copy Count | `/copy` |
| รับ-ส่งเอกสาร | Check-in / QR | `/checkins` |
| รับ-ส่งเอกสาร | Room Attendance | `/attendance` |
| เอกสารประกอบการเบิก | Rate Settings | `/invigilation-rate-rules` |
| เอกสารประกอบการเบิก | Draft Payment Summary | `/invigilation-payment-document-draft` |
| เอกสารประกอบการเบิก | Draft Supporting Roster | `/invigilation-advance-batch-preview` |
| เอกสารประกอบการเบิก | Document Settings | `/payment-document-settings` |
| ส่งออก | Export Center | `/exports-center` |
| ส่งออก | Workflow / Approval | `/workflow` |
| ส่งออก | External Exams | `/external` |
| ส่งออก | Co-Exam | `/coexam` |
| ประวัติ | Historical Schedules | `/historical-schedules` |

**Direct URL only (not in sidebar):**
- Users: `/users`
- Settings: `/settings`

### Should NOT See in Sidebar (by default)

| Page | Route | Reason |
|------|-------|--------|
| Admin Intelligence Dashboard | `/admin-intelligence-dashboard` | Demo signal; not daily ops |
| Executive Analytics | `/analytics` | Enterprise trends; D5 maturity |
| Governance Cockpit | `/governance` | Redundant with Dashboard + Workflow |
| Operational Health | `/operational-health` | IT/dev monitoring |
| Audit Explorer | `/audit-explorer` | Compliance/dev tool |
| Optimizer Trace | `/optimizer-trace` | Debug/admin debug tool |
| Platform Config | `/platform-config` | Complex governance config; partially wired |
| Import Audit | `/import-audit` | Admin review tool; not daily |

**Admin CAN reach all hidden pages by direct URL.** These are not removed — they are just not surfaced in the sidebar.

---

## Role: ESQ Head (`esq_head`)

### Should See

| Module | Page | Route |
|--------|------|-------|
| หน้าหลัก | Dashboard | `/dashboard` |
| ตารางสอบ | Exam Schedule | `/schedule` |
| ตารางสอบ | Sections | `/sections` |
| จัดคนคุมสอบ | Invigilation Workload | `/duty-workload` |
| จัดคนคุมสอบ | Swaps | `/swaps` |
| ส่งเอกสาร | Submissions | `/submissions` |
| ส่งเอกสาร | Print Review | `/printreview` |
| รับ-ส่งเอกสาร | Room Attendance | `/attendance` |
| เอกสารประกอบการเบิก | Document Settings | `/payment-document-settings` |
| ส่งออก | Workflow / Approval | `/workflow` |
| ส่งออก | Export Center | `/exports-center` |
| ประวัติ | Historical Schedules | `/historical-schedules` |

### Should NOT See

- Admin Intelligence Dashboard (admin-only analytics)
- Executive Analytics (enterprise trends)
- Governance Cockpit (redundant with Workflow)
- Operational Health (IT/dev tool)
- Audit Explorer (dev tool; esq_head currently has access — reconsider)
- Optimizer Trace (dev/admin debug)
- Platform Configuration (admin setup tool)
- Import, Import Audit (admin data management)
- Rooms, Period, Optimizer, Staff Availability (admin ops)

**Note on Audit Explorer:** `esq_head` currently has access to Audit Explorer. Consider whether this is intentional for compliance oversight or a permissioning error. If intentional, it should still be hidden from the sidebar (URL-direct access only).

---

## Role: Secretary (`secretary`)

### Should See

| Module | Page | Route |
|--------|------|-------|
| หน้าหลัก | Dashboard | `/dashboard` |
| ตารางสอบ | Exam Schedule | `/schedule` |
| ตารางสอบ | Sections | `/sections` |
| จัดคนคุมสอบ | Invigilation Workload | `/duty-workload` |
| จัดคนคุมสอบ | Swaps | `/swaps` |
| ส่งเอกสาร | Submissions | `/submissions` |
| ส่งเอกสาร | Print Review | `/printreview` |
| รับ-ส่งเอกสาร | Room Attendance | `/attendance` |
| เอกสารประกอบการเบิก | Document Settings | `/payment-document-settings` |
| ส่งออก | Workflow / Approval | `/workflow` |
| ส่งออก | Export Center | `/exports-center` |
| ประวัติ | Historical Schedules | `/historical-schedules` |

### Should NOT See

- Executive Analytics, Governance Cockpit, Admin Intelligence (analytics/enterprise)
- All developer tools (Operational Health, Audit Explorer, Optimizer Trace, Platform Config)
- Import, Rooms, Period, Optimizer, Staff Availability (admin ops)

---

## Role: Department Supervisor (`dept_supervisor`)

### Should See

| Module | Page | Route |
|--------|------|-------|
| หน้าหลัก | Dashboard | `/dashboard` |
| ตารางสอบ | Exam Schedule | `/schedule` |
| ตารางสอบ | Sections | `/sections` |
| ตารางสอบ | Exam Manager | `/exammanager` |
| จัดคนคุมสอบ | Invigilation Workload | `/duty-workload` |
| จัดคนคุมสอบ | Swaps | `/swaps` |
| ส่งเอกสาร | Submissions | `/submissions` |
| รับ-ส่งเอกสาร | Check-in / QR | `/checkins` |
| รับ-ส่งเอกสาร | Room Attendance | `/attendance` |
| ประวัติ | Historical Schedules | `/historical-schedules` |

### Should NOT See

- All payment pages (configuration and documents)
- All analytics/intelligence pages
- All developer tools
- Import, Rooms, Period, Optimizer, Staff Availability (admin ops)
- Print Review, Copy Count (admin/staff print prep)

---

## Role: Staff (`staff`)

### Should See

| Module | Page | Route |
|--------|------|-------|
| หน้าหลัก | Dashboard | `/dashboard` |
| ตารางสอบ | Exam Schedule | `/schedule` |
| ตารางสอบ | Sections | `/sections` |
| จัดคนคุมสอบ | Invigilation Workload | `/duty-workload` |
| จัดคนคุมสอบ | Swaps | `/swaps` |
| ส่งเอกสาร | Submissions | `/submissions` |
| ส่งเอกสาร | Copy Count | `/copy` |
| รับ-ส่งเอกสาร | Check-in / QR | `/checkins` |
| รับ-ส่งเอกสาร | Room Attendance | `/attendance` |
| เอกสารประกอบการเบิก | Rate Settings | `/invigilation-rate-rules` |
| เอกสารประกอบการเบิก | Draft Payment Summary | `/invigilation-payment-document-draft` |
| เอกสารประกอบการเบิก | Draft Supporting Roster | `/invigilation-advance-batch-preview` |
| เอกสารประกอบการเบิก | Document Settings | `/payment-document-settings` |
| ส่งออก | Export Center | `/exports-center` |
| ส่งออก | External Exams | `/external` |
| ประวัติ | Historical Schedules | `/historical-schedules` |

### Should NOT See

- All executive analytics, intelligence dashboards, governance cockpit
- All developer tools (Operational Health, Audit Explorer, Optimizer Trace, Platform Config)
- Admin-only pages (Rooms, Period, Import, Optimizer, Staff Availability, Exam Manager, Co-Exam)
- Print Review (admin/esq only)

---

## Role: Teacher (`teacher`)

### Should See

| Module | Page | Route |
|--------|------|-------|
| หน้าหลัก | Dashboard | `/dashboard` |
| ตารางสอบ | Exam Schedule | `/schedule` |
| ตารางสอบ | Sections | `/sections` |
| จัดคนคุมสอบ | Invigilation Workload | `/my-workload` |
| จัดคนคุมสอบ | Swaps | `/swaps` |
| จัดคนคุมสอบ | My Exam | `/myexam` |
| ส่งเอกสาร | Submissions | `/submissions` |
| รับ-ส่งเอกสาร | Check-in / QR | `/checkins` |
| รับ-ส่งเอกสาร | Room Attendance | `/attendance` |
| ประวัติ | Historical Schedules | `/historical-schedules` |

### Should NOT See

- Payment configuration pages (rate settings, payment draft, document settings)
- Admin analytics (intelligence dashboard, executive analytics)
- Developer tools (operational health, audit explorer, optimizer trace, platform config)
- All admin ops pages (rooms, import, period, optimizer, etc.)
- Print Review, Copy Count, Print Queue (not teacher responsibilities)

**Teacher's world is simple:** See the schedule → see my assignments → submit my exam materials → check in on exam day → request a swap if needed. Nothing else should appear.

---

## Role: Print Shop (`print_shop`)

### Should See

| Module | Page | Route |
|--------|------|-------|
| คิวพิมพ์ | Print Queue | `/print-queue` |

**That is all.** Print shop has one job: manage the print queue. No other pages should appear in their sidebar.

**Note:** Current route access correctly restricts print_shop to `/print-queue` only. This is already correct and should not change.

---

## Role: Student (public, no auth)

### Should Access

- Student search: `/student-search` (public, no login required)

**Nothing else.** Students use a public-facing schedule lookup only.

---

## Cross-Role Safety Rules

The following rules must hold across all roles after any navigation cleanup:

| Rule | Why |
|------|-----|
| Payment pages visible only to admin/esq_head/secretary/staff | Payment docs are invigilation payment only; no other roles involved |
| All developer tools hidden from ALL roles in sidebar | No faculty role needs Operational Health, Audit Explorer, Optimizer Trace, or Platform Config in their daily sidebar |
| Schedule visible to ALL authenticated roles | The schedule is the core product; every role needs it |
| Print queue visible ONLY to print_shop | Print queue is a specialized workflow; no other role needs to see the queue |
| My Exam visible ONLY to teacher | Teacher's personal assignment view |
| Optimizer visible ONLY to admin | Only admin runs optimization |
| Import visible ONLY to admin | Only admin performs data import |

---

## Current Violations to Resolve in Phase B

The following pages are currently visible in the sidebar to roles that should not see them:

| Page | Currently Visible To | Should Be Hidden From | Action |
|------|--------------------|--------------------|--------|
| Admin Intelligence Dashboard | admin | admin (sidebar; URL OK) | Set hidden: true |
| Executive Analytics | admin, esq_head, secretary | All roles (sidebar; URL OK for admin) | Set hidden: true |
| Governance Cockpit | admin, esq_head, secretary | All roles (sidebar; URL OK for admin) | Set hidden: true |
| Operational Health | admin, esq_head | All roles (sidebar; URL OK for admin) | Set hidden: true |
| Audit Explorer | admin, esq_head | All roles (sidebar; URL OK for admin) | Set hidden: true |
| Optimizer Trace | admin | admin (sidebar; URL OK) | Set hidden: true |
| Platform Config | admin | admin (sidebar; URL OK) | Set hidden: true |
| Import Audit | admin | admin (sidebar; URL OK) | Set hidden: true |

**Phase B implementation:** 8 `hidden: true` entries in `navigation.ts`. One file. Reversible by removing the flag.
