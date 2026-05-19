"""Room utilization analytics service.

Pure logic. No DB. No ORM. No HTTP.  All inputs are plain dicts / lists of dicts.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _floor_key_from_room_name(room_name: str) -> str:
    """Infer floor key from room name prefix (ENG, SCI, LAW, etc.)."""
    name = (room_name or "").strip().upper()
    alpha = "".join(ch for ch in name if ch.isalnum())
    return alpha[:3] if alpha else "unknown"


# ── Public API ────────────────────────────────────────────────────────────────

def compute_room_analytics(
    room_schedules: list[dict],
    period_info: dict | None = None,
) -> dict:
    """Compute room utilization analytics from pre-computed room schedule data.

    Args:
        room_schedules: [{room_name, building, capacity, exam_date,
                          exam_time, sections_count}]
        period_info:    Optional {academic_year, semester, exam_type}

    Returns:
        RoomUtilizationSummary-shaped dict.
    """
    if not room_schedules:
        return {
            "average_utilization":     0.0,
            "underutilized_count":     0,
            "overcapacity_count":      0,
            "building_distribution":   {},
            "floor_distribution":      {},
            "room_risk_flags":         [],
        }

    # Detect double-booking conflicts: same room + same date + same time range
    slot_usage: dict[tuple[str, str, str], int] = defaultdict(int)
    for sch in room_schedules:
        room_name = sch.get("room_name", "")
        date = str(sch.get("exam_date", ""))
        time_range = str(sch.get("exam_time", ""))
        slot_usage[(room_name, date, time_range)] += 1

    conflict_count = sum(1 for cnt in slot_usage.values() if cnt > 1)

    # Building distribution
    building_map: dict[str, dict] = defaultdict(
        lambda: {"scheduled_rooms": 0, "total_capacity": 0, "total_students": 0}
    )
    for sch in room_schedules:
        bldg = sch.get("building") or "unknown"
        building_map[bldg]["scheduled_rooms"] += 1
        building_map[bldg]["total_capacity"] += _safe_int(sch.get("capacity", 0))
        building_map[bldg]["total_students"] += _safe_int(sch.get("sections_count", 0))

    bldg_dist = {}
    for bldg, stats in building_map.items():
        cap = max(stats["total_capacity"], 1)
        bldg_dist[bldg] = {
            "scheduled_rooms":   stats["scheduled_rooms"],
            "total_capacity":    stats["total_capacity"],
            "utilized_sheets":   stats["total_students"],
            "avg_utilization":   round(stats["total_students"] / cap, 4),
        }

    # Floor distribution
    floor_map: dict[str, dict] = defaultdict(
        lambda: {"rooms": 0, "total_capacity": 0, "total_students": 0}
    )
    for sch in room_schedules:
        fk = _floor_key_from_room_name(str(sch.get("room_name", "")))
        floor_map[fk]["rooms"] += 1
        floor_map[fk]["total_capacity"] += _safe_int(sch.get("capacity", 0))
        floor_map[fk]["total_students"] += _safe_int(sch.get("sections_count", 0))

    floor_dist = {}
    for fk, stats in floor_map.items():
        cap = max(stats["total_capacity"], 1)
        floor_dist[fk] = {
            "rooms":           stats["rooms"],
            "total_capacity":  stats["total_capacity"],
            "avg_utilization": round(stats["total_students"] / cap, 4),
        }

    # Utilisation per room schedule row (row-level count)
    total_students = sum(_safe_int(sch.get("sections_count", 0)) for sch in room_schedules)
    total_capacity = sum(_safe_int(sch.get("capacity", 0)) for sch in room_schedules)

    # Room utilisation is measured as a per-slot average fraction of used seats:
    # sum(sections_count) / sum(capacity) for all occupied slots of the room.
    avg_util = (total_students / max(total_capacity, 1)) if total_capacity > 0 else 0.0

    # Underutilised / overcapacity flags
    underutilized = []
    overcapacity = []
    seen_rooms: dict[str, float] = {}
    for sch in room_schedules:
        room_name = str(sch.get("room_name", ""))
        cap = _safe_int(sch.get("capacity", 0))
        sects = _safe_int(sch.get("sections_count", 0))
        if cap == 0:
            continue
        ratio = sects / cap
        if ratio < 0.3 and room_name not in seen_rooms:
            underutilized.append(room_name)
            seen_rooms[room_name] = ratio
        if sects > 1 and sch.get("exam_time"):
            # same room, multiple sections, same time slot
            pass  # counted in conflicts above

    # Room risk flags
    risk_flags: list[dict] = []
    if conflict_count > 0:
        risk_flags.append({
            "risk": f"{conflict_count} room double-booking conflict(s) detected",
            "severity": "high",
        })

    for sch in room_schedules:
        room_name = str(sch.get("room_name", ""))
        cap    = _safe_int(sch.get("capacity", 0))
        sects  = _safe_int(sch.get("sections_count", 0))
        util_f = (sects / max(cap, 1)) if cap > 0 else 0.0
        if sects > cap:
            risk_flags.append({
                "risk": (f"Room {room_name} oversubscribed "
                         f"({sects}/{cap}) on "
                         f"{sch.get('exam_date', '?')} "
                         f"{sch.get('exam_time', '?')}"),
                "severity": "high",
            })
        elif util_f < 0.3:
            risk_flags.append({
                "risk": (f"Room {room_name} underutilised "
                         f"(~{round(util_f*100,1)}%) on "
                         f"{sch.get('exam_date', '?')} "
                         f"{sch.get('exam_time', '?')}"),
                "severity": "low",
            })

    for bldg, stats in bldg_dist.items():
        cap = max(stats["total_capacity"], 1)
        util = stats.get("utilized_sheets", 0) / cap
        if util > 0.95:
            risk_flags.append({
                "risk": f"Building {bldg} at {round(util*100,1)}% utilisation",
                "severity": "medium",
            })
        elif util < 0.15:
            risk_flags.append({
                "risk": f"Building {bldg} significantly underutilised (~{round(util*100,1)}%)",
                "severity": "low",
            })

    # Split-room efficiency: ratio of multi-use schedules to total unique slots
    # A "split room" is one used for >1 time-slot (across all periods being measured)
    room_slot_count: dict[str, int] = defaultdict(int)
    for sch in room_schedules:
        room_name = str(sch.get("room_name", ""))
        room_slot_count[room_name] += 1
    multi_slot_count = sum(1 for cnt in room_slot_count.values() if cnt > 1)
    split_room_efficiency = round(
        multi_slot_count / max(len(room_slot_count), 1), 4
    )

    # Room dependency risk: rooms without an alternative
    # Identified as rooms that appear in only one slot
    single_slot_rooms = [rn for rn, cnt in room_slot_count.items() if cnt == 1]
    room_dependency_risk = round(len(single_slot_rooms) / max(len(room_slot_count), 1), 4)

    return {
        "average_utilization":          round(avg_util, 4),
        "underutilized_count":          len(underutilized),
        "underutilized_rooms":          underutilized,
        "overcapacity_count":           conflict_count,
        "building_distribution":        bldg_dist,
        "floor_distribution":           floor_dist,
        "room_risk_flags":              risk_flags[:10],
        "split_room_efficiency":        split_room_efficiency,
        "room_dependency_risk":         room_dependency_risk,
        "period_info":                  period_info or {},
    }
