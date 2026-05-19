"""
export_serializer.py — serialization for export operations.

Owns:
- schedule audit payload
- export metadata shaping
- filename generation response
"""
from typing import Optional
from datetime import datetime, timezone


def serialize_export_metadata(
    filename: str,
    row_count: int,
    scope: str,
    params: dict,
) -> dict:
    """Serialize export metadata."""
    return {
        "filename": filename,
        "row_count": row_count,
        "scope": scope,
        "params": params,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def serialize_schedule_summary(schedules: list, user_lookup: dict) -> dict:
    """Serialize schedule summary for audit."""
    return {
        "schedule_count": len(schedules),
        "unique_dates": len(set(s.exam_date for s in schedules if s.exam_date)),
        "unique_rooms": len(set(s.room.room_name for s in schedules if s.room and s.room.room_name)),
        "generated_by": user_lookup.get("user_id", "unknown"),
    }


def serialize_error_response(error_code: str, message: str, details: Optional[str] = None) -> dict:
    """Serialize error response."""
    return {
        "error": error_code,
        "message": message,
        "details": details,
    }