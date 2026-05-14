"""Faculty scope service — Phase 3 skeleton.

All public functions return safely when multi_faculty_enabled is False.
No DB schema changes in this phase.

After the multi_faculty migration:
  - get_active_period_for_faculty() will filter by faculty_id
  - get_rooms_for_faculty() will filter by faculty_id
  - get_staff_for_faculty() will filter by division/faculty mapping
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    import models
    from sqlalchemy.orm import Session


def get_active_period_for_faculty(
    db: "Session",
    faculty_id: int | None,
) -> Any:
    """Return the active exam period for the given faculty.

    Phase 3 skeleton: falls back to global active period (current behaviour).
    After migration: filter Period by faculty_id before returning.
    """
    import models as m
    return (
        db.query(m.Period)
        .filter(m.Period.lifecycle_status == "active")
        .first()
    )


def get_rooms_for_faculty(
    db: "Session",
    faculty_id: int | None,
) -> List[Any]:
    """Return the room pool available to the given faculty.

    Phase 3 skeleton: returns all active rooms (current behaviour).
    After migration: filter Room by faculty_id or building assignment.
    """
    import models as m
    return db.query(m.Room).filter(m.Room.is_active.is_(True)).all()


def get_staff_for_faculty(
    db: "Session",
    faculty_id: int | None,
    *,
    roles: tuple[str, ...] = ("staff", "esq_head", "dept_supervisor"),
) -> List[Any]:
    """Return users eligible as invigilators for the given faculty.

    Phase 3 skeleton: returns all active users with staff-tier roles.
    After migration: scope by faculty_id or division mapping.
    """
    import models as m
    return (
        db.query(m.User)
        .filter(m.User.is_active.is_(True), m.User.role.in_(roles))
        .all()
    )


def get_faculty_audit_boundary(faculty_id: int | None) -> dict[str, Any]:
    """Return the audit boundary descriptor for a faculty.

    Describes which audit log actions are scoped to this faculty.
    Phase 3 skeleton: returns global boundary (no faculty filter yet).
    """
    return {
        "faculty_id": faculty_id,
        "schedule_scoped": False,
        "export_scoped": False,
        "import_scoped": False,
        "audit_scoped": False,
        "note": "Phase 3 skeleton — all boundaries are global until migration",
    }
