"""faculty_config_registry.py — Configurable faculty/unit registry."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class FacultyConfig:
    faculty_code: str
    faculty_name_en: str
    faculty_name_th: str
    timezone: str = "Asia/Bangkok"
    workload_policy_code: str = "default"
    alert_policy_code: str = "default"
    governance_policy_code: str = "default"
    feature_flags: dict[str, bool] | None = None


DEFAULT_FACULTY = FacultyConfig(
    faculty_code="POL",
    faculty_name_en="Faculty of Political Science and Public Administration",
    faculty_name_th="คณะรัฐศาสตร์และรัฐประศาสนศาสตร์",
    feature_flags={"multi_unit": False},
)


class FacultyConfigRegistry:
    _configs: dict[str, FacultyConfig] = {"POL": DEFAULT_FACULTY}

    @classmethod
    def get_default_faculty_config(cls) -> FacultyConfig:
        return DEFAULT_FACULTY

    @classmethod
    def get_faculty_config(cls, faculty_code: str) -> FacultyConfig:
        return cls._configs.get(faculty_code, DEFAULT_FACULTY)

    @classmethod
    def list_enabled_faculties(cls) -> list[str]:
        return list(cls._configs.keys())
