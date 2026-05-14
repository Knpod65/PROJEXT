"""Workflow reporting helpers extracted from optimize_workflow router.

Thin orchestration layer — delegates to staff_workloads and adds period/role context.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

import models
from staff_workloads import get_period_workload_snapshot


def build_staff_workload_report(
    db: Session,
    period: models.ExamPeriod,
    viewer_role: str | None,
) -> dict[str, Any]:
    """Return the staff workload snapshot enriched with period metadata and viewer role.

    Args:
        db:          Active database session.
        period:      The ExamPeriod to report on.
        viewer_role: Role string of the requesting user (for frontend gating).

    Returns:
        Dict from get_period_workload_snapshot() with "period" and "viewer_role" keys added.
    """
    snapshot = get_period_workload_snapshot(db, period)
    snapshot["period"] = {
        "id":            period.id,
        "semester":      period.semester,
        "academic_year": period.academic_year,
        "exam_type":     period.exam_type,
        "label":         period.label,
    }
    snapshot["viewer_role"] = viewer_role
    return snapshot
