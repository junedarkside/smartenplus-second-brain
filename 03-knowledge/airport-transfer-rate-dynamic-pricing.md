# Airport Transfer — Dynamic Pricing by Date

## Summary

Two distinct pricing paths for airport transfers. Zone path (`resolveZone`) is date-agnostic at display time; date filtering happens at cart-add. Route path (`fare-calendar`) is fully date-aware. Critical gap: displayed zone price ≠ cart price when date-specific ratecards exist.

## Context

Researched 2026-08-04 (session #287) to support AIRPORT-TRANSFER-ZONE slice 4b and AIRPORT-DETAIL-CONVERSION R1 implementation. No prior vault note covered this flow.

## Core Model — `Contract_RateCard`

`operators/models.py:521–545`

| Field | Type | Meaning |
|-------|------|---------|
| `contract` | FK | Linked contract/product |
| `ratecard` | FK → RateCard | Type: ADULT / CHILD / INFANT / VEHICLE |
| `selling_rate` | Decimal | Customer-facing price |
| `bar_rate` | Decimal | Internal cost |
| `rate_date` | DateField, nullable | NULL = default rate; date = override for that day |
| `is_active` | Boolean | Soft delete |

Unique constraint: `(contract, ratecard, rate_date)` — one rate per type per date.
History tracked via `HistoricalRecords`. Admin: `ContractRateCardAdmin` (`operators/admin.py:715`).

## Two Pricing Paths

### Path A — Zone Transfer (Airport Transfer page)

**Endpoint:** `GET /api/v1/resolve-zone/?airport={id}&lat={N}&lng={N}`

**Flow:**
```
User types address → PlacePicker.js → Google Places → lat/lng
  ↓ tripsApi.resolveZone (store/api/tripsApi.js:108-117)
BE: stations/geo.py ray-casting → highest-priority active TransferZone match
  ↓ ZoneContract M2M → linked contracts
BE: min(selling_rate) from active Contract_RateCard — NO rate_date filter
  ↓ returns {matched, zone, options:[{contract_id, contract_name, price}]}
FE: ZonePriceBox.js renders ZoneOptionCard per contract
  ↓
User picks date (SlideCalendar2, showFares=false — no per-day prices shown)
  ↓
User books → BookButton.updateRateCard(contract, bookingDate)
  ↓ helpers/checkoutRatecards.js — filterRatecardsForCheckout(ratecards, bookingDate)
     1. Prefer rate_date === bookingDate (date-specific rates)
     2. Fallback: rate_date === null (base rate for missing pax types)
  ↓ Cart item with date-filtered rate snapshot
```

**Response shape:**
```json
{
  "matched": true,
  "zone": { "id": 5, "name": "Downtown Area" },
  "options": [
    { "contract_id": 10, "contract_name": "Airport Express - Deluxe", "price": "500.00" }
  ]
}
```

### Path B — Route Fare Calendar (standard trips)

**Endpoint:** `GET /api/v1/fare-calendar/{from}/{to}/?date={YYYY-MM-DD}&people={N}&direction={direction}`

**View:** `FareCalendarViewSet` (`products/views.py:2133–2180`)

For each day in ±7-day window:
```python
Q(rate_date=d) | Q(rate_date__isnull=True)  # date-specific OR default
```
Returns min(selling_rate) per day. Null = unavailable/no contract.

**Response shape:**
```json
{
  "2026-08-01": 400.50,
  "2026-08-02": 425.00,
  "2026-08-03": null
}
```

SlideCalendar2 renders per-day prices in tabs, highlights cheapest in green.

## Critical Gap — Displayed Price ≠ Cart Price

`resolveZone` returns `min(selling_rate)` with **no date filter**. This is always the base/cheapest active ratecard, regardless of the user's selected date.

If an operator sets date-specific rates (e.g. high-season surcharge on `rate_date=2026-12-25`):
- ZonePriceBox shows: base rate (e.g. ฿450)
- Cart adds at: date-specific rate (e.g. ฿600)
- **User sees price change at checkout** → trust risk

Impact on **AIRPORT-DETAIL-CONVERSION R1** ("From THB X" hero anchor): the `Math.min` of ratecards will always reflect base rates, not date-adjusted — which is technically "from" semantics but may not match what user actually pays for their chosen date.

**Fix option (deferred):** Pass `date` param to `resolveZone` and apply `Q(rate_date=date) | Q(rate_date__isnull=True)` same as fare-calendar. Currently not built.

## Key File Map

### Frontend

| File | Role |
|------|------|
| `pages/airport-transfer/[slug].js` | Page — `showFares={false}` on calendar; passes `bookingDate` to ZonePriceBox |
| `components/airport-transfer/ZonePriceBox.js` | Zone pricing orchestrator; triggers resolveZone on address select |
| `components/airport-transfer/ZoneOptionCard.js` | Per-contract option + BookButton with `bookingDate` |
| `components/airport-transfer/PlacePicker.js` | Google Places autocomplete → lat/lng → resolveZone |
| `components/search/SlideCalendar2.js` | Date calendar; `showFares=false` hides fare tabs on airport page |
| `helpers/checkoutRatecards.js` | `filterRatecardsForCheckout()` — date-specific + null fallback merge |
| `store/api/tripsApi.js:96–117` | RTK Query: `getFareCalendar` + `resolveZone` endpoints |

### Backend

| File | Role |
|------|------|
| `operators/models.py:521–545` | `Contract_RateCard` — pricing table |
| `stations/models.py:265–351` | `TransferZone` + `ZoneContract` M2M |
| `stations/geo.py` | Ray-casting point-in-polygon (pure Python, no PostGIS) |
| `stations/views.py:638–700` | `ResolveZoneView` |
| `products/views.py:2133–2180` | `FareCalendarViewSet` (15-day date loop) |
| `products/views.py:1591–1605` | `_get_display_rate()` — shared date-filter helper |
| `carts/models.py:111–250` | `CartItemCheckoutInfo` — stores resolved_contract + coords + direction |
| `operators/admin.py:715–775` | `ContractRateCardAdmin` — rate management UI |

## Ratecard Object Shape (FE)

```js
{
  id: number,
  rate_card_type: 'ADULT' | 'CHILD' | 'INFANT' | 'VEHICLE',  // day trips
  ratecard: 'ADULT' | 'CHILD' | 'INFANT' | 'VEHICLE',         // transport alias
  selling_rate: number,
  bar_rate: number,
  rate_date: 'YYYY-MM-DD' | null,  // null = base rate
}
```

## Related

- [[adr-airport-transfer-zone-pricing]] — Slice 1–4a ADR (zone model + admin draw + FE picker + BE persistence)
- [[airport-transfer-detail-conversion-spec]] — R1 "From THB X" conversion spec (affected by date-agnostic gap)
- [[checkout-zone-transfer-card-spec]] — direction + ZonePriceBox stash, CHECKOUT-ZONE-CARD feature
- [[airport-transfer-width-audit]] — unresolved layout width gap on detail page
