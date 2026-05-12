# Modernization Pass 2026-05-12 — Explainable Optimization (Phase A1)

Summary of changes:

- Added `backend/services/optimization_explanation_service.py` — generates deterministic explanations for room assignments based on actual schedule inputs (capacity, building preference, availability, staff load).
- Added `backend/services/optimization_quality_service.py` — computes a simple quality report with weighted scores: overall, fairness, room efficiency, and student conflict.
- Added tests in `backend/tests/test_optimization_explain_quality.py`.

Validation steps run: `compileall`, `import main`, `pytest backend/tests` — all green for the new tests.

Next actions: integrate these services into the optimization pipeline (non-destructive observation path), add richer heuristics and tie explanations to optimizer provenance, then implement multi-pass recheck categories and comparison engine.
