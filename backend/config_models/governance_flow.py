"""GovernanceFlowConfig — per-faculty signer/approval flow configuration.

Pure Python frozen dataclasses. No DB, no HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class SignerSlot:
    position: int             # 1-based slot index
    role: str                 # expected role string for this slot
    username_hint: str | None # optional specific username override
    required: bool            # True = must sign before advancing


@dataclass(frozen=True)
class GovernanceFlowConfig:
    faculty_id: int | None    # None = global default flow
    flow_name: str
    round_1_signers: tuple[SignerSlot, ...]
    round_2_signers: tuple[SignerSlot, ...]
    requires_governance_review: bool
    approval_quorum: int      # minimum required signers per round (>= 1)
    created_at: str           # UTC ISO
    metadata: dict[str, Any]


def make_governance_flow_config(
    flow_name: str,
    round_1_signers: list[dict[str, Any]],
    round_2_signers: list[dict[str, Any]],
    *,
    faculty_id: int | None = None,
    requires_governance_review: bool = True,
    approval_quorum: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> GovernanceFlowConfig:
    """Convert list-of-dicts slot specs into a frozen GovernanceFlowConfig.

    Each slot dict should have keys: position, role, username_hint (optional), required (optional).
    approval_quorum defaults to len(round_1_signers).
    """
    def _parse_slots(raw: list[dict[str, Any]]) -> tuple[SignerSlot, ...]:
        return tuple(
            SignerSlot(
                position=s["position"],
                role=s["role"],
                username_hint=s.get("username_hint"),
                required=s.get("required", True),
            )
            for s in raw
        )

    slots_r1 = _parse_slots(round_1_signers)
    slots_r2 = _parse_slots(round_2_signers)
    quorum = approval_quorum if approval_quorum is not None else len(slots_r1)

    return GovernanceFlowConfig(
        faculty_id=faculty_id,
        flow_name=flow_name,
        round_1_signers=slots_r1,
        round_2_signers=slots_r2,
        requires_governance_review=requires_governance_review,
        approval_quorum=quorum,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata=dict(metadata) if metadata else {},
    )
