# EMS Post-Descope Localhost Smoke Report

**Date:** 2026-06-30  
**Purpose:** Localhost smoke after EMS navigation de-scope Phase B.  
**Root:** `C:\Users\DELL\Desktop\PROJEXT\opt\ems_system`  
**Branch at smoke start:** `main`  
**Commit at smoke start:** `b958230 docs(scope): record EMS navigation de-scope phase B validation`

## Preflight

| Check | Result |
| ----- | ------ |
| `git rev-parse --show-toplevel` | `C:/Users/DELL/Desktop/PROJEXT/opt/ems_system` |
| Branch | `main` |
| `git pull --ff-only origin main` | Already up to date |
| Starting worktree | Clean |
| Local branch alignment | `main` matched `origin/main` at `b958230` |

## Localhost Services

| Service | URL | PID | Status | Command |
| ------- | --- | --- | ------ | ------- |
| Backend | `http://127.0.0.1:8000` | `13552` | Running | `backend\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000` |
| Frontend | `http://127.0.0.1:3000` | `27052` | Running | `npm run dev` / Vite `--host 0.0.0.0 --port 3000` |

No listeners were present on ports `8000`, `3000`, or `5173` before startup. No unknown processes were stopped.

## Health Results

| Check | Result |
| ----- | ------ |
| `GET http://127.0.0.1:8000/api/health` | `200`, `{"status":"ok","service":"EMS"}` |
| `GET http://127.0.0.1:3000/` | `200`, title `EMS | Exam Management System` |
| Backend log note | Development SQLite fallback and development startup mutation warnings were present; local development only. |
| Frontend log note | Vite ready on `http://localhost:3000/`. |

## Browser And Visual Smoke

The frontend was opened in the local browser at `http://127.0.0.1:3000/` for handoff.

In-app browser automation was not available in this Codex session after tool discovery, and the repo does not include Playwright or Puppeteer. Therefore this pass does not claim full visual browser validation or screenshots. Validation below is based on:

- live localhost health checks,
- authenticated API login checks,
- source-of-truth navigation config inspection,
- route declaration inspection,
- Vite HTTP route smoke.

## Authenticated Session Smoke

| Role | Username checked | Result |
| ---- | ---------------- | ------ |
| `admin` | documented demo admin | PASS |
| `esq_head` | documented demo ESQ account | PASS |
| `dept_supervisor` | documented seeded supervisor | PASS |
| `staff` | documented seeded staff | PASS |
| `teacher` | documented demo teacher | PASS |
| `print_shop` | documented demo print shop | PASS |
| `secretary` | local DB user found, no working documented demo password | NOT LIVE-SMOKED |

No credentials are recorded in this report.

## Navigation Source Validation

Canonical navigation source: `frontend/src/config/navigation.ts`.

Hidden from main navigation:

| Page | Result |
| ---- | ------ |
| Admin Intelligence Dashboard | PASS, `hidden: true` |
| Executive Analytics | PASS, `hidden: true` |
| Governance Cockpit | PASS, `hidden: true` |
| Operational Health | PASS, `hidden: true` |
| Audit Explorer | PASS, `hidden: true` |
| Optimizer Trace | PASS, `hidden: true` |
| Platform Configuration | PASS, `hidden: true` |
| Import Audit | PASS, `hidden: true` |

Visible core routes confirmed in navigation config for appropriate roles:

| Route | Result |
| ----- | ------ |
| `/dashboard` | Visible |
| `/schedule` | Visible |
| `/import` | Visible for admin |
| `/rooms-v2` | Visible for admin |
| `/period` | Visible for admin |
| `/staff-availability` | Visible for admin |
| `/optimizer` | Visible for admin |
| `/submissions` | Visible by existing role filters |
| `/print-queue` | Visible for print shop |
| `/checkins` | Visible by existing role filters |
| `/attendance` | Visible by existing role filters |
| `/swaps` | Visible by existing role filters |
| `/exports-center` | Visible by existing role filters |
| `/invigilation-payment-document-draft` | Visible for admin/staff |
| `/historical-schedules` | Visible for existing `admin` role |

`/rooms` is not a declared route; `/rooms-v2` is the correct current rooms route.

## Hidden Direct URL Validation

Route declarations remain present in `frontend/src/App.tsx`, and Vite returned the EMS app shell for each direct URL:

| Route | Declared | Frontend HTTP |
| ----- | -------- | ------------- |
| `/admin-intelligence-dashboard` | Yes | `200` |
| `/analytics` | Yes | `200` |
| `/governance` | Yes | `200` |
| `/operational-health` | Yes | `200` |
| `/audit-explorer` | Yes | `200` |
| `/optimizer-trace` | Yes | `200` |
| `/platform-config` | Yes | `200` |
| `/import-audit` | Yes | `200` |

Route guards were not changed in this pass. Direct-route authorization remains governed by the existing `GuardedPage` role lists in `frontend/src/App.tsx`.

## Core Route Quick Smoke

Vite returned the EMS app shell with title `EMS | Exam Management System` for:

`/dashboard`, `/schedule`, `/import`, `/rooms-v2`, `/period`, `/staff-availability`, `/optimizer`, `/submissions`, `/print-queue`, `/checkins`, `/attendance`, `/swaps`, `/exports-center`, `/invigilation-payment-document-draft`.

## Safety Checks

| Safety item | Result |
| ----------- | ------ |
| Code changed | NO |
| Navigation changed | NO |
| Routes deleted | NO |
| Page files deleted | NO |
| Route guards changed | NO |
| Role permissions changed | NO |
| Backend changed | NO |
| Scheduling/optimization logic changed | NO |
| Workload calculations changed | NO |
| Payment/export/review/settings logic changed | NO |
| Final approval/authorization added | NO |

## Validation Commands

| Command | Result |
| ------- | ------ |
| `npm run build` | PASS; Vite emitted the existing large chunk warning. |
| `npm run check:i18n` | PASS; `en` and `th` key sets both `2509`. |
| `npm run check:i18n:raw` | PASS; existing warning-mode raw string candidates reported in `AdminIntelligenceDashboard.tsx`. |
| `git diff --check` | PASS |
| `git status --short` | Only the two expected untracked ops docs before commit. |

## Services Left Running

Services were intentionally left running for handoff.

| Service | PID | Stop command |
| ------- | --- | ------------ |
| Backend | `13552` | `Stop-Process -Id 13552` |
| Frontend | `27052` | `Stop-Process -Id 27052` |

Before stopping later, re-check listener ownership:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,3000 |
  Select-Object LocalAddress,LocalPort,OwningProcess

Get-CimInstance Win32_Process -Filter "ProcessId=<pid>" |
  Select-Object ProcessId,Name,CommandLine
```

Stop only verified EMS-owned Uvicorn/Vite processes.
