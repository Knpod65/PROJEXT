"""Academic group registry service — configurable overlay on academic_groups.py.

academic_groups.py is NOT modified. This service provides:
- Per-faculty group definitions stored in a module-level registry
- Fallback to academic_groups.py constants (PREFIX_TO_GROUP, GROUP_TO_LABEL, etc.)
  when no registry entry is found

Use clear_all_groups() in tests for isolation.
"""
from __future__ import annotations

import threading
from typing import Any

from config_models.academic_group_config import AcademicGroupConfig, make_academic_group_config

_lock = threading.Lock()
_registry: dict[int, list[AcademicGroupConfig]] = {}


def register_academic_groups(faculty_id: int, groups: list[AcademicGroupConfig]) -> None:
    """Replace all groups for a faculty with the provided list."""
    with _lock:
        _registry[faculty_id] = list(groups)


def get_group_for_code(
    code: str,
    faculty_id: int | None = None,
) -> AcademicGroupConfig | None:
    """Return the group config matching `code` for the given faculty.

    Falls back to a synthetic config built from GROUP_TO_LABEL when no registry entry.
    """
    normalized = code.strip().upper()
    if faculty_id is not None:
        with _lock:
            for g in _registry.get(faculty_id, []):
                if g.code == normalized or normalized in [a.strip().upper() for a in g.legacy_aliases]:
                    return g

    # Fallback to academic_groups module constants
    from academic_groups import GROUP_TO_LABEL, normalize_academic_group_code
    resolved = normalize_academic_group_code(code)
    if resolved and resolved in GROUP_TO_LABEL:
        return _synthetic_group(resolved, GROUP_TO_LABEL[resolved])
    return None


def get_group_for_prefix(
    prefix: str,
    faculty_id: int | None = None,
) -> AcademicGroupConfig | None:
    """Return the group config for the given 3-digit course prefix.

    Checks registry first; falls back to PREFIX_TO_GROUP from academic_groups.py.
    """
    if faculty_id is not None:
        with _lock:
            for g in _registry.get(faculty_id, []):
                if prefix in g.course_prefixes:
                    return g

    from academic_groups import PREFIX_TO_GROUP, GROUP_TO_LABEL
    code = PREFIX_TO_GROUP.get(prefix)
    if code:
        return _synthetic_group(code, GROUP_TO_LABEL.get(code, code), prefixes=(prefix,))
    return None


def get_group_for_course_id(
    course_id: str,
    faculty_id: int | None = None,
) -> AcademicGroupConfig | None:
    """Extract 3-digit prefix from course_id and delegate to get_group_for_prefix."""
    digits = "".join(ch for ch in str(course_id).strip() if ch.isdigit())
    if len(digits) < 3:
        return None
    return get_group_for_prefix(digits[:3], faculty_id)


def list_groups(faculty_id: int) -> list[AcademicGroupConfig]:
    """Return all active groups for the given faculty."""
    with _lock:
        return [g for g in _registry.get(faculty_id, []) if g.is_active]


def get_group_label(
    code: str,
    faculty_id: int | None = None,
    *,
    lang: str = "th",
) -> str | None:
    """Return the display label for a group code in the requested language.

    Falls back to GROUP_TO_LABEL from academic_groups.py.
    """
    group = get_group_for_code(code, faculty_id)
    if group is None:
        return None
    return group.label_th if lang == "th" else group.label_en


def normalize_group_code(
    code: str | None,
    faculty_id: int | None = None,
) -> str | None:
    """Resolve legacy aliases from registry or LEGACY_GROUP_ALIASES.

    Returns None for None/empty input.
    """
    if not code:
        return None
    normalized = code.strip().upper()

    if faculty_id is not None:
        with _lock:
            for g in _registry.get(faculty_id, []):
                if normalized in [a.strip().upper() for a in g.legacy_aliases]:
                    return g.code

    from academic_groups import LEGACY_GROUP_ALIASES
    return LEGACY_GROUP_ALIASES.get(normalized, normalized)


def can_access_group(
    viewer_code: str | None,
    target_code: str | None,
    faculty_id: int | None = None,
) -> bool:
    """Check if viewer_code is allowed to access target_code resources.

    Falls back to academic_groups.can_access_academic_group().
    """
    resolved_viewer = normalize_group_code(viewer_code, faculty_id)
    resolved_target = normalize_group_code(target_code, faculty_id)

    if resolved_target in (None, "ALL"):
        return True
    if resolved_viewer is None:
        return False
    return resolved_viewer == resolved_target


def load_defaults_from_academic_groups(faculty_id: int) -> None:
    """Seed registry with the 4 default groups from academic_groups.py constants."""
    from academic_groups import PREFIX_TO_GROUP, GROUP_TO_LABEL, LEGACY_GROUP_ALIASES

    code_to_prefixes: dict[str, list[str]] = {}
    for prefix, code in PREFIX_TO_GROUP.items():
        code_to_prefixes.setdefault(code, []).append(prefix)

    alias_map: dict[str, list[str]] = {}
    for alias, code in LEGACY_GROUP_ALIASES.items():
        alias_map.setdefault(code, []).append(alias)

    groups = []
    for code, label in GROUP_TO_LABEL.items():
        groups.append(make_academic_group_config(
            faculty_id=faculty_id,
            code=code,
            label_th=label,
            label_en=label,
            course_prefixes=tuple(code_to_prefixes.get(code, [])),
            legacy_aliases=tuple(alias_map.get(code, [])),
        ))
    register_academic_groups(faculty_id, groups)


def clear_faculty_groups(faculty_id: int) -> None:
    with _lock:
        _registry.pop(faculty_id, None)


def clear_all_groups() -> None:
    with _lock:
        _registry.clear()


def _synthetic_group(
    code: str,
    label: str,
    *,
    prefixes: tuple[str, ...] = (),
    faculty_id: int = 0,
) -> AcademicGroupConfig:
    """Build a synthetic AcademicGroupConfig from academic_groups.py constants."""
    return AcademicGroupConfig(
        faculty_id=faculty_id,
        code=code,
        label_th=label,
        label_en=label,
        course_prefixes=prefixes,
        legacy_aliases=(),
        is_active=True,
        metadata={"source": "academic_groups_fallback"},
    )
