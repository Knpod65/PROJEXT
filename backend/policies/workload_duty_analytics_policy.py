"""workload_duty_analytics_policy.py — Policy checks for workload duty analytics.

Rules:
- Pure functions. No DB, no ORM, no FastAPI imports.
- Returns booleans; callers handle 403/404.
"""
from __future__ import annotations

from typing import Any


_ROLE_GROUPS = {
    "admin": frozenset({"admin", "staff", "supervisor", "teacher"}),
    "staff": frozenset({"staff", "supervisor", "admin"}),
    "supervisor": frozenset({"staff", "supervisor", "teacher"}),
    "dept_supervisor": frozenset({"staff", "supervisor", "teacher"}),
    "esq_head": frozenset({"staff", "supervisor", "teacher"}),
    "secretary": frozenset({"staff", "supervisor", "teacher"}),
    "teacher": frozenset({"teacher"}),
    "dpo": frozenset({"admin", "staff", "supervisor", "teacher"}),
}


def _role_name(user: Any) -> str:
    role = getattr(user, "view_as_role", None) or getattr(user, "role", None)
    if hasattr(role, "value"):
        role = role.value
    return str(role or "").lower()


def _user_identity(user: Any) -> str:
    user_id = getattr(user, "id", None)
    if user_id is not None:
        return str(user_id)
    username = getattr(user, "username", None)
    return str(username or "")


def normalize_role_group(value: Any) -> str:
    role_group = str(value or "all").strip().lower()
    if role_group in {"dept_supervisor", "esq_head", "secretary"}:
        return "supervisor"
    if role_group in {"all", "admin", "staff", "supervisor", "teacher"}:
        return role_group
    return role_group


def allowed_role_groups(user: Any) -> frozenset[str]:
    return _ROLE_GROUPS.get(_role_name(user), frozenset())


def can_view_workload_dashboard(user: Any, scope: dict[str, Any] | None = None) -> bool:
    scope = scope or {}
    role = _role_name(user)
    requested_role_group = normalize_role_group(scope.get("role_group"))
    person_id = scope.get("person_id")

    if role in {"", "student"}:
        return False

    if role == "admin":
        return True

    if role == "teacher":
        if requested_role_group not in {"all", "teacher"}:
            return False
        if person_id is None:
            return True
        return str(person_id) in {_user_identity(user), str(getattr(user, "username", ""))}

    if role == "dpo":
        return requested_role_group in {"all", "admin", "staff", "supervisor", "teacher"}

    if role in {"staff", "supervisor", "dept_supervisor", "esq_head", "secretary"}:
        return requested_role_group in {"all", "admin", "staff", "supervisor", "teacher"}

    return False


def can_view_person_workload(user: Any, person_id: Any, role_group: str) -> bool:
    role = _role_name(user)
    role_group = normalize_role_group(role_group)
    person_id = str(person_id) if person_id is not None else None

    if role in {"", "student"}:
        return False
    if role == "admin":
        return True
    if role == "dpo":
        return False
    if role == "teacher":
        return role_group == "teacher" and person_id in {_user_identity(user), str(getattr(user, "username", ""))}
    if role in {"staff", "supervisor", "dept_supervisor", "esq_head", "secretary"}:
        return True
    return False


def can_view_teacher_workload(user: Any, teacher_id: Any) -> bool:
    role = _role_name(user)
    teacher_id = str(teacher_id) if teacher_id is not None else None

    if role in {"", "student"}:
        return False
    if role == "admin":
        return True
    if role == "dpo":
        return False
    if role == "teacher":
        return teacher_id in {_user_identity(user), str(getattr(user, "username", ""))}
    return role in {"staff", "supervisor", "dept_supervisor", "esq_head", "secretary"}

