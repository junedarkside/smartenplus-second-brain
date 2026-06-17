# Homepage Search — Transportation | Experiences Tabs (Implementation Plan)

## Summary
File-by-file plan to add a Transportation | Experiences segmented control to the homepage search, replace the white-card hero with the existing cinematic hero, and split the over-size search form. Decision basis: [[adr-homepage-search-transportation-experiences-tabs-2026-06-17]] (audited 2026-06-17). Frontend repo: `smartenplus-frontend`. No backend change.

## Charter (binding)
No tech debt · no over-engineering · KISS (≤200 lines/component, ≤30/function, ≤3 params) · reuse first.

## Audit-confirmed constraints (do not relitigate)
- `/activities` contract = `?location=&category=` only — no date/guests (`hooks/useDayTripFilters.js:19-32`). Experiences tab = Destination + Category.
- **Do NOT reuse `ActivitySearch`** — `ActivitySearch.js:40` fires `useGetActivityLocationsQuery` unconditionally → would add `dayTripsApi` RTK + API call to homepage (not loaded today).
- Tokens canonical in `helpers/designSystem.js` (`COLORS.brand.primary`, `BORDER_RADIUS.button 6`/`imageCard 12`, `FONT_WEIGHTS.semibold`). No 16px radius.
- Category list = static `EXPERIENCE_CATEGORIES` + `SERVICE_CATEGORY_LABELS` (`constants/dayTripConstants.js:22-44`).
- Experiences URL built with plain template (pattern: `ExperienceTitleArea.js:46`, `DayTripDetailHeader.js:101`).

## Build steps (ordered)

### 1. Extract shared sub-fields from `ProductSearchForm2.js` (379 → smaller)
Split the monolith so both modes compose, none duplicated. New files under `components/search/fields/`:
- `LocationField.js` — the From/To label+input+swap block (currently `ProductSearchForm2.js:227-267`). Props: which slot, value, onClick, error.
- `DateField.js` — departure/return date trigger (`:268-317`). (A thin `DateField.js` already exists in `components/search/` — check before creating; extend it, don't fork.)
- `PassengerField.js` — passenger trigger (`:320-330`).
Each ≤~60 lines. Transportation mode composes all; Experiences composes Location(destination) only.

### 2. `TransportationSearch.js` (new, ~120 lines)
The current `ProductSearchForm2` body (round-trip switch, From/To/Date/Return/Passenger/Search, modals, `handleFindTrips` URL build) composing the step-1 fields. Behavior unchanged — same Redux slices (`location-slice`, `calendar-slice`, `passenger-slice`), same `/trips/[from]/[to]?date=&people=&direction=` navigation (`pages/homepagev2.js:171-203` logic stays where it is or moves with the form — keep the `onSearch` prop contract).

### 3. `ExperiencesSearch.js` (new, ~80 lines)
- Destination: reuse `AutoCompleteSearch` (`onLocation='from'` → writes `from_location` slice, shared with Transportation per decision) OR a thin freeSolo MUI Autocomplete. No `ActivitySearch`, no RTK.
- Category: static select/chips from `EXPERIENCE_CATEGORIES`/`SERVICE_CATEGORY_LABELS`.
- Search Experiences → `router.push(\`/activities?location=${encodeURIComponent(dest)}&category=${cat}\`)`. Use `helpers/urlUtils.js`/`slugify.js` if a builder fits; else inline template (matches existing pattern).

### 4. `SearchModeTabs.js` (new, ~40 lines)
Segmented control Transportation | Experiences. Active mode = **local `useState`** in the parent search block (no Redux). Selected = `COLORS.brand.primary` underline + `FONT_WEIGHTS.semibold`. Not bordered tabs.

### 5. Hero — replace `DiscoverySection.js`
Swap white card for `components/UI/FeaturedImageHeader.js`: `isCinematic`, `customMinHeight="min-h-[500px] md:min-h-[620px]"`, destination `imgUrl`, and pass `SearchModeTabs` + active mode form as `children`. Keep the `onSearch`/`errors` prop pass-through from `homepagev2.js:348-353`. Ensure legibility: form sits on the `hero-top-gradient` overlay; may need a translucent panel behind fields (token: `COLORS`, not raw).

### 6. Popular-route chips (Transportation only)
Below the search, chips from existing `responseHomePage` routes (`homepagev2.js:118-122`). White/80% text, underline on hover. Link to the same `/trips/...` path.

### 7. Button restyle
Search button → `h-14` (56px), `rounded-md` (`BORDER_RADIUS.button` 6px), `FONT_WEIGHTS.semibold`, `COLORS.brand.primary`. No raw `#1E4ED8`, no 16px.

## Reuse map
| Need | Reuse (path) |
|---|---|
| Hero | `components/UI/FeaturedImageHeader.js` |
| Destination autocomplete | `components/autocompletesearch/AutoCompleteSearch.js` |
| Date / passenger | existing `components/search/DateField.js`, `Passenger.js` |
| Category data | `constants/dayTripConstants.js` (EXPERIENCE_CATEGORIES, SERVICE_CATEGORY_LABELS) |
| Tokens | `helpers/designSystem.js` |
| Location state | `store/location-slice.js` (`from_location`) |
| URL template | pattern at `ExperienceTitleArea.js:46` |

## Regression checks (CLAUDE.md Search gotchas)
- `StickySearchBar` Redux-empty → URL-slug fallback (`fromLocationRedux || fromSearch`) still works.
- `HeaderSearchSummary` / `HeaderSearchContext` sticky injection (`homepagev2.js:139-150`) unaffected — Transportation summary unchanged; decide whether sticky shows Experiences mode (recommend: Transportation only for v1).
- No `useEffect` chains; mode is derived/local, not effect-synced.

## Verify
- `npm run dev` → homepage: hero photo + gradient, segmented control switches modes, Transportation search → `/trips/...` identical to today, Experiences search → `/activities?location=&category=` lands filtered.
- Confirm Network tab: **no new dayTripsApi locations call on homepage load** (proves ActivitySearch not pulled in).
- Each new component ≤200 lines; `ProductSearchForm2` removed or reduced to a thin re-export.
- Existing search/sticky tests pass; add a test for the Experiences URL builder.

## Related
- [[adr-homepage-search-transportation-experiences-tabs-2026-06-17]]
- [[adr-experiences-nav-category-filtering-2026-05-25]]
