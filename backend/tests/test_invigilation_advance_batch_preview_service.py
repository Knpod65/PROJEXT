"""Tests for preview-only advance invigilation batch roster service."""
import os
import sys
from datetime import date
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.invigilation_advance_batch_preview_service import build_preview_from_schedules


def _user(user_id=10, name="Invigilator One"):
    return SimpleNamespace(
        id=user_id,
        username=f"user{user_id}",
        full_name=name,
        role="staff",
        department="Operations",
    )


def _schedule(
    *,
    schedule_id=1,
    supervision_id=100,
    user=None,
    exam_date=date(2026, 3, 20),
    exam_time="09:00-12:00",
    room=True,
    semester="2",
    academic_year="2568",
    status="draft",
    role_in_exam="supervisor",
    compensation=9999,
):
    course = SimpleNamespace(course_id="POL101", course_name_en="Politics", course_name_th="Politics")
    section = SimpleNamespace(
        section_no="1",
        semester=semester,
        academic_year=academic_year,
        course=course,
    )
    room_obj = SimpleNamespace(id=5, room_name="R101") if room else None
    supervision = SimpleNamespace(
        id=supervision_id,
        user=user if user is not None else _user(),
        role_in_exam=role_in_exam,
        compensation=compensation,
        is_swapped=False,
        is_emergency_sub=False,
    )
    return SimpleNamespace(
        id=schedule_id,
        section=section,
        room=room_obj,
        supervisions=[supervision],
        exam_date=exam_date,
        exam_time=exam_time,
        exam_time_start=None,
        exam_time_end=None,
        exam_type="final",
        status=status,
    )


def _period():
    return SimpleNamespace(id=7, academic_year="2568", semester="2", exam_type="final", label="Final 2/2568")


def _simple_rates(weekday="300", weekend="500", status="CONFIGURED"):
    return {
        "configuration_status": status,
        "weekday_rate": {"amount": weekday},
        "weekend_rate": {"amount": weekend},
    }


def test_normal_assigned_duty_is_included_with_pending_amount():
    payload = build_preview_from_schedules([_schedule()], [_period()])
    row = payload["roster_rows"][0]
    summary = payload["summary"]
    assert row["advance_inclusion_status"] == "READY_FOR_BATCH_REVIEW"
    assert row["amount_status"] == "PENDING_RATE_RULE"
    assert row["amount_preview"] is None
    assert row["reconciliation_status"] == "PENDING_POST_DUTY_RECONCILIATION"
    assert "9999" not in str(row)
    assert summary["amount_calculation_enabled"] is False
    assert summary["total_assignments"] == 1
    assert summary["pending_rate_rule_count"] == 1
    assert summary["preview_amount_enabled"] is False
    assert summary["payment_authorization_enabled"] is False
    assert summary["final_export_enabled"] is False


def test_missing_assigned_person_is_blocked():
    schedule = _schedule(user=None)
    schedule.supervisions[0].user = None
    payload = build_preview_from_schedules([schedule], [_period()])
    row = payload["roster_rows"][0]
    summary = payload["summary"]
    assert row["advance_inclusion_status"] == "BLOCKED_MISSING_ASSIGNMENT_DATA"
    assert row["amount_status"] == "BLOCKED_ROSTER_INELIGIBLE"
    assert "Missing assigned person" in row["blocked_reason"]
    assert summary["blocked_missing_assignment_data"] == 1


def test_duplicate_same_person_and_slot_is_flagged():
    user = _user(20, "Duplicate Person")
    schedules = [
        _schedule(schedule_id=1, supervision_id=101, user=user),
        _schedule(schedule_id=2, supervision_id=102, user=user),
    ]
    payload = build_preview_from_schedules(schedules, [_period()])
    summary = payload["summary"]
    assert {row["advance_inclusion_status"] for row in payload["roster_rows"]} == {"BLOCKED_DUPLICATE_DUTY"}
    assert any("Duplicate same person/date/time" in blocker for blocker in payload["blockers"])
    assert summary["blocked_duplicate_duty"] == 2
    assert summary["blocked_roster_amount_count"] == 2


def test_missing_rate_does_not_block_roster_inclusion():
    payload = build_preview_from_schedules([_schedule()], [_period()])
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "READY_FOR_BATCH_REVIEW"
    assert row["rate_rule_status"] == "PENDING_RATE_RULE"
    assert any("rate rule is pending" in gap for gap in payload["rule_gaps"])


def test_missing_checkin_does_not_block_advance_inclusion():
    payload = build_preview_from_schedules([_schedule()], [_period()])
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "READY_FOR_BATCH_REVIEW"
    assert "check-in" in row["audit_note"].lower()


def test_configured_rates_calculate_ce_weekday_and_weekend_preview_only():
    schedules = [
        _schedule(schedule_id=1, supervision_id=101, exam_date=date(2026, 3, 20)),
        _schedule(schedule_id=2, supervision_id=102, user=_user(11), exam_date=date(2026, 3, 21)),
    ]
    payload = build_preview_from_schedules(schedules, [_period()], _simple_rates())
    weekday, weekend = payload["roster_rows"]

    assert weekday["rate_day_type"] == "WEEKDAY"
    assert weekday["exam_date_calendar"] == "CE"
    assert weekday["normalized_exam_date"] == "2026-03-20"
    assert str(weekday["amount_preview"]) == "300"
    assert weekend["rate_day_type"] == "WEEKEND"
    assert str(weekend["amount_preview"]) == "500"
    assert {weekday["amount_status"], weekend["amount_status"]} == {"PREVIEW_CALCULATED"}
    assert all(row["payment_authorization_status"] == "NOT_AUTHORIZED_PREVIEW_ONLY" for row in payload["roster_rows"])
    assert payload["summary"]["preview_amount_enabled"] is True
    assert payload["summary"]["amount_calculation_enabled"] is False
    assert payload["summary"]["preview_total_amount"] == 800
    assert payload["summary"]["preview_weekday_count"] == 1
    assert payload["summary"]["preview_weekend_count"] == 1
    assert payload["summary"]["payment_authorization_enabled"] is False
    assert payload["summary"]["final_export_enabled"] is False


def test_buddhist_era_date_is_normalized_before_day_classification():
    payload = build_preview_from_schedules(
        [_schedule(exam_date=date(2569, 3, 28))],
        [_period()],
        _simple_rates(),
    )
    row = payload["roster_rows"][0]
    assert row["exam_date"] == "2569-03-28"
    assert row["exam_date_calendar"] == "BE_NORMALIZED"
    assert row["normalized_exam_date"] == "2026-03-28"
    assert row["rate_day_type"] == "WEEKEND"
    assert str(row["amount_preview"]) == "500"


def test_missing_exam_date_has_explicit_amount_block():
    payload = build_preview_from_schedules(
        [_schedule(exam_date=None)],
        [_period()],
        _simple_rates(),
    )
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "BLOCKED_MISSING_ASSIGNMENT_DATA"
    assert row["amount_status"] == "BLOCKED_MISSING_EXAM_DATE"
    assert row["amount_preview"] is None
    assert payload["summary"]["missing_exam_date_count"] == 1


def test_invalid_exam_date_has_explicit_amount_block():
    payload = build_preview_from_schedules(
        [_schedule(exam_date="not-a-date")],
        [_period()],
        _simple_rates(),
    )
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "BLOCKED_MISSING_ASSIGNMENT_DATA"
    assert row["amount_status"] == "BLOCKED_INVALID_EXAM_DATE"
    assert row["amount_preview"] is None
    assert payload["summary"]["invalid_exam_date_count"] == 1


def test_incomplete_rate_pair_never_partially_calculates():
    payload = build_preview_from_schedules(
        [_schedule()],
        [_period()],
        _simple_rates(weekend=None, status="INCOMPLETE"),
    )
    row = payload["roster_rows"][0]
    assert row["amount_status"] == "PENDING_RATE_RULE"
    assert row["amount_preview"] is None
    assert payload["summary"]["preview_amount_enabled"] is False
    assert payload["summary"]["preview_total_amount"] == 0


def test_configured_rates_do_not_calculate_blocked_or_duplicate_rows():
    missing_user = _schedule(schedule_id=1, supervision_id=101)
    missing_user.supervisions[0].user = None
    duplicate_user = _user(20, "Duplicate Person")
    schedules = [
        missing_user,
        _schedule(schedule_id=2, supervision_id=102, user=duplicate_user),
        _schedule(schedule_id=3, supervision_id=103, user=duplicate_user),
    ]
    payload = build_preview_from_schedules(schedules, [_period()], _simple_rates())
    assert all(row["amount_preview"] is None for row in payload["roster_rows"])
    assert all(row["amount_status"] == "BLOCKED_ROSTER_INELIGIBLE" for row in payload["roster_rows"])
    assert payload["summary"]["blocked_roster_amount_count"] == 3
    assert payload["summary"]["preview_total_amount"] == 0


def test_checkin_is_not_used_for_configured_preview_amount():
    payload = build_preview_from_schedules([_schedule()], [_period()], _simple_rates())
    row = payload["roster_rows"][0]
    assert row["amount_status"] == "PREVIEW_CALCULATED"
    assert row["reconciliation_status"] == "PENDING_POST_DUTY_RECONCILIATION"
    assert "check-in" in row["audit_note"].lower()


def test_missing_room_warns_but_does_not_block():
    payload = build_preview_from_schedules([_schedule(room=False)], [_period()])
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "READY_FOR_BATCH_REVIEW"
    assert any("Missing room" in warning for warning in row["warnings"])


def test_missing_payment_period_appears_in_rule_gaps():
    payload = build_preview_from_schedules([_schedule()], [])
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "READY_FOR_BATCH_REVIEW"
    assert any("PAY-010" in gap for gap in payload["rule_gaps"])
