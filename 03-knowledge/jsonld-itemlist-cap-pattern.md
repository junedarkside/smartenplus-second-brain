# JSON-LD ItemList Cap Pattern

## Summary
Cap `ItemList.itemListElement` and `CollectionPage.keywords` at top ~100 entries — full-list JSON-LD bloats HTML with zero SEO gain past top entries.

## Context
Index pages (`/trips`, `/locations`, `/destinations`) emit `ItemList` JSON-LD for every listed item. At 1000+ items the `<script type="application/ld+json">` block alone adds hundreds of KB to HTML — hurting the site-wide HTML <100KB budget ([[core-web-vitals-budget]]) while search engines extract no additional value from tail entries.

## Details

```js
const SCHEMA_ITEM_CAP = 100;
const cappedRoutes = validRoutes.slice(0, SCHEMA_ITEM_CAP);

const itemListElements = cappedRoutes.map((route, index) => ({
  '@type': 'ListItem',
  position: index + 1,
  item: { '@type': 'TouristTrip', name: ..., url: ... },
}));

// keywords from same capped slice — a 1000-name comma string is pure bloat
keywords: cappedRoutes.map((r) => `${r.from} to ${r.to}`).join(', '),
```

Why 100: Google documents no ItemList size limit, but rich-result eligibility and entity extraction concentrate on top entries; the marginal entry costs HTML bytes on *every* page load for crawl-only value ≈ 0. Individual detail pages carry their own full schema — the index list is a discovery aid, not the canonical source.

Applies when list source order is meaningful (API popularity order) — cap keeps the *top* entries, so slice before any client-side alphabetical sort.

## Related
[[trips-page-redesign]] · [[core-web-vitals-budget]] · [[progressive-reveal-batch-pattern]]
