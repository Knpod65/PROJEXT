# EMS Localhost Current Session Report

**Date**: 2026-06-15
**Commit at startup**: `14633cab6c23532c2b2909ed612842ed4f7432ab`
**Branch**: `main`
**Environment**: local development only

## Startup Result

- Preflight worktree was clean and `git pull --ff-only origin main` reported already up to date.
- Backend started at `http://127.0.0.1:8000`.
- Frontend started at `http://127.0.0.1:3000`.
- Backend health check `GET /api/health`: `200`, service `EMS`, status `ok`.
- Frontend root and SPA routes returned `200`.
- Backend startup used the development-only SQLite fallback and development create/seed path.
- Runtime logs are ignored local files:
  - `backend-local-session.out.log`
  - `backend-local-session.err.log`
  - `frontend-local-session.out.log`
  - `frontend-local-session.err.log`

Actual process IDs are intentionally not persisted in Git. Obtain and verify the current listener
owners immediately before stopping:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,3000 |
  Select-Object LocalAddress,LocalPort,OwningProcess

Get-CimInstance Win32_Process -Filter "ProcessId=<verified-listener-pid>" |
  Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine
```

## Verified Routes

| Route | Result |
|---|---|
| `http://127.0.0.1:8000/api/health` | `200` |
| `http://127.0.0.1:3000/` | `200`, EMS title |
| `/dashboard` | SPA route returned `200` |
| `/invigilation-payment-document-draft` | SPA route returned `200`; authenticated reviewer smoke passed |
| `/payment-document-settings` | SPA route returned `200` |
| `/invigilation-advance-batch-preview` | SPA route returned `200` |

## Authenticated Reviewer Smoke

- Signed in through the local role-selection and login flow using an authorized local demo admin
  account. No credential is recorded here.
- Opened `/invigilation-payment-document-draft`.
- Confirmed the reviewer page displays `DRAFT_NOT_AUTHORIZED` and the Thai supporting-finance-roster
  export action `ส่งออกรายชื่อประกอบการเบิก`.
- Confirmed the page states that draft acceptance is not payment approval and that official/final
  export remains disabled.
- The reviewer page was left open for local handoff.

## Exact Startup Commands

Run from the repository root:

```powershell
$root = (Get-Location).Path

Start-Process -FilePath "$root\backend\.venv\Scripts\python.exe" `
  -ArgumentList "-m","uvicorn","main:app","--host","127.0.0.1","--port","8000" `
  -WorkingDirectory "$root\backend" -WindowStyle Hidden `
  -RedirectStandardOutput "$root\backend-local-session.out.log" `
  -RedirectStandardError "$root\backend-local-session.err.log"

Start-Process -FilePath "npm.cmd" -ArgumentList "run","dev" `
  -WorkingDirectory "$root\frontend" -WindowStyle Hidden `
  -RedirectStandardOutput "$root\frontend-local-session.out.log" `
  -RedirectStandardError "$root\frontend-local-session.err.log"
```

## Safe Shutdown

Do not stop a PID copied from an old report. Resolve the current listener owner, inspect its command
line, and stop only the verified Uvicorn/Vite listener:

```powershell
$backendPid = (Get-NetTCPConnection -State Listen -LocalPort 8000).OwningProcess
$frontendPid = (Get-NetTCPConnection -State Listen -LocalPort 3000).OwningProcess

Get-CimInstance Win32_Process -Filter "ProcessId=$backendPid" |
  Select-Object ProcessId,Name,CommandLine
Get-CimInstance Win32_Process -Filter "ProcessId=$frontendPid" |
  Select-Object ProcessId,Name,CommandLine

# Run only after the displayed command lines are the expected local Uvicorn and Vite commands.
Stop-Process -Id $backendPid -ErrorAction Stop
Stop-Process -Id $frontendPid -ErrorAction Stop
```

This report certifies a local-development session only. It does not certify pilot or production
readiness.
