# SmartEnPlus: /locations vs /destinations Product Split

## Summary
`/locations` and `/destinations` are different products. Never consolidate, never cross-canonical.

## Context
Discovered during homepage terminology audit (2026-06-05). Phase 1 analysis incorrectly called these "duplicate content." Code investigation overturned this.

## Details

### /locations
- **Index** (`pages/locations/index.js`): Alphabetical city/station list. API: `/locations/?summary=true&has_trips=true`. Renders `LocationGridComponent`. SSG via `getStaticProps`.
- **Detail** (`pages/locations/[slug].js`): All transport routes **departing FROM** a city. API: `/admin-dashboard-stations/locationsv2/?location={slug}`. Renders route cards (departure station → arrival station). SSR via `getServerSideProps`.
- **User intent:** "What routes can I take FROM Bangkok?"

### /destinations
- **Index** (`pages/destinations/index.js`): Search + filter all stations with station counts. API: `/locations/?has_trips=true&destinations_page=true`. Renders `LocationCard` + `SearchBar` + `useLocationFiltering`. SSG via `getStaticProps`.
- **Detail** (`pages/destinations/[slug].js`): Trip booking interface TO a specific station. APIs: `/stationsinfo/{slug}` + `/trips/{from}/{to}/`. Renders `FilteredTripList` with prices/times. ISR via `getStaticProps` with blocking fallback.
- **User intent:** "I want to go TO Koh Samui — show me available trips."

## Why Both in Sitemap
`pages/server-sitemap.xml/index.js` generates paired entries for every station: both `/locations/{slug}` and `/destinations/{slug}`. Intentional — different pages, both indexable, both serve distinct queries.

## Rules
- ❌ Never add `canonical` from /locations pointing to /destinations (or vice versa)
- ❌ Never 301 redirect one to the other
- ❌ Never consolidate these two page trees
- ✅ Both nav items should exist with distinct labels (e.g. "Routes" for /locations, "Destinations" for /destinations)

## Tradeoffs
- **Pro:** Each page ranks for its own distinct query type
- **Pro:** Clear user journey: browse routes vs book a destination
- **Con:** Visual similarity of index pages may confuse casual users — mitigate with clear H1 differentiation

## Related
- [[production-url-rename-cost-framework]]
- [[nav-label-url-slug-two-layer-strategy]]
- [[homepage-terminology-audit-2026-06-05]]
