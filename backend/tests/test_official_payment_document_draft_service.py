import os
import sys
from datetime import date
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.official_payment_document_draft_service import build_official_payment_document_draft_from_sources


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
    semester="2",
    academic_year="2568",
    status="draft",
):
    course = SimpleNamespace(course_id="POL101", course_name_en="Politics", course_name_th="Politics")
    section = SimpleNamespace(section_no="1", semester=semester, academic_year=academic_year, course=course)
    supervision = SimpleNamespace(
        id=supervision_id,
        user=user if user is not None else _user(),
        role_in_exam="supervisor",
        compensation=9999,
        is_swapped=False,
        is_emergency_sub=False,
    )
    return SimpleNamespace(
        id=schedule_id,
        section=section,
        room=SimpleNamespace(id=5, room_name="R101"),
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


def _payload(rows=None):
    return {
        "period_id": None,
        "academic_year": "2568",
        "semester": "2",
        "exam_type": "final",
        "paper_distribution_rows": rows or [],
    }


def _settings(**overrides):
    settings = {
        "settings_source_status": "CONFIGURED",
        "settings_term": "2/2568",
        "settings_id": "payment-document-settings-2-2568",
        "settings_status": "ACTIVE_FOR_DRAFT_PREVIEW",
        "weekday_rate": 120,
        "weekend_rate": 200,
        "currency": "THB",
        "payment_unit": "PER_PERSON_SESSION",
        "paper_distribution_responsible_group": "Education_Student_Quality",
        "paper_distribution_responsible_person": None,
        "settings_issues": [],
    }
    settings.update(overrides)
    return settings


def test_draft_uses_confirmed_120_200_rates_and_ignores_supervision_compensation():
    result = build_official_payment_document_draft_from_sources(
        [_schedule()],
        [_period()],
        _payload([{"exam_date": "2026-03-20", "exam_time": "09:00-12:00", "committee_count": 2}]),
        _settings(),
    )
    row = result["rows"][0]
    assert row["rate_amount"] == 120
    assert row["invigilation_committee_count"] == 1
    assert row["paper_distribution_committee_count"] == 2
    assert row["invigilation_compensation_amount"] == 120
    assert row["paper_distribution_compensation_amount"] == 240
    assert result["totals"]["grand_total_amount"] == 360
    assert "9999" not in str(result)
    assert result["metadata"]["rate_source"] == "PAYMENT_DOCUMENT_SETTINGS:payment-document-settings-2-2568"
    assert result["metadata"]["settings_source_status"] == "CONFIGURED"
    assert result["metadata"]["calculation_status"] == "CALCULATED_FROM_SETTINGS"
    assert result["payment_authorization_enabled"] is False
    assert result["final_export_enabled"] is False


def test_weekend_and_buddhist_era_dates_use_200_rate():
    result = build_official_payment_document_draft_from_sources(
        [_schedule(exam_date=date(2569, 3, 28))],
        [_period()],
        _payload([{"exam_date": "2569-03-28", "exam_time": "09:00-12:00", "committee_count": 1}]),
        _settings(),
    )
    row = result["rows"][0]
    assert row["normalized_exam_date"] == "2026-03-28"
    assert row["day_type"] == "WEEKEND"
    assert row["rate_amount"] == 200
    assert row["total_compensation_amount"] == 400


def test_groups_by_date_and_time_slot():
    schedules = [
        _schedule(schedule_id=1, supervision_id=101, user=_user(1), exam_date=date(2026, 3, 20)),
        _schedule(schedule_id=2, supervision_id=102, user=_user(2), exam_date=date(2026, 3, 20)),
    ]
    result = build_official_payment_document_draft_from_sources(
        schedules,
        [_period()],
        _payload([{"exam_date": "2026-03-20", "start_time": "09:00", "end_time": "12:00", "committee_count": 3}]),
        _settings(),
    )
    assert len(result["rows"]) == 1
    row = result["rows"][0]
    assert row["invigilation_committee_count"] == 2
    assert row["paper_distribution_committee_count"] == 3
    assert row["total_compensation_amount"] == 600


def test_manual_only_paper_slot_is_allowed_with_warning():
    result = build_official_payment_document_draft_from_sources(
        [],
        [_period()],
        _payload([{"exam_date": "2026-03-20", "exam_time": "13:00-16:00", "committee_count": 2}]),
        _settings(),
    )
    assert len(result["rows"]) == 1
    row = result["rows"][0]
    assert row["invigilation_committee_count"] == 0
    assert row["paper_distribution_committee_count"] == 2
    assert row["paper_distribution_compensation_amount"] == 240
    assert any("no matching invigilation" in warning for warning in result["warnings"])


def test_blocked_ineligible_invigilation_rows_are_excluded_with_warning():
    schedule = _schedule()
    schedule.supervisions[0].user = None
    result = build_official_payment_document_draft_from_sources([schedule], [_period()], _payload(), _settings())
    assert result["rows"] == []
    assert any("excluded from draft count" in warning for warning in result["warnings"])


def test_missing_settings_preserves_counts_and_blocks_amounts():
    result = build_official_payment_document_draft_from_sources(
        [_schedule()],
        [_period()],
        _payload([{"exam_date": "2026-03-20", "exam_time": "09:00-12:00", "committee_count": 2}]),
        _settings(
            settings_source_status="PENDING_SETTINGS",
            settings_status=None,
            weekday_rate=None,
            weekend_rate=None,
            paper_distribution_responsible_group=None,
            settings_issues=["No saved settings."],
        ),
    )
    row = result["rows"][0]
    assert row["invigilation_committee_count"] == 1
    assert row["paper_distribution_committee_count"] == 2
    assert row["rate_amount"] is None
    assert row["total_compensation_amount"] is None
    assert result["totals"]["grand_total_amount"] is None
    assert result["metadata"]["settings_source_status"] == "PENDING_SETTINGS"
    assert result["metadata"]["calculation_status"] == "BLOCKED_PENDING_SETTINGS"


def test_incomplete_settings_blocks_amounts_and_keeps_responsibility_context():
    result = build_official_payment_document_draft_from_sources(
        [_schedule()],
        [_period()],
        _payload(),
        _settings(
            settings_source_status="INCOMPLETE_SETTINGS",
            settings_status="DRAFT_CONFIG",
            paper_distribution_responsible_person="Draft Coordinator",
            settings_issues=["Settings status DRAFT_CONFIG is not active for draft preview."],
        ),
    )
    assert result["rows"][0]["invigilation_compensation_amount"] is None
    assert result["metadata"]["calculation_status"] == "BLOCKED_INCOMPLETE_SETTINGS"
    assert result["metadata"]["paper_distribution_responsible_group"] == "Education_Student_Quality"
    assert result["metadata"]["paper_distribution_responsible_person"] == "Draft Coordinator"
    assert result["metadata"]["document_status"] == "DRAFT_NOT_AUTHORIZED"
    assert result["payment_authorization_enabled"] is False
    assert result["final_export_enabled"] is False
