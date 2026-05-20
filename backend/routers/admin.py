"""Admin-only operational endpoints for shipped configuration pages."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth_utils import require_admin
from database import get_db
import models
from services.analytics_metric_registry_service import list_metrics
from services.integration_contract_registry_service import list_contracts
from services.platform_config_export_service import build_platform_snapshot

router = APIRouter()


@router.get("/platform-config")
def get_platform_config_snapshot(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    snapshot = build_platform_snapshot(
        faculty_configs=[],
        workload_policies=[],
        governance_flows=[],
        academic_group_configs=[],
        role_mappings=[],
        export_metadata={
            "source": "platform_config_export_service",
            "note": "DB-backed D3 config registries are not fully wired in this release. Configuration sections may return empty arrays until registry-backed persistence is enabled.",
            "requested_by": current_user.username,
        },
    )
    snapshot["integration_contracts"] = list_contracts()
    snapshot["analytics_metrics"] = list_metrics()
    return snapshot
