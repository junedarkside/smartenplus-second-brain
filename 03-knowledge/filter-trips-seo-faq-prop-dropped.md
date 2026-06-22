# FilterTripsSEO FAQPage Prop Silently Dropped

## Summary
`FilterTripsSEO.js` accepts `faqMainEntity` prop in JSDoc and destructuring but the JSX render block never emits a FAQPage schema. Route listing pages have zero structured data in production HTML despite the infrastructure appearing to be wired.

## Problem
`components/trips/search/FilterTripsSEO.js` lines 41–55:
- JSDoc at line 14 documents `faqMainEntity` prop
- Prop is destructured at line 25
- JSX render block (lines 41–55) has no `<FAQPageJsonLd>` or `<JsonLd schema={...}>` output
- The `faqMainEntity` prop is silently discarded

Additionally, even if the render block is fixed, the data source is `useRouteSeo` — a client-side hook. For FAQPage to appear in SSR HTML (required for rich results and AI engine extraction), the FAQ data must be moved from the hook into `getStaticProps` on the trips page.

## Fix

**Step 1** — Add render in `FilterTripsSEO.js`:
```jsx
import { FAQPageJsonLd } from 'next-seo'
// in JSX:
{faqMainEntity?.length > 0 && <FAQPageJsonLd mainEntity={faqMainEntity} />}
```

**Step 2** — Move FAQ data generation from `useRouteSeo` hook into `getStaticProps` in the trips page so schema appears in SSR HTML.

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
