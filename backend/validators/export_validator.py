"""
export_validator.py — validation for export operations.

Owns:
- exam_type validation
- semester validation
- period resolution validation
- export scope validation
"""
from typing import Optional
from fastapi import HTTPException


class ExportValidator:
    """Validation for export operations."""

    @staticmethod
    def validate_exam_type(exam_type: str) -> str:
        """Validate exam_type is valid."""
        if exam_type not in ("midterm", "final"):
            raise HTTPException(400, "exam_type ต้องเป็น 'midterm' หรือ 'final'")
        return exam_type

    @staticmethod
    def validate_semester(semester: str) -> str:
        """Validate semester is valid."""
        if semester not in ("1", "2"):
            raise HTTPException(400, "semester ต้องเป็น '1' หรือ '2'")
        return semester

    @staticmethod
    def validate_export_scope(scope: Optional[str] = None) -> str:
        """Validate export scope is allowed."""
        valid_scopes = ("schedule", "workload", "paper_distribution", "submissions", "compensation")
        if scope and scope not in valid_scopes:
            raise HTTPException(400, f"export_scope ต้องเป็นหนึ่งใน: {valid_scopes}")
        return scope or "schedule"

    @staticmethod
    def validate_period_params(semester: Optional[str], academic_year: Optional[str]) -> tuple:
        """Validate or resolve period parameters."""
        if not semester or not academic_year:
            from config.periods import resolve_export_period
            from database import get_db
            db = next(get_db())
            period = resolve_export_period(db, semester, academic_year, "final")
            return period.semester, period.academic_year
        return semester, academic_year