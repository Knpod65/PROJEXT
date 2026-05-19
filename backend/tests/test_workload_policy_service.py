"""Tests for D3.4 — workload and staff policy config service."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.workload_policy import WorkloadPolicy, make_workload_policy
from services.workload_policy_service import (
    build_default_policy_from_settings,
    clear_workload_policies,
    get_effective_policy,
    get_supervision_slot_limit,
    is_eligible_for_paper_distribution,
    is_excluded_supervisor,
    register_workload_policy,
    validate_workload_policy,
)
from policies.workload_policy_registry import (
    EXCLUDED_DIVISION_FACULTY_SECRETARY,
    SPECIAL_ROLE_ESQ_STAFF,
    SPECIAL_ROLE_ROOM_KEEPER,
    get_effective_workload_policy,
)


def setup_function():
    clear_workload_policies()


# ── build_default_policy_from_settings ───────────────────────────────────────

def test_default_policy_reads_settings():
    policy = build_default_policy_from_settings()
    from config.settings import settings
    assert policy.paper_distribution_division == settings.paper_distribution_division
    assert policy.excluded_usernames == settings.paper_distribution_excluded_usernames


def test_default_policy_includes_faculty_secretary_in_excluded_divisions():
    policy = build_default_policy_from_settings()
    assert "Faculty_Secretary" in policy.excluded_divisions


def test_default_policy_includes_room_keeper_in_excluded_special_roles():
    policy = build_default_policy_from_settings()
    assert "room_keeper" in policy.excluded_special_roles


def test_default_policy_includes_esq_staff_in_excluded_special_roles():
    policy = build_default_policy_from_settings()
    assert "esq_staff" in policy.excluded_special_roles


def test_default_policy_faculty_id_is_none():
    policy = build_default_policy_from_settings()
    assert policy.faculty_id is None


# ── register / get_effective_policy ──────────────────────────────────────────

def test_get_effective_returns_faculty_when_registered():
    fac_policy = make_workload_policy(faculty_id=7, paper_distribution_division="CustomDiv")
    register_workload_policy(fac_policy)
    result = get_effective_policy(7)
    assert result.paper_distribution_division == "CustomDiv"


def test_get_effective_returns_global_when_no_faculty_policy():
    global_policy = make_workload_policy(faculty_id=None, paper_distribution_division="Global")
    register_workload_policy(global_policy)
    result = get_effective_policy(99)
    assert result.paper_distribution_division == "Global"


def test_faculty_override_does_not_affect_other_faculty():
    fac1 = make_workload_policy(faculty_id=1, paper_distribution_division="Div1")
    fac2 = make_workload_policy(faculty_id=2, paper_distribution_division="Div2")
    register_workload_policy(fac1)
    register_workload_policy(fac2)
    assert get_effective_policy(1).paper_distribution_division == "Div1"
    assert get_effective_policy(2).paper_distribution_division == "Div2"


# ── is_eligible_for_paper_distribution ───────────────────────────────────────

def test_false_when_username_excluded():
    policy = make_workload_policy(
        faculty_id=None,
        excluded_usernames=frozenset({"araya.fa", "sapanyu.wong"}),
    )
    register_workload_policy(policy)
    assert is_eligible_for_paper_distribution("araya.fa", "อารยา", "OtherDiv", None) is False


def test_false_when_name_snippet_matches():
    policy = make_workload_policy(
        faculty_id=None,
        excluded_name_snippets=("อารยา", "สัพพัญญู"),
    )
    register_workload_policy(policy)
    assert is_eligible_for_paper_distribution("x.y", "อารยา ฟ้ารุ่งสาง", "OtherDiv", None) is False


def test_false_when_division_matches_distribution_division():
    policy = make_workload_policy(
        faculty_id=None,
        paper_distribution_division="Education_Student_Quality",
    )
    register_workload_policy(policy)
    assert is_eligible_for_paper_distribution("user", "Name", "Education_Student_Quality", None) is False


def test_false_when_special_role_excluded():
    policy = make_workload_policy(
        faculty_id=None,
        excluded_special_roles=frozenset({"room_keeper"}),
    )
    register_workload_policy(policy)
    assert is_eligible_for_paper_distribution("user", "Name", "OtherDiv", "room_keeper") is False


def test_true_when_no_exclusion_applies():
    policy = make_workload_policy(
        faculty_id=None,
        paper_distribution_division="TargetDiv",
        excluded_usernames=frozenset({"excluded_user"}),
    )
    register_workload_policy(policy)
    assert is_eligible_for_paper_distribution("other_user", "Clean Name", "OtherDiv", None) is True


def test_name_snippet_is_substring_match():
    policy = make_workload_policy(faculty_id=None, excluded_name_snippets=("อารยา",))
    register_workload_policy(policy)
    assert is_eligible_for_paper_distribution("x", "นางสาวอารยา สมชื่อ", "Div", None) is False


def test_empty_excluded_usernames_allows_all():
    policy = make_workload_policy(faculty_id=None, excluded_usernames=frozenset())
    register_workload_policy(policy)
    assert is_eligible_for_paper_distribution("anyone", "Name", "Div", None) is True


# ── is_excluded_supervisor ────────────────────────────────────────────────────

def test_excluded_supervisor_true_for_faculty_secretary_division():
    policy = make_workload_policy(
        faculty_id=None,
        excluded_divisions=frozenset({"Faculty_Secretary"}),
    )
    register_workload_policy(policy)
    assert is_excluded_supervisor("user", "Faculty_Secretary", None) is True


def test_excluded_supervisor_true_for_room_keeper():
    policy = make_workload_policy(
        faculty_id=None,
        excluded_special_roles=frozenset({"room_keeper"}),
    )
    register_workload_policy(policy)
    assert is_excluded_supervisor("user", "SomeDivision", "room_keeper") is True


def test_excluded_supervisor_false_when_neither():
    policy = make_workload_policy(
        faculty_id=None,
        excluded_divisions=frozenset({"Faculty_Secretary"}),
        excluded_special_roles=frozenset({"room_keeper"}),
    )
    register_workload_policy(policy)
    assert is_excluded_supervisor("user", "OtherDiv", "supervisor") is False


# ── get_supervision_slot_limit ────────────────────────────────────────────────

def test_supervision_slot_limit_returns_zero_for_unlimited():
    policy = make_workload_policy(faculty_id=None, max_supervision_sessions=0)
    register_workload_policy(policy)
    assert get_supervision_slot_limit() == 0


def test_supervision_slot_limit_returns_set_value():
    policy = make_workload_policy(faculty_id=None, max_supervision_sessions=5)
    register_workload_policy(policy)
    assert get_supervision_slot_limit() == 5


# ── validate_workload_policy ──────────────────────────────────────────────────

def test_validate_valid_policy_returns_empty():
    policy = make_workload_policy()
    assert validate_workload_policy(policy) == []


def test_validate_errors_on_negative_max_sessions():
    policy = make_workload_policy(max_supervision_sessions=-1)
    errors = validate_workload_policy(policy)
    assert any("max_supervision_sessions" in e for e in errors)


# ── WorkloadPolicy is frozen ──────────────────────────────────────────────────

def test_workload_policy_is_frozen():
    policy = make_workload_policy()
    with pytest.raises(Exception):
        policy.allow_cross_department = True  # type: ignore[misc]


# ── constants ─────────────────────────────────────────────────────────────────

def test_registry_constants():
    assert SPECIAL_ROLE_ROOM_KEEPER == "room_keeper"
    assert SPECIAL_ROLE_ESQ_STAFF == "esq_staff"
    assert EXCLUDED_DIVISION_FACULTY_SECRETARY == "Faculty_Secretary"


def test_get_effective_workload_policy_delegates():
    policy = make_workload_policy(faculty_id=None, paper_distribution_division="Test")
    register_workload_policy(policy)
    result = get_effective_workload_policy(None)
    assert result.paper_distribution_division == "Test"
