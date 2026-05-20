# Workload Duty Analytics Browser Smoke

> Audience: QA, admin reviewers, and pilot release owners  
> Purpose: Lightweight real-browser verification plan for Workload Duty Analytics

---

## Evidence to Capture

For each scenario below, capture:
- current route
- active role
- language mode
- screenshot of the visible dashboard area
- pass/fail note

Recommended screenshot names:
- `wda-admin-route.png`
- `wda-staff-route.png`
- `wda-teacher-route.png`
- `wda-empty-results.png`
- `wda-thai-mode.png`
- `wda-english-mode.png`

---

## Admin Route Smoke

1. Sign in as an `admin`.
2. Open `/workload-duty-analytics`.
3. Verify the page loads without route errors.
4. Verify summary cards, filters, fairness panel, chart cards, and table section render.
5. Verify sidebar navigation contains the workload analytics entry.

Expected:
- admin route is reachable
- role-appropriate title is shown
- no unauthorized guard is triggered

---

## Staff Route Smoke

1. Sign in as `staff`, `dept_supervisor`, `esq_head`, or `secretary`.
2. Open `/duty-workload`.
3. Verify the page loads and the shared staff-facing title appears.
4. Verify sidebar navigation reaches the same route.

Expected:
- staff-facing route is reachable for authorized operational roles
- page layout matches the shared workload analytics view
- route guards remain intact

---

## Teacher Route Smoke

1. Sign in as a `teacher`.
2. Open `/my-workload`.
3. Verify the teacher title appears.
4. Verify the dashboard renders without exposing broader-role navigation.

Expected:
- teacher route is reachable
- teacher view renders normally
- teacher scope remains constrained to own workload defaults

---

## Empty Payload Smoke

1. Use filters that are expected to return no workload records.
2. Verify summary cards still render.
3. Verify the explicit no-results state appears.
4. Verify person chart, daily chart, time-slot chart, and table show their empty messaging.
5. Verify fairness lists show the explicit no-overloaded / no-underloaded messages.

Expected:
- no blank analytics body
- no page crash
- no regression to raw fallback text

---

## Chart Section Smoke

1. Load a route with known workload data.
2. Verify by-person chart renders.
3. Verify daily cumulative chart renders.
4. Verify time-slot chart renders.
5. Confirm values and labels fit the card layout.

Expected:
- charts render in their intended cards
- no obvious overflow or broken axes/labels

---

## Filter Section Smoke

1. Open the dashboard with default filters.
2. Change semester, academic year, period, exam type, role group, person search, and duty type one at a time.
3. Use reset after changing several filters.

Expected:
- inputs accept changes without layout breakage
- duty type labels are localized
- reset returns the page to the role-appropriate default state

---

## Thai / English Toggle Smoke

1. Open the dashboard in English mode.
2. Capture labels, placeholders, fairness bands, and empty states.
3. Switch to Thai mode.
4. Capture the same areas again.

Expected:
- no raw English UI strings remain in Thai mode for the workload page
- fairness bands are localized
- placeholders and table headers are localized

---

## Sidebar Navigation Smoke

1. For each authorized role, reach the page through sidebar navigation instead of direct URL entry.
2. Confirm the active nav state matches the route.
3. Confirm the page title and top-level content stay synchronized with the route.

Expected:
- sidebar links work for authorized roles
- active state tracks the current route
- workload analytics is not expected in mobile bottom navigation

---

## Completion Notes

- This smoke plan is intentionally manual because no frontend test framework is installed in the repo.
- Use this checklist together with:
  - `docs/architecture/WORKLOAD_DUTY_ANALYTICS.md`
  - `docs/architecture/WORKLOAD_DUTY_ANALYTICS_QA_CHECKLIST.md`
