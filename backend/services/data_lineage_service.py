"""Data lineage service.

Tracks logical provenance across 8 stages:
  Import → validation → mapping → optimization → recheck → governance
  → publication → export

Pure logic. No DB, no ORM, no HTTP.
All functions accept and return plain Python dicts.
"""
from __future__ import annotations

import copy
import re
from collections import defaultdict
from typing import Any

_PDPA_RESTRICTED_FIELD_PATTERN = re.compile(
    r'(student_id|student_name|teacher_name|staff_name|qr_token|uploaded_file|pdf_file|export_data)',
    re.IGNORECASE,
)

_REQUIRED_STAGES = [
    "import", "validation", "mapping", "optimization",
    "recheck", "governance", "publication", "export",
]
_CRITICAL_STAGES: frozenset[str] = frozenset({"governance", "publication"})


def _detect_node_pdpa_level(node: dict[str, Any]) -> str:
    """Infer PDPA level from a node's metadata values."""
    metadata = node.get("metadata", {})
    if isinstance(metadata, dict):
        md_values = str(metadata)
    else:
        md_values = str(metadata)
    if _PDPA_RESTRICTED_FIELD_PATTERN.search(md_values):
        return "restricted"
    source = str(node.get("source_system", ""))
    if source.lower() in {"sis", "lms"}:
        return "confidential"
    return "public"


def build_lineage_node(
    node_id: str,
    node_type: str,
    entity_type: str,
    entity_id: int,
    source_system: str,
    timestamp: str,
    metadata: dict[str, Any] | None = None,
    pdpa_level: str | None = None,
) -> dict[str, Any]:
    """Build a single lineage node dict with a deep-copied metadata field."""
    meta_raw = metadata if metadata is not None else {}
    return {
        "node_id":     node_id,
        "node_type":   node_type,
        "entity_type": entity_type,
        "entity_id":   int(entity_id),
        "source_system": source_system,
        "timestamp":   timestamp,
        "metadata":    copy.deepcopy(meta_raw),
        "pdpa_level":  pdpa_level if pdpa_level else _detect_node_pdpa_level(
            {"metadata": meta_raw, "source_system": source_system}
        ),
    }


def build_lineage_edge(
    from_node: str,
    to_node: str,
    relation_type: str,
    transformation: str,
    confidence: float = 1.0,
) -> dict[str, Any]:
    """Build a single lineage edge dict."""
    e: dict[str, Any] = {
        "from_node":      from_node,
        "to_node":        to_node,
        "relation_type":  relation_type,
        "transformation": transformation,
        "confidence":     float(max(0.0, min(1.0, confidence))),
    }
    return {k: round(v, 4) if isinstance(v, float) else v for k, v in e.items()}


def build_lineage_graph(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    entry_node_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Assemble a lineage graph.  All nodes and edges are deep-copied on entry."""
    return {
        "nodes":        [copy.deepcopy(n) for n in nodes],
        "edges":        [copy.deepcopy(e) for e in edges],
        "entry_nodes":  list(entry_node_ids or []),
        "node_count":   len(nodes),
        "edge_count":   len(edges),
    }


def summarize_lineage_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Return a lightweight summary of an assembled lineage graph."""
    nodes = graph.get("nodes", [])
    stage_counts: dict[str, int] = defaultdict(int)
    pdpa_counts: dict[str, int] = defaultdict(int)
    for node in nodes:
        meta = node.get("metadata", {})
        if isinstance(meta, dict) and "stage" in meta:
            stage_counts[str(meta["stage"])] += 1
        else:
            stage_counts["unknown"] += 1
        pdpa_counts[str(node.get("pdpa_level", "public"))] += 1
    return {
        "node_count":       len(nodes),
        "edge_count":       len(graph.get("edges", [])),
        "stage_coverage":   dict(stage_counts),
        "pdpa_distribution":dict(pdpa_counts),
    }


def detect_lineage_gaps(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect missing edges between consecutive required pipeline stages.

    For each stage that has at least one node in the graph (skipping stage 0 /
    'import' which has no predecessor), verify that the immediately preceding
    required stage's nodes have at least one edge pointing at least one of this
    stage's nodes.  If no such cross-stage edge exists, report a gap.

    Stages with zero nodes are silently skipped (not reported as gaps).
    """
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # Stage → set of node_ids
    stage_nodes: dict[str, set[str]] = defaultdict(set)
    for node in nodes:
        meta = node.get("metadata", {})
        if isinstance(meta, dict) and "stage" in meta:
            stage_nodes[str(meta["stage"])].add(str(node.get("node_id", "")))

    # Adjacency: from_stage → to_stage (where cross-stage edges exist)
    connected_pairs: set[tuple[str, str]] = set()
    for edge in edges:
        from_id = edge.get("from_node", "")
        to_id   = edge.get("to_node",   "")
        from_s  = _stage_of(from_id, nodes)
        to_s    = _stage_of(to_id,   nodes)
        if from_s and to_s:
            connected_pairs.add((from_s, to_s))

    gaps: list[dict[str, Any]] = []
    for i, stage in enumerate(_REQUIRED_STAGES):
        if i == 0:
            continue
        if stage not in stage_nodes:
            continue
        prev = _REQUIRED_STAGES[i - 1]
        if (prev, stage) not in connected_pairs:
            gaps.append({
                "missing_stage": stage,
                "expected_from": prev,
                "expected_to":   stage,
                "severity": "critical" if stage in _CRITICAL_STAGES else "warning",
            })
    return gaps


def _stage_of(node_id: str, nodes: list[dict[str, Any]]) -> str | None:
    for n in nodes:
        if str(n.get("node_id", "")) == node_id:
            meta = n.get("metadata", {})
            if isinstance(meta, dict) and "stage" in meta:
                return str(meta["stage"])
            return None
    return None
