# Trip Page Full Audit — /trips/hatyai/koh-lipe — 2026-06-15

## Summary
3-agent full-page functional audit. **IMPLEMENTED** (`fix/trip-page-audit-2026-06-15`, build clean). C2-C4 crash bugs fixed, S1 XSS fixed (DOMPurify inline), D1-D3 dead files deleted, M1 badge defaults fixed, M2 filter guards added, M8 key fixed, C1 rewritten for clarity. Build passes (pre-existing activities errors unrelated). Pending: PR → develop.

## Context
Full component + function audit of `/trips/[from]/[to]` route. 50+ files across orchestration, filter modal, trip results, and below-fold. Follows [[trip-filter-modal-audit-2026-06-15]] (filter-only scope). Agents covered all 3 layers in parallel.

---

## CRITICAL — Fix Immediately

### ~~C1~~: Filter dialog handler — MINOR (demoted)
- `FilterTripsPage.js:169`
- `&&` pattern IS functional — `setFilterDialogOpen(true)` executes. Not a real bug.
- Rewrite for clarity only (lint `no-unused-expressions`):
  ```js
  useCallback(() => { if (tripsFilterSet?.operator_list?.length) setFilterDialogOpen(true); }, [tripsFilterSet])
  ```

### C2: Crash — ratecard undefined on flatMap
- `FilteredTripList.js:97`
- `Math.max(...contract.ratecard.map(i => i.selling_rate))` — no guard on `ratecard`
- If any contract has `ratecard: null` or `ratecard: []`, crashes with TypeError or returns `-Infinity`
- Fix:
  ```js
  rate: contract.ratecard?.length ? Math.max(...contract.ratecard.map(i => i.selling_rate)) : 0,
  ```

### C3: Crash — transport composit length on undefined
- `FilteredTripList.js:53`
- `contractTransportComposits.length` — `.map()` result from optional chain can be undefined
- After BUG-1 fix (L51), `expectedTransportComposits` can still be undefined if both fields missing
- Fix:
  ```js
  const exactMatch = (contractTransportComposits?.length ?? 0) === (expectedTransportComposits?.length ?? 0) &&
    expectedTransportComposits?.every(expected => contractTransportComposits?.includes(expected));
  ```

### C4: Crash — operator null in TripSummary
- `TripSummary.js:72`
- `item.operator.operator_name` — no optional chain on `operator`
- Fix: `item.operator?.operator_name`

---

## SECURITY

### S1: XSS — BlogPost unsanitized HTML
- `BlogPost.js:46`
- `dangerouslySetInnerHTML={{ __html: blogPost?.content }}` — raw CMS HTML, no DOMPurify
- Content from WordPress API — could contain injected scripts
- Fix: wrap with `DOMPurify.sanitize()` or `html-react-parser` with security config

### S2: XSS — RouteFaqs unsanitized HTML
- `RouteFaqs.js:19`
- `dangerouslySetInnerHTML={{ __html: item?.post?.data?.post?.content }}` — no sanitization
- Same fix as S1 (also dead code — see D3 below)

---

## MEDIUM

### M1: Active filter badge uses hardcoded price defaults
- `TripSearchFilters.js:~16`
- Compares `priceRange` against hardcoded `[0, 100]` but defaults come from API (`min_rate/max_rate`)
- Badge shows false "+1" when user never touched price slider
- Fix: pass actual min/max from `tripsFilterSet` as props

### M2: Unguarded contract field access in filter loop
- `FilteredTripList.js:35, 40, 45, 71, 77`
- `contract.route.departure_station` — no `?.` on `route`
- `contract.operator.operator_name` — no `?.` on `operator`
- `contract.extra.some()` — no `?.` on `extra`
- All crash if API returns contract with missing nested objects
- Fix: add optional chaining throughout `filterContracts()`

### M3: useTripFilters — setFilterData exposed raw
- `hooks/useTripFilters.js:~78`
- Exports `setFilterData` directly — caller can set arbitrary shape, breaking children expecting array fields
- Low risk today (only FilterTrip.js calls it)

### M4: Sort tiebreaker NaN on string IDs
- `FilteredTripList.js:120`
- `(a.id || 0) - (b.id || 0)` returns NaN for string IDs
- Fix: `String(b.id).localeCompare(String(a.id))`

### M5: Conditions + Amenities use OR logic
- `FilteredTripList.js:70-78`
- `.some()` = show trip if ANY selected condition matches (OR)
- WiFi + Meals selected → trips with WiFi **or** Meals shown
- Product decision: AND vs OR? If AND needed, restructure to `.every()` per selected item

### M6: FilterTrip handlers recreated every render
- `FilterTrip.js:264-293`
- `createCheckboxHandler` factory returns new functions on each render
- Causes child component re-renders if children aren't memoized
- Fix: memoize returned handlers or wrap factory in `useCallback`

### M7: DepartureStations labelRenderer not memoized
- `DepartureStations.js:13-17`
- Creates new function each render (ArrivalStations.js uses `useCallback`, DepartureStations doesn't)
- Fix: wrap in `useCallback`

### M8: Index as key on reorderable list
- `FilteredTripList.js:148`
- `<div key={index}>` — items reorder on filter/sort, causing wrong animations and state
- Fix: `key={contract.id}` or `key={contract.tripId}`

---

## DEAD CODE — Safe to Delete

### D1: TripList.js — orphaned
- `components/trips/TripList.js`
- Zero imports anywhere in codebase (confirmed by grep)
- FilteredTripList.js is the live version used in 5+ places

### D2: tripItemv2.js — orphaned
- `components/trips/tripItemv2.js`
- Zero imports anywhere (confirmed by grep)
- Legacy version of TripItem

### D3: RouteFaqs.js — orphaned
- `components/trips/RouteFaqs.js`
- Zero imports anywhere — only RouteFAQ.js is used
- Contains unsanitized dangerouslySetInnerHTML (S2 above)

---

## MINOR

### N1: Unused handleSortChange prop
- `FilterTripsPage.js:~254` passes to TripSearchFilters
- TripSearchFilters only uses `handleSortChangeDirect`

### N2: isLoading in JSDoc but not implemented
- `TripSearchFilters.js:~62`
- `@param {boolean} isLoading` documented, never destructured or used

### N3: getStaticProps unused props
- `pages/trips/[...slug].js:~143-144`
- Returns `lastModified` + `error` that FilterTripsPage never accepts

---

## WIRING — OK

- filterData lifts correctly: FilterTripsPage → FilterTrip + FilteredTripList ✓
- Dialog open/close handlers correctly wired ✓
- useTripFilters single instance at page level ✓
- Page file routes `/trips/[...slug]` to FilterTripsPage ✓
- Client-side filtering intentional ✓
- RTK Query `tripsApi` endpoints called with correct params ✓

---

## Fix Status

| # | Issue | File | Status |
|---|-------|------|--------|
| 1 | C2: ratecard crash | FilteredTripList.js:97 | ✅ FIXED |
| 2 | C3: composit length crash | FilteredTripList.js:53 | ✅ FIXED |
| 3 | C4: operator null crash | TripSummary.js:72 | ✅ FIXED |
| 4 | S1: BlogPost XSS | BlogPost.js:46 | ✅ FIXED (DOMPurify inline) |
| 5 | M2: filter loop unguarded | FilteredTripList.js:35,40,45,71,77 | ✅ FIXED |
| 6 | M1: badge hardcoded defaults | TripSearchFilters.js:16 | ✅ FIXED |
| 7 | M8: index key on list | FilteredTripList.js:148 | ✅ FIXED |
| 8 | D1-D3: delete dead files | 3 files | ✅ DELETED |
| 9 | C1: rewrite dialog handler | FilterTripsPage.js:169 | ✅ FIXED (clarity) |
| 10 | M4: tiebreaker NaN | FilteredTripList.js:120 | ✅ FIXED |
| 11 | M5: OR/AND conditions | FilteredTripList.js:70-78 | ✅ NO CHANGE (OR confirmed correct) |
| 12 | M6: handler memoization | FilterTrip.js:304-353 | ✅ FIXED (8 handlers → useMemo) |
| 13 | M7: labelRenderer memoize | DepartureStations.js:13 | ✅ FIXED (useCallback added) |

---

## ADDENDUM — Currency Context (2026-06-15, session #116)

Two more outliers on the same page fixed after the audit merged: hardcoded currency in user-facing labels, ignored `CurrencyContext`. All other price-rendering components on `/trips/hatyai/koh-lipe` (`TripItem`, `FilterTrip`, `TripDetailBooking`, `RouteFAQ`) were already using `useFormatPrice`. Calendar and "Departures by Operator" section were the last two. Same branch (`fix/trip-page-audit-2026-06-15`).

### CC1: SlideCalendar2 hardcoded `฿` symbol
- `components/search/SlideCalendar2.js:977`
- `฿{dayFare.toLocaleString()}` — ignored `CurrencyContext`. User selecting USD/EUR/JPY saw mixed display (calendar still in ฿, everything else converted).
- Fix: import `useFormatPrice`, call hook, replace render with `{formatPrice(dayFare)}` + add `whitespace-nowrap` + add `formatPrice` to `useCallback` deps array.
- Lint clean.
- Atom: [[currency-context-price-rendering-rule]] (Rule 1 — user-facing labels)

### CC2: TripSummary "from THB" hardcoded prefix
- `components/trips/TripSummary.js:35`
- `from THB {minPrice.toLocaleString()}` in the `TripItem` local component (not the canonical `components/trips/TripItem.js`). Bypassed currency context.
- Fix: import `useFormatPrice`, call hook in local `TripItem`, replace render with `from {formatPrice(minPrice)}`, change guard to `formatPrice(minPrice) && ...` (returns null for `price <= 0`).
- Lint clean.
- Atom: [[currency-context-price-rendering-rule]] (Rule 1 — user-facing labels)

### CC3: JSON-LD priceCurrency kept as THB (NOT a fix — intentional)
- `components/trips/TripSummary.js:91` — `priceCurrency: 'THB'` + raw `price: minPrice`
- Schema.org `Offer` describes the **merchant offer**, not viewer display. Converting to USD would misrepresent the actual transactional price to Google.
- Atom: [[currency-context-price-rendering-rule]] (Rule 2 — JSON-LD integrity)
- Companion: [[structured-data-schema-patterns]]

### CC4 (out of scope): TripDetailSchedule doesn't wire fareCalendar
- `components/trips/TripDetailSchedule.js:46-49` renders `SlideCalendar2` without `fareCalendar` + `fareCalendarLoading` props. Falls through to invisible `–` on every cell. Used on separate route `/trips/detail/[...slug]`.
- **Pre-existing bug, not caused by currency fix.** Only 1 of 5 `SlideCalendar2` callers wires the props — see [[slidecalendar2-farecalendar-prop-pattern]] for the full caller inventory and follow-up fix recipe.
- Fix when revisited: copy `useGetFareCalendarQuery` + `skipToken` block from `TripSearchFilters.js:80-99` into `TripDetailSchedule.js`, pass both props. Separate PR.

### Why these were not in the original audit
The full audit focused on crashes, XSS, dead code, perf. Currency rendering was an orthogonal concern — *if `useCurrency` worked correctly* (it did) and *if the component called `useFormatPrice`* (it didn't). Not a regression; just two more components that needed the same hook call everyone else had. A "currency rendering audit" pattern check would catch all 7 in one pass — see [[currency-context-price-rendering-rule]] audit checklist.

## Related

[[currency-context-price-rendering-rule]] | [[slidecalendar2-farecalendar-prop-pattern]] | [[trip-filter-modal-audit-2026-06-15]] | [[frontend-architecture-audit-2026-06-11]] | [[trip-search-results-redesign-2026-06-14]] | [[trip-search-below-fold-redesign-2026-06-15]]
