# UI Residual Defect Backlog

**Date/time**: 2026-06-05 18:15:00 +07:00
**Source**: screenshot review after EMS UI alignment pass
**Status**: No P0/P1 defects found from screenshot review; four P2 polish items validated by targeted frontend build/i18n and route-smoke passes through 2026-06-15.

## Defect Register

| defect_id | route | screenshot | component/file | description | severity | expected template behavior | suggested fix | owner | status | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| UI-P2-002 | `/platform-config` | `docs/operations/demo-smoke-screenshots/ui-alignment-platform-config.png` | `PlatformConfiguration` page hero | Hero eyebrow displays raw key-like `PLATFORMCONFIG.EYEBROW`. | P2_POLISH | Hero eyebrow should be a localized, human-readable label. | Add or use a localized platform-config eyebrow string and verify Thai/English render cleanly. | Frontend/UI | VALIDATED | `platformConfig.eyebrow` added in EN/TH; build and i18n checks passed on 2026-06-08. |
| UI-P2-003 | `/governance` | `docs/operations/demo-smoke-screenshots/ui-alignment-governance.png` | `GovernanceCockpit` page hero | Hero eyebrow displays raw key-like `GOVERNANCE.EYEBROW`. | P2_POLISH | Hero eyebrow should be a localized, human-readable label. | Add or use a localized governance eyebrow string and verify Thai/English render cleanly. | Frontend/UI | VALIDATED | `governance.eyebrow` added in EN/TH; build and i18n checks passed on 2026-06-08. |
| UI-P2-004 | `/operational-health` | `docs/operations/demo-smoke-screenshots/ui-alignment-operational-health.png` | operational health status chip | Small status chip text `red` appears raw/technical. | P2_POLISH | Status chips should use localized EMS vocabulary and consistent badge labels. | Map technical health color to a localized status label such as critical/needs review/alert, then verify badge styling. | Frontend/UI | VALIDATED | Analytics badge now renders existing `dashboard.band.*` labels while preserving color logic; build and i18n checks passed on 2026-06-08. |
| UI-P2-005 | `/admin-intelligence-dashboard` | `docs/operations/demo-smoke-screenshots/admin-dashboard-visual-redesign.png` | admin intelligence dashboard | Text-heavy hierarchy exposed raw keys/tokens, concatenated units, misleading higher-is-better severity, and healthy recovery actions. | P2_POLISH | Dashboard should provide a calm visual hierarchy with localized display states and contextual actions. | Add a dedicated frontend presenter, five-card summary, visual analysis, capped priorities, and tabbed details without changing backend scoring. | Frontend/UI | VALIDATED | Frontend-only redesign validated on 2026-06-15; API `100%` displays healthy, connected database suppresses recovery action, and backend/readiness behavior is unchanged. |

## Summary

- P0 blocking defects: `0`.
- P1 fix-before-demo defects: `0`.
- P2 polish defects from screenshot review: `4`.
- P2 polish defects validated in targeted follow-up: `4`.
- Open P0/P1/P2 defects from this register: `0`.
- Final UI QA reconciliation state: `HUMAN_VISUAL_QA_PASSED_ACCEPTED_FOR_SUPERVISOR_REVIEW`.
- Code fixes were limited to frontend display/i18n only.
- Recommended next action: proceed to supervisor/finance review or the next feature gate; capture refreshed visual evidence later only if required.
