"""Workflow user helpers extracted from optimize_workflow router.

Pure-computation functions — no FastAPI dependencies, no side effects.
"""
from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

import models


def format_user_dict(u: models.User) -> dict:
    """Serialize a User ORM object to the standard workflow user dict."""
    return {
        "id":          u.id,
        "username":    u.username,
        "email":       u.email,
        "role":        u.role.value if u.role else None,
        "full_name":   u.full_name,
        "title":       u.title,
        "division":    u.division,
        "unit":        u.unit,
        "dept_code":   u.dept_code,
        "mobile":      u.mobile,
        "ext":         u.ext,
        "employee_id": u.employee_id,
        "is_active":   u.is_active,
    }


def build_external_workflow_issues(
    db: Session,
    period_id: int | None,
) -> list[dict[str, object]]:
    """Query ExternalExam rows for a period and return staffing issue dicts.

    Returns an empty list when period_id is falsy.
    Each dict describes one invigilator staffing gap (none assigned or shortage).
    """
    if not period_id:
        return []

    exams = (
        db.query(models.ExternalExam)
        .options(joinedload(models.ExternalExam.supervisions))
        .filter(models.ExternalExam.exam_period_id == period_id)
        .order_by(
            models.ExternalExam.exam_date,
            models.ExternalExam.exam_time,
            models.ExternalExam.id,
        )
        .all()
    )

    issues: list[dict[str, object]] = []
    for exam in exams:
        assigned = len(exam.supervisions or [])
        needed = exam.invigilators_needed or 0
        reference = exam.title or f"External exam #{exam.id}"

        if needed > 0 and assigned == 0:
            issues.append(
                {
                    "id": f"external-none-{exam.id}",
                    "type": "no_invigilator_assigned",
                    "severity": "error",
                    "scope": "external",
                    "title": "No invigilator assigned",
                    "message": (
                        f"{reference} has no assigned staff for "
                        f"{exam.exam_date or '-'} {exam.exam_time or ''}."
                    ),
                    "reference": reference,
                }
            )
            continue

        if assigned < needed:
            issues.append(
                {
                    "id": f"external-short-{exam.id}",
                    "type": "external_staff_shortage",
                    "severity": "warning",
                    "scope": "external",
                    "title": "External exam staff shortage",
                    "message": (
                        f"{reference} needs {needed} staff but only {assigned} are assigned."
                    ),
                    "reference": reference,
                }
            )

    return issues
