# Invigilation Rate Rule Frontend Decision Gate

**Date**: 2026-06-02

## Decision

`IMPLEMENT_PAGE_NOW`

## Reason

- Backend rate-rule endpoints are small, isolated, and configuration-only.
- The page can use existing EMS `Card`, `Badge`, `Button`, and `DataTable` patterns.
- The UI can clearly label rates as preview/configuration only.
- No final payment, approval, or export action is needed.

## Constraints

- Page visible to admin and staff.
- Backend write actions remain admin-only.
- Staff may view rates; mutation failures must be shown safely.
- No official payment wording.
- No amount calculation outside the user-entered rate value.

