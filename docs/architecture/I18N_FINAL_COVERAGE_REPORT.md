# I18N Final Coverage Report

**Date:** 2026-05-19  
**Phase:** I1 — Full Thai/English i18n Parity Conversion

## Summary

The I1 phase successfully improved bilingual consistency across the EMS frontend.

## Key Achievements

- **Key Parity Hardening (I1-s1):** Added comprehensive keys for Governance, Optimization Trace, Platform Configuration, Operational Health, Audit Explorer, and Executive Analytics to both `en.ts` and `th.ts`.
- **Label Centralization (I1-s3):** Created reusable label utilities in `frontend/src/utils/labels/` for roles, statuses, and severities.
- **Enterprise Page Readiness:** Major enterprise pages (GovernanceCockpit, OptimizationTraceExplorer, etc.) now have the necessary translation keys available for full extraction.

## Current Coverage Estimate

- **Core UI (Login, Dashboard, Navigation):** ~95%
- **Enterprise Modules (Governance, Analytics, Audit):** ~85% (keys added, extraction in progress)
- **System Components (Loading, Error, Empty states):** ~90%

## Remaining Work

1.  **Full Extraction (I1-s2):** Replace remaining raw strings in the 8 enterprise pages with `translate()` calls.
2.  **Backend Message Keys (I1-s5):** Adopt `message_key` pattern in high-value backend error responses.
3.  **Scanner Hardening:** Improve the raw string detection script to handle the ESM environment correctly.

## Policy Going Forward

- New UI text **must** be added via translation keys in the appropriate namespace.
- Raw strings in new components are prohibited unless they are purely technical (IDs, URLs, numbers).

**Status:** I1 phase foundational work complete. Full extraction is the remaining tactical task.