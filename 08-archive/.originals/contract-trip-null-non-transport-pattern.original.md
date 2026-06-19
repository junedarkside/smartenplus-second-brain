# Contract Trip Null — Non-Transport Pattern

## Summary
Non-transport contracts always have `trip=None`. Any frontend code reading `contract.trip.*` without a null guard crashes for DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, etc.

## Context
`operators/models.py`: `trip = ForeignKey(Trip, ..., null=True, blank=True)`. When `sanitize_category_fields()` copies a contract in non-transport categories, trip is explicitly set to `None`. This is permanent by design, not orphaned data.

## Problem
Frontend assumes `contract.trip` always exists. `departure_time`, `arrival_time`, `route` are transport-only fields — meaningless for experience contracts.

## Pattern

**Wrong:**
```js
const departureTime = booking.contract.trip.departure_time || '06:00:00';
```

**Correct:**
```js
if (!booking.contract?.trip) return false; // skip non-transport items
const departureTime = booking.contract.trip.departure_time || '06:00:00';
```

For array checks:
```js
item.contract?.trip && item.contract?.stop_sale_dates?.some(...)
```

## Where This Bites
- Any `.some()` / `.filter()` / `.map()` over cart items that accesses `contract.trip.*`
- Computed values at component render root (before conditional guards run) — worst case: crashes entire page
- `departure_time`, `arrival_time`, `route`, `stop_sale_dates` are transport-only — guard all of them

## Existing Correct Usage
`sortCartItems.js:72`, `EnhancedTripCard.js:93`, `TripsConfirmation.js:18` — all use `contract?.trip?.departure_time`

## Related
[[cartitems-500-error-analysis]] — backend null guard (`carts/utils.py:591`)
