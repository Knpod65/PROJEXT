from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class DecisionExplanation:
    decision_type: str
    entity: Any
    reasoning: List[str]
    tradeoffs: List[str]
    confidence: int


def _capacity_reasoning(students: int, room_capacity: int) -> List[str]:
    r = []
    if room_capacity >= students:
        r.append("capacity_match")
        if room_capacity - students <= 5:
            r.append("tight_capacity_fit")
    else:
        r.append("over_capacity")
    return r


def _utilization_tradeoffs(students: int, room_capacity: int) -> List[str]:
    util = students / room_capacity if room_capacity else 0
    t = []
    if util < 0.5:
        t.append("lower_utilization")
    if util > 0.95:
        t.append("risk_of_overcrowding")
    return t


def explain_room_assignment(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce an explanation for a single schedule entry's room assignment.

    Expected `entry` keys: `course_id`, `section_id`, `num_students`, `room` (dict with `id`, `capacity`, `building`),
    optional `course_preferred_building`, `room_unavailable` (bool), and `staff_load` (approx int).
    """
    students = entry.get("num_students", 0)
    room = entry.get("room") or {}
    capacity = room.get("capacity") or 0
    reasoning = []
    tradeoffs = []

    reasoning += _capacity_reasoning(students, capacity)

    # building preference
    pref = entry.get("course_preferred_building")
    if pref and room.get("building") == pref:
        reasoning.append("same_building_preference")

    # room availability
    if entry.get("room_unavailable"):
        reasoning.append("room_availability_issue")

    # staffing tradeoffs
    tradeoffs += _utilization_tradeoffs(students, capacity)
    staff_load = entry.get("staff_load")
    if staff_load and staff_load > 3:
        tradeoffs.append("higher_staff_load")

    confidence = min(95, 40 + 12 * max(1, len(reasoning)))

    expl = DecisionExplanation(
        decision_type="ROOM_ASSIGNMENT",
        entity=entry.get("course_id") or entry.get("section_id"),
        reasoning=reasoning,
        tradeoffs=tradeoffs,
        confidence=confidence,
    )
    return asdict(expl)


def explain_schedule(schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Explain a full schedule (list of entries)."""
    return [explain_room_assignment(e) for e in schedule]
