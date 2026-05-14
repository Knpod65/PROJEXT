# Optimization Trace Architecture
## EMS Academic Operations Platform — Enterprise Maturity Phase T1
**Date:** 2026-05-14

---

## 1. Purpose

The optimization trace layer provides post-hoc, structured traceability for every
decision the CP-SAT optimization engine makes during schedule generation. It does NOT
modify the optimizer. All trace services are read-only and operate on already-generated
outputs.

---

## 2. Design Principles

- **Post-hoc only**: No changes to optimizer code. Trace services read existing observer payloads.
- **Frozen dataclasses**: All trace objects are immutable to prevent accidental mutation.
- **PII protection**: `strip_pii()` from `optimization_trace_policy.py` blocks student identifiers.
- **Three-layer trace**: Candidate rejections → Constraint evaluation → Final decisions.

---

## 3. Trace Object Hierarchy

```
OptimizationDecision (top-level per schedule entry)
│
├── CandidateTrace[]         -- rejected/accepted rooms, staff, timeslots
├── ConstraintTrace[]        -- constraint violations with severity mapping
└── DecisionLogEntry         -- chosen allocation with confidence and policy source
```

### 3.1 CandidateTrace

```python
@dataclass(frozen=True)
class CandidateTrace:
    trace_id: str           # uuid4
    section_id: Any
    candidate_type: str     # "ROOM" | "STAFF" | "TIMESLOT"
    candidate_id: Any
    decision: str           # "ACCEPTED" | "REJECTED"
    reason: str
    constraint_name: str | None
    severity: str           # "INFO" | "WARNING" | "HARD_FAIL"
    optimization_stage: str
    domain: str             # "optimization"
    timestamp: str          # ISO 8601
```

Entry-point: `build_candidate_traces(schedule_entries: list[dict]) -> list[CandidateTrace]`

Source fields read:
- `entry["rejected_room_candidates"]`
- `entry["rejected_staff_candidates"]`

### 3.2 ConstraintTrace

```python
@dataclass(frozen=True)
class ConstraintTrace:
    trace_id: str
    constraint_name: str
    triggered: bool
    severity: str       # "HARD_FAIL" | "WARNING" | "INFO" | "SUGGESTION"
    optimization_stage: str
    message: str
    category: str
    blocking: bool      # always True for HARD_FAIL
    domain: str
    audit_metadata: dict
    timestamp: str
```

Entry-point: `build_constraint_traces(recheck_issues: list[dict]) -> list[ConstraintTrace]`

Severity normalization:
- `"ERROR"` → `"HARD_FAIL"`
- `"WARN"` → `"WARNING"`
- `"SUGGEST"` → `"SUGGESTION"`

### 3.3 DecisionLogEntry

```python
@dataclass(frozen=True)
class DecisionLogEntry:
    log_id: str
    section_id: Any
    course_id: str | None
    chosen_room_id: Any
    chosen_room_capacity: int | None
    chosen_staff_ids: tuple
    exam_date: str | None
    exam_time: str | None
    split_count: int
    decision_factors: tuple[str, ...]
    confidence: str         # "HIGH" | "MEDIUM" | "LOW"
    policy_source: str
    governance_relevance: str  # "NONE" | "REVIEW_REQUIRED" | "BLOCKED"
    audit_metadata: dict
    timestamp: str
```

Entry-point: `build_decision_log(observer_payload: dict) -> list[DecisionLogEntry]`

`governance_relevance` mapping:
- `AUTO_APPROVED` → `"NONE"`
- `APPROVAL_REQUIRED` / `MANUAL_REVIEW_REQUIRED` / `ESCALATION_REQUIRED` → `"REVIEW_REQUIRED"`
- `BLOCKED` → `"BLOCKED"`

---

## 4. Data Flow

```
ExamSchedule ORM objects
    ↓ (observer normalization)
observer_payload["schedule_entries"]   ← rejected_room_candidates, rejected_staff_candidates
    ↓
build_candidate_traces()  →  list[CandidateTrace]

observer_payload["issues"]             ← recheck constraint violations
    ↓
build_constraint_traces()  →  list[ConstraintTrace]

observer_payload (full)
    ↓
build_decision_log()  →  list[DecisionLogEntry]
```

---

## 5. Typed Event Vocabulary

`OptimizationEventType` (15 values) in `events/optimization_events.py`:

| Event | Stage |
|---|---|
| OPTIMIZATION_STARTED / FINISHED | GOVERNANCE |
| ROOM_CANDIDATE_REJECTED / ACCEPTED | CANDIDATE_GENERATION |
| INVIGILATOR_REJECTED / ACCEPTED | CANDIDATE_GENERATION |
| TIMESLOT_REJECTED / ACCEPTED | CANDIDATE_GENERATION |
| CONSTRAINT_TRIGGERED | CONSTRAINT_EVALUATION |
| HARD_CONSTRAINT_FAILED | CONSTRAINT_EVALUATION |
| SOFT_CONSTRAINT_PENALIZED | SCORING |
| QUALITY_SCORE_ADJUSTED | SCORING |
| ROOM_SPLIT_APPLIED | SELECTION |
| GOVERNANCE_ESCALATED | GOVERNANCE |
| RECHECK_WARNING_GENERATED | RECHECK |

---

## 6. Audit Guarantees

- All trace objects carry `timestamp` (ISO 8601 UTC) and `domain = "optimization"`.
- `audit_metadata` dict in ConstraintTrace and DecisionLogEntry is structurally reserved for future persistence.
- PII fields (`student_id`, `student_ids`, `student_name`, `email`, `mobile`) are stripped before any trace object is created.

---

## 7. Files

| File | Role |
|---|---|
| `events/optimization_events.py` | OptimizationEventType enum, stage constants |
| `services/optimization_candidate_trace_service.py` | CandidateTrace factory |
| `services/optimization_decision_log_service.py` | DecisionLogEntry factory |
| `services/optimization_constraint_trace_service.py` | ConstraintTrace factory |
| `policies/optimization_trace_policy.py` | TraceEventType, TraceEvent, strip_pii() |
| `tests/test_optimization_candidate_trace_service.py` | 20 tests |
| `tests/test_optimization_decision_log_service.py` | 22 tests |
| `tests/test_optimization_constraint_trace_service.py` | 20 tests |
