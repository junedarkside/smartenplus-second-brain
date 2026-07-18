# Slim ISR Payload Pattern

## Summary
Trim nested API objects to card-shape fields inside `getStaticProps` before returning props — ~10x payload cut on index pages with 100+ items.

## Context
Next.js serializes `getStaticProps` props as JSON into every page's HTML (`__NEXT_DATA__`). Passing raw API responses through ships every nested field the UI never reads.

## Problem
`/trips` index: each route from `/admin-dashboard-routes/home/` carries nested `departure_station.location` + `arrival_station.location` objects (city, province, country, slugs) ≈ 1KB+/route. At 297 prod routes (growing to 1000+) that's 300KB–1MB of JSON baked into HTML.

## Details
Map to exactly what cards render, in `getStaticProps` (server-side, free):

```js
const allRoutes = allResults
  .map((r) => ({
    id: r.slug || null,
    from: r.departure_station?.location?.location_name || '',
    to: r.arrival_station?.location?.location_name || '',
    image: r.arrival_station?.location?.image || r.departure_station?.location?.image || null,
    price: r.lowest_price || null,
  }))
  .filter((r) => r.from && r.to);
```

Result: ~147B/route incl. S3 image URL → 1000 routes ≈ 150KB. Verified via `.next/server/pages/trips.json` size after build.

Side benefits: consuming components/hooks lose all nested optional chains; fallback logic (image resolution, null guards) runs once server-side instead of per-render.

## Tradeoffs
- Slim shape is a contract — adding a card field later means touching `getStaticProps` map too.
- Filter `!from || !to` server-side replaces per-component null-render guards.

## Related
[[trips-page-redesign]] · [[progressive-reveal-batch-pattern]]
