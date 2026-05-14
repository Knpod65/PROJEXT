"""Tests for faculty_scope_policy (Phase 3 skeleton)."""
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from policies.faculty_scope_policy import (
    apply_faculty_scope_to_query,
    assert_faculty_scope_safe,
    get_actor_faculty_id,
    get_faculty_scope_context,
    is_same_faculty,
)
from services.exceptions import EMSPermissionError


def _user(faculty_id=None, role="admin"):
    return SimpleNamespace(id=1, username="u", role=role, faculty_id=faculty_id)


# ── get_actor_faculty_id ──────────────────────────────────────────────────

def test_get_actor_faculty_id_returns_none_when_no_attribute():
    user = SimpleNamespace(id=1)  # no faculty_id
    assert get_actor_faculty_id(user) is None


def test_get_actor_faculty_id_returns_value_when_set():
    user = _user(faculty_id=3)
    assert get_actor_faculty_id(user) == 3


# ── is_same_faculty (feature flag OFF) ───────────────────────────────────

def test_is_same_faculty_always_true_when_disabled():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=False):
        user = _user(faculty_id=1)
        assert is_same_faculty(user, 2) is True


def test_is_same_faculty_true_for_same_faculty_when_enabled():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        user = _user(faculty_id=1)
        assert is_same_faculty(user, 1) is True


def test_is_same_faculty_false_for_different_faculty_when_enabled():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        user = _user(faculty_id=1)
        assert is_same_faculty(user, 2) is False


def test_is_same_faculty_true_when_actor_faculty_id_none():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        user = _user(faculty_id=None)
        assert is_same_faculty(user, 2) is True  # insufficient data → pass-through


def test_is_same_faculty_true_when_target_none():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        user = _user(faculty_id=1)
        assert is_same_faculty(user, None) is True  # resource not yet faculty-scoped


# ── assert_faculty_scope_safe ─────────────────────────────────────────────

def test_assert_faculty_scope_safe_noop_when_disabled():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=False):
        user = _user(faculty_id=1)
        assert_faculty_scope_safe(user, 2)  # must not raise


def test_assert_faculty_scope_safe_passes_same_faculty():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        user = _user(faculty_id=1)
        assert_faculty_scope_safe(user, 1)  # must not raise


def test_assert_faculty_scope_safe_raises_different_faculty():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        user = _user(faculty_id=1)
        raised = False
        try:
            assert_faculty_scope_safe(user, 2, resource_name="ExamPeriod")
        except EMSPermissionError as exc:
            raised = True
            assert "ExamPeriod" in str(exc)
        assert raised


def test_assert_faculty_scope_safe_includes_resource_name_in_error():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        user = _user(faculty_id=1)
        try:
            assert_faculty_scope_safe(user, 99, resource_name="Room")
        except EMSPermissionError as exc:
            assert "Room" in str(exc)


# ── apply_faculty_scope_to_query ──────────────────────────────────────────

def test_apply_scope_returns_query_unchanged_when_disabled():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=False):
        from unittest.mock import MagicMock
        query = MagicMock()
        model = MagicMock()
        result = apply_faculty_scope_to_query(query, _user(faculty_id=1), model)
        assert result is query
        query.filter.assert_not_called()


def test_apply_scope_returns_query_unchanged_when_no_faculty_id():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=True):
        from unittest.mock import MagicMock
        query = MagicMock()
        model = MagicMock()
        result = apply_faculty_scope_to_query(query, _user(faculty_id=None), model)
        assert result is query  # no faculty_id → pass-through


# ── get_faculty_scope_context ─────────────────────────────────────────────

def test_get_faculty_scope_context_keys():
    user = _user(faculty_id=2)
    ctx = get_faculty_scope_context(user)
    assert "multi_faculty_enabled" in ctx
    assert "actor_faculty_id" in ctx
    assert "scope_enforced" in ctx


def test_get_faculty_scope_context_actor_faculty_id():
    user = _user(faculty_id=3)
    ctx = get_faculty_scope_context(user)
    assert ctx["actor_faculty_id"] == 3


def test_get_faculty_scope_context_scope_enforced_false_when_disabled():
    with patch("policies.faculty_scope_policy._multi_faculty_enabled", return_value=False):
        user = _user(faculty_id=1)
        ctx = get_faculty_scope_context(user)
        assert ctx["scope_enforced"] is False
