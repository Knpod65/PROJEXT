# I18N GUIDE

## Current Implementation

- Provider: `frontend/src/i18n/index.tsx`
- Dictionaries:
  - `frontend/src/i18n/en.ts`
  - `frontend/src/i18n/th.ts`
- Languages:
  - English (`en`)
  - Thai (`th`)

## How Translation Works

- `I18nProvider` stores the active language in React state
- language preference is persisted in local storage (`ems.language`)
- document language attribute is synchronized on change
- `t(key, params)` resolves the current language
- fallback chain:
  1. active language
  2. English
  3. final fallback string/key caller behavior

## Missing Key Logging

- Missing-key warnings are dev-only
- Current warning format:
  - `[EMS i18n] Missing translation key: ...`
- Repeated warnings are deduplicated during a session

## Naming Conventions

Use domain-first keys.

Examples:
- `navigation.pages.schedule.title`
- `dashboard.pendingSwaps`
- `workflowV2.issueType.room_capacity_exceeded`
- `staffAvailability.actions.saveBlock`
- `exportCenter.cards.examDocuments.title`
- `checkins.pickupModal.note`

Use `common.*` only for true cross-app UI labels.

## Rules For Adding New UI

1. Add English and Thai keys together.
2. Use `t(...)` or `translateWithFallback(...)`.
3. Do not ship hardcoded UI labels in JSX.
4. Keep domain keys grouped in both translation files.
5. Reuse existing `common.*` keys for shared labels like date/time/status/confirm.

## Recommended Workflow

1. Build UI with stable domain names first.
2. Choose the translation namespace before writing the component.
3. Add keys in `en.ts` and `th.ts`.
4. Wire the component with `useI18n()`.
5. Run build and a key audit before merging.

## Runtime Helpers

- `translate(...)`: global helper using current language
- `translateWithFallback(...)`: safe helper when a component still needs a human-readable fallback
- `formatRole(...)`: role label translation helper
- `formatTranslatedValue(namespace, value)`: translate structured enum-like values

## Common Pitfalls

- adding keys only in one language file
- hardcoding button/empty-state text in pages
- using backend/raw values directly without mapping when the value is part of the UI vocabulary
- forgetting that navigation text also needs dictionary entries

## Validation Checklist

- no literal missing-key audit failures
- no console warning for missing translation keys in dev
- language toggle updates active page immediately
- no mixed-language headers/buttons on translated screens
