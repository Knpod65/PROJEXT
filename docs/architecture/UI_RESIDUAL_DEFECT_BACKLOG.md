# UI Residual Defect Backlog

**Date/time**: 2026-06-05 18:15:00 +07:00
**Source**: screenshot review after EMS UI alignment pass
**Status**: No P0/P1 defects found from screenshot review.

## Defect Register

| defect_id | route | screenshot | component/file | description | severity | expected template behavior | suggested fix | owner | status | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| UI-P2-002 | `/platform-config` | `docs/operations/demo-smoke-screenshots/ui-alignment-platform-config.png` | `PlatformConfiguration` page hero | Hero eyebrow displays raw key-like `PLATFORMCONFIG.EYEBROW`. | P2_POLISH | Hero eyebrow should be a localized, human-readable label. | Add or use a localized platform-config eyebrow string and verify Thai/English render cleanly. | Frontend/UI | OPEN | Does not block demo review. |
| UI-P2-003 | `/governance` | `docs/operations/demo-smoke-screenshots/ui-alignment-governance.png` | `GovernanceCockpit` page hero | Hero eyebrow displays raw key-like `GOVERNANCE.EYEBROW`. | P2_POLISH | Hero eyebrow should be a localized, human-readable label. | Add or use a localized governance eyebrow string and verify Thai/English render cleanly. | Frontend/UI | OPEN | Does not block demo review. |
| UI-P2-004 | `/operational-health` | `docs/operations/demo-smoke-screenshots/ui-alignment-operational-health.png` | operational health status chip | Small status chip text `red` appears raw/technical. | P2_POLISH | Status chips should use localized EMS vocabulary and consistent badge labels. | Map technical health color to a localized status label such as critical/needs review/alert, then verify badge styling. | Frontend/UI | OPEN | Does not block demo review. |

## Summary

- P0 blocking defects: `0`.
- P1 fix-before-demo defects: `0`.
- P2 polish defects: `3`.
- Code fixes are not part of this evidence pass.
- Recommended next action: proceed to supervisor/finance review or the next feature gate, while scheduling a targeted P2 UI polish pass.
