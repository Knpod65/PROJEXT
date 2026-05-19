"""Workload policy registry — constants + convenience accessor for workload policies."""
from __future__ import annotations

from config_models.workload_policy import WorkloadPolicy
from services.workload_policy_service import get_effective_policy

# Well-known special role constants
SPECIAL_ROLE_ROOM_KEEPER = "room_keeper"
SPECIAL_ROLE_ESQ_STAFF   = "esq_staff"
EXCLUDED_DIVISION_FACULTY_SECRETARY = "Faculty_Secretary"


def get_effective_workload_policy(faculty_id: int | None = None) -> WorkloadPolicy:
    """Return the effective workload policy for the given faculty."""
    return get_effective_policy(faculty_id)
