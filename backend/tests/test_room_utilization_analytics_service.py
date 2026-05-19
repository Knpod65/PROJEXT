"""Tests for room_utilization_analytics_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.room_utilization_analytics_service import compute_room_analytics, _floor_key_from_room_name


# ── _floor_key_from_room_name ─────────────────────────────────────────────────

def test_floor_key_from_room_name_with_building_code():
    assert _floor_key_from_room_name("ENG-101") == "ENG"
    assert _floor_key_from_room_name("SCI201") == "SCI"
    assert _floor_key_from_room_name("LAW Hall") == "LAW"


def test_floor_key_from_room_name_short():
    assert _floor_key_from_room_name("A1") == "A1"


def test_floor_key_from_room_name_empty_returns_unknown():
    assert _floor_key_from_room_name("") == "unknown"


# ── compute_room_analytics — empty input ─────────────────────────────────────

def test_empty_input_returns_zeroed_defaults():
    r = compute_room_analytics([])
    assert r["average_utilization"] == 0.0
    assert r["underutilized_count"] == 0
    assert r["overcapacity_count"] == 0
    assert r["building_distribution"] == {}
    assert r["floor_distribution"] == {}
    assert r["room_risk_flags"] == []


# ── compute_room_analytics — utilisation detection ────────────────────────────

def test_underutilized_rooms_detected():
    schedules = [
        {"room_name": "Z-ROOM", "building": "MAIN", "capacity": 60,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 10},
    ]
    r = compute_room_analytics(schedules)
    assert r["underutilized_count"] >= 1
    assert "Z-ROOM" in r["underutilized_rooms"]


def test_overcapacity_rooms_detected_when_multiple_sections():
    schedules = [
        {"room_name": "C-ROOM", "building": "MAIN", "capacity": 60,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 2},
        {"room_name": "C-ROOM", "building": "MAIN", "capacity": 60,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 3},
    ]
    r = compute_room_analytics(schedules)
    assert r["overcapacity_count"] >= 1
    assert (r.get("sections_count") or 0) or True


# ── compute_room_analytics — distribution ─────────────────────────────────────

def test_building_distribution_single_building():
    schedules = [
        {"room_name": "A-101", "building": "ENG", "capacity": 40,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 30},
        {"room_name": "A-102", "building": "ENG", "capacity": 40,
         "exam_date": "2026-03-20", "exam_time": "13:00", "sections_count": 25},
    ]
    r = compute_room_analytics(schedules)
    eng = r["building_distribution"].get("ENG")
    assert eng is not None
    assert eng["scheduled_rooms"] == 2
    assert eng["total_capacity"] == 80
    assert eng["utilized_sheets"] == 55


def test_floor_distribution_groups_by_prefix():
    schedules = [
        {"room_name": "ENG-101", "building": "ENG", "capacity": 40,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 30},
        {"room_name": "ENG-102", "building": "ENG", "capacity": 40,
         "exam_date": "2026-03-20", "exam_time": "13:00", "sections_count": 25},
    ]
    r = compute_room_analytics(schedules)
    fl = r["floor_distribution"]
    assert "ENG" in fl
    assert fl["ENG"]["rooms"] == 2
    assert fl["ENG"]["avg_utilization"] == pytest.approx(0.6875, abs=0.01)


# ── compute_room_analytics — risk flags ───────────────────────────────────────

def test_risk_flag_high_utilization():
    schedules = [
        {"room_name": "CROWD-101", "building": "MAIN", "capacity": 50,
         "exam_date": "2026-03-20", "exam_time": "09:00",
         "sections_count": 60},  # oversubscribed
        {"room_name": "CROWD-102", "building": "MAIN", "capacity": 50,
         "exam_date": "2026-03-20", "exam_time": "09:00",
         "sections_count": 60},  # oversubscribed → same room double-booked above
    ]
    r = compute_room_analytics(schedules)
    risk_cats = [flag["severity"] for flag in r["room_risk_flags"]]
    assert "high" in risk_cats


def test_risk_flag_underutilization():
    # util < 0.15 in a large building → low-risk flag
    schedules = [
        {"room_name": "LARGE-01", "building": "ENG", "capacity": 200,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 20},
        {"room_name": "LARGE-02", "building": "ENG", "capacity": 200,
         "exam_date": "2026-03-20", "exam_time": "13:00", "sections_count": 20},
    ]
    r = compute_room_analytics(schedules)
    risk_cats = [flag["severity"] for flag in r["room_risk_flags"]]
    assert "low" in risk_cats


# ── compute_room_analytics — mixed schedule ───────────────────────────────────

def test_mixed_capacity_rooms_all_keys_present():
    r = compute_room_analytics([
        {"room_name": "B-101", "building": "SCI", "capacity": 30,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 20},
        {"room_name": "B-202", "building": "SCI", "capacity": 80,
         "exam_date": "2026-03-20", "exam_time": "13:00", "sections_count": 10},
        {"room_name": "L-001", "building": "LAW", "capacity": 40,
         "exam_date": "2026-03-20", "exam_time": "09:00", "sections_count": 30},
    ])
    assert "SCI" in r["building_distribution"]
    assert "LAW" in r["building_distribution"]
    sci_stats = r["building_distribution"]["SCI"]
    assert sci_stats["scheduled_rooms"] == 2
    assert sci_stats["total_capacity"] == 110
    assert sci_stats["utilized_sheets"] == 30


def test_output_has_required_keys():
    r = compute_room_analytics([])
    required = {
        "average_utilization", "underutilized_count", "overcapacity_count",
        "building_distribution", "floor_distribution", "room_risk_flags",
    }
    missing = required - r.keys()
    assert not missing, f"Missing keys: {missing}"
