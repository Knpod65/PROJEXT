# Payment Document Configurable Settings Model

**Date**: 2026-06-08  
**Status**: model scaffold only  
**Current implementation decision**: `DOCS_ONLY_MODEL_NOW`

## Purpose

Define future configurable settings needed for payment-related draft documents. Settings support draft preparation and review only. Settings alone do not authorize payment, final export, or final payment truth.

## Rate Settings

| Field | Purpose |
|---|---|
| `term` | Academic term or term-specific scope. |
| `weekday_rate` | Monday-Friday amount per person/session. |
| `weekend_rate` | Saturday-Sunday amount per person/session. |
| `effective_term` | Term where the rate applies. |
| `status` | Draft, active-for-draft, archived, or pending approval. |
| `changed_by` | User/person who changed the setting. |
| `changed_at` | Change timestamp. |
| `note` | Evidence, memo, or explanation. |

## Paper-Distribution Responsibility Settings

Default conceptual group:

`Education_Student_Quality`

| Field | Purpose |
|---|---|
| `responsible_group` | Current group/unit responsible for paper-distribution committee data. |
| `responsible_person` | Named responsible person, if applicable. |
| `effective_from` | Start date or term. |
| `effective_to` | End date or term, if known. |
| `status` | Active, pending, archived, or superseded. |
| `change_reason` | Why responsibility changed. |
| `updated_by` | User/person who updated responsibility. |
| `updated_at` | Update timestamp. |

## Why Settings Must Be Configurable

- Compensation rates can change by term or approved policy.
- Staff turnover is frequent.
- Paper-distribution responsibility may move between people or groups.
- Official document drafts must not depend on hardcoded names, groups, or permanent assumptions.
- Future audits need to know which setting was in force for each draft.

## Safety Rules

- Settings support draft preparation and review only.
- Settings do not authorize payment.
- Settings do not create official PDF/Excel/export.
- Settings do not make manual paper-distribution rows final payable truth.
- Active EMS rate changes remain a separate controlled configuration action.
