from typing import List, Dict, Any
import math


def _room_efficiency_score(schedule: List[Dict[str, Any]]) -> float:
    utils = []
    for e in schedule:
        students = e.get("num_students", 0)
        room = e.get("room") or {}
        cap = room.get("capacity") or 1
        utils.append(min(1.0, students / cap))
    return 100 * (sum(utils) / len(utils)) if utils else 100.0


def _fairness_score(schedule: List[Dict[str, Any]]) -> float:
    # fairness measured by stddev of assignments per staff
    counts = {}
    for e in schedule:
        for s in e.get("assigned_staff", []):
            counts[s] = counts.get(s, 0) + 1
    if not counts:
        return 100.0
    vals = list(counts.values())
    mean = sum(vals) / len(vals)
    variance = sum((v - mean) ** 2 for v in vals) / len(vals)
    stddev = math.sqrt(variance)
    # normalize: higher stddev -> lower fairness
    score = max(0.0, 100.0 - (stddev / (mean + 1e-6)) * 25.0)
    return score


def _student_conflict_score(schedule: List[Dict[str, Any]]) -> float:
    # expect schedule entries to include 'student_ids' set per entry
    student_map = {}
    collisions = 0
    total_students = 0
    for e in schedule:
        sids = set(e.get("student_ids", []))
        total_students += len(sids)
        for sid in sids:
            student_map.setdefault(sid, 0)
            student_map[sid] += 1
    for sid, cnt in student_map.items():
        if cnt > 1:
            collisions += cnt - 1
    if total_students == 0:
        return 100.0
    # each collision reduces score
    reduction = min(100.0, (collisions / total_students) * 100.0)
    return max(0.0, 100.0 - reduction)


def compute_quality_report(schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
    room_eff = _room_efficiency_score(schedule)
    fairness = _fairness_score(schedule)
    student_conflict = _student_conflict_score(schedule)

    # simple weighted overall score
    overall = (
        0.35 * room_eff + 0.30 * fairness + 0.25 * student_conflict + 0.10 * 100.0
    )

    risk_level = "LOW"
    if overall < 60:
        risk_level = "HIGH"
    elif overall < 80:
        risk_level = "MEDIUM"

    return {
        "overall_score": int(round(overall)),
        "risk_level": risk_level,
        "fairness_score": int(round(fairness)),
        "room_efficiency_score": int(round(room_eff)),
        "student_conflict_score": int(round(student_conflict)),
        "warnings": [],
        "critical_issues": [],
    }
