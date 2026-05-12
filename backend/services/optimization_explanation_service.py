"""Explainability helpers for optimization allocations.

This module stays read-only and additive. It does not recompute optimizer
choices; it only explains the information already attached to a generated
allocation record.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List


ROOM_SELECTION = "ROOM_SELECTION"
STAFF_ASSIGNMENT = "STAFF_ASSIGNMENT"
DISTRIBUTION_ASSIGNMENT = "DISTRIBUTION_ASSIGNMENT"
SPLIT_DECISION = "SPLIT_DECISION"
TIMESLOT_SELECTION = "TIMESLOT_SELECTION"
CONFLICT_AVOIDANCE = "CONFLICT_AVOIDANCE"
FAIRNESS_BALANCING = "FAIRNESS_BALANCING"

SOURCE_SOLVER_TRACE = "SOLVER_TRACE"
SOURCE_INPUT_CONSTRAINT = "INPUT_CONSTRAINT"
SOURCE_POST_HOC_HEURISTIC = "POST_HOC_HEURISTIC"
SOURCE_POLICY_RULE = "POLICY_RULE"

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"

EXPLANATION_FACTOR_WEIGHTS: dict[str, float] = {
    ROOM_SELECTION: 1.2,
    STAFF_ASSIGNMENT: 1.0,
    DISTRIBUTION_ASSIGNMENT: 0.8,
    SPLIT_DECISION: 0.9,
    TIMESLOT_SELECTION: 1.0,
    CONFLICT_AVOIDANCE: 1.1,
    FAIRNESS_BALANCING: 1.0,
}


@dataclass(frozen=True)
class RejectedAlternativeExplanation:
    candidate_type: str
    candidate_id: Any
    rejection_reason: str
    violated_constraint: str | None = None
    severity: str = "INFO"
    improvement_hint: str | None = None


@dataclass
class ExplanationFactor:
    category: str
    explanation_type: str
    source: str
    summary: str
    reasoning: List[str] = field(default_factory=list)
    tradeoff_notes: List[str] = field(default_factory=list)
    contributing_constraints: List[str] = field(default_factory=list)
    rejected_alternatives: List[Dict[str, Any]] = field(default_factory=list)
    fairness_notes: List[str] = field(default_factory=list)
    operational_notes: List[str] = field(default_factory=list)
    balancing_notes: List[str] = field(default_factory=list)
    confidence: str = CONFIDENCE_MEDIUM
    confidence_score: int = 70
    weight: float = 1.0


@dataclass
class DecisionExplanation:
    # Compatibility fields kept from the Phase A1 format.
    decision_type: str
    entity: Any
    reasoning: List[str]
    tradeoffs: List[str]
    confidence: int
    # Expanded explainability fields.
    explanation_type: str
    source: str
    confidence_level: str
    confidence_score: int
    readable_summary: str
    tradeoff_notes: List[str] = field(default_factory=list)
    contributing_constraints: List[str] = field(default_factory=list)
    rejected_alternatives: List[Dict[str, Any]] = field(default_factory=list)
    fairness_notes: List[str] = field(default_factory=list)
    operational_notes: List[str] = field(default_factory=list)
    balancing_notes: List[str] = field(default_factory=list)
    explanation_categories: List[str] = field(default_factory=list)
    weighted_reasoning: List[Dict[str, Any]] = field(default_factory=list)
    factor_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    recommended_review_action: str = "REVIEW_DETAILS"


def _capacity_reasoning(students: int, room_capacity: int) -> List[str]:
    reasoning = []
    if room_capacity >= students > 0:
        reasoning.append("capacity_match")
        if room_capacity - students <= 5:
            reasoning.append("tight_capacity_fit")
        elif room_capacity - students <= 15:
            reasoning.append("practical_capacity_fit")
    elif room_capacity < students:
        reasoning.append("over_capacity")
    return reasoning


def _utilization_tradeoffs(students: int, room_capacity: int) -> List[str]:
    utilization = students / room_capacity if room_capacity else 0
    tradeoffs = []
    if utilization < 0.5:
        tradeoffs.append("lower_utilization")
    if utilization > 0.95:
        tradeoffs.append("risk_of_overcrowding")
    return tradeoffs


def _confidence_label(score: int) -> str:
    if score >= 80:
        return CONFIDENCE_HIGH
    if score >= 60:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_LOW


def _unique(values: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    ordered: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _normalize_rejected_alternatives(
    alternatives: Iterable[Dict[str, Any]] | None,
    *,
    candidate_type: str,
) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for alternative in alternatives or []:
        if isinstance(alternative, str):
            item = RejectedAlternativeExplanation(
                candidate_type=candidate_type,
                candidate_id=None,
                rejection_reason=alternative,
            )
        else:
            item = RejectedAlternativeExplanation(
                candidate_type=candidate_type,
                candidate_id=alternative.get("candidate_id", alternative.get("id")),
                rejection_reason=alternative.get("rejection_reason", alternative.get("reason", "unknown_reason")),
                violated_constraint=alternative.get("violated_constraint", alternative.get("constraint")),
                severity=alternative.get("severity", "INFO"),
                improvement_hint=alternative.get("improvement_hint", alternative.get("hint")),
            )
        normalized.append({key: value for key, value in asdict(item).items() if value is not None})
    return normalized


def _factor(
    category: str,
    summary: str,
    *,
    source: str = SOURCE_POST_HOC_HEURISTIC,
    reasoning: List[str] | None = None,
    tradeoff_notes: List[str] | None = None,
    contributing_constraints: List[str] | None = None,
    rejected_alternatives: List[Dict[str, Any]] | None = None,
    fairness_notes: List[str] | None = None,
    operational_notes: List[str] | None = None,
    balancing_notes: List[str] | None = None,
    confidence_score: int = 70,
) -> Dict[str, Any]:
    factor = ExplanationFactor(
        category=category,
        explanation_type="WEIGHTED_FACTOR",
        source=source,
        summary=summary,
        reasoning=reasoning or [],
        tradeoff_notes=tradeoff_notes or [],
        contributing_constraints=contributing_constraints or [],
        rejected_alternatives=rejected_alternatives or [],
        fairness_notes=fairness_notes or [],
        operational_notes=operational_notes or [],
        balancing_notes=balancing_notes or [],
        confidence=_confidence_label(confidence_score),
        confidence_score=max(0, min(100, confidence_score)),
        weight=EXPLANATION_FACTOR_WEIGHTS.get(category, 1.0),
    )
    return asdict(factor)


def _build_room_factor(entry: Dict[str, Any]) -> Dict[str, Any]:
    students = entry.get("num_students", 0) or 0
    room = entry.get("room") or {}
    capacity = room.get("capacity") or 0
    building = room.get("building")
    preferred_building = entry.get("course_preferred_building")
    reasoning = _capacity_reasoning(students, capacity)
    tradeoffs = _utilization_tradeoffs(students, capacity)
    constraints = ["room_capacity", "room_availability"]
    if preferred_building:
        constraints.append("building_preference")
        if building == preferred_building:
            reasoning.append("same_building_preference")
    if not entry.get("room_conflict"):
        reasoning.append("no_room_conflict_detected")
    if entry.get("room_unavailable"):
        tradeoffs.append("room_availability_issue")
    utilization = students / capacity if capacity else 0
    confidence_score = 88
    if capacity and students > capacity:
        confidence_score = 32
    elif utilization < 0.5:
        confidence_score = 68
    rejected = _normalize_rejected_alternatives(entry.get("rejected_room_candidates"), candidate_type="room")
    operational_notes = []
    if building:
        operational_notes.append(f"selected_building:{building}")
    if preferred_building and building == preferred_building:
        operational_notes.append("department_movement_minimized")
    summary = f"Room {room.get('id') or 'unassigned'} was selected for {students} students"
    return _factor(
        ROOM_SELECTION,
        summary,
        reasoning=reasoning,
        tradeoff_notes=tradeoffs,
        contributing_constraints=constraints,
        rejected_alternatives=rejected,
        operational_notes=operational_notes,
        balancing_notes=["room_utilization_considered"],
        source=SOURCE_INPUT_CONSTRAINT,
        confidence_score=confidence_score,
    )


def _build_staff_factor(entry: Dict[str, Any]) -> Dict[str, Any]:
    assigned_staff = [staff for staff in entry.get("assigned_staff", []) if staff is not None]
    staff_load = entry.get("staff_load")
    rejected = _normalize_rejected_alternatives(entry.get("rejected_staff_candidates"), candidate_type="staff")
    reasoning = ["assigned_staff_available"]
    tradeoffs = []
    fairness_notes = []
    balancing_notes = []
    if staff_load is not None:
        if staff_load <= 3:
            reasoning.append("balanced_staff_load")
            fairness_notes.append("invigilator_load_within_target")
        elif staff_load <= 5:
            tradeoffs.append("minor_staff_imbalance")
            balancing_notes.append("assignment_kept_within_acceptable_workload_range")
        else:
            tradeoffs.append("forced_staff_overload")
            fairness_notes.append("manual_workload_review_recommended")
    if entry.get("staff_conflict_avoided"):
        reasoning.append("staff_conflict_avoided")
    summary = f"{len(assigned_staff)} invigilator(s) retained for this slot"
    confidence_score = 86 if staff_load is None or staff_load <= 3 else 64 if staff_load <= 5 else 38
    return _factor(
        STAFF_ASSIGNMENT,
        summary,
        source=SOURCE_POST_HOC_HEURISTIC,
        reasoning=reasoning,
        tradeoff_notes=tradeoffs,
        contributing_constraints=["staff_availability", "workload_balance", "slot_conflict_avoidance"],
        rejected_alternatives=rejected,
        fairness_notes=fairness_notes,
        balancing_notes=balancing_notes,
        confidence_score=confidence_score,
    )


def _build_distribution_factor(entry: Dict[str, Any]) -> Dict[str, Any]:
    distributor = entry.get("paper_distributor")
    rejected = _normalize_rejected_alternatives(entry.get("rejected_distributor_candidates"), candidate_type="distributor")
    reasoning = []
    tradeoffs = []
    operational_notes = []
    if distributor:
        reasoning.append("distribution_staff_assigned")
        operational_notes.append("paper_handover_ready")
        summary = f"Distributor {distributor} was assigned to keep paper flow continuous"
        confidence_score = 82
    else:
        tradeoffs.append("distribution_assignment_missing")
        summary = "No distributor is currently attached to this slot"
        confidence_score = 34
    return _factor(
        DISTRIBUTION_ASSIGNMENT,
        summary,
        source=SOURCE_POLICY_RULE,
        reasoning=reasoning,
        tradeoff_notes=tradeoffs,
        contributing_constraints=["distribution_coverage", "operational_readiness"],
        rejected_alternatives=rejected,
        operational_notes=operational_notes,
        confidence_score=confidence_score,
    )


def _build_split_factor(entry: Dict[str, Any]) -> Dict[str, Any]:
    split_count = entry.get("split_count", 1) or 1
    split_reason = entry.get("split_reason")
    rejected = _normalize_rejected_alternatives(entry.get("rejected_split_candidates"), candidate_type="split")
    reasoning = []
    tradeoffs = []
    operational_notes = []
    if split_count > 1:
        reasoning.append("split_required")
        if split_reason:
            reasoning.append(split_reason)
        operational_notes.append("multi_room_coordination_required")
        summary = f"The allocation was split across {split_count} units to satisfy room or operational constraints"
        confidence_score = 62
    else:
        reasoning.append("single_allocation_retained")
        operational_notes.append("single_room_delivery_simplified")
        summary = "No split was needed; a single allocation path remained acceptable"
        confidence_score = 85
    if split_count > 2:
        tradeoffs.append("higher_split_complexity")
    return _factor(
        SPLIT_DECISION,
        summary,
        source=SOURCE_POST_HOC_HEURISTIC,
        reasoning=reasoning,
        tradeoff_notes=tradeoffs,
        contributing_constraints=["split_minimization", "room_capacity", "operational_complexity"],
        rejected_alternatives=rejected,
        operational_notes=operational_notes,
        confidence_score=confidence_score,
    )


def _build_timeslot_factor(entry: Dict[str, Any]) -> Dict[str, Any]:
    exam_date = entry.get("exam_date")
    exam_time = entry.get("exam_time")
    rejected = _normalize_rejected_alternatives(entry.get("rejected_timeslot_candidates"), candidate_type="timeslot")
    avoided_conflicts = entry.get("avoided_conflicts", []) or []
    reasoning = ["timeslot_selected_from_active_generation"]
    if avoided_conflicts:
        reasoning.append("conflict_window_avoided")
    tradeoffs = []
    if entry.get("timeslot_compromise"):
        tradeoffs.append("acceptable_timeslot_compromise")
    summary = f"Timeslot {exam_date or '-'} {exam_time or '-'} was retained for the allocation"
    return _factor(
        TIMESLOT_SELECTION,
        summary,
        source=SOURCE_INPUT_CONSTRAINT,
        reasoning=reasoning,
        tradeoff_notes=tradeoffs,
        contributing_constraints=["period_window", "slot_conflict_avoidance", "room_staff_alignment"],
        rejected_alternatives=rejected,
        operational_notes=["timeslot_keeps_schedule_sequence_intact"] if exam_time else [],
        confidence_score=78 if not entry.get("timeslot_compromise") else 61,
    )


def _build_conflict_avoidance_factor(entry: Dict[str, Any]) -> Dict[str, Any]:
    avoided_conflicts = _unique(str(item) for item in (entry.get("avoided_conflicts", []) or []))
    rejected = []
    rejected.extend(_normalize_rejected_alternatives(entry.get("rejected_room_candidates"), candidate_type="room"))
    rejected.extend(_normalize_rejected_alternatives(entry.get("rejected_staff_candidates"), candidate_type="staff"))
    rejected.extend(_normalize_rejected_alternatives(entry.get("rejected_timeslot_candidates"), candidate_type="timeslot"))
    if not avoided_conflicts and not rejected:
        avoided_conflicts = ["no_explicit_conflict_signal_recorded"]
    summary = "Known conflict candidates were filtered out before finalizing the allocation"
    return _factor(
        CONFLICT_AVOIDANCE,
        summary,
        source=SOURCE_POST_HOC_HEURISTIC,
        reasoning=avoided_conflicts,
        contributing_constraints=["room_conflict", "staff_conflict", "student_conflict"],
        rejected_alternatives=rejected,
        operational_notes=["uses_known_filtered_candidates_only"],
        confidence_score=84 if rejected else 66,
    )


def _build_fairness_factor(entry: Dict[str, Any]) -> Dict[str, Any]:
    staff_load = entry.get("staff_load")
    fairness_delta = entry.get("fairness_delta")
    reasoning = []
    tradeoffs = []
    fairness_notes = []
    balancing_notes = []
    if staff_load is None:
        fairness_notes.append("staff_load_not_provided")
        confidence_score = 58
    else:
        if staff_load <= 3:
            reasoning.append("load_balanced_against_current_assignments")
            fairness_notes.append("assignment_kept_near_team_average")
            confidence_score = 84
        elif staff_load <= 5:
            tradeoffs.append("minor_load_imbalance_accepted")
            fairness_notes.append("monitor_followup_balance_after_manual_review")
            confidence_score = 63
        else:
            tradeoffs.append("high_load_fallback")
            fairness_notes.append("fairness_instability_warning")
            confidence_score = 36
    if fairness_delta is not None:
        balancing_notes.append(f"fairness_delta:{fairness_delta}")
    summary = "Fairness and workload balance were considered while preserving the final allocation"
    return _factor(
        FAIRNESS_BALANCING,
        summary,
        source=SOURCE_POST_HOC_HEURISTIC,
        reasoning=reasoning,
        tradeoff_notes=tradeoffs,
        contributing_constraints=["fairness_balance", "workload_ceiling", "operational_continuity"],
        fairness_notes=fairness_notes,
        balancing_notes=balancing_notes,
        confidence_score=confidence_score,
    )


def explain_schedule_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a multi-factor explanation for a single allocation entry."""
    factors = [
        _build_room_factor(entry),
        _build_staff_factor(entry),
        _build_distribution_factor(entry),
        _build_split_factor(entry),
        _build_timeslot_factor(entry),
        _build_conflict_avoidance_factor(entry),
        _build_fairness_factor(entry),
    ]

    weighted_reasoning = [
        {
            "category": factor["category"],
            "weight": factor["weight"],
            "summary": factor["summary"],
            "confidence": factor["confidence"],
            "confidence_score": factor["confidence_score"],
        }
        for factor in factors
    ]

    total_weight = sum(item["weight"] for item in weighted_reasoning) or 1.0
    confidence_score = int(
        round(
            sum(item["confidence_score"] * item["weight"] for item in weighted_reasoning) / total_weight
        )
    )
    confidence_level = _confidence_label(confidence_score)
    source_priority = [
        SOURCE_SOLVER_TRACE,
        SOURCE_INPUT_CONSTRAINT,
        SOURCE_POLICY_RULE,
        SOURCE_POST_HOC_HEURISTIC,
    ]
    sources_seen = [factor.get("source") for factor in factors if factor.get("source")]
    source = next((candidate for candidate in source_priority if candidate in sources_seen), SOURCE_POST_HOC_HEURISTIC)

    reasoning = _unique(
        reason
        for factor in factors
        for reason in factor.get("reasoning", [])
    )
    tradeoff_notes = _unique(
        note
        for factor in factors
        for note in factor.get("tradeoff_notes", [])
    )
    contributing_constraints = _unique(
        item
        for factor in factors
        for item in factor.get("contributing_constraints", [])
    )
    fairness_notes = _unique(
        note
        for factor in factors
        for note in factor.get("fairness_notes", [])
    )
    operational_notes = _unique(
        note
        for factor in factors
        for note in factor.get("operational_notes", [])
    )
    balancing_notes = _unique(
        note
        for factor in factors
        for note in factor.get("balancing_notes", [])
    )
    rejected_alternatives = [
        alternative
        for factor in factors
        for alternative in factor.get("rejected_alternatives", [])
    ]
    readable_summary = " | ".join(factor["summary"] for factor in factors[:3])

    explanation = DecisionExplanation(
        decision_type="ROOM_ASSIGNMENT",
        entity=entry.get("course_id") or entry.get("section_id"),
        reasoning=reasoning,
        tradeoffs=tradeoff_notes,
        confidence=confidence_score,
        explanation_type="MULTI_FACTOR_ALLOCATION_EXPLANATION",
        source=source,
        confidence_level=confidence_level,
        confidence_score=confidence_score,
        readable_summary=readable_summary,
        tradeoff_notes=tradeoff_notes,
        contributing_constraints=contributing_constraints,
        rejected_alternatives=rejected_alternatives,
        fairness_notes=fairness_notes,
        operational_notes=operational_notes,
        balancing_notes=balancing_notes,
        explanation_categories=[factor["category"] for factor in factors],
        weighted_reasoning=weighted_reasoning,
        factor_breakdown=factors,
        recommended_review_action=(
            "REVIEW_HIGH_RISK" if confidence_level == CONFIDENCE_LOW else "REVIEW_NORMAL" if tradeoff_notes else "APPROVE_WITH_STANDARD_REVIEW"
        ),
    )
    return asdict(explanation)


def explain_room_assignment(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility wrapper preserved for existing callers."""
    return explain_schedule_entry(entry)


def explain_schedule(schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Explain a full schedule (list of normalized allocation entries)."""
    return [explain_schedule_entry(entry) for entry in schedule]
