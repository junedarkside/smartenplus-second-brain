# CartItems 500 Error — Production Bug Analysis

## Summary

`POST /carts/{id}/cartitems/` returns 500 HTML page (not JSON) when user books a day trip activity. Three distinct bugs found — one in error handling, two in payload construction.

## Context

Reported 2026-06-02. Production URL: `https://api.smartenplus.co.th/carts/c8b48780-7178-4950-acec-925595f9e2f8/cartitems/`

RTK Query error object:
```
status: 'PARSING_ERROR'
originalStatus: 500
data: Django HTML 500 page
error: "SyntaxError: Unexpected token '<'..."
```

Files involved:
- `components/activities/detail/DayTripBookingWidget.js`
- `components/activities/detail/DayTripDetailPage.js`
- `store/api/api-slice.js` (createCartItem endpoint)
- `store/api/dayTripsApi.js` (getContractBySlug)

## Root Causes (Ranked)

### Bug 1 — P1: Stale `initialContract` ratecard IDs sent with specific `traveling_date`

**How it breaks:**
1. Page loads via SSG → `initialContract` has only null-`rate_date` default ratecards
2. User selects a date → `selectedDate` flips from null to a date string
3. `shouldSkipInitialFetch` flips `true → false` → RTK Query fires new fetch
4. While fetch in-flight: `contract = fetchedContract ?? initialContract` = stale `initialContract`
5. `filteredRatecards` useMemo falls back to null-`rate_date` default ratecards (no date-specific ones exist yet)
6. User clicks "Add to Cart" → `convertToRatecard()` sends default ratecard IDs WITH a specific `traveling_date`
7. Backend checks: these ratecard IDs are not valid for this date → Django IntegrityError → HTML 500

**Code path:**
```
DayTripDetailPage.js:101 → contract = fetchedContract ?? initialContract (stale during loading)
DayTripBookingWidget.js:47-70 → filteredRatecards useMemo → falls back to null-date ratecards
DayTripBookingWidget.js:108-161 → convertToRatecard() sends wrong IDs
DayTripBookingWidget.js:269-278 → payload to API with bad contract_ratecard
```

**Fix:** Disable "Add to Cart" button while `isLoading` is true. Widget must not be interactive until date-specific contract arrives.

```js
// Add to disabled condition in DayTripBookingWidget.js button:
disabled={isLoading || totalParticipants === 0 || !selectedDate || ...}
```

Pass `isLoading` prop through: `DayTripDetailPage → DayTripMobileBookingBar/PremiumBookingPanel → DayTripBookingWidget`.

---

### Bug 2 — P1: `contract_ratecard: undefined` if ratecard uses `pk` not `id`

**How it breaks:**
`dayTripsApi.getContractBySlug` has no `transformResponse`. If backend returns ratecard objects with key `pk` instead of `id`, then:
- `ratecards[0].id` = `undefined`
- JSON.stringify drops `undefined` values
- Payload becomes `{ "quantity": 1 }` (missing `contract_ratecard` field)
- DRF serializer validation fails → Django 500

**Evidence:** `api-slice.js:110-120` — no `transformResponse`. `convertToRatecard()` lines 115, 129, 138, 149 — no `.id` guard anywhere.

**Fix:** Guard in `convertToRatecard()`:
```js
contract_ratecard: adultRate.id ?? adultRate.pk
```
Also add `transformResponse` in `dayTripsApi.js` to normalize `pk → id` on all ratecard objects.

---

### Bug 3 — P0: `PARSING_ERROR` not caught by 500 error handler (silent failure)

**How it breaks:**
RTK Query sets `error.status = 'PARSING_ERROR'` (string) when response is non-JSON. The catch block:
```js
} else if (error.status >= 500) {  // DayTripBookingWidget.js:338
```
`'PARSING_ERROR' >= 500` evaluates `false` in JavaScript (string vs number). The 500 branch **never fires**. Falls through to generic "Could not add item to cart" toast — hides the real error.

**Fix:**
```js
} else if (error.status === 'PARSING_ERROR' || error.originalStatus >= 500) {
  toast.error('Server error. Please try again later.', autoClose);
}
```

---

## Payload Shape (Actual)

```json
{
  "user": "<session.id | null>",
  "contract_id": "<contract.id>",
  "traveling_date": "YYYY-MM-DD",
  "contract_ratecard": [
    { "contract_ratecard": "<ratecard.id>", "quantity": 1 }
  ],
  "adult": 2,
  "child": 0,
  "infant": 0,
  "product_type": "JOIN"
}
```

## Fix Plan

| Priority | File | Line | Change |
|---|---|---|---|
| P0 | `DayTripBookingWidget.js` | 338 | Fix PARSING_ERROR catch: `error.status === 'PARSING_ERROR' \|\| error.originalStatus >= 500` |
| P1 | `DayTripBookingWidget.js` | button disabled | Add `isLoading` to disabled condition |
| P1 | `DayTripDetailPage.js` | 235/247 | Pass `isLoading` prop to both booking components |
| P1 | `DayTripBookingWidget.js` | 115, 129, 138, 149 | Add `.id ?? .pk` fallback in `convertToRatecard()` |
| P2 | `store/api/dayTripsApi.js` | getContractBySlug | Add `transformResponse` to normalize ratecard field names |

## Tradeoffs

- **P0 error handler fix** — zero risk, pure improvement. Do immediately.
- **P1 isLoading disable** — prevents booking with stale data at cost of brief UI lockout (spinner). Correct tradeoff.
- **P2 transformResponse** — requires confirming whether backend actually returns `pk` vs `id`. Check backend serializer before adding. Could be defensive-only.

## Related

- [[cart]] — CartItem model, cartitems endpoint
- [[DayTripBookingWidget]] — booking flow
- [[nextjs-isr-ratecard-empty-array-guard]] — similar stale data guard pattern
- [[payment-checkout-architecture-audit]] — error handling patterns
