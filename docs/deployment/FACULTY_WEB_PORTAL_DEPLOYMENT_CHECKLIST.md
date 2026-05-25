# FACULTY_WEB_PORTAL_DEPLOYMENT_CHECKLIST.md

**Date**: 2026-05-25

## Pre-Deployment Checklist (Faculty Web Portal)

### 1. Mount Path & Routing
- [ ] Confirmed exact frontend mount path (e.g. /ems)
- [ ] Confirmed API proxy prefix (e.g. /ems-api)
- [ ] Faculty web reverse proxy rules documented and tested in staging
- [ ] Frontend VITE_APP_BASE_PATH and VITE_API_BASE_URL configured for target
- [x] Subpath build compatibility validated locally (root + /ems + /ems-api) — see FACULTY_WEB_SUBPATH_BUILD_VALIDATION_LOG.md
- [x] Root assumption + direct API call hardening completed (2026-05-25) — all internal window.location/root href + /api bypasses centralized via helpers; post-fix builds + i18n validated. See FACULTY_WEB_ROOT_PATH_HARDENING_AUDIT.md + FACULTY_WEB_API_BASE_HARDENING_AUDIT.md + EXPORT_DOWNLOAD_PATH_REVIEW.md

### 2. Auth / OAuth
- [ ] Laravel / Faculty Web auth contract fully answered and verified
- [ ] ServiceUrl / callback strategy decided and tested
- [ ] Verified identity payload structure (CMU email, roles, scope)
- [ ] Print shop external access model chosen and implemented (or fallback documented)
- [ ] Logout behavior agreed (single sign-out or separate)

### 3. Database
- [ ] PostgreSQL target (dedicated EMS DB or schema) provisioned
- [ ] Connection string and credentials configured in hosting environment
- [ ] Backup/restore tested with evidence
- [ ] Migration ownership and process agreed
- [ ] No real data loaded without DPO approval

### 4. Proxy / Headers / Cookies
- [ ] X-Forwarded-Proto, Host, Prefix headers correctly forwarded
- [ ] FastAPI configured with appropriate root_path or trusted proxy middleware
- [ ] Auth cookies use correct Secure, SameSite, domain, path for the portal domain
- [ ] CORS origins restricted to faculty web domains only

### 5. Observability & Operations
- [ ] Health endpoint exposed and monitored through faculty web tier
- [ ] Logs aggregated with faculty web logging
- [ ] Error tracking / alerting configured
- [ ] Rollback plan documented and tested

### 6. Security & Compliance
- [ ] DPO review completed for web portal data flows
- [ ] Secrets managed via faculty web hosting secrets store (no .env with real values)
- [ ] Rate limiting and security headers verified in portal context
- [ ] Audit logging includes source (faculty web vs direct)

### 7. Testing
- [ ] Full browser smoke under the actual web portal paths (not just local root)
- [ ] All roles tested with real faculty web login (when auth bridge ready)
- [ ] Print shop external lane tested end-to-end
- [ ] Performance / load acceptable under faculty web hosting

### 8. Documentation & Handover
- [ ] Updated runbooks for faculty web operations team
- [ ] On-call / escalation process agreed
- [ ] Training for faculty web support staff (if needed)

Only proceed to staging deployment when the majority of items above have evidence or explicit waivers.

---
*This checklist replaces previous pure LAN deployment checklists.*
