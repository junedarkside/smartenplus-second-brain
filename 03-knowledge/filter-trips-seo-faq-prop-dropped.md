# FilterTripsSEO FAQPage Prop Silently Dropped

## Summary
`FilterTripsSEO.js` accepts `faqMainEntity` prop in JSDoc and destructuring but the JSX render block never emits a FAQPage schema. Route listing pages have zero structured data in production HTML despite the infrastructure appearing to be wired.

## Problem (updated 2026-10-07)

Re-audit found the root cause evolved. The prop-not-rendered symptom was fixed at some point, but the schema still does not emit. Current root cause is **contradictory suppression logic**:

- `FilterTripsPage.js:235` — `faqMainEntity={contracts?.length > 0 ? null : faqMainEntity}` — **suppresses** the prop when trips exist, with a comment claiming RouteFAQ will emit it instead.
- `RouteFAQ.js:8` — comment explicitly says: "FAQPage schema is emitted by FilterTripsSEO (ISR SSR path) — not duplicated here." — so **RouteFAQ does not emit it**.

Result: every page with real trips passes `null` to FilterTripsSEO, and RouteFAQ opts out by design. Zero FAQPage JSON-LD on any live route page.

## Fix (2026-10-07)

1. Remove the `contracts?.length > 0 ? null :` suppression at `FilterTripsPage.js:235` — pass `faqMainEntity` unconditionally.
2. Ensure `faqMainEntity` is built from `buildRouteFAQItems()` output in `useRouteSeo.js` and returned as a separate value — the current `faqMainEntity` built from `faqPosts` (WordPress) is empty for routes with no WP posts. A complete fix computes a schema FAQ array from `buildRouteFAQItems` and passes it to `FilterTripsSEO` unconditionally.
3. Update the stale comment in `RouteFAQ.js:8`.

## History (original finding — 2026-06-22)

`components/trips/search/FilterTripsSEO.js` destructured `faqMainEntity` prop but JSX render block had no `<FAQPageJsonLd>` output — prop silently discarded. Additionally data source was `useRouteSeo` (client-side hook), not ISR. Both issues identified 2026-06-22.

## Detection
```bash
grep -n "faqMainEntity" components/trips/search/FilterTripsSEO.js
# Should show destructure but NO render/return usage
```

## Impact
- Route listing pages (all `/trips/*`) have zero JSON-LD in production HTML
- AEO score: 2/10 (was incorrectly scored 8.5/10 in live audit 2026-06-22)
- Live verified 2026-06-22 via WebFetch

## Related
[[trip-route-page-seo-aeo-geo-audit]] · [[seo-aeo-geo-live-audit-2026-06-22/r5-live-reaudit]] · [[isr-client-rtk-stats-seo-pattern]]
