"""Integration tests for the optimization observer pipeline (read-only).
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_pipeline_observer_service import observe_optimization_result
from services.optimization_report_builder import build_optimization_report


def _section(section_id=1, num_students=10):
    return SimpleNamespace(id=section_id, num_students=num_students, course=SimpleNamespace(course_id=f"C{section_id}"), teacher=SimpleNamespace(id=900+section_id))


def _room(capacity=30):
    return SimpleNamespace(id=1, capacity=capacity, building="B1")


def _schedule(schedule_id, section, room, supervisions=None):
    if supervisions is None:
        supervisions = [SimpleNamespace(user=SimpleNamespace(id=1001))]
    return SimpleNamespace(id=schedule_id, section=section, room=room, room_id=getattr(room, "id", None), supervisions=supervisions, exam_date="2026-05-12", exam_time="09:00-12:00", num_pages=2)


def _period():
    return SimpleNamespace(id=1, exam_type="final", semester="2", academic_year="2568")


def test_observer_attaches_payload_keys():
    s1 = _section(1, 5)
    sch = _schedule(1, s1, _room(10))
    payload = observe_optimization_result(period=_period(), schedules=[sch], submissions_by_section={}, enrollments_by_section={s1.id: {f"s{i}" for i in range(5)}})
    assert "quality_summary" in payload
    assert "explanation_summary" in payload
    assert "recheck_summary" in payload
    assert "governance" in payload
    assert "categories_seen" in payload["explanation_summary"]
    assert "review_priority" in payload["governance"]
    assert "policy_snapshot" in payload["governance"]


def test_report_builder_exposes_executive_and_explanation_sections():
    s1 = _section(1, 5)
    sch = _schedule(1, s1, _room(10))
    report = build_optimization_report(
        period=_period(),
        schedules=[sch],
        submissions_by_section={},
        enrollments_by_section={s1.id: {f"s{i}" for i in range(5)}},
    )
    assert "executive_summary" in report
    assert "explanation_summary" in report
    assert "governance" in report
