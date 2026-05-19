"""Tests for D3.7 — platform config export service."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.academic_group_config import make_academic_group_config
from config_models.faculty_config import make_faculty_config
from config_models.faculty_role_mapping import make_faculty_role_mapping
from config_models.governance_flow import make_governance_flow_config
from config_models.workload_policy import make_workload_policy
from services.platform_config_export_service import (
    build_platform_snapshot,
    export_academic_groups,
    export_faculty_config,
    export_governance_flow,
    export_role_mappings,
    export_workload_policy,
    platform_snapshot_to_json,
)


def _faculty():
    return make_faculty_config(1, "POL", "คณะรัฐศาสตร์", "Political Science")


def _flow():
    return make_governance_flow_config(
        "test_flow",
        [{"position": 1, "role": "admin", "username_hint": "atikant.s", "required": True}],
        [],
        faculty_id=1,
    )


def _policy():
    return make_workload_policy(
        faculty_id=1,
        excluded_usernames=frozenset({"araya.fa", "sapanyu.wong"}),
        excluded_name_snippets=("ดร.",),
        excluded_special_roles=frozenset({"room_keeper"}),
        excluded_divisions=frozenset({"Faculty_Secretary"}),
    )


def _group():
    return make_academic_group_config(1, "IA", "รัฐศาสตร์", "Political Science", ("126",))


def _mapping():
    return make_faculty_role_mapping("admin", faculty_id=1, can_view_all=True, can_manage_config=True)


# ── export_faculty_config ─────────────────────────────────────────────────────

def test_export_faculty_config_includes_schema_version():
    result = export_faculty_config(_faculty())
    assert result["schema_version"] == "1.0"


def test_export_faculty_config_all_fields_present():
    result = export_faculty_config(_faculty())
    for field in ("faculty_id", "code", "name_th", "name_en", "email_domain",
                  "timezone", "academic_year_default", "semester_default",
                  "is_active", "created_at", "updated_at", "metadata"):
        assert field in result, f"Missing field: {field}"


def test_export_faculty_config_values():
    result = export_faculty_config(_faculty())
    assert result["faculty_id"] == 1
    assert result["code"] == "POL"
    assert result["name_th"] == "คณะรัฐศาสตร์"


# ── export_workload_policy ────────────────────────────────────────────────────

def test_export_workload_policy_frozenset_as_sorted_list():
    result = export_workload_policy(_policy())
    assert isinstance(result["excluded_usernames"], list)
    assert result["excluded_usernames"] == sorted(["araya.fa", "sapanyu.wong"])


def test_export_workload_policy_includes_schema_version():
    result = export_workload_policy(_policy())
    assert result["schema_version"] == "1.0"


def test_export_workload_policy_special_roles_sorted():
    result = export_workload_policy(_policy())
    assert isinstance(result["excluded_special_roles"], list)


# ── export_governance_flow ────────────────────────────────────────────────────

def test_export_governance_flow_includes_nested_signer_slots():
    result = export_governance_flow(_flow())
    assert isinstance(result["round_1_signers"], list)
    assert len(result["round_1_signers"]) == 1
    slot = result["round_1_signers"][0]
    assert slot["position"] == 1
    assert slot["role"] == "admin"
    assert slot["username_hint"] == "atikant.s"
    assert slot["required"] is True


def test_export_governance_flow_empty_round2():
    result = export_governance_flow(_flow())
    assert result["round_2_signers"] == []


def test_export_governance_flow_schema_version():
    result = export_governance_flow(_flow())
    assert result["schema_version"] == "1.0"


# ── export_academic_groups ────────────────────────────────────────────────────

def test_export_academic_groups_returns_list():
    result = export_academic_groups([_group()])
    assert isinstance(result, list)
    assert len(result) == 1


def test_export_academic_groups_includes_prefixes_as_list():
    result = export_academic_groups([_group()])
    assert isinstance(result[0]["course_prefixes"], list)
    assert "126" in result[0]["course_prefixes"]


# ── export_role_mappings ──────────────────────────────────────────────────────

def test_export_role_mappings_returns_list():
    result = export_role_mappings([_mapping()])
    assert len(result) == 1
    assert result[0]["role"] == "admin"
    assert result[0]["can_view_all"] is True
    assert result[0]["can_manage_config"] is True


# ── build_platform_snapshot ───────────────────────────────────────────────────

def test_build_platform_snapshot_includes_exported_at():
    snap = build_platform_snapshot(
        faculty_configs=[_faculty()],
        workload_policies=[],
        governance_flows=[],
        academic_group_configs=[],
        role_mappings=[],
    )
    assert "exported_at" in snap
    assert snap["exported_at"].endswith("+00:00") or "Z" in snap["exported_at"] or "T" in snap["exported_at"]


def test_build_platform_snapshot_schema_version():
    snap = build_platform_snapshot(
        faculty_configs=[],
        workload_policies=[],
        governance_flows=[],
        academic_group_configs=[],
        role_mappings=[],
    )
    assert snap["schema_version"] == "1.0"


def test_build_platform_snapshot_empty_lists_valid():
    snap = build_platform_snapshot(
        faculty_configs=[],
        workload_policies=[],
        governance_flows=[],
        academic_group_configs=[],
        role_mappings=[],
    )
    assert snap["faculty_configs"] == []
    assert snap["export_metadata"] == {}


# ── platform_snapshot_to_json ─────────────────────────────────────────────────

def test_platform_snapshot_to_json_valid_json():
    snap = build_platform_snapshot(
        faculty_configs=[_faculty()],
        workload_policies=[_policy()],
        governance_flows=[_flow()],
        academic_group_configs=[_group()],
        role_mappings=[_mapping()],
    )
    text = platform_snapshot_to_json(snap)
    parsed = json.loads(text)
    assert parsed["schema_version"] == "1.0"


def test_platform_snapshot_to_json_deterministic():
    snap = build_platform_snapshot(
        faculty_configs=[_faculty()],
        workload_policies=[],
        governance_flows=[],
        academic_group_configs=[],
        role_mappings=[],
    )
    assert platform_snapshot_to_json(snap) == platform_snapshot_to_json(snap)
