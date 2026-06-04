# Invigilation Rate Rule Browser Smoke Blocked Report

**Date**: 2026-06-04  
**Scope**: EMS invigilation payment rate-rule browser smoke only.

## Decision

`BROWSER_SMOKE_STATUS = BLOCKED`

The authenticated browser smoke for `/invigilation-rate-rules` was not executed. API-only validation is not accepted as a replacement for browser smoke.

## EMS Root And Git State

- Confirmed root: `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`
- Branch: `main`
- Starting HEAD: `0e3b468 docs(payment): record live smoke evidence for invigilation rate rules`
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
- Chrome diagnostic results:
  - Google Chrome installed: **YES**
  - Google Chrome running: **YES**
  - Selected Chrome profile: `Default`
  - Codex Chrome Extension installed in selected profile: **NO**
  - Codex Chrome Extension enabled in selected profile: **NO**
  - Native messaging host manifest exists and is correct: **YES**

The blocker is the missing Codex Chrome Extension in the selected Chrome profile. The native host does not need repair.

### Other Local Browser Automation

- No repo-local Playwright automation dependency was available.
- No alternate browser automation was used after Chrome extension recovery failed.
- No API-only smoke was used as a browser-smoke substitute.

## Server Check

The current EMS backend and frontend were previously confirmed capable of starting from `main`, with auth and invigilation rate-rule routes present. They were not used to claim browser-smoke success in this blocked pass.

## Required Recovery

1. Install and enable the Codex Chrome Extension in Chrome profile `Default`, or enable the Codex in-app Browser for the session.
2. Confirm the browser client appears to Codex.
3. Rerun the authenticated manual/browser smoke checklist.

Codex must not install or repair the Chrome extension or native host automatically.

## Safety Confirmation

- Browser smoke passed: **NO**
- Screenshots captured: **NO**
- Code changed: **NO**
- Payment calculation implemented: **NO**
- Advance Batch amount integration changed: **NO**
- Final payment approval/export added: **NO**
- Teaching workload logic touched: **NO**
- Production deployment attempted: **NO**

