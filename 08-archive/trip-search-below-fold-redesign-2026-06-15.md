# Trip Search Below-Fold Redesign — 2026-06-15

## Summary
Full redesign of the below-fold sections on `/trips/[from]/[to]` (TripOverview, RouteSummary, RouteFAQ new, TripSummary). Merged to `develop` @ `6f2ada9`.

## Context
Competitors (12Go, Bookaway, Rome2Rio, Lomprayah) all have richer below-fold sections. SmartEnPlus had: a 5-row client-side stats table (zero SEO), a trip overview with no right-column value, no FAQ section, and a TripSummary with no prices.

## Changes

### RouteFAQ.js (NEW — `components/trips/RouteFAQ.js`)
- 6 dynamic FAQ Q&A auto-generated from `tripsFilterSet` + `contracts[]`
- `<details>/<summary>` native accordion — zero JS, zero state, zero MUI
- FAQPage JSON-LD schema injected via `<Head>`
- Questions: cheapest way (+ cheapest operator name), journey duration, operators (list names), transport types (new — replaced last-departure Q), first departure, direct route
- Operator names: `[...new Set(contracts.map(c => c.operator?.operator_name))]`
- Cheapest operator: sort by min ratecard rate, take `[0].operator_name`
- Transport types: `[...new Set(contracts.map(c => c.type))]`
- Dynamic only — no WordPress, no backend changes

### RouteSummary.js (REWRITE — `components/trips/RouteSummary.js`)
- Removed 5-row client-side stats table (Number of Operators / Price Range / Duration / Earliest / Latest)
- All 5 MUI icon imports dropped, useCurrency / formatCurrency / formatSeconds / customFormatTime removed
- Replaced with ISR-rendered transport type chips + operator name list from `contracts[]`
- Chips: `bg-blue-50 text-blue-700 border border-blue-100 rounded-full`
- Decision: client-side RTK stats = zero crawl value; ISR contracts = indexable

### TripOverview.js
- Swapped `tripsFilterSet` prop → `contracts` (no longer needs tripsFilterSet)
- Passes `contracts` down to `<RouteSummary>`

### TripSummary.js
- Added min price per TripItem: `from THB {price}` right-aligned, blue, semibold
- Price source: `data[0].avaliable_routes[].ratecard[]` matched by slug
- Filter: `rate_date === null && (ratecard === 'ADULT' || ratecard === 'VEHICLE') && selling_rate > 0`
- Bug fixed: `ExteaContractSerializer` (used for `contracts[]`) has no `ratecard` field — `item.ratecard` was always `undefined`. Must use `avaliable_routes[]` + slug match.
- Added JSON-LD `ItemList` schema per contract: `Product` with `Offer` (price, THB, InStock)
- Schema injected via `<Head>` — eligible for Google rich results on travel queries

### FilterTripsPage.js
- Wired `contracts={contracts}` to `<DynamicRouteFAQ>`, `<DynamicTripOverview>`, `<DynamicTripSummary>`
- Wired `data={data}` to `<DynamicTripSummary>`
- Removed `tripsFilterSet` from `<DynamicTripOverview>` (no longer consumed)

## Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| FAQ data source | Dynamic only (`tripsFilterSet` + `contracts[]`) | No WordPress, no admin work, auto-generates per route |
| RouteSummary content | ISR contracts instead of RTK stats | RTK stats = zero crawl value; contracts indexable |
| TripSummary price source | `avaliable_routes[].ratecard[]` not `contracts[].ratecard` | ExteaContractSerializer has no ratecard field |
| Price filter | `rate_date=null` only | Show stable year-round baseline, not holiday overrides |
| FAQ accordion | `<details>/<summary>` | Zero JS, zero state, zero MUI, crawlable |

## Commits
- `9204379` — initial below-fold cleanup + RouteFAQ + FAQPage schema
- `01b8d5d` — enrich with ISR route data + ItemList schema + price fix
- `6f2ada9` — merge to develop

## Related
- [[extea-contract-serializer-no-ratecard]]
- [[isr-client-rtk-stats-seo-pattern]]
- [[wordpress-faqpage-deprecation-note]]
- [[trip-search-results-redesign-2026-06-14]]
