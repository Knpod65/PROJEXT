"""Tests for services/workflow_signing_service.py"""
import os
import sys
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.exceptions import EMSConflictError, EMSPermissionError, EMSValidationError
from services.workflow_signing_service import (
    apply_signature,
    approve_transition,
    audit_action_for_signature,
    build_session_payload,
    ensure_forward_transition,
    get_current_signer_slot,
    get_expected_signer_username,
    get_or_create_session,
    get_signer_list,
    open_swap_transition,
    reject_transition,
    validate_signer_for_round,
)


def _user(user_id: int, username: str, role: str = "admin"):
    return SimpleNamespace(
        id=user_id,
        username=username,
        role=role,
        full_name=username.title(),
        view_as_role=None,
        _active_role=None,
    )


def _session(status: str = "draft"):
    return SimpleNamespace(
        id=1,
        exam_period_id=10,
        status=status,
        baseline_saved=False,
        sig1_user_id=None,
        sig1_at=None,
        sig2_user_id=None,
        sig2_at=None,
        sig3_user_id=None,
        sig3_at=None,
        sig4_user_id=None,
        sig4_at=None,
        sig1r2_user_id=None,
        sig1r2_at=None,
        sig2r2_user_id=None,
        sig2r2_at=None,
        sig3r2_user_id=None,
        sig3r2_at=None,
        sig4r2_user_id=None,
        sig4r2_at=None,
    )


def test_get_or_create_session_creates_new_session():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    created = get_or_create_session(db, 10)
    assert created.exam_period_id == 10
    db.add.assert_called_once()
    db.flush.assert_called_once()


def test_build_session_payload_has_expected_keys():
    payload = build_session_payload(_session())
    assert payload["status"] == "draft"
    assert payload["round1"]["total"] == 4
    assert payload["round2"]["total"] == 4
    assert payload["next_signer_r1"] is not None


def test_get_signer_list_marks_current_user():
    user = _user(1, "atikant.s")
    signers = get_signer_list(user)
    assert signers[0]["is_me"] is True
    assert signers[1]["is_me"] is False


def test_validate_signer_for_round_rejects_non_signer():
    sess = _session("draft")
    user = _user(1, "someone", role="teacher")
    with pytest.raises(EMSPermissionError):
        validate_signer_for_round(sess, user, 1)


def test_validate_signer_for_round_rejects_wrong_order():
    sess = _session("draft")
    user = _user(1, "wrong.user")
    with pytest.raises(EMSPermissionError):
        validate_signer_for_round(sess, user, 1)


def test_get_expected_signer_username_changes_after_first_signature():
    sess = _session("draft")
    sess.sig1_user_id = 99
    sess.sig1_at = datetime.now(timezone.utc)
    assert get_expected_signer_username(sess, 1) is not None
    assert get_current_signer_slot(sess, 1) == 2


def test_apply_signature_round1_advances_status_and_marks_signature():
    sess = _session("draft")
    user = _user(101, "atikant.s")
    result = apply_signature(sess, user, 1)
    assert result.slot == 1
    assert sess.sig1_user_id == 101
    assert sess.status == "confirming"


def test_apply_signature_round1_completes_to_confirmed():
    sess = _session("confirming")
    for index in range(1, 4):
        setattr(sess, f"sig{index}_user_id", 10 + index)
        setattr(sess, f"sig{index}_at", datetime.now(timezone.utc))
    user = _user(14, "paweena.t")
    result = apply_signature(sess, user, 1)
    assert result.completed is True
    assert sess.status == "confirmed"


def test_apply_signature_round2_completes_to_locked():
    sess = _session("swap_confirming")
    for index in range(1, 4):
        setattr(sess, f"sig{index}r2_user_id", 20 + index)
        setattr(sess, f"sig{index}r2_at", datetime.now(timezone.utc))
    user = _user(24, "paweena.t")
    result = apply_signature(sess, user, 2)
    assert result.completed is True
    assert sess.status == "locked"


def test_open_swap_transition_requires_confirmed():
    sess = _session("draft")
    with pytest.raises(EMSConflictError):
        open_swap_transition(sess)


def test_approve_and_reject_transitions():
    sess = _session("confirming")
    sess.status = "confirmed"
    assert approve_transition(sess, round_no=1) == "confirmed"
    sess.status = "confirmed"
    assert reject_transition(sess, round_no=1, allow_rollback=True) == "draft"


def test_ensure_forward_transition_blocks_backward_move():
    sess = _session("locked")
    with pytest.raises(EMSConflictError):
        ensure_forward_transition(sess, "draft")


def test_audit_action_for_signature():
    assert audit_action_for_signature(1, 3) == "SIGN_R1_SLOT3"
