# Humanization Strategy

## Goal

Make EMS feel safe to use.

The platform is already capable. The documentation must now reduce fear, reduce cognitive load, and make each workflow feel like a guided operational path instead of a maze of institutional controls.

## Principles

### 1. Progressive Disclosure

Show the minimum needed information first.

Users should only see the deeper layers when they need them.

### 2. Role-First Entry

Every guide should begin with the user’s role and daily task, not with system internals.

### 3. Operational Meaning Before Technical Meaning

Explain what something means in real work before explaining how the system computes it.

### 4. Escalation Before Deep Repair

If something looks wrong, the first question is who should handle it and how urgent it is.

### 5. One Page, One Job

Each dashboard or page should be documented around one primary operational question.

### 6. Human Labels Over Internal Labels

Use plain language in guides even when the internal service or route names are technical.

## Simplification Model

### Beginner Mode

- Show only the main task path
- Explain icons, colors, and alerts in plain language
- Hide advanced governance and trace details unless needed

### Operator Mode

- Show the daily workflow
- Include warnings, common mistakes, and escalation paths
- Keep analytics tied to operational decisions

### Governance Mode

- Show approval rules, traceability, audit consequences, and publication gates
- Explain why a control exists, not just that it exists

### Executive Mode

- Show decision-ready summaries
- Reduce charts to trend, risk, and next action
- Avoid implementation detail unless a decision depends on it

## Documentation Sequence

The recommended writing order is:

1. System cognitive map
2. Humanization strategy
3. Master document tree
4. Role manuals
5. Dashboard interpretation guide
6. Troubleshooting guide
7. Playbooks
8. Screenshot atlas
9. Visual journey book
10. Training handbook

## Cognitive Load Reduction Rules

- Limit every dashboard explanation to the few signals that matter most.
- Use consistent terms for urgency, readiness, risk, and escalation.
- Avoid mixing governance language with operational language unless both are needed.
- Break large workflows into numbered steps and short callouts.
- Keep the first version of each guide short enough that users can finish it.

## What To Avoid

- Explaining every backend layer in one guide
- Using the same page to teach role behavior and architecture theory
- Overusing tables when a simple step list is clearer
- Treating advanced intelligence views as if they were beginner dashboards
- Describing metrics without telling people what to do with them

## Practical Outcome

After this strategy is applied, a user should be able to:

- open the right page for their role
- recognize what the dashboard is telling them
- understand what needs attention now
- know when to escalate
- trust that the platform is helping rather than overwhelming them
