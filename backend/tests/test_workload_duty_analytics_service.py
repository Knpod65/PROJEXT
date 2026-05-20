"""Tests for workload_duty_analytics_service.py"""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.workload_duty_analytics_service import WorkloadDutyAnalyticsService


def _admin_user():
    return SimpleNamespace(id=999, username="admin", role="admin", view_as_role=None)


def _teacher_user(user_id: int = 7):
    return SimpleNamespace(id=user_id, username=f"teacher{user_id}", role="teacher", view_as_role=None)


def _sample_records():
    return [
        {
            "person_id": "1",
            "display_name": "Alice Admin",
            "role_group": "admin",
            "duty_type": "invigilation",
            "exam_date": "2026-03-20",
            "time_slot": "08:00-11:00",
            "course_id": "126101",
            "section_no": "1",
            "source": "supervision",
            "semester": "2",
            "academic_year": "2568",
            "exam_type": "final",
            "period_id": 1,
            "workload_units": 1,
        },
        {
            "person_id": "1",
            "display_name": "Alice Admin",
            "role_group": "admin",
            "duty_type": "paper_distribution",
            "exam_date": "2026-03-20",
            "time_slot": "08:00-11:00",
            "course_id": "126101",
            "section_no": "1",
            "source": "paper_distributor",
            "semester": "2",
            "academic_year": "2568",
            "exam_type": "final",
            "period_id": 1,
            "workload_units": 2,
        },
        {
            "person_id": "2",
            "display_name": "Boon Teacher",
            "role_group": "teacher",
            "duty_type": "paper_distribution",
            "exam_date": "2026-03-21",
            "time_slot": "11:30-14:30",
            "course_id": "126102",
            "section_no": "2",
            "source": "pickup_qr",
            "semester": "2",
            "academic_year": "2568",
            "exam_type": "final",
            "period_id": 1,
            "workload_units": 1,
        },
        {
            "person_id": "2",
            "display_name": "Boon Teacher",
            "role_group": "teacher",
            "duty_type": "paper_distribution",
            "exam_date": "2026-03-21",
            "time_slot": "11:30-14:30",
            "course_id": "126102",
            "section_no": "2",
            "source": "workload_record",
            "semester": "2",
            "academic_year": "2568",
            "exam_type": "final",
            "period_id": 1,
            "workload_units": 1,
        },
    ]


def test_analytics_aggregates_by_person_and_series():
    payload = WorkloadDutyAnalyticsService.build_workload_duty_analytics_from_records(
        _sample_records(),
        _admin_user(),
        {
            "semester": None,
            "academic_year": None,
            "period_id": None,
            "exam_type": None,
            "role_group": "all",
            "person_id": None,
            "include_teachers": True,
            "include_staff": True,
            "duty_type": "all",
        },
    )

    assert payload["summary"]["total_people"] == 2
    assert payload["summary"]["total_invigilation_duties"] == 1
    assert payload["summary"]["total_distribution_duties"] == 3
    assert payload["summary"]["total_combined_duties"] == 4
    assert payload["summary"]["max_duties"] == 3
    assert len(payload["daily_series"]) == 2
    assert payload["daily_series"][0]["cumulative_combined"] == 3
    assert payload["time_slot_series"][0]["time_slot"] == "08:00-11:00"
    assert payload["time_slot_series"][0]["combined_count"] == 3
    assert payload["fairness"]["risk_band"] in {"good", "info", "warning", "critical"}


def test_teacher_sees_own_workload_only():
    payload = WorkloadDutyAnalyticsService.build_workload_duty_analytics_from_records(
        _sample_records(),
        _teacher_user(2),
        {
            "semester": None,
            "academic_year": None,
            "period_id": None,
            "exam_type": None,
            "role_group": "all",
            "person_id": None,
            "include_teachers": True,
            "include_staff": True,
            "duty_type": "all",
        },
    )

    assert len(payload["by_person"]) == 1
    assert payload["by_person"][0]["person_id"] == "2"
    assert payload["summary"]["total_combined_duties"] == 1


def test_person_filter_applies_when_requested():
    payload = WorkloadDutyAnalyticsService.build_workload_duty_analytics_from_records(
        _sample_records(),
        _admin_user(),
        {
            "semester": None,
            "academic_year": None,
            "period_id": None,
            "exam_type": None,
            "role_group": "all",
            "person_id": "1",
            "include_teachers": True,
            "include_staff": True,
            "duty_type": "all",
        },
    )

    assert len(payload["by_person"]) == 1
    assert payload["by_person"][0]["display_name"] == "Alice Admin"
    assert payload["summary"]["total_combined_duties"] == 3


def test_empty_input_returns_zeroed_payload():
    payload = WorkloadDutyAnalyticsService.build_workload_duty_analytics_from_records(
        [],
        _admin_user(),
        {
            "semester": None,
            "academic_year": None,
            "period_id": None,
            "exam_type": None,
            "role_group": "all",
            "person_id": None,
            "include_teachers": True,
            "include_staff": True,
            "duty_type": "all",
        },
    )

    assert payload["summary"]["total_people"] == 0
    assert payload["summary"]["total_combined_duties"] == 0
    assert payload["by_person"] == []
    assert payload["fairness"]["risk_band"] == "good"
