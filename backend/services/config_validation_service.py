"""Config validation service — severity-graded validation reports for D3 config objects.

All functions are pure (no DB, no HTTP). Returns frozen ConfigValidationReport objects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from config_models.academic_group_config import AcademicGroupConfig
from config_models.faculty_config import FacultyConfig
from config_models.governance_flow import GovernanceFlowConfig
from config_models.workload_policy import WorkloadPolicy


class ValidationSeverity(str, Enum):
    HARD_FAIL  = "HARD_FAIL"
    WARNING    = "WARNING"
    INFO       = "INFO"
    SUGGESTION = "SUGGESTION"


@dataclass(frozen=True)
class ValidationResult:
    severity: ValidationSeverity
    code: str
    message: str
    field: str | None
    context: dict[str, Any]


@dataclass(frozen=True)
class ConfigValidationReport:
    valid: bool          # True if no HARD_FAIL results
    results: tuple[ValidationResult, ...]
    validated_at: str    # UTC ISO
    config_type: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _report(results: list[ValidationResult], config_type: str) -> ConfigValidationReport:
    has_fail = any(r.severity == ValidationSeverity.HARD_FAIL for r in results)
    return ConfigValidationReport(
        valid=not has_fail,
        results=tuple(results),
        validated_at=_now_iso(),
        config_type=config_type,
    )


def _fail(code: str, message: str, field: str | None = None, **ctx: Any) -> ValidationResult:
    return ValidationResult(ValidationSeverity.HARD_FAIL, code, message, field, dict(ctx))


def _warn(code: str, message: str, field: str | None = None, **ctx: Any) -> ValidationResult:
    return ValidationResult(ValidationSeverity.WARNING, code, message, field, dict(ctx))


def _info(code: str, message: str, field: str | None = None, **ctx: Any) -> ValidationResult:
    return ValidationResult(ValidationSeverity.INFO, code, message, field, dict(ctx))


def validate_faculty_config(config: FacultyConfig) -> ConfigValidationReport:
    results: list[ValidationResult] = []

    if config.faculty_id < 1:
        results.append(_fail("INVALID_FACULTY_ID", "faculty_id must be >= 1", "faculty_id"))
    if not config.code.strip():
        results.append(_fail("MISSING_FACULTY_CODE", "code must not be empty", "code"))
    if not config.name_th.strip():
        results.append(_fail("MISSING_FACULTY_NAME_TH", "name_th must not be empty", "name_th"))
    if not config.name_en.strip():
        results.append(_fail("MISSING_FACULTY_NAME_EN", "name_en must not be empty", "name_en"))

    if not config.email_domain.strip() or "." not in config.email_domain:
        results.append(_warn("INVALID_EMAIL_DOMAIN", "email_domain appears invalid", "email_domain"))

    if not config.metadata:
        results.append(_info("EMPTY_METADATA", "metadata is empty", "metadata"))

    return _report(results, "FacultyConfig")


def validate_workload_policy(policy: WorkloadPolicy) -> ConfigValidationReport:
    results: list[ValidationResult] = []

    if policy.max_supervision_sessions < 0:
        results.append(_fail("NEGATIVE_SUPERVISION_SESSIONS",
                             "max_supervision_sessions must be >= 0",
                             "max_supervision_sessions"))

    if not policy.excluded_usernames:
        results.append(_warn("EMPTY_EXCLUDED_USERNAMES",
                             "excluded_usernames is empty — all users are eligible",
                             "excluded_usernames"))

    if policy.allow_cross_department:
        results.append(_info("CROSS_DEPARTMENT_ENABLED",
                             "allow_cross_department is True",
                             "allow_cross_department"))

    return _report(results, "WorkloadPolicy")


def validate_governance_flow(flow: GovernanceFlowConfig) -> ConfigValidationReport:
    results: list[ValidationResult] = []

    if not flow.flow_name.strip():
        results.append(_fail("MISSING_FLOW_NAME", "flow_name must not be empty", "flow_name"))

    if not flow.round_1_signers:
        results.append(_fail("NO_ROUND1_SIGNERS",
                             "round_1_signers must have at least one slot",
                             "round_1_signers"))
    elif flow.approval_quorum > len(flow.round_1_signers):
        results.append(_fail("QUORUM_EXCEEDS_SLOTS",
                             f"approval_quorum ({flow.approval_quorum}) > round_1_signers count ({len(flow.round_1_signers)})",
                             "approval_quorum",
                             quorum=flow.approval_quorum,
                             slot_count=len(flow.round_1_signers)))

    if not flow.round_2_signers:
        results.append(_warn("EMPTY_ROUND2_SIGNERS",
                             "round_2_signers is empty — single-round approval only",
                             "round_2_signers"))

    if not flow.requires_governance_review:
        results.append(_info("GOVERNANCE_REVIEW_DISABLED",
                             "requires_governance_review is False",
                             "requires_governance_review"))

    return _report(results, "GovernanceFlowConfig")


def validate_academic_group_config(config: AcademicGroupConfig) -> ConfigValidationReport:
    results: list[ValidationResult] = []

    if not config.code.strip():
        results.append(_fail("MISSING_GROUP_CODE", "code must not be empty", "code"))

    if not config.course_prefixes:
        results.append(_fail("EMPTY_COURSE_PREFIXES",
                             "course_prefixes must not be empty",
                             "course_prefixes"))

    if not config.label_th.strip():
        results.append(_warn("MISSING_LABEL_TH", "label_th is empty", "label_th"))

    return _report(results, "AcademicGroupConfig")


def validate_platform_snapshot(snapshot: dict[str, Any]) -> list[ConfigValidationReport]:
    """Validate all configs in a raw snapshot dict."""
    from services.platform_config_import_service import (
        parse_faculty_config,
        parse_workload_policy,
        parse_governance_flow,
        parse_academic_group_config,
    )

    reports: list[ConfigValidationReport] = []

    for d in snapshot.get("faculty_configs", []):
        try:
            reports.append(validate_faculty_config(parse_faculty_config(d)))
        except Exception as exc:
            results = [_fail("PARSE_ERROR", str(exc))]
            reports.append(_report(results, "FacultyConfig"))

    for d in snapshot.get("workload_policies", []):
        try:
            reports.append(validate_workload_policy(parse_workload_policy(d)))
        except Exception as exc:
            results = [_fail("PARSE_ERROR", str(exc))]
            reports.append(_report(results, "WorkloadPolicy"))

    for d in snapshot.get("governance_flows", []):
        try:
            reports.append(validate_governance_flow(parse_governance_flow(d)))
        except Exception as exc:
            results = [_fail("PARSE_ERROR", str(exc))]
            reports.append(_report(results, "GovernanceFlowConfig"))

    for d in snapshot.get("academic_group_configs", []):
        try:
            reports.append(validate_academic_group_config(parse_academic_group_config(d)))
        except Exception as exc:
            results = [_fail("PARSE_ERROR", str(exc))]
            reports.append(_report(results, "AcademicGroupConfig"))

    return reports


def has_hard_failures(reports: list[ConfigValidationReport]) -> bool:
    return any(not r.valid for r in reports)


def summarize_validation(reports: list[ConfigValidationReport]) -> dict[str, Any]:
    counts: dict[str, int] = {
        "hard_fail_count": 0,
        "warning_count": 0,
        "info_count": 0,
        "suggestion_count": 0,
    }
    for report in reports:
        for result in report.results:
            if result.severity == ValidationSeverity.HARD_FAIL:
                counts["hard_fail_count"] += 1
            elif result.severity == ValidationSeverity.WARNING:
                counts["warning_count"] += 1
            elif result.severity == ValidationSeverity.INFO:
                counts["info_count"] += 1
            elif result.severity == ValidationSeverity.SUGGESTION:
                counts["suggestion_count"] += 1
    counts["all_valid"] = counts["hard_fail_count"] == 0  # type: ignore[assignment]
    return counts
