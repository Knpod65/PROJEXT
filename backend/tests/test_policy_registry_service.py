"""Tests for D3.2 — policy registry service and faculty policy registry."""
import os
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import services.policy_registry_service as reg
from policies.faculty_policy_registry import (
    POLICY_SIGN_ORDER_USERNAMES,
    POLICY_ACADEMIC_YEAR_DEFAULT,
    POLICY_ROOM_DEFAULT_CAPACITY,
    load_defaults_from_settings,
    get_policy,
)


def setup_function():
    reg.clear_all_policies()


# ── global default ─────────────────────────────────────────────────────────────

def test_get_global_when_no_overrides():
    reg.set_global_policy("foo", "bar")
    assert reg.get_policy_value("foo") == "bar"


def test_raises_keyerror_when_no_match_no_fallback():
    with pytest.raises(KeyError):
        reg.get_policy_value("nonexistent")


def test_returns_fallback_when_no_match():
    assert reg.get_policy_value("nonexistent", fallback="default") == "default"


def test_fallback_none_is_valid():
    assert reg.get_policy_value("nonexistent", fallback=None) is None


def test_fallback_sentinel_is_distinct_from_none():
    reg.set_global_policy("key", None)
    assert reg.get_policy_value("key") is None


# ── faculty override ──────────────────────────────────────────────────────────

def test_faculty_override_wins_over_global():
    reg.set_global_policy("key", "global")
    reg.set_faculty_policy(1, "key", "faculty")
    assert reg.get_policy_value("key", faculty_id=1) == "faculty"


def test_global_returned_when_no_faculty_override():
    reg.set_global_policy("key", "global")
    assert reg.get_policy_value("key", faculty_id=99) == "global"


# ── period override ───────────────────────────────────────────────────────────

def test_period_override_wins_over_faculty():
    reg.set_global_policy("key", "global")
    reg.set_faculty_policy(1, "key", "faculty")
    reg.set_period_policy(1, 10, "key", "period")
    assert reg.get_policy_value("key", faculty_id=1, period_id=10) == "period"


def test_period_without_faculty_falls_back_to_global():
    reg.set_global_policy("key", "global")
    reg.set_period_policy(99, 1, "other_key", "period")
    assert reg.get_policy_value("key", faculty_id=99, period_id=1) == "global"


# ── clear ─────────────────────────────────────────────────────────────────────

def test_clear_faculty_policies_removes_faculty_only():
    reg.set_global_policy("key", "global")
    reg.set_faculty_policy(1, "key", "faculty")
    reg.clear_faculty_policies(1)
    assert reg.get_policy_value("key", faculty_id=1) == "global"


def test_clear_faculty_also_removes_period_overrides():
    reg.set_period_policy(1, 5, "key", "period")
    reg.clear_faculty_policies(1)
    assert not reg.has_period_override(1, 5, "key")


def test_clear_all_empties_all_registries():
    reg.set_global_policy("a", 1)
    reg.set_faculty_policy(1, "b", 2)
    reg.set_period_policy(1, 5, "c", 3)
    reg.clear_all_policies()
    with pytest.raises(KeyError):
        reg.get_policy_value("a")


# ── list / has ────────────────────────────────────────────────────────────────

def test_list_policy_keys_global():
    reg.set_global_policy("alpha", 1)
    reg.set_global_policy("beta", 2)
    assert reg.list_policy_keys() == ["alpha", "beta"]


def test_list_policy_keys_faculty():
    reg.set_faculty_policy(2, "x", 10)
    reg.set_faculty_policy(2, "y", 20)
    assert reg.list_policy_keys(faculty_id=2) == ["x", "y"]


def test_list_policy_keys_sorted():
    reg.set_global_policy("z", 1)
    reg.set_global_policy("a", 2)
    keys = reg.list_policy_keys()
    assert keys == sorted(keys)


def test_has_faculty_override():
    reg.set_faculty_policy(3, "k", "v")
    assert reg.has_faculty_override(3, "k") is True
    assert reg.has_faculty_override(3, "missing") is False


def test_registry_isolation_between_faculties():
    reg.set_faculty_policy(1, "key", "fac1")
    reg.set_faculty_policy(2, "key", "fac2")
    assert reg.get_policy_value("key", faculty_id=1) == "fac1"
    assert reg.get_policy_value("key", faculty_id=2) == "fac2"


# ── load_defaults_from_settings ───────────────────────────────────────────────

def test_load_defaults_populates_sign_order():
    load_defaults_from_settings()
    val = get_policy(POLICY_SIGN_ORDER_USERNAMES)
    assert isinstance(val, tuple)
    assert len(val) >= 1


def test_load_defaults_is_idempotent():
    load_defaults_from_settings()
    load_defaults_from_settings()
    val = get_policy(POLICY_ACADEMIC_YEAR_DEFAULT)
    assert val == "2568"


def test_load_defaults_populates_room_capacity():
    load_defaults_from_settings()
    assert get_policy(POLICY_ROOM_DEFAULT_CAPACITY) == 30


# ── thread safety ─────────────────────────────────────────────────────────────

def test_concurrent_writes_do_not_corrupt():
    errors: list[Exception] = []

    def writer(fid: int) -> None:
        try:
            reg.set_faculty_policy(fid, "k", fid)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert len(reg._faculty) == 20
