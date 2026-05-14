# Lifecycle Timeline Reconstruction
## EMS Academic Operations Platform
**Date:** 2026-05-14
**Phase:** D1.5

---

## 1. Purpose

EMS events come from multiple sources: governance trace events (from
`governance_trace_service`), domain events (from `DomainEvent`/`EventEnvelope`),
audit events, and optimization trace events. Each source uses a slightly different
field naming convention.

The lifecycle timeline service normalizes all of these into a single uniform
timeline, enabling:
- Executive-facing audit trails
- Lifecycle forensics (when was a schedule published? who approved it?)
- Replay and read-model construction (future)
- Cross-source event correlation

---

## 2. Implementation

**File:** `backend/services/lifecycle_timeline_service.py`

### Functions

```python
def build_lifecycle_timeline(events: list[dict]) -> list[dict]
# Normalize → sort by timestamp (Nones last)

def summarize_lifecycle_timeline(timeline: list[dict]) -> dict
# Compute aggregate summary from normalized timeline
```

### Timeline Item Shape

```python
{
    "timestamp":      str | None,
    "event_type":     str,          # "UNKNOWN" if missing
    "domain":         str,          # "unknown" if missing
    "actor_id":       int | None,
    "actor_role":     str | None,
    "summary":        str,          # human-readable description
    "severity":       str,          # INFO | WARNING | HIGH_RISK | CRITICAL | HARD_FAIL
    "aggregate_type": str | None,
    "aggregate_id":   str | None,
}
```

### Field Extraction Fallbacks

| Output field | Primary key | Fallback | Default |
|---|---|---|---|
| `event_type` | `event_type` | `type` | `"UNKNOWN"` |
| `domain` | `domain` | — | `"unknown"` |
| `actor_id` | `actor_id` | `actor` | `None` |
| `actor_role` | `actor_role` | — | `None` |
| `summary` | `details` | `description`, `summary`, `event_type`, `type` | `"UNKNOWN"` |
| `severity` | `severity` | — | `"INFO"` |
| `aggregate_type` | `aggregate_type` | — | `None` |
| `aggregate_id` | `aggregate_id` | — | `None` |

### Summary Shape

```python
{
    "event_count":      int,
    "first_event_at":   str | None,   # earliest timestamp
    "last_event_at":    str | None,   # latest timestamp
    "has_rollback":     bool,         # any event_type containing "ROLL"
    "has_override":     bool,         # any event_type containing "OVERRIDE"
    "has_publication":  bool,         # any event_type containing "PUBLISH"
    "highest_severity": str,          # worst severity across all events
}
```

### Severity Ordering

```
INFO < WARNING < HIGH_RISK < HARD_FAIL < CRITICAL
```

---

## 3. Event Source Compatibility

| Source | Key format | Notes |
|---|---|---|
| `governance_trace_service` | `type`, `details`, `severity` | Uses "type" not "event_type" |
| `DomainEvent` (asdict) | `event_type`, `domain`, `actor_id`, `payload` | Standard format |
| `EventEnvelope` (to_dict) | `event_type`, `domain`, `actor_id`, `actor_role`, `severity` | Richest format |
| `build_audit_event()` | `audit_event_id`, `action`, `resource_type` | Different shape — not directly a timeline event |

---

## 4. Usage Example

```python
from services.lifecycle_timeline_service import (
    build_lifecycle_timeline,
    summarize_lifecycle_timeline,
)

# Mix sources: governance trace + EventEnvelope dicts
all_events = [
    *governance_trace_events,         # from build_governance_trace()
    *[event_envelope_to_dict(e) for e in envelope_events],
]

timeline = build_lifecycle_timeline(all_events)
summary = summarize_lifecycle_timeline(timeline)

# summary.has_rollback → show rollback warning badge
# summary.highest_severity → color-code the timeline header
# timeline → render chronological event list in UI
```

---

## 5. What Is Deferred

- **DB-backed timeline storage**: Current implementation is pure in-memory
  reconstruction from passed-in events. A future persistent event store would
  allow `SELECT * FROM event_store WHERE aggregate_id = ?` style queries.
- **Pagination and filtering**: No pagination or filter parameters yet. Suitable
  for session-level timelines (typically 10–50 events). Add when needed.
- **Cross-session timeline correlation**: Currently scoped to a single call. Future
  work: correlated timelines across related sessions via `correlation_id`.
