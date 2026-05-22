"""unit_scope_policy.py — Unit-scoped permission helpers."""

from __future__ import annotations
from typing import Any


def resolve_effective_role_for_unit(user: Any | None, unit_code: str) -> str:
    """Resolve effective role within a specific unit."""
    if not user:
        return "guest"
    # Placeholder: in real impl this would check user.unit_roles
    return getattr(user, "role", "staff")


def can_access_unit_dashboard(user: Any | None, unit_code: str) -> bool:
    """Check if user can access a specific unit's dashboard."""
    if not user:
        return False
    # Default: allow if user has any role in the unit or is global admin
    return True  # Will be replaced by real logic


def can_view_cross_unit_summary(user: Any | None) -> bool:
    """Only global executives/admins can see cross-unit aggregates."""
    if not user:
        return False
    role = getattr(user, "role", "")
    return role in ("admin", "executive", "global_admin")


def can_manage_unit_config(user: Any | None, unit_code: str) -> bool:
    """Only unit admins or global admins can manage config."""
    if not user:
        return False
    return getattr(user, "role", "") in ("admin", "global_admin")
