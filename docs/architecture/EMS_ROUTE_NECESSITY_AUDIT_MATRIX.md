# EMS Route Necessity Audit Matrix

**Date:** 2026-06-30
**Auditor:** Original Intent Recenter Pass
**Routes audited:** 50 active routes + 6 legacy page files + 9 misplaced source artifacts
**No code was changed in this pass.**

---

## Recommendation Legend

| Code | Meaning |
|------|---------|
| `CORE_KEEP` | Core to original intent; do not reduce visibility |
| `KEEP_BUT_SIMPLIFY` | Valuable but over-exposed or duplicated in nav; simplify placement |
| `KEEP_INTERNAL_ADMIN_ONLY` | Keep route active; hide from main nav; accessible by direct URL for admin/dev |
| `HIDE_FROM_MAIN_NAV` | Remove from sidebar; keep route active; admin can still navigate to it |
| `MERGE_WITH_ANOTHER_PAGE` | Functionality should be absorbed into a sibling page |
| `DEFER_POST_PILOT` | Already hidden; defer any decision until after pilot |
| `ARCHIVE_ROUTE_LATER` | Legacy file still exists but no longer actively routed; schedule for cleanup |
| `REMOVE_CANDIDATE_AFTER_CONFIRMATION` | Candidate for deletion; requires explicit user confirmation |
| `DO_NOT_TOUCH_CRITICAL` | Core exam-day or auth path; regression risk is unacceptable |

---

## Active Route Audit Table

| Route | Component | In Nav | Roles | Family | User Need It Serves | Relation to Original Intent | Business Value | Theme Consistent | Cognitive Load | Data Ready | Recommendation | Rationale |
|-------|-----------|--------|-------|--------|--------------------|-----------------------------|----------------|-----------------|---------------|------------|----------------|-----------|
| `/` | HomeRedirect | No | All | Auth | Auto-redirect to role home | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | Auth entry point; removing would break login flow |
| `/login` | LoginPage | No | Public | Auth | Authentication | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | Auth |
| `/role-selection` | RoleSelectionPage | No | Public | Auth | Role intent before login | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | Auth |
| `/student-search` | StudentSearchRoute | No | Public | Public | Public exam timetable lookup | Core | High | Yes | Low | Yes | CORE_KEEP | Serves students; public access; no auth required |
| `/dashboard` | DashboardPage | Yes | admin, esq_head, secretary, dept_supervisor, staff, teacher | Dashboard | Main operational overview | Core | High | Yes | Medium | Yes | CORE_KEEP | Primary landing page for all roles; operational hub |
| `/admin-intelligence-dashboard` | AdminIntelligenceDashboard | Yes | admin | Analytics | Role-based platform metrics | Peripheral | Medium | Yellow | High | Partial | HIDE_FROM_MAIN_NAV | Added for demo maturity signal; not a daily faculty need; partially wired; high cognitive load |
| `/workload-duty-analytics` | WorkloadDutyAnalytics | Yes | admin | Analytics | Exam duty fairness audit (admin view) | Related | Medium | Yes | Medium | Yes | KEEP_BUT_SIMPLIFY | Same component as /duty-workload and /my-workload; three nav entries for one concept; consolidate |
| `/duty-workload` | WorkloadDutyAnalytics | Yes | staff, dept_supervisor, esq_head, secretary | Analytics | Exam duty fairness audit (staff view) | Related | Medium | Yes | Medium | Yes | KEEP_BUT_SIMPLIFY | Same component; keep route; reduce to one nav entry labeled "ภาระงานคุมสอบ" |
| `/my-workload` | WorkloadDutyAnalytics | Yes | teacher | Analytics | My exam duty summary | Related | Medium | Yes | Low | Yes | KEEP_BUT_SIMPLIFY | Teacher view of same component; keep route active; rename nav entry |
| `/analytics` | ExecutiveAnalytics | Yes | admin, esq_head, secretary | Analytics | Institutional health and trend analysis | Peripheral | Low | Yellow | High | Partial | HIDE_FROM_MAIN_NAV | Enterprise framing; D5 maturity target; not tied to daily exam-op workflow; partially wired |
| `/governance` | GovernanceCockpit | Yes | admin, esq_head, secretary | Governance | Approval blocker aggregation | Peripheral | Low | Yellow | High | Partial | HIDE_FROM_MAIN_NAV | Blocker visibility already in Dashboard + Workflow; "governance cockpit" is enterprise framing; D5 maturity |
| `/workflow` | WorkflowV2Page | Yes | admin, esq_head, secretary | Ops | Approval pipeline and signatures | Core | High | Yes | Medium | Yes | CORE_KEEP | Multi-step sign-off is central to exam readiness gate |
| `/copy` | CopyPage | Yes | admin, staff | Ops | Sheet counts and copy cost planning | Core | High | Yes | Low | Yes | CORE_KEEP | Essential pre-exam paper preparation; directly supports print workflow |
| `/print-queue` | PrintQueuePage | Yes | print_shop | Ops | Print shop work queue | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | Only entry point for print_shop role; removing would make role unusable |
| `/printreview` | PrintReviewPage | Yes | admin, esq_head, secretary | Ops | Pre-print verification gate | Core | High | Yes | Low | Yes | CORE_KEEP | Required gate before print job is released |
| `/coexam` | CoExamPage | Yes | admin | Ops | Shared-exam candidate grouping | Related | Medium | Yes | Medium | Partial | KEEP_BUT_SIMPLIFY | Useful for complex multi-department exams; specialized; lower nav prominence acceptable |
| `/optimizer` | OptimizerPage | Yes | admin | Ops | Room and invigilator assignment optimization | Core | High | Yes | High | Yes | CORE_KEEP | Core scheduling optimization; must keep; high complexity is justified by function |
| `/optimizer-trace` | OptimizerTraceExplorerPage | Yes | admin | Dev/Admin | Optimization candidate lineage and scoring | Dev tool | Low | Yellow | Very High | Partial | KEEP_INTERNAL_ADMIN_ONLY | Too technical for daily faculty use; intended for admin debug; hide from main nav |
| `/staff-availability` | StaffAvailabilityPage | Yes | admin | Ops | Staff availability blocks | Core | High | Yes | Low | Yes | CORE_KEEP | Required input before optimizer can produce valid assignments |
| `/rooms-v2` | RoomManagementV2Page | Yes | admin | Ops | Room capacity and blocking | Core | High | Yes | Low | Yes | CORE_KEEP | Room configuration is a prerequisite for schedule and optimizer |
| `/external` | ExternalPage | Yes | admin, staff | Ops | External exam staff allocation | Related | Medium | Yes | Medium | Yes | CORE_KEEP | Needed for non-standard sessions that fall outside the main schedule |
| `/exports-center` | ExportCenterPage | Yes | admin, staff | Ops | Centralized document and data exports | Core | High | Yes | Low | Yes | CORE_KEEP | Central hub for schedule, workload, payment, and paper distribution exports |
| `/invigilation-advance-batch-preview` | AdvanceInvigilationBatchPreview | Yes | admin, staff | Payment | Draft advance disbursement roster | Core | High | Yes | Medium | Yes | CORE_KEEP | Supporting finance roster; draft-only; core payment support output |
| `/invigilation-rate-rules` | InvigilationRateRules | Yes | admin, staff | Payment | Weekday/weekend rate configuration | Core | High | Yes | Low | Yes | CORE_KEEP | Rate input required before payment calculation can proceed |
| `/invigilation-payment-document-draft` | OfficialPaymentDocumentDraft | Yes | admin, staff | Payment | Draft payment table preview | Core | High | Yes | Medium | Yes | CORE_KEEP | Primary invigilation payment draft output; draft-only |
| `/payment-document-settings` | PaymentDocumentSettings | Yes | admin, esq_head, secretary, staff | Payment | Term-specific draft document settings | Core | High | Yes | Low | Yes | CORE_KEEP | Required to configure draft payment parameters |
| `/historical-schedules` | HistoricalSchedulesPage | Yes | admin | Analytics | Historical schedule comparison | Related | Medium | Yes | Medium | Partial | KEEP_BUT_SIMPLIFY | Seasonal use (post-optimization fairness audit); should be accessible to more roles; lower nav prominence |
| `/sections` | SectionsPage | Yes | admin, esq_head, secretary, dept_supervisor, staff, teacher | Academic | Course sections and enrollments | Core | High | Yes | Low | Yes | CORE_KEEP | Academic reference data; most roles need visibility |
| `/myexam` | MyExamPage | Yes | teacher | Academic | Teacher's personal exam assignments | Core | High | Yes | Low | Yes | CORE_KEEP | Teacher's primary view of their own duties |
| `/import` | ImportV2Page | Yes | admin | Data | Bulk data intake with staged validation | Core | High | Yes | Medium | Yes | CORE_KEEP | Critical for populating schedule; ImportV2 is the current active version |
| `/import-audit` | ImportAuditPage | Yes | admin | Dev/Admin | Import execution audit and row-level logs | Admin | Low | Yes | Medium | Yes | KEEP_INTERNAL_ADMIN_ONLY | Admin/dev review tool; not needed in daily faculty workflow; hide from main nav |
| `/users` | UsersV2Page | No (hidden) | admin | Admin | User registry and role management | Core | High | Yes | Low | Yes | CORE_KEEP | Hidden from nav is already correct; direct URL access for admin is the right pattern |
| `/period` | PeriodPage | Yes | admin | Admin | Exam period (term) management | Core | High | Yes | Low | Yes | CORE_KEEP | Foundation for all modules; all operations depend on active period |
| `/settings` | SettingsV2Page | No (hidden) | admin | Admin | System configuration and deadlines | Core | High | Yes | Low | Yes | CORE_KEEP | Hidden from nav is already correct; must remain accessible |
| `/platform-config` | PlatformConfigurationPage | Yes | admin | Dev/Admin | Faculty governance config (D3 faculty, governance) | Dev tool | Low | Yellow | Very High | Partial | KEEP_INTERNAL_ADMIN_ONLY | D3–D5 maturity feature; backend shows empty arrays; complex; not for daily faculty use |
| `/operational-health` | OperationalHealthPage | Yes | admin, esq_head | Dev/Admin | Backend and service health monitoring | Dev tool | Low | Yellow | High | Yes | KEEP_INTERNAL_ADMIN_ONLY | IT/dev monitoring tool; no daily need for faculty staff; should be URL-direct only |
| `/audit-explorer` | AuditExplorerPage | Yes | admin, esq_head | Dev/Admin | Audit events and lifecycle browser | Dev tool | Low | Yellow | High | Yes | KEEP_INTERNAL_ADMIN_ONLY | Compliance/dev tool; not a daily faculty workflow need; PDPA-relevant but not user-facing |
| `/venues-v2` | VenueManagementV2Page | No (hidden) | admin | Admin | Venue management | Related | Low | Yes | Low | Partial | DEFER_POST_PILOT | Already hidden; rarely needed separately from room management; defer scope decision to post-pilot |
| `/students-v2` | StudentsV2Page | No (hidden) | admin | Admin | Student records management | Related | Low | Yes | Low | Partial | DEFER_POST_PILOT | Already hidden; student data comes via import; direct management rarely needed; defer |
| `/exammanager` | ExamManagerPage | Yes | admin, dept_supervisor | Academic | Department course ownership assignment | Core | High | Yes | Low | Yes | CORE_KEEP | Required to assign midterm/final ownership before submissions can proceed |
| `/submissions` | SubmissionsPage | Yes | admin, esq_head, secretary, dept_supervisor, teacher | Core Ops | Multi-step exam paper submission workflow | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | Critical multi-role workflow; teacher → dept → approval chain |
| `/attendance` | RoomAttendancePage | Yes | admin, esq_head, secretary, dept_supervisor, staff, teacher | Core Ops | Room-by-room exam day operations | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | Live exam day operations; all roles need access |
| `/checkins` | CheckinsPage | Yes | admin, dept_supervisor, staff, teacher | Core Ops | QR scan and paper pickup check-in | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | QR-based paper handoff is a core exam-day workflow |
| `/swaps` | SwapsV2Page | Yes | admin, dept_supervisor, staff, teacher | Core Ops | Invigilator schedule swap requests | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | Critical flexibility mechanism for invigilation schedule |
| `/schedule` | SchedulePage | Yes | admin, esq_head, secretary, dept_supervisor, staff, teacher | Core Ops | Master exam timetable | Core | High | Yes | Low | Yes | DO_NOT_TOUCH_CRITICAL | THE primary product; the exam schedule is what EMS exists to produce |

---

## Summary by Recommendation

| Recommendation | Count | Routes |
|----------------|-------|--------|
| DO_NOT_TOUCH_CRITICAL | 7 | `/`, `/login`, `/role-selection`, `/print-queue`, `/submissions`, `/attendance`, `/checkins`, `/swaps`, `/schedule` |
| CORE_KEEP | 21 | `/student-search`, `/dashboard`, `/workflow`, `/copy`, `/printreview`, `/optimizer`, `/staff-availability`, `/rooms-v2`, `/external`, `/exports-center`, `/invigilation-advance-batch-preview`, `/invigilation-rate-rules`, `/invigilation-payment-document-draft`, `/payment-document-settings`, `/sections`, `/myexam`, `/import`, `/users`, `/period`, `/settings`, `/exammanager` |
| KEEP_BUT_SIMPLIFY | 5 | `/workload-duty-analytics`, `/duty-workload`, `/my-workload`, `/coexam`, `/historical-schedules` |
| KEEP_INTERNAL_ADMIN_ONLY | 6 | `/optimizer-trace`, `/import-audit`, `/platform-config`, `/operational-health`, `/audit-explorer` + `/platform-config` |
| HIDE_FROM_MAIN_NAV | 3 | `/admin-intelligence-dashboard`, `/analytics`, `/governance` |
| DEFER_POST_PILOT | 2 | `/venues-v2`, `/students-v2` |

**Total: 44 active routes classified** (50 registered minus redirect aliases)

---

## Legacy Page Files (Still on Disk, Not Actively Routed)

These files exist in `frontend/src/pages/` but their routes now point to V2 successors.

| File | Superseded By | Current Route Target | Recommendation |
|------|--------------|---------------------|----------------|
| `pages/Import.tsx` | `pages/ImportV2.tsx` | `/import` → ImportV2Page | ARCHIVE_ROUTE_LATER |
| `pages/Swaps.tsx` | `pages/SwapsV2.tsx` | `/swaps` → SwapsV2Page | ARCHIVE_ROUTE_LATER |
| `pages/Workflow.tsx` | `pages/WorkflowV2.tsx` | `/workflow` → WorkflowV2Page | ARCHIVE_ROUTE_LATER |
| `pages/Settings.tsx` | `pages/SettingsV2.tsx` | `/settings` → SettingsV2Page | ARCHIVE_ROUTE_LATER |
| `pages/Users.tsx` | `pages/UsersV2.tsx` | `/users` → UsersV2Page | ARCHIVE_ROUTE_LATER |
| `pages/RoleDashboard.tsx` | `pages/Dashboard.tsx` | Not actively routed | ARCHIVE_ROUTE_LATER |

**Action:** Do not delete now. Schedule for Phase D (post-pilot) cleanup. Confirm routes point to V2 components before removing legacy files.

---

## Misplaced Source Files in docs/architecture/

The following React/TypeScript source files were found untracked inside `docs/architecture/`. Source code does not belong in the docs directory. These are likely accidental copies.

| File Found in docs/ | Likely Origin | Action Required |
|--------------------|--------------|-----------------|
| `docs/architecture/Import.tsx` | `frontend/src/pages/Import.tsx` | Move to correct location OR delete if already superseded |
| `docs/architecture/PagePlaceholder.tsx` | `frontend/src/pages/PagePlaceholder.tsx` | Move or delete |
| `docs/architecture/RoleDashboard.tsx` | `frontend/src/pages/RoleDashboard.tsx` | Move or delete |
| `docs/architecture/Settings.tsx` | `frontend/src/pages/Settings.tsx` | Move or delete |
| `docs/architecture/Swaps.tsx` | `frontend/src/pages/Swaps.tsx` | Move or delete |
| `docs/architecture/Users.tsx` | `frontend/src/pages/Users.tsx` | Move or delete |
| `docs/architecture/Workflow.tsx` | `frontend/src/pages/Workflow.tsx` | Move or delete |
| `docs/architecture/useEffectiveRole.ts` | `frontend/src/hooks/useEffectiveRole.ts` | Move or delete |
| `docs/architecture/useRoleDashboard.ts` | `frontend/src/hooks/domain/useRoleDashboard.ts` | Move or delete |

**These files were NOT included in this audit commit. They require a separate cleanup pass.**

---

## Pre-existing Dirty State (Not Part of This Audit)

| Item | Status | Recommended Action |
|------|--------|--------------------|
| `frontend/src/hooks/useEffectiveRole.ts` | M (modified) | Review change, commit separately or stash |
| `frontend/src/hooks/PageSkeleton.tsx` | ?? (untracked) | Review, stage, and commit separately |
| Misplaced `.tsx`/`.ts` in `docs/architecture/` | ?? (untracked) | Resolve in a separate cleanup pass |
