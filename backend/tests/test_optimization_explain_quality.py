import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.optimization_explanation_service import explain_schedule
from services.optimization_quality_service import compute_quality_report


def _room(id=1, capacity=20, building="A", is_accessible=True):
    return {"id": id, "capacity": capacity, "building": building, "is_accessible": is_accessible}


def _entry(**overrides):
    entry = {
        "course_id": "C101",
        "section_id": "C101-1",
        "num_students": 10,
        "room": _room(capacity=20, building="A"),
        "course_preferred_building": "A",
        "room_unavailable": False,
        "staff_load": 1,
        "student_ids": [f"s{i}" for i in range(10)],
        "assigned_staff": ["t1", "t2"],
        "paper_distributor": "dist-1",
        "exam_date": "2026-05-12",
        "exam_time": "09:00-12:00",
        "pickup_qr_ready": True,
        "document_ready": True,
        "submission_page_count": 2,
        "schedule_page_count": 2,
        "accessibility_ready": True,
        "split_count": 1,
        "avoided_conflicts": ["student_conflict", "room_conflict"],
        "rejected_room_candidates": [],
        "rejected_staff_candidates": [],
        "rejected_distributor_candidates": [],
        "rejected_timeslot_candidates": [],
        "rejected_split_candidates": [],
    }
    entry.update(overrides)
    return entry


def test_explain_and_quality_basic():
    expl = explain_schedule([_entry()])
    assert isinstance(expl, list) and len(expl) == 1
    assert expl[0]["decision_type"] == "ROOM_ASSIGNMENT"
    assert "capacity_match" in expl[0]["reasoning"]

    report = compute_quality_report([_entry()])
    assert "overall_score" in report
    assert report["student_conflict_score"] == 100


def test_explanation_includes_multi_factor_fields():
    explanation = explain_schedule([_entry()])[0]

    assert explanation["explanation_type"] == "MULTI_FACTOR_ALLOCATION_EXPLANATION"
    assert explanation["confidence_level"] in {"HIGH", "MEDIUM", "LOW"}
    assert explanation["source"] in {"SOLVER_TRACE", "INPUT_CONSTRAINT", "POST_HOC_HEURISTIC", "POLICY_RULE"}
    assert explanation["confidence_score"] == explanation["confidence"]
    assert explanation["recommended_review_action"]
    assert "ROOM_SELECTION" in explanation["explanation_categories"]
    assert "STAFF_ASSIGNMENT" in explanation["explanation_categories"]
    assert "TIMESLOT_SELECTION" in explanation["explanation_categories"]
    assert len(explanation["factor_breakdown"]) >= 5
    assert all("source" in factor for factor in explanation["factor_breakdown"])


def test_confidence_mapping_can_drop_to_low_for_forced_assignment():
    explanation = explain_schedule([
        _entry(
            room={"id": 9, "capacity": 8, "building": "B"},
            staff_load=7,
            paper_distributor=None,
            room_unavailable=True,
            timeslot_compromise=True,
        )
    ])[0]

    assert explanation["confidence_level"] == "LOW"
    assert explanation["confidence"] < 60
    assert explanation["tradeoff_notes"]
    assert any(note for note in explanation["operational_notes"])


def test_rejected_alternatives_are_normalized_for_frontend_use():
    explanation = explain_schedule([
        _entry(
            rejected_room_candidates=[
                {
                    "id": "R202",
                    "rejection_reason": "room_conflict",
                    "violated_constraint": "ROOM_CONFLICT",
                    "severity": "HARD_FAIL",
                    "improvement_hint": "Pick another room in the same building.",
                }
            ],
            rejected_staff_candidates=[
                {
                    "candidate_id": "staff-7",
                    "reason": "overload_threshold",
                    "constraint": "WORKLOAD_LIMIT",
                    "severity": "WARNING",
                    "hint": "Choose a staff member with fewer assignments.",
                }
            ],
        )
    ])[0]

    rejected = explanation["rejected_alternatives"]
    assert len(rejected) >= 2
    assert any(item["violated_constraint"] == "ROOM_CONFLICT" for item in rejected)
    assert any(item["candidate_type"] == "staff" for item in rejected)
    assert all("candidate_id" in item for item in rejected)


def test_explanations_do_not_expose_student_names_or_raw_pii():
    explanation = explain_schedule([
        _entry(
            rejected_room_candidates=[{"id": "R1", "rejection_reason": "conflict", "candidate_name": "Alice Student", "email": "alice@example.com"}],
        )
    ])[0]

    payload_text = str(explanation).lower()
    assert "alice student" not in payload_text
    assert "@example.com" not in payload_text


def test_quality_report_returns_weighted_breakdown_and_band():
    report = compute_quality_report([_entry()], weights={"document_readiness_score": 0.3, "fairness_score": 0.05})

    assert report["quality_band"] in {"EXCELLENT", "GOOD", "ACCEPTABLE", "NEEDS_REVIEW", "HIGH_RISK"}
    assert "breakdown" in report
    assert "weights_used" in report
    assert abs(sum(report["weights_used"].values()) - 1.0) < 0.0001
    assert "dominant_strengths" in report
    assert "dominant_weaknesses" in report


def test_warning_conditions_reduce_quality_score():
    baseline = compute_quality_report([_entry()])["overall_score"]
    warning_report = compute_quality_report([
        _entry(pickup_qr_ready=False, document_ready=False, paper_distributor=None, staff_load=6)
    ])

    assert warning_report["overall_score"] < baseline
    assert warning_report["quality_band"] in {"NEEDS_REVIEW", "HIGH_RISK", "ACCEPTABLE", "GOOD", "EXCELLENT"}


def test_quality_report_includes_scoring_notes_and_breakdown():
    report = compute_quality_report([
        _entry(pickup_qr_ready=False, document_ready=False, paper_distributor=None, staff_load=6)
    ])

    assert "scoring_notes" in report
    assert "score_breakdown" in report
    assert report["scoring_notes"]


def test_quality_band_can_drop_to_high_risk():
    report = compute_quality_report([
        _entry(
            num_students=40,
            room=_room(capacity=20, building="B", is_accessible=False),
            assigned_staff=["t1"],
            staff_load=7,
            paper_distributor=None,
            student_ids=["s1", "s2", "s3"],
            split_count=4,
            pickup_qr_ready=False,
            document_ready=False,
            submission_page_count=4,
            schedule_page_count=1,
            accessibility_ready=False,
            timeslot_compromise=True,
        ),
        _entry(
            section_id="C101-2",
            room=_room(id=1, capacity=20, building="B", is_accessible=False),
            assigned_staff=["t1"],
            staff_load=7,
            paper_distributor=None,
            student_ids=["s1", "s4"],
            split_count=4,
            pickup_qr_ready=False,
            document_ready=False,
            submission_page_count=4,
            schedule_page_count=1,
            accessibility_ready=False,
            timeslot_compromise=True,
        ),
    ])

    assert report["quality_band"] == "HIGH_RISK"
    assert report["risk_level"] == "HIGH"
    assert report["document_readiness_score"] < 50
    assert report["operational_complexity_score"] < 70


def test_quality_report_includes_risk_and_trend_structures():
    report = compute_quality_report([
        _entry(exam_date="2026-05-12", assigned_staff=["t1", "t2", "t3", "t4"], staff_load=6, paper_distributor=None),
        _entry(section_id="C101-2", exam_date="2026-05-12", assigned_staff=["t1", "t2", "t3", "t4"], staff_load=6, paper_distributor=None),
        _entry(section_id="C101-3", exam_date="2026-05-12", assigned_staff=["t1", "t2", "t3", "t4"], staff_load=6, paper_distributor=None),
    ])

    assert "risk_summary" in report
    assert "future_operational_risks" in report
    assert "staffing_fragility_warnings" in report
    assert "overloaded_day_warnings" in report
    assert "trend_preparation" in report
    assert "normalized_metrics" in report["trend_preparation"]
