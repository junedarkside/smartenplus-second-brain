# trip-detail-server-side-seo-pattern

## Summary
Pattern for moving client-side SEO hook generation to server-side `getStaticProps` on transport trip-detail pages. Fixes AEO root cause (schema absent from crawled HTML) and removes hook complexity.

## Context
Transport trip-detail page (`/trips/detail/[...slug]`) originally generated all SEO in a client-side hook (`useTripSEO`), meaning schema was only present after React hydration — invisible to crawlers and answer engines. Day-trip pages already used the correct server-side pattern. This atom captures the reusable pattern for any transport product page.

## Pattern

### 1. Pure util file (no React, no hooks)
`helpers/seo/tripDetailSEOUtils.js` — 5 named exports:
- `generateTripSEOConfig({ productData, slug })` → NextSeo config (canonical, OG, hreflang, geo meta)
- `generateTripProductJsonLd({ productData })` → ProductJsonLd props (no empty `{}` offer keys)
- `generateTripJsonLd({ productData })` → **payload fields only** (no `@context`/`@type` — `CustomJsonLd` injects those)
- `generateTripBreadcrumbItems({ slug, productData })` → BreadcrumbJsonLd itemListElements
- `generateTripFAQItems({ productData })` → FAQPageJsonLd mainEntity (4 Q&A pairs from productData)

### 2. getStaticProps computes all SEO
```js
const seoProps = {
  seoConfig: generateTripSEOConfig({ productData, slug }),
  productJsonLd: generateTripProductJsonLd({ productData }),
  tripJsonLd: generateTripJsonLd({ productData }),
  breadcrumbItems: generateTripBreadcrumbItems({ slug, productData }),
  faqItems: generateTripFAQItems({ productData }),
};
return { props: { productData, seoProps }, revalidate: 300 };
```
No new fetch — `productData` already fetched at build/ISR time.

### 3. SEO component = thin renderer (no logic)
```jsx
const TripDetailSEO = ({ seoConfig, productJsonLd, breadcrumbItems, tripJsonLd, faqItems }) => (
  <>
    <NextSeo {...seoConfig} />
    <ProductJsonLd {...productJsonLd} />
    <BreadcrumbJsonLd itemListElements={breadcrumbItems} />
    {faqItems?.length > 0 && <FAQPageJsonLd mainEntity={faqItems} />}
    {tripJsonLd && <CustomJsonLd type="TouristTrip" {...tripJsonLd} />}
  </>
);
```

## Key rules
- `generateTripJsonLd` returns **payload only** — no `@context`/`@type`. `CustomJsonLd` (`helpers/JsonLd.js`) injects both from its `type` prop. Mixing them causes duplicate keys (last-value-wins in JSON.stringify but intent is muddled).
- `getSiteUrl()` (`utils/blog/seoHelper.js:3`) for all canonical/href values. Returns `NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'`. Does NOT force HTTPS/www — relies on prod env being correct.
- `findLowestSellingRate(productData)` (`helpers/tripSorting.js:74`) for ISR price. ≤5min stale (revalidate:300). Acceptable for schema price.
- hreflang: `['th', 'en', 'de', 'fr', 'en-SG', 'x-default']` + `og:locale:alternate: ['en_US','en_GB','de_DE','fr_FR','en_SG']`. All point at same canonical URL (signal-only, no i18n routing).
- `noindex`/`nofollow` NOT set in seoProps — the page's `lowestRate===null` early-return handles noindex before `TripDetailSEO` ever renders.

## Reference files
- `helpers/seo/tripDetailSEOUtils.js` — util (126 lines)
- `components/trips/detail/TripDetailSEO.js` — renderer (35 lines)
- `helpers/seo/dayTripSEOUtils.js` — original reference pattern
- `components/activities/detail/DayTripDetailSEO.js` — original reference component

## Related
[[trip-detail-seo-aeo-geo-audit-2026-06-16/r2-leader-synthesis]] · [[trip-detail-seo-aeo-geo-audit-2026-06-16/r3-implementation-plan]]
