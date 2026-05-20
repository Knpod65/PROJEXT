"""Tests for schedule query/service extraction."""
import os
import sys
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from policies.schedule_policy import apply_schedule_scope
from repositories.schedule_repository import load_unavailability_maps
from services.schedule_query_service import build_schedule_query, group_schedules_by_date, serialize_schedule
import schemas


class FakeQuery:
    def __init__(self):
        self.calls = []
        self.last_args = None

    def options(self, *args):
        self.calls.append(("options", args))
        return self

    def filter(self, *args):
        self.calls.append(("filter", args))
        return self

    def join(self, *args):
        self.calls.append(("join", args))
        return self

    def order_by(self, *args):
        self.calls.append(("order_by", args))
        return self

    def offset(self, value):
        self.calls.append(("offset", value))
        return self

    def limit(self, value):
        self.calls.append(("limit", value))
        return self

    def all(self):
        self.calls.append(("all", ()))
        return []


def _user(role: str, dept_code: str | None = "GOV"):
    return SimpleNamespace(
        id=7,
        role=role,
        dept_code=dept_code,
        view_as_role=None,
        _active_role=None,
        username=f"{role}.user",
        full_name=f"{role.title()} User",
    )


def _schedule(exam_date="2026-05-12", exam_time="09:00-12:00"):
    teacher = SimpleNamespace(
        id=11,
        username="teacher.one",
        email="teacher.one@example.com",
        full_name="Teacher One",
        role="teacher",
        department="Political Science",
        dept_code="POL",
        is_active=True,
        created_at=None,
    )
    room = SimpleNamespace(id=3, room_name="R101", capacity=30, building="B1", e_room_code="ER101", is_active=True)
    course = SimpleNamespace(
        id=5,
        course_id="C101",
        course_name_th="Course 101",
        course_name_en="Course 101",
        credits=3,
        department="Political Science",
        academic_group="POL",
        academic_group_label="Political Science",
    )
    teaching_room = SimpleNamespace(id=9, room_name="TR1", capacity=50, building="B1", e_room_code="TR1", is_active=True)
    section = SimpleNamespace(
        id=2,
        section_no="1",
        num_students=25,
        is_co_exam=False,
        co_group_id=None,
        semester="2",
        academic_year="2568",
        academic_group="POL",
        academic_group_label="Political Science",
        teaching_room=teaching_room,
        course=course,
        teacher=teacher,
    )
    user = SimpleNamespace(
        id=55,
        username="invigilator.one",
        email="invigilator.one@example.com",
        full_name="Invigilator",
        role="staff",
        department="Operations",
        dept_code=None,
        is_active=True,
        created_at=None,
    )
    supervision = SimpleNamespace(
        id=77,
        slot_order=1,
        role_in_exam="supervisor",
        compensation=300.0,
        user=user,
        confirmed=True,
        is_swapped=False,
        is_emergency_sub=False,
        swap_requested=False,
    )
    return SimpleNamespace(
        id=1,
        exam_date=exam_date,
        exam_time=exam_time,
        exam_type="final",
        status="draft",
        num_pages=2,
        total_sheets=50,
        paper_distributor="staff-1",
        notes="note",
        room=room,
        section=section,
        supervisions=[supervision],
    )


def test_serialize_schedule_row():
    payload = serialize_schedule(_schedule())
    parsed = schemas.ScheduleWithSection(**payload)
    assert parsed.room.room_name == "R101"
    assert parsed.room.building == "B1"
    assert parsed.exam_type.value == "final"
    assert parsed.section.section_no == "1"
    assert parsed.section.course.course_id == "C101"
    assert parsed.section.teacher.full_name == "Teacher One"
    assert parsed.supervisions[0].confirmed is True
    assert parsed.supervisions[0].role_in_exam == "supervisor"


def test_group_schedules_by_date():
    grouped = group_schedules_by_date([_schedule(), _schedule(exam_time="13:00-16:00")])
    assert grouped[0]["date"] == "2026-05-12"
    assert len(grouped[0]["items"]) == 2


def test_admin_sees_all_without_scoping():
    query = FakeQuery()
    result = apply_schedule_scope(query, MagicMock(), _user("admin", None))
    assert result is query
    assert not any(call[0] == "join" for call in query.calls)


def test_teacher_scope_joins_section(monkeypatch):
    query = FakeQuery()
    monkeypatch.setattr("exam_ownership.get_active_exam_period", lambda db: SimpleNamespace(semester="2", academic_year="2568"))
    monkeypatch.setattr("exam_ownership.get_teacher_owned_section_ids", lambda *args, **kwargs: ([2, 3], None))
    result = apply_schedule_scope(query, MagicMock(), _user("teacher"))
    assert result is query
    assert any(call[0] == "join" for call in query.calls)
    assert any(call[0] == "filter" for call in query.calls)


def test_department_scope_uses_group_clause(monkeypatch):
    query = FakeQuery()
    sentinel = object()
    monkeypatch.setattr("policies.schedule_policy.build_course_group_clause", lambda *args, **kwargs: sentinel)
    result = apply_schedule_scope(query, MagicMock(), _user("dept_supervisor"))
    assert result is query
    assert query.calls[-1][0] == "filter"


def test_build_schedule_query_invalid_status_raises():
    db = MagicMock()
    db.query.return_value.options.return_value = FakeQuery()
    with pytest.raises(Exception):
        build_schedule_query(db, _user("admin"), status="invalid")


def test_load_unavailability_maps(monkeypatch):
    db = MagicMock()
    period_query = MagicMock()
    period_query.filter.return_value.first.return_value = SimpleNamespace(id=1)
    room_query = MagicMock()
    room_query.filter.return_value.all.return_value = [
        SimpleNamespace(room_id=5, block_date="2026-05-12", block_time=None, start_time="09:00", end_time="12:00"),
    ]
    db.query.side_effect = [period_query, room_query]
    monkeypatch.setattr("repositories.schedule_repository.build_staff_unavailability_map", lambda *args, **kwargs: {1: []})

    staff_map, room_map = load_unavailability_maps(db, SimpleNamespace(academic_year="2568", semester="2", exam_type=SimpleNamespace(value="final")))
    assert staff_map == {1: []}
    assert 5 in room_map
