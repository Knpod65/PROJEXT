"""Faculty scope policy — Phase 3 skeleton.

When multi_faculty_enabled is False (current default), all scope checks
pass unconditionally so existing single-faculty behaviour is unchanged.

When multi_faculty_enabled is True, scope functions enforce that a user
can only access resources belonging to their own faculty_id.

NOTE (Phase 3 skeleton): models.User does not yet have a faculty_id column.
get_actor_faculty_id() returns None until the DB migration adds the column.
With None faculty_id, all scope checks fall back to pass-through.

After the migration:
  1. Set multi_faculty_enabled=true in production settings.
  2. Uncomment the filter line in apply_faculty_scope_to_query().
  3. Populate faculty_id on all existing users.
"""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import models


def _multi_faculty_enabled() -> bool:
    from config.settings import settings
    return getattr(settings, "multi_faculty_enabled", False)


def get_actor_faculty_id(user: "models.User") -> int | None:
    """Return faculty_id from user record.

    Phase 3 skeleton: models.User does not yet have a faculty_id column.
    Returns None until the DB migration adds the column.
    """
    return getattr(user, "faculty_id", None)


def is_same_faculty(
    user: "models.User",
    target_faculty_id: int | None,
) -> bool:
    """Return True if user belongs to the same faculty as the target resource.

    With multi_faculty_enabled=false: always returns True (single-faculty mode).
    With actor_faculty_id or target_faculty_id = None: returns True (insufficient
    data — defers to role-based access control).
    """
    if not _multi_faculty_enabled():
        return True
    actor_faculty = get_actor_faculty_id(user)
    if actor_faculty is None or target_faculty_id is None:
        return True
    return actor_faculty == target_faculty_id


def assert_faculty_scope_safe(
    user: "models.User",
    resource_faculty_id: int | None,
    *,
    resource_name: str = "resource",
) -> None:
    """Raise EMSPermissionError if user is accessing a resource from another faculty.

    No-op when multi_faculty_enabled=false.
    """
    if not is_same_faculty(user, resource_faculty_id):
        from services.exceptions import EMSPermissionError
        raise EMSPermissionError(
            f"Faculty boundary violation: {resource_name} belongs to a different faculty."
        )


def apply_faculty_scope_to_query(
    query: Any,
    user: "models.User",
    model_class: Any,
) -> Any:
    """Apply a faculty_id filter to a SQLAlchemy query.

    Phase 3 skeleton: returns query unmodified until:
      1. faculty_id column is added to model_class via migration.
      2. multi_faculty_enabled is set to True.

    After migration, uncomment the filter line below.
    """
    if not _multi_faculty_enabled():
        return query
    actor_faculty = get_actor_faculty_id(user)
    if actor_faculty is None:
        return query
    # TODO (Phase 3 migration): uncomment after adding faculty_id to all scoped models
    # return query.filter(model_class.faculty_id == actor_faculty)
    return query


def get_faculty_scope_context(user: "models.User") -> dict[str, Any]:
    """Return a dict describing the user's faculty scope context for audit logs."""
    return {
        "multi_faculty_enabled": _multi_faculty_enabled(),
        "actor_faculty_id": get_actor_faculty_id(user),
        "scope_enforced": _multi_faculty_enabled() and get_actor_faculty_id(user) is not None,
    }
