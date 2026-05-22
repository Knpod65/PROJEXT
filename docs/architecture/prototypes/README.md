# Deferred EMS Prototypes

This directory is reserved for prototype and research-oriented EMS materials that are not part of the production runtime.

## Purpose

- Preserve exploratory architecture notes, prototype references, and future-phase concepts without presenting them as production-ready features.
- Keep speculative work separate from the active runtime until it is reviewed, tested, and explicitly promoted.

## Status

- Prototype and research content only
- Not approved for production use
- May reflect incomplete assumptions or future-state ideas
- Must not be treated as current runtime behavior

## Guardrails

- Do not merge prototype services, policies, or other speculative assets into production workflows without explicit review.
- Do not wire prototype materials into runtime code paths without tests, validation, and implementation approval.
- Keep experimental or future-phase concepts separate from committed production behavior until they have clear ownership and acceptance criteria.

## Relationship To Current Readiness Docs

Production and pilot decisions should be taken from the active readiness and operations documentation in the main `docs/` tree, not from prototype materials stored here.

## Working Rule

Anything stored in this directory should be assumed non-production unless a later documented hardening and promotion pass says otherwise.
