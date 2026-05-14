"""TypedDict payload contracts for the optimization domain."""
from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict


class QualityContract(TypedDict):
    overall_score: int
    quality_band: str
    risk_level: str
    fairness_score: int
    room_efficiency_score: int
    invigilator_balance_score: int
    conflict_risk_score: int
    governance_readiness_score: int


class RecheckSummaryContract(TypedDict):
    hard_fail_count: int
    warning_count: int
    info_count: int
    total_issues: int


class ObserverContract(TypedDict):
    quality_summary: QualityContract
    recheck_summary: RecheckSummaryContract
    issues: List[dict]
    governance: dict
    explanation_summary: dict
    checked_schedule_count: int


class ReportContract(TypedDict):
    executive_summary: dict
    severity_summary: dict
    issue_summary: List[dict]
    quality_breakdown: QualityContract
    governance: dict
    risk_matrix: List[dict]
    quality_band_summary: dict
    optimization_confidence_score: float
