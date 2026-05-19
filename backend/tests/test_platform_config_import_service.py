"""Tests for D3.7 — platform config import service."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.academic_group_config import make_academic_group_config
from config_models.faculty_config import make_faculty_config
from config_models.faculty_role_mapping import make_faculty_role_mapping
from config_models.governance_flow import make_governance_flow_config
from config_models.workload_policy import make_workload_policy
from services.platform_config_export_service import build_platform_snapshot
from services.platform_config_import_service import (
    diff_platform_snapshots,
    parse_academic_group_config,
    parse_faculty_config,
    parse_governance_flow,
    parse_platform_snapshot,
    parse_role_mapping,
    parse_workload_policy,
    validate_and_import_snapshot,
)


# ── parse_faculty_config ──────────────────────────────────────────────────────

def test_parse_faculty_config_missing_faculty_id_raises():
    with pytest.raises(ValueError, match="faculty_id"):
        parse_faculty_config({"code": "POL", "name_th": "x", "name_en": "y"})


def test_parse_faculty_config_missing_code_raises():
    with pytest.raises(ValueError, match="code"):
        parse_faculty_config({"faculty_id": 1, "code": "", "name_th": "x", "name_en": "y"})


def test_parse_faculty_config_returns_faculty_config():
    from config_models.faculty_config import FacultyConfig
    fc = parse_faculty_config({"faculty_id": 2, "code": "ENG", "name_th": "วิศวะ", "name_en": "Engineering"})
    assert isinstance(fc, FacultyConfig)
    assert fc.faculty_id == 2
    assert fc.code == "ENG"


# ── parse_workload_policy ─────────────────────────────────────────────────────

def test_parse_workload_policy_returns_workload_policy():
    from config_models.workload_policy import WorkloadPolicy
    data = {
        "faculty_id": 1,
        "paper_distribution_division": "Division A",
        "excluded_usernames": ["araya.fa"],
        "excluded_name_snippets": [],
        "excluded_special_roles": ["room_keeper"],
        "excluded_divisions": ["Faculty_Secretary"],
        "max_supervision_sessions": 3,
        "allow_cross_department": False,
        "metadata": {},
    }
    policy = parse_workload_policy(data)
    assert isinstance(policy, WorkloadPolicy)
    assert "araya.fa" in policy.excluded_usernames
    assert policy.max_supervision_sessions == 3


def test_parse_workload_policy_handles_missing_optional_fields():
    policy = parse_workload_policy({"faculty_id": None})
    assert policy.excluded_usernames == frozenset()
    assert policy.max_supervision_sessions == 0


# ── parse_governance_flow ─────────────────────────────────────────────────────

def test_parse_governance_flow_deserializes_signer_slots():
    from config_models.governance_flow import GovernanceFlowConfig
    data = {
        "flow_name": "test",
        "round_1_signers": [{"position": 1, "role": "admin", "username_hint": "alice", "required": True}],
        "round_2_signers": [],
        "faculty_id": None,
        "requires_governance_review": True,
        "approval_quorum": 1,
        "metadata": {},
    }
    flow = parse_governance_flow(data)
    assert isinstance(flow, GovernanceFlowConfig)
    assert len(flow.round_1_signers) == 1
    assert flow.round_1_signers[0].username_hint == "alice"


# ── parse_platform_snapshot ───────────────────────────────────────────────────

def test_parse_platform_snapshot_returns_all_keys():
    snap = build_platform_snapshot(
        faculty_configs=[make_faculty_config(1, "POL", "A", "B")],
        workload_policies=[make_workload_policy(faculty_id=1)],
        governance_flows=[make_governance_flow_config("f", [{"position": 1, "role": "admin", "username_hint": None, "required": True}], [])],
        academic_group_configs=[make_academic_group_config(1, "IA", "A", "B", ("126",))],
        role_mappings=[make_faculty_role_mapping("admin")],
    )
    result = parse_platform_snapshot(snap)
    assert set(result.keys()) == {
        "faculty_configs", "workload_policies", "governance_flows",
        "academic_group_configs", "role_mappings",
    }


def test_parse_platform_snapshot_empty_snapshot():
    result = parse_platform_snapshot({})
    assert result["faculty_configs"] == []
    assert result["role_mappings"] == []


# ── diff_platform_snapshots ───────────────────────────────────────────────────

def test_diff_detects_added_faculty():
    before = build_platform_snapshot(faculty_configs=[], workload_policies=[], governance_flows=[], academic_group_configs=[], role_mappings=[])
    after = build_platform_snapshot(
        faculty_configs=[make_faculty_config(1, "POL", "A", "B")],
        workload_policies=[], governance_flows=[], academic_group_configs=[], role_mappings=[],
    )
    diff = diff_platform_snapshots(before, after)
    assert len(diff["faculty_configs"]["added"]) == 1
    assert diff["faculty_configs"]["removed"] == []


def test_diff_detects_removed_faculty():
    before = build_platform_snapshot(
        faculty_configs=[make_faculty_config(1, "POL", "A", "B")],
        workload_policies=[], governance_flows=[], academic_group_configs=[], role_mappings=[],
    )
    after = build_platform_snapshot(faculty_configs=[], workload_policies=[], governance_flows=[], academic_group_configs=[], role_mappings=[])
    diff = diff_platform_snapshots(before, after)
    assert len(diff["faculty_configs"]["removed"]) == 1
    assert diff["faculty_configs"]["added"] == []


def test_diff_identical_snapshots_no_changes():
    snap = build_platform_snapshot(
        faculty_configs=[make_faculty_config(1, "POL", "A", "B")],
        workload_policies=[], governance_flows=[], academic_group_configs=[], role_mappings=[],
    )
    diff = diff_platform_snapshots(snap, snap)
    assert diff["faculty_configs"]["added"] == []
    assert diff["faculty_configs"]["removed"] == []
    assert diff["faculty_configs"]["modified"] == []


# ── validate_and_import_snapshot ─────────────────────────────────────────────

def test_validate_dry_run_valid_snapshot():
    snap = build_platform_snapshot(
        faculty_configs=[make_faculty_config(1, "POL", "A", "B")],
        workload_policies=[], governance_flows=[], academic_group_configs=[], role_mappings=[],
    )
    result = validate_and_import_snapshot(snap, dry_run=True)
    assert result["valid"] is True
    assert result["errors"] == []
    assert result["dry_run"] is True


def test_validate_dry_run_does_not_mutate_registries():
    from services.faculty_role_mapping_service import clear_role_mappings, has_permission
    clear_role_mappings()
    snap = build_platform_snapshot(
        faculty_configs=[],
        workload_policies=[],
        governance_flows=[],
        academic_group_configs=[],
        role_mappings=[make_faculty_role_mapping("custom_role", can_manage_config=True)],
    )
    validate_and_import_snapshot(snap, dry_run=True)
    # custom_role should NOT be in registry since dry_run=True
    assert has_permission("custom_role", "manage_config") is False
    clear_role_mappings()


def test_validate_invalid_snapshot_returns_errors():
    snap = {"faculty_configs": [{"faculty_id": None, "code": "", "name_th": "", "name_en": ""}]}
    result = validate_and_import_snapshot(snap, dry_run=True)
    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_validate_empty_faculty_configs_adds_warning():
    snap = build_platform_snapshot(faculty_configs=[], workload_policies=[], governance_flows=[], academic_group_configs=[], role_mappings=[])
    result = validate_and_import_snapshot(snap, dry_run=True)
    assert any("faculty_configs" in w for w in result["warnings"])


# ── round-trip ────────────────────────────────────────────────────────────────

def test_round_trip_faculty_config():
    original = make_faculty_config(5, "MED", "แพทย์", "Medicine", email_domain="med.cmu.ac.th")
    from services.platform_config_export_service import export_faculty_config
    exported = export_faculty_config(original)
    restored = parse_faculty_config(exported)
    assert restored.faculty_id == original.faculty_id
    assert restored.code == original.code
    assert restored.name_th == original.name_th
    assert restored.email_domain == original.email_domain
