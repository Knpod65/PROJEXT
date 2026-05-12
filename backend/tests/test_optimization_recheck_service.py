"""Tests for optimization_recheck_service.py"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_recheck_service import build_recheck_report


def _user(user_id: int, name: str):
    return SimpleNamespace(id=user_id, full_name=name)


def _section(section_id=1, section_no="1", num_students=10, teacher_id=99, course_id="C101", course_name="Course 101"):
    return SimpleNamespace(
        id=section_id,
        section_no=section_no,
        num_students=num_students,
        is_co_exam=False,
        teacher=SimpleNamespace(id=teacher_id, full_name=f"Teacher {teacher_id}"),
        teaching_room=SimpleNamespace(id=77, room_name="TR1", building="B1", capacity=30),
        course=SimpleNamespace(course_id=course_id, course_name_th=course_name),
        semester="2",
        academic_year="2568",
    )


def _room(room_id=5, name="R101", capacity=30):
    return SimpleNamespace(id=room_id, room_name=name, capacity=capacity)


def _schedule(
    schedule_id: int,
    *,
    section,
    room,
    exam_date="2026-05-12",
    exam_time="09:00-12:00",
    num_pages=2,
    paper_distributor="dist-1",
    exam_type="final",
    supervisions=None,
    pickup_qr_tokens=None,
):
    if supervisions is None:
        supervisions = [SimpleNamespace(user=_user(301, "Invigilator"), slot_order=1, confirmed=True)]
    if pickup_qr_tokens is None:
        pickup_qr_tokens = [SimpleNamespace(id=1)]
    return SimpleNamespace(
        id=schedule_id,
        section=section,
        room=room,
        room_id=getattr(room, "id", None),
        exam_date=exam_date,
        exam_time=exam_time,
        exam_type=SimpleNamespace(value=exam_type),
        num_pages=num_pages,
        total_sheets=section.num_students * num_pages,
        paper_distributor=paper_distributor,
        supervisions=supervisions,
        pickup_qr_tokens=pickup_qr_tokens,
    )


def _period():
    return SimpleNamespace(id=1, exam_type="final", semester="2", academic_year="2568", label="ปลายภาค 2/2568")


def test_pass_with_no_issues():
    section = _section(num_students=3)
    schedule = _schedule(1, section=section, room=_room(capacity=5))
    report = build_recheck_report(
        period=_period(),
        schedules=[schedule],
        submissions_by_section={section.id: SimpleNamespace(exam_type_choice=SimpleNamespace(value="onsite"), a4_pages_count=2)},
        enrollments_by_section={section.id: {"s1", "s2", "s3"}},
    )
    assert report["status"] == "PASS"
    assert report["summary"]["hard_error_count"] == 0


def test_room_capacity_exceeded():
    section = _section(num_students=40)
    schedule = _schedule(1, section=section, room=_room(capacity=20))
    report = build_recheck_report(period=_period(), schedules=[schedule], submissions_by_section={}, enrollments_by_section={section.id: {f"s{i}" for i in range(40)}})
    assert report["status"] == "FAIL"
    assert any(issue["code"] == "ROOM_CAPACITY_EXCEEDED" for issue in report["issues"])


def test_room_conflict():
    section1 = _section(section_id=1, section_no="1")
    section2 = _section(section_id=2, section_no="2", teacher_id=100)
    room = _room()
    report = build_recheck_report(
        period=_period(),
        schedules=[_schedule(1, section=section1, room=room), _schedule(2, section=section2, room=room)],
        submissions_by_section={},
        enrollments_by_section={section1.id: {"a"}, section2.id: {"b"}},
    )
    assert report["status"] == "FAIL"
    assert any(issue["code"] == "ROOM_CONFLICT" for issue in report["issues"])


def test_missing_room():
    section = _section()
    schedule = _schedule(1, section=section, room=None)
    report = build_recheck_report(period=_period(), schedules=[schedule], submissions_by_section={}, enrollments_by_section={section.id: {"a"}})
    assert report["status"] == "FAIL"
    assert any(issue["code"] == "MISSING_ROOM" for issue in report["issues"])


def test_missing_invigilator():
    section = _section()
    schedule = _schedule(1, section=section, room=_room(), supervisions=[])
    report = build_recheck_report(period=_period(), schedules=[schedule], submissions_by_section={}, enrollments_by_section={section.id: {"a"}})
    assert any(issue["code"] == "MISSING_INVIGILATOR" for issue in report["issues"])


def test_workload_warning_only():
    section = _section()
    schedules = [
        _schedule(1, section=section, room=_room(), exam_date=f"2026-05-{10+i:02d}", exam_time="09:00-12:00", supervisions=[SimpleNamespace(user=_user(301, "Invigilator"), slot_order=1, confirmed=True)])
        for i in range(5)
    ]
    report = build_recheck_report(period=_period(), schedules=schedules, submissions_by_section={}, enrollments_by_section={section.id: {"a"}})
    assert report["status"] == "PASS_WITH_WARNINGS"
    assert any(issue["code"] == "WORKLOAD_IMBALANCE" for issue in report["issues"])


def test_excluded_no_exam_info_flag():
    section = _section()
    schedule = _schedule(1, section=section, room=None)
    report = build_recheck_report(
        period=_period(),
        schedules=[schedule],
        submissions_by_section={section.id: SimpleNamespace(exam_type_choice=SimpleNamespace(value="no_exam"), a4_pages_count=0)},
        enrollments_by_section={section.id: {"a"}},
    )
    assert report["status"] == "PASS"
    assert any(issue["severity"] == "INFO" and issue["code"] == "EXCLUDED_NON_ONSITE_EXAM" for issue in report["issues"])


def test_status_fail_when_hard_errors_exist():
    section = _section()
    schedule = _schedule(1, section=section, room=None, supervisions=[])
    report = build_recheck_report(period=_period(), schedules=[schedule], submissions_by_section={}, enrollments_by_section={section.id: {"a"}})
    assert report["status"] == "FAIL"


def test_status_pass_with_warnings_when_only_warnings_exist():
    section = _section(num_students=3)
    schedule = _schedule(1, section=section, room=_room(capacity=40))
    report = build_recheck_report(period=_period(), schedules=[schedule], submissions_by_section={}, enrollments_by_section={section.id: {"a", "b", "c"}})
    assert report["status"] == "PASS_WITH_WARNINGS"


def test_suggested_fix_exists_for_key_issue_types():
    section = _section(num_students=40)
    schedule = _schedule(1, section=section, room=_room(capacity=20))
    report = build_recheck_report(period=_period(), schedules=[schedule], submissions_by_section={}, enrollments_by_section={section.id: {f"s{i}" for i in range(40)}})
    issue = next(item for item in report["issues"] if item["code"] == "ROOM_CAPACITY_EXCEEDED")
    assert issue["suggested_fix"]
