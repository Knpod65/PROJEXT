# Workload Duty Analytics QA Checklist

> Audience: QA, pilot admins, staff reviewers, and release owners  
> Purpose: Manual verification checklist for the Workload Duty Analytics dashboard

---

## Empty Data

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| No duty records for the selected scope | Summary cards remain visible with zero values |  |  |
| No workload results match current filters | `noFilteredResults` empty state is shown with filter-adjust guidance |  |  |
| No person-level records | By-person chart shows explicit empty state and table shows a dedicated empty row |  |  |
| No daily series | Daily cumulative card shows explicit empty messaging |  |  |
| No time-slot series | Time-slot card shows explicit empty messaging |  |  |
| No overloaded people | Fairness panel shows explicit no-overloaded message |  |  |
| No underloaded people | Fairness panel shows explicit no-underloaded message |  |  |

## Minimal Data

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| One person only | Table shows one row and by-person chart renders one entry cleanly |  |  |
| One exam date only | Daily cumulative chart renders a single date without layout breakage |  |  |
| One time slot only | Time-slot chart renders a single bar without clipping |  |  |
| Invigilation-only data | Invigilation totals and combined totals stay correct |  |  |
| Distribution-only data | Paper distribution totals and combined totals stay correct |  |  |

## Mixed Data

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| Staff + teacher records present | Role-group labels and totals remain readable and correct |  |  |
| Staff + supervisor + admin mix | By-person ranking and fairness values remain stable |  |  |
| Mixed invigilation and distribution duties | Combined totals equal invigilation plus distribution totals |  |  |
| Overloaded and underloaded lists populated | Correct people appear in each fairness list |  |  |

## Large Data

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| 100+ people in one result set | Page remains usable and table remains scrollable |  |  |
| Long Thai display names | No broken layout, clipped cells, or unreadable chart labels beyond acceptable truncation |  |  |
| Many dates | Daily cumulative section remains readable and does not overflow unexpectedly |  |  |
| Many time slots | Time-slot section remains readable and does not collapse visually |  |  |

## Filter Behavior

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| Default blank filters | Broad workload view loads successfully |  |  |
| Semester and academic-year filter | Data changes consistently with the selected scope |  |  |
| Period filter | Result set narrows to the selected exam period |  |  |
| Role-group filter | Visible dataset changes while route permissions remain intact |  |  |
| Person search filter | Matching person rows are narrowed correctly |  |  |
| Duty-type filter | Invigilation, paper distribution, and combined views behave as expected |  |  |
| Reset action | Filters reset to role-appropriate defaults and the dataset refreshes |  |  |

## Permission Behavior

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| Admin route `/workload-duty-analytics` | Admin can access full dashboard route |  |  |
| Staff/supervisor/esq/secretary route `/duty-workload` | Authorized operational roles can access the shared staff-facing route |  |  |
| Teacher route `/my-workload` | Teacher sees teacher-facing page and own workload default |  |  |
| Student access attempt | Student cannot access workload duty analytics routes |  |  |
| Unauthorized role route attempt | Existing route guards still block unauthorized access |  |  |

## Bilingual UI

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| English mode | Labels, placeholders, fairness bands, and empty states read naturally |  |  |
| Thai mode | Labels, placeholders, fairness bands, and empty states read naturally |  |  |
| Thai cards and chart headings | No clipped labels or obvious layout distortion |  |  |
| Thai mode raw-string check | No raw English UI strings remain in `WorkloadDutyAnalytics` display text |  |  |

## Visual QA

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| Desktop width | Layout sections align correctly and charts remain readable |  |  |
| Tablet width | Cards wrap cleanly and table remains usable |  |  |
| Mobile width if route is opened | Content remains navigable without major overlap |  |  |
| Chart overflow | Chart sections do not overflow their cards unexpectedly |  |  |
| Table scroll | Table remains horizontally scrollable when needed |  |  |
| Long names in fairness lists | Long names do not break the card layout |  |  |
| Empty fairness lists | Fairness section still looks intentional and readable |  |  |

## PDPA QA

| Scenario | Expected Result | Pass/Fail | Evidence / Notes |
|----------|-----------------|-----------|------------------|
| No student PII in dashboard | Student names, IDs, and unrelated student data are not exposed |  |  |
| No unnecessary raw internal IDs | Visible UI does not expose raw internal IDs unless operationally justified |  |  |
| Teacher access scope | Teacher cannot view unauthorized people’s workload details |  |  |
| Staff/supervisor scope | Authorized operational roles remain inside allowed visibility boundaries |  |  |
| Audit expectations documented | Tester can map the feature to `WORKLOAD_DUTY_ANALYTICS.md` and browser smoke evidence |  |  |
