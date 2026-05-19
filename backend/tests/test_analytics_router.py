"""Tests for analytics router"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


def test_list_metrics_endpoint():
    resp = client.get("/api/analytics/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Spot-check one known metric
    codes = {m["metric_code"] for m in data}
    assert "opt_quality_score" in codes


def test_get_metric_endpoint_found():
    resp = client.get("/api/analytics/metrics/opt_quality_score")
    assert resp.status_code == 200
    data = resp.json()
    assert data["metric_code"] == "opt_quality_score"
    assert data["name"] == "Optimization Quality Score"


def test_get_metric_endpoint_not_found():
    resp = client.get("/api/analytics/metrics/nonexistent")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Metric 'nonexistent' not found"


def test_executive_summary_endpoint():
    resp = client.get("/api/analytics/executive-summary")
    assert resp.status_code == 200
    data = resp.json()
    # Must return the default dashboard shape
    required = {
        "overall_health_score", "risk_band", "optimization_quality_avg",
        "governance_blocker_count", "publication_ready_count",
        "workload_balance_score", "room_utilization_score", "pdpa_alert_count",
        "top_risks", "recommended_actions",
    }
    assert required.issubset(data.keys())
    assert data["risk_band"] == "red"
    assert data["overall_health_score"] == 0.0


def test_integration_contracts_endpoint():
    resp = client.get("/api/analytics/integration-contracts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 5  # SIS, HR, LMS, Finance, CMU SSO
    system_codes = {c["system_code"] for c in data}
    assert system_codes == {"sis", "hr", "lms", "finance", "cmu_sso"}


def test_router_is_included_in_main():
    """Assert that /api/analytics/* routes exist in the TestClient."""
    resp = client.get("/api/analytics/metrics")
    assert resp.status_code != 404  # not found means router not included