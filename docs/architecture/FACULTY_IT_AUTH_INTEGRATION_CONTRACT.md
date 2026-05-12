# Faculty IT Auth Integration Contract
## EMS Academic Operations Platform — 2026-05-12

---

## 1. Purpose

This document defines the recommended integration contract between Faculty IT authentication services and EMS. It is intentionally designed to integrate with Faculty IT or Laravel-style auth flows **without rewriting EMS into Laravel/PHP**.

---

## 2. Current EMS Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy + Pydantic v2
- Session model: EMS-issued JWT + HttpOnly cookie (`ems_session`)
- Authorization model: EMS-owned RBAC via `auth_utils.py`, `permissions.py`, and `services/permission_service.py`
- Existing SSO stub: `backend/cmu_sso.py`

---

## 3. Why a Laravel Rewrite Is Not Recommended

- EMS already contains working academic workflow logic, QR flows, exports, scheduling, submissions, and role-aware operations.
- Rewriting would replace known hardening work with migration risk.
- The real integration requirement is identity proof exchange, not business-platform replacement.
- EMS should continue to own session issuance and RBAC even if Faculty IT owns upstream authentication.

---

## 4. Recommended Integration Model

```text
Faculty IT Auth / Laravel AuthMiddleware / AuthenController / callback/authen / cmu_at
    -> EMS Auth Integration Layer
    -> EMS JWT + HttpOnly session cookie
    -> EMS RBAC / permission_service
```

### Recommended EMS-side components
- `auth_integration_service`
- `cmu_identity_service`
- `session_service`
- callback or verification route under `/api/auth/...`

---

## 5. Required Callback Payload Fields

Faculty IT should provide either a signed callback payload, a verifiable token, or a code-exchange result that can resolve the following fields:

| Field | Required | Notes |
|------|----------|-------|
| `request_id` | Yes | Correlation ID for audit and troubleshooting |
| `provider` | Yes | Example: `faculty_it`, `cmu_oidc`, `laravel_gateway` |
| `username` | Yes | Primary EMS mapping key; should match `users.username` |
| `email` | Strongly recommended | Secondary match / audit trail |
| `display_name` | Yes | Human-readable name |
| `employee_id` or `student_id` | Recommended | For future canonical identity mapping |
| `faculty_code` | Recommended | For future faculty isolation |
| `department_code` | Recommended | For dept-scoped RBAC mapping |
| `issued_at` | Yes | Token/payload issuance time |
| `expires_at` | Yes | Expiration time |
| `signature` or verifiable token proof | Yes | Required for trust |
| `roles_hint` | Optional | Hint only; EMS remains RBAC authority |

---

## 6. Token Verification Expectations

EMS should not trust an opaque callback body without verification.

Minimum expectations:
- HTTPS only
- issuer validation
- audience/client validation
- signature validation or direct server-to-server token introspection
- replay protection using `state` and, where possible, nonce/request binding
- hard expiry enforcement
- clock-skew tolerance kept small

Preferred model:
1. Faculty IT issues short-lived code or token.
2. EMS verifies it directly, or verifies a signed assertion from a trusted gateway.
3. EMS resolves the user.
4. EMS issues its own JWT and HttpOnly cookie.

---

## 7. Session Lifecycle Expectations

### Upstream identity token
- Short-lived
- Used only to prove identity to EMS
- Not used as the EMS application session

### EMS session
- Issued by EMS after successful verification
- Stored in HttpOnly cookie
- Current default EMS session duration: `12 hours`
- Logout revokes the EMS token
- EMS session expiry should force re-authentication through Faculty IT

---

## 8. User Provisioning and Mapping Rules

### Recommended mapping order
1. `users.username`
2. `users.email`
3. future canonical identity table if added later

### Rules
- EMS remains the source of truth for application roles.
- Faculty IT may provide identity attributes but should not directly grant EMS admin roles.
- Missing EMS user mapping should not auto-create privileged accounts.
- Safe default for unmapped identities:
  - deny access, or
  - create a restricted pending profile requiring admin approval
- Inactive EMS users must remain denied even if upstream auth succeeds.

---

## 9. Audit Requirements

EMS must record:
- auth source/provider
- callback request ID
- matched username/email
- provisioning outcome
- session issuance success/failure
- permission-denied outcomes after successful identity proof

Do not log:
- raw secrets
- raw upstream tokens
- passwords
- unredacted signed payload blobs unless formally approved

---

## 10. Failure Modes

| Failure Mode | EMS Response |
|------|------|
| Invalid signature / unverifiable token | `401` / deny session |
| Expired upstream token | `401` / prompt re-auth |
| Missing required claims | `400` or `401` depending on source |
| Valid identity but no EMS user mapping | deny or restricted pending flow |
| Valid identity but user inactive in EMS | `403` |
| Upstream service timeout | fail closed; do not issue EMS session |
| Role mismatch between hint and EMS | use EMS role mapping and audit the mismatch |

---

## 11. Security Checklist

- [ ] HTTPS enforced end-to-end
- [ ] Callback endpoint allowlisted with Faculty IT
- [ ] `state` validation implemented
- [ ] Signature / token introspection validated
- [ ] Upstream expiry enforced
- [ ] No upstream token stored in browser-readable storage
- [ ] EMS continues issuing its own HttpOnly session cookie
- [ ] No automatic privileged provisioning
- [ ] Audit logs added for auth source, mapping, and failures
- [ ] Timeout and retry policy agreed between EMS and Faculty IT

---

## 12. Questions for Faculty IT

1. Will Faculty IT provide a direct callback payload, an OAuth/OIDC code flow, or a Laravel gateway assertion?
2. What is the exact issuer/audience/signature model?
3. Which field is the stable identity key for EMS mapping: `username`, `employee_id`, `student_id`, or another identifier?
4. What are the token TTLs and expected clock skew?
5. Can Faculty IT provide department/faculty codes in the verified payload?
6. Is a shared gateway mandatory, or can EMS verify directly?
7. Who owns incident response when upstream auth succeeds but EMS mapping fails?

---

## 13. Recommended Next Step

Use this contract to align with Faculty IT first. After sign-off, implement an EMS auth integration adapter on the current FastAPI backend. No Laravel rewrite should be started for auth alignment alone.
