# Data Lineage Model

## Overview

The data lineage model tracks logical provenance of exam data across an 8-stage pipeline,
from raw data ingestion through to export or publication.

## Stage Definitions

| #  | Stage         | Description                                              |
|----|---------------|----------------------------------------------------------|
| 0  | `import`      | Raw data ingested from upstream source (SIS, LMS, HR)  |
| 1  | `validation`  | Import rows validated against schema                 |
| 2  | `mapping`     | Canonical field mapping applied                         |
| 3  | `optimization`| Scheduling optimization solver produces improved plan   |
| 4  | `recheck`     | Quality recheck / re-verification cycle                |
| 5  | `governance`  | Human governance review / approval workflow            |
| 6  | `publication` | Schedule published to exam participants                |
| 7  | `export`      | Final copies / PDFs dispatched to print shop + storage |

## Node Specification

### LineageNode TypedDict

```
node_id: str            "n:{source}:{record_id}:{stage}"
node_type: str          "source" | "stage" | "output"
entity_type: str        "exam_schedule" | "exam_submission" | "import_session" | ...
entity_id: int          Numeric primary key
source_system: str      "EMS" | "SIS" | "LMS" | "HR" | "Finance"
timestamp: str          ISO 8601
metadata: dict          Stage-specific fields incl. "stage" key
pdpa_level: str         "public" | "internal" | "confidential" | "restricted"
```

## Edge Specification

### LineageEdge TypedDict

```
from_node: str          Source node_id
to_node: str            Target node_id
relation_type: str      "produced_by" | "validated_by" | "derived_from" |
                        "signed_by" | "published_from" | "exported_from"
transformation: str     Human-readable description
confidence: float       0.0 – 1.0
```

## PDPA Boundary

- **public**:          Room names, building codes, counts, aggregate scores
- **internal**:        Invigilation load summaries, governance health index
- **confidential**:    SIS / LMS source lineage nodes (carry PII in metadata)
- **restricted**:      Any node whose metadata contains `student_id`, `student_name`,
                      `teacher_name`, `staff_name`, `qr_token`, `uploaded_file`,
                      `pdf_file`, or `export_data`

Restricted nodes must **never** appear in analytics summary outputs; the lineage
graph must carry their `pdpa_level` for downstream compliance auditors only.

## Gap Detection Algorithm

**Invariant:** Every stage that has at least one node in the graph must have at least one  
incoming cross-stage edge from its immediate predecessor in the required order.

### Algorithm

1. Build `stage_nodes: dict[str, set[node_id]]` from all node metadata.
2. Derive `connected_pairs: set[(from_stage, to_stage)]` from all edges.
3. For each required stage (skipping stage 0 / "import" which has no predecessor):
   - If the stage has nodes AND `(prev_stage, this_stage)` is absent from `connected_pairs`:
     - Report gap at this stage.

### Gap Severity

| Severity | Stage(s)                  |
|----------|---------------------------|
| critical | `governance`, `publication` |
| warning  | all others                |

### Example

Full 8-node chain with edges at all consecutive pairs → 0 gaps.

Chain where `governance→publication` edge is absent:
- governance in `stage_nodes` → check `(recheck, governance)` present ✓ → no gap at governance
- publication in `stage_nodes` → check `(governance, publication)` ABSENT → **gap at publication (warning)**

Chain where `recheck` has nodes but `optimization→recheck` edge is absent:
- recheck in `stage_nodes` → check `(mapping, recheck)` ABSENT → **gap at recheck (warning)**

## Gap Severity Matrix

| Stage            | Critical | Warning |
|------------------|----------|---------|
| import           | —        | warning |
| validation       | —        | warning |
| mapping          | —        | warning |
| optimization     | —        | warning |
| recheck          | —        | warning |
| governance       | **critical** | — |
| publication      | —        | **critical** |
| export           | —        | warning |

## Future: Replay Path

The lineage graph is designed to support a future **trace-replay** service that
can reconstruct any historical state of an exam section by following its node
chain backwards:

1. Start from a `replay_anchor_node_id` (typically the `publication` node).
2. Walk edges backwards to `source_system` nodes.
3. Materialise the reconstructed state as `LineageDiffResult` (not yet implemented).

No implementation of replay is included in D4; the node/edge spec is designed
to be replay-ready without actual replay logic.
