# EMS Core Product Scope Proposal

**Date:** 2026-06-30
**Purpose:** Define the focused product scope for the EMS controlled pilot. Classify pages that are core, secondary, or non-core without removing any code.

---

## Core Thesis

EMS is an **exam operations workspace**, not a platform intelligence suite. For the pilot phase, the product should feel like:

> "I open EMS, I see what needs to happen today for this exam period, I do my part of the workflow, I close EMS."

Every page that requires the user to think "what does this page do and why am I here?" before using it is a cognitive load problem during pilot onboarding.

---

## Core User-Facing Modules

The following five modules represent the full product scope for the current pilot.

---

### Module 1 — Exam Schedule Management

**Goal:** Produce and publish the master exam timetable for a term.

**Pages:**
| Page | Route | Role |
|------|-------|------|
| Exam Periods | `/period` | admin |
| Rooms | `/rooms-v2` | admin |
| Import Data | `/import` | admin |
| Exam Schedule | `/schedule` | All staff |
| Sections | `/sections` | All staff |
| Course Ownership | `/exammanager` | admin, dept_supervisor |

**What users do here:**
- Configure the exam term
- Import enrollment and course data
- Assign rooms and build the timetable
- View and verify the exam schedule

**Safety note:** `/schedule` is the primary product. It must never be hidden or restricted.

---

### Module 2 — Invigilation Assignment

**Goal:** Assign invigilators fairly and efficiently, manage swaps.

**Pages:**
| Page | Route | Role |
|------|-------|------|
| Staff Availability | `/staff-availability` | admin |
| Assign Invigilators | `/optimizer` | admin |
| Workload (Admin view) | `/workload-duty-analytics` | admin |
| Workload (Staff view) | `/duty-workload` | staff, dept_supervisor, esq_head, secretary |
| Workload (Teacher view) | `/my-workload` | teacher |
| Swaps | `/swaps` | admin, dept_supervisor, staff, teacher |
| My Exam | `/myexam` | teacher |

**What users do here:**
- Block staff availability periods
- Run optimization to assign invigilators to rooms
- Review and verify workload fairness
- Request and approve duty swaps
- Teachers view their own assignments

**Note on workload routes:** Three routes (`/workload-duty-analytics`, `/duty-workload`, `/my-workload`) all use the same `WorkloadDutyAnalytics` component with role-filtered views. These should be consolidated to a single nav entry labeled "ภาระงานคุมสอบ" in Phase C. The routes themselves should remain active.

**Note on historical schedules:** `/historical-schedules` provides a term-to-term comparison useful for verifying that optimization is fair across exam periods. It should remain accessible to staff and admin (not just admin) for transparency. This is a secondary but valuable page — see Module classification below.

---

### Module 3 — Exam Paper / File Handoff

**Goal:** Track exam paper preparation, distribution, and receipt confirmation.

**Pages:**
| Page | Route | Role |
|------|-------|------|
| Submissions | `/submissions` | admin, esq_head, secretary, dept_supervisor, teacher |
| Print Review | `/printreview` | admin, esq_head, secretary |
| Copy Count | `/copy` | admin, staff |
| Print Queue | `/print-queue` | print_shop |
| Room Attendance | `/attendance` | All staff |
| Check-in / QR | `/checkins` | admin, dept_supervisor, staff, teacher |

**What users do here:**
- Teachers submit exam files and materials
- Admin/ESQ verify submissions before sending to print
- Copy count planning for paper prep
- Print shop manages print queue and delivery
- Staff confirm check-in and attendance on exam day
- QR codes confirm pickup and paper handoff

---

### Module 4 — Payment Support, Draft Only

**Goal:** Produce draft invigilation payment documents for finance review. No final authorization.

**Pages:**
| Page | Route | Role |
|------|-------|------|
| Rate Settings | `/invigilation-rate-rules` | admin, staff |
| Draft Payment Summary | `/invigilation-payment-document-draft` | admin, staff |
| Draft Supporting Roster | `/invigilation-advance-batch-preview` | admin, staff |
| Draft Settings | `/payment-document-settings` | admin, esq_head, secretary, staff |

**What users do here:**
- Configure weekday/weekend invigilation rates
- Preview the draft payment calculation
- Review the supporting finance roster for submission
- Configure draft document parameters per term

**Critical constraint:** All payment pages are DRAFT ONLY. No final authorization is implemented. Teaching workload compensation is explicitly out of scope.

---

### Module 5 — Essential Administration

**Goal:** Manage users, roles, settings, and exports required for operations.

**Pages:**
| Page | Route | Role |
|------|-------|------|
| Users & Roles | `/users` | admin (direct URL) |
| Settings | `/settings` | admin (direct URL) |
| Export Center | `/exports-center` | admin, staff |
| External Exams | `/external` | admin, staff |
| Co-Exam Planning | `/coexam` | admin |
| Dashboard | `/dashboard` | All staff |

**What users do here:**
- Admin manages user accounts and role assignments
- System settings configuration (deadlines, term config)
- Export schedule, workload, and payment documents
- Manage external exam allocations
- Manage co-exam groupings (shared multi-department exams)

---

## Secondary Pages (Useful but Not Primary)

The following pages support the core workflow in a secondary or seasonal capacity. They should remain accessible but at lower navigation prominence.

| Page | Route | Why Secondary | Recommended Placement |
|------|-------|--------------|----------------------|
| Historical Schedules | `/historical-schedules` | Seasonal fairness audit use | Keep visible; expand role access to staff |
| Workflow Approval | `/workflow` | Approval pipeline (less frequent) | Keep in nav; lower prominence |
| Import Audit | `/import-audit` | Admin review of import sessions | Hide from main nav; admin URL access |

---

## Not Core for Current Pilot

The following pages are **not part of the core workflow for real faculty staff** during the pilot. They were added to demonstrate platform maturity and should be classified as internal/admin-only or hidden from the main navigation.

| Page | Route | Classification | Reason |
|------|-------|---------------|--------|
| Admin Intelligence Dashboard | `/admin-intelligence-dashboard` | HIDE_FROM_MAIN_NAV | Demo signal; not a daily faculty need; partially wired |
| Executive Analytics | `/analytics` | HIDE_FROM_MAIN_NAV | Enterprise trend analysis; D5 maturity; not exam-op |
| Governance Cockpit | `/governance` | HIDE_FROM_MAIN_NAV | Redundant with Dashboard + Workflow; enterprise framing |
| Operational Health | `/operational-health` | KEEP_INTERNAL_ADMIN_ONLY | IT/dev monitoring; no daily need for faculty |
| Audit Explorer | `/audit-explorer` | KEEP_INTERNAL_ADMIN_ONLY | Compliance/dev tool; not a daily workflow item |
| Optimizer Trace | `/optimizer-trace` | KEEP_INTERNAL_ADMIN_ONLY | Debug/admin tool; too technical for daily faculty |
| Platform Config | `/platform-config` | KEEP_INTERNAL_ADMIN_ONLY | Complex governance config; D3–D5; empty arrays in backend |
| Venues V2 | `/venues-v2` | DEFER_POST_PILOT | Already hidden; scope unclear; defer |
| Students V2 | `/students-v2` | DEFER_POST_PILOT | Already hidden; student data via import; defer |

**Classification principle:** If a real faculty staff member opened this page for the first time without guidance and could not immediately understand its purpose relative to their exam duties, it belongs in the internal/hidden category.

---

## What Should Never Appear for Specific Roles

| Role | Should Never See |
|------|-----------------|
| teacher | Payment config, admin analytics, system health, dev tools, governance |
| staff | Executive analytics, dev diagnostics, governance cockpit |
| print_shop | Everything except print queue |
| dept_supervisor | Payment settings, analytics, dev tools |
| student (public) | Everything except student search |

---

## Proposed Module Navigation Map

```
EMS Pilot Navigation
├── หน้าหลัก (Dashboard)
│
├── [Module 1: ตารางสอบ]
│   ├── ตารางสอบ (Schedule)
│   ├── นำเข้าข้อมูล (Import) [admin]
│   ├── ห้องสอบ (Rooms) [admin]
│   ├── ช่วงสอบ (Period) [admin]
│   ├── หน่วยงาน (Sections)
│   └── ผู้จัดการสอบ (Exam Manager) [admin, sup]
│
├── [Module 2: จัดคนคุมสอบ]
│   ├── ความพร้อมบุคลากร (Staff Availability) [admin]
│   ├── จัดคนคุมสอบ (Optimizer) [admin]
│   ├── ภาระงานคุมสอบ (Workload) [role-filtered]
│   └── สลับเวร (Swaps)
│
├── [Module 3: ส่งเอกสาร / คิว]
│   ├── ส่งข้อสอบ (Submissions)
│   ├── ตรวจก่อนพิมพ์ (Print Review) [admin, esq, sec]
│   ├── นับสำเนา (Copy Count) [admin, staff]
│   ├── คิวพิมพ์ (Print Queue) [print_shop]
│   ├── รับเอกสาร / QR (Check-ins)
│   └── สถานะห้อง (Room Attendance)
│
├── [Module 4: เอกสารประกอบการเบิก]
│   ├── อัตราค่าตอบแทน (Rate Rules)
│   ├── ตารางสรุปค่าตอบแทน (Payment Draft)
│   ├── บัญชีรายชื่อประกอบการเบิก (Advance Batch)
│   └── ตั้งค่าเอกสาร (Document Settings)
│
├── [Module 5: ส่งออก / ตั้งค่า]
│   ├── ศูนย์ส่งออก (Export Center)
│   ├── สอบภายนอก (External Exams)
│   └── อนุมัติงาน (Workflow) [admin, esq, sec]
│
└── [Hidden / Internal — URL access only]
    ├── /admin-intelligence-dashboard
    ├── /analytics
    ├── /governance
    ├── /operational-health
    ├── /audit-explorer
    ├── /optimizer-trace
    ├── /platform-config
    └── /import-audit
```

---

## Implementation Note

**No code changes are required to begin de-scoping.** Phase B (navigation cleanup) requires only:
1. Setting `hidden: true` on 8 page entries in `frontend/src/config/navigation.ts`
2. No route deletions, no component changes, no backend changes

Routes remain active. Admin can still navigate to all pages by direct URL. Only the sidebar presentation changes.
