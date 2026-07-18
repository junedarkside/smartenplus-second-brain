# Trips Index Page Redesign

## Summary
`/trips` index redesigned from plain-text route list → image-forward card grid, parity with destinations/locations pages. Branch `feat/trips-page-redesign` commit `db5982be`.

## Context
Destinations (`354889f1`) and locations (`4b549d91`) were redesigned first. Trips was the last index page still showing gray text boxes with no images, no search, no sticky filter bar, no structured data.

## What Changed

### Files created
| File | Purpose |
|---|---|
| `components/trips/RouteCard.js` | Image-forward card: `departure → arrival` text, gradient overlay, `TouristTrip` itemScope, 59 lines |
| `hooks/useTripsFiltering.js` | Memoised search + sort against `"from to"` joined string, 41 lines |
| `hooks/useTripsStructuredData.js` | SEO obj + `ItemList` of `TouristTrip` + `BreadcrumbList` + `CollectionPage` with `speakable`, 98 lines |

### `pages/trips/index.js` — rewritten (733 → 162 lines)
- `getServerSideProps` → `getStaticProps` + `revalidate: 3600`, fetches all routes `page_size=1000`
- `PageSeo` replaces raw `NextSeo`
- Reuses `components/locations/{SearchBar, FilterControls, StatsDisplay, EmptyState}` unchanged
- Removes: letter pills, MUI Pagination, `useMediaQuery`, `FavoriteBorderOutlinedIcon`, all SSR pagination logic

## SEO Additions (FE-only)
- `ItemList` of `TouristTrip` JSON-LD via `PageSeo`
- `BreadcrumbList` + `CollectionPage` + `Organization` schemas
- `speakable: { cssSelector: ['h1[data-speakable]'] }` on `CollectionPage` — AEO gain
- `<link rel="alternate" hrefLang="en">` + `hrefLang="x-default"` in `<Head>` — first page in codebase with hreflang

## Projected SEO Scores
Before: SEO ~4–5 / AEO ~3 / GEO ~3  
After: SEO ~8.5 / AEO ~8.5 / GEO ~7.0

Ceiling (9+) requires BE price field in `/admin-dashboard-routes/home/` + route listing pages SSR fix — separate sessions.

## Decision: Reuse locations components unchanged
`FilterControls`, `SearchBar`, `StatsDisplay`, `EmptyState` imported from `components/locations/` as-is. No modification. Rationale: identical UX need, zero side-effect risk. Only `RouteCard` is new (route pair shape differs from location shape).

## Decision: getStaticProps over getServerSideProps
Routes don't change per-request. ISR `revalidate:3600` = CDN-cached HTML, faster Googlebot crawl, matches destinations/locations pattern. Old code had a commented-out `getStaticProps` implementation (lines 227–288) — reactivated with the `page_size=1000` pagination loop.

## Key Gotcha: detail/index.js re-export
`pages/trips/detail/index.js` re-exports `pages/trips/index.js` default. When `allRoutes` is `undefined` (no `getStaticProps` on that route), `useMemo` spread `[...allRoutes]` throws `TypeError`. Fixed: `allRoutes = []` default in component destructure + `allRoutes || []` guards in both hooks.

## Scale Fix (2026-07-19, `perf/trips-index-scale` `f3e0e7fc`)

Prod count verified live: **297 routes** (dev has 8), growing toward 1000+. Three bottlenecks fixed FE-only:

1. **Slim payload** — `getStaticProps` maps nested API objects → `{id, from, to, image, price}` (~147B/route incl. S3 URL vs ~1KB+ nested). 1000 routes ≈ 150KB vs ~1MB. `RouteCard` + both hooks consume slim shape directly.
2. **Progressive reveal** — render 24 cards, IntersectionObserver sentinel (`rootMargin: 400px`) auto-loads +24. `visibleCount` reset to 24 inside search/sort handlers (no effect chain). "Showing X of Y routes" below grid.
3. **JSON-LD cap** — `itemListElements` + `keywords` sliced to top 100 (`SCHEMA_ITEM_CAP`). Full list bloats HTML, no SEO gain past top entries.

Rejected as over-engineering at this scale: react-window virtualization, server-side search, RTK Query client fetch. Client `useMemo` filter over 1000 slim objects is fast.

**Image fix (`316a284a`):** API has `image` on location objects, not route. Resolution: arrival location image → departure location image → `default-route.webp`. Resolved in `getStaticProps` (not component).

## Status
**MERGED → develop `24e3104b` (redesign `bffb532f` + scale fix). Both branches pushed.**

Remaining:
1. QA at `localhost:3000/trips` — cards + S3 images, search, sort, progressive reveal on scroll, empty state, JSON-LD ≤100 items in devtools
2. Mobile QA: 375/768/1280
3. Prod deploy (develop → main flow) — remember ISR cache: deploy script must clear `smartenplus_next_cache` volume

## Related
[[destinations-page-redesign]] · [[locations-page-redesign (master-state)]] · [[nextseo-v6-jsonld-silent-drop]]
