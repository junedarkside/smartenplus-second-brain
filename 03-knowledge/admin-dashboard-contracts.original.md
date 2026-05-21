# Admin Dashboard — Contracts

Contract category management, form flow, and payload transformation.

## Category Registry

**Source of truth:** `CATEGORY_CAPABILITIES` in `components/contracts/constants.js`.

Never hardcode category strings — use helpers:

| Helper | Controls |
|--------|---------|
| `isTransportationCategory()` | Trip field, Route Info, isTransport flag |
| `hasBaggagePolicy()` | Baggage Allowance section |
| `hasVehicleSpec()` | TransportComposit |
| `hasRouteInfo()` | Route Info rich text |
| `hasItineraryDuration()` | Duration Days |

### Visibility by Category

| Section | TRANS | TRANSFER | DAY_TOUR | MULTI | SPA | EVENT | ATTRACT | FOOD | ACCOM | OTHER |
|---------|:-----:|:--------:|:--------:|:-----:|:---:|:-----:|:-------:|:----:|:-----:|:-----:|
| Trip | Y | Y | - | - | - | - | - | - | - | - |
| Primary Location | - | - | Y | Y | Y | Y | Y | Y | Y | Y |
| Route Info | Y | Y | - | - | - | - | - | - | - | - |
| TransportComposit | Y | Y | Y | Y | - | - | - | - | - | - |
| Booking Config | - | - | Y | Y | Y | Y | Y | Y | Y | Y |
| Duration Days | - | - | Y | Y | - | - | - | - | - | - |
| Experience Content | - | - | Y | Y | Y | Y | Y | Y | Y | Y |
| Baggage Allowance | Y | Y | Y | Y | - | - | - | - | - | - |

## Payload Rules

- `tour_duration_days` — DAY_TOUR + MULTI_DAY_TOUR only
- `transportComposit` — vehicleSpec categories only
- `routeInfo` — transport categories only
- `baggage` — baggage categories (nullable)
- `toNullableNumber()` — always for Django IntegerFields (empty string = 500)
- `imageSelection` — passes through transform as-is. Backend reads directly. Do NOT rename to `image_gallery`.
- **Sentinel ID rule:** Frontend sends `id: -1` for new unsaved rows in array fields (`transportComposit`, ratecards, etc.). Backend must branch on `id > 0` before any `get_or_create()` — never pass sentinel as PK. New rows → `create()`. Existing rows → `get_or_create(id=..., ...)`. See [[operators]] Contract_TranspotComposit fix.

## Image Flow

```
Formik imageSelection [{id, image}]
  → ImageSelection (container)
    → ProductImages (selected grid — drag reorder, delete, preview)
    → OperatorImages (gallery — add to selection, preview)
  → transformContractFormValues: imageSelection passes through unchanged
  → Backend update: reads imageSelection from request data
    → creates/updates ImageGallery records per {id, image, order}
  → Response: image_gallery (read-only, from imagegallery_set)
  → useContractFormData: data?.image_gallery → Formik imageSelection
```

## Form Components

- `ContractFormFields.js` — Master form layout
- `BookingConfig.js` — Min/Max Participants, Difficulty, Duration Days
- `DayTripDetails.js` — Experience Content: rich text + meeting point
- `TimeInputGroup.js` — Advance Hour + dynamic duration label
- `TransportComposit.js` — Vehicle type + seat rows
- `DateInputGroup.js` — Start/end dates
- `SettingsInputGroup.js` — Contract type, active toggle

## Related

- [[operators]] — Operator model, TimeSlot, ContractAddon
- [[admin-dashboard-image-pipeline]] — Image error reset, dedup helpers