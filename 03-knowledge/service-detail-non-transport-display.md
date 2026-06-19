# Service Detail — Non-Transport Contract Display

## Summary
Booking detail page (`ServiceTabbedInfo.js` + `ServiceDetail.js`) reads non-transport contract fields via three new ContractSerializer outputs. Field-name contract and `customFormatDuration` safety are the load-bearing details.

## Why It Matters
Reuse for any booking/order/email rendering of non-transport contracts. Field name `cancellation_window` was wrong — actual DB field is `refund_hours`. `duration` is a `DurationField` returning `"8:00:00"`; `customFormatDuration` splits on `:` and handles it.

## Detail
Three field contracts the frontend reads:

1. **Description (RichText)**
   ```js
   contract?.general_information?.description
   ```
   `GeneralInformation.description` is `RichTextField` (HTML). Backend exposes via `_GeneralInformationSerializer` (FK from Contract, `read_only=True`).

2. **Refund policy (DurationField)**
   ```js
   cancellationPolicy.refund_hours
   ```
   `CancellationPolicy` model: `free_refund` (bool), `refund_hours` (DurationField → "8:00:00"), `charge_type`, `charge_amount`. **No `cancellation_window` field** — older frontend code referenced this and crashed with `undefined`.

3. **Duration display**
   ```js
   customFormatDuration(contract.duration)
   ```
   Safe with `"8:00:00"` format produced by Django `DurationField`. Format helper splits on `:`.

## Constraints / Gotchas
- `CancellationPolicy` is in `policies.models` — must add to `operators/serializers.py` import line; not in default import group.
- `image` field on contract uses reverse accessor `imagegallery_set` via `source=` param, not direct FK.
- `requirements` does NOT exist on `Contract` model — do not add.
- `meeting_point_type` + `meeting_point_details` are new flat fields; both `null=True`.

## Related
- [[contract-serializer-non-transport-fields]] — backend serializer fix
- [[contract-trip-null-non-transport-pattern]] — companion null-guard pattern
- [[copy-cartitem-trip-none-guard]] — backend write-path guard
- [[checkout-confirmation-payment-crash]] — full flow audit source
