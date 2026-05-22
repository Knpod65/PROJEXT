# WIP Resolution Plan

**Date**: 2026-05-22

This plan defines the explicit action for every file on the `wip/ems-orphan-services-transfer` branch.

## Production Candidates (Category A) — Review for Safe Promotion

| File | Action | Reason | Merge Now? | Next Step |
|------|--------|--------|------------|-----------|
| dashboard_alert_service.py | Wire deeper + add tests | Already partially used in Phase C | No | Create feature branch off main, add tests, cherry-pick if passes |
| workload_forecasting_service.py | Production candidate | Explainable, low risk | No | Same as above |
| staffing_forecast_service.py | Production candidate | Useful for staffing risk | No | Same as above |
| room_pressure_forecast_service.py | Production candidate | Useful for room pressure | No | Same as above |

## Archive as Prototypes (Category B & D)

All other files have been moved (or will be moved) to `docs/architecture/prototypes/` on the WIP branch.

- distributed_cognition_service.py
- educational_futures_service.py
- federated_intelligence_service.py
- governance_reasoning_service.py
- institutional_coordination_service.py
- institutional_registry_service.py
- institutional_state_model_service.py
- institutional_trust_service.py
- national_resilience_service.py
- self_calibration_service.py
- faculty_config_registry.py
- unit_context_service.py
- policy_pack_registry.py
- unit_scope_policy.py

**Action**: Keep on WIP branch in prototypes folder. Do not merge to main.

## Duplicate / Overlap (Category C)

- institutional_state_model_service.py → Overlaps existing dashboard state logic.

**Action**: Document in DUPLICATE_SERVICE_REVIEW.md. Likely delete or absorb useful parts only.

## Overall Strategy

1. Never merge the entire WIP branch.
2. Only promote the 4 forecasting/alert services after they pass tests on a clean feature branch from main.
3. All speculative services remain archived on the WIP branch.
4. Update this plan and the audit document whenever decisions change.

**Current Recommendation (as of 2026-05-22)**: Do not promote any services to main yet. Continue with documentation and hardening work on main first.
