---
name: slidecalendar2-farecalendar-prop-pattern
description: SlideCalendar2 accepts optional fareCalendar (date-keyed rate map) + fareCalendarLoading (boolean) props. Caller MUST fetch via useGetFareCalendarQuery and pass both. Only TripSearchFilters.js wires them correctly; TripDetailSchedule.js:46 doesn't (out of scope for prior fix).
type: knowledge-atom
date: 2026-06-15
parent: trip-page-full-audit-2026-06-15
---

# SlideCalendar2 fareCalendar Prop Pattern

## Summary
`SlideCalendar2` (the 7-day date strip with per-day fare labels on `/trips/...` and detail pages) accepts two optional props for ISO-aware rate display: `fareCalendar` (`{ 'YYYY-MM-DD': number }` of raw THB rates) and `fareCalendarLoading` (boolean). The component reads these to highlight the cheapest day in amber + render `useFormatPrice(dayFare)` under each date. If neither is passed, the price row falls through to an invisible `–` placeholder and no cheapest highlight fires. **The component does NOT fetch fare data itself** — every caller is responsible for wiring `useGetFareCalendarQuery`.

## Context
This session fixed `SlideCalendar2.js:977` to be currency-aware (see [[currency-context-price-rendering-rule]]). While doing so, a secondary gap was confirmed by the prior audit: only **1 of 5 callers** wires the `fareCalendar` + `fareCalendarLoading` props. The detail-page caller (`TripDetailSchedule.js`) does NOT, leaving the price row invisible on `/trips/detail/[...slug]`. This is a pre-existing bug, not introduced by the currency fix. **Out of scope for the currency fix** — different route, different render chain, requires `useGetFareCalendarQuery` wiring in `TripDetailSchedule.js` to resolve.

## Prop Contract

```jsx
// components/search/SlideCalendar2.js:605
const SlideCalendar2 = ({
  data,                     // (required) { slug, date, returnDate, people, ... } — query state
  updateUrl = true,         // (optional) push date changes to URL
  updateRedux = true,       // (optional) sync to Redux calendar slice
  className = 'mx-2 md:mx-3 xl:mx-0',  // Tailwind outer container
  fareCalendar,             // (optional) { 'YYYY-MM-DD': rate_thb_int } — daily rates
  fareCalendarLoading,      // (optional) boolean — shows Skeleton while true
}) => { ... }
```

**Both props optional.** When `fareCalendar` is undefined, the price row renders an invisible `–` (line 982) — visual placeholder for layout height consistency, zero-width on the user. The day-cell click still works; only the price + cheapest-day highlight are missing.

**Why invisible `–` not blank:** prevents layout shift when `fareCalendar` arrives. Tab cells stay same height whether fares are loaded or not.

### Cheapest-day highlight logic (line 941-947)

```js
const visibleFares = Array.from({ length: CALENDAR_DAYS_COUNT }, (_, i) => {
  const key = format(addDays(firstDayInView, i), 'yyyy-MM-dd');
  return fareCalendar?.[key] ? Number(fareCalendar[key]) : null;
}).filter(Boolean);
const minFare = visibleFares.length > 1 ? Math.min(...visibleFares) : null;
const allSame = minFare !== null && visibleFares.every(f => f === minFare);
// ...
const isCheapest = !allSame && dayFare !== null && dayFare === minFare;
const priceColor = isSelected ? '#3b5998' : isCheapest ? '#059669' : '#6b7280';
```

- Cheapest day colored **emerald `#059669`** (not blue, not gray)
- All-same-prices case (`allSame === true`) suppresses the highlight — no "cheapest" badge when every day costs the same
- Single-fare case (`visibleFares.length <= 1`) suppresses the highlight — too few samples to call it a deal

## Caller Pattern (canonical)

`components/trips/TripSearchFilters.js:80-105` is the only fully-wired caller:

```jsx
import { useGetFareCalendarQuery } from '../../store/api/tripsApi';
import { skipToken } from '@reduxjs/toolkit/query';

const fareCalendarArgs = useMemo(() => {
  if (slideCalendarData?.slug?.length === 2 && slideCalendarData.date) {
    return { from: slideCalendarData.slug[0], to: slideCalendarData.slug[1], date: slideCalendarData.date, people: slideCalendarData.people, direction: slideCalendarData.direction };
  }
  return skipToken;  // RTK Query: don't fire until all args present
}, [slideCalendarData?.slug?.[0], slideCalendarData?.slug?.[1], slideCalendarData?.date, slideCalendarData?.people, slideCalendarData?.direction]);

const { data: fareCalendar, isFetching: fareCalendarFetching } = useGetFareCalendarQuery(fareCalendarArgs);

return (
  // ...
  <DynamicSlideCalendar2
    data={slideCalendarData}
    fareCalendar={fareCalendar}                 // RTK Query result
    fareCalendarLoading={fareCalendarFetching}  // RTK Query isFetching
  />
);
```

**`skipToken` is the key.** RTK Query pattern: don't fire the request until ALL required args are populated. Otherwise the query fires with `undefined` slug → 404 noise + wasted bandwidth on every keystroke during search.

## Caller Inventory (grep 2026-06-15)

| Caller file | Wires `fareCalendar`? | Notes |
|---|---|---|
| `components/trips/TripSearchFilters.js:99-105` | ✅ yes | Only correct caller. `useGetFareCalendarQuery` + `skipToken` pattern. Used on `/trips/[...slug]` (filter list page). |
| `components/trips/TripDetailSchedule.js:46-49` | ❌ no | Renders `<DynamicSlideCalendar2 data={query} updateUrl={false} />` — no `fareCalendar`, no `fareCalendarLoading`. **Falls through to invisible `–` on every cell.** Used on `/trips/detail/[...slug]` (separate route). **Pre-existing bug — not in scope for currency fix.** |
| `pages/destinations/[slug].js:385` | ❌ no | Passes `data` only. Calendar visible but no fare row. |
| `pages/airport-transfer/[slug].js:261` | ❌ no | Passes `data` only. Calendar visible but no fare row. |
| `pages/trips/detail/[...slug].js:346` | ❌ no | Passes `data` only. Calendar visible but no fare row. (Distinct from `TripDetailSchedule.js` — both render `SlideCalendar2` on detail-ish routes, neither wires fare data.) |

5 callers total. **1 wired correctly. 4 missing the fare props.** None crash — fall through is graceful. The detail-page `SlideCalendar2` was *always* going to be a no-op price-wise; the prior assumption (visible fare row on detail page) was wrong.

## Decision

### Use `useFormatPrice` for the price label (this session)

See [[currency-context-price-rendering-rule]] for the full pattern. Key line:

```jsx
import { useFormatPrice } from '../../hooks/useFormatPrice';
const formatPrice = useFormatPrice();
// at line 977:
{dayFare ? (
  <div className="text-[13px] font-semibold mt-0.5 whitespace-nowrap" style={{ color: priceColor }}>
    {formatPrice(dayFare)}
  </div>
) : fareCalendarLoading ? (
  <Skeleton variant="text" width={28} sx={{ fontSize: '13px', mx: 'auto', mt: '2px' }} />
) : (
  <div className="text-[13px] invisible mt-0.5">–</div>
)}
```

Add `formatPrice` to the `renderCalendarDays` `useCallback` deps array (line 995).

### Do NOT add fareCalendar wiring to `SlideCalendar2` itself

Tempting to make `SlideCalendar2` self-fetch (`useGetFareCalendarQuery(slug)` inside the component). **Rejected** because:
- Component would need its own provider awareness (CurrencySelector awareness via `useCurrency`) — coupling increases
- 5 callers with different `data` shapes — `data` already contains the query state, caller is the right place to derive fetch args
- 1 of 5 callers already wires it correctly — pattern works; expand the pattern, don't refactor the contract
- Atomic principle: components render, callers fetch. Reuse `useGetFareCalendarQuery` at the call site.

### For `TripDetailSchedule.js` follow-up (out of scope)

When the detail page is revisited, the fix is a 5-line addition: copy the `fareCalendarArgs` `useMemo` + `useGetFareCalendarQuery` block from `TripSearchFilters.js:80-99` into `TripDetailSchedule.js`, then pass `fareCalendar={fareCalendar}` and `fareCalendarLoading={fareCalendarFetching}` to `DynamicSlideCalendar2`. **Do this as a separate PR** — different render chain, different page, different review surface. Don't bundle with the currency fix.

## Tradeoffs

- **Pro:** Self-contained fix. 1 import + 1 hook call + 1 render swap + 1 dep array add. 4 lines net.
- **Pro:** SSR-safe — `useFormatPrice` falls back to `THB` when `currentRate` is null (see [[currency-context-price-rendering-rule]]).
- **Pro:** `fareCalendarLoading` Skeleton branch unchanged — loading UX preserved.
- **Con:** `whitespace-nowrap` added to the cell div (line 978) because `"THB 1,234"` is longer than `"฿1,234"`. Horizontal scroll on mobile absorbs overflow.
- **Con:** `formatPrice` called twice per render in the `dayFare ?` branch. Trivial cost.

## Real-World Triggers

When auditing or modifying `SlideCalendar2`:
- **Always grep for callers** before changing the prop contract — 5 files render it.
- **`fareCalendar` and `fareCalendarLoading` travel together** — if you add one, the other must also be passable. Don't make one required.
- **RTK Query `skipToken` is mandatory** when query args depend on user input. Without it, requests fire on every render until args are populated.

When auditing any page that uses `SlideCalendar2`:
- Check whether fare row should be visible. If yes, ensure caller wires `fareCalendar` + `fareCalendarLoading`. If no (e.g. detail page where prices are shown elsewhere), leave invisible.

## Related
- [[currency-context-price-rendering-rule]] — companion atom; the currency fix
- [[trip-page-full-audit-2026-06-15]] — parent audit context
- [[trip-search-below-fold-redesign-2026-06-15]] — sibling work (`TripSearchFilters.js` is on the same route as `RouteFAQ`/`RouteSummary`/`TripSummary`)
- [[isr-csr-overlay-stale-fields]] — pattern for ISR + CSR overlay price display (related: `fareCalendar` is RTK-gated, so on cold load the cells show Skeleton until the query resolves)
