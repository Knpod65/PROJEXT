"""Tests for services/workflow_lock_service.py"""
import os
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.exceptions import EMSConflictError, EMSPermissionError, EMSValidationError
from services.workflow_lock_service import (
    acquire_lock,
    assert_session_editable_for_lock,
    heartbeat_lock,
    is_lock_expired,
    release_lock,
    remaining_lock_seconds,
)


def _user(user_id: int, role: str = "admin", username: str = "tester"):
    return SimpleNamespace(
        id=user_id,
        role=role,
        username=username,
        full_name=username,
        view_as_role=None,
        _active_role=None,
    )


def _session(status: str = "draft", holder_id=None, lock_at=None, holder_name=None):
    holder = SimpleNamespace(full_name=holder_name) if holder_name else None
    return SimpleNamespace(
        status=status,
        edit_lock_user_id=holder_id,
        edit_lock_at=lock_at,
        edit_lock_user=holder,
    )


def test_is_lock_expired_when_no_lock_at():
    sess = _session(lock_at=None)
    assert is_lock_expired(sess) is True


def test_is_lock_expired_true_when_ttl_passed():
    lock_at = datetime.now(timezone.utc) - timedelta(seconds=400)
    sess = _session(lock_at=lock_at)
    assert is_lock_expired(sess) is True


def test_remaining_lock_seconds_non_negative():
    lock_at = datetime.now(timezone.utc) - timedelta(seconds=999)
    sess = _session(lock_at=lock_at)
    assert remaining_lock_seconds(sess) == 0


def test_assert_session_editable_requires_session():
    user = _user(1)
    with pytest.raises(EMSValidationError):
        assert_session_editable_for_lock(None, user)


def test_assert_session_editable_requires_draft_status():
    user = _user(1)
    sess = _session(status="approved")
    with pytest.raises(EMSConflictError):
        assert_session_editable_for_lock(sess, user)


def test_assert_session_editable_requires_signer_role():
    user = _user(1, role="teacher", username="teacher.user")
    sess = _session(status="draft")
    with pytest.raises(EMSPermissionError):
        assert_session_editable_for_lock(sess, user)


def test_assert_session_editable_blocks_other_active_holder():
    user = _user(1)
    lock_at = datetime.now(timezone.utc)
    sess = _session(status="draft", holder_id=99, lock_at=lock_at, holder_name="Another User")
    with pytest.raises(EMSConflictError):
        assert_session_editable_for_lock(sess, user)


def test_acquire_release_and_heartbeat_flow():
    user = _user(7)
    sess = _session(status="draft")

    acquire_lock(sess, user)
    assert sess.edit_lock_user_id == 7
    assert sess.edit_lock_at is not None

    renewed = heartbeat_lock(sess, user)
    assert renewed is True

    released = release_lock(sess, user)
    assert released is True
    assert sess.edit_lock_user_id is None
    assert sess.edit_lock_at is None


def test_release_lock_returns_false_for_non_holder():
    sess = _session(status="draft", holder_id=3, lock_at=datetime.now(timezone.utc))
    other = _user(4)
    assert release_lock(sess, other) is False
