from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from term_lifecycle import find_period, get_active_period


def resolve_export_period(
    db: Session,
    semester: str | None,
    academic_year: str | None,
    exam_type: str | None = "final",
) -> models.ExamPeriod:
    if semester and academic_year:
        period = find_period(db, academic_year, semester, exam_type)
        if period:
            return period
    period = get_active_period(db)
    if not period:
        raise HTTPException(400, "ไม่มี active period")
    return period
