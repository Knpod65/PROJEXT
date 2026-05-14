"""TypedDict payload contracts for the publication domain."""
from __future__ import annotations

from typing import List, Optional
from typing_extensions import TypedDict


class PublicationBlockerContract(TypedDict):
    code: str
    severity: str
    message: str
    can_override: bool


class PublicationReadinessContract(TypedDict):
    can_publish: bool
    risk_score: float
    blockers: List[PublicationBlockerContract]
    warnings: List[str]
    governance_state: str
    approval_metadata: dict


class PublishAuditContract(TypedDict):
    action: str
    actor_id: Optional[int]
    session_id: Optional[str]
    published_at: str
    risk_score: float
    governance_state: str
    can_publish: bool
    blocker_codes: List[str]
    warning_count: int
    approval_metadata: dict


class EmergencyOverrideContract(TypedDict):
    action: str
    actor_id: Optional[int]
    override_reason: str
    blockers_overridden: List[str]
    override_at: str
    requires_post_incident_review: bool
