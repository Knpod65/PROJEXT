# EMS System Overview

This document describes the current frontend and its relationship to the EMS backend as of April 17, 2026. It is meant to be the working source of truth for new developers and future UI work.

---

## 1) SYSTEM OVERVIEW

### What EMS Frontend Is
The EMS frontend is a React single-page application for exam operations management. It is built as a role-based control center rather than a general-purpose website.

The frontend is responsible for:
- authenticating users
- selecting the active role for the session
- showing role-specific navigation and home routes
- exposing the operational pages for scheduling, submissions, swaps, attendance, printing, and administration
- previewing alternative role views for admin users through View-As

### High-Level Architecture
The system has three main layers:

1. React SPA
   - route-driven user interface
   - protected route guards
   - role-aware shell and navigation
   - page-level data hooks and view models

2. API-based services
   - frontend service modules call the FastAPI backend
   - service modules wrap auth, scheduling, printing, user management, and related endpoints
   - data is fetched through API calls whenever a page is backed by real system state

3. Role and session layer
   - login uses a chosen role context
   - the active role is stored in the authenticated session token
   - admin users can temporarily preview another role through View-As
   - public routes exist for role selection and student search

### Current Frontend Pattern
The current app uses a hybrid model:
- legacy V1 pages remain in place and are still routable
- V2 pages exist for Stitch-based redesign work
- preview and mock-only surfaces exist for unfinished product areas

This means the frontend is not a pure mock app and not yet a fully consolidated V2 app. It is a staged migration.

---

## 2) ROLE-BASED ARCHITECTURE [CRITICAL]

### Role List
The current system supports these roles:

- admin
- staff
- teacher
- dept_supervisor
- esq_head
- secretary
- print_shop
- student

### Role Responsibilities and Boundaries

#### admin
[PRODUCTION READY]
- full institutional access
- can access all admin routes
- can switch View-As for previewing other roles
- can see both legacy and V2 admin surfaces where routes exist
- can manage settings, users, periods, imports, workflow, swaps, rooms, venues, students, and oversight tools

Boundary:
- admin is the only role allowed to use View-As
- admin access is still constrained by route guards and feature availability

#### staff
[PRODUCTION READY]
- operational support role
- handles schedule-related operations, check-ins, swaps, and attendance workflows
- can access execution-oriented pages, not system administration pages

Boundary:
- staff cannot access admin-only configuration pages
- staff does not get View-As

#### teacher
[PRODUCTION READY]
- teaching-side operational role
- works with personal exam work, submissions, schedules, swaps, and check-ins
- can access their own exam coordination pages

Boundary:
- teacher cannot access admin-only pages
- teacher sees a narrower route set than staff and admin

#### dept_supervisor
[PRODUCTION READY]
- department-level oversight role
- sees department-scoped schedule, swaps, attendance, and workflow pages
- used for supervisory review and coordination inside a department

Boundary:
- dept_supervisor is broader than teacher but narrower than admin
- access is department-aware rather than institution-wide

#### esq_head
[PRODUCTION READY]
- executive quality and oversight role
- part of the same functional family as secretary
- can view all relevant institutional operations
- can sign or review in the approval flow
- is treated as read-heavy and oversight-oriented

Boundary:
- esq_head is not a normal edit-heavy operator role
- esq_head is paired with secretary in the same governance family

#### secretary
[PRODUCTION READY]
- same functional family as esq_head
- read-heavy institutional coordination role
- can view cross-organization information
- participates in review and sign-off flow

Boundary:
- secretary behaves like esq_head from a product perspective
- both are intentionally grouped as the ESQ family

#### print_shop
[PARTIAL]
- separate operational role for print production and dispatch
- not part of the ESQ family
- owns the print queue and delivery workflow
- should not be confused with admin, staff, or teacher

Boundary:
- print_shop is a dedicated production queue role
- access is limited to /print-queue and supporting print surfaces

#### student
[PRODUCTION READY for public lookup]
- public-facing exam visibility role
- does not represent a standard authenticated staff user journey
- used for student schedule lookup and related public surfaces

Boundary:
- student access is public-facing and read-only
- student does not participate in the admin workflow or operational shell in the same way as staff roles

### ESQ Head + Secretary Family Rule
ESQ Head and Secretary are intentionally treated as the same functional family in the product model.

This means:
- both are oversight and review roles
- both can see broad institutional data
- both are read-heavy rather than execution-heavy
- both belong to the governance and approval layer
- both share the same general access boundaries for full-view pages

### Print Shop Separation Rule
print_shop is intentionally separate from the ESQ family.

It is an operational production role with a narrow purpose:
- consume the print queue
- process batches
- mark dispatch and delivery state
- manage supply watch behavior

It is not a general oversight role and should not be treated as one.

---

## 3) ROLE ENTRY FLOW [VERY IMPORTANT]

### Production Flow
The production login flow is:

Role Selection -> Login -> Enter app

### Why This Exists
This is intentional and serves as double validation:
- the user first selects the intended workspace or role family
- the login request then submits the actual credentials together with the selected role
- the backend validates both identity and role permission

This avoids accidental access into the wrong workspace and keeps the authenticated session aligned with the chosen role context.

### Session Locking
After login:
- the backend issues an authenticated session token
- the token includes the active role for the session
- the frontend derives the active role from the authenticated user payload
- the active role determines routing, access, and shell styling

The session is role-locked in practice because the active role is stored in the authenticated session context and reused across the app.

### Admin-Only View-As
Admin users have a separate View-As flow.

Behavior:
- admin can switch the preview role without changing the base account
- the backend stores the impersonation state as view_as_role
- the frontend updates theme, shell labels, and access preview based on that state
- View-As is for preview and validation, not for changing the real account role

Important rule:
- only base admin can use View-As
- the preview role never replaces the underlying admin identity

---

## 4) ROUTING MODEL

### Core Route Groups
The app is organized around route guards and role-aware home routes.

Public routes:
- /role-selection
- /login
- /student-search

Protected routes:
- /dashboard
- /schedule
- /submissions
- /attendance
- /checkins
- /swaps
- /swaps-v2
- /sections
- /copy
- /print-queue
- /workflow
- /workflow-v2
- /coexam
- /optimizer
- /printreview
- /external
- /import
- /period
- /settings
- /settings-v2
- /rooms-v2
- /venues-v2
- /students-v2
- /users
- /users-v2
- /myexam
- /exammanager

### Home Routes
Current role home routes are:

- admin -> /dashboard
- esq_head -> /workflow
- secretary -> /workflow
- dept_supervisor -> /dashboard
- staff -> /dashboard
- teacher -> /dashboard
- student -> /student-search
- print_shop -> /print-queue

### Route Guards
The frontend uses two layers of protection:

1. ProtectedRoute
   - blocks unauthenticated access to private pages
   - routes unauthenticated users back to the public entry flow

2. GuardedPage
   - checks allowed roles for a page
   - can allow base admin preview on selected routes
   - returns an access-denied empty state if the role is not permitted

### Access Rules Worth Noting
- /print-queue is print_shop only
- /settings and /settings-v2 are admin only, with base admin preview allowed
- /swaps-v2, /workflow-v2, /students-v2, /rooms-v2, /venues-v2, /users-v2 are admin preview routes
- /student-search is public and does not require login

---

## 5) PAGE INVENTORY

### V1 [LEGACY]
[PRODUCTION READY]
These are the legacy routes that still represent the main working product flow:

| Route | Page | Status | Notes |
| --- | --- | --- | --- |
| /dashboard | DashboardPage | production ready | Main role-based landing page |
| /schedule | SchedulePage | production ready | Shared schedule and export page |
| /submissions | SubmissionsPage | production ready | Legacy submissions workflow |
| /attendance | RoomAttendancePage | production ready | Dedicated room attendance page |
| /checkins | CheckinsPage | production ready | Operational check-in tracking |
| /swaps | SwapsPage | production ready | Legacy swap workflow |
| /workflow | WorkflowPage | production ready | Legacy approval and sign-off flow |
| /settings | SettingsPage | production ready | Legacy settings page |
| /users | UsersPage | production ready | Legacy user admin page |
| /copy | CopyPage | production ready | Copy count and print cost support |
| /sections | SectionsPage | production ready | Section and assignment listing |
| /myexam | MyExamPage | production ready | Teacher personal exam work |
| /exammanager | ExamManagerPage | production ready but hidden | Manual assignment / admin utility |

### V2 [STITCH-BASED]
[PARTIAL]
These routes exist to bring Stitch-based role-specific experiences into the React app:

| Route | Page | Status | Notes |
| --- | --- | --- | --- |
| /swaps-v2 | SwapsV2Page | partial | Local-state V2 swap preview, no backend persistence |
| /workflow-v2 | WorkflowV2Page | partial | Read-only V2 workflow preview with local data |
| /students-v2 | StudentsV2Page | partial | Local mock student management preview |
| /rooms-v2 | RoomManagementV2Page | partial | Local mock room management preview |
| /venues-v2 | VenueManagementV2Page | partial | Local mock venue management preview |
| /users-v2 | UsersV2Page | partial | V2 user management preview, still under migration |
| /settings-v2 | SettingsV2Page | partial | View-As is real, settings fields are preview-only |

### Preview / Mock-Only Surfaces
[MOCK / PREVIEW]
There are no separate long-lived preview routes beyond the V2 pages above, but several internal surfaces are preview-only:

| Surface | Type | Status | Notes |
| --- | --- | --- | --- |
| Settings View-As panel | embedded preview UI | preview | Uses real admin View-As, but the form controls are mock |
| V2 swap actions | embedded preview UI | preview | Actions update local state only |
| V2 workflow actions | embedded preview UI | preview | Buttons are read-only placeholders |
| V2 student records | embedded preview UI | preview | Uses in-memory student rows |
| V2 room and venue data | embedded preview UI | preview | Uses in-memory room and venue rows |

### Production Readiness Summary
- V1 pages are the current production baseline
- V2 pages are a migration layer and should not be assumed complete
- Preview-only controls should not be treated as final backend behavior

---

## 6) DATA ARCHITECTURE

### services/*
The services layer contains the API wrappers used by the frontend.

Typical responsibilities:
- auth calls
- schedule queries
- printing workflow calls
- user management calls
- period and import calls
- export and review calls

The design goal is to keep network and endpoint details out of the pages themselves.

### hooks/*
The hooks layer contains the page-facing data models and interaction state.

Two major patterns are used:

1. Real API-backed hooks
   - useAsyncData is the shared async state wrapper
   - pages call services through loaders and then map the response into UI state
   - examples include users, dashboard, schedule, copy, imports, periods, and print queue pages

2. Mock or local-state hooks
   - the hook owns its own array or draft state
   - the hook simulates a product area before backend integration is complete
   - examples include SwapsV2, WorkflowV2, StudentsV2, Rooms/VenuesV2, and SettingsV2 preview fields

### useAsyncData
useAsyncData is the common async helper used by many pages.

It provides:
- data
- error
- loading
- reload

It reloads data when the loader or its dependency list changes.

This is the main abstraction for API-backed page state in the frontend.

### Real API-Backed Hooks
[PRODUCTION READY or PARTIAL depending on page]
These hooks are tied to live services or backend calls:

- useAsyncData-based pages that call services/*
- usePrintQueueData
- useUsersData
- dashboard and schedule loaders
- copy-count and export-related loaders
- import and period loaders
- my exam and external exam loaders

### Mock Hooks
[MOCK / PREVIEW]
These hooks are currently local-state or mock-data driven:

- useSwapsData
- useWorkflowData
- useStudentsData
- useRoomsData
- useSettingsData (settings form state is local; View-As is real)

---

## 7) FEATURE STATUS

| Feature | Status | Missing Pieces |
| --- | --- | --- |
| SwapsV2 | mock / preview | No backend persistence, local state only, no full integration with real swap APIs |
| WorkflowV2 | mock / preview | Read-only preview only, no real sign-off mutation, no backend write path |
| StudentsV2 | mock / preview | No backend-backed records, no import sync, no CRUD integration |
| Rooms/VenuesV2 | mock / preview | No live room or venue management API wiring, no persistence |
| SettingsV2 | partial | View-As is real, but settings fields are only preview state and do not save to backend |
| Print Queue | partial | Live queue actions exist, but supply alerts and manifest export are still manual / preview-oriented |

### Interpretation
- real means the feature is backed by live backend behavior and is intended for production use now
- partial means part of the workflow is real, but some user-facing pieces are still preview or manually simulated
- mock means the page exists mainly as a UI prototype or local-state demo

---

## 8) PRINT SHOP MODULE

### Purpose of print_shop
print_shop is a dedicated operational role for the print production and dispatch line.

Its job is to:
- receive released print jobs
- process batches through a queue
- move jobs through operational states
- dispatch and confirm delivery
- monitor supply readiness

### Route
- /print-queue

### What Is Real
[PARTIAL]
- the page is route-protected for print_shop only
- the queue uses live service calls for job state transitions
- copy-count totals are pulled into the page as supporting operational metrics
- job actions update the queue and reload the state

### What Is Still Preview or Manual
[MOCK / PREVIEW]
- supply alerts are static in-page alerts
- manifest export is currently a preview action
- the page still mixes real queue behavior with simulated support information

### Missing Backend Integrations
- automated manifest export pipeline
- formal supply inventory API
- dispatch confirmation integration with downstream logistics
- stronger audit trail for print production steps
- clearer separation between live queue data and support-panel mock data

---

## 9) KNOWN GAPS / RISKS

- available_roles is still a frontend fallback when the backend does not provide a populated role list
- mock data still exists in the V2 surfaces and should not be mistaken for final backend state
- no full build validation is guaranteed just by the presence of the pages
- V1 and V2 pages both exist for several areas, which creates duplication risk during navigation and maintenance
- View-As is admin-only and can be misread as a real account change if not documented clearly
- print_shop is a separate role and should not be merged into staff or admin logic
- student is a public-facing role and should not be forced into the same workflow as authenticated staff users

---

## 10) NEXT STEPS ROADMAP

### Critical Fixes
1. Replace remaining mock-only settings fields with backend persistence or clearly remove the save affordance.
2. Align all role-based entry points so session and route labels are consistent across login, home routes, and navigation.
3. Verify all V1 and V2 role routes after each migration step to avoid broken links or duplicate menu entries.
4. Add a build and route validation pass to catch regressions before cutover.

### Feature Completion
1. Convert SwapsV2 from local preview state into a real backend-backed workflow.
2. Convert WorkflowV2 from read-only preview into a real approval and sign-off pipeline.
3. Replace StudentsV2 mock records with backend-managed student data.
4. Replace Rooms/VenuesV2 mock inventory with live room and venue services.
5. Finish the Print Queue integration so manifest, dispatch, and supply tracking are all connected.

### Cleanup
1. Decide when each V1 page can be retired after the corresponding V2 route is stable.
2. Remove temporary preview labels once a V2 page becomes the production route.
3. Consolidate duplicated UI primitives where V1 and V2 components now overlap.
4. Keep this document updated whenever the route map or role model changes.

---

## Quick Reference

### Current Route Families
- Command: dashboard, schedule, submissions, attendance, checkins, swaps, workflow
- Teaching: myexam, sections, student-search
- Operations: copy, print-queue, coexam, optimizer, printreview, external
- System: import, period, settings, users, rooms-v2, venues-v2, students-v2

### Role Summary at a Glance
- admin: full control and View-As
- esq_head: governance and oversight, same family as secretary
- secretary: governance and oversight, same family as esq_head
- dept_supervisor: department-scoped supervision
- staff: operational execution
- teacher: personal academic coordination
- print_shop: dedicated print-production role
- student: public lookup role

### Source of Truth Notes
- routing lives in frontend/src/App.tsx and frontend/src/config/navigation.ts
- role helpers live in frontend/src/utils/roles.ts and frontend/src/store/auth.store.tsx
- real vs mock page behavior is split across frontend/src/hooks/* and frontend/src/services/*
- role definitions and backend session behavior are controlled by the FastAPI backend under backend/routers/auth.py and backend/auth_utils.py
