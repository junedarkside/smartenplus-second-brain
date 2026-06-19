# Trip Filter Modal Audit — 2026-06-15

## Summary
3-agent functional audit of filter modal on `/trips/hatyai/koh-lipe`. 2 critical bugs, 2 logic ambiguities, 4 minor dead-code issues. Core wiring intact.

## Context
User requested audit of filter modal components and functions for functional correctness. Scope: filter modal only (not full trip page). 3 parallel Explore agents ran against FilterTrip.js, useTripFilters.js, FilteredTripList.js, TripSearchFilters.js, TransportationOptionsFilter.js, FilterTripsPage.js, and the page route file.

## Details

### Architecture — How Filter Modal Works

| Layer | File | Role |
|-------|------|------|
| Page route | `pages/trips/[...slug].js` | Renders FilterTripsPage for `/trips/hatyai/koh-lipe` |
| Orchestrator | `components/trips/FilterTripsPage.js` | Holds `isFilterDialogOpen` state, renders MUI Dialog |
| State hook | `hooks/useTripFilters.js` | Single source of truth for all filter state |
| Filter UI | `components/trips/FilterTrip.js` | 8 expandable filter sections inside the dialog |
| Control bar | `components/trips/TripSearchFilters.js` | Sort pills + filter button with active count badge |
| Transport pills | `components/trips/TransportationOptionsFilter.js` | Horizontal transport type selector |
| Filter logic | `components/trips/FilteredTripList.js` | Client-side in-memory filtering + sorting |
| Data fetch | `store/api/tripsApi.js` | `getTripFilterSet()` fetches available filter options once |

**Key design:** filtering is fully client-side — no API call on filter change. Filter set fetched once from `/api/v1/tripfilter/{from}/{to}/`.

---

### CRITICAL BUGS

**BUG-1: Transport options filter silently fails (typo field name)**
- File: `components/trips/FilteredTripList.js` ~line 51
- `option.trasportation_com` (misspelled) — if API returns `transportation_com` (correct), filter finds nothing
- Result: selecting any transport option shows 0 results instead of filtered results
- Fix: mirror fallback pattern from `TransportationOptionsFilter.js` lines 13, 36:
  ```js
  // Current (broken):
  const expectedTransportComposits = option.trasportation_com?.map(...)
  // Fixed:
  const expectedTransportComposits = (option?.transportation_com || option?.trasportation_com)?.map(...)
  ```

**BUG-2: Active filter count badge shows false positive on price range**
- File: `components/trips/TripSearchFilters.js` ~line 16
- Badge count checks `priceRange !== [0, 100]` hardcoded, but actual defaults come from `tripsFilterSet.min_rate / max_rate` (set in `useTripFilters.js` ~line 34-35)
- Result: if route has min_rate=500, max_rate=8000, badge shows "+1 active filter" even when user never touched price
- Fix: receive actual min/max as props or compare against tripsFilterSet values

---

### LOGIC AMBIGUITY (product decision needed)

**AMBIG-1: Conditions + Amenities use OR logic**
- File: `components/trips/FilteredTripList.js` ~lines 70-78
- Both use `.some()` — selecting WiFi + Meals shows trips with WiFi **OR** Meals
- If intent is AND (trips must have ALL selected), switch to `.every()` check per selected item
- Clarify with product: OR = "discovery mode", AND = "strict match"

**AMBIG-2: Sort tiebreaker fails on string IDs**
- File: `components/trips/FilteredTripList.js` ~line 120
- `(b.id || 0) - (a.id || 0)` returns NaN if IDs are strings
- Low impact if IDs are always numeric, but should be hardened:
  ```js
  // Fix:
  String(b.id).localeCompare(String(a.id))
  ```

---

### MINOR ISSUES (dead code / stale props)

**MINOR-1: Unused handleSortChange prop**
- `FilterTripsPage.js` ~line 254 passes `handleSortChange` to TripSearchFilters
- TripSearchFilters never uses it (uses `handleSortChangeDirect` only)
- Safe to remove the prop pass

**MINOR-2: Documented but unimplemented isLoading prop**
- `TripSearchFilters.js` ~line 62 JSDoc declares `@param {boolean} isLoading`
- Never destructured or used in component body
- Remove JSDoc entry or implement

**MINOR-3: getStaticProps returns unused props**
- `pages/trips/[...slug].js` ~lines 143-144 returns `lastModified` and `error`
- FilterTripsPage never accepts them — silently dropped
- Remove from getStaticProps return or add to component props

**MINOR-4: Raw setFilterData exposed without shape validation**
- `hooks/useTripFilters.js` ~line 78 exports `setFilterData` directly
- Caller can set arbitrary shape, breaking children that expect arrays for conditions/amenities/etc.
- Low risk today (only FilterTrip.js calls it), but fragile

---

### WIRING — ALL OK

- filterData lifted to FilterTripsPage, flows to both FilterTrip and FilteredTripList ✓
- Dialog open/close wired correctly (handleOpenFilterDialog / handleCloseFilterDialog) ✓
- useTripFilters instantiated once at page level (single source of truth) ✓
- Page file `/trips/[...slug].js` renders correct component for URL pattern ✓
- FilterTrip receives all required props from FilterTripsPage ✓
- Client-side filtering is intentional — correct by design ✓

## Decision

No code changes in this session — report only. Fix order:

1. **BUG-1** (transport filter silent failure) — fix typo fallback, ~2 lines
2. **BUG-2** (price range badge false positive) — pass min/max as props, ~5 lines
3. **AMBIG-1** (OR vs AND conditions) — product decision first
4. **AMBIG-2** (tiebreaker NaN) — low priority edge case
5. **MINOR-1 to 4** — cleanup sprint

## Related

[[frontend-architecture-audit]] | [[trip-search-results-redesign-2026-06-14]] | [[trip-route-page-seo-aeo-geo-audit]]
