"""Optimization simulation service.

Generates alternative schedule scenarios by applying deterministic
transformations to an already-generated schedule. Does NOT invoke the
CP-SAT solver or modify optimizer decisions.

Use cases:
  - "What if we move this exam to a larger room?"
  - "What if we rebalance staff to reduce overload?"
  - "What if we eliminate split-room scenarios?"

All transform functions deep-copy the input before modification — the
original schedule list is never mutated.
"""
from __future__ import annotations

import copy
from collections import defaultdict
from typing import Any, Iterable


def _clone(schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return copy.deepcopy(schedule)


# ── Transformations ───────────────────────────────────────────────────────

def simulate_room_swap(
    schedule: list[dict[str, Any]],
    entry_index: int,
    new_room: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return a new schedule with the room at entry_index replaced by new_room.

    The original schedule is NOT mutated.
    """
    result = _clone(schedule)
    result[entry_index]["room"] = dict(new_room)
    return result


def simulate_staff_rebalance(
    schedule: list[dict[str, Any]],
    *,
    max_load_per_staff: int = 3,
) -> list[dict[str, Any]]:
    """Return a scenario with overloaded staff removed from their excess slots.

    Staff with total assignments > max_load_per_staff are removed from ALL
    entries. In a real rebalance, they would be replaced; here we remove to
    expose the delta — comparison service will score the gap.
    """
    result = _clone(schedule)

    counts: dict[Any, int] = defaultdict(int)
    for entry in result:
        for sid in entry.get("assigned_staff", []):
            if sid is not None:
                counts[sid] += 1

    overloaded = {sid for sid, n in counts.items() if n > max_load_per_staff}

    for entry in result:
        entry["assigned_staff"] = [
            s for s in entry.get("assigned_staff", [])
            if s not in overloaded
        ]

    return result


def simulate_split_elimination(
    schedule: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a scenario with all split_count values reset to 1.

    This simulates "what if we could avoid all split-room arrangements?"
    """
    result = _clone(schedule)
    for entry in result:
        entry["split_count"] = 1
    return result


def simulate_distributor_fill(
    schedule: list[dict[str, Any]],
    default_distributor: str = "UNASSIGNED",
) -> list[dict[str, Any]]:
    """Return a scenario where every entry has a distributor assigned.

    Used to score the impact of filling distributor gaps.
    """
    result = _clone(schedule)
    for entry in result:
        if not entry.get("paper_distributor"):
            entry["paper_distributor"] = default_distributor
    return result


# ── Scoring ───────────────────────────────────────────────────────────────

def score_simulation(
    simulated_schedule: list[dict[str, Any]],
) -> dict[str, Any]:
    """Score a simulated schedule using the standard quality pipeline.

    Returns the same structure as compute_quality_report() so the comparison
    service can diff directly.
    """
    from services.optimization_quality_service import compute_quality_report
    return compute_quality_report(simulated_schedule)
