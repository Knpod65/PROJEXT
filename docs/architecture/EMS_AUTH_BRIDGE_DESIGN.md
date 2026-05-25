# EMS_AUTH_BRIDGE_DESIGN.md (Updated for Faculty Web Portal)

**Date**: 2026-05-25 (updated from previous LAN version)

**Purpose**: Define the safe target architecture for bridging EMS authentication with the **Faculty Web Portal** (Laravel/CMU email auth system). No bridge code may be written until the contract is verified.

## Updated Context

- Target environment is now the Faculty Web Portal (PHP/Laravel faculty website), not a pure LAN-only server.
- EMS may be mounted under a path such as /ems or exposed via proxy.
- Central faculty web OAuth patterns exist (ServiceUrl → /oauth/callback).
- CMU email remains the primary identity for authenticated users.
- Print shop / external partner users must remain a separate lane (do not force fake CMU identity).

## High-Level Integration Models (Still Pending Contract)

### Model 1 — Laravel as Central Auth Handler (Preferred Direction)
- User logs in via faculty web / POLSCI OAuth.
- Laravel validates and issues a short-lived, signed token or session artifact to EMS (e.g. via redirect with one-time code or trusted internal header when proxied).
- EMS validates the artifact, creates its own session/JWT, and issues HttpOnly cookie.
- Logout can be coordinated (Laravel central or EMS local with notification).

### Model 2 — Direct ServiceUrl to EMS Callback
- Faculty web configures ServiceUrl pointing directly to EMS callback endpoint.
- EMS receives the OAuth response, validates it (using shared secret or JWKS), maps CMU email, creates session.
- Still requires verified payload structure (session("USS"), cmu_at, etc.).

### Model 3 — Hybrid (Print Shop External + CMU via Laravel)
- CMU users go through faculty web OAuth.
- Print shop users use a separate external partner flow (Laravel external accounts or EMS-managed).
- EMS receives verified identity + role/scope from the appropriate source.

## Critical Unknowns (Must Be Answered Before Any Code)

See the updated questions in LARAVEL_AUTH_CONTRACT_QUESTIONS.md (reframed for Faculty Web Portal).

Key new/updated questions for web portal target:
- Can EMS be mounted at /ems (or other path) under the faculty web domain?
- Will the faculty web reverse proxy forward the original OAuth response, or will Laravel act as the sole callback handler?
- What exact payload / headers / token will EMS receive for a verified CMU user?
- How will print shop external users authenticate when the app lives under the faculty web?
- What is the cookie domain and path policy when the frontend is served from portal.mis.pol.cmu.ac.th/ems?

## Security & Audit Requirements (Unchanged)

- Never trust unauthenticated input for identity.
- All identity must be verified server-side.
- Full audit trail of auth events (who, when, from which source).
- Fallback to current standalone username/password must remain available during transition.
- No production secrets or real OAuth client credentials in EMS until contract is closed.

## Implementation Gate (Reinforced)

Auth bridge code may only begin after:
- Contract answers verified against actual Laravel codebase.
- Security reviewer sign-off on the chosen model.
- Leadership decision recorded in post-demo decision documents.
- Clear mount path and proxy model confirmed.

---
*This is an evolution of the previous LAN-focused design. The core safety principles remain identical.*
