# Contract Trip Null — Non-Transport Pattern

## Summary
Non-transport contracts always have `trip=None`. Frontend code reading `contract.trip.*` without null guard crashes for DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, etc.

## Context
`operators/models.py`: `trip = ForeignKey(Trip, ..., null=True, blank=True)`. `sanitize_category_fields()` sets trip=None for non-transport categories. Permanent by design, not orphaned data.

## Problem
Frontend assumes `contract.trip` always exists. `departure_time`, `arrival_time`, `route` are transport-only — meaningless for experience contracts.

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
- `.some()` / `.filter()` / `.map()` over cart items accessing `contract.trip.*`
- Computed values at render root (before guards run) — crashes entire page
- `departure_time`, `arrival_time`, `route`, `stop_sale_dates` transport-only — guard all

## Existing Correct Usage
`sortCartItems.js:72`, `EnhancedTripCard.js:93`, `TripsConfirmation.js:18` — all use `contract?.trip?.departure_time`

## Multi-File Fix Evidence

`checkout-confirmation-payment-crash` root-caused 5 separate frontend crashes (Confirmation.js, TripsConfirmation.js, OrderDetail.js, BookingInfoDialog, ServiceDetail) all from `contract.trip.X` without optional chaining. Single null-guard pattern in `helpers/contractDisplay.js` would have prevented all 5.

## Related
- [[cartitems-500-error-analysis]] — backend null guard (`carts/utils.py:591`)
- [[checkout-confirmation-payment-crash]] — multi-file evidence
- [[build-experience-faq-items-pure-function]] — same `contract?.trip` guard pattern in FAQ builder