# Optimization Explainability Model
## EMS Academic Operations Platform

**Status:** Implemented for read-only schedule observation.

---

## 1. Purpose

The explainability model turns generated optimization output into human-readable review data. It does not re-run the solver and does not alter scheduling decisions.

The model is designed for:

- staff review
- governance review
- audit trail preparation
- frontend explanation drawers

---

## 2. Explanation Categories

Current categories:

- `ROOM_SELECTION`
- `STAFF_ASSIGNMENT`
- `DISTRIBUTION_ASSIGNMENT`
- `SPLIT_DECISION`
- `TIMESLOT_SELECTION`
- `CONFLICT_AVOIDANCE`
- `FAIRNESS_BALANCING`
- `DOCUMENT_READINESS`
- `QR_READINESS`

Each explanation entry may include multiple categories when more than one factor contributed to the final allocation.

---

## 3. Core Fields

Each explanation entry exposes:

- `explanation_type`
- `source`
- `confidence_level`
- `confidence_score`
- `contributing_constraints`
- `tradeoff_notes`
- `fairness_notes`
- `operational_notes`
- `balancing_notes`
- `rejected_alternatives`
- `recommended_review_action`

Compatibility fields from the earlier phase remain available so existing consumers do not break.

---

## 4. Source Values

The source field describes where the explanation came from:

- `SOLVER_TRACE` - real solver trace, if available in a future integration
- `INPUT_CONSTRAINT` - direct inference from supplied schedule constraints
- `POST_HOC_HEURISTIC` - default when the explanation is reconstructed after generation
- `POLICY_RULE` - rule-derived reasoning such as staff distribution or operational policy

Current implementation primarily uses `POST_HOC_HEURISTIC`, `INPUT_CONSTRAINT`, and `POLICY_RULE`. The model does not claim solver trace provenance unless the optimizer actually exposes trace metadata.

---

## 5. Confidence Model

Confidence is expressed in two forms:

- `confidence_score` from 0 to 100
- `confidence_level` as `HIGH`, `MEDIUM`, or `LOW`

The confidence level is a coarse band for frontend badges and review prioritization. The score is deterministic and derived from the assembled factor weights.

---

## 6. Rejected Alternatives

Rejected alternatives are normalized into a frontend-safe list with fields such as:

- `candidate_type`
- `candidate_id`
- `rejection_reason`
- `violated_constraint`
- `severity`
- `improvement_hint`

The model avoids exposing student names, emails, or other raw PII in explanation payloads.

---

## 7. Recommended Review Action

Each explanation can suggest a review posture such as:

- standard review
- high-risk review
- normal approval review

This is advisory only and does not replace governance decisions.

---

## 8. Deferred Scope

Not implemented yet:

- live solver trace ingestion
- human annotation feedback loop
- explanation versioning
- explanation diffing across optimization runs
