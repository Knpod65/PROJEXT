# AUTH_BRIDGE_IMPLEMENTATION_GATE.md

**Date**: 2026-05-22  
**Status**: GATE — No bridge code may be written until all conditions below are met.

---

## A. Implementation Is ALLOWED Only When ALL of the Following Are Verified

- [ ] `session("USS")` payload has been confirmed against the real Laravel codebase
- [ ] CMU email source field name has been confirmed (not assumed)
- [ ] Token / `cmu_at` handling has been verified (lifetime, validation, scope)
- [ ] EMS mount path on Faculty LAN is decided and documented
- [ ] PostgreSQL target is confirmed and owned by EMS or clearly separated (not shared with Laravel app tables)
- [ ] Security model agreed: EMS resolves role from EMS database only, never from client-side claims
- [ ] Logout behavior agreed: both Laravel session and EMS session are cleared
- [ ] Audit logging plan defined for bridge auth events (what is logged, what is NOT logged)
- [ ] Auth bridge option selected (Option B preferred: short-lived server-side bridge code)
- [ ] Test scenarios defined and agreed with Laravel owner

---

## B. Implementation Is NOT Allowed When Any of the Following Are True

- [ ] `session("USS")` structure is unknown
- [ ] `cmu_at` meaning or lifecycle is unknown
- [ ] Frontend would receive raw CMU token (must never be exposed to frontend)
- [ ] Backend would trust CMU email from a client-side claim (must be server-verified)
- [ ] Role would be assigned client-side (must come from EMS database)
- [ ] Proxy headers can be spoofed by unauthenticated requests
- [ ] No audit logging plan for bridge auth events
- [ ] CMU email data flow has not been reviewed by DPO

---

## C. Accepted Bridge Options

| Option | Description | Status |
|--------|-------------|--------|
| **Option B** (Preferred) | Laravel issues one-time server-verified EMS login code; EMS exchanges it server-to-server | Allowed after contract verified |
| **Option A** | Laravel acts as auth gateway with server-side bridge | Allowed after contract verified and topology agreed |

**Note**: Both options require route, session, token, and cookie details to be fully verified before any code is written.

---

## D. Rejected / Explicitly Risky Options

| Pattern | Why Rejected |
|---------|------------|
| Raw email query parameter | Spoofable, no server-side verification |
| Frontend-stored `cmu_at` | Token exposure to browser, XSS risk |
| Spoofable reverse proxy header | Client can set any header value |
| Client-side role mapping | No server authority, easy to escalate |
| Trusting unsigned Laravel session cookie | Session can be crafted by client |

---

## E. Required Tests Before Merge

No auth bridge code may be merged without passing all of the following:

- [ ] Valid CMU email maps correctly to an existing EMS user
- [ ] Unknown CMU email is denied (or assigned a safe guest role, depending on policy)
- [ ] Role mismatch is denied (CMU identity does not override EMS DB role)
- [ ] Expired or replayed bridge code is rejected
- [ ] Logout clears both Laravel session and EMS session
- [ ] No CMU token (`cmu_at`) appears in any log line
- [ ] No CMU token is returned to the frontend
- [ ] Audit log entry is created for every successful bridge login

---

## F. Gate Decision Record

| Gate Check | Status | Date | Verified By |
|------------|--------|------|-------------|
| All contract questions answered | [ ] Unmet  [ ] Met | | |
| Session payload confirmed | [ ] Unmet  [ ] Met | | |
| CMU email field confirmed | [ ] Unmet  [ ] Met | |
| Token handling verified | [ ] Unmet  [ ] Met | | |
| EMS mount path decided | [ ] Unmet  [ ] Met | | |
| PostgreSQL target confirmed | [ ] Unmet  [ ] Met | | |
| Auth bridge option selected | [ ] Unmet  [ ] Met | | |
| Logout behavior agreed | [ ] Unmet  [ ] Met | | |
| Audit logging plan defined | [ ] Unmet  [ ] Met | | |
| All required tests passing | [ ] Unmet  [ ] Met | | |

**All checks must be MET before any bridge code is written or merged.**

---

---

## G. Lane-Specific Implementation Gates (Added 2026-05-25)

### CMU / POLSCI lane may start only when all are MET

- [ ] POLSCI callback payload verified against the real Laravel implementation
- [ ] Exact callback parameter names verified
- [ ] Verified CMU email field name confirmed
- [ ] Token lifecycle verified, including whether `cmu_at` exists and how it is handled
- [ ] `session("USS")` payload verified against live Laravel code
- [ ] EMS mount path and callback ownership verified

### External print-shop lane may start only when all are MET

- [ ] External identity owner selected (EMS-owned, Laravel-owned, signed-link flow, or other approved design)
- [ ] External account source selected and documented
- [ ] Print-shop permission matrix approved
- [ ] Audit logging requirements approved
- [ ] PDPA-minimized visible field set approved
- [ ] Route family for print-shop access approved as separate from student-facing routes

### Additional prohibitions

- [ ] No frontend token handling for POLSCI / CMU artifacts
- [ ] No trust in query-string email
- [ ] No trust in frontend role claims
- [ ] No treatment of print-shop users as fake CMU students or fake staff

---

**End of AUTH_BRIDGE_IMPLEMENTATION_GATE.md**  
This gate is the hard constraint. Do not bypass it for any timeline reason.
