# Layout Spacing Consistency Audit 2026-06-01

## Summary

Cross-page layout audit: activities browse (`/activities`) vs homepage (`/`) vs trips browse (`/trips`). 3 inconsistencies found. Container width consistent. H-padding and card grid gap deviate on activities.

---

## Context

Triggered by activities browse audit sprint (branch `260601-fix/activities-browse-audit`). After functional fixes (FQ-0 through DS-1), checked layout values against site-wide standards before merge.

Pages compared:
- Homepage: `pages/homepagev2.js` + `components/common/Section.js` + `lib/homepage/components/PopularRoutesSection.js`
- Trips: `pages/trips/index.js` + `components/trips/tripItemv2.js` + `components/trips/TripSummary.js`
- Activities: `components/activities/browse/FilterDayTripsPage.js` + `DayTripList.js` + `DayTripCard.js`

---

## Canonical Patterns

Authoritative layout values from homepage (most refined page). New browse pages match these.

| Token | Value | Tailwind | Used in |
|-------|-------|---------|--------|
| Container max-width | 1200px | `max-w-[1200px] mx-auto` | All pages ✓ |
| Horizontal padding mobile | 16px | `px-4` | Homepage sections |
| Horizontal padding xl | 0 | `xl:px-0` | Homepage sections |
| Section vertical padding | 24px | `py-6` | Homepage + Trips |
| Card inset margin (non-grid) | 8px→12px→0 | `mx-2 md:mx-3 xl:mx-0` | TripSummary.js |
| Inter-section gap (homepage) | 32px | `gap-8` | `homepagev2.js` main |
| Section internal gap | 12px | `gap-3` | `Section.js` base |

Trips uses tighter h-padding (`px-2 md:px-3`) — hero search bar extends full-bleed. Clean browse page (no hero): use homepage standard `px-4 xl:px-0`.

---

## Page Comparison Table

### Container + Outer Padding

| Property | Homepage | Trips | Activities | Match? |
|----------|----------|-------|------------|--------|
| Max-width | `max-w-[1200px]` | `max-w-[1200px]` | `max-w-[1200px]` | ✓ |
| H-padding mobile | `px-4` | `px-2 md:px-3` | `p-2` (all sides) | ✗ |
| H-padding xl | `xl:px-0` | — | — | ✗ |
| V-padding | `py-6` | `py-6` | `pb-6 sm:py-8` | ✗ partial |

### Card Grid Gap

| Property | Homepage cards | Trips grid | Activities skeleton | Activities loaded |
|----------|---------------|------------|--------------------|--------------------|
| Gap | N/A (carousel) | `gap-4 md:gap-6` | `spacing={2}` (16px) | `spacing={1}` (8px) |
| Match? | — | Reference | Partial (16=gap-4) | ✗ (8px too tight) |

### Card Internal Padding

| Property | Homepage PopularRouteCard | Trips TripItem | Activities DayTripCard |
|----------|--------------------------|----------------|------------------------|
| Content padding | varies by card | `p-2` (8px) | `px:3 pt:3 pb:3` (24px) |
| Intentional? | Yes | Yes (list style) | Yes (image card) |
| Match needed? | No — different card types | No | No |

---

## Issues Found

### LAY-1 [P1] — Activities horizontal padding wrong

**File:** `components/activities/browse/FilterDayTripsPage.js:55`
**Current:** `className="w-full max-w-[1200px] mx-auto p-2 pb-6 sm:py-8"`
**Problem:** `p-2` applies 8px on ALL sides at ALL breakpoints. No `xl:px-0` to bleed edge-to-edge at wide viewports. Content too narrow-margined on mobile, still has margins on xl where it shouldn't.
**Fix:**
```
w-full max-w-[1200px] mx-auto px-4 xl:px-0 py-2 pb-6 sm:py-8
```
Change `p-2` → `px-4 xl:px-0`. Keep vertical padding as-is.

### LAY-2 [P1] — Grid gap mismatch between loading and loaded states

**File:** `components/activities/browse/DayTripList.js`
**Current:** Skeleton: `<Grid container spacing={2}>` | Loaded: `<Grid container spacing={1}>`
**Problem:** `spacing={2}` = 16px while loading, collapses to `spacing={1}` = 8px on load. Visible layout shift. Cards jump 8px closer when data arrives.
**Fix:** Both to `spacing={2}`. 16px matches trips' `gap-4` reference.
```js
// Line 41 (skeleton) — already correct spacing={2}
// Line 85 (loaded) — change spacing={1} → spacing={2}
```

### LAY-3 [P2] — Vertical padding `sm:py-8` vs standard `py-6`

**File:** `components/activities/browse/FilterDayTripsPage.js:55`
**Current:** `sm:py-8` = 32px vertical at sm+
**Standard:** `py-6` = 24px (homepage + trips)
**Assessment:** Browse pages content-dense — extra breathing room (32px) defensible. Not a bug. Keep `sm:py-8`, document as intentional browse-page exception.

---

## Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Activities h-padding | Fix to `px-4 xl:px-0` | Match homepage standard. `p-2` wrong — applies all sides uniformly. |
| Grid gap unification | Fix loaded to `spacing={2}` | Prevent layout shift. 16px correct card density for image browse grid. |
| Vertical `sm:py-8` | Keep — intentional exception | Browse pages benefit from extra top/bottom breathing vs section cards. |
| Card content padding | No change — intentional | DayTripCard at 24px correct for image card anatomy. Trips list at 8px correct for list-row style. |

---

## Fix Scope

**LAY-1 + LAY-2** apply on `260601-fix/activities-browse-audit` before merge. Both 1-2 line changes.

- `FilterDayTripsPage.js:55` — `p-2` → `px-4 xl:px-0 py-2`
- `DayTripList.js:85` — `spacing={1}` → `spacing={2}`

---

## Related

- [[activities-day-tour-page-review]] — Full functional audit this layout check follows
- [[featured-image-header-width-bug]] — Prior width bug: `w-[1200px]` hardcoded broke mobile. Rule: never `w-[Npx]` on layout elements.
- [[airport-transfer-width-audit]] — Unresolved inner padding issue on AT post-calendar sections
- [[design-system-tokens-expansion]] — SPACING tokens defined but not yet applied to layout containers