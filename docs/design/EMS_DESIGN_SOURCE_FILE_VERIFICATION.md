# EMS Design Source File Verification

This file classifies the primary design-context sources for the EMS Claude Design handoff.

| File | Exists? | Tracked? | Current? | Use in Design? | Priority | Notes |
|---|---|---|---|---|---|---|
| `docs/architecture/UI_UX_CONSISTENCY_REPORT.md` | No | No | No | No | MISSING | Requested primary UI consistency source is not present in the real EMS root. Use the real-root substitute audit instead. |
| `docs/architecture/EMS_DESIGN_CONSISTENCY_CHECKLIST.md` | No | No | No | No | MISSING | Requested checklist is not present in the real EMS root. Do not fabricate its contents. |
| `docs/architecture/UX_UI_HUMANIZATION_AUDIT.md` | Yes | Yes | Current | Yes | MUST ATTACH | Real-root substitute for the missing consistency report. Strongest UX summary of strengths, inconsistencies, role UX, and humanization gaps. |
| `docs/architecture/FRONTEND_SUPERIOR_ENGINEER_AUDIT.md` | Yes | Yes | Current | Yes | MUST ATTACH | Frontend maturity, route drift, legacy/V2 coexistence, shell consistency, and known risk context. |
| `docs/architecture/EMS_FULL_SYSTEM_SUPERIOR_DEVELOPER_REVIEW.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | System maturity context; use for frontend risk framing, but do not let backend-only concerns distract visual design. |
| `docs/humanization/screenshot-atlas/major-pages.md` | Yes | Yes | Current | Yes | MUST ATTACH | Best live screenshot atlas index. Shows page intent, visible states, and operational meaning. |
| `docs/humanization/screenshot-atlas/SCREENSHOT_CAPTURE_REPORT.md` | Yes | Yes | Current | Yes | MUST ATTACH | Capture evidence, issue list, and screenshot freshness caveats. Key source for what is real versus broken. |
| `docs/humanization/screenshot-atlas/images/` | Yes | Yes | Current | Yes | MUST ATTACH | Real screenshot evidence folder. Claude Design should inspect filenames and use them as visual evidence, not fabricate replacements. |
| `docs/humanization/dashboard-guides/README.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Explains how dashboard pages should be interpreted operationally. Useful for role-aware design priorities. |
| `docs/humanization/journeys/README.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Defines workflow-driven visual journeys. Important for page sequencing and demo flow. |
| `docs/operations/DEMO_SCOPE_AND_BOUNDARIES.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Defines what the demo may and may not claim. Essential for honest design framing. |
| `docs/operations/DEMO_USER_JOURNEY_SCRIPT.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Presentational walkthrough and role progression. Helps prioritize what the redesigned UI should surface first. |
| `docs/operations/DEMO_ROUTE_SMOKE_MAP.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Route priority map for demo-critical surfaces. Useful for determining design sequence. |
| `docs/operations/DEMO_ACCOUNT_AND_DATA_READINESS.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Demo account/data gaps and empty-state expectations. Helps avoid false completeness claims. |
| `docs/deployment/PILOT_ROUTE_AND_AUTH_MAPPING.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Preliminary Faculty LAN route/auth mapping. Important if the redesign touches login or route hierarchy. |
| `docs/architecture/HYBRID_AUTH_MODEL_CMU_AND_PRINT_SHOP.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Explicitly separates CMU/POLSCI and print-shop lanes. Design must preserve that distinction. |
| `docs/architecture/PRINT_SHOP_AUTH_OPTIONS_MATRIX.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | External print-shop auth options and constraints. Keep for login/auth design only. |
| `docs/deployment/POLSCI_OAUTH_FLOW_ANALYSIS.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Observed POLSCI flow and open contract questions. Important if redesigning login/auth. |
| `docs/deployment/FACULTY_LARAVEL_AUTH_INTEGRATION_SPEC.md` | Yes | Yes | Current | Yes | SHOULD ATTACH | Integration boundary and verified-contract warning. Keep honest about what is not implemented yet. |
| `docs/architecture/DEMO_READINESS_SOURCE_REVIEW.md` | Yes | No | Current | Yes | CONTEXT ONLY | Useful cross-check for demo blockers and evidence gaps, but not required as a primary attachment. |
| `docs/operations/DEMO_AUTH_AND_PRINT_SHOP_SCOPE.md` | Yes | No | Current | Yes | CONTEXT ONLY | Additional auth/print-shop scope note. Useful background if Claude Design is asked to touch login or partner access. |

## Notes

- `Tracked?` reflects whether the file is tracked in the real EMS repository, not whether it is present in the parent workspace.
- `Current?` means the file is still relevant to the current handoff and not a dead historical artifact.
- `Use in Design?` means the file should influence the Claude Design brief or design prompt.
- `Priority` should be read literally:
  - `MUST ATTACH` for the strongest sources Claude Design should read directly.
  - `SHOULD ATTACH` for supporting context that materially improves the redesign brief.
  - `CONTEXT ONLY` for sources that help but are not essential attachments.
  - `DO NOT ATTACH` for backend-only, security-only, or out-of-scope material.
  - `MISSING` for requested files that do not exist in the real EMS root.

## Design Rationale

The missing UI consistency report and design checklist are treated as absent inputs, not merged from outside the real EMS root. The real EMS substitute sources are enough to build a strong handoff package without inventing unsupported content.