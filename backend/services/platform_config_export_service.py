"""Platform config export service — serialize D3 config objects to JSON-safe dicts.

All functions are pure (no DB, no HTTP). Used by the import service and API layer.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from config_models.academic_group_config import AcademicGroupConfig
from config_models.faculty_config import FacultyConfig
from config_models.faculty_role_mapping import FacultyRoleMapping
from config_models.governance_flow import GovernanceFlowConfig, SignerSlot
from config_models.workload_policy import WorkloadPolicy

_SCHEMA_VERSION = "1.0"


def export_faculty_config(config: FacultyConfig) -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "faculty_id": config.faculty_id,
        "code": config.code,
        "name_th": config.name_th,
        "name_en": config.name_en,
        "email_domain": config.email_domain,
        "timezone": config.timezone,
        "academic_year_default": config.academic_year_default,
        "semester_default": config.semester_default,
        "is_active": config.is_active,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
        "metadata": dict(config.metadata),
    }


def export_workload_policy(policy: WorkloadPolicy) -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "faculty_id": policy.faculty_id,
        "paper_distribution_division": policy.paper_distribution_division,
        "excluded_usernames": sorted(policy.excluded_usernames),
        "excluded_name_snippets": list(policy.excluded_name_snippets),
        "excluded_special_roles": sorted(policy.excluded_special_roles),
        "excluded_divisions": sorted(policy.excluded_divisions),
        "max_supervision_sessions": policy.max_supervision_sessions,
        "allow_cross_department": policy.allow_cross_department,
        "metadata": dict(policy.metadata),
    }


def _export_signer_slot(slot: SignerSlot) -> dict[str, Any]:
    return {
        "position": slot.position,
        "role": slot.role,
        "username_hint": slot.username_hint,
        "required": slot.required,
    }


def export_governance_flow(flow: GovernanceFlowConfig) -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "faculty_id": flow.faculty_id,
        "flow_name": flow.flow_name,
        "round_1_signers": [_export_signer_slot(s) for s in flow.round_1_signers],
        "round_2_signers": [_export_signer_slot(s) for s in flow.round_2_signers],
        "requires_governance_review": flow.requires_governance_review,
        "approval_quorum": flow.approval_quorum,
        "created_at": flow.created_at,
        "metadata": dict(flow.metadata),
    }


def export_academic_groups(
    groups: list[AcademicGroupConfig],
) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": _SCHEMA_VERSION,
            "faculty_id": g.faculty_id,
            "code": g.code,
            "label_th": g.label_th,
            "label_en": g.label_en,
            "course_prefixes": list(g.course_prefixes),
            "legacy_aliases": list(g.legacy_aliases),
            "is_active": g.is_active,
            "metadata": dict(g.metadata),
        }
        for g in groups
    ]


def export_role_mappings(
    mappings: list[FacultyRoleMapping],
) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": _SCHEMA_VERSION,
            "faculty_id": m.faculty_id,
            "role": m.role,
            "can_view_all": m.can_view_all,
            "can_sign": m.can_sign,
            "can_supervise": m.can_supervise,
            "can_write_sections": m.can_write_sections,
            "can_manage_print": m.can_manage_print,
            "can_manage_config": m.can_manage_config,
            "metadata": dict(m.metadata),
        }
        for m in mappings
    ]


def build_platform_snapshot(
    *,
    faculty_configs: list[FacultyConfig],
    workload_policies: list[WorkloadPolicy],
    governance_flows: list[GovernanceFlowConfig],
    academic_group_configs: list[AcademicGroupConfig],
    role_mappings: list[FacultyRoleMapping],
    export_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a complete platform config snapshot dict."""
    return {
        "schema_version": _SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "faculty_configs": [export_faculty_config(c) for c in faculty_configs],
        "workload_policies": [export_workload_policy(p) for p in workload_policies],
        "governance_flows": [export_governance_flow(f) for f in governance_flows],
        "academic_group_configs": export_academic_groups(academic_group_configs),
        "role_mappings": export_role_mappings(role_mappings),
        "export_metadata": dict(export_metadata) if export_metadata else {},
    }


def platform_snapshot_to_json(snapshot: dict[str, Any]) -> str:
    """Serialize snapshot to a deterministic JSON string."""
    return json.dumps(snapshot, indent=2, sort_keys=True, default=str)
