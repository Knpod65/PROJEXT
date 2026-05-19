"""FacultyConfig — pure-Python frozen dataclass for per-faculty platform configuration.

NOT a SQLAlchemy model. No DB reads or writes here.
The in-memory repository and DB-backed repository both implement
FacultyConfigRepository; only the in-memory variant ships in D3.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class FacultyConfig:
    faculty_id: int
    code: str             # short code: "POL", "ENG", "MED"
    name_th: str          # Thai full name
    name_en: str          # English full name
    email_domain: str     # "polsci.cmu.ac.th"
    timezone: str         # "Asia/Bangkok"
    academic_year_default: str  # "2568"
    semester_default: str       # "2"
    is_active: bool
    created_at: str       # UTC ISO
    updated_at: str       # UTC ISO
    metadata: dict[str, Any]


def make_faculty_config(
    faculty_id: int,
    code: str,
    name_th: str,
    name_en: str,
    *,
    email_domain: str = "",
    timezone: str = "Asia/Bangkok",
    academic_year_default: str = "2568",
    semester_default: str = "2",
    is_active: bool = True,
    metadata: dict[str, Any] | None = None,
) -> FacultyConfig:
    """Factory that auto-generates created_at and updated_at timestamps."""
    now = _utc_now_iso()
    return FacultyConfig(
        faculty_id=faculty_id,
        code=code.strip(),
        name_th=name_th,
        name_en=name_en,
        email_domain=email_domain,
        timezone=timezone,
        academic_year_default=academic_year_default,
        semester_default=semester_default,
        is_active=is_active,
        created_at=now,
        updated_at=now,
        metadata=dict(metadata) if metadata else {},
    )
