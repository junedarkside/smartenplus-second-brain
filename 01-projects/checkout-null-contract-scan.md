# Checkout Null Contract/Trip Scan — 2026-06-03

## Summary
Full scan of checkout flow for unguarded `contract` / `contract.trip` access. Context: non-transport contracts always have `trip=null` by design. Orphaned items have `contract=null`. Three bugs already fixed (sessions #34–35). This scan identifies remaining exposure.

## Background

| Contract type | `contract` | `contract.trip` | `contract.info_fields` |
|--------------|-----------|----------------|----------------------|
| TRANSPORTATION / TRANSFER | exists | exists | `[]` or populated |
| DAY_TOUR / SPA / EVENT | exists | **null** (by design) | `[]` |
| Orphaned (deleted) | **null** | — | — |

Step-0 validation blocks orphaned items but there's a race window between validation and component mount.

## Already Fixed

| Commit | File | Lines | Bug |
|--------|------|-------|-----|
| `43b7ece` | `pages/checkout/index.js` | 608–618 | `booking.contract.trip.departure_time` + `item.contract.stop_sale_dates` at render root |
| `5873403` | `components/forms/checkout/Passengers.js` | 259, 501 | `item.contract.info_fields.forEach` in lazy useState + useMemo |

## Scan Results — Remaining Bugs

### REAL BUG — Passengers.js:1097 (CRITICAL)

```js
<>{`Trip ${displayIndex}:${tripWrapper.trip.contract.trip.route_route} (${formatDate(tripWrapper.trip.traveling_date)})`}</>
```

**Chain:** `tripWrapper.trip` → `.contract` → `.trip` → `.route_route` — zero guards.

**Crash when:** Any non-transport item (DAY_TOUR/SPA/EVENT) reaches Passengers step — `contract.trip = null` → `null.route_route` → TypeError. Crashes Passengers render entirely.

**Fix:**
```js
<>{`Trip ${displayIndex}: ${tripWrapper.trip?.contract?.trip?.route_route || tripWrapper.trip?.contract?.name || 'Trip Details'} (${formatDate(tripWrapper.trip?.traveling_date)})`}</>
```

**Priority: P0 — crashes Passengers step for all non-transport items.**

---

### FALSE POSITIVES (agents flagged, but actually safe)

| File | Lines | Why Safe |
|------|-------|----------|
| `EnhancedTripCard.js:297-300` | `item.contract.trip.departure_time` inside `{isTransportation && item.contract?.trip && ...}` | JSX condition short-circuits — if `contract=null`, `contract?.trip` = `undefined` = falsy, block never renders |
| `ServiceCategoryDetail.js:154-160` | Same pattern — inside `item.contract?.trip &&` JSX guard | Same: guard prevents render when null |
| `TripsConfirmation.js:19` | `item.contract.trip.departure_time.substring(0,5)` after `item.contract?.trip?.departure_time ?` ternary guard | Ternary guard already confirmed non-null before access |
| `index.js:611` | `booking.contract.advance_hr` after `if (!booking.contract?.trip) return false` | If `contract=null`, `contract?.trip` = `undefined` = falsy → returns false before line 611 |
| `sortCartItems.js:73` | `item.contract.trip.departure_time` | Line 72 already checks `item.contract?.trip?.departure_time` as condition — safe |

---

### LOW — bookingContext.js:87

```js
route = booking.contract.trip.route.route_route;
```

Inside a guard block per agent report (`booking.contract?.trip?.route?.route_route` as condition). Same pattern as above — likely safe, but needs verification. Used in recommendations display, not checkout critical path.

---

## Debate Summary

**Agent 1 (index.js scan):** Flagged line 611 `booking.contract.advance_hr` as unguarded. **OVERTURNED** — the guard `!booking.contract?.trip` returns false for null contract (`null?.trip = undefined = falsy`), so line 611 is never reached.

**Agent 2 (form components):** Flagged EnhancedTripCard + ServiceCategoryDetail lines inside JSX `&&` guards. **OVERTURNED** — JSX short-circuit is a valid guard. Also flagged Passengers.js:1097 correctly — **CONFIRMED REAL BUG**.

**Agent 3 (helpers/hooks):** Flagged sortCartItems.js:73 and bookingContext.js:87. sortCartItems **OVERTURNED** — guarded by enclosing condition. bookingContext LOW priority, not in checkout critical path.

**Verdict:** 1 real actionable bug remaining (Passengers.js:1097). All other flagged sites are safe.

---

## Status: RESOLVED 2026-06-03 — `05fc0aa` shipped to production

## Fix Plan

**File:** `components/forms/checkout/Passengers.js:1097`

```js
// BEFORE
<>{`Trip ${displayIndex}:${tripWrapper.trip.contract.trip.route_route} (${formatDate(tripWrapper.trip.traveling_date)})`}</>

// AFTER
<>{`Trip ${displayIndex}: ${tripWrapper.trip?.contract?.trip?.route_route || tripWrapper.trip?.contract?.name || 'Trip Details'} (${formatDate(tripWrapper.trip?.traveling_date)})`}</>
```

Fallback chain: `route_route` → contract `name` → generic "Trip Details". Non-transport items show contract name (e.g., "Chiang Mai Day Tour") instead of a route.

## Related
[[contract-trip-null-non-transport-pattern]]
[[cartitems-500-error-analysis]]
