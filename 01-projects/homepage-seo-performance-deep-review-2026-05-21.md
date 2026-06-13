---
name: homepage-seo-performance-deep-review-2026-05-21
description: 3-specialist SEO + performance deep audit. Structured data errors, Technical SEO gaps, Core Web Vitals risks. Leader synthesis with priority fix queue.
metadata:
  type: project
  reviewed_by: seo-homepage-auditor
  date: 2026-05-21
  page: http://localhost:3000
---

# Homepage SEO & Performance Deep Review — 2026-05-21

## Summary
30 findings: 3 critical, 11 major, 14 minor, 2 info. Most critical: create `pages/server-sitemap.xml.js` — active 404 referenced in `robots.txt` + `next-sitemap.config.js`, suppresses dynamic trip route indexing.

## Context
SmartEnPlus homepage (`pages/homepagev2.js`). ISR 60s. Specialists: Structured Data + Technical SEO + Performance + Leader.

## Specialist A: Structured Data (11 findings)

**SD1 — TravelAgency telephone hardcoded fake** | Critical | `homepagev2.js:295`
`"telephone": "+66-2-123-4567"`. Real: `COMPANY_PHONE_NUMBER = '+66-61-465-5695'` at `helpers/constants.js:63`. Fix: import constant.

**SD2 — TravelAgency streetAddress placeholder** | Critical | `homepagev2.js:297-302`
`"streetAddress": "123 Sukhumvit Road"`, `"postalCode": "10110"`. No address constant. False address risks manual action. Fix: add `COMPANY_ADDRESS` constant.

**SD3 — TravelAgency aggregateRating hardcoded** | Major | `homepagev2.js:310-314`
`"ratingValue": "4.5"`, `"reviewCount": "128"` literals. `lastTopReviewData.average_rating` + `review_count` available. Fix: pass into schema.

**SD4 — TravelAgency sameAs missing** | Major | `homepagev2.js:286-318`
No `sameAs` array. `FACEBOOK_URL`, `INSTAGRAM_URL`, `X_URL` in constants not imported. Fix: import and add.

**SD5 — TravelAgency logo missing** | Minor | `homepagev2.js:286-318`
No `logo` property. Fix: add `"logo": { "@type": "ImageObject", "url": "https://smartenplus.co.th/smartenplus.png" }`.

**SD6 — WebPageJsonLd lastReviewed 2 years stale** | Major | `homepagev2.js:278`
`lastReviewed="2024-05-26..."`. ISR 60s. Fix: `new Date().toISOString()`.

**SD7 — WebSite + SearchAction schema missing** | Major | `homepagev2.js`
Required for Sitelinks Search Box. Fix: add WebSite with `potentialAction: { "@type": "SearchAction", "target": "https://smartenplus.co.th/trips/{from}/{to}?date={date}" }`.

**SD8 — LocationsStructuredData GeoCoordinates malformed** | Minor | `LocationsStructuredData.js:51-53`
`"geo": { "@type": "GeoCoordinates", "addressCountry": "TH" }`. Invalid on GeoCoordinates. Fix: add lat/lng or remove.

**SD9 — PopularRoutesStructuredData Trip missing temporal data** | Minor | `PopularRoutesStructuredData.js:22-65`
No `departureTime`/`arrivalTime`. Recommended for travel rich results. Fix: map from API if available.

**SD10 — FAQPage schema missing** | Minor | `homepagev2.js:493-495`
WordPress `helpSubcategories` fetched, never converted to FAQPage schema. Fix: add FAQPage mapping.

**SD11 — TravelAgency contactPoint missing** | Minor | `homepagev2.js:286-318`
Enables ContactPage rich results. Fix: add `contactPoint` with phone, support type, languages.

## Specialist B: Technical SEO (10 findings)

**TS1 — No DefaultSeo in _app.js** | Major | `_app.js`
Only viewport + GSC meta. No `<DefaultSeo>` fallback. Pages without `<NextSeo>` get zero metadata. Fix: add `<DefaultSeo>`.

**TS2 — _document.js missing preconnect/dns-prefetch** | Major | `_document.js:1-26`
Bare skeleton. GTM, both S3 buckets, API domain missing hints. Fix: add `<link rel="preconnect" href="https://www.googletagmanager.com" />`, S3 DNS prefetch.

**TS3 — og:site_name missing** | Minor | `Seo.js:31-44`
`openGraph` missing `siteName`. Fix: `siteName: siteName`.

**TS4 — og:locale missing** | Minor | `Seo.js:31-44`
Thai market requires `th_TH`. Fix: `locale: 'th_TH'`.

**TS5 — twitter:site handle missing** | Minor | `Seo.js:45-50`
No `site` handle. Fix: `site: '@smartenplus'`.

**TS6 — server-sitemap.xml active 404** | Critical | `next-sitemap.config.js:12`, `robots.txt:17`
Referenced but file missing. Googlebot 404s, GSC error, suppresses crawl. Fix (hotfix): remove refs. Fix (proper): create `pages/server-sitemap.xml.js`.

**TS7 — robots.txt duplicate User-agent blocks** | Major | `robots.txt:1-9`
Two `User-agent: *` blocks. RFC 9309 parsers use first match only. Fix: merge into one.

**TS8 — Missing HSTS, CSP, Permissions-Policy** | Major | `next.config.js:84-113`
Only `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`. Fix: add `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`.

**TS9 — domainURL canonical may include query string** | Minor | `useHomeSeoData.js:13`
`router.asPath` includes UTM params. Fix: use `router.pathname`.

**TS10 — og:image uses build-hash-dependent path** | Minor | `Seo.js:8-9`
`bgDefault.src` = `/_next/static/media/...hash....webp`. Hash changes per build. Fix: move to `/public/og-image.jpg`.

## Specialist C: Performance (9 findings)

**PP1 — DynamicProductSearchForm ssr:false CLS** | Major | `homepagev2.js:145-152,350`
`md:min-h-0` collapses to 0 during JS load. Spinner 64px ≠ final 104px. CLS every desktop cold load. Fix: `md:min-h-[104px]`.

**PP2 — Hero banner hard-swap, no crossfade** | Major | `homepagev2.js:181-187`
`setInterval` 5000ms changes imgUrl. No opacity transition = visible flash. Fix: add `transition-opacity duration-500` + opacity state.

**PP3 — generateBlurDataURL ignores imageUrl** | Minor | `imageOptimization.js:12-17`
Always returns brand-blue SVG. Fix: rename to `generateColorPlaceholder()`, or implement LQIP.

**PP4 — No preconnect for GTM or S3** | Major | `_document.js:1-26`
Zero resource hints. Cold-load penalty ~300–600ms on 4G. Same as TS2. Fix: add preconnect/dns-prefetch.

**PP5 — Next.js 14.2.5 fetchpriority="high" correct** | Info | `package.json:53`
No action needed.

**PP6 — Hero sizes missing 640px breakpoint** | Minor | `imageOptimization.js:27`
Missing iPhone landscape. Fix: add `(max-width: 640px) 100vw,`.

**PP7 — colorthief dynamic import correct** | Minor | `FeaturedImageHeader.js:58-78`
Non-blocking, correct. No fix needed.

**PP8 — minimumCacheTTL/compress/standalone correct** | Info | `next.config.js`
No action needed.

**PP9 — getOptimalImageQuality SSR/CSR mismatch** | Minor | `imageOptimization.js:62-87`
Returns 85 SSR vs 75 on 3G = different image URL. Fix: fixed `quality={85}` for hero; use for CSR-only below-fold.

**PP10 — No preload for actual LCP image** | Major | `homepagev2.js:265-328`
`priority={true}` preloads SSR fallback only. Real LCP = `heroBannerImage` from S3. No `<link rel="preload">` emitted. Fix: extract first banner URL in `getStaticProps`, add preload link.

## Priority Fix Queue

**P0 — Correctness (breaks rich results / active 404)**
1. SD1: Replace fake phone with `COMPANY_PHONE_NUMBER` in `homepagev2.js:295`
2. SD2: Add `COMPANY_ADDRESS` constant; replace placeholder in `homepagev2.js:297-302`
3. TS6: Remove `server-sitemap.xml` refs (hotfix), then create `pages/server-sitemap.xml.js`

**P1 — Coverage gaps (missing rich results)**
4. SD3: Wire TravelAgency `aggregateRating` to `lastTopReviewData`
5. SD4: Add `sameAs: [FACEBOOK_URL, INSTAGRAM_URL, X_URL]`
6. SD6: Replace hardcoded `lastReviewed` with `new Date().toISOString()`
7. SD7: Add WebSite + SearchAction schema
8. TS1: Add `<DefaultSeo>` to `_app.js`
9. TS3/4/5: Add `siteName`, `locale: 'th_TH'`, `site: '@smartenplus'` to openGraph

**P2 — Performance (Core Web Vitals)**
10. PP10: Add `<link rel="preload">` for first CMS hero banner
11. PP1: `md:min-h-0` → `md:min-h-[104px]`
12. PP2: Add CSS crossfade to hero banner swap
13. TS2/PP4: Add preconnect/dns-prefetch for GTM + S3

**P3 — Completeness**
14. TS7: Merge duplicate `User-agent: *` blocks in `robots.txt`
15. TS8: Add `Strict-Transport-Security` to `next.config.js`
16. TS9: `router.asPath` → `router.pathname` in `useHomeSeoData.js:13`
17. TS10: Move og:image to `/public/og-image.jpg`
18. SD8: Fix `LocationsStructuredData` geo — remove invalid `addressCountry`
19. SD5: Add `logo` ImageObject
20. SD11: Add `contactPoint`
21. PP9: Fixed `quality={85}` for hero

**P4 — Future**
22. SD9: Add `departureTime`/`arrivalTime` to PopularRoutes if API provides
23. SD10: Generate FAQPage schema from `subcategoriesData`
24. PP3: Rename `generateBlurDataURL` → `generateColorPlaceholder` or implement LQIP
25. PP6: Add 640px breakpoint to hero sizes

## Key Files
`pages/homepagev2.js`, `helpers/constants.js`, `components/FrontPage/Seo.js`, `pages/_app.js`, `pages/_document.js`, `next-sitemap.config.js`, `public/robots.txt`, `pages/server-sitemap.xml.js`, `components/UI/FeaturedImageHeader.js`, `lib/homepage/hooks/useHomeSeoData.js`, `lib/homepage/components/LocationsStructuredData.js`, `next.config.js`, `helpers/imageOptimization.js`

## Related
[[homepage-ux-review-2026-05-21]] · [[blog-seo-performance-2026-05-20]] · [[seo-homepage-specialist-team]]

## Related Atoms (Extracted 2026-06-13)
- [[defaultseo-fallback-pattern]] — `<DefaultSeo>` config in `_app.js`
- [[hero-cls-precise-sizes-attribute]] — `LocationGridComponent.js:59` `next/image` `sizes` per breakpoint
