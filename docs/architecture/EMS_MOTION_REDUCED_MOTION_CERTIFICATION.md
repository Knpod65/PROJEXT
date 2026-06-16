# EMS Motion Reduced-Motion Certification

Date: 2026-06-16

## Result

Motion result: `CERTIFIED`

## Source Contract

Motion tokens and reduced-motion behavior are centralized in `frontend/src/styles/tokens.css`.

Relevant source checks:

- `--motion-fast`
- `--motion-state`
- `--motion-page`
- `--motion-ease`
- `@media (prefers-reduced-motion: reduce)`

## Browser Evidence

| Route | Role | Evidence | Result |
| --- | --- | --- | --- |
| `/dashboard` | admin | `admin-dashboard-1366-th-reduced-motion.png` | CERTIFIED |
| `/workflow` | esq_head | `esq_head-workflow-1366-th-reduced-motion.png` | CERTIFIED |
| `/invigilation-payment-document-draft` | admin | `admin-invigilation-payment-document-draft-1366-th-reduced-motion.png` | CERTIFIED |

## Acceptance

Reduced-motion captures preserved layout, heading hierarchy, readable content, and role accents. No evidence showed motion-dependent content reveal, hidden sticky content, or horizontal overflow in reduced-motion mode.

## Boundary

No motion library, animation framework, route behavior, or data calculation was changed.
