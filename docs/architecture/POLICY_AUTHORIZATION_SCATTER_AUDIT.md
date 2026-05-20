# Policy Authorization Scatter Audit

**Phase:** L5 - Final Policy-Only Authorization Alignment Pass  
**Date:** 2026-05-20  
**Goal:** Centralize scattered authorization checks into unified policy helpers.

---

## Executive Summary

Found 31+ inline authorization checks across 5 backend routers and 2 frontend pages that can be consolidated into semantic helpers in `backend/services/permission_service.py` and `frontend/src/utils/permissions.ts`.

---

## Backend Scattered Checks

### optimize_workflow.py

| Line(s) | Current Pattern | Recommended Helper |
|---------|-----------------|-------------------|
| 411-418 | `get_effective_role(current_user) not in (admin, staff, esq_head, secretary)` | `can_run_optimization_recheck(user)` |
| 464-470 | `get_effective_role(current_user) not in (admin, staff, esq_head, secretary)` | `can_run_optimization_recheck(user)` |

**Priority:** HIGH - Duplicated pattern, clear abstraction

---

### users.py

| Line(s) | Current Pattern | Recommended Helper |
|---------|-----------------|-------------------|
| 44 | `role in (models.UserRole.teacher, models.UserRole.dept_supervisor)` | `can_manage_users_ui` (teacher check not needed here - this is a filter) |
| 74 | `models.User.role == models.UserRole.admin` | `can_manage_users_ui(user)` |
| 91 | `user.role == models.UserRole.admin` | `can_impersonate_admin(user)` |
| 132 | `if user.role != models.UserRole.admin` | `can_impersonate_admin(user)` |
| 349 | `models.User.role == models.UserRole.staff` | N/A (filter logic, not auth) |

**Priority:** MEDIUM - Mix of auth and query filters

---

### exam_manager.py

| Line(s) | Current Pattern | Recommended Helper |
|---------|-----------------|-------------------|
| 80 | `if user.role == models.UserRole.admin:` | `can_manage_schedule(user)` |
| 86 | `elif user.role == models.UserRole.dept_supervisor:` | `can_manage_dept_schedule(user, dept_code)` |
| 214 | `current_user.role == models.UserRole.dept_supervisor` | `can_manage_dept_schedule(user, dept_code)` |
| 312-313 | `eff = get_effective_role(current_user)`, `is_admin = current_user.role == UserRole.admin` | `can_manage_schedule(user)`, `can_impersonate_admin(user)` |
| 331 | `models.User.role == models.UserRole.teacher` | Part of filter logic |
| 422 | `is_admin = current_user.role == models.UserRole.admin` | `can_manage_schedule(user)` |
| 459 | `models.User.role == models.UserRole.teacher` | Filter logic |
| 672 | `current_user.role == models.UserRole.dept_supervisor` | `can_manage_dept_schedule(user, dept_code)` |
| 688 | `elif current_user.role == models.UserRole.teacher` | Filter logic |
| 819 | `is_admin = current_user.role == models.UserRole.admin` | `can_manage_schedule(user)` |
| 900 | `is_admin = current_user.role == models.UserRole.admin` | `can_manage_schedule(user)` |

**Priority:** HIGH - Repeated admin checks, clear duplication

---

### submissions.py

| Line(s) | Current Pattern | Recommended Helper |
|---------|-----------------|-------------------|
| 108 | `effective = get_effective_role(user)` | Use `permissions.py` `assert_submission_access` instead |
| 200 | `effective = get_effective_role(current_user)` | Use `permissions.py` `assert_submission_access` instead |
| 266 | `effective = get_effective_role(current_user)` | Use `permissions.py` `assert_submission_access` instead |
| 828 | `effective = get_effective_role(current_user)` | Use `permissions.py` `assert_submission_access` instead |

**Priority:** MEDIUM - Can consolidate to existing `assert_submission_access`

---

### public.py

| Line(s) | Current Pattern | Recommended Helper |
|---------|-----------------|-------------------|
| 166-178 | `get_effective_role` + inline role list | `can_view_student_schedule(user, ...)` (uses existing logic) |

**Priority:** LOW - Edge case, already has some semantic logic

---

## Frontend Scattered Checks

### Optimizer.tsx

| Line | Current Pattern | Replacement |
|------|-----------------|-------------|
| 342 | `const isAdmin = role === "admin";` | `const isAdmin = canManageExamPeriods(user);` |

**Priority:** HIGH - Simple replacement

---

### ExamManager.tsx

| Line | Current Pattern | Replacement |
|------|-----------------|-------------|
| 125 | `user?.role === "dept_supervisor" ? t("roles.dept_supervisor") : t("roles.admin")` | `getEffectiveRole(user) === "dept_supervisor" ? ...` |

**Priority:** LOW - Display logic, not authorization

---

## Existing Helpers (Reuse)

### Backend: backend/services/permission_service.py

Already exists with 11 helpers:
- `can_manage_users`
- `can_view_user_list`
- `can_use_view_as`
- `can_view_all`
- `can_view_dept`
- `can_manage_workflow`
- `can_sign_workflow`
- `can_manage_exam_periods`
- `can_export_admin_reports`
- `can_export_own_department`
- `can_submit_exam_paper`
- `can_approve_submission`
- `can_manage_schedule`
- `can_access_print_queue`
- `can_access_external_exams`
- `can_view_student_schedule`

### Frontend: frontend/src/utils/permissions.ts

Mirrors backend with 15 helpers:
- `canManageUsers`
- `canViewUserList`
- `canUseViewAs`
- `canViewAll`
- `canExportAdminReports`
- `canExportOwnDepartment`
- `canManageWorkflow`
- `canSignWorkflow`
- `canManageExamPeriods`
- `canSubmitExamPaper`
- `canApproveSubmission`
- `canManageSchedule`
- `canAccessPrintQueue`
- `canManageOperationalWork`
- `canAccessExternalExams`
- `canViewOwnExamWork`
- `canManageCoExam`
- `canViewSettings`
- `canEditSettings`

---

## Recommended New Helpers

| Helper | Signature | Logic |
|--------|-----------|-------|
| `can_run_optimization_recheck` | `(user) -> bool` | `role in (admin, staff, esq_head, secretary)` |
| `can_view_governance_report` | `(user) -> bool` | `role in (admin, esq_head, secretary)` |
| `can_impersonate_admin` | `(user) -> bool` | `user.role == admin` (base role, not effective) |

---

## Migration Strategy

1. **L5-s0:** Document (this file)
2. **L5-s1:** Extend `permission_service.py` with missing helpers
3. **L5-s2:** Replace inline checks in `optimize_workflow.py`, `exam_manager.py`
4. **L5-s3:** Create `usePermission` hook
5. **L5-s4:** Replace frontend inline checks