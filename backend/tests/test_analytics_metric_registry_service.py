"""Tests for analytics_metric_registry_service.py"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.analytics_metric_registry_service import (
    list_metrics,
    get_metric,
    list_metrics_by_category,
    list_public_metrics,
    classify_metric_pdpa,
)
from policies.pdpa_policy import DataSensitivity


def test_list_metrics_returns_all_11():
    metrics = list_metrics()
    assert len(metrics) == 11
    codes = {m["metric_code"] for m in metrics}
    assert "opt_quality_score" in codes
    assert "sched_coverage_pct" in codes
    assert "wkl_invigilation_balance_score" in codes
    assert "rms_avg_utilization_pct" in codes
    assert "gov_health_score" in codes
    assert "pub_ready_count" in codes
    assert "prt_throughput_score" in codes
    assert "qr_pickup_rate_pct" in codes
    assert "stu_conflict_count" in codes
    assert "fac_oper_score" in codes
    assert "pdpa_alert_count" in codes


def test_all_metrics_have_required_keys():
    required = {"metric_code", "name", "category", "description", "unit",
                "aggregation", "pdpa_level", "dimension_keys", "source_entities", "refresh_mode"}
    for m in list_metrics():
        assert required.issubset(m.keys()), f"Missing keys in {m['metric_code']}"


def test_all_pdpa_levels_valid():
    valid = {"public", "internal", "confidential", "restricted"}
    for m in list_metrics():
        assert m["pdpa_level"] in valid, f"Invalid pdpa_level: {m['pdpa_level']}"


def test_get_metric_returns_single():
    m = get_metric("opt_quality_score")
    assert m["metric_code"] == "opt_quality_score"
    assert m["name"] == "Optimization Quality Score"


def test_get_metric_missing_raises_key_error():
    with pytest.raises(KeyError):
        get_metric("nonexistent_metric")


def test_list_metrics_by_category_optimization():
    results = list_metrics_by_category("optimization")
    assert len(results) == 1
    assert results[0]["metric_code"] == "opt_quality_score"


def test_list_metrics_by_category_returns_only_matching():
    results = list_metrics_by_category("governance")
    assert all(m["category"] == "governance" for m in results)
    assert len(results) == 1


def test_list_metrics_by_category_unknown_returns_empty():
    assert list_metrics_by_category("nonexistent_category") == []


def test_list_public_metrics_only_public_level():
    results = list_public_metrics()
    assert all(m["pdpa_level"] == "public" for m in results)
    assert len(results) >= 1


def test_public_metrics_excludes_restricted():
    codes = {m["metric_code"] for m in list_public_metrics()}
    assert "stu_conflict_count" not in codes


def test_classify_metric_pdpa_returns_data_sensitivity():
    assert classify_metric_pdpa("opt_quality_score") == DataSensitivity.public


def test_classify_metric_pdpa_internal():
    assert classify_metric_pdpa("gov_health_score") == DataSensitivity.authenticated


def test_classify_metric_pdpa_restricted():
    assert classify_metric_pdpa("stu_conflict_count") == DataSensitivity.sensitive


def test_classify_metric_pdpa_missing_raises_key_error():
    with pytest.raises(KeyError):
        classify_metric_pdpa("nonexistent_metric")


def test_metrics_have_no_none_pdpa_level():
    for m in list_metrics():
        assert m["pdpa_level"] is not None
        assert isinstance(m["pdpa_level"], str)
