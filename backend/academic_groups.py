from __future__ import annotations

from dataclasses import dataclass


LEGACY_GROUP_ALIASES = {
    "IR": "IA",
}

PREFIX_TO_GROUP = {
    "126": "IA",
    "127": "GOV",
    "128": "PA",
    "131": "STB",
    "140": "ALL",
}

GROUP_TO_LABEL = {
    "IA": "International Affairs",
    "GOV": "Political Science",
    "PA": "Public Administration",
    "STB": "School of Sustainability",
    "ALL": "All Groups",
}


@dataclass(frozen=True)
class AcademicGroupInfo:
    code: str
    label: str
    prefix: str | None = None


def normalize_academic_group_code(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    return LEGACY_GROUP_ALIASES.get(text, text)


def get_academic_group_info_from_course_id(course_id: object | None) -> AcademicGroupInfo | None:
    if course_id is None:
        return None
    text = "".join(ch for ch in str(course_id).strip() if ch.isdigit())
    if len(text) < 3:
        return None
    prefix = text[:3]
    code = PREFIX_TO_GROUP.get(prefix)
    if not code:
        return None
    return AcademicGroupInfo(code=code, label=GROUP_TO_LABEL.get(code, code), prefix=prefix)


def get_academic_group_code_from_course_id(course_id: object | None) -> str | None:
    info = get_academic_group_info_from_course_id(course_id)
    return info.code if info else None


def academic_group_label(code: object | None) -> str | None:
    normalized = normalize_academic_group_code(code)
    if not normalized:
        return None
    return GROUP_TO_LABEL.get(normalized, normalized)


def can_access_academic_group(
    viewer_group: object | None,
    target_group: object | None,
) -> bool:
    normalized_viewer = normalize_academic_group_code(viewer_group)
    normalized_target = normalize_academic_group_code(target_group)
    if normalized_target in (None, "ALL"):
        return True
    if normalized_viewer is None:
        return False
    return normalized_viewer == normalized_target


def visible_course_prefixes_for_group(viewer_group: object | None) -> list[str]:
    normalized_viewer = normalize_academic_group_code(viewer_group)
    if not normalized_viewer:
        return []
    return [
        prefix
        for prefix, group_code in PREFIX_TO_GROUP.items()
        if group_code in (normalized_viewer, "ALL")
    ]


def build_course_group_clause(course_id_column, viewer_group: object | None):
    from sqlalchemy import or_

    prefixes = visible_course_prefixes_for_group(viewer_group)
    if not prefixes:
        return None
    return or_(*[course_id_column.like(f"{prefix}%") for prefix in prefixes])
