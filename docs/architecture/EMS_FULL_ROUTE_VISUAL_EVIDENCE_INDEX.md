# EMS Full Route Visual Evidence Index

Date: 2026-06-16

## Evidence Location

Screenshot directory:

`docs/operations/demo-smoke-screenshots/full-route-visual-certification/`

Naming pattern:

`<role>-<route>-<viewport>-<language>.png`

Special state examples:

- `teacher-unauthorized-payment-draft-1600-th.png`
- `print_shop-unauthorized-settings-1600-th.png`
- `guest-not-found-1600-th.png`
- `admin-dashboard-1366-th-reduced-motion.png`

## Evidence Counts

| Evidence Type | Count |
| --- | ---: |
| Total PNG screenshots | 176 |
| Accepted captures | 172 |
| Documented P2 captures | 4 |
| Direct secretary captures | 11 |
| Mobile-critical captures | 30+ |
| Reduced-motion captures | 3 |

## Required Viewports

| Viewport | Use |
| --- | --- |
| `1600x900` | Desktop acceptance |
| `1366x768` | Standard laptop acceptance |
| `1024x768` | Compact laptop/sidebar acceptance |
| `390x844` | Mobile-critical routes and public/system states |

## Representative Screenshots

| Area | Evidence |
| --- | --- |
| Canonical admin dashboard | `admin-admin-intelligence-dashboard-1600-th.png` |
| Admin dashboard mobile-critical | `admin-dashboard-390-th.png` |
| Schedule fixed mobile overflow | `admin-schedule-390-th.png` |
| Optimization trace | `admin-optimizer-trace-1600-th.png` |
| Workload analytics admin | `admin-workload-duty-analytics-1600-th.png` |
| Staff duty workload English | `staff-duty-workload-1366-en.png` |
| Teacher my exam mobile | `teacher-myexam-390-th.png` |
| Direct secretary governance | `secretary-governance-1366-th.png` |
| Direct secretary payment settings | `secretary-payment-document-settings-1366-th.png` |
| Print shop queue P2 | `print_shop-print-queue-1366-th.png` |
| Payment draft Thai | `admin-invigilation-payment-document-draft-1600-th.png` |
| Payment draft English supporting label | `admin-invigilation-payment-document-draft-1366-en.png` |
| Unauthorized payment guard | `teacher-unauthorized-payment-draft-390-th.png` |
| Unauthorized settings guard | `print_shop-unauthorized-settings-1600-th.png` |
| Public student search mobile | `public-student-search-390-th.png` |
| Guest not found mobile | `guest-not-found-390-th.png` |

## Metric Evidence Captured

For each automated capture, the sweep recorded:

- Final path after redirects
- Language
- Visible `h1` count and text
- Document scroll/client width and horizontal overflow
- Runtime role and density when authenticated
- Role accent and universal status colors
- Raw-key and technical-label hits
- Payment safety string presence for payment/document pages
- Browser log observations where relevant

The transient metrics JSON was kept outside the repository under the local temp directory. Repository evidence is the screenshots plus this certification documentation.
