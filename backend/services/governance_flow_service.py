"""Governance flow service — load, register, and resolve per-faculty signing flows.

Module-level singleton registry keyed by faculty_id (or None for global default).
Thread-safe via threading.Lock. Use clear_governance_flows() in tests.
"""
from __future__ import annotations

import threading
from typing import Any

from config_models.governance_flow import (
    GovernanceFlowConfig,
    SignerSlot,
    make_governance_flow_config,
)

_lock = threading.Lock()
_registry: dict[int | None, GovernanceFlowConfig] = {}


def build_default_flow_from_settings() -> GovernanceFlowConfig:
    """Construct a GovernanceFlowConfig from settings.sign_order_usernames.

    First username gets role="admin"; subsequent ones get role="esq_head".
    This is the settings-derived global default — faculty_id=None.
    """
    from config.settings import settings

    usernames = settings.sign_order_usernames
    slots = []
    for i, username in enumerate(usernames, start=1):
        role = "admin" if i == 1 else "esq_head"
        slots.append({
            "position": i,
            "role": role,
            "username_hint": username,
            "required": True,
        })

    return make_governance_flow_config(
        "settings_derived",
        slots,
        [],
        faculty_id=None,
        requires_governance_review=True,
        approval_quorum=len(slots),
    )


def register_governance_flow(config: GovernanceFlowConfig) -> None:
    """Store a governance flow in the registry, keyed by faculty_id."""
    with _lock:
        _registry[config.faculty_id] = config


def get_effective_flow(faculty_id: int | None = None) -> GovernanceFlowConfig:
    """Return the governance flow for the given faculty.

    Resolution: faculty-specific → global (faculty_id=None) → build from settings.
    """
    with _lock:
        if faculty_id is not None and faculty_id in _registry:
            return _registry[faculty_id]
        if None in _registry:
            return _registry[None]

    default = build_default_flow_from_settings()
    with _lock:
        _registry[None] = default
    return default


def get_signer_order(faculty_id: int | None = None) -> tuple[str | None, ...]:
    """Return (username_hint, ...) tuple from round_1_signers.

    Compatibility shim for code that uses settings.sign_order_usernames directly.
    Returns None entries for slots that have no username_hint.
    """
    flow = get_effective_flow(faculty_id)
    return tuple(slot.username_hint for slot in flow.round_1_signers)


def validate_flow_config(config: GovernanceFlowConfig) -> list[str]:
    """Return a list of validation error strings (empty = valid)."""
    errors: list[str] = []
    if not config.flow_name.strip():
        errors.append("flow_name must not be empty")
    if len(config.round_1_signers) == 0:
        errors.append("round_1_signers must contain at least one slot")
    if config.approval_quorum > len(config.round_1_signers):
        errors.append(
            f"approval_quorum ({config.approval_quorum}) exceeds "
            f"round_1_signers count ({len(config.round_1_signers)})"
        )
    positions = [s.position for s in config.round_1_signers]
    if len(positions) != len(set(positions)):
        errors.append("round_1_signers positions must be unique")
    if any(p < 1 for p in positions):
        errors.append("round_1_signers positions must be >= 1 (1-based)")
    return errors


def clear_governance_flows() -> None:
    """Reset module-level registry. Use in tests for isolation."""
    with _lock:
        _registry.clear()
