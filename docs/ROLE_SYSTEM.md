# ROLE SYSTEM

## Roles

### admin

- Full operational/admin control
- Can import data, manage users, run optimizer, start workflow, open swap window, and use settings
- Color theme:
  - primary: `#1f4d8f`
  - soft background: `rgba(31, 77, 143, 0.14)`
  - accent/border: `#173867`

### teacher

- Works on submissions and personal exam responsibilities
- Sees teaching/exam-related pages only
- Color theme:
  - primary: `#2f855a`
  - soft background: `rgba(47, 133, 90, 0.14)`
  - accent/border: `#256947`

### staff

- Handles room operations, check-ins, staffing logistics, and selected export/external exam flows
- Color theme:
  - primary: `#c97a1c`
  - soft background: `rgba(201, 122, 28, 0.16)`
  - accent/border: `#9e5f16`

### dept_supervisor

- Departmental review/oversight
- Sees schedule, submissions, dashboard, swap-related visibility for their scope
- Color theme:
  - primary: `#7a4bb7`
  - soft background: `rgba(122, 75, 183, 0.14)`
  - accent/border: `#603993`

### esq_head

- Governance/approval role
- Participates in final workflow sign-off and readiness review
- Color theme:
  - primary: `#8b3a3a`
  - soft background: `rgba(139, 58, 58, 0.14)`
  - accent/border: `#6d2d2d`

### secretary

- Shared governance role with sign-off responsibilities
- Participates in workflow review and final visibility
- Color theme:
  - primary: `#1f7a74`
  - soft background: `rgba(31, 122, 116, 0.14)`
  - accent/border: `#185f5b`

### print_shop

- Print production workspace
- Uses print queue and downstream delivery-oriented features
- Color theme:
  - primary: `#5a6b83`
  - soft background: `rgba(90, 107, 131, 0.14)`
  - accent/border: `#455365`

### student

- Public schedule lookup only
- No internal admin/operational workspace access
- Color theme:
  - primary: `#475569`
  - soft background: `rgba(71, 85, 105, 0.14)`
  - accent/border: `#334155`

## Visibility Rules

- Route access is enforced in `frontend/src/App.tsx` via `GuardedPage`
- Navigation visibility is defined in `frontend/src/config/navigation.ts`
- Backend still performs authorization checks; frontend visibility is not the only gate
- Some pages are intentionally hidden from navigation but still routed

## View-As / Effective Role

- Admin can preview other role shells through the view-as flow
- UI should always use `effective_role` when available
- Theme, layout tone, and navigation should match the effective role, not only the base account role

## Role Theme Usage Rules

- Do not hardcode role colors in feature pages
- Always use `getRoleTheme(role)` from `frontend/src/theme/roleThemes.ts`
- Apply the same role palette to:
  - badges
  - sidebar/shell accents
  - role distribution visuals
  - any role-colored cards/chips

## Permission Summary

- `admin`: all management flows
- `teacher`: teaching/exam contribution flows
- `staff`: operations + check-in flows
- `dept_supervisor`: department-level oversight
- `esq_head` / `secretary`: governance + sign-off
- `print_shop`: print operations
- `student`: public search only
