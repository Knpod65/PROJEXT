# EMS Demo/Review End-To-End Checklist

**Release candidate**: `EMS_DEMO_REVIEW_RC_1`  
**Date**: 2026-06-12

## 1. App Availability

- [x] Backend health returns HTTP `200`.
- [x] Frontend loads.
- [x] All `44` registered renderable URLs pass HTTP smoke; not-found behavior also returns HTTP `200`.

## 2. UI Readiness

- [x] P0 blockers: `0`.
- [x] P1 blockers: `0`.
- [x] Residual P2 decisions remain documented.
- [x] Quiet Institutional Command Center template remains applied.
- [x] Current screenshot evidence is available.

## 3. Payment Document Settings

- [x] Term is `2/2568`.
- [x] Weekday rate is `120`.
- [x] Weekend rate is `200`.
- [x] Responsible group is `Education_Student_Quality`.
- [x] Settings remain configurable.
- [x] Settings do not authorize payment.

## 4. Review Workflow

- [x] Persistent review record exists.
- [x] Review comment exists.
- [x] Review status is `ACCEPTED_FOR_DRAFT_EXPORT`.
- [x] Review remains non-authorizing.

## 5. Draft Preview

- [x] Draft uses settings-backed rates.
- [x] Calculation status is `CALCULATED_FROM_SETTINGS`.
- [x] `DRAFT_NOT_AUTHORIZED` is visible.
- [x] Missing or incomplete settings block monetary calculation, confirmed by the full backend suite.

## 6. Draft Export

- [x] Draft XLSX export is gated.
- [x] Export is allowed only after review acceptance and safety preconditions.
- [x] Workbook is labeled draft/review-only.
- [x] Export is not final payment approval.
- [x] Export is not final authorization.

## 7. Role Behavior

- [x] Admin evidence captured.
- [x] Staff evidence captured.
- [x] Teacher is blocked from restricted payment workspaces.
- [x] Print shop is blocked from restricted payment workspaces.

## 8. Safety Boundaries

- [x] Final payment approval is absent.
- [x] Final authorization is absent.
- [x] Official-final export is absent.
- [x] `payment_authorization_enabled=false`.
- [x] `final_export_enabled=false`.
- [x] Manual paper rows are not persisted as final payment truth.
- [x] Workload logic and presentation were not changed.

## Result

`EMS_DEMO_REVIEW_RC_1_VALIDATED_WITH_DOCUMENTED_CONSTRAINTS`

