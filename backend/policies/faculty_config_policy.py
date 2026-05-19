"""Faculty config policy — access control for faculty configuration operations."""
from __future__ import annotations


def can_create_faculty_config(user_role: str) -> bool:
    return user_role == "admin"


def can_update_faculty_config(user_role: str) -> bool:
    return user_role == "admin"


def can_delete_faculty_config(user_role: str) -> bool:
    return user_role == "admin"


def can_read_faculty_config(user_role: str) -> bool:
    return bool(user_role)


def assert_faculty_config_write_allowed(user_role: str) -> None:
    """Raise EMSPermissionError if role is not admin."""
    if not can_create_faculty_config(user_role):
        from services.exceptions import EMSPermissionError
        raise EMSPermissionError(
            f"Role '{user_role}' is not permitted to modify faculty configuration."
        )
