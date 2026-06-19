---
name: currency-context-price-rendering-rule
description: User-facing prices go through useFormatPrice() hook (CurrencyContext-driven, SSR-safe, JPY/KRW aware). Schema.org JSON-LD Offer.price + priceCurrency stays in merchant base currency (THB) regardless of viewer preference.
type: knowledge-atom
date: 2026-06-15
parent: trip-page-full-audit
---

# Currency Context Price Rendering Rule

## Summary
Two distinct surfaces, two distinct rules. **User-facing labels** render through `useFormatPrice()` from `hooks/useFormatPrice.js` — reads `CurrencyContext` and converts raw THB integer to the viewer's selected currency (THB/USD/EUR/GBP/JPY/...). **Schema.org JSON-LD** keeps raw THB integer in `Offer.price` with `priceCurrency: 'THB'` — schema describes the merchant offer, not the viewer display. Mixing the two breaks either UX consistency or Google Rich Results.

## Context
Two outlier components on `/trips/hatyai/koh-lipe` (this session): `SlideCalendar2.js:977` hardcoded `฿{dayFare.toLocaleString()}` and `TripSummary.js:35` hardcoded `from THB {minPrice.toLocaleString()}`. Both bypassed `CurrencyContext`. Calendar visible when user selects USD/EUR/JPY from `CurrencySelector` while every other trip page price (`TripItem`, `TripDetailBooking`, `FilterTrip` slider, `RouteFAQ`) updated correctly. Calendar and "Departures by Operator" section were the only outliers. Fix: `useFormatPrice()` in both — same pattern as the 5 already-correct components.

## Problem

### Symptom
User opens `/trips/hatyai/koh-lipe`, switches `CurrencySelector` to `USD` → trip cards show `USD 24`, booking bar shows `USD 24`, FAQ mentions `USD 24`, but calendar cells and Departures-by-Operator rows still show `฿800` (or `from THB 800`). Visual mismatch on the same page.

### Why both surfaces exist
- **User-facing labels** must reflect viewer's display preference — the viewer wants to see prices in their currency.
- **Schema.org `Offer`** describes the *offer* to search engines — Google's Rich Results expect `price` and `priceCurrency` to be a consistent monetary amount. The product IS offered at 800 THB in the ratecard (the source of truth). The viewer-display-currency is a UI concern, not a product-attribute concern.

## Decision

### Rule 1 — User-facing price = `useFormatPrice(priceInThb)`

```jsx
// components/search/SlideCalendar2.js:977
import { useFormatPrice } from '../../hooks/useFormatPrice';

const formatPrice = useFormatPrice();
// ...
{dayFare ? (
  <div className="text-[13px] font-semibold mt-0.5 whitespace-nowrap" style={{ color: priceColor }}>
    {formatPrice(dayFare)}
  </div>
) : fareCalendarLoading ? (
  <Skeleton ... />
) : (
  <div className="text-[13px] invisible mt-0.5">–</div>
)}
```

`useFormatPrice()` (hook at `hooks/useFormatPrice.js:9`) returns a memoized `(price) => string` that:
- Returns `null` for `price <= 0` or `null/undefined` (safe fallback for guards)
- Converts: `formatCurrency(price / currentRate.rate, currentRate.currency)` when `currentRate` loaded
- Falls back to `formatCurrency(price, 'THB')` when `currentRate` still null (initial SSR / pre-forex-fetch)

### Rule 2 — JSON-LD `Offer` = raw THB integer + `'THB'` currency

```jsx
// components/trips/TripSummary.js:91 — UNCHANGED
offers: minPrice != null ? {
  '@type': 'Offer',
  price: minPrice,                // raw THB integer from ratecard
  priceCurrency: 'THB',           // merchant base currency
  availability: 'https://schema.org/InStock',
} : undefined,
```

**Do NOT** convert `minPrice` here. Schema integrity > visual consistency on schema side. Google indexes the merchant's transactional price; viewer-display-currency is not crawled.

### Guard: trust `useFormatPrice` return value as the source of truth

```jsx
// Before (TripSummary old):
{minPrice != null && (
  <span className="text-xs font-semibold text-blue-700 whitespace-nowrap">
    from THB {minPrice.toLocaleString()}
  </span>
)}

// After:
{formatPrice(minPrice) && (
  <span className="text-xs font-semibold text-blue-700 whitespace-nowrap">
    from {formatPrice(minPrice)}
  </span>
)}
```

`useFormatPrice` returns `null` for `price <= 0` (hook line 13) — collapses two checks (`minPrice != null` + truthy) into one. Same pattern as `RouteFAQ.js:24` and `TripDetailBooking.js:97`.

## Details

### Why `useFormatPrice` is SSR-safe

- `CurrencyContext` defaults to `currentRate: null` (`components/contexts/CurrencyContext.js:7`)
- `useFormatPrice` falls back to `formatCurrency(price, 'THB')` when `currentRate` is null (hook line 17)
- First SSR paint: viewer sees "from THB 800" (or "THB 800" for calendar) regardless of `selectedCurrency`
- Post-hydration: `CurrencyProvider.useEffect` (line 12-31) fires forex fetch, updates `currentRate`, all price renderers re-render with converted values
- Identical hydration pattern to `TripItem`, `FilterTrip`, `RouteFAQ` — all on the same page, all `useFormatPrice`-driven
- No `useEffect` needed in the consumer; the context handles the re-render

### Why JPY/KRW work without extra code

`formatCurrency` (`helpers/formatCurrency.js:6`) detects `JPY`/`KRW` and sets `minimumFractionDigits: 0, maximumFractionDigits: 0` on `Intl.NumberFormat`. So `formatCurrency(800 / 3.2, 'JPY')` → `"JPY 250"` (no decimals), matching how Japanese yen is conventionally written. The hook inherits this — no consumer-side change needed when adding JPY/KRW to the CurrencySelector.

### Why `whitespace-nowrap` is required on the calendar cell

`formatPrice(800)` returns `"THB 800"` (8 chars) or `"USD 25"` (6 chars) instead of the old `"฿800"` (4 chars). Calendar cell `minWidth: 60` (mobile) — `"THB 1,234"` at 13px font ≈ 70-80px → would wrap. `whitespace-nowrap` keeps it on one line; horizontal scrollable tabs absorb overflow.

## Tradeoffs

- **Pro:** 1 import + 1 hook call + 1 render swap. Reuses existing hook. No new utility, no new prop, no new context field.
- **Pro:** SSR-safe without `useEffect` — pattern proven across 5 existing components.
- **Pro:** JPY/KRW formatting works automatically.
- **Con:** Two-call pattern (`formatPrice(minPrice) && ... {formatPrice(minPrice)} ...`) calls the hook twice per render. Cheap (pure function of `currentRate`), but a `useMemo` would over-engineer this. Acceptable.
- **Con:** JSON-LD `priceCurrency: 'THB'` may look wrong to engineers reviewing schema output for a USD viewer. Tradeoff intentional — schema integrity rule.

## Real-World Triggers (audit checklist)

`grep` for any of these in `components/` — each is a hardcoded-currency offender:
1. `toLocaleString()` near a price variable — likely raw `฿{n.toLocaleString()}` pattern
2. Literal `"THB"` or `"฿"` in JSX (not in comments, not in JSON-LD)
3. `Intl.NumberFormat` without `useFormatPrice` indirection
4. `parseFloat(selling_rate).toLocaleString()` — common `ExteaContractSerializer` consumer pattern

Canonical consumers (all correct):
- `components/trips/TripItem.js:105, 110` — trip card price
- `components/trips/TripItemAccordionContent.js:94, 107` — accordion
- `components/trips/TripDetailBooking.js:97` — booking bar
- `components/trips/FilterTrip.js:146-163, 378` — price slider
- `components/trips/RouteFAQ.js:24` — FAQ

Newly-fixed (this session):
- `components/search/SlideCalendar2.js:977` — calendar price
- `components/trips/TripSummary.js:35` — Departures by Operator row

## Out of Scope (deferred)

- `formatCurrency` hardcodes `'th-TH'` locale (`helpers/formatCurrency.js:16`) — output uses Thai digit grouping + symbol placement for all currencies. Should derive locale from currency code (e.g. `en-US` for USD), but unchanged here to keep the 2-file diff minimal.
- `getMainPrice` helper — has 5-arg signature, used by 1 caller, not part of the surface area.
- `TripSummary.js:35` only fixes the visible "from THB" label. The `<Head>` JSON-LD `priceCurrency: 'THB'` is intentional (Rule 2).

## Related
- [[trip-page-full-audit]] — parent audit; C2-C4 crash fixes also from this session
- [[slidecalendar2-farecalendar-prop-pattern]] — companion atom for the calendar's data wiring
- [[trip-search-below-fold-redesign-2026-06-15]] — sibling work that shipped RouteFAQ/RouteSummary; both consume `useFormatPrice`
- [[structured-data-schema-patterns]] — JSON-LD integrity rules (companion to Rule 2)
- [[currency-context-infinite-fetch]] — historical bug in `CurrencyContext` itself (race + ref stability), separate issue
