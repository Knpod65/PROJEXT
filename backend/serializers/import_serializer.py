"""
import_serializer.py — serialization for import operations.

Owns:
- session audit payload
- import result shaping
- row log shaping
- summary shaping
"""
from typing import Optional
from datetime import datetime, timezone
import pandas as pd
from collections import defaultdict


def _detect_import_type(session) -> str:
    """Detect import type from session counts."""
    if (session.opencourse_rows or 0) > 0 and (session.enrollment_rows or 0) > 0:
        return "mixed"
    if (session.opencourse_rows or 0) > 0:
        return "opencourse"
    if (session.enrollment_rows or 0) > 0:
        return "enrollment"
    return "personnel_or_employee"


def _status_from_counts(total_rows: int, imported_rows: int, skipped_rows: int, error_rows: int) -> str:
    """Determine status from counts."""
    if total_rows == 0:
        return "no_logs"
    if imported_rows == 0 and error_rows > 0:
        return "blocked"
    if skipped_rows > 0:
        return "completed_with_skips"
    return "completed"


def serialize_session_audit(session, user_lookup: dict, counts: dict) -> dict:
    """Serialize import session audit payload."""
    total_rows = counts.get("total_rows", 0)
    valid_rows = counts.get("valid_rows", 0)
    warning_rows = counts.get("warning_rows", 0)
    error_rows = counts.get("error_rows", 0)
    imported_rows = counts.get("imported_rows", 0)
    skipped_rows = counts.get("skipped_rows", 0)

    return {
        "import_session_id": session.id,
        "id": session.id,
        "import_type": _detect_import_type(session),
        "academic_year": session.academic_year,
        "semester": session.semester,
        "exam_type": session.exam_type,
        "imported_by": user_lookup.get(session.created_by, "unknown"),
        "started_at": session.created_at.isoformat() if session.created_at else None,
        "completed_at": session.last_updated.isoformat() if session.last_updated else None,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "last_updated": session.last_updated.isoformat() if session.last_updated else None,
        "opencourse_rows": session.opencourse_rows,
        "enrollment_rows": session.enrollment_rows,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "warning_rows": warning_rows,
        "error_rows": error_rows,
        "imported_rows": imported_rows,
        "skipped_rows": skipped_rows,
        "status": _status_from_counts(total_rows, imported_rows, skipped_rows, error_rows),
    }


def serialize_import_result(session_id: int, academic_year: str, semester: str,
                            exam_type: str, file_rows: int, stats: dict) -> dict:
    """Serialize import operation result."""
    return {
        "status": "ok",
        "session_id": session_id,
        "academic_year": academic_year,
        "semester": semester,
        "exam_type": exam_type,
        "file_rows": file_rows,
        "stats": stats,
    }


def serialize_enrollment_result(session_id: int, academic_year: str, semester: str,
                                 exam_type: str, stats: dict) -> dict:
    """Serialize enrollment import result."""
    return {
        "status": "ok",
        "session_id": session_id,
        "academic_year": academic_year,
        "semester": semester,
        "exam_type": exam_type,
        "stats": stats,
    }


def serialize_session_summary(session, sections: list) -> dict:
    """Serialize session summary."""
    total_students = sum(s.num_students or 0 for s in sections)

    return {
        "session": {
            "id": session.id,
            "academic_year": session.academic_year,
            "semester": session.semester,
            "exam_type": session.exam_type,
        },
        "total_sections": len(sections),
        "total_students": total_students,
        "sections": [
            {
                "course_id": s.course.course_id if s.course else None,
                "course_name": s.course.course_name_th if s.course else None,
                "section_no": s.section_no,
                "num_students": s.num_students,
            }
            for s in sections
        ],
    }