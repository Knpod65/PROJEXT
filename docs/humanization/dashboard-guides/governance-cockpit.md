# Governance Cockpit Guide

## What This Is For

This dashboard explains what is blocked, what is pending, and what is ready to publish.

It is the best place to check if the system is safe to move forward.

## What To Look At First

- Pending approvals
- Publication blockers
- Escalation count
- Rollback or exception events
- Audit completeness

## What The Colors Mean

- Green: the control is satisfied
- Amber: the workflow is waiting or incomplete
- Red: a blocker or policy issue is preventing release

## What Matters Operationally

- A blocker means the work is not ready yet.
- An approval item means a human decision is required.
- An audit gap means the workflow may be incomplete or unsafe to publish.

## Recommended Action Pattern

1. Check whether the blocker is policy, approval, or data quality.
2. Find the owning role.
3. Confirm whether the issue can be resolved without changing the workflow path.
4. Escalate if publication, trust, or traceability is affected.
