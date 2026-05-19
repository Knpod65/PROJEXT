"""Workload policy service — configurable staff eligibility and exclusion rules.

Wraps the logic currently hardcoded in:
- config/settings.py paper_distribution_* values
- auth_utils.is_eligible_supervisor() Faculty_Secretary exclusion
- auth_utils.is_room_keeper() / is_esq_staff() special role checks

Existing auth_utils.py is NOT modified. This service provides the configurable
equivalent for new callers. The per-faculty resolution falls back to
settings-derived global defaults.
"""
from __future__ import annotations

import threading

from config_models.workload_policy import WorkloadPolicy, make_workload_policy

_lock = threading.Lock()
_registry: dict[int | None, WorkloadPolicy] = {}

_DEFAULT_EXCLUDED_SPECIAL_ROLES = frozenset({"room_keeper", "esq_staff"})
_DEFAULT_EXCLUDED_DIVISIONS = frozenset({"Faculty_Secretary"})


def build_default_policy_from_settings() -> WorkloadPolicy:
    """Construct WorkloadPolicy from settings singleton (global default)."""
    from config.settings import settings

    return make_workload_policy(
        faculty_id=None,
        paper_distribution_division=settings.paper_distribution_division,
        excluded_usernames=settings.paper_distribution_excluded_usernames,
        excluded_name_snippets=settings.paper_distribution_excluded_name_snippets,
        excluded_special_roles=_DEFAULT_EXCLUDED_SPECIAL_ROLES,
        excluded_divisions=_DEFAULT_EXCLUDED_DIVISIONS,
    )


def register_workload_policy(policy: WorkloadPolicy) -> None:
    with _lock:
        _registry[policy.faculty_id] = policy


def get_effective_policy(faculty_id: int | None = None) -> WorkloadPolicy:
    """Return faculty-specific policy, falling back to global, then settings."""
    with _lock:
        if faculty_id is not None and faculty_id in _registry:
            return _registry[faculty_id]
        if None in _registry:
            return _registry[None]

    default = build_default_policy_from_settings()
    with _lock:
        _registry[None] = default
    return default


def is_eligible_for_paper_distribution(
    username: str,
    full_name: str,
    division: str,
    special_role: str | None,
    *,
    faculty_id: int | None = None,
) -> bool:
    """Return True if the user should receive paper distribution assignments.

    Configurable replacement for the hardcoded exclusion logic in optimize_workflow.py.
    Returns False if any exclusion criterion matches.
    """
    policy = get_effective_policy(faculty_id)

    if username in policy.excluded_usernames:
        return False
    for snippet in policy.excluded_name_snippets:
        if snippet and snippet in full_name:
            return False
    if division == policy.paper_distribution_division:
        return False
    if special_role and special_role in policy.excluded_special_roles:
        return False
    return True


def is_excluded_supervisor(
    username: str,
    division: str,
    special_role: str | None,
    *,
    faculty_id: int | None = None,
) -> bool:
    """Return True if the user is excluded from supervision assignments.

    Configurable wrapper for the logic in auth_utils.is_eligible_supervisor().
    Returns True if division is in excluded_divisions or special_role is room_keeper.
    """
    policy = get_effective_policy(faculty_id)

    if division in policy.excluded_divisions:
        return True
    if special_role and special_role in policy.excluded_special_roles:
        return True
    return False


def get_supervision_slot_limit(faculty_id: int | None = None) -> int:
    """Return max_supervision_sessions for the faculty (0 = unlimited)."""
    return get_effective_policy(faculty_id).max_supervision_sessions


def validate_workload_policy(policy: WorkloadPolicy) -> list[str]:
    """Return validation error list (empty = valid)."""
    errors: list[str] = []
    if policy.max_supervision_sessions < 0:
        errors.append("max_supervision_sessions must be >= 0")
    return errors


def clear_workload_policies() -> None:
    """Reset module state. Use in tests for isolation."""
    with _lock:
        _registry.clear()
