# EMS Simplified Navigation Proposal

**Date:** 2026-06-30
**Purpose:** Propose a focused sidebar navigation for the EMS pilot. No code changes in this pass — this is a proposal to be approved before Phase B implementation.

---

## Design Principle

Every item in the main navigation should pass this test:

> "A real faculty staff member could open this for the first time and immediately know what it's for, without explanation."

Items that fail this test belong in a secondary or hidden section.

---

## Proposed Main Navigation

The following items should appear in the sidebar for the roles indicated. All other pages remain accessible by direct URL to admin users.

### Group 1 — หน้าหลัก (Home)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| หน้าหลัก | Dashboard | `/dashboard` | All authenticated roles |

---

### Group 2 — ตารางสอบ (Exam Schedule)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| ตารางสอบ | Exam Schedule | `/schedule` | All staff |
| นำเข้าข้อมูล | Import Data | `/import` | admin |
| ห้องสอบ | Rooms | `/rooms-v2` | admin |
| ช่วงสอบ | Exam Periods | `/period` | admin |
| หน่วยงาน | Sections | `/sections` | admin, esq_head, secretary, dept_supervisor, staff, teacher |
| ผู้จัดการสอบ | Exam Manager | `/exammanager` | admin, dept_supervisor |

---

### Group 3 — จัดคนคุมสอบ (Invigilation)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| ความพร้อมบุคลากร | Staff Availability | `/staff-availability` | admin |
| จัดคนคุมสอบ | Assign Invigilators | `/optimizer` | admin |
| ภาระงานคุมสอบ | Invigilation Workload | `/workload-duty-analytics` (admin), `/duty-workload` (staff/esq/sec/sup), `/my-workload` (teacher) | All staff (role-filtered) |
| สลับเวร | Swaps | `/swaps` | admin, dept_supervisor, staff, teacher |
| งานสอบของฉัน | My Exam | `/myexam` | teacher |

**Note on workload:** All three workload routes use the same component. The nav should show a single "ภาระงานคุมสอบ" entry per role that links to the appropriate route. This is already how role-filtering works — this proposal just formalizes the label.

---

### Group 4 — ส่งเอกสาร / คิว (Submissions & Print)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| ส่งข้อสอบ | Submissions | `/submissions` | admin, esq_head, secretary, dept_supervisor, teacher |
| ตรวจก่อนพิมพ์ | Print Review | `/printreview` | admin, esq_head, secretary |
| นับสำเนา | Copy Count | `/copy` | admin, staff |
| คิวพิมพ์ | Print Queue | `/print-queue` | print_shop |

---

### Group 5 — รับ-ส่งเอกสาร (Handoff & Check-in)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| รับเอกสาร / QR | Check-in / QR Pickup | `/checkins` | admin, dept_supervisor, staff, teacher |
| สถานะห้องสอบ | Room Attendance | `/attendance` | admin, esq_head, secretary, dept_supervisor, staff, teacher |

---

### Group 6 — เอกสารประกอบการเบิก (Payment Documents)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| อัตราค่าตอบแทน | Rate Settings | `/invigilation-rate-rules` | admin, staff |
| ตารางสรุป (ร่าง) | Draft Payment Summary | `/invigilation-payment-document-draft` | admin, staff |
| บัญชีรายชื่อ (ร่าง) | Draft Supporting Roster | `/invigilation-advance-batch-preview` | admin, staff |
| ตั้งค่าเอกสาร | Document Settings | `/payment-document-settings` | admin, esq_head, secretary, staff |

---

### Group 7 — ส่งออก / อนุมัติ (Exports & Approval)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| ศูนย์ส่งออก | Export Center | `/exports-center` | admin, staff |
| อนุมัติงาน | Workflow / Approval | `/workflow` | admin, esq_head, secretary |
| สอบภายนอก | External Exams | `/external` | admin, staff |
| สอบร่วม | Co-Exam | `/coexam` | admin |

---

### Group 8 — ประวัติ (Historical — Secondary)

| Thai Label | English | Route | Roles |
|-----------|---------|-------|-------|
| ประวัติตาราง | Historical Schedules | `/historical-schedules` | admin, esq_head, secretary, staff (expanded from admin-only) |

**Note:** This group is secondary and can be placed at lower nav prominence. Expanding role access beyond admin is recommended for fairness transparency (see Scope Bloat report).

---

## Proposed Hidden / Internal Section

The following pages should have `hidden: true` set in `navigation.ts`. Routes remain active. Admin can navigate to them by direct URL.

| Page | Route | Keep Route? | Hide Nav? | Admin URL Access? | Reason for Hiding |
|------|-------|-------------|----------|-----------------|------------------|
| Admin Intelligence Dashboard | `/admin-intelligence-dashboard` | Yes | Yes | Yes | Demo signal; not daily exam ops; partially wired |
| Executive Analytics | `/analytics` | Yes | Yes | Yes | Enterprise trends; D5 maturity; not exam-op |
| Governance Cockpit | `/governance` | Yes | Yes | Yes | Redundant with Dashboard + Workflow; enterprise framing |
| Operational Health | `/operational-health` | Yes | Yes | Yes | IT/dev monitoring tool; not for faculty |
| Audit Explorer | `/audit-explorer` | Yes | Yes | Yes | Compliance/dev tool; not daily faculty workflow |
| Optimizer Trace | `/optimizer-trace` | Yes | Yes | Yes | Debug/admin tool; too technical for faculty |
| Platform Configuration | `/platform-config` | Yes | Yes | Yes | Complex governance config; empty arrays in backend |
| Import Audit | `/import-audit` | Yes | Yes | Yes | Admin review tool; not daily use |
| Users | `/users` | Yes | Yes (already) | Yes | Already hidden; correct pattern |
| Settings | `/settings` | Yes | Yes (already) | Yes | Already hidden; correct pattern |
| Venues V2 | `/venues-v2` | Yes | Yes (already) | Yes | Already hidden; defer |
| Students V2 | `/students-v2` | Yes | Yes (already) | Yes | Already hidden; defer |

---

## Comparison: Current vs. Proposed

### Current nav (items visible in sidebar, aggregated across all roles)
All 5 nav groups visible to relevant roles:
1. dashboard — 6 items (Dashboard, Admin Intelligence, Workload ×3, Executive Analytics, Governance)
2. operations — 17 items (Workflow, Copy, Print Queue, Print Review, Co-Exam, Optimizer, Optimization Trace, Staff Availability, Rooms, External, Export Center, Advance Batch, Rate Rules, Payment Draft, Payment Settings, Historical, Import Audit)
3. examManagement — 6 items (Sections, My Exam, Import, Import Audit, Exam Manager)
4. people — 1 item (Users — already hidden)
5. system — 7 items (Period, Platform Config, Operational Health, Audit Explorer, Settings, Venues, Students)

**Total visible items (before role filtering):** ~37

### Proposed nav (items visible in sidebar)
1. หน้าหลัก — 1 item
2. ตารางสอบ — 6 items
3. จัดคนคุมสอบ — 5 items
4. ส่งเอกสาร / คิว — 4 items
5. รับ-ส่งเอกสาร — 2 items
6. เอกสารประกอบการเบิก — 4 items
7. ส่งออก / อนุมัติ — 4 items
8. ประวัติ — 1 item (secondary)

**Total visible items (before role filtering):** 27

**Reduction: ~10 items removed from main nav** (moved to hidden/internal)

---

## Mobile Navigation

No changes proposed for mobile bottom nav. Current `mobilePageKeys` are already minimal:
- Dashboard
- Schedule
- Submissions
- Attendance
- Check-ins

These are the correct choices for mobile exam-day operations.

---

## What Stays Unchanged

- All route paths remain the same
- All role guards remain the same
- All backend APIs remain the same
- All component code remains the same
- Auth/login/redirect flows unchanged
- Print shop workflow unchanged
- Payment draft pages unchanged
- QR/check-in flows unchanged

**The only change in Phase B is:** setting `hidden: true` on the 8 pages listed above in `frontend/src/config/navigation.ts`.

---

## ASCII Navigation Diagram (Proposed)

```
┌─────────────────────────────────────┐
│  EMS — ระบบจัดการสอบ               │
├─────────────────────────────────────┤
│  [role avatar]  [term badge]        │
├─────────────────────────────────────┤
│  ● หน้าหลัก                        │
├─────────────────────────────────────┤
│  ตารางสอบ                           │
│  ├─ ตารางสอบ                       │
│  ├─ นำเข้าข้อมูล      [admin]      │
│  ├─ ห้องสอบ           [admin]      │
│  ├─ ช่วงสอบ           [admin]      │
│  ├─ หน่วยงาน                       │
│  └─ ผู้จัดการสอบ     [admin/sup]   │
├─────────────────────────────────────┤
│  จัดคนคุมสอบ                        │
│  ├─ ความพร้อมบุคลากร  [admin]      │
│  ├─ จัดคนคุมสอบ       [admin]      │
│  ├─ ภาระงานคุมสอบ                  │
│  ├─ สลับเวร                        │
│  └─ งานสอบของฉัน      [teacher]    │
├─────────────────────────────────────┤
│  ส่งเอกสาร / คิว                    │
│  ├─ ส่งข้อสอบ                      │
│  ├─ ตรวจก่อนพิมพ์    [admin/esq]   │
│  ├─ นับสำเนา          [admin/staff] │
│  └─ คิวพิมพ์          [print_shop] │
├─────────────────────────────────────┤
│  รับ-ส่งเอกสาร                      │
│  ├─ รับเอกสาร / QR                 │
│  └─ สถานะห้องสอบ                   │
├─────────────────────────────────────┤
│  เอกสารประกอบการเบิก                │
│  ├─ อัตราค่าตอบแทน                 │
│  ├─ ตารางสรุป (ร่าง)               │
│  ├─ บัญชีรายชื่อ (ร่าง)            │
│  └─ ตั้งค่าเอกสาร                  │
├─────────────────────────────────────┤
│  ส่งออก / อนุมัติ                    │
│  ├─ ศูนย์ส่งออก                    │
│  ├─ อนุมัติงาน        [admin/esq]  │
│  ├─ สอบภายนอก                      │
│  └─ สอบร่วม           [admin]      │
├─────────────────────────────────────┤
│  ประวัติ                            │
│  └─ ประวัติตาราง                   │
├─────────────────────────────────────┤
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │
│  [Hidden — URL access only]         │
│  /admin-intelligence-dashboard      │
│  /analytics                         │
│  /governance                        │
│  /operational-health                │
│  /audit-explorer                    │
│  /optimizer-trace                   │
│  /platform-config                   │
│  /import-audit                      │
└─────────────────────────────────────┘
```

---

## Implementation Prerequisite

Before implementing Phase B, user must confirm answers to the decision questions in `EMS_SCOPE_RECENTER_DECISION_QUESTIONS.md`. Specifically:
- Q1–Q8: Which pages to hide (this proposal recommends all 8)
- Q9: Whether Historical Schedules role access should be expanded
- Q10: Whether the workload nav consolidation is acceptable
