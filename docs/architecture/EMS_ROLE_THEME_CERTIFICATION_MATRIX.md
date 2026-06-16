# EMS Role Theme Certification Matrix

Date: 2026-06-16

## Result

Role theme result: `CERTIFIED`

Runtime theme source:

- `AppShell` applies `data-role={role ?? "guest"}` and `data-density="comfortable"`.
- `frontend/src/styles/tokens.css` maps role accents and universal status colors.
- Universal status colors were stable across role sweeps and did not inherit role accents.

## Role Evidence

| Role / State | Captures | Runtime Role State | Role Accent Observed | Universal Status Sample | Result |
| --- | ---: | --- | --- | --- | --- |
| `admin` | 63 | `data-role="admin"` | `#1f4d8f` | success `#047857`, danger `#b91c1c` | CERTIFIED |
| `esq_head` | 24 | `data-role="esq_head"` | `#8b3a3a` | success `#047857`, danger `#b91c1c` | CERTIFIED |
| `secretary` | 11 | `data-role="secretary"` | `#1f7a74` | success `#047857`, danger `#b91c1c` | CERTIFIED |
| `dept_supervisor` | 4 | `data-role="dept_supervisor"` | `#7a4bb7` | success `#047857`, danger `#b91c1c` | CERTIFIED |
| `staff` | 27 | `data-role="staff"` | `#c97a1c` | success `#047857`, danger `#b91c1c` | CERTIFIED |
| `teacher` | 22 | `data-role="teacher"` | `#2f855a` | success `#047857`, danger `#b91c1c` | CERTIFIED |
| `print_shop` | 7 | `data-role="print_shop"` | `#5a6b83` | success `#047857`, danger `#b91c1c` | CERTIFIED_WITH_DOCUMENTED_P2 |
| guest/public | 18 | no authenticated shell or guest default | `#0d6efd` default | success `#047857`, danger `#b91c1c` | CERTIFIED |

## Secretary Evidence Note

Direct secretary evidence was captured with an active local secretary session and without recording credentials. The direct secretary screenshots cover dashboard, schedule, analytics, duty workload, governance, submissions, attendance, sections, workflow, print review, and payment document settings at `1366x768`.

## Theme Boundary

No route permissions were changed. Admin `view_as` was not used as a substitute for secretary permission evidence. It was not necessary for final certification after direct secretary screenshots were captured.

## Residual Theme Debt

`frontend/src/theme/roleThemes.ts` still contains visual color metadata. Runtime evidence did not show a mismatch because the active shell theme is driven by `data-role` CSS variables. This remains documentation-level debt only and is not a certification blocker.
