# UI Residual Audit Explorer Hotfix Report

Date: 2026-06-02

## Scope

Root confirmed: `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`

This hotfix is limited to the Audit Explorer frontend UI. It does not implement invigilation rate rules, payment calculation, payment approval, official export, backend payment logic, or any extra-teaching workload workflow.

## Screenshot Issue Summary

The post-commit visual smoke for `1deb2ec fix(ui): align drifted operational pages with EMS design system` still showed residual Audit Explorer drift:

- Missing translation rendered as raw `audit.eyebrow`.
- Tab controls appeared as raw/default browser buttons.
- The section/tab area still looked scaffold-like instead of using the EMS design system.

## Source Issue Found

The issue was actual source code, not only a stale dev server:

- `frontend/src/pages/AuditExplorer.tsx` still referenced `translate("audit.eyebrow")`.
- `audit.eyebrow` was not present in the locale dictionaries.
- Audit Explorer still used `renderTabButton`, which creates native `<button>` elements outside the shared EMS `Tabs` component.

## Files Changed

- `frontend/src/pages/AuditExplorer.tsx`
- `frontend/src/i18n/en.ts`
- `frontend/src/i18n/th.ts`
- `docs/architecture/UI_RESIDUAL_AUDIT_EXPLORER_HOTFIX_REPORT.md`

## Fix Summary

- Replaced `audit.eyebrow` usage with `audit.consoleEyebrow`.
- Added English and Thai locale values for the Audit Console eyebrow.
- Replaced the page-specific `renderTabButton` usage with the shared EMS `Tabs` component.
- Preserved existing data fetching, route behavior, permissions, and audit table data flow.

## Validation

Validation completed from `frontend/`:

- `npm run build` - PASS
- `npm run check:i18n` - PASS
- `npm run check:i18n:raw` - PASS with warning-only heuristic candidates from the existing raw-string scanner.

Source checks completed:

- `rg "audit\\.eyebrow" frontend/src/pages/AuditExplorer.tsx frontend/src/i18n -S` - no matches.
- `rg "renderTabButton" frontend/src/pages/AuditExplorer.tsx -S` - no matches.

## Screenshot

Screenshot capture was attempted with a standalone headless browser. The unauthenticated browser session was redirected to the role-selection screen, so no valid Audit Explorer screenshot was committed.

The in-app browser automation surface was also attempted, but it was not available in this session.

Manual or authenticated browser smoke should confirm:

- No raw `audit.eyebrow` text.
- No default browser tab buttons.
- Tabs use EMS design-system styling.
- Audit event table remains in a styled EMS card/table container.
- No payment/rate-rule UI or backend changes.

## Payment Safety Confirmation

Payment/rate-rule code changed: No.

Final payment calculation, approval, and export remain unimplemented in this hotfix.
