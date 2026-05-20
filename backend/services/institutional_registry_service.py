"""institutional_registry_service.py — Institutional domain registry."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class InstitutionalDomain:
    domain_code: str
    domain_name: str
    governance_owner: str
    data_classification: str
    pdpa_level: str
    operational_criticality: str


class InstitutionalRegistryService:
    _domains: dict[str, InstitutionalDomain] = {
        "exams": InstitutionalDomain("exams", "Exam Operations", "admin", "operational", "high", "critical"),
        "workload": InstitutionalDomain("workload", "Workload Analytics", "staff", "operational", "medium", "high"),
        "governance": InstitutionalDomain("governance", "Governance", "admin", "governance", "high", "critical"),
    }

    @classmethod
    def get_domain(cls, code: str) -> InstitutionalDomain | None:
        return cls._domains.get(code)

    @classmethod
    def list_domains(cls) -> list[str]:
        return list(cls._domains.keys())
