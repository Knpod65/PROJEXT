# EMS Another-Computer Transfer Checklist

Use this checklist when preparing EMS on another development/demo computer. Prefer a clean Git
clone and environment recreation. Transfer runtime data only when it is genuinely required.

## Clean Clone And Environment

- [ ] Confirm the source repository worktree is clean.
- [ ] Push all intended tracked changes before moving to the other computer.
- [ ] Clone `https://github.com/Knpod65/PROJEXT.git` and check out the intended commit on `main`.
- [ ] Create a new `backend\.venv`; do not copy the old virtual environment.
- [ ] Install backend dependencies from `backend\requirements.txt`.
- [ ] Run `npm ci` in `frontend`; do not copy `node_modules`.
- [ ] Create local environment configuration from tracked templates.
- [ ] Supply secrets through an approved secure channel, never through Git or this checklist.
- [ ] Verify ports `8000` and `3000` before startup.

## Optional Existing SQLite Data Transfer

Skip this section for a fresh development/demo database; development startup can create and seed a
new `backend\ems.db`.

- [ ] Confirm the source and destination use a compatible application commit/schema.
- [ ] Stop the backend and frontend on the source computer.
- [ ] Verify no process is holding `backend\ems.db`.
- [ ] Make a backup before transfer.
- [ ] Copy the closed/checkpointed `backend\ems.db` through an approved secure transfer method.
- [ ] Do not copy an actively open database.
- [ ] Do not transfer only `ems.db-wal` or `ems.db-shm` as a substitute for the database.
- [ ] Keep `backend\ems.db`, WAL, SHM, journals, and backups out of Git.
- [ ] Run only the migration procedure required by the checked-out commit, after backing up.

## Optional Upload Transfer

- [ ] Stop services before copying runtime uploads when consistency matters.
- [ ] Transfer `backend\uploads` separately through an approved secure method if the demo needs it.
- [ ] Confirm uploaded files contain no data that is prohibited on the destination computer.
- [ ] Keep uploads out of Git.

## Do Not Transfer Through Git

- Passwords, API keys, session tokens, or production credentials
- `.env`, `.env.local`, or any machine-specific secret file
- `backend\ems.db*`, database backups, WAL/SHM/journal files
- `.venv`, `node_modules`, frontend build output, caches, or runtime logs
- Runtime process IDs or stale listener assumptions

## Destination Validation

- [ ] `git status --short --branch` is clean on the intended commit.
- [ ] Backend starts using the destination computer's recreated environment.
- [ ] `GET http://127.0.0.1:8000/api/health` returns `200`.
- [ ] `http://127.0.0.1:3000/` loads.
- [ ] An authorized local reviewer can open `/invigilation-payment-document-draft`.
- [ ] Draft/non-authorization warnings remain visible.
- [ ] The supporting-finance-roster action is visible to an authorized reviewer.
- [ ] No pilot or production-readiness claim is made from this local validation.
