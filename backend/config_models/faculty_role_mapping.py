"""FacultyRoleMapping — per-faculty configurable permission matrix overlay.

Pure Python frozen dataclass. permissions.py is NOT modified.
This provides an additive configurable layer for new callers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FacultyRoleMapping:
    faculty_id: int | None   # None = global override (applies when no faculty-specific)
    role: str
    can_view_all: bool
    can_sign: bool
    can_supervise: bool
    can_write_sections: bool
    can_manage_print: bool
    can_manage_config: bool  # typically admin-only
    metadata: dict[str, Any]


def make_faculty_role_mapping(
    role: str,
    *,
    faculty_id: int | None = None,
    can_view_all: bool = False,
    can_sign: bool = False,
    can_supervise: bool = False,
    can_write_sections: bool = False,
    can_manage_print: bool = False,
    can_manage_config: bool = False,
    metadata: dict[str, Any] | None = None,
) -> FacultyRoleMapping:
    return FacultyRoleMapping(
        faculty_id=faculty_id,
        role=role,
        can_view_all=can_view_all,
        can_sign=can_sign,
        can_supervise=can_supervise,
        can_write_sections=can_write_sections,
        can_manage_print=can_manage_print,
        can_manage_config=can_manage_config,
        metadata=dict(metadata) if metadata else {},
    )
