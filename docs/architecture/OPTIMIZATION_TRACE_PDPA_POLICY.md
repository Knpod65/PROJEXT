# Optimization Trace PDPA Policy
## D2 Trace Safety Rules

---

## 1. Purpose

Optimization traces are useful only if they remain safe to inspect, export, and replay. D2 therefore adds an explicit trace-specific PDPA policy on top of the existing event PDPA policy.

Primary implementation:
- `backend/policies/optimization_trace_pdpa_policy.py`

Supporting enforcement:
- `backend/policies/event_pdpa_policy.py`
- `backend/services/optimization_trace_context.py`
- `backend/services/optimization_trace_replay_service.py`

---

## 2. Protected Data Classes

Restricted keys:
- `student_id`
- `student_ids`
- `token`
- `qr`
- `qr_payload`
- `qr_code`
- `secret`
- `password`

Confidential keys:
- `student_name`
- `student_names`
- `candidate_name`
- `full_name`
- `display_name`
- `email`
- `phone`
- `mobile`
- `attachment_path`
- `pdf_original_path`
- `pdf_stripped_path`

These keys must never appear in raw form inside optimization trace output.

---

## 3. Policy API

Implemented functions:
- `classify_trace_event(event)`
- `mask_trace_event(event)`
- `assert_trace_event_safe(event)`
- `classify_trace_batch(events)`

Behavior:
- classification detects raw and already-masked sensitive keys
- masking returns a deep-copied redacted event
- assertion raises on any raw sensitive field
- batch classification supports reporting and governance review

---

## 4. Enforcement Rules

Hard rules:
- no raw student names
- no raw student identifiers
- no email
- no phone
- no QR payload
- no token
- no password or secret
- no sensitive attachment path

Allowed:
- aggregate counts
- room IDs
- schedule IDs
- section IDs
- candidate IDs that are not sensitive identities
- quality and governance summary values
- sanitized metadata

Mask value:
- `[REDACTED]`

Masked values are treated as safe.

---

## 5. D2 Data Flow

Safety is applied in layers:

1. Trace context sanitizes event metadata before storing events in memory.
2. Trace PDPA policy masks or rejects sensitive keys.
3. Event PDPA policy remains available for broader envelope-level sanitization.
4. Replay helpers strip known sensitive keys during normalization.

This means native trace events are protected before they are:
- attached to reports
- converted to event envelopes
- replayed into lineage
- returned from boundary instrumentation

---

## 6. Classification Semantics

Recommended classifications:
- `restricted` when restricted keys are present or masked
- `confidential` when confidential-only keys are present or masked
- `internal` when no sensitive keys are detected

Batch classification returns:
- `total_events`
- `unsafe_event_count`
- `safe_event_count`
- `sensitive_keys`
- `masked_keys`
- `recommended_classification`

---

## 7. Operational Guidance

When adding new trace metadata:
- prefer counts, IDs, codes, booleans, and normalized labels
- never store names, contact details, or raw QR/token material
- treat attachment paths as sensitive unless clearly non-sensitive
- keep payloads JSON-safe and minimal

When expanding deeper solver trace later:
- apply this policy before persistence
- extend the sensitive-key allowlist and denylist deliberately
- validate new event shapes with dedicated tests

---

## 8. Future Work

Deferred but recommended:
- persisted trace-classification tags in a future trace store
- automated DPO review checklist for new trace metadata keys
- UI badges showing trace safety classification
