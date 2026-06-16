# EMS Thai Export Non-Regression Record

Date: 2026-06-16

## Preserved Backend Behavior

- Existing endpoints remain unchanged.
- Existing request and response schemas remain unchanged.
- Existing authorization dependencies remain unchanged.
- Existing review and payment settings gates remain unchanged.
- Existing RC1 draft summary export data and formulas remain unchanged.
- Existing supporting finance roster aggregation, deduplication, room mapping, and five-sheet contract remain unchanged.
- Historical CSV content remains CSV with Excel-compatible UTF-8 BOM.

## Explicitly Not Added

- No payment approval workflow.
- No final authorization workflow.
- No official-final export.
- No new backend route.
- No proprietary font file.

## Regression Evidence

Focused test coverage passed for:

- Export helper header/encoding/font contract.
- RC1 draft payment export gates and workbook bytes.
- Supporting finance roster source, mapping, permissions, gates, and workbook structure.

Full backend regression coverage also passed: `1588 passed, 17 warnings`.

Frontend build and i18n checks passed even though no frontend source was changed:

- `npm run build`
- `npm run check:i18n`
- `npm run check:i18n:raw`

The expected development warnings about missing local `SECRET_KEY`, SQLAlchemy/Pydantic deprecations, and test-environment configuration remain unrelated to this pass.
