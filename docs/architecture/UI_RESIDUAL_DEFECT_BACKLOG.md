# UI Residual Defect Backlog

**Date/time**: 2026-06-05 18:15:00 +07:00
**Source**: screenshot review after EMS UI alignment pass
**Status**: No P0/P1 defects found from screenshot review; three P2 polish items validated by targeted frontend build/i18n pass on 2026-06-08.

## Defect Register

| defect_id | route | screenshot | component/file | description | severity | expected template behavior | suggested fix | owner | status | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| UI-P2-002 | `/platform-config` | `docs/operations/demo-smoke-screenshots/ui-alignment-platform-config.png` | `PlatformConfiguration` page hero | Hero eyebrow displays raw key-like `PLATFORMCONFIG.EYEBROW`. | P2_POLISH | Hero eyebrow should be a localized, human-readable label. | Add or use a localized platform-config eyebrow string and verify Thai/English render cleanly. | Frontend/UI | VALIDATED | `platformConfig.eyebrow` added in EN/TH; build and i18n checks passed on 2026-06-08. |
| UI-P2-003 | `/governance` | `docs/operations/demo-smoke-screenshots/ui-alignment-governance.png` | `GovernanceCockpit` page hero | Hero eyebrow displays raw key-like `GOVERNANCE.EYEBROW`. | P2_POLISH | Hero eyebrow should be a localized, human-readable label. | Add or use a localized governance eyebrow string and verify Thai/English render cleanly. | Frontend/UI | VALIDATED | `governance.eyebrow` added in EN/TH; build and i18n checks passed on 2026-06-08. |
| UI-P2-004 | `/operational-health` | `docs/operations/demo-smoke-screenshots/ui-alignment-operational-health.png` | operational health status chip | Small status chip text `red` appears raw/technical. | P2_POLISH | Status chips should use localized EMS vocabulary and consistent badge labels. | Map technical health color to a localized status label such as critical/needs review/alert, then verify badge styling. | Frontend/UI | VALIDATED | Analytics badge now renders existing `dashboard.band.*` labels while preserving color logic; build and i18n checks passed on 2026-06-08. |

## Summary

- P0 blocking defects: `0`.
- P1 fix-before-demo defects: `0`.
- P2 polish defects from screenshot review: `3`.
- P2 polish defects validated in targeted follow-up: `3`.
- Open P0/P1/P2 defects from this register: `0`.
- Code fixes were limited to frontend display/i18n only.
- Recommended next action: proceed to supervisor/finance review or the next feature gate; capture refreshed visual evidence later only if required.
