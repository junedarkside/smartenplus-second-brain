# ISR vs Client-Side RTK Stats — SEO Pattern

## Summary
Client-side RTK Query data in below-fold page sections = zero crawl value. Googlebot only indexes the ISR HTML snapshot. Replace with ISR-rendered props from `getStaticProps`.

## Problem

`tripsFilterSet` data (from `useGetTripFilterSetQuery`) is fetched client-side at runtime:
- `min_rate`, `max_rate` — price range
- `min_duration`, `max_duration` — journey time
- `min_departure_time`, `max_departure_time` — schedule window
- `operator_list[]` — operator count
- `unique_transport_composit_list[]` — transport combos

Googlebot crawls the ISR HTML and sees empty `<td>` cells / blank spans. These fields never get indexed.

## Solution

Use ISR-rendered props from `getStaticProps`:
- `contracts[]` (from `ExteaContractSerializer`) — operator names, transport types, slugs, dates
- `data[0].avaliable_routes[]` (from `AvialableContractSerializer`) — same + ratecard prices

These are in the initial HTML. Googlebot indexes them.

## Applied Decision — RouteSummary

Old (client-side, zero SEO):
```
Number of Operators    2
Price range    THB 4,200 – THB 9,000
Ride Duration Range    ...
Earliest Departure    ...
Latest Departure    ...
```

New (ISR-rendered, indexable):
```
Transport    [VIP Bus]  [Ferry]  [Speedboat]
Operators    Lomprayah, Seatran Discovery
```

Derived from `contracts[]` via `[...new Set(contracts.map(c => c.type))]` and `[...new Set(contracts.map(c => c.operator?.operator_name))]`.

## Rule

> If a data field comes from a React hook or RTK Query (not getStaticProps), it is invisible to search engines on ISR pages. Do not use it as the primary content in below-fold sections.

## Related
- `components/trips/RouteSummary.js` — applied here
- `components/trips/TripSummary.js` — ISR price via `priceBySlug`
- [[extea-contract-serializer-no-ratecard]]
- [[isr-csr-overlay-stale-fields]]
