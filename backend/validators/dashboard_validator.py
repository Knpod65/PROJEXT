"""
dashboard_validator.py — validation for dashboard operations.

Owns:
- semester validation
- academic year validation
- query parameter normalization
"""
from typing import Optional
from fastapi import HTTPException


class DashboardValidator:
    """Validation for dashboard operations."""

    @staticmethod
    def validate_semester(semester: Optional[str]) -> str:
        if semester is None:
            return "2"
        s = semester.strip()
        if s not in ("1", "2"):
            raise HTTPException(400, "semester ต้องเป็น '1' หรือ '2'")
        return s

    @staticmethod
    def validate_academic_year(year: Optional[str]) -> str:
        if year is None:
            return "2568"
        y = year.strip()
        if not y.isdigit() or len(y) != 4:
            raise HTTPException(400, "academic_year ต้องเป็นตัวเลข 4 หลัก")
        return y
