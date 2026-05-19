"""Faculty policy registry — named policy key constants + settings-derived defaults.

Provides stable string constants so callers don't hardcode policy key strings,
and a loader that seeds the global registry from the settings singleton.
"""
from __future__ import annotations

from typing import Any

from services.policy_registry_service import (
    _SENTINEL,
    clear_all_policies,
    get_policy_value,
    set_global_policy,
)

# ── Standard policy key constants ─────────────────────────────────────────────

POLICY_PAPER_DISTRIBUTION_DIVISION  = "paper_distribution_division"
POLICY_PAPER_EXCLUDED_USERNAMES     = "paper_distribution_excluded_usernames"
POLICY_PAPER_EXCLUDED_SNIPPETS      = "paper_distribution_excluded_snippets"
POLICY_SIGN_ORDER_USERNAMES         = "sign_order_usernames"
POLICY_APPROVAL_QUORUM              = "approval_quorum"
POLICY_MAX_SUPERVISION_SESSIONS     = "max_supervision_sessions"
POLICY_ROOM_DEFAULT_CAPACITY        = "room_default_capacity"
POLICY_ACADEMIC_YEAR_DEFAULT        = "academic_year_default"
POLICY_SEMESTER_DEFAULT             = "semester_default"
POLICY_FACULTY_NAME_TH              = "faculty_name_th"
POLICY_FACULTY_NAME_EN              = "faculty_name_en"
POLICY_EMAIL_DOMAIN                 = "email_domain"


def load_defaults_from_settings() -> None:
    """Seed the global policy registry from the settings singleton.

    Idempotent — safe to call multiple times (subsequent calls overwrite with same values).
    """
    from config.settings import settings

    set_global_policy(POLICY_SIGN_ORDER_USERNAMES, settings.sign_order_usernames)
    set_global_policy(POLICY_PAPER_DISTRIBUTION_DIVISION, settings.paper_distribution_division)
    set_global_policy(
        POLICY_PAPER_EXCLUDED_USERNAMES,
        settings.paper_distribution_excluded_usernames,
    )
    set_global_policy(
        POLICY_PAPER_EXCLUDED_SNIPPETS,
        settings.paper_distribution_excluded_name_snippets,
    )
    set_global_policy(POLICY_ACADEMIC_YEAR_DEFAULT, "2568")
    set_global_policy(POLICY_SEMESTER_DEFAULT, "2")
    set_global_policy(POLICY_ROOM_DEFAULT_CAPACITY, 30)


def get_policy(
    key: str,
    *,
    faculty_id: int | None = None,
    period_id: int | None = None,
    fallback: Any = _SENTINEL,
) -> Any:
    """Thin convenience wrapper over policy_registry_service.get_policy_value."""
    return get_policy_value(
        key,
        faculty_id=faculty_id,
        period_id=period_id,
        fallback=fallback,
    )
