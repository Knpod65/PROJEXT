# UI Role-Based Visual Evidence Report

**Date**: 2026-06-11  
**Result**: `ROLE_BASED_VISUAL_EVIDENCE_PASSED`  
**Scope**: narrow P2 payment-interface copy, blocked-role clarity, and unchanged role behavior

## Evidence Method

- Local EMS backend and frontend returned HTTP `200`.
- Screenshots were captured from the real rendered application with isolated local Chrome sessions.
- Documented local demo accounts were authenticated through the local EMS auth endpoint inside each browser session.
- No user browser profile, password store, backend file, or application data contract was modified.

## Role Evidence

| Role | Route/state | Visual result | Screenshot |
|---|---|---|---|
| admin | Official payment draft, review and draft-export gate | `DRAFT_NOT_AUTHORIZED` remains visible; review-only draft-export gate is visible; export control is restricted and disabled until a preview exists. | `docs/operations/demo-smoke-screenshots/role-admin-payment-draft.png` |
| admin | Draft-export control and safety banner | Draft XLSX is explicitly distinguished from official export, payment approval, and final authorization. | `docs/operations/demo-smoke-screenshots/role-admin-draft-export-button.png` |
| staff | Official payment draft | Review-comment and request/preview actions are available; no draft-export control is present; `DRAFT_NOT_AUTHORIZED` remains visible. | `docs/operations/demo-smoke-screenshots/role-staff-payment-draft.png` |
| staff | Payment-document settings | Page is visibly `Read-only`; no save or export action is present. | `docs/operations/demo-smoke-screenshots/role-staff-payment-settings-readonly.png` |
| teacher | Official payment draft | Access remains blocked and the shared unauthorized state now explains that the current workspace role cannot access the route. | `docs/operations/demo-smoke-screenshots/role-teacher-payment-blocked.png` |
| print shop | Official payment draft | Access remains blocked and the shared unauthorized state now explains that the current workspace role cannot access the route. | `docs/operations/demo-smoke-screenshots/role-printshop-payment-blocked.png` |

## P2 Outcome

- `P2_SAFE_FIX_NOW` fixed and visually evidenced: `3`.
- Payment warning copy now accurately describes gated draft XLSX output.
- Disabled draft-export tooltip copy uses localized human-readable gate language.
- Shared blocked-role state includes a localized explanatory description.
- `P2_DEFER_VISUAL_ONLY`: broad legacy/custom operational-page polish.
- `P2_DEFER_WORKLOAD_SCOPE_NOT_TOUCHING`: workload-route presentation.
- `P2_DEFER_AUTH_LIMITATION`: unavailable role/data states, if encountered in later evidence passes.

## Safety Confirmation

- `DRAFT_NOT_AUTHORIZED` weakened or removed: `NO`.
- Backend, API contract, route permission, payment calculation, settings, review, or draft-export gate behavior changed: `NO`.
- Payment approval or final authorization added: `NO`.
- Official/final export added: `NO`.
- Workload, Work H, opencourse, coinstruc, or teaching-workload files changed: `NO`.
- Readiness score changed: `NO`.

