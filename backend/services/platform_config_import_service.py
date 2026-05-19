"""Platform config import service — deserialize JSON dicts back to D3 config objects.

All functions are pure (no DB, no HTTP). Used by the API layer and CLI import tools.
"""
from __future__ import annotations

from typing import Any

from config_models.academic_group_config import AcademicGroupConfig, make_academic_group_config
from config_models.faculty_config import FacultyConfig, make_faculty_config
from config_models.faculty_role_mapping import FacultyRoleMapping, make_faculty_role_mapping
from config_models.governance_flow import GovernanceFlowConfig, SignerSlot, make_governance_flow_config
from config_models.workload_policy import WorkloadPolicy, make_workload_policy


def parse_faculty_config(data: dict[str, Any]) -> FacultyConfig:
    if not data.get("faculty_id"):
        raise ValueError("faculty_id is required")
    if not data.get("code", "").strip():
        raise ValueError("code is required")
    return make_faculty_config(
        faculty_id=int(data["faculty_id"]),
        code=data["code"],
        name_th=data.get("name_th", ""),
        name_en=data.get("name_en", ""),
        email_domain=data.get("email_domain", ""),
        timezone=data.get("timezone", "Asia/Bangkok"),
        academic_year_default=data.get("academic_year_default", "2568"),
        semester_default=data.get("semester_default", "2"),
        is_active=bool(data.get("is_active", True)),
        metadata=dict(data.get("metadata") or {}),
    )


def parse_workload_policy(data: dict[str, Any]) -> WorkloadPolicy:
    return make_workload_policy(
        faculty_id=data.get("faculty_id"),
        paper_distribution_division=data.get("paper_distribution_division", ""),
        excluded_usernames=frozenset(data.get("excluded_usernames") or []),
        excluded_name_snippets=tuple(data.get("excluded_name_snippets") or []),
        excluded_special_roles=frozenset(data.get("excluded_special_roles") or []),
        excluded_divisions=frozenset(data.get("excluded_divisions") or []),
        max_supervision_sessions=int(data.get("max_supervision_sessions", 0)),
        allow_cross_department=bool(data.get("allow_cross_department", False)),
        metadata=dict(data.get("metadata") or {}),
    )


def _parse_signer_slot(d: dict[str, Any]) -> SignerSlot:
    return SignerSlot(
        position=int(d["position"]),
        role=str(d.get("role", "")),
        username_hint=d.get("username_hint"),
        required=bool(d.get("required", True)),
    )


def parse_governance_flow(data: dict[str, Any]) -> GovernanceFlowConfig:
    r1 = [dict(s) for s in (data.get("round_1_signers") or [])]
    r2 = [dict(s) for s in (data.get("round_2_signers") or [])]
    return make_governance_flow_config(
        flow_name=data.get("flow_name", ""),
        round_1_signers=r1,
        round_2_signers=r2,
        faculty_id=data.get("faculty_id"),
        requires_governance_review=bool(data.get("requires_governance_review", True)),
        approval_quorum=data.get("approval_quorum"),
        metadata=dict(data.get("metadata") or {}),
    )


def parse_academic_group_config(data: dict[str, Any]) -> AcademicGroupConfig:
    return make_academic_group_config(
        faculty_id=int(data.get("faculty_id", 0)),
        code=str(data.get("code", "")),
        label_th=str(data.get("label_th", "")),
        label_en=str(data.get("label_en", "")),
        course_prefixes=tuple(data.get("course_prefixes") or []),
        legacy_aliases=tuple(data.get("legacy_aliases") or []),
        is_active=bool(data.get("is_active", True)),
        metadata=dict(data.get("metadata") or {}),
    )


def parse_role_mapping(data: dict[str, Any]) -> FacultyRoleMapping:
    return make_faculty_role_mapping(
        role=str(data.get("role", "")),
        faculty_id=data.get("faculty_id"),
        can_view_all=bool(data.get("can_view_all", False)),
        can_sign=bool(data.get("can_sign", False)),
        can_supervise=bool(data.get("can_supervise", False)),
        can_write_sections=bool(data.get("can_write_sections", False)),
        can_manage_print=bool(data.get("can_manage_print", False)),
        can_manage_config=bool(data.get("can_manage_config", False)),
        metadata=dict(data.get("metadata") or {}),
    )


def parse_platform_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Parse all config sections from a platform snapshot dict."""
    return {
        "faculty_configs": [parse_faculty_config(d) for d in snapshot.get("faculty_configs", [])],
        "workload_policies": [parse_workload_policy(d) for d in snapshot.get("workload_policies", [])],
        "governance_flows": [parse_governance_flow(d) for d in snapshot.get("governance_flows", [])],
        "academic_group_configs": [parse_academic_group_config(d) for d in snapshot.get("academic_group_configs", [])],
        "role_mappings": [parse_role_mapping(d) for d in snapshot.get("role_mappings", [])],
    }


def diff_platform_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compare two raw snapshot dicts, returning {added, removed, modified} by section."""
    result: dict[str, Any] = {}
    sections = {
        "faculty_configs": "faculty_id",
        "workload_policies": "faculty_id",
        "governance_flows": "flow_name",
        "academic_group_configs": "code",
        "role_mappings": "role",
    }
    for section, key_field in sections.items():
        before_items = {str(item.get(key_field)): item for item in before.get(section, [])}
        after_items = {str(item.get(key_field)): item for item in after.get(section, [])}

        added = [after_items[k] for k in after_items if k not in before_items]
        removed = [before_items[k] for k in before_items if k not in after_items]
        modified = [
            {"before": before_items[k], "after": after_items[k]}
            for k in before_items
            if k in after_items and before_items[k] != after_items[k]
        ]
        result[section] = {"added": added, "removed": removed, "modified": modified}
    return result


def validate_and_import_snapshot(
    snapshot: dict[str, Any],
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Validate snapshot and optionally apply it to registries.

    dry_run=True  — validate without applying (safe default).
    dry_run=False — validate then apply to in-memory registries.
    Returns {valid, errors, warnings, dry_run}.
    """
    errors: list[str] = []
    warnings: list[str] = []

    faculty_configs: list[FacultyConfig] = []
    workload_policies: list[WorkloadPolicy] = []
    governance_flows: list[GovernanceFlowConfig] = []
    academic_group_configs: list[AcademicGroupConfig] = []
    role_mappings: list[FacultyRoleMapping] = []

    for i, d in enumerate(snapshot.get("faculty_configs", [])):
        try:
            faculty_configs.append(parse_faculty_config(d))
        except Exception as exc:
            errors.append(f"faculty_configs[{i}]: {exc}")

    for i, d in enumerate(snapshot.get("workload_policies", [])):
        try:
            workload_policies.append(parse_workload_policy(d))
        except Exception as exc:
            errors.append(f"workload_policies[{i}]: {exc}")

    for i, d in enumerate(snapshot.get("governance_flows", [])):
        try:
            governance_flows.append(parse_governance_flow(d))
        except Exception as exc:
            errors.append(f"governance_flows[{i}]: {exc}")

    for i, d in enumerate(snapshot.get("academic_group_configs", [])):
        try:
            academic_group_configs.append(parse_academic_group_config(d))
        except Exception as exc:
            errors.append(f"academic_group_configs[{i}]: {exc}")

    for i, d in enumerate(snapshot.get("role_mappings", [])):
        try:
            role_mappings.append(parse_role_mapping(d))
        except Exception as exc:
            errors.append(f"role_mappings[{i}]: {exc}")

    if not faculty_configs:
        warnings.append("snapshot contains no faculty_configs")

    valid = len(errors) == 0

    if valid and not dry_run:
        from services.faculty_config_service import create_faculty_config
        from repositories.faculty_config_repository import InMemoryFacultyConfigRepository
        from services.governance_flow_service import register_governance_flow
        from services.workload_policy_service import register_workload_policy
        from services.academic_group_registry_service import register_academic_groups
        from services.faculty_role_mapping_service import register_role_mapping

        repo = InMemoryFacultyConfigRepository()
        for cfg in faculty_configs:
            try:
                create_faculty_config(cfg, repo)
            except ValueError:
                repo.save(cfg)

        for flow in governance_flows:
            register_governance_flow(flow)

        for policy in workload_policies:
            register_workload_policy(policy)

        groups_by_faculty: dict[int, list[AcademicGroupConfig]] = {}
        for grp in academic_group_configs:
            groups_by_faculty.setdefault(grp.faculty_id, []).append(grp)
        for fid, grps in groups_by_faculty.items():
            register_academic_groups(fid, grps)

        for mapping in role_mappings:
            register_role_mapping(mapping)

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "dry_run": dry_run,
    }
