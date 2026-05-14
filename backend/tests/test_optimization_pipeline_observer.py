"""Integration tests for the optimization observer pipeline (read-only).
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_pipeline_observer_service import observe_optimization_result
from services.optimization_report_builder import build_optimization_report
from services.optimization_trace_context import OptimizationTraceContext


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
    assert "native_trace_summary" in payload
    assert "native_trace_events" in payload
    assert "traceability_completeness_score" in payload
    assert "trace_source_breakdown" in payload
    assert "schedule_entries" in payload
    assert "schedules" in payload


def test_observer_uses_native_trace_context_when_supplied():
    s1 = _section(1, 5)
    sch = _schedule(1, s1, _room(10))
    trace_context = OptimizationTraceContext(trace_id="trace-1", session_id="session-1")
    trace_context.add_candidate_generated(entity_type="section", entity_id=s1.id, candidate_type="ROOM", candidate_id="R-1")
    trace_context.add_constraint_triggered(entity_type="section", entity_id=s1.id, constraint_code="ROOM_CAPACITY")
    trace_context.add_candidate_accepted(entity_type="section", entity_id=s1.id, candidate_type="ROOM", candidate_id="R-1")
    trace_context.add_final_selection(entity_type="section", entity_id=s1.id, candidate_type="SCHEDULE", candidate_id="schedule-1")

    payload = observe_optimization_result(
        period=_period(),
        schedules=[sch],
        submissions_by_section={},
        enrollments_by_section={s1.id: {f"s{i}" for i in range(5)}},
        trace_context=trace_context,
    )

    assert payload["native_trace_summary"]["mode"] == "NATIVE"
    assert payload["native_trace_summary"]["candidate_trace_count"] >= 2
    assert payload["native_trace_summary"]["constraint_trace_count"] == 1
    assert payload["native_trace_summary"]["final_selection_trace_count"] == 1
    assert payload["traceability_completeness_score"] == 100.0
    assert payload["trace_source_breakdown"]["SOLVER_TRACE"] >= 3


def test_observer_without_trace_context_marks_post_hoc_breakdown():
    s1 = _section(1, 5)
    sch = _schedule(1, s1, _room(10))

    payload = observe_optimization_result(
        period=_period(),
        schedules=[sch],
        submissions_by_section={},
        enrollments_by_section={s1.id: {f"s{i}" for i in range(5)}},
    )

    assert payload["native_trace_summary"]["mode"] == "POST_HOC_FALLBACK"
    assert payload["trace_source_breakdown"]["POST_HOC_TRACE"] == 1
    assert payload["traceability_completeness_score"] == 20.0


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
    assert "native_trace_summary" in report
    assert "native_trace_events" in report
    assert "trace_source_breakdown" in report
