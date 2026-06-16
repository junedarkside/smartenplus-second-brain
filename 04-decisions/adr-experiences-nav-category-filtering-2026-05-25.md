# ADR: Experiences Nav → Activities Category Filtering

## ⚠️ SUPERSEDED 2026-05-25

Original decision (Experiences submenu with `?category=` children) was reversed same session.

**New decision:** No Experiences submenu. `navConfig.js` Experiences → `children: null`.

**Reason:** `CategoryFilter` on `/activities` page already hardcodes from `SERVICE_CATEGORIES` in `dayTripConstants.js`. Nav submenu would be a second source of truth. Keeping submenu requires either (a) manual NavigationItem DB entries that drift from `SERVICE_CATEGORY_CHOICES`, or (b) new backend endpoint — neither justified when on-page chips solve the same UX need.

**If submenu returns:** derive `navConfig.js` Experiences children dynamically from `SERVICE_CATEGORY_LABELS` in `dayTripConstants.js`. Do NOT hardcode separately.

Architecture chain below remains accurate for how the `?category=` param works when used.

---

## Summary

Experiences submenu uses URL query params (`?category=X`) → server-side API filter on `/activities` page. Each submenu item routes to a distinct backend category, not a client-side UI filter.

## Context

Nav Phase 1 added an Experiences dropdown. Original navConfig had 4 of 7 children using the same `DAY_TOUR` href — placeholder that was never corrected. This ADR documents the final correct design and the full verified chain.

## Decision

Submenu items in Experiences dropdown each map to a **distinct `service_category` value** from the backend enum. The URL param approach (not client-side filtering) was chosen because activities inventory is dynamic and paginated — client-side filtering would require fetching all records first.

## Architecture Chain

```
Nav submenu click
  → /activities?category=FOOD_DINING
  → pages/activities/index.js:14
      const { category } = router.query
  → FilterDayTripsPage.js:24-36
      useEffect → updateFilter('category', initialCategory)
  → dayTripsApi.js:52-62
      RTK Query → /api/v1/contract/?service_category=FOOD_DINING
  → operators/views.py:237-241
      queryset.filter(service_category__in=category_list)
  → filtered results rendered
```

## Backend Category Enum

`operators/models.py:296-307` — full valid values:

| Value | Display |
|-------|---------|
| `DAY_TOUR` | Day Tour |
| `MULTI_DAY_TOUR` | Multi-Day Tour |
| `SPA_WELLNESS` | Spa & Wellness |
| `EVENT_TICKET` | Event Ticket |
| `ATTRACTION_TICKET` | Attraction Ticket |
| `FOOD_DINING` | Food & Dining |
| `ACCOMMODATION` | Accommodation |
| `TRANSFER` | Transfer Service |
| `TRANSPORTATION` | Transportation |
| `OTHER` | Other |

API also accepts comma-separated: `?service_category=DAY_TOUR,MULTI_DAY_TOUR`

## Current navConfig (static fallback)

`constants/navConfig.js` — 7 distinct children as of 2026-05-25:

```js
{ label: 'Food & Night Markets', href: '/activities?category=FOOD_DINING' },
{ label: 'Day Tours',            href: '/activities?category=DAY_TOUR' },
{ label: 'Multi-Day Tours',      href: '/activities?category=MULTI_DAY_TOUR' },
{ label: 'Culture & Temples',    href: '/activities?category=ATTRACTION_TICKET' },
{ label: 'Events & Tickets',     href: '/activities?category=EVENT_TICKET' },
{ label: 'Wellness',             href: '/activities?category=SPA_WELLNESS' },
{ label: 'Accommodation',        href: '/activities?category=ACCOMMODATION' },
```

## Contrast: Destinations Page

`/destinations?filter=islands` uses **client-side filtering** — all locations loaded via `getStaticProps`, `router.query.filter` → `setSearchTerm` → local filter. Correct for static location data. Activities must use server-side because inventory is dynamic + paginated.

## Phase 3 — Backend Nav Data

When `NavigationSection` + `NavigationItem` table is populated in Django admin, the RTK Query endpoint `/api/v1/pages-info/navigation/` replaces the static `navConfig.js` fallback. `NavigationItem.href` stores the full URL string including `?category=` param — admin must enter correct hrefs.

## Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| URL param → server filter (chosen) | Works with pagination, no over-fetch | Extra API call per nav click |
| Client-side filter | No API call | Requires loading all activities first |
| Separate pages per category | Perfect SEO URLs | 10+ new pages to maintain |

## Related

- [[nav-header-redesign]] — nav phases + implementation history
- [[daytrips-to-activities-rename-2026-05-23]] — URL rename history, category param confirmed working
