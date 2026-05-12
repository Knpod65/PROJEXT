# Optimization Quality Model
## EMS Academic Operations Platform

**Status:** Implemented for read-only observation of generated schedules.

---

## 1. Purpose

The quality model scores generated schedules after optimization completes. It is a post-hoc analysis layer and does not change the optimizer output.

It is intended for:

- approval readiness checks
- governance review
- operational risk ranking
- dashboard summaries

---

## 2. Component Scores

The current report exposes deterministic component scores including:

- `fairness_score`
- `room_efficiency_score`
- `invigilator_balance_score`
- `distribution_balance_score`
- `conflict_risk_score`
- `operational_complexity_score`
- `student_experience_score`
- `document_readiness_score`
- `qr_readiness_score`
- `governance_readiness_score`

Additional compatibility metrics such as accessibility and continuity remain available.

---

## 3. Quality Bands

The quality band maps the aggregated score and risk profile into one of:

- `EXCELLENT`
- `GOOD`
- `ACCEPTABLE`
- `NEEDS_REVIEW`
- `HIGH_RISK`

Banding is intentionally conservative. Any low readiness, high risk, or governance fragility can elevate the band.

---

## 4. Score Payload

Each quality report includes:

- `overall_score`
- `quality_band`
- `risk_level`
- `dominant_strengths`
- `dominant_weaknesses`
- `recommended_actions`
- `score_breakdown`
- `scoring_notes`

The report also keeps compatibility keys that existed before the quality expansion.

---

## 5. Deterministic Scoring Principles

The model follows these rules:

- use only available schedule data
- do not infer hidden solver state
- score conservatively when data is missing
- do not expose student names or other raw PII
- keep calculations stable across repeated runs for the same input

---

## 6. Scoring Notes

`scoring_notes` explains why a score moved up or down. Example notes include:

- missing QR readiness
- missing document readiness
- absent staff-load data
- conservative fallback due to missing room capacity
- custom scoring weights applied

These notes are meant for reviewers, not for the solver.

---

## 7. Deferred Scope

Not implemented yet:

- external benchmark scoring
- historical trend storage
- simulation mode against alternate schedules
- policy-driven score overrides
