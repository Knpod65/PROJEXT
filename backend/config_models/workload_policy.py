"""WorkloadPolicy — per-faculty staff eligibility and workload configuration.

Pure Python frozen dataclass. No DB, no HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkloadPolicy:
    faculty_id: int | None
    paper_distribution_division: str       # division name for paper distributors
    excluded_usernames: frozenset[str]     # usernames excluded from paper distribution
    excluded_name_snippets: tuple[str, ...] # Thai name substrings to exclude
    excluded_special_roles: frozenset[str] # {"room_keeper", "esq_staff"}
    excluded_divisions: frozenset[str]     # {"Faculty_Secretary"}
    max_supervision_sessions: int          # 0 = unlimited
    allow_cross_department: bool
    metadata: dict[str, Any]


def make_workload_policy(
    *,
    faculty_id: int | None = None,
    paper_distribution_division: str = "",
    excluded_usernames: frozenset[str] | None = None,
    excluded_name_snippets: tuple[str, ...] = (),
    excluded_special_roles: frozenset[str] | None = None,
    excluded_divisions: frozenset[str] | None = None,
    max_supervision_sessions: int = 0,
    allow_cross_department: bool = False,
    metadata: dict[str, Any] | None = None,
) -> WorkloadPolicy:
    return WorkloadPolicy(
        faculty_id=faculty_id,
        paper_distribution_division=paper_distribution_division,
        excluded_usernames=excluded_usernames if excluded_usernames is not None else frozenset(),
        excluded_name_snippets=excluded_name_snippets,
        excluded_special_roles=excluded_special_roles if excluded_special_roles is not None else frozenset(),
        excluded_divisions=excluded_divisions if excluded_divisions is not None else frozenset(),
        max_supervision_sessions=max_supervision_sessions,
        allow_cross_department=allow_cross_department,
        metadata=dict(metadata) if metadata else {},
    )
