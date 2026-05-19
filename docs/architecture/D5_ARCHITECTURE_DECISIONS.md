# D5 Architecture Decisions (ADRs)

## ADR-001: Analytics Endpoint Location

**Status**: Accepted
**Context**: Where to place thin-proxy analytics endpoints for governance-timeline and lifecycle-timeline
**Decision**: Append to existing `/api/analytics` router to maintain codebase cohesion
**Consequences**: Single source of truth for analytics, no new router needed

## ADR-002: PDPA Boundary Enforcement

**Status**: Accepted
**Context**: Need runtime validation for PII exposure in responses
**Decision**: Implement `pdpa_runtime_guard_service.py` with pure-dict validation (no ORM)
**Consequences**: Zero change to existing callers, additive safety layer

## ADR-003: Secrets Environment-only

**Status**: Accepted
**Context**: `.env` files committed by accident leak secrets
**Decision**: Add CI check for `.env` patterns in commits; runtime warning if dev SECRET_KEY used
**Consequences**: Safer defaults, clearer production readiness signal

## ADR-004: Nginx Server Name Wildcard

**Status**: Accepted
**Context**: `nginx.conf` uses `server_name _` (H-7)
**Decision**: Keep wildcard for flexhosting; domain tightening deferred to pre-production
**Consequences**: Works in dev/staging; production needs explicit domain config

## ADR-005: Bundle Code-splitting

**Status**: Accepted
**Context**: Main bundle 687KB (gzip 184KB) exceeds 500KB warning
**Decision**: Lazy-load heaviest routes via `React.lazy(() => import(...))`
**Consequences**: Faster initial load; route-specific chunks smaller