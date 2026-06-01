# Activities Search — Merge Review 2026-06-01

## Summary

3-specialist team (UX/UI, Design, Frontend) reviewed whether `/activities` dual search inputs (location + keyword) should merge into one. Verdict: true merge deferred — backend architecture doesn't support it cleanly. Implemented: icon differentiation + side-by-side layout. Zero behavior change.

---

## Context

Page had two visually near-identical search inputs stacked vertically:
1. **Location** (`DayTripLocationSearch`) — MUI Autocomplete, POPULAR_DESTINATIONS dropdown, sends `?location=`
2. **Keyword** (`TextField`) — plain input, sends `?search=`

Both had `SearchIcon` (magnifier) startAdornment, same height, same border radius. No visual distinction except placeholder text. Users confused about which to use.

---

## Problem

- Two inputs looked identical → user didn't know which to type in
- Standard OTA pattern (Klook, Viator, GetYourGuide) uses ONE search bar
- True merge question: can they become one input?

---

## Team Findings

### UX/UI Specialist

**FOR merge:** Reduces cognitive load. One box. Matches mental model. More cards above fold.

**AGAINST merge:** Backend treats location + keyword as independent filters — they AND together. `?location=Phuket&search=snorkeling` = Phuket snorkeling tours. Merging loses this power. Intent disambiguation ("Phuket snorkeling" = which filter?) requires NLP or explicit affordance.

**Verdict:** Merge valid only if bar does both — location suggestions as `📍` chips + keyword results inline. That's Klook-level complexity. Simpler fix: differentiate the two inputs visually. Equal UX clarity, zero code risk.

### Design Specialist

**Visual problem identified:**
- Same icon (SearchIcon) on both inputs
- No label hierarchy (only placeholder text differed)
- Stacked layout gave no grouping cue that they're related filters

**Options evaluated:**

| Option | Description | Complexity | Risk |
|--------|-------------|------------|------|
| 1 — Merge hero bar | Single 56px bar, grouped autocomplete | High (~100 lines) | High |
| 2 — Icon + label diff | Pin icon for location, magnifier for keyword | Minimal (4 lines) | None |
| 3 — Side-by-side on desktop | `flex-row` on sm+, `flex-col` on mobile | Low (4 lines) | None |

**Verdict:** Option 2 + 3 combined. Solves the UX problem with 8 lines of code.

### Frontend Specialist

**True merge feasibility:**
- Single `<Autocomplete>` with grouped options needs type-discriminated suggestions
- `useDayTripFilters` has separate `location` + `search` keys — merge requires routing freetext to one or both
- Freetext → keyword = location only selectable from dropdown (acceptable but different UX)
- Freetext → location = keyword search lost entirely
- Freetext → both = backend ANDs them → no results unless contract matches both fields

**Simpler merge (keyword absorbs location):**
Route everything to `search`, extend backend search filter to hit location fields. Loses `filters.location` → H1 dynamic title ("Day Trips in Phuket"). Needs backend change.

**Verdict:** Side-by-side (Option 3) has best effort/risk ratio for current sprint. True merge revisit when backend can handle OR-union on a single param.

---

## Debate & Resolution

### Debate 1 — True merge vs visual fix

UX wants merge. Design says differentiate. Frontend says merge needs backend work.

**Resolution:** Defer true merge. Implement Option 2 + 3 now. Revisit merge in a dedicated sprint with backend involvement.

### Debate 2 — Freetext routing in a merged scenario

Three options analyzed (keyword, location, both). All have tradeoffs. Backend currently ANDs `location` + `search` params — sending freetext to both would over-restrict results.

**Resolution:** Moot this sprint. Requires backend `OR` union support first.

### Debate 3 — Mobile layout at 50/50 split

375px phone → each input ~166px wide. Usable but tight. Placeholder text would truncate.

**Resolution:** `flex-col sm:flex-row` — stacked on mobile, side-by-side on sm+ (640px+). Standard Tailwind responsive pattern.

---

## Decision

**Implemented (2026-06-01):**
- Location input: `LocationOnIcon` (pin) as startAdornment — visually = "place"
- Keyword input: `SearchIcon` (magnifier) as startAdornment — visually = "search"
- Labels: "Destination" + "Activity or tour name"
- Layout: `flex-col sm:flex-row gap-3` wrapper — side by side on sm+
- Zero behavior change — both filters still independent

**Grill finding (2026-06-01) — "backend OR-union required" claim OVERTURNED:**
- True merge IS feasible without backend change
- Intent detection = `POPULAR_DESTINATIONS.some(d => d.name.toLowerCase() === input || d.keywords.includes(input))` — static list check, not NLP
- Freetext typed → keyword (`?search=`). Location only via autocomplete selection (`?location=`). Both params still AND correctly.
- BLOCKED by tech debt: two separate POPULAR_DESTINATIONS sources with incompatible shapes:
  - `utils/popularDestinations.js` — flat `string[]`, used by `DayTripLocationSearch` + `ListLocation`
  - `components/autocompletesearch/utils/popularDestinations.js` — rich `Object[]` with `name`, `nameTh`, `category`, `keywords[]`, used by `SearchResultsList`
- Merge requires consolidating to single canonical source first. No side effects confirmed.

**COMPLETED (2026-06-01 session #21):**
1. **ACT-5 — Destinations data consolidated** — `utils/destinations.js` (canonical rich `Object[]`). Old files deleted. `ListLocation` + `SearchResultsList` import updated. `DayTripLocationSearch` deleted (superseded).
2. **ACT-6 — Unified `ActivitySearch` component** — single MUI Autocomplete, dropdown selection → `?location=`, freetext → `?search=`. No `isLocationMatch` needed.
3. **Backend source of truth added** — `ActivitySearch` fetches locations from new `GET /api/v1/contract/locations/?service_category=DAY_TOUR`. Returns only locations with active contracts. Hardcoded static list no longer used for dropdown.
4. **Backend: `GET /api/v1/contract/locations/`** — `@action` on `ContractViewSet`. Distinct `Location` objects from `primary_location` FK + `service_areas` M2M. 1h cache, invalidated on contract save/delete.

---

## Consequences

- UX confusion eliminated — single search bar, OTA pattern
- Dropdown shows only real destinations (backend source of truth, not hardcoded list)
- Intent: dropdown selection = location filter, freetext = keyword search — unambiguous
- `filters.location` → H1 "Day Trips in X" still works
- `utils/destinations.js` kept — still used by `ListLocation` + `SearchResultsList` for header search

---

## Files Changed

| File | Change |
|------|--------|
| `utils/destinations.js` | CREATED — canonical rich destinations, replaces both old files |
| `utils/popularDestinations.js` | DELETED |
| `components/autocompletesearch/utils/popularDestinations.js` | DELETED |
| `components/activities/shared/ActivitySearch.js` | CREATED — unified search, RTK Query hook |
| `components/activities/shared/DayTripLocationSearch.js` | DELETED |
| `components/activities/browse/FilterDayTripsPage.js` | Dual inputs → single `ActivitySearch` |
| `components/search/ListLocation.js` | Import → `utils/destinations` |
| `components/autocompletesearch/SearchResultsList.js` | Import → `utils/destinations` |
| `store/api/dayTripsApi.js` | Added `getActivityLocations` endpoint |
| `products/views.py` (backend) | `locations` action on `ContractViewSet` |
| `products/signals.py` (backend) | Cache invalidation for `contract_locations_v1_*` |

---

## Related

- [[activities-day-tour-page-review-2026-06-01]] — UX-1 finding originally flagged dual unlabeled search as P0
- [[activities-location-search-bug-2026-06-01]] — location search zero-results bug fix (RC-1 through RC-3)
- [[adr-experiences-nav-category-filtering-2026-05-25]] — category URL param chain
