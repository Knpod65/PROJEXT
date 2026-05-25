# SECURITY_PDPA_100_PERCENT_READINESS_SCORE.md

**Date**: 2026-05-25  
**Audit**: EMS 100% SYSTEM READINESS AUDIT  
**Sources**: SECURITY_PDPA_AUTHORIZATION_AUDIT.md (2026-05-22), HIGH_RISK_HARDENING_TRIAGE, SAFE_CODE_HARDENING_PLAN, LARAVEL_AUTH_CONTRACT_QUESTIONS, fresh code inspection (security.py, settings.py, main.py, auth.py, permissions.py), validation baseline

---

## Security / PDPA / Auth Scores (0–100)

| Dimension | Score | Evidence | Why Not 100 | Demo Safe? | Pilot Safe? | Production Safe? |
|-----------|-------|----------|-------------|------------|-------------|------------------|
| 1. Secret handling | 72 | settings.py production enforces 50+ char + no empty; security.py validate_production_secrets + INSECURE list + lifespan call; dev fallback with warning; no hardcoded prod secrets | Minor ENV/ENVIRONMENT drift remains (pdpa_runtime_guard_service prefers ENV); no secret manager / rotation evidence; compose still has placeholder examples | Yes (local only) | **No** — must unify + prove real secrets on target | **No** |
| 2. Auth flow safety | 78 | JWT + HttpOnly cookie primary; revocation support; role selection; print_shop isolated lane; cmu_sso stub inactive | Login still returns bearer token in response body (auth.py); no contract for Laravel session("USS") / cmu_at / CMU email mapping | Yes (standalone demo accounts work) | **No** — contract unverified; bridge not implemented | **No** |
| 3. Backend authorization | 86 | permissions.py central RBAC (273 lines, role sets, object-level, build_dependencies()); all guarded routers use it; policy layer for PDPA/export | Split with auth_utils.py; some inline checks remain; no automated policy test for every route | Yes | Medium (after bridge) | High (after evidence) |
| 4. Frontend trust boundaries | 65 | auth.store.tsx central; api.ts credentials:include; role guards in App.tsx; no localStorage token storage by default | Frontend still trusts server for role data; no signed claims validation on client; raw role from /me possible | Low risk for demo | High risk if bridge returns unverified roles | Critical |
| 5. Audit logging | 82 | Immutable audit service + outbox + handlers; event model; PDPA policy; request id correlation | No tamper-proof storage proof; export audit not yet wired to retention | Yes | Medium (needs DPO review) | High |
| 6. PDPA data minimization | 70 | Policies exist (pdpa_policy, event_pdpa, optimization_trace_pdpa); consent/ purpose fields in models; retention config | No runtime minimization enforcement visible; no DPO sign-off on CMU email flow through Laravel | Yes (demo data fake) | **No** — requires signed DPO + real data flow | **No** |
| 7. Backup / retention readiness | 40 | Runbooks exist (BACKUP_AND_RESTORE_RUNBOOK, DISASTER_RECOVERY); evidence template in ops/ | **No actual backup/restore executed on target Faculty PostgreSQL**; no retention test evidence attached to blocker dashboard | N/A (demo uses sqlite) | **Critical blocker** | Critical |
| 8. External partner access (print_shop) | 75 | Isolated lane with own token expiry; separate from CMU SSO | No contract for external print shop identity provider; print_shop ops role has broad access | Yes (mocked) | Medium (after IT approval) | High |
| 9. Laravel / POLSCI OAuth readiness | 35 | Excellent analysis docs (POLSCI_OAUTH_FLOW, HYBRID_AUTH_MODEL, LARAVEL_AUTH_CONTRACT_QUESTIONS 203 lines, closure tracker) | **Zero answers received** from Laravel owner/IT; session("USS"), cmu_at, callback ownership, EMS mount path, logout all TBD | N/A (demo does not use) | **0% until answered + verified** | 0% |
| 10. Production evidence | 30 | Hardening plan + triage exist; secret checks improved; startup/DB now gated | No real Faculty LAN env, no DPO sign-off, no backup proof, no load test, no incident response drill, no PDPA compliance certificate | N/A | **No** | **No** |

**Overall Security/PDPA/Auth Score: 61 / 100**

**Clear Separation**:
- **Safe for Demo 100%**: Standalone auth (local accounts: mathawee.m/admin123 etc.), RBAC, logging, dev secret warnings. No external bridge claimed.
- **Not safe for Pilot 100%**: Laravel contract unverified (biggest blocker), no backup/DPO evidence on real PostgreSQL, minor env drift.
- **Far from Production 100%**: Requires all pilot items + secret management, full PDPA sign-off, tamper-proof audit, production evidence chain.

**Top Blockers**:
1. LARAVEL_AUTH_CONTRACT_QUESTIONS.md unanswered (P0 for any integrated pilot).
2. No executed backup/restore + DPO sign-off on target DB.
3. Remaining ENV drift + login body token.

**Evidence**: All from disk + run (no fabrication).

---
*Security posture is appropriate for controlled demo. Pilot/production require external contracts and operational proof.*
