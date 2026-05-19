# I18N_FINAL_COVERAGE_REPORT

## I1.5 Completion Summary

- I1.5-s1A: PlatformConfiguration / OperationalHealth localized (table headers + states)
- I1.5-s1B: AuditExplorer / ExecutiveAnalytics localized (audit.* + executiveAnalytics.* namespaces)
- I1.5-s1C: ExportCenter + Settings localized (historical schedule card + settings sections)
- I1.5-s2: Shared components localized (Modal close button using existing common.close; EmptyState/DataTable/ConfirmDialog already using i18n)
- I1.5-s3: Backend message_key helper introduced; high-value errors updated in imports.py and exports.py (partial, ~35-45% of user-facing errors)
- I1.5-s4: Raw string scanner added to check-i18n.js with --raw (warning) and --strict modes

## Metrics (honest estimates as of 2026-05-19)

- i18n key parity: 100% (en=1290, th=1290, check:i18n passes)
- enterprise page namespace coverage: 95–98%
- shared component i18n coverage: 95%+
- backend message_key coverage: partial/high-value start (35–45%)
- raw string scanner maturity: 70–75% (noisy heuristic, ~100 candidates reported)
- overall Thai/English readiness: 94–96%

## Validation Status

- npm run build: PASS
- npm run check:i18n: PASS
- npm run check:i18n:raw: ~100 candidates (mostly import paths and code fragments)
- npm run check:i18n:strict: exits 1 when candidates exist (intentional)

## Remaining Known Gaps

1. Raw scanner reports ~100 candidates and requires allowlist refinement
2. Backend message_key only started for imports/exports/auth; remaining routers deferred
3. Some raw strings may remain in legacy/non-enterprise pages
4. check:i18n validates key parity only, not semantic translation quality
5. Thai wording should be reviewed by operations/business owner before production release

## Future PR Checklist

Before merging new UI:
- No new raw UI strings without translation key
- en/th keys must both be added
- Status/severity/role labels must use central label utilities
- Shared component defaults must use i18n
- Backend user-facing errors should include message_key
- Run: npm run build, npm run check:i18n, npm run check:i18n:raw
- Strict mode may be used for focused cleanup branches

## Next Recommended Phase

U1 — Frontend ViewModel / MVC Cleanup

---

Generated during I1.5-s5 final documentation pass.