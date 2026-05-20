"""workload_duty_analytics_validator.py — validation for workload duty analytics."""
from __future__ import annotations

from fastapi import HTTPException


class WorkloadDutyAnalyticsValidator:
    """Validation for workload duty analytics operations."""

    VALID_ROLE_GROUPS = {"all", "admin", "staff", "supervisor", "teacher"}
    VALID_DUTY_TYPES = {"all", "invigilation", "paper_distribution", "combined"}

    @staticmethod
    def validate_semester(semester: str | None) -> str | None:
        if semester is None:
            return None
        text = semester.strip()
        if not text:
            return None
        if text not in {"1", "2", "summer"}:
            raise HTTPException(400, "semester ต้องเป็น 1, 2 หรือ summer")
        return text

    @staticmethod
    def validate_academic_year(year: str | None) -> str | None:
        if year is None:
            return None
        text = year.strip()
        if not text:
            return None
        if not text.isdigit() or len(text) != 4:
            raise HTTPException(400, "academic_year ต้องเป็นตัวเลข 4 หลัก")
        return text

    @staticmethod
    def validate_period_id(period_id: int | None) -> int | None:
        if period_id is None:
            return None
        if not isinstance(period_id, int) or period_id <= 0:
            raise HTTPException(400, "period_id ต้องเป็น integer บวก")
        return period_id

    @staticmethod
    def validate_exam_type(exam_type: str | None) -> str | None:
        if exam_type is None:
            return None
        text = exam_type.strip().lower()
        if not text:
            return None
        if len(text) > 32:
            raise HTTPException(400, "exam_type ยาวเกินไป")
        return text

    @staticmethod
    def validate_role_group(role_group: str | None) -> str:
        text = (role_group or "all").strip().lower()
        if text not in WorkloadDutyAnalyticsValidator.VALID_ROLE_GROUPS:
            raise HTTPException(400, "role_group ต้องเป็น all, admin, staff, supervisor หรือ teacher")
        return text

    @staticmethod
    def validate_person_id(person_id: str | None) -> str | None:
        if person_id is None:
            return None
        text = person_id.strip()
        if not text:
            return None
        if len(text) > 64:
            raise HTTPException(400, "person_id ยาวเกินไป")
        return text

    @staticmethod
    def validate_duty_type(duty_type: str | None) -> str:
        text = (duty_type or "all").strip().lower()
        if text not in WorkloadDutyAnalyticsValidator.VALID_DUTY_TYPES:
            raise HTTPException(400, "duty_type ต้องเป็น all, invigilation, paper_distribution หรือ combined")
        return text

    @staticmethod
    def validate_include_flag(value: bool | None, default: bool = True) -> bool:
        if value is None:
            return default
        return bool(value)

    @staticmethod
    def normalize_filters(
        semester: str | None = None,
        academic_year: str | None = None,
        period_id: int | None = None,
        exam_type: str | None = None,
        role_group: str | None = None,
        person_id: str | None = None,
        include_teachers: bool | None = True,
        include_staff: bool | None = True,
        duty_type: str | None = None,
    ) -> dict[str, object]:
        return {
            "semester": WorkloadDutyAnalyticsValidator.validate_semester(semester),
            "academic_year": WorkloadDutyAnalyticsValidator.validate_academic_year(academic_year),
            "period_id": WorkloadDutyAnalyticsValidator.validate_period_id(period_id),
            "exam_type": WorkloadDutyAnalyticsValidator.validate_exam_type(exam_type),
            "role_group": WorkloadDutyAnalyticsValidator.validate_role_group(role_group),
            "person_id": WorkloadDutyAnalyticsValidator.validate_person_id(person_id),
            "include_teachers": WorkloadDutyAnalyticsValidator.validate_include_flag(include_teachers, True),
            "include_staff": WorkloadDutyAnalyticsValidator.validate_include_flag(include_staff, True),
            "duty_type": WorkloadDutyAnalyticsValidator.validate_duty_type(duty_type),
        }
