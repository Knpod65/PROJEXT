"""schedule_validator.py — pure validation helpers for schedule params.

Existing Pydantic models (ScheduleFilterRequest) are retained above.
Pure functions below are side-effect-free and testable without DB.
"""


def normalize_date_params(date: str | None, exam_date: str | None) -> str | None:
    """Return the effective date: exam_date takes priority, date is the fallback."""
    return exam_date if exam_date else date


def validate_pagination_clamp(page: int, limit: int) -> tuple[int, int]:
    """Clamp page ≥ 1 and limit 1–500."""
    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    if limit > 500:
        limit = 500
    return page, limit


def validate_status(status: str | None) -> str | None:
    """Return validated status string or None."""
    if status is None:
        return None
    allowed = {"draft", "published", "locked", "archived"}
    if status.lower() not in allowed:
        raise ValueError(f"status ไม่ถูกต้อง: {status}")
    return status.lower()


def validate_exam_type_coerce(raw) -> str:
    """Coerce exam_type enum or string to a plain string value."""
    if hasattr(raw, "value"):
        return raw.value
    return str(raw)
