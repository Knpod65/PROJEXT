# Payment Document Settings API Contract

**Date**: 2026-06-08  
**Status**: implemented draft-preparation settings contract  
**Authorization boundary**: settings do not authorize payment or export

## Settings Object

```json
{
  "settings_id": "payment-document-settings-2-2568",
  "term": "2/2568",
  "weekday_rate": 120,
  "weekend_rate": 200,
  "currency": "THB",
  "payment_unit": "PER_PERSON_SESSION",
  "paper_distribution_responsible_group": "Education_Student_Quality",
  "paper_distribution_responsible_person": null,
  "status": "DRAFT_CONFIG",
  "configuration_status": "CONFIGURED",
  "effective_from": null,
  "effective_to": null,
  "note": "Draft settings for document preparation only",
  "updated_by": 1,
  "updated_at": "2026-06-08T00:00:00Z",
  "payment_authorization_enabled": false,
  "final_export_enabled": false
}
```

If no row exists for a term, `GET /api/payment-document-settings/{term}` returns `configuration_status = PENDING_CONFIGURATION`, null rates, and the suggested default group `Education_Student_Quality`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/payment-document-settings` | List saved settings rows. |
| `GET` | `/api/payment-document-settings/{term}` | Get one term's saved settings or safe pending defaults. |
| `PUT` | `/api/payment-document-settings/{term}` | Upsert one term's settings. |

The `{term}` path supports values such as `2/2568`.

## Allowed Statuses

- `DRAFT_CONFIG`
- `ACTIVE_FOR_DRAFT_PREVIEW`
- `ARCHIVED`

`ACTIVE_FOR_DRAFT_PREVIEW` means active for draft/preparation context only. It is not payment approval, final authorization, official export readiness, or final payment truth.

## Validation

- `term` is required and must match the path term on save.
- `weekday_rate` and `weekend_rate` must be positive numbers on save.
- `currency` is fixed to `THB`.
- `payment_unit` is fixed to `PER_PERSON_SESSION`.
- `paper_distribution_responsible_group` is required.
- `paper_distribution_responsible_person` is optional.
- Unknown statuses are rejected.
- `effective_to` must not be earlier than `effective_from`.

## Permissions

| Role | Read | Write |
|---|---:|---:|
| `admin` | Yes | Yes |
| `esq_head` | Yes | Yes |
| `secretary` | Yes | Yes |
| `staff` | Yes | No |
| `teacher` | No | No |
| `print_shop` | No | No |
| `student` | No | No |

## Non-Authorization Rules

- Settings do not authorize payment.
- Settings do not create final payment truth.
- Settings do not enable official PDF, Excel, or export.
- Settings do not bypass payment-document review records.
- Settings do not mutate active simple invigilation rates.
- Settings do not persist manual paper-distribution draft rows as payable truth.
