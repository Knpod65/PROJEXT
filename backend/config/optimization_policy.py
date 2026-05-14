"""Typed optimization policy configuration.

Extends config/settings.py with optimization-specific tunables that can be
overridden via environment variables. The existing threshold dicts in
policies/optimization_policy.py remain canonical; this module adds
per-rule toggles and enforcement mode config.

Usage:
    from config.optimization_policy import optimization_policy_config
    if optimization_policy_config.rules_enforce_mode:
        ...
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class OptimizationPolicyConfig:
    # When True, HARD_FAIL rules block schedule release. When False, warn-only.
    rules_enforce_mode: bool = field(
        default_factory=lambda: os.getenv("OPT_RULES_ENFORCE", "true").lower() == "true"
    )

    # Maximum allowed quality score drop (0–100) before auto-escalating governance.
    max_score_drop_before_escalation: float = field(
        default_factory=lambda: float(os.getenv("OPT_MAX_SCORE_DROP", "15.0"))
    )

    # Penalty-to-score ratio above which human review is required.
    penalty_ratio_review_threshold: float = field(
        default_factory=lambda: float(os.getenv("OPT_PENALTY_RATIO_REVIEW", "0.25"))
    )

    # Minimum room utilization for auto-approval (mirrors ROOM_UTILIZATION_THRESHOLDS["low"]).
    min_room_utilization_auto_approve: float = field(
        default_factory=lambda: float(os.getenv("OPT_MIN_ROOM_UTIL", "0.40"))
    )

    # Quality score below which governance auto-escalates (mirrors quality_escalation_threshold).
    quality_escalation_threshold: float = field(
        default_factory=lambda: float(os.getenv("OPT_QUALITY_ESCALATION", "55.0"))
    )

    # Quality score below which human review is required.
    quality_review_threshold: float = field(
        default_factory=lambda: float(os.getenv("OPT_QUALITY_REVIEW", "70.0"))
    )


# Module-level singleton — read once at import time.
optimization_policy_config: OptimizationPolicyConfig = OptimizationPolicyConfig()
