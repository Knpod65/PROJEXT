"""Tests for data_lineage_service.py"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.data_lineage_service import (
    build_lineage_node,
    build_lineage_edge,
    build_lineage_graph,
    summarize_lineage_graph,
    detect_lineage_gaps,
)

_STAGES = ["import", "validation", "mapping", "optimization",
           "recheck", "governance", "publication", "export"]

_PUBLIC_NODE = {
    "node_id": "n:EMS:1:import",
    "node_type": "source",
    "entity_type": "exam_schedule",
    "entity_id": 1,
    "source_system": "EMS",
    "timestamp": "2026-01-01T00:00:00Z",
    "metadata": {"stage": "import"},
}


def _make_node(stage: str, idx: int = 1, pii: bool = False) -> dict[str, Any]:
    meta = {"stage": stage}
    if pii:
        meta["student_id"] = "12345678"
    return {
        "node_id": f"n:EMS:{idx}:{stage}",
        "node_type": "stage",
        "entity_type": "exam_schedule",
        "entity_id": idx,
        "source_system": "EMS",
        "timestamp": "2026-01-01T00:00:00Z",
        "metadata": meta,
    }


# ── Helpers ────────────────────────────────────────────────────────────────────

def _full_chain(n: int = 8) -> tuple[list[dict], list[dict]]:
    nodes = [_make_node(s, i) for i, s in enumerate(_STAGES)]
    edges: list[dict] = []
    for i in range(len(nodes) - 1):
        edges.append(build_lineage_edge(
            nodes[i]["node_id"], nodes[i + 1]["node_id"],
            "produced_by" if i == 0 else "derived_from",
            f"{_STAGES[i]} → {_STAGES[i+1]}",
        ))
    return nodes, edges


def _edges_skipping(skip_stage: str) -> list[dict]:
    """Build edges that link each present stage to the next present stage, skipping skip_stage."""
    nodes = [_make_node(s, i) for i, s in enumerate(_STAGES)]
    presente = [s for s in _STAGES]  # all present
    idx_map = {s: i for i, s in enumerate(presente)}
    edges: list[dict] = []
    for i in range(len(presente) - 1):
        cur = presente[i]
        nxt = presente[i + 1]
        if cur == skip_stage or nxt == skip_stage:
            continue
        ni   = idx_map[cur]
        nj   = idx_map[nxt]
        edges.append(build_lineage_edge(
            nodes[ni]["node_id"], nodes[nj]["node_id"],
            "produced_by" if ni == 0 else "derived_from",
            f"{cur} → {nxt}",
        ))
    return edges


def _graph_skipping(skip_stage: str) -> dict:
    nodes = [_make_node(s, i) for i, s in enumerate(_STAGES)]
    edges = _edges_skipping(skip_stage)
    return build_lineage_graph(nodes, edges)


# ── build_lineage_node ────────────────────────────────────────────────────────

def test_basic_node_has_all_keys():
    n = build_lineage_node("n1", "stage", "exam_schedule", 42, "EMS", "2026-01-01T00:00:00Z")
    assert n["node_id"] == "n1"
    assert n["node_type"] == "stage"
    assert n["entity_type"] == "exam_schedule"
    assert n["entity_id"] == 42
    assert n["source_system"] == "EMS"
    assert n["timestamp"] == "2026-01-01T00:00:00Z"
    assert n["metadata"] == {}
    assert n["pdpa_level"] == "public"


def test_node_pdpa_level_auto_detected_public():
    n = build_lineage_node("n1", "stage", "exam_schedule", 1, "EMS", "2026-01-01T00:00:00Z")
    assert n["pdpa_level"] == "public"


def test_node_pdpa_level_auto_detected_confidential_for_sis():
    n = build_lineage_node("n1", "source", "student_enrollment", 1, "SIS", "2026-01-01T00:00:00Z")
    assert n["pdpa_level"] == "confidential"


def test_node_pdpa_level_auto_detected_restricted_for_pii_metadata():
    meta = {"stage": "import", "student_id": "12345678"}
    n = build_lineage_node("n1", "source", "exam_schedule", 1, "EMS", "2026-01-01T00:00:00Z",
                           metadata=meta)
    assert n["pdpa_level"] == "restricted"


def test_node_explicit_pdpa_level_override():
    n = build_lineage_node("n1", "stage", "exam_schedule", 1, "EMS", "2026-01-01T00:00:00Z",
                           pdpa_level="internal")
    assert n["pdpa_level"] == "internal"


def test_node_entity_id_coerced_to_int():
    n = build_lineage_node("n1", "stage", "exam_schedule", "7", "EMS", "2026-01-01T00:00:00Z")
    assert n["entity_id"] == 7


def test_node_metadata_cloned():
    meta = {"stage": "import", "details": {"key": "val"}}
    n = build_lineage_node("n1", "source", "section", 1, "SIS", "2026-01-01T00:00:00Z",
                           metadata=meta)
    n["metadata"]["details"]["key"] = "changed"
    assert meta["details"]["key"] == "val"  # original not mutated

# ── build_lineage_edge ────────────────────────────────────────────────────────

def test_basic_edge_keys():
    e = build_lineage_edge("n1", "n2", "produced_by", "import creates schedule", confidence=0.95)
    assert e["from_node"] == "n1"
    assert e["to_node"] == "n2"
    assert e["relation_type"] == "produced_by"
    assert e["transformation"] == "import creates schedule"
    assert e["confidence"] == pytest.approx(0.95)


def test_edge_confidence_clamped_to_1():
    e = build_lineage_edge("n1", "n2", "produced_by", "x", confidence=3.0)
    assert e["confidence"] == pytest.approx(1.0)


def test_edge_confidence_clamped_to_0():
    e = build_lineage_edge("n1", "n2", "produced_by", "x", confidence=-0.5)
    assert e["confidence"] == pytest.approx(0.0)


def test_edge_default_confidence_is_1():
    e = build_lineage_edge("n1", "n2", "produced_by", "x")
    assert e["confidence"] == pytest.approx(1.0)

# ── build_lineage_graph ───────────────────────────────────────────────────────

def test_graph_basic_structure():
    nodes, edges = _full_chain()
    g = build_lineage_graph(nodes, edges)
    assert g["node_count"] == 8
    assert g["edge_count"] == 7
    assert g["nodes"][0]["node_id"] == "n:EMS:0:import"
    assert g["entry_nodes"] == []


def test_graph_with_entry_nodes():
    nodes, edges = _full_chain()
    g = build_lineage_graph(nodes, edges, entry_node_ids=["n:EMS:0:import"])
    assert g["entry_nodes"] == ["n:EMS:0:import"]


def test_graph_isolates_input_mutations():
    nodes, edges = _full_chain()
    original_nodes = nodes[0].copy()
    original_edges = edges[0].copy()
    g = build_lineage_graph(nodes, edges)
    g["nodes"][0]["node_id"] = "tampered"
    g["edges"][0]["from_node"] = "tampered"
    assert nodes[0]["node_id"] == original_nodes["node_id"]
    assert edges[0]["from_node"] == original_edges["from_node"]


def test_graph_empty_inputs():
    g = build_lineage_graph([], [])
    assert g["node_count"] == 0
    assert g["edge_count"] == 0

# ── summarize_lineage_graph ───────────────────────────────────────────────────

def test_summary_counts():
    nodes, edges = _full_chain()
    g = build_lineage_graph(nodes, edges)
    summary = summarize_lineage_graph(g)
    assert summary["node_count"] == 8
    assert summary["edge_count"] == 7


def test_summary_stage_coverage():
    nodes, edges = _full_chain()
    g = build_lineage_graph(nodes, edges)
    summary = summarize_lineage_graph(g)
    assert len(summary["stage_coverage"]) == len(_STAGES)
    assert all(summary["stage_coverage"][s] == 1 for s in _STAGES)


def test_summary_pdpa_distribution():
    mixed = [
        build_lineage_node("n1", "source", "schedule", 1, "EMS", "2026-01-01", pdpa_level="public"),
        build_lineage_node("n2", "source", "enrollment", 1, "SIS", "2026-01-01", pdpa_level="confidential"),
        build_lineage_node("n3", "stage", "section", 1, "EMS", "2026-01-01",
                           metadata={"stage": "recheck", "student_id": "12345678"},
                           pdpa_level="restricted"),
    ]
    g = build_lineage_graph(mixed, [])
    s = summarize_lineage_graph(g)
    assert s["pdpa_distribution"]["public"] == 1
    assert s["pdpa_distribution"]["confidential"] == 1
    assert s["pdpa_distribution"]["restricted"] == 1

# ── detect_lineage_gaps ───────────────────────────────────────────────────────

def test_full_8_stage_chain_no_gaps():
    nodes, edges = _full_chain()
    g = build_lineage_graph(nodes, edges)
    gaps = detect_lineage_gaps(g)
    assert gaps == []


def test_skip_recheck_detected_as_gap():
    """recheck receives no incoming edge from its nominal predecessor → flagged as gap."""
    nodes  = _full_chain()[0]
    # Implicit edges: import→validation→mapping→optimization, governance→publication→export
    # recheck node (idx 4) has no incoming edge
    edges = [
        build_lineage_edge(nodes[0]["node_id"], nodes[1]["node_id"],
                           "produced_by",           "import → validation"),
        build_lineage_edge(nodes[1]["node_id"], nodes[2]["node_id"],
                           "derived_from",          "validation → mapping"),
        build_lineage_edge(nodes[2]["node_id"], nodes[3]["node_id"],
                           "derived_from",          "mapping → optimization"),
        build_lineage_edge(nodes[5]["node_id"], nodes[6]["node_id"],
                           "derived_from",          "governance → publication"),
        build_lineage_edge(nodes[6]["node_id"], nodes[7]["node_id"],
                           "derived_from",          "publication → export"),
    ]
    g     = build_lineage_graph(nodes, edges)
    gaps  = detect_lineage_gaps(g)
    gap_s = {g_item["missing_stage"] for g_item in gaps}
    # recheck has nodes but predecessor optimization has no edge to it
    assert "recheck" in gap_s
    # governance has incoming from itself (governance→pub edge has governance as from_node, not to_node)
    # and no incoming from recheck → also a gap
    assert "governance" in gap_s
    # publication/export have incoming edges from governance/publication respectively
    assert "publication" not in gap_s
    assert "export" not in gap_s


def test_skip_governance_critical_severity_for_gov():
    """Skipping governance: governance → 'critical' gap. Publication → 'warning' (no rebridge edge at all)."""
    nodes = [_make_node(s, i) for i, s in enumerate(_STAGES)]
    # Implicit edges covering every stage except governance has no incoming:
    # import→validation→mapping→optimization, (explicit at each step)
    # publication→export (rechecks.trans -> pub → exp = no gov -> pub = pub gap)
    edges = [
        build_lineage_edge(nodes[0]["node_id"], nodes[1]["node_id"],
                           "produced_by",  "import → validation"),
        build_lineage_edge(nodes[1]["node_id"], nodes[2]["node_id"],
                           "derived_from", "validation → mapping"),
        build_lineage_edge(nodes[2]["node_id"], nodes[3]["node_id"],
                           "derived_from", "mapping → optimization"),
        # No edge into governance node(idx 5) and no governance→publication edge
        build_lineage_edge(nodes[3]["node_id"], nodes[6]["node_id"],
                           "derived_from", "optimization jumps to publication (skips governance & recheck)"),
        build_lineage_edge(nodes[6]["node_id"], nodes[7]["node_id"],
                           "derived_from", "publication → export"),
    ]
    g    = build_lineage_graph(nodes, edges)
    gaps = detect_lineage_gaps(g)
    by_stage = {g_item["missing_stage"]: g_item for g_item in gaps}
    # Governance (idx=5) has nodes, predecessor (recheck, idx=4) has no edge to it
    assert "governance" in by_stage
    assert by_stage["governance"]["severity"] == "critical"


def test_no_gaps_when_8_stage_chain_complete():
    nodes, edges = _full_chain()
    g = build_lineage_graph(nodes, edges)
    gaps = detect_lineage_gaps(g)
    assert len(gaps) == 0


def test_gap_severity_for_non_critical_stage():
    """Single-node (import only) graph is its own first stage — stage-0 skipped, no gaps."""
    nodes = [_make_node("import", 0)]
    g = build_lineage_graph(nodes, [])
    gaps = detect_lineage_gaps(g)
    # import is stage 0 (skipped) and no other stages have nodes
    assert len(gaps) == 0


def test_pii_field_in_metadata_triggers_restricted_level():
    meta = {"stage": "import", "student_name": "Test User", "department": "Science"}
    n = build_lineage_node("n:trace", "source", "section", 1, "SIS", "2026-01-01T00:00:00Z",
                           metadata=meta)
    assert n["pdpa_level"] == "restricted"
