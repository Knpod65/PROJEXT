"""
analytics_validator.py — validation for analytics operations.

Owns:
- metric code validation
- session ID validation
- query parameter normalization
"""
from typing import Optional
from fastapi import HTTPException


class AnalyticsValidator:
    """Validation for analytics operations."""

    VALID_METRIC_PREFIXES = ("workload", "room", "governance", "submission", "swap", "checkin")

    @staticmethod
    def validate_metric_code(metric_code: str) -> str:
        if not metric_code or not isinstance(metric_code, str):
            raise HTTPException(400, "metric_code ต้องเป็น string ที่ไม่ว่าง")
        if len(metric_code) > 128:
            raise HTTPException(400, "metric_code ยาวเกินไป")
        return metric_code.strip().lower()

    @staticmethod
    def validate_session_id(session_id: int) -> int:
        if not isinstance(session_id, int) or session_id <= 0:
            raise HTTPException(400, "session_id ต้องเป็น integer บวก")
        return session_id

    @staticmethod
    def normalize_semester(semester: Optional[str]) -> Optional[str]:
        if semester is None:
            return None
        s = semester.strip()
        if s not in ("1", "2"):
            raise HTTPException(400, "semester ต้องเป็น '1' หรือ '2'")
        return s

    @staticmethod
    def normalize_academic_year(year: Optional[str]) -> Optional[str]:
        if year is None:
            return None
        y = year.strip()
        if not y.isdigit() or len(y) != 4:
            raise HTTPException(400, "academic_year ต้องเป็นตัวเลข 4 หลัก")
        return y
