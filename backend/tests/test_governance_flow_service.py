"""Tests for D3.3 — governance flow configuration service."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_models.governance_flow import (
    GovernanceFlowConfig,
    SignerSlot,
    make_governance_flow_config,
)
from services.governance_flow_service import (
    build_default_flow_from_settings,
    clear_governance_flows,
    get_effective_flow,
    get_signer_order,
    register_governance_flow,
    validate_flow_config,
)
from config.settings import settings


def setup_function():
    clear_governance_flows()


# ── build_default_flow_from_settings ─────────────────────────────────────────

def test_default_flow_uses_settings_usernames():
    flow = build_default_flow_from_settings()
    usernames = settings.sign_order_usernames
    assert len(flow.round_1_signers) == len(usernames)


def test_default_flow_correct_slot_count():
    flow = build_default_flow_from_settings()
    assert len(flow.round_1_signers) >= 1


def test_default_flow_has_faculty_id_none():
    flow = build_default_flow_from_settings()
    assert flow.faculty_id is None


def test_default_flow_first_slot_is_admin():
    flow = build_default_flow_from_settings()
    assert flow.round_1_signers[0].role == "admin"


def test_default_flow_quorum_equals_slot_count():
    flow = build_default_flow_from_settings()
    assert flow.approval_quorum == len(flow.round_1_signers)


# ── make_governance_flow_config ───────────────────────────────────────────────

def test_make_flow_defaults_quorum_to_slot_count():
    flow = make_governance_flow_config(
        "test",
        [{"position": 1, "role": "admin", "username_hint": "a"}, {"position": 2, "role": "esq_head", "username_hint": "b"}],
        [],
    )
    assert flow.approval_quorum == 2


def test_make_flow_explicit_quorum():
    flow = make_governance_flow_config(
        "test",
        [{"position": 1, "role": "admin", "username_hint": None}, {"position": 2, "role": "esq_head", "username_hint": None}],
        [],
        approval_quorum=1,
    )
    assert flow.approval_quorum == 1


def test_flow_is_frozen():
    flow = make_governance_flow_config("test", [{"position": 1, "role": "admin", "username_hint": None}], [])
    with pytest.raises(Exception):
        flow.flow_name = "mutated"  # type: ignore[misc]


def test_signer_slot_is_frozen():
    slot = SignerSlot(position=1, role="admin", username_hint="a", required=True)
    with pytest.raises(Exception):
        slot.role = "mutated"  # type: ignore[misc]


def test_round_2_can_be_empty():
    flow = make_governance_flow_config(
        "single_round",
        [{"position": 1, "role": "admin", "username_hint": None}],
        [],
    )
    assert flow.round_2_signers == ()


# ── register / get_effective_flow ─────────────────────────────────────────────

def test_register_and_get_faculty_flow():
    flow = make_governance_flow_config(
        "faculty_flow",
        [{"position": 1, "role": "admin", "username_hint": "x"}],
        [],
        faculty_id=42,
    )
    register_governance_flow(flow)
    result = get_effective_flow(42)
    assert result.flow_name == "faculty_flow"


def test_get_effective_falls_back_to_global():
    global_flow = make_governance_flow_config(
        "global",
        [{"position": 1, "role": "admin", "username_hint": None}],
        [],
        faculty_id=None,
    )
    register_governance_flow(global_flow)
    result = get_effective_flow(99)
    assert result.flow_name == "global"


def test_get_effective_auto_builds_from_settings_if_no_global():
    result = get_effective_flow(None)
    assert result.flow_name == "settings_derived"
    assert len(result.round_1_signers) >= 1


def test_faculty_flow_does_not_affect_global():
    fac_flow = make_governance_flow_config(
        "fac_only",
        [{"position": 1, "role": "admin", "username_hint": "z"}],
        [],
        faculty_id=5,
    )
    register_governance_flow(fac_flow)
    global_result = get_effective_flow(None)
    assert global_result.flow_name == "settings_derived"


# ── get_signer_order ──────────────────────────────────────────────────────────

def test_get_signer_order_returns_username_hints():
    flow = make_governance_flow_config(
        "test",
        [
            {"position": 1, "role": "admin", "username_hint": "alice"},
            {"position": 2, "role": "esq_head", "username_hint": "bob"},
        ],
        [],
        faculty_id=None,
    )
    register_governance_flow(flow)
    order = get_signer_order(None)
    assert order == ("alice", "bob")


def test_get_signer_order_returns_none_for_no_hint():
    flow = make_governance_flow_config(
        "no_hints",
        [{"position": 1, "role": "admin", "username_hint": None}],
        [],
        faculty_id=None,
    )
    register_governance_flow(flow)
    order = get_signer_order(None)
    assert order == (None,)


# ── validate_flow_config ──────────────────────────────────────────────────────

def test_validate_valid_flow_returns_empty():
    flow = make_governance_flow_config(
        "valid",
        [{"position": 1, "role": "admin", "username_hint": None}],
        [],
    )
    assert validate_flow_config(flow) == []


def test_validate_errors_on_empty_flow_name():
    flow = make_governance_flow_config(
        "  ",  # whitespace only
        [{"position": 1, "role": "admin", "username_hint": None}],
        [],
    )
    errors = validate_flow_config(flow)
    assert any("flow_name" in e for e in errors)


def test_validate_errors_on_no_signers():
    flow = GovernanceFlowConfig(
        faculty_id=None,
        flow_name="empty",
        round_1_signers=(),
        round_2_signers=(),
        requires_governance_review=True,
        approval_quorum=0,
        created_at="2026-01-01T00:00:00+00:00",
        metadata={},
    )
    errors = validate_flow_config(flow)
    assert any("round_1_signers" in e for e in errors)


def test_validate_errors_when_quorum_exceeds_slots():
    flow = make_governance_flow_config(
        "bad_quorum",
        [{"position": 1, "role": "admin", "username_hint": None}],
        [],
        approval_quorum=5,
    )
    errors = validate_flow_config(flow)
    assert any("quorum" in e for e in errors)


def test_validate_errors_on_duplicate_positions():
    flow = GovernanceFlowConfig(
        faculty_id=None,
        flow_name="dup",
        round_1_signers=(
            SignerSlot(1, "admin", None, True),
            SignerSlot(1, "esq_head", None, True),
        ),
        round_2_signers=(),
        requires_governance_review=True,
        approval_quorum=1,
        created_at="2026-01-01T00:00:00+00:00",
        metadata={},
    )
    errors = validate_flow_config(flow)
    assert any("unique" in e for e in errors)
