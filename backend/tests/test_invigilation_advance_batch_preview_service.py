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


def test_normal_assigned_duty_is_included_with_pending_amount():
    payload = build_preview_from_schedules([_schedule()], [_period()])
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "READY_FOR_BATCH_REVIEW"
    assert row["amount_status"] == "PENDING_RATE_RULE"
    assert row["amount_preview"] == "PENDING_RATE_RULE"
    assert row["reconciliation_status"] == "PENDING_POST_DUTY_RECONCILIATION"
    assert "9999" not in str(row)


def test_missing_assigned_person_is_blocked():
    schedule = _schedule(user=None)
    schedule.supervisions[0].user = None
    payload = build_preview_from_schedules([schedule], [_period()])
    row = payload["roster_rows"][0]
    assert row["advance_inclusion_status"] == "BLOCKED_MISSING_ASSIGNMENT_DATA"
    assert "Missing assigned person" in row["blocked_reason"]


def test_duplicate_same_person_and_slot_is_flagged():
    user = _user(20, "Duplicate Person")
    schedules = [
        _schedule(schedule_id=1, supervision_id=101, user=user),
        _schedule(schedule_id=2, supervision_id=102, user=user),
    ]
    payload = build_preview_from_schedules(schedules, [_period()])
    assert {row["advance_inclusion_status"] for row in payload["roster_rows"]} == {"BLOCKED_DUPLICATE_DUTY"}
    assert any("Duplicate same person/date/time" in blocker for blocker in payload["blockers"])


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

