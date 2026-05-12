"""
workflow_policy.py — canonical workflow signing rules.

This module centralizes the optimizer confirmation workflow constants and
state-transition rules so routers and services do not duplicate them.
"""
from __future__ import annotations

from config.policy import SIGN_ORDER_USERNAMES

WORKFLOW_SIGN_ORDER: tuple[str, ...] = tuple(SIGN_ORDER_USERNAMES)

WORKFLOW_STATE_ORDER: tuple[str, ...] = (
    "draft",
    "confirming",
    "confirmed",
    "swap_open",
    "swap_confirming",
    "locked",
)

ROUND1_ALLOWED_STATUSES: tuple[str, ...] = ("draft", "confirming")
ROUND2_ALLOWED_STATUSES: tuple[str, ...] = ("swap_open", "swap_confirming")

STATE_INDEX = {status: index for index, status in enumerate(WORKFLOW_STATE_ORDER)}


def is_backward_transition(current_status: str, target_status: str) -> bool:
    current_index = STATE_INDEX.get(current_status)
    target_index = STATE_INDEX.get(target_status)
    if current_index is None or target_index is None:
        return False
    return target_index < current_index


def get_round_allowed_statuses(round_no: int) -> tuple[str, ...]:
    if round_no == 1:
        return ROUND1_ALLOWED_STATUSES
    if round_no == 2:
        return ROUND2_ALLOWED_STATUSES
    raise ValueError(f"Unsupported round: {round_no}")
