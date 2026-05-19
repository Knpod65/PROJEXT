"""Tests for D3.5 — academic group registry service."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.academic_group_config import AcademicGroupConfig, make_academic_group_config
from services.academic_group_registry_service import (
    can_access_group,
    clear_all_groups,
    clear_faculty_groups,
    get_group_for_code,
    get_group_for_course_id,
    get_group_for_prefix,
    get_group_label,
    list_groups,
    load_defaults_from_academic_groups,
    normalize_group_code,
    register_academic_groups,
)


def setup_function():
    clear_all_groups()


def _make_group(faculty_id: int, code: str, label: str, prefixes: tuple, **kwargs) -> AcademicGroupConfig:
    return make_academic_group_config(
        faculty_id=faculty_id,
        code=code,
        label_th=f"คณะ {label}",
        label_en=label,
        course_prefixes=prefixes,
        **kwargs,
    )


# ── make_academic_group_config ────────────────────────────────────────────────

def test_make_group_config_populates_fields():
    g = _make_group(1, "IA", "International Affairs", ("126",))
    assert g.faculty_id == 1
    assert g.code == "IA"
    assert g.label_en == "International Affairs"
    assert g.course_prefixes == ("126",)
    assert g.is_active is True
    assert g.metadata == {}


def test_academic_group_config_is_frozen():
    g = _make_group(1, "GOV", "Political Science", ("127",))
    with pytest.raises(Exception):
        g.code = "MUTATED"  # type: ignore[misc]


# ── register / get_group_for_code ─────────────────────────────────────────────

def test_register_and_get_group_for_code():
    g = _make_group(1, "IA", "International Affairs", ("126",))
    register_academic_groups(1, [g])
    result = get_group_for_code("IA", faculty_id=1)
    assert result is not None
    assert result.code == "IA"


def test_get_group_for_prefix_returns_registry_entry():
    g = _make_group(1, "GOV", "Political Science", ("127",))
    register_academic_groups(1, [g])
    result = get_group_for_prefix("127", faculty_id=1)
    assert result is not None
    assert result.code == "GOV"


def test_get_group_for_prefix_falls_back_to_academic_groups():
    result = get_group_for_prefix("126")
    assert result is not None
    assert result.code == "IA"


def test_get_group_for_prefix_returns_none_for_unknown_with_no_registry():
    result = get_group_for_prefix("999")
    assert result is None


# ── get_group_for_course_id ───────────────────────────────────────────────────

def test_get_group_for_course_id_extracts_prefix():
    result = get_group_for_course_id("127001")
    assert result is not None
    assert result.code == "GOV"


def test_get_group_for_course_id_too_short_returns_none():
    assert get_group_for_course_id("12") is None


# ── get_group_label ───────────────────────────────────────────────────────────

def test_get_group_label_returns_thai_by_default():
    g = make_academic_group_config(1, "IA", "รัฐศาสตร์", "Pol Sci", ("126",))
    register_academic_groups(1, [g])
    label = get_group_label("IA", faculty_id=1, lang="th")
    assert label == "รัฐศาสตร์"


def test_get_group_label_returns_english():
    g = make_academic_group_config(1, "IA", "รัฐศาสตร์", "International Affairs", ("126",))
    register_academic_groups(1, [g])
    label = get_group_label("IA", faculty_id=1, lang="en")
    assert label == "International Affairs"


def test_get_group_label_falls_back_to_academic_groups():
    label = get_group_label("GOV")
    assert label is not None
    assert "Political" in label or "GOV" in label


# ── normalize_group_code ──────────────────────────────────────────────────────

def test_normalize_group_code_resolves_legacy_alias_from_registry():
    g = make_academic_group_config(1, "IA", "IA", "IA", ("126",), legacy_aliases=("IR",))
    register_academic_groups(1, [g])
    result = normalize_group_code("IR", faculty_id=1)
    assert result == "IA"


def test_normalize_group_code_falls_back_to_legacy_group_aliases():
    result = normalize_group_code("IR")
    assert result == "IA"


def test_normalize_group_code_returns_none_for_none():
    assert normalize_group_code(None) is None


def test_normalize_group_code_returns_none_for_empty():
    assert normalize_group_code("") is None


# ── can_access_group ──────────────────────────────────────────────────────────

def test_can_access_same_code():
    assert can_access_group("GOV", "GOV") is True


def test_can_access_when_target_none():
    assert can_access_group("GOV", None) is True


def test_cannot_access_different_codes():
    assert can_access_group("GOV", "IA") is False


def test_can_access_when_target_all():
    assert can_access_group("GOV", "ALL") is True


# ── load_defaults_from_academic_groups ───────────────────────────────────────

def test_load_defaults_registers_four_default_groups():
    load_defaults_from_academic_groups(faculty_id=1)
    groups = list_groups(1)
    codes = {g.code for g in groups}
    assert "IA" in codes
    assert "GOV" in codes
    assert "PA" in codes
    assert "STB" in codes


# ── list_groups ───────────────────────────────────────────────────────────────

def test_list_groups_returns_only_active():
    active = make_academic_group_config(1, "IA", "IA", "IA", ("126",), is_active=True)
    inactive = make_academic_group_config(1, "GOV", "GOV", "GOV", ("127",), is_active=False)
    register_academic_groups(1, [active, inactive])
    result = list_groups(1)
    assert len(result) == 1
    assert result[0].code == "IA"


# ── registry isolation ────────────────────────────────────────────────────────

def test_registry_isolated_between_faculties():
    g1 = _make_group(1, "IA", "IA", ("126",))
    g2 = _make_group(2, "ENG", "Engineering", ("200",))
    register_academic_groups(1, [g1])
    register_academic_groups(2, [g2])
    assert get_group_for_code("IA", faculty_id=1) is not None
    assert get_group_for_code("ENG", faculty_id=1) is None
    assert get_group_for_code("ENG", faculty_id=2) is not None


def test_clear_all_groups_resets_state():
    register_academic_groups(1, [_make_group(1, "IA", "IA", ("126",))])
    clear_all_groups()
    assert list_groups(1) == []
