"""policy_pack_registry.py — Faculty-specific policy packs."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class WorkloadPolicyPack:
    overload_threshold: float = 1.5
    severe_imbalance_threshold: float = 0.4
    distribution_weight: float = 0.6
    invigilation_weight: float = 1.0


@dataclass
class AlertPolicyPack:
    cooldown_minutes: int = 30
    max_alerts_per_category: int = 10


class PolicyPackRegistry:
    _workload: dict[str, WorkloadPolicyPack] = {"POL": WorkloadPolicyPack()}
    _alert: dict[str, AlertPolicyPack] = {"POL": AlertPolicyPack()}

    @classmethod
    def get_workload_policy(cls, faculty_code: str = "POL") -> WorkloadPolicyPack:
        return cls._workload.get(faculty_code, WorkloadPolicyPack())

    @classmethod
    def get_alert_policy(cls, faculty_code: str = "POL") -> AlertPolicyPack:
        return cls._alert.get(faculty_code, AlertPolicyPack())
