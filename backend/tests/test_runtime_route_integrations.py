"""Regression tests for runtime route wiring and shipped endpoint shapes."""
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main as main_module
from routers.admin import get_platform_config_snapshot
from routers.exports import get_audit_logs


def test_import_routers_start_cleanly():
    assert main_module.IMPORT_ROUTERS_ERROR is None


def test_main_app_exposes_required_runtime_routes():
    paths = {getattr(route, "path", "") for route in main_module.app.routes}
    assert "/api/dashboard/admin-intelligence" in paths
    assert "/api/dashboard/workload-duty-analytics" in paths
    assert "/api/import/sessions" in paths
    assert "/api/exports/audit-logs" in paths
    assert "/api/admin/platform-config" in paths


def test_platform_config_snapshot_shape():
    payload = get_platform_config_snapshot(
        db=MagicMock(),
        current_user=SimpleNamespace(username="admin.test"),
    )
    assert "faculty_configs" in payload
    assert "workload_policies" in payload
    assert "governance_flows" in payload
    assert "academic_group_configs" in payload
    assert "role_mappings" in payload
    assert "integration_contracts" in payload
    assert "analytics_metrics" in payload
    assert payload["export_metadata"]["source"] == "platform_config_export_service"


def test_audit_logs_route_shape(monkeypatch):
    actor = SimpleNamespace(full_name="Audit Admin", username="audit.admin")
    row = SimpleNamespace(
        id=10,
        actor=actor,
        action="EXPORT_AUDIT_LOGS",
        table_name="audit_logs",
        record_id=99,
        timestamp=SimpleNamespace(isoformat=lambda: "2026-05-20T10:00:00+00:00"),
        http_status=200,
        request_id="req-123",
    )

    monkeypatch.setattr(
        "routers.exports.ExportService.get_audit_logs",
        lambda db, filters: {"total": 1, "page": 1, "limit": 50, "logs": [row]},
    )

    payload = get_audit_logs(db=MagicMock(), current_user=SimpleNamespace())
    assert payload["total"] == 1
    assert payload["page"] == 1
    assert payload["limit"] == 50
    assert payload["logs"][0]["actor"] == "Audit Admin"
    assert payload["logs"][0]["request_id"] == "req-123"
