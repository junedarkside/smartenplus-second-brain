# ADR: Homepage Search — Transportation | Experiences Tabs

## Status
proposed — audited 2026-06-17 (scrutinize pass): direction confirmed, two gaps corrected (token source = `helpers/designSystem.js` not just Tailwind; Experiences destination must NOT reuse `ActivitySearch`). Implementation plan: [[homepage-search-transportation-experiences-tabs]].

## Context

A 2026 "10/10" homepage redesign spec reframes SmartEnPlus from booking-engine to **Thailand Travel Discovery + Transportation**, and asks the homepage search component to gain a **Transportation | Experiences segmented control**. This ADR reviews the *search component only* (hero + search form) against that spec and records the recommended approach. No frontend code changed yet.

**Review charter (binding, per frontend `CLAUDE.md`):** no tech debt · no over-engineering · keep it simple (≤200 lines/component) · **reuse first**.

### Current state (frontend)
- Homepage `pages/index.js` → `pages/homepagev2.js`.
- Hero/search = `lib/homepage/components/DiscoverySection.js:9-27` — search form inside a **white card** (`bg-white border rounded-md shadow-md`) on a `bg-warm-surface` band. This is exactly the "search form in a white card" the spec rejects. No hero image, no segmented control.
- Search form = `components/search/ProductSearchForm2.js` (~380 lines, MUI) — **Transportation only**: From/To (swap) / Date / optional Return / Passengers / Search → builds `/trips/[from]/[to]?date=&people=&direction=` (`homepagev2.js:171-203`). Already **over** the 200-line ceiling.
- No Experiences mode, no popular-route chips.

### The decisive contract finding
The spec's Experiences form lists **Destination + Date + Guests + Category**. But the destination page it would feed — `/activities` — consumes a *different* shape:
- `pages/activities/index.js:14` reads **only** `?location=` and `?category=`.
- `components/activities/browse/FilterDayTripsPage.js:47-90` + `useDayTripFilters` expose: `location`, `category` (service_category), free-text `search`, price, duration, contract, features, rating, sort. **No `date`. No `guests`.**
- Category source already exists: `EXPERIENCE_CATEGORIES` + `SERVICE_CATEGORY_LABELS` in `constants/dayTripConstants.js` (enum documented in [[adr-experiences-nav-category-filtering]]).
- The activities page already ships a **reusable search bar**: `components/activities/shared/ActivitySearch.js` (location autocomplete via `useGetActivityLocationsQuery` + free-text, with `compact`/`stacked` + controlled-input props).

So **Date and Guests in the spec's Experiences form have no backend or page to consume them.** Adding them = dead UI = tech debt (charter violation).

## Decision

Mirror the **activities page's real search** in the homepage Experiences tab, not the spec's literal field list.

1. **Hero — reuse, don't build.** Replace the white-card `DiscoverySection` with `components/UI/FeaturedImageHeader.js` using `isCinematic` (full-bleed) + `customMinHeight="min-h-[500px] md:min-h-[620px]"` + destination photo, passing the segmented control + active search form into its `children` slot. It already provides `next/image` `fill`/`cover`, `priority`, blur placeholder, and `hero-top-gradient` overlay.
2. **Segmented control — local state.** `Transportation | Experiences` as a plain 2-option control; active mode held in **local `useState`** in the search block (UI-only; no Redux). Selected = brand-colored underline + bold (no bordered tabs).
3. **Transportation mode** — the existing `ProductSearchForm2` flow, unchanged in behavior.
4. **Experiences mode** = **Destination + Category** only → `router.push('/activities?location=<dest>&category=<SERVICE_CATEGORY>')`. **Do NOT reuse `ActivitySearch`** for the destination (see Gap-2 correction below) — it drags `useGetActivityLocationsQuery` (RTK `dayTripsApi`) + `useDayTripFilters` onto the homepage, which loads neither today. Instead reuse the **existing `AutoCompleteSearch`** (already powers Transportation, zero new deps) or a thin freeSolo input, and `EXPERIENCE_CATEGORIES`/`SERVICE_CATEGORY_LABELS` (`constants/dayTripConstants.js`) as a static category selector (no API). The URL is built with the same plain string-template pattern already used at `components/activities/detail/ExperienceTitleArea.js:46` / `DayTripDetailHeader.js:101` (`/activities?category=${service_category}`). **Drop Date and Guests** until `/activities` supports them.
5. **Shared state** — Destination reuses the existing `from_location` slice (`store/location-slice.js`; `AutoCompleteSearch onLocation='from'` already writes there). Category is Experiences-only local state. Switching tabs **retains** shared location, leaves the rest independent. No new Redux slice.
6. **Form split (charter)** — because `ProductSearchForm2` is already >200 lines, do **not** add a second mode inline. Extract shared sub-fields (location, date, passengers) into composable pieces; each mode component composes them; the segmented control picks which renders. Split, don't duplicate.
7. **Tokens** — the canonical token source for the search/experiences UI is **`helpers/designSystem.js`** (a richer JS module than `tailwind.config.js`; it's what `ActivitySearch.js:9` and the activities browse UI import). Map spec *intent* there:

| Spec value | Canonical token (`helpers/designSystem.js`) | Resolution |
|---|---|---|
| primary `#1E4ED8` | `COLORS.brand.primary #3b5998` / `COLORS.brand.secondary #2563eb` (mirrors `tailwind brand.*`) | use brand token; do not hardcode `#1E4ED8` |
| radius `16` | `BORDER_RADIUS.button '6px'`, `BORDER_RADIUS.imageCard '12px'` (no 16) | search button → `button` (6px); hero/photo cards → `imageCard` (12px). 16 is off-system — do not introduce. |
| button height `56px` | `TOUCH_TARGET.minHeight '44px'` (WCAG floor only) | no height token; 56px is a deliberate one-off `h-14`, above the 44px minimum — fine. |
| weight `600` | `FONT_WEIGHTS.semibold 'font-semibold'` | use `FONT_WEIGHTS.semibold`. |
| 1200px shell | `LAYOUT` / `tailwind maxWidth.container 1200px` ✓ | matches |

> Correction to first draft: the original table reconciled against `tailwind.config.js` only and proposed a possible new 16px token. `designSystem.js` is canonical and already standardizes radius (`button 6` / `imageCard 12`) — **no new radius token; 16px is rejected.**

## Alternatives Considered
1. **Keep all 4 Experiences fields, pass `?date=&guests=` anyway** — rejected: `/activities` ignores them → dead params, tech debt.
2. **All 4 fields + add date/guests filtering to backend + RTK query** — rejected for this scope: out of the search-component boundary, larger effort; revisit only if activities inventory gains time/occupancy.
3. **Add second mode inline in `ProductSearchForm2`** — rejected: worsens an already >200-line monolith (charter).
4. **New Redux slice for Experiences / mode state** — rejected: mode is UI-only (local `useState`); destination reuses existing location state. New slice = over-engineering.
5. **Build a fresh hero** — rejected: `FeaturedImageHeader` covers ≥80%; reuse it.
6. **Reuse `ActivitySearch` for the Experiences destination** — rejected after audit: `ActivitySearch.js:40` fires `useGetActivityLocationsQuery` unconditionally (even in controlled mode), forcing `dayTripsApi`/RTK + a locations API call onto homepage load. Use `AutoCompleteSearch`/thin input instead.

## Tradeoffs
- **Gained:** spec's editorial hero + Transportation|Experiences UX with zero new infra — reuses `FeaturedImageHeader`, `AutoCompleteSearch`, static category constants, `from_location` slice, existing URL-template pattern. **No new RTK slice or API call on the homepage.** No tech debt.
- **Lost:** Date/Guests in the Experiences tab (they were never consumable). Honest scope, not a regression.
- **Risk (resolved by Gap-2 audit):** the first draft proposed reusing `ActivitySearch`. Audit showed `ActivitySearch.js:40` fires `useGetActivityLocationsQuery` **unconditionally** (controlled mode does not gate it) — reuse would add `dayTripsApi` (RTK) + a locations API call to homepage load, which it doesn't carry today. **Decision: do not reuse `ActivitySearch`** on the homepage; use `AutoCompleteSearch` (already present) or a thin input + static category select, build the URL on Search. Remaining risk: `AutoCompleteSearch` writes `from_location` — confirm sharing that slot with Transportation matches the "retain shared location" intent (it does).

## Consequences
- `DiscoverySection.js` is replaced by a hero-backed search block; `ProductSearchForm2` is refactored into composable sub-fields + two mode components + a segmented control.
- Experiences tab routes to the existing `/activities?location=&category=` contract — no backend change.
- Popular-route chips (Transportation) + button restyle are token-mapped, brand-colored.
- Verify against `CLAUDE.md` Search gotchas (StickySearchBar Redux-empty URL-slug fallback, `HeaderSearchSummary`, `HeaderSearchContext`) — Transportation behavior must be unchanged.
- If Date/Guests are wanted later, that's a separate backend+ADR effort.

## Related
- [[adr-experiences-nav-category-filtering]] — category enum + `/activities?category=` server-filter contract reused here
- [[check-your-booking-redesign]] — adjacent homepage redesign work
