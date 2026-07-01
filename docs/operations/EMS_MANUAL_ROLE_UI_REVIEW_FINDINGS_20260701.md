# EMS Manual Role UI Review Findings - 2026-07-01

**Status after review:** TESTED WITH FINDINGS  
**Fix pass status:** TESTED WITH FINDINGS FIXED in the follow-up fix pass  
**Method:** Direct demo-account browser review at `http://127.0.0.1:3000`; Admin View As was not used.  
**Evidence directory:** `docs/operations/role-ui-review-screenshots/20260701/`

---

## Role Status Summary

| Role | Account | Review status | Notes |
|------|---------|---------------|-------|
| Admin | `mathawee.m` / `admin123` | PASS | No role-specific issue recorded in the review pass. |
| ESQ Head | `napaporn.ph` / `esq123` | PASS | Navigation matched expected role routes; TH/EN and responsive checks passed. |
| Dept Supervisor | `phusanisa.sai` / `staff123` | ISSUES | `/dashboard` was visible but backend dashboard API returned 403. |
| Staff | `araya.fa` / `staff123` | ISSUES BEFORE DOC FIX | Provided account `ketsinee.s` did not work as staff in local DB; `araya.fa` is the confirmed staff account for review. |
| Teacher | `pailin.phu` / `teacher123` | PASS | Teacher navigation excluded admin/audit/health/platform/payment-settings/optimizer tools. |
| Print Shop | `printshop.ops` / `print123` | ISSUES | Main queue rendered, but supplemental copy-count request returned 403. |

---

## Finding #1

```text
Role: Dept Supervisor
URL: /dashboard
Viewport: Desktop and 1024px
Language: EN and TH toggle covered
Problem: Sidebar exposed /dashboard, but GET /api/dashboard/?semester=2&academic_year=2568 returned 403. The dashboard showed a load-error state instead of role-appropriate department data.
Expected: Dept Supervisor can load /dashboard and see department-scoped dashboard aggregates, without admin-only recent logs.
Severity: P1
Screenshot: dept-supervisor-desktop.png, dept-supervisor-1024.png
Fix status: Fixed in follow-up pass by allowing dept_supervisor in dashboard policy and scoping dashboard aggregates by academic group.
```

## Finding #2

```text
Role: Staff
URL: Login / role workspace entry
Viewport: Desktop
Language: EN
Problem: The review credential list named ketsinee.s / staff123, but the local database reported ketsinee.s as esq_head, so it could not validate the staff workspace.
Expected: Manual staff review uses a confirmed staff credential.
Severity: P0
Screenshot: Not captured in rerun screenshot set
Fix status: Fixed in docs by using araya.fa / staff123 as the confirmed staff demo account. Local DB was not mutated.
```

## Finding #3

```text
Role: Print Shop
URL: /print-queue
Viewport: Desktop and 1024px
Language: EN and TH toggle covered
Problem: The print queue rendered, but the page also called GET /api/schedule/copy-count?semester=2&academic_year=2568, which returned 403 for print_shop.
Expected: Print Shop can use print queue and handoff workflow without unauthorized supplemental schedule requests.
Severity: P2
Screenshot: print-shop-desktop.png, print-shop-1024.png
Fix status: Fixed in follow-up pass by skipping the copy-count supplemental call for print_shop and preserving print-job fallback metrics.
```

---

## Evidence Screenshots

| Screenshot | Role | Viewport |
|------------|------|----------|
| `dept-supervisor-desktop.png` | Dept Supervisor | Desktop |
| `dept-supervisor-1024.png` | Dept Supervisor | 1024px |
| `esq-head-desktop.png` | ESQ Head | Desktop |
| `esq-head-1024.png` | ESQ Head | 1024px |
| `print-shop-desktop.png` | Print Shop | Desktop |
| `print-shop-1024.png` | Print Shop | 1024px |
| `teacher-desktop.png` | Teacher | Desktop |
| `teacher-1024.png` | Teacher | 1024px |

---

## Guardrails

- Admin View As remains NOT VALID for permission or UI review.
- Payment pages remain draft/review/supporting only; no final approval or authorization was introduced.
- Screenshots are evidence artifacts only; no browser session state or credentials are committed.

---

## Follow-Up Fix Pass Validation

| Check | Result |
|-------|--------|
| Dept Supervisor API | `phusanisa.sai` / `staff123` resolved as `dept_supervisor`; `GET /api/dashboard/?semester=2&academic_year=2568` returned 200. |
| Dept Supervisor Chrome UI | `/dashboard` loaded with department dashboard content; no previous dashboard load-error state was visible. |
| Staff API | `araya.fa` / `staff123` resolved as `staff`. |
| Print Shop API | `printshop.ops` / `print123` resolved as `print_shop`; `GET /api/printing/queue` returned 200. |
| Print Shop Chrome UI | `/print-queue` loaded with `Print queue and dispatch control`; Chrome error logs had no `copy-count` entries. |
| Teacher Chrome UI | `/dashboard` loaded without admin-only audit, health, platform configuration, payment settings, or optimizer trace links/text. |
| Direct copy-count permission | `GET /api/schedule/copy-count?semester=2&academic_year=2568` still returned 403 for `print_shop`, as intended. |
