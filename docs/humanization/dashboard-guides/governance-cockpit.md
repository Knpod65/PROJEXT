# Governance Cockpit Guide

## What This Is For

This dashboard explains what is blocked, what is pending, and what is ready to publish.

It is the best place to check if the system is safe to move forward.

## Live Screenshot

![Governance Cockpit](../screenshot-atlas/images/governance/governance-cockpit-viewport.png)

Full page:
[governance-cockpit-full.png](../screenshot-atlas/images/governance/governance-cockpit-full.png)

Responsive variants:
[governance-cockpit-tablet.png](../screenshot-atlas/images/governance/governance-cockpit-tablet.png) · [governance-cockpit-mobile.png](../screenshot-atlas/images/governance/governance-cockpit-mobile.png)

## Current Capture Note

The page rendered, but the local screenshot still shows untranslated governance labels such as `governance.healthScore`.

That visual gap is recorded intentionally so the manuals stay honest about the current runtime state.

## What To Look At First

- Pending approvals
- Publication blockers
- Escalation count
- Rollback or exception events
- Audit completeness

## Dashboard Reading Order

1. Start with the risk band and overall governance signal.
2. Scan blockers and pending approvals before reading detailed events.
3. Check recent events only after you understand whether release is already blocked.
4. Open audit or workflow follow-up if traceability is unclear.

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

## What Action Should I Take?

- Hold publication when blockers or missing approvals affect release safety.
- Use `Audit Explorer` when the issue is sequence, ownership, or missing trace evidence.
- Use `Operational Health` if the page suggests platform instability rather than workflow disagreement.
