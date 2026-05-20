"""
services/permission_service.py — Semantic domain permission helpers.

DOES NOT replace auth_utils.py or permissions.py.
Provides higher-level named predicates that encode business rules, so
pages/services can ask "can this user manage workflow?" instead of
checking raw role sets inline.

All functions return bool. They never raise exceptions — callers decide
how to respond (raise 403, hide UI, etc.).

Depends on: models.UserRole, auth_utils.get_effective_role
No FastAPI imports, no Depends(), no HTTPException.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import models


def _effective_role(user: "models.User") -> "models.UserRole":
    from auth_utils import get_effective_role
    return get_effective_role(user)


# ── User management ───────────────────────────────────────────

def can_manage_users(user: "models.User") -> bool:
    """Create, edit, deactivate users. Admin only."""
    from models import UserRole
    return _effective_role(user) == UserRole.admin


def can_view_user_list(user: "models.User") -> bool:
    """View the full user directory."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
    )


def can_use_view_as(user: "models.User") -> bool:
    """Admin impersonation feature (view_as_role). Real admin only, not impersonated admin."""
    from models import UserRole
    return user.role == UserRole.admin


def can_impersonate_admin(user: "models.User") -> bool:
    """Alias for can_use_view_as - check if user has real admin role (not impersonated)."""
    return can_use_view_as(user)


# ── Data visibility ───────────────────────────────────────────

def can_view_all(user: "models.User") -> bool:
    """Access cross-department data: schedules, submissions, audit logs."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
    )


def can_view_dept(user: "models.User", dept_code: str) -> bool:
    """
    True if user can view data for the given dept_code.
    admin/esq_head/secretary see all; dept_supervisor and teacher
    see only their own dept_code.
    """
    from models import UserRole
    from academic_groups import normalize_academic_group_code, can_access_academic_group

    role = _effective_role(user)
    if role in (UserRole.admin, UserRole.esq_head, UserRole.secretary):
        return True
    if role in (UserRole.dept_supervisor, UserRole.teacher):
        viewer = normalize_academic_group_code(getattr(user, "dept_code", None))
        target = normalize_academic_group_code(dept_code)
        return can_access_academic_group(viewer, target)
    return False


# ── Workflow management ───────────────────────────────────────

def can_manage_workflow(user: "models.User") -> bool:
    """Advance/revert workflow signing rounds, unlock swap windows."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
    )


def can_sign_workflow(user: "models.User") -> bool:
    """Sign a workflow round (same set as manage_workflow)."""
    return can_manage_workflow(user)


def can_manage_exam_periods(user: "models.User") -> bool:
    """Create, activate, lock, archive exam periods."""
    from models import UserRole
    return _effective_role(user) == UserRole.admin


# ── Export access ─────────────────────────────────────────────

def can_export_admin_reports(user: "models.User") -> bool:
    """Download full-faculty exports: all schedules, audit exports, print logs."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
    )


def can_export_own_department(user: "models.User") -> bool:
    """Download department-scoped exports."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
        UserRole.dept_supervisor,
    )


# ── Submissions ───────────────────────────────────────────────

def can_submit_exam_paper(user: "models.User") -> bool:
    """Create or update an exam submission."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.teacher,
        UserRole.dept_supervisor,
    )


def can_approve_submission(user: "models.User") -> bool:
    """Approve or reject a submission on behalf of the faculty."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
    )


# ── Schedule / print access ───────────────────────────────────

def can_manage_schedule(user: "models.User") -> bool:
    """Run the optimizer, assign supervisors, edit schedule entries."""
    from models import UserRole
    return _effective_role(user) == UserRole.admin


def can_access_print_queue(user: "models.User") -> bool:
    """View and update the print queue."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
        UserRole.print_shop,
    )


def can_access_external_exams(user: "models.User") -> bool:
    """Manage or view external (non-standard) exam entries."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.staff,
        UserRole.esq_head,
        UserRole.secretary,
    )


# ── Student schedule (object-level) ──────────────────────────

def can_view_student_schedule(
    user: "models.User",
    requested_student_id: int,
) -> bool:
    """
    True if user may view the schedule for requested_student_id.
    - admin/esq_head/secretary: always yes
    - student: only their own record
    - teacher/dept_supervisor: yes (they need it for context)
    - staff: yes (supervisors need it)
    - print_shop: no
    """
    from models import UserRole

    role = _effective_role(user)
    if role in (UserRole.admin, UserRole.esq_head, UserRole.secretary):
        return True
    if role in (UserRole.teacher, UserRole.dept_supervisor, UserRole.staff):
        return True
    if role == UserRole.student:
        return user.id == requested_student_id
    return False


# ── Optimization helpers ─────────────────────────────────────────

def can_run_optimization_recheck(user: "models.User") -> bool:
    """Run optimization recheck. admin, staff, esq_head, secretary."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.staff,
        UserRole.esq_head,
        UserRole.secretary,
    )


def can_view_governance_report(user: "models.User") -> bool:
    """View governance reports. admin, esq_head, secretary."""
    from models import UserRole
    return _effective_role(user) in (
        UserRole.admin,
        UserRole.esq_head,
        UserRole.secretary,
    )
