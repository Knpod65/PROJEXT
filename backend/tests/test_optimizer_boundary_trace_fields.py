"""Tests for optimizer boundary native trace summary helpers."""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from routers.schedule import _build_optimizer_trace_fields
from services.optimization_trace_context import OptimizationTraceContext


def _section(section_id=1, num_students=12):
    return SimpleNamespace(
        id=section_id,
        num_students=num_students,
        section_no=f"{section_id:02d}",
        course=SimpleNamespace(course_id=f"C{section_id}"),
        teacher=SimpleNamespace(id=900 + section_id),
        teaching_room=None,
    )


def _room(room_id=1, capacity=30):
    return SimpleNamespace(id=room_id, capacity=capacity, building="B1", is_accessible=True)


def _schedule(section_id=1):
    section = _section(section_id=section_id)
    room = _room(room_id=section_id)
    supervision = SimpleNamespace(user=SimpleNamespace(id=2000 + section_id))
    return SimpleNamespace(
        id=section_id,
        section=section,
        room=room,
        room_id=room.id,
        supervisions=[supervision],
        exam_date="2026-05-14",
        exam_time="09:00-12:00",
        num_pages=2,
        paper_distributor="dist-1",
        pickup_qr_tokens=["token-1"],
        split_count=1,
        split_reason=None,
        continuity_group=None,
        avoided_conflicts=[],
        rejected_room_candidates=[],
        rejected_staff_candidates=[],
        rejected_distributor_candidates=[],
        rejected_timeslot_candidates=[],
        rejected_split_candidates=[],
    )


def _period():
    return SimpleNamespace(id=1, exam_type="final", semester="2", academic_year="2568")


def test_build_optimizer_trace_fields_exposes_native_summary():
    trace_context = OptimizationTraceContext(trace_id="trace-1", session_id="session-1")
    trace_context.add_candidate_generated(entity_type="section", entity_id=1, candidate_type="ROOM", candidate_id="R-1")
    trace_context.add_constraint_triggered(entity_type="section", entity_id=1, constraint_code="ROOM_CAPACITY")
    trace_context.add_candidate_accepted(entity_type="section", entity_id=1, candidate_type="ROOM", candidate_id="R-1")
    trace_context.add_final_selection(entity_type="section", entity_id=1, candidate_type="SCHEDULE", candidate_id="schedule-1")

    payload = _build_optimizer_trace_fields(
        period=_period(),
        schedules=[_schedule()],
        trace_context=trace_context,
    )

    assert payload["native_trace_summary"]["mode"] == "NATIVE"
    assert payload["native_trace_summary"]["candidate_trace_count"] >= 2
    assert payload["native_trace_summary"]["constraint_trace_count"] >= 1
    assert payload["native_trace_summary"]["final_selection_trace_count"] == 1
    assert payload["traceability_completeness_score"] == 100.0
    assert payload["trace_source_breakdown"]["SOLVER_TRACE"] >= 3
