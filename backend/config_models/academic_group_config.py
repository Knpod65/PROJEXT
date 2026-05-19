"""AcademicGroupConfig — per-faculty configurable academic group definitions.

Pure Python frozen dataclass. academic_groups.py is NOT modified.
This registry overlays academic_groups.py constants and falls back to them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AcademicGroupConfig:
    faculty_id: int
    code: str                        # "IA", "GOV", "PA", "STB"
    label_th: str                    # Thai display label
    label_en: str                    # English display label
    course_prefixes: tuple[str, ...] # 3-digit course ID prefixes ("126",)
    legacy_aliases: tuple[str, ...]  # old codes that map to this group
    is_active: bool
    metadata: dict[str, Any]


def make_academic_group_config(
    faculty_id: int,
    code: str,
    label_th: str,
    label_en: str,
    course_prefixes: tuple[str, ...],
    *,
    legacy_aliases: tuple[str, ...] = (),
    is_active: bool = True,
    metadata: dict[str, Any] | None = None,
) -> AcademicGroupConfig:
    return AcademicGroupConfig(
        faculty_id=faculty_id,
        code=code.strip().upper(),
        label_th=label_th,
        label_en=label_en,
        course_prefixes=course_prefixes,
        legacy_aliases=legacy_aliases,
        is_active=is_active,
        metadata=dict(metadata) if metadata else {},
    )
