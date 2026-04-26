# PROJECT OVERVIEW

## What EMS Is

EMS (Exam Management System) is the operational workspace for planning, reviewing, approving, and exporting university exam operations.

The system is designed to support:
- exam scheduling and room allocation
- invigilator/staff assignment
- approval and sign-off workflow
- exam document generation and export
- operational check-ins and QR-based pickup confirmation
- admin-facing data import, audit, and user management

## Target Users

- `admin`: manages periods, users, imports, optimization, workflow, exports
- `teacher`: submits exam information and reviews personal exam work
- `staff`: handles room operations, check-ins, and selected export/external-exam flows
- `dept_supervisor`: oversees departmental readiness and staffing issues
- `esq_head`: signs off workflow and reviews governance-facing readiness
- `secretary`: joins final approval/signature flow
- `print_shop`: uses print queue and print delivery workflow
- `student`: public schedule lookup only

## High-Level Architecture

### Frontend

- Stack: React + TypeScript + Vite
- Main entry: `frontend/src/App.tsx`
- Shell/navigation: `frontend/src/components/layout/*`
- i18n: `frontend/src/i18n/index.tsx`, `frontend/src/i18n/en.ts`, `frontend/src/i18n/th.ts`
- Role theme system: `frontend/src/theme/roleThemes.ts`

### Backend

- Stack: FastAPI + SQLAlchemy
- Main entry: `backend/main.py`
- API routers: `backend/routers/*`
- Auth/session handling: `backend/auth_utils.py`, `backend/routers/auth.py`
- Local data store in this repo is currently SQLite-based (`backend/ems.db`) for development

### Data Flow

1. Admin imports academic/master data.
2. Operational modules enrich imported data with scheduling, ownership, staffing, and workflow state.
3. Workflow and optimizer modules produce reviewable assignments and approval checkpoints.
4. Export/document modules generate PDFs, Excel outputs, and QR-linked operational artifacts.

## Key Modules

- `Dashboard`: role-aware operational summary
- `Schedule`: master exam schedule and coverage
- `Workflow`: approval/readiness/signature flow
- `Optimizer`: room + invigilator assignment and staffing constraints
- `Staff Availability`: operational blocking calendar for staff
- `Check-ins`: room updates and QR pickup confirmation
- `Export Center`: centralized export entry point
- `Import / Import Audit`: controlled data intake and review
- `Users`: admin account/role management
- `Exam Manager`: course ownership by exam cycle
- `Copy / Print Queue / Print Review`: print preparation and output operations

## Key Repo Paths

- `frontend/src/pages`: route-level pages
- `frontend/src/components`: shared UI and domain components
- `frontend/src/services`: API client modules
- `backend/routers`: API surface grouped by domain
- `backend/models.py`: SQLAlchemy models
- `backend/schemas.py`: API schema contracts
- `docs/`: project reference material for humans and AI tools

## Notes For Maintainers

- Prefer reading `frontend/src/config/navigation.ts` and `frontend/src/App.tsx` together to understand page coverage.
- Prefer reading `backend/main.py` to see which routers are active in the app.
- Role behavior is split between route guards, navigation visibility, and backend authorization checks.
- Operational data is layered on top of imported academic data. See `DATA_MODEL.md`.
