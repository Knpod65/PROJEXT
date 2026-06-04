# Invigilation Rate Rule Browser Smoke Blocked Report

**Date**: 2026-06-04  
**Scope**: EMS invigilation payment rate-rule browser smoke only.

## Decision

`BROWSER_SMOKE_STATUS = BLOCKED`

The authenticated browser smoke for `/invigilation-rate-rules` was not executed. API-only validation is not accepted as a replacement for browser smoke.

## EMS Root And Git State

- Confirmed root: `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`
- Branch: `main`
- Starting HEAD: `0ea213b docs(payment): record blocked invigilation rate rule browser smoke`
- Worktree was clean before browser recovery checks.
- No extra-teaching workload files were touched.

## Browser Recovery Attempts

### Codex In-App Browser

- Browser runtime discovery returned no available browser clients.
- Connection to browser id `iab` failed because the in-app browser was unavailable.
- A retry did not make the in-app browser available.

### Codex Chrome Extension Browser

- Connection to browser id `extension` failed.
- The connection was retried after two seconds and remained unavailable.
- A fresh Chrome window was opened with profile `Default`; connection still failed.
- Chrome was fully restarted and profile `Default` reopened; the final connection retry still returned no available browser clients.
- Chrome diagnostic results:
  - Google Chrome installed: **YES**
  - Google Chrome running: **YES**
  - Selected Chrome profile: `Default`
  - Codex Chrome Extension version: `1.1.5_0`
  - Codex Chrome Extension installed in selected profile: **YES**
  - Codex Chrome Extension enabled in selected profile: **YES**
  - Native messaging host manifest exists and is correct: **YES**

The extension installation and native host are now healthy, but the Codex browser runtime still reports no available `extension` browser client. Browser smoke remains blocked until the extension establishes a live connection to Codex.

### Other Local Browser Automation

- No repo-local Playwright automation dependency was available.
- No alternate browser automation was used after Chrome extension recovery failed.
- No API-only smoke was used as a browser-smoke substitute.

## Server Check

The current EMS backend and frontend were previously confirmed capable of starting from `main`, with auth and invigilation rate-rule routes present. They were not used to claim browser-smoke success in this blocked pass.

## Required Recovery

1. Reinstall or reconnect the Chrome plugin from the Codex plugin UI because extension installation, enablement, profile selection, Chrome restart, and native host checks already pass.
2. Confirm browser runtime discovery returns the `extension` browser client.
3. Rerun the authenticated manual/browser smoke checklist only after the client is available.

Codex must not claim browser smoke success from API-only checks.

## Safety Confirmation

- Browser smoke passed: **NO**
- Screenshots captured: **NO**
- Code changed: **NO**
- Payment calculation implemented: **NO**
- Advance Batch amount integration changed: **NO**
- Final payment approval/export added: **NO**
- Teaching workload logic touched: **NO**
- Production deployment attempted: **NO**
