# UI Full Regression Route Recheck Matrix

**Date**: 2026-06-11  
**Declarations**: `50`  
**Visual destinations**: `43`  
**Routing-only declarations**: `7`

| Route | Component/state | Access | Prior evidence | Current risk | Safety/workload risk | Closure decision |
|---|---|---|---|---|---|---|
| `/` | Home redirect | public/routing | routing check | none | none | `PASS_NO_ACTION` |
| `/role-selection` | Role selection | public | limited | low | none | `ACCEPTABLE_WITH_NOTE` |
| `/login` | Login | public | limited | low | none | `ACCEPTABLE_WITH_NOTE` |
| `/student-search` | Student search | public/student | yes | low | none | `PASS_NO_ACTION` |
| `/dashboard` | Dashboard | multi-role | yes | low | none | `PASS_NO_ACTION` |
| `/admin-intelligence-dashboard` | Admin intelligence | admin | yes | low P2 | none | `ACCEPTABLE_WITH_NOTE` |
| `/schedule` | Schedule | multi-role | yes | custom P2 | none | `ACCEPTABLE_WITH_NOTE` |
| `/analytics` | Executive analytics | reviewer roles | yes | data-sensitive P2 | none | `DEFER_PRODUCT_DECISION` |
| `/workload-duty-analytics` | Workload analytics | admin | yes | custom P2 | workload | `DEFER_WORKLOAD_SCOPE` |
| `/duty-workload` | Workload analytics | staff/reviewers | auth limited | custom P2 | workload | `DEFER_WORKLOAD_SCOPE` |
| `/my-workload` | Workload analytics | teacher | auth limited | custom P2 | workload | `DEFER_WORKLOAD_SCOPE` |
| `/governance` | Governance cockpit | reviewer roles | yes | low | none | `PASS_NO_ACTION` |
| `/submissions` | Submission operations | multi-role | yes | recently polished | none | `PASS_NO_ACTION` |
| `/attendance` | Room attendance | multi-role | yes | low P2 | none | `PASS_NO_ACTION` |
| `/checkins` | Check-ins | operations roles | yes | low P2 | none | `PASS_NO_ACTION` |
| `/swaps` | Swap coordination | operations roles | yes | residual labels | none | `SAFE_FIX_NOW` |
| `/swaps-v2` | Redirect to swaps | routing | routing check | none | none | `PASS_NO_ACTION` |
| `/sections` | Sections | multi-role | yes | low | none | `PASS_NO_ACTION` |
| `/copy` | Copy count | admin/staff | yes | low | none | `PASS_NO_ACTION` |
| `/print-queue` | Print queue | print shop | auth limited | role-specific | none | `DEFER_AUTH_LIMITATION` |
| `/workflow` | Workflow | reviewer roles | yes | low P2 | none | `ACCEPTABLE_WITH_NOTE` |
| `/workflow-v2` | Redirect to workflow | routing | routing check | none | none | `PASS_NO_ACTION` |
| `/coexam` | Co-exam | admin | yes | low | none | `PASS_NO_ACTION` |
| `/optimizer` | Optimizer | admin | yes | data-sensitive P2 | none | `DEFER_PRODUCT_DECISION` |
| `/optimizer-trace` | Optimizer trace | admin | yes | data-sensitive P2 | none | `DEFER_PRODUCT_DECISION` |
| `/staff-availability` | Staff availability | admin | yes | low | none | `PASS_NO_ACTION` |
| `/printreview` | Print review | reviewer roles | yes | residual deeper states | none | `SAFE_FIX_NOW` |
| `/external` | External exams | admin/staff | yes | residual deeper states | none | `SAFE_FIX_NOW` |
| `/exports-center` | Export center | admin/staff | yes | low | export wording | `PASS_NO_ACTION` |
| `/invigilation-advance-batch-preview` | Payment preview | admin/staff | yes | low | payment safety | `PASS_NO_ACTION` |
| `/invigilation-rate-rules` | Simple rate rules | admin/staff | yes | low | rate safety | `PASS_NO_ACTION` |
| `/invigilation-payment-document-draft` | Draft/review/export states | admin/staff | yes | high safety importance | payment/export | `PASS_NO_ACTION` |
| `/payment-document-settings` | Editable/read-only settings | reviewer/staff | yes | high safety importance | settings/payment | `PASS_NO_ACTION` |
| `/historical-schedules` | Historical comparison | admin | yes | data-sensitive P2 | none | `DEFER_PRODUCT_DECISION` |
| `/import` | Import | admin | yes | low | none | `PASS_NO_ACTION` |
| `/import-audit` | Import audit | admin | yes | low P2 | none | `ACCEPTABLE_WITH_NOTE` |
| `/period` | Exam periods | admin | yes | recently polished | none | `PASS_NO_ACTION` |
| `/settings` | Settings | admin/hidden | yes | low | none | `PASS_NO_ACTION` |
| `/settings-v2` | Redirect to settings | routing | routing check | none | none | `PASS_NO_ACTION` |
| `/platform-config` | Platform config | admin | yes | low | none | `PASS_NO_ACTION` |
| `/operational-health` | Operational health | admin/esq head | yes | low | none | `PASS_NO_ACTION` |
| `/audit-explorer` | Audit explorer | admin/esq head | yes | low | none | `PASS_NO_ACTION` |
| `/rooms-v2` | Rooms and availability | admin | yes | residual error fallbacks | none | `SAFE_FIX_NOW` |
| `/venues-v2` | Venue management | admin/hidden | yes | preview/custom P2 | none | `ACCEPTABLE_WITH_NOTE` |
| `/students-v2` | Student management | admin/hidden | yes | preview/custom P2 | none | `ACCEPTABLE_WITH_NOTE` |
| `/users` | User management | admin/hidden | yes | low | none | `PASS_NO_ACTION` |
| `/users-v2` | Redirect to users | routing | routing check | none | none | `PASS_NO_ACTION` |
| `/myexam` | Teacher submission workflow | teacher | auth limited | product-sensitive P2 | none | `DEFER_PRODUCT_DECISION` |
| `/exammanager` | Exam ownership | admin/supervisor | yes | low P2 | none | `ACCEPTABLE_WITH_NOTE` |
| `*` | Not-found/public redirect | routing | routing check | none | none | `PASS_NO_ACTION` |

## Initial Counts

- `SAFE_FIX_NOW`: `4` routes.
- `DEFER_WORKLOAD_SCOPE`: `3` routes.
- `DEFER_PRODUCT_DECISION`: `5` routes.
- `DEFER_AUTH_LIMITATION`: `1` route.
- All other declarations: pass or acceptable with note.

Final classifications are updated only if live regression evidence contradicts this matrix.
