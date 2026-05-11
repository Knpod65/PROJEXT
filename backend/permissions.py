"""
permissions.py — Centralized RBAC & Object-Level Authorization
================================================================
Single source of truth for role-based access decisions.
All routers import from here instead of duplicating role checks.
"""
from __future__ import annotations
from typing import Optional, Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
from models import UserRole
from database import get_db

# ── Role capability sets ──────────────────────────────────────────────────────

VIEW_ALL_ROLES: Set[UserRole] = {
    UserRole.admin,
    UserRole.esq_head,
    UserRole.secretary,
}

WRITE_ROLES: Set[UserRole] = {
    UserRole.admin,
    UserRole.teacher,
    UserRole.dept_supervisor,
}

SIGNER_ROLES: Set[UserRole] = {
    UserRole.admin,
    UserRole.esq_head,
    UserRole.secretary,
}

SUPERVISION_ROLES: Set[UserRole] = {
    UserRole.admin,
    UserRole.staff,
    UserRole.teacher,
}


# ── Effective role (respects view_as impersonation) ──────────────────────────

def get_effective_role(user: models.User) -> UserRole:
    if user.role == UserRole.admin and user.view_as_role:
        return user.view_as_role
    return user.role


def get_dept_filter(user: models.User) -> Optional[str]:
    """Returns dept_code restriction, or None = see all."""
    if user.role in VIEW_ALL_ROLES:
        return None
    if user.role in (UserRole.dept_supervisor, UserRole.teacher):
        return user.dept_code
    return None


def coerce_user_role(value: object) -> UserRole | None:
    """Safely coerce a string or UserRole to UserRole. Returns None for unrecognized values.

    Use instead of inline ``try: UserRole(x) except ValueError`` blocks.
    """
    if isinstance(value, UserRole):
        return value
    if isinstance(value, str):
        try:
            return UserRole(value)
        except ValueError:
            return None
    return None


# ── FastAPI dependency guards ─────────────────────────────────────────────────
# These are defined as functions that accept `current_user` via Depends.
# Import get_current_user lazily to avoid circular imports.

def _get_cu():
    from auth_utils import get_current_user
    return get_current_user


def require_admin(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError("Use Depends(permissions.require_admin) after module load")


def require_staff_or_admin(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


def require_view_all(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


def require_write(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


def require_read_only(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


def require_can_edit(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


def require_dept_or_admin(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


def require_print_shop(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


def require_base_admin(current_user: models.User = Depends(lambda: None)) -> models.User:
    raise NotImplementedError


# ── Rebuild dependencies properly after auth_utils is available ───────────────
# Called once from main.py lifespan after all modules are imported.

def build_dependencies():
    """Wire FastAPI dependency functions. Call once at app startup."""
    global require_admin, require_staff_or_admin, require_view_all, require_write, \
        require_read_only, require_can_edit, require_dept_or_admin, require_print_shop, \
        require_base_admin
    from auth_utils import get_current_user

    def _require_admin(cu: models.User = Depends(get_current_user)) -> models.User:
        if cu.role != UserRole.admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ต้องการสิทธิ์ admin")
        return cu

    def _require_staff_or_admin(cu: models.User = Depends(get_current_user)) -> models.User:
        if cu.role not in (UserRole.admin, UserRole.staff):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ต้องการสิทธิ์ staff หรือ admin")
        return cu

    def _require_view_all(cu: models.User = Depends(get_current_user)) -> models.User:
        if cu.role not in VIEW_ALL_ROLES:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ต้องการสิทธิ์ระดับ admin หรือผู้มีอำนาจ")
        return cu

    def _require_write(cu: models.User = Depends(get_current_user)) -> models.User:
        if cu.role in (UserRole.esq_head, UserRole.secretary):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
        if cu.role not in WRITE_ROLES:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์แก้ไข")
        return cu

    def _require_read_only(cu: models.User = Depends(get_current_user)) -> models.User:
        if get_effective_role(cu) in (UserRole.esq_head, UserRole.secretary):
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว — ไม่สามารถแก้ไขได้")
        return cu

    def _require_can_edit(cu: models.User = Depends(get_current_user)) -> models.User:
        eff = get_effective_role(cu)
        if eff in (UserRole.esq_head, UserRole.secretary):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
        if eff not in (UserRole.admin, UserRole.teacher, UserRole.dept_supervisor):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์แก้ไข")
        return cu

    def _require_dept_or_admin(cu: models.User = Depends(get_current_user)) -> models.User:
        if get_effective_role(cu) not in (
            UserRole.admin, UserRole.dept_supervisor,
            UserRole.esq_head, UserRole.secretary,
        ):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ต้องการสิทธิ์ระดับแผนกหรือสูงกว่า")
        return cu

    def _require_print_shop(cu: models.User = Depends(get_current_user)) -> models.User:
        if get_effective_role(cu) != UserRole.print_shop:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Print shop role required")
        return cu

    def _require_base_admin(cu: models.User = Depends(get_current_user)) -> models.User:
        if cu.role != UserRole.admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ต้องการสิทธิ์ admin")
        return cu

    require_admin = _require_admin
    require_staff_or_admin = _require_staff_or_admin
    require_view_all = _require_view_all
    require_write = _require_write
    require_read_only = _require_read_only
    require_can_edit = _require_can_edit
    require_dept_or_admin = _require_dept_or_admin
    require_print_shop = _require_print_shop
    require_base_admin = _require_base_admin


# ── Object-level authorization helpers ───────────────────────────────────────

def assert_submission_access(
    db: Session,
    submission_id: int,
    user: models.User,
    write: bool = False,
) -> models.ExamSubmission:
    """
    Enforce object-level access for ExamSubmission.
    Raises 403/404. Returns submission on success.
    """
    from sqlalchemy.orm import joinedload

    sub = (
        db.query(models.ExamSubmission)
        .options(joinedload(models.ExamSubmission.section))
        .filter(models.ExamSubmission.id == submission_id)
        .first()
    )
    if not sub:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบ submission")

    eff = get_effective_role(user)

    if user.role in VIEW_ALL_ROLES:
        if write and user.role != UserRole.admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "บัญชีนี้มีสิทธิ์อ่านอย่างเดียว")
        return sub

    if user.role == UserRole.dept_supervisor:
        # dept_supervisor can read all submissions (dept filter applied at list level)
        if write:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "dept_supervisor ไม่สามารถแก้ไข submission ได้")
        return sub

    if eff == UserRole.teacher:
        section = sub.section
        if not section or section.teacher_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "ไม่มีสิทธิ์เข้าถึง submission นี้")
        return sub

    raise HTTPException(status.HTTP_403_FORBIDDEN, "role นี้ไม่มีสิทธิ์เข้าถึง submissions")


def assert_schedule_supervisor(
    db: Session,
    schedule_id: int,
    user: models.User,
) -> models.ExamSchedule:
    """Verify user is an assigned supervisor or teacher for this schedule."""
    is_supervisor = (
        db.query(models.Supervision)
        .filter(
            models.Supervision.schedule_id == schedule_id,
            models.Supervision.user_id == user.id,
        )
        .first()
    )
    is_teacher = (
        db.query(models.ExamSchedule)
        .join(models.Section)
        .filter(
            models.ExamSchedule.id == schedule_id,
            models.Section.teacher_id == user.id,
        )
        .first()
    )
    if not is_supervisor and not is_teacher:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "คุณไม่ได้รับมอบหมายให้ดูแลการสอบนี้")

    schedule = (
        db.query(models.ExamSchedule)
        .filter(models.ExamSchedule.id == schedule_id)
        .first()
    )
    if not schedule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบตารางสอบ")
    return schedule
