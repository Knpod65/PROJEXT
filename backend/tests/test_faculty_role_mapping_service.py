"""Tests for D3.6 — multi-faculty role semantics service."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.faculty_role_mapping import FacultyRoleMapping, make_faculty_role_mapping
from services.faculty_role_mapping_service import (
    build_default_mappings_from_permissions,
    clear_role_mappings,
    get_all_permitted_roles,
    get_effective_mapping,
    has_permission,
    register_role_mapping,
    validate_role_mapping,
)


def setup_function():
    clear_role_mappings()


# ── build_default_mappings_from_permissions ───────────────────────────────────

def test_default_mappings_include_view_all_for_admin():
    mappings = build_default_mappings_from_permissions()
    admin_map = next((m for m in mappings if m.role == "admin"), None)
    assert admin_map is not None
    assert admin_map.can_view_all is True


def test_default_mappings_include_sign_for_esq_head():
    mappings = build_default_mappings_from_permissions()
    esq_map = next((m for m in mappings if m.role == "esq_head"), None)
    assert esq_map is not None
    assert esq_map.can_sign is True


def test_default_mappings_include_supervise_for_staff():
    mappings = build_default_mappings_from_permissions()
    staff_map = next((m for m in mappings if m.role == "staff"), None)
    assert staff_map is not None
    assert staff_map.can_supervise is True


def test_default_mappings_include_write_for_teacher():
    mappings = build_default_mappings_from_permissions()
    teacher_map = next((m for m in mappings if m.role == "teacher"), None)
    assert teacher_map is not None
    assert teacher_map.can_write_sections is True


# ── has_permission ────────────────────────────────────────────────────────────

def test_has_permission_true_for_known_role():
    assert has_permission("admin", "view_all") is True


def test_has_permission_false_for_role_without_permission():
    assert has_permission("print_shop", "view_all") is False


def test_has_permission_falls_back_to_permissions_when_no_override():
    clear_role_mappings()
    assert has_permission("esq_head", "sign") is True


# ── register_role_mapping / faculty override ──────────────────────────────────

def test_faculty_specific_mapping_overrides_global():
    fac_mapping = make_faculty_role_mapping("esq_head", faculty_id=5, can_sign=False)
    register_role_mapping(fac_mapping)
    assert has_permission("esq_head", "sign", faculty_id=5) is False


def test_global_override_applies_when_no_faculty_specific():
    global_mapping = make_faculty_role_mapping("teacher", faculty_id=None, can_manage_print=True)
    register_role_mapping(global_mapping)
    assert has_permission("teacher", "manage_print") is True


def test_register_replaces_previous_for_same_key():
    m1 = make_faculty_role_mapping("admin", faculty_id=1, can_manage_config=False)
    m2 = make_faculty_role_mapping("admin", faculty_id=1, can_manage_config=True)
    register_role_mapping(m1)
    register_role_mapping(m2)
    assert has_permission("admin", "manage_config", faculty_id=1) is True


# ── get_all_permitted_roles ───────────────────────────────────────────────────

def test_get_all_permitted_roles_includes_admin_for_manage_config():
    roles = get_all_permitted_roles("manage_config")
    assert "admin" in roles


def test_get_all_permitted_roles_for_view_all():
    roles = get_all_permitted_roles("view_all")
    assert "admin" in roles
    assert "esq_head" in roles


# ── validate_role_mapping ─────────────────────────────────────────────────────

def test_validate_valid_mapping_returns_empty():
    m = make_faculty_role_mapping("admin")
    assert validate_role_mapping(m) == []


def test_validate_errors_on_empty_role():
    m = make_faculty_role_mapping("  ")
    errors = validate_role_mapping(m)
    assert any("role" in e for e in errors)


# ── FacultyRoleMapping is frozen ──────────────────────────────────────────────

def test_faculty_role_mapping_is_frozen():
    m = make_faculty_role_mapping("admin")
    with pytest.raises(Exception):
        m.can_sign = True  # type: ignore[misc]


# ── faculty_id=None as global ─────────────────────────────────────────────────

def test_none_faculty_id_applies_as_global():
    global_m = make_faculty_role_mapping("teacher", faculty_id=None, can_supervise=False)
    register_role_mapping(global_m)
    assert has_permission("teacher", "supervise", faculty_id=None) is False
    assert has_permission("teacher", "supervise", faculty_id=99) is False


# ── permissions are independent ───────────────────────────────────────────────

def test_can_sign_does_not_affect_can_view_all():
    m = make_faculty_role_mapping("custom", can_sign=True, can_view_all=False)
    register_role_mapping(m)
    assert has_permission("custom", "sign") is True
    assert has_permission("custom", "view_all") is False


# ── clear_role_mappings ───────────────────────────────────────────────────────

def test_clear_role_mappings_resets_state():
    register_role_mapping(make_faculty_role_mapping("admin", can_manage_config=False))
    clear_role_mappings()
    # After clear, should fall back to permissions.py default (admin can manage config)
    assert has_permission("admin", "manage_config") is True
