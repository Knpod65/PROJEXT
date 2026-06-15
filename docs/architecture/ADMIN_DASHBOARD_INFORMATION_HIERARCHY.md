# Admin Dashboard Information Hierarchy

**Date**: 2026-06-15  
**Design direction**: calm, actionable institutional command center

## Level 1: Orientation

The reused `PageHeader` provides a localized eyebrow, concise purpose statement, overall display status, active-period label, and last-computed timestamp. Language and user identity remain in the existing application shell.

## Level 2: Primary Summary

Five cards answer the first operational questions:

1. Overall readiness
2. Scheduled progress
3. Unscheduled sections
4. Governance blockers
5. Consolidated system availability

The cards separate values from units, use compact state badges, and expose an action only when the represented state is degraded and actionable.

## Level 3: Analysis And Priorities

- A reused `DonutChart` shows scheduled versus unscheduled sections from existing totals.
- A reused `BarChart` compares only available percentage or score metrics.
- A priority alert explains why the overall state needs attention.
- A priority list is capped at five issues and includes contextual actions.

No unsupported time-series, slot, date, or personnel distribution is presented.

## Level 4: Detail

Secondary metrics are organized into five tabs:

- Scheduling
- Governance
- People
- Delivery
- System

Each metric shows a localized title, display state, separated value/unit, concise explanation, optional restricted-data badge, and an action only when useful.

## Responsive Behavior

Scoped `.admin-command*` styles reduce the five-card grid at narrower breakpoints, stack analysis panels, preserve wrapping, and avoid horizontal overflow. No new dependency or design system was introduced.

