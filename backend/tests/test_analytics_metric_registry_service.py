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


# ── list_metrics ──────────────────────────────────────────────────────────────

def test_list_metrics_returns_list():
    result = list_metrics()
    assert isinstance(result, list)
    assert len(result) == 11  # 11 metric codes defined


def test_list_metrics_all_have_required_keys():
    required_keys = {
        "metric_code", "name", "category", "description", "unit",
        "aggregation", "pdpa_level", "dimension_keys",
        "source_entities", "refresh_mode",
    }
    for m in list_metrics():
        assert required_keys == required_keys.intersection(m.keys()), (
            f"Metric {m.get('metric_code')} missing keys: "
            f"{required_keys - m.keys()}"
        )


def test_list_metrics_shallow_copy_independence():
    original = list_metrics()
    assert original[0]["name"] == "Optimization Quality Score"

    # mutate returned list must not corrupt registry
    original[0]["name"] = "Hacked"
    fresh = list_metrics()
    assert fresh[0]["name"] == "Optimization Quality Score", (
        "Registry was mutated by caller — dict must be a shallow copy."
    )


def test_list_metrics_all_codes_unique():
    codes = [m["metric_code"] for m in list_metrics()]
    assert len(codes) == len(set(codes)), "Duplicate metric_code detected."


# ── get_metric ────────────────────────────────────────────────────────────────

def test_get_metric_known_code():
    m = get_metric("opt_quality_score")
    assert m["metric_code"] == "opt_quality_score"
    assert m["category"] == "optimization"
    assert m["aggregation"] == "avg"


def test_get_metric_returns_copy():
    m1 = get_metric("gov_health_score")
    m1["name"] = "Hacked"
    m2 = get_metric("gov_health_score")
    assert m2["name"] == "Governance Health Score"


def test_get_metric_unknown_code_raises_keyerror():
    with pytest.raises(KeyError, match="not found"):
        get_metric("does_not_exist")


def test_get_metric_keyerror_message_contains_valid_codes():
    try:
        get_metric("bad_code")
    except KeyError as exc:
        assert "opt_quality_score" in str(exc)
        assert "sched_coverage_pct" in str(exc)


# ── list_metrics_by_category ──────────────────────────────────────────────────

def test_list_metrics_by_category_optimization():
    result = list_metrics_by_category("optimization")
    assert len(result) == 1
    assert result[0]["metric_code"] == "opt_quality_score"


def test_list_metrics_by_category_governance():
    result = list_metrics_by_category("governance")
    assert len(result) == 1
    assert result[0]["metric_code"] == "gov_health_score"


def test_list_metrics_by_category_unknown_returns_empty():
    result = list_metrics_by_category("nonexistent")
    assert result == []


def test_list_metrics_by_category_preserves_category_field():
    for m in list_metrics():
        cat_result = list_metrics_by_category(m["category"])
        assert all(r["category"] == m["category"] for r in cat_result)


# ── list_public_metrics ───────────────────────────────────────────────────────

def test_list_public_metrics_no_internal():
    result = list_public_metrics()
    for m in result:
        assert m["pdpa_level"] == "public", (
            f"Metric {m['metric_code']} appeared in public list "
            f"but pdpa_level={m['pdpa_level']}"
        )


def test_list_public_metrics_all_known_public():
    codes = {m["metric_code"] for m in list_public_metrics()}
    actual_public = {m["metric_code"] for m in list_metrics()
                     if m["pdpa_level"] == "public"}
    assert codes == actual_public


def test_list_public_metrics_return_copy():
    result = list_public_metrics()
    if result:
        result[0]["name"] = "Hacked"
        fresh = list_public_metrics()
        assert fresh[0]["name"] != "Hacked"


# ── classify_metric_pdpa ──────────────────────────────────────────────────────

def test_classify_pdpa_optimization_returns_role_restricted():
    ds = classify_metric_pdpa("opt_quality_score")
    assert ds == DataSensitivity.role_restricted


def test_classify_pdpa_coverage_returns_public():
    ds = classify_metric_pdpa("sched_coverage_pct")
    assert ds == DataSensitivity.public


def test_classify_pdpa_qr_rate_returns_public():
    ds = classify_metric_pdpa("qr_pickup_rate_pct")
    assert ds == DataSensitivity.public


def test_classify_pdpa_conflict_returns_critical():
    ds = classify_metric_pdpa("stu_conflict_count")
    assert ds == DataSensitivity.critical


def test_classify_pdpa_governance_returns_role_restricted():
    ds = classify_metric_pdpa("gov_health_score")
    assert ds == DataSensitivity.role_restricted


def test_classify_pdpa_pdpa_alerts_returns_critical():
    ds = classify_metric_pdpa("pdpa_alert_count")
    assert ds == DataSensitivity.critical


def test_classify_pdpa_unknown_code_raises_keyerror():
    with pytest.raises(KeyError):
        classify_metric_pdpa("nonexistent")


# ── PDPA level coverage ───────────────────────────────────────────────────────

def test_all_pdpa_levels_are_valid():
    valid = {"public", "internal", "confidential", "restricted"}
    for m in list_metrics():
        assert m["pdpa_level"] in valid, (
            f"Metric {m['metric_code']} has invalid pdpa_level={m['pdpa_level']}"
        )


def test_all_aggregations_are_valid():
    valid = {"count", "sum", "avg", "ratio", "score"}
    for m in list_metrics():
        assert m["aggregation"] in valid, (
            f"Metric {m['metric_code']} has invalid aggregation={m['aggregation']}"
        )


def test_all_source_entities_non_empty():
    for m in list_metrics():
        assert m["source_entities"], (
            f"Metric {m['metric_code']} must have at least one source_entity"
        )


def test_all_refresh_modes_valid():
    valid = {"on_demand", "scheduled", "event_driven"}
    for m in list_metrics():
        assert m["refresh_mode"] in valid, (
            f"Metric {m['metric_code']} has invalid refresh_mode={m['refresh_mode']}"
        )
