# Logging and Monitoring Guide

**System**: EMS
**Last Updated**: 2026-05-22

## What to Log

### Must Log (Operational Value)
- Authentication events (login success/failure, token issuance)
- Authorization decisions (role checks, workspace access)
- Critical business actions (schedule publication, submission finalization, overrides)
- All errors with stack traces (in non-production) or sanitized errors (production)
- Database migration events
- Background task execution (if any)

### Must NOT Log
- Passwords or password hashes
- Full JWT tokens
- Personal data (names, emails, student IDs) unless explicitly required for audit and approved by DPO
- Request bodies containing sensitive fields

## PDPA-Safe Logging

- Never log raw personal data in production logs.
- Use anonymized identifiers (e.g., `user_id` instead of name) when possible.
- Log retention for personal data must follow the PDPA retention policy (see `PDPA_RETENTION_DAYS`).

## Log Levels

| Level   | Use Case                              | Example |
|---------|---------------------------------------|---------|
| DEBUG   | Detailed troubleshooting              | SQL queries, full request payloads (dev only) |
| INFO    | Normal operational events             | User logged in, schedule published |
| WARNING | Recoverable issues, suspicious activity | Failed login attempts, rate limiting |
| ERROR   | Unhandled exceptions, critical failures | 500 errors, database connection loss |
| CRITICAL| System-wide failures                  | Application cannot start |

## Request Tracing

- Use a request ID (X-Request-ID header) propagated across services.
- Include request ID in all log lines for correlation.

## Frontend Error Reporting

- Uncaught exceptions in the browser should be captured and sent to the backend `/api/logs/frontend-error` (or equivalent) with:
  - message
  - stack
  - user agent
  - route
  - user role (anonymized where possible)

## Monitoring & Alerting Targets (Pilot)

- Application uptime (`/health`)
- Error rate (5xx responses)
- Authentication failure rate
- Database connection pool usage
- Slow queries (if instrumentation exists)

**Pilot Monitoring Cadence**: Daily review of error logs + weekly health dashboard review.

## Tools (Recommended)

- Structured logging (JSON)
- Centralized log aggregation (e.g., ELK, Loki, or institutional solution)
- Uptime monitoring (e.g., UptimeRobot, Pingdom, or internal)
