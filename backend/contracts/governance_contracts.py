"""TypedDict payload contracts for the governance domain."""
from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict


class GovernanceDecisionContract(TypedDict):
    governance_state: str
    review_priority: str
    escalation_reason: Optional[str]
    override_recommendation: str
    approval_reasoning: str


class OverrideRequestContract(TypedDict):
    actor_id: int
    session_id: str
    override_reason: str
    blockers_overridden: List[str]
    severity: str
