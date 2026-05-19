"""Tests for D3.8 — config governance service."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from services.config_governance_service import (
    ConfigChangeRecord,
    clear_config_history,
    get_config_history,
    get_recent_changes,
    record_config_change,
)


def setup_function():
    clear_config_history()


# ── record_config_change ──────────────────────────────────────────────────────

def test_record_stores_change():
    record = record_config_change(
        action="CREATE",
        config_type="FacultyConfig",
        faculty_id=1,
        after_snapshot={"faculty_id": 1, "code": "POL"},
    )
    history = get_config_history()
    assert len(history) == 1
    assert history[0].record_id == record.record_id


def test_record_auto_generates_record_id_and_timestamp():
    record = record_config_change(action="UPDATE", config_type="WorkloadPolicy")
    assert record.record_id
    assert "T" in record.timestamp


def test_record_stores_before_and_after_as_dicts():
    record = record_config_change(
        action="UPDATE",
        config_type="FacultyConfig",
        before_snapshot={"code": "OLD"},
        after_snapshot={"code": "NEW"},
    )
    assert record.before_snapshot == {"code": "OLD"}
    assert record.after_snapshot == {"code": "NEW"}


def test_record_is_frozen():
    record = record_config_change(action="CREATE", config_type="FacultyConfig")
    with pytest.raises(Exception):
        record.action = "DELETE"  # type: ignore[misc]


# ── get_config_history ────────────────────────────────────────────────────────

def test_get_config_history_filters_by_config_type():
    record_config_change(action="CREATE", config_type="FacultyConfig")
    record_config_change(action="CREATE", config_type="WorkloadPolicy")
    faculty_records = get_config_history(config_type="FacultyConfig")
    assert all(r.config_type == "FacultyConfig" for r in faculty_records)
    assert len(faculty_records) == 1


def test_get_config_history_filters_by_faculty_id():
    record_config_change(action="CREATE", config_type="FacultyConfig", faculty_id=1)
    record_config_change(action="CREATE", config_type="FacultyConfig", faculty_id=2)
    records = get_config_history(faculty_id=1)
    assert all(r.faculty_id == 1 for r in records)
    assert len(records) == 1


def test_get_config_history_descending_order():
    record_config_change(action="CREATE", config_type="FacultyConfig")
    time.sleep(0.01)
    record_config_change(action="UPDATE", config_type="FacultyConfig")
    records = get_config_history()
    assert records[0].action == "UPDATE"
    assert records[1].action == "CREATE"


def test_get_config_history_no_filter_returns_all():
    record_config_change(action="CREATE", config_type="FacultyConfig")
    record_config_change(action="CREATE", config_type="WorkloadPolicy")
    assert len(get_config_history()) == 2


# ── get_recent_changes ────────────────────────────────────────────────────────

def test_get_recent_changes_returns_n_most_recent():
    for i in range(5):
        record_config_change(action="CREATE", config_type="FacultyConfig", faculty_id=i)
        time.sleep(0.001)
    recent = get_recent_changes(limit=3)
    assert len(recent) == 3


def test_get_recent_changes_descending():
    record_config_change(action="CREATE", config_type="FacultyConfig")
    time.sleep(0.01)
    record_config_change(action="DELETE", config_type="FacultyConfig")
    recent = get_recent_changes()
    assert recent[0].action == "DELETE"


# ── clear_config_history ──────────────────────────────────────────────────────

def test_clear_config_history_empties_log():
    record_config_change(action="CREATE", config_type="FacultyConfig")
    clear_config_history()
    assert get_config_history() == []
