"""Faculty role mapping service — configurable permission overlay on permissions.py.

permissions.py is NOT modified — it remains the authoritative default.
This service reads VIEW_ALL_ROLES, SIGNER_ROLES, SUPERVISION_ROLES, WRITE_ROLES
from permissions.py to build default mappings, then allows per-faculty overrides.

Registry key: (faculty_id, role) — faculty_id=None means global override.
"""
from __future__ import annotations

import threading
from typing import Any

from config_models.faculty_role_mapping import FacultyRoleMapping, make_faculty_role_mapping

_lock = threading.Lock()
_registry: dict[tuple[int | None, str], FacultyRoleMapping] = {}

_VALID_PERMISSIONS = frozenset({
    "view_all", "sign", "supervise", "write_sections", "manage_print", "manage_config",
})


def build_default_mappings_from_permissions() -> list[FacultyRoleMapping]:
    """Derive FacultyRoleMapping list from the existing permissions.py sets.

    Returns a list with faculty_id=None for all entries (global defaults).
    """
    from permissions import (
        VIEW_ALL_ROLES,
        WRITE_ROLES,
        SIGNER_ROLES,
        SUPERVISION_ROLES,
    )

    all_roles: set[str] = set()
    for role_set in (VIEW_ALL_ROLES, WRITE_ROLES, SIGNER_ROLES, SUPERVISION_ROLES):
        for role in role_set:
            all_roles.add(str(role.value) if hasattr(role, "value") else str(role))

    def _role_str(r: Any) -> str:
        return str(r.value) if hasattr(r, "value") else str(r)

    view_all_strs = {_role_str(r) for r in VIEW_ALL_ROLES}
    write_strs = {_role_str(r) for r in WRITE_ROLES}
    signer_strs = {_role_str(r) for r in SIGNER_ROLES}
    supervision_strs = {_role_str(r) for r in SUPERVISION_ROLES}

    mappings = []
    for role in all_roles:
        mappings.append(make_faculty_role_mapping(
            role=role,
            faculty_id=None,
            can_view_all=role in view_all_strs,
            can_sign=role in signer_strs,
            can_supervise=role in supervision_strs,
            can_write_sections=role in write_strs,
            can_manage_print=role in ("admin", "print_shop"),
            can_manage_config=role == "admin",
        ))
    return mappings


def register_role_mapping(mapping: FacultyRoleMapping) -> None:
    """Store a role mapping, replacing any existing mapping for (faculty_id, role)."""
    with _lock:
        _registry[(mapping.faculty_id, mapping.role)] = mapping


def get_effective_mapping(
    role: str,
    faculty_id: int | None = None,
) -> FacultyRoleMapping:
    """Return the mapping for (role, faculty_id).

    Resolution: faculty-specific → global override → permissions.py-derived default.
    """
    with _lock:
        if faculty_id is not None and (faculty_id, role) in _registry:
            return _registry[(faculty_id, role)]
        if (None, role) in _registry:
            return _registry[(None, role)]

    # Build from permissions.py and cache
    defaults = build_default_mappings_from_permissions()
    with _lock:
        for m in defaults:
            _registry[(None, m.role)] = m
        if (None, role) in _registry:
            return _registry[(None, role)]

    # Unknown role — return all-False mapping
    return make_faculty_role_mapping(role=role, faculty_id=faculty_id)


def has_permission(
    role: str,
    permission: str,
    *,
    faculty_id: int | None = None,
) -> bool:
    """Return True if `role` has the given permission for the faculty.

    `permission` must be one of: view_all, sign, supervise, write_sections,
    manage_print, manage_config.
    """
    mapping = get_effective_mapping(role, faculty_id)
    return bool(getattr(mapping, f"can_{permission}", False))


def get_all_permitted_roles(
    permission: str,
    faculty_id: int | None = None,
) -> list[str]:
    """Return list of role strings that have the given permission set to True."""
    from permissions import VIEW_ALL_ROLES, WRITE_ROLES, SIGNER_ROLES, SUPERVISION_ROLES

    def _role_str(r: Any) -> str:
        return str(r.value) if hasattr(r, "value") else str(r)

    all_roles: set[str] = {"admin"}
    for role_set in (VIEW_ALL_ROLES, WRITE_ROLES, SIGNER_ROLES, SUPERVISION_ROLES):
        for r in role_set:
            all_roles.add(_role_str(r))

    return sorted(r for r in all_roles if has_permission(r, permission, faculty_id=faculty_id))


def validate_role_mapping(mapping: FacultyRoleMapping) -> list[str]:
    """Return validation error list (empty = valid)."""
    errors: list[str] = []
    if not mapping.role.strip():
        errors.append("role must not be empty")
    return errors


def clear_role_mappings() -> None:
    """Reset module state. Use in tests for isolation."""
    with _lock:
        _registry.clear()
