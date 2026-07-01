# DEMO_ACCOUNT_AND_DATA_READINESS.md

**Date**: 2026-05-22
**Status**: Review
**Purpose**: Audit demo account availability, seeded data, and data gaps before demo.

---

## 1. Seed Data Source

Seed defined in `backend/seed.py`. Key details:

- Seeds only when `User.query.count() == 0` (first-run only)
- All passwords are bcrypt hashed
- Local SQLite `backend/ems.db` used for demo
- No real personal data from CMU Personnel_120226.xlsx (the real file) — values are anonymized example data

---

## 2. Seed Structure

| Role | Count | Username pattern | Password |
|------|-------|-----------------|---------|
| Admin | 2 | firstname.lastname | `admin123` |
| ESQ Head | 1 | firstname.lastname | `esq123` |
| Dept Supervisor | 4 | firstname.lastname | `staff123` |
| Staff | 26+ | firstname.lastname | `staff123` |
| Teacher | 44+ | firstname.lastname | `teacher123` |
| Print Shop | 1 | printshop.ops | `print123` |

**Total**: 70+ users across 6 roles.

---

## 3. Demo Account Status

| Field | Status |
|-------|--------|
| Seed function works | ✅ Confirmed (first-run logic in `seed.py:24-26`) |
| Hashed passwords | ✅ bcrypt |
| Gated by `env == "development"` in main.py startup | ✅ Yes |
| Demo accounts exist in local SQLite | ✅ Yes (after first Sahara run) |
| demo db file | `backend/ems.db` (13.8 MB WAL mode) |
| Demo dev passwords documented in RUNBOOK.md | ✅ Yes |
| Demo mode flag or banner | ❌ Not yet implemented |
| Staff workspace assignment stable | ⚠️ May be partial — screenshot report noted `workspace_not_assigned` for some staff accounts |

---

## 4. Segregated Roles

| Role | Key capability | Demo flow |
|------|---------------|-----------|
| `admin` | Full access, settings | Admin dashboard, workload analytics, governance cockpit |
| `esq_head` | ESQ governance, quality | Governance cockpit, audit explorer |
| `secretary` | Staff-level + workflow | Workflow page, staff workload |
| `dept_supervisor` | Department-scoped data | Department workload, staff availability |
| `staff` | Operational execution | Duty workload, attendance, check-ins |
| `teacher` | Submission + schedule | My Exam Work, My Workload, Submissions |
| `print_shop` | Print queue only | Print queue page |

---

## 5. Data Availability for Demo Routes

| Page | Local Data Status | Demo Impact |
|------|-----------------|-------------|
| `/dashboard` | Populated or empty-state | Empty-state OK if documented |
| `/admin-intelligence-dashboard` | May show load-error due to positional-arg issue | **Needs fix before demo** |
| `/workload-duty-analytics` | Empty-state expected with seed data | Empty-state OK |
| `/duty-workload` | Empty-state expected | Empty-state OK |
| `/my-workload` | Empty-state expected | Empty-state OK |
| `/governance` | May show empty or untranslated keys | Untranslated keys need i18n check |
| `/operational-health` | Backend health available | Should populate |
| `/audit-explorer` | AuditLog table may be empty | Empty-state OK |
| `/schedule` | Seed data has sections + schedules | May have populated rows |
| `/submissions` | May be empty or seed-populated | OK |
| `/attendance` | Empty-state expected | OK |
| `/checkins` | Empty-state expected | OK |

---

## 6. Demo Data Gaps

| Gap | Impact | Resolvable |
|-----|--------|------------|
| AdminIntelligenceDashboard service positional-arg issue | Load-error state shown on `/admin-intelligence-dashboard` | Yes — fix before demo |
| ExecutiveAnalytics route error | `/analytics` may show error | Verify / fix before demo |
| Governance cockpit untranslated keys | Raw i18n keys visible to user | Yes — add missing keys |
| Workload analytics likely empty | Bar chart may show no bars | OK — empty-state UX should handle this |
| Staff workspace `workspace_not_assigned` | Some staff accounts may not access staff pages | Use confirmed staff account `araya.fa` / `staff123`; do not use Admin View As for permission or role UI review |
| No real exam submission records | Submission flow looks empty | OK — empty-state is still useful |

Manual role UI review note: the local database used during the 2026-07-01 review reported `ketsinee.s` as `esq_head`, so it is not a valid local staff credential for that review pass. Use `araya.fa` / `staff123` for staff role checks unless a fresh seed/database reset confirms otherwise.

---

## 7. Demo Password Policy

> **DEMO ONLY — DO NOT USE IN PRODUCTION**

All demo passwords are intentionally simple and well-known:
- `admin123` (admin)
- `esq123` (ESQ head)
- `staff123` (staff/dept supervisors)
- `teacher123` (teachers)
- `print123` (print shop)

**Before pilot or production**:
1. All passwords must be reset
2. Admin must assign new passwords via EMS user management
3. CMU OAuth auth replaces password login for CMU-affiliated users
4. SECRET_KEY must be regenerated with `secrets.token_hex(32)`

---

**End of DEMO_ACCOUNT_AND_DATA_READINESS.md**
