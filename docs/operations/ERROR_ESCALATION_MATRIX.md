# Error Escalation Matrix

**System**: EMS
**Last Updated**: 2026-05-22

## Severity Levels & Response

| Severity | Description                              | Response Time | Primary Owner     | Escalation Path                  | Example |
|----------|------------------------------------------|---------------|-------------------|----------------------------------|---------|
| **Critical** | Complete outage or data loss affecting all users | Immediate (< 15 min) | System Owner + IT Lead | DPO (if PDPA), Executive Sponsor | Database down, major security breach |
| **High**     | Major feature broken for large user group | < 1 hour     | System Owner      | IT Lead → DPO (if needed)        | Submissions blocked for entire faculty |
| **Medium**   | Partial degradation or limited impact    | < 4 hours    | On-call Developer | System Owner                     | One dashboard slow, export failing for some users |
| **Low**      | Minor issue, workaround exists           | Next business day | Developer        | Team Lead                        | UI text error, non-critical report glitch |
| **Security** | Potential or confirmed security incident | Immediate    | Security Lead + DPO | Executive Sponsor + Legal        | Unauthorized data access, token leak |

## Who Responds to What

- **Critical / Security**: System Owner + IT + DPO must be notified immediately (phone/SMS + ticket).
- **High**: System Owner + relevant module owner.
- **Medium / Low**: Assigned via ticket queue during business hours.

## Escalation Rules

1. If no update within SLA → escalate to next level.
2. Any incident involving personal data (even suspected) → DPO must be informed within 1 hour.
3. All Critical and Security incidents require a Post-Incident Review within 5 business days.

## Communication

- Use the incident communication template from the Disaster Recovery Runbook.
- Status updates every 30–60 minutes for P1/P2 incidents until resolved.

## Pilot Phase Adjustments

During controlled pilot:
- All High and above incidents must also be logged in the Pilot Feedback Tracker.
- DPO is notified for any incident rated Medium or higher that touches submission or personal data.
