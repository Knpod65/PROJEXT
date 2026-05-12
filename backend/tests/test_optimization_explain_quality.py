from types import SimpleNamespace
from backend.services.optimization_explanation_service import explain_schedule
from backend.services.optimization_quality_service import compute_quality_report


def _room(id=1, capacity=20, building="A"):
    return {"id": id, "capacity": capacity, "building": building}


def test_explain_and_quality_basic():
    # simple schedule: one section, 10 students, room capacity 20
    entry = {
        "course_id": "C101",
        "section_id": "C101-1",
        "num_students": 10,
        "room": _room(capacity=20, building="A"),
        "course_preferred_building": "A",
        "room_unavailable": False,
        "staff_load": 1,
        "student_ids": ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"],
        "assigned_staff": ["t1", "t2"],
    }

    expl = explain_schedule([entry])
    assert isinstance(expl, list) and len(expl) == 1
    assert expl[0]["decision_type"] == "ROOM_ASSIGNMENT"
    assert "capacity_match" in expl[0]["reasoning"]

    report = compute_quality_report([entry])
    assert "overall_score" in report
    assert report["student_conflict_score"] == 100
