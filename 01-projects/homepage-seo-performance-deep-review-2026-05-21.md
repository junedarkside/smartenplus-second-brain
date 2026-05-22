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
30 findings across 3 specialists (11 SD, 10 TS, 9 PP): 3 critical, 11 major, 14 minor, 2 info. Most critical: create `pages/server-sitemap.xml.js` — absence causes active 404 referenced in `robots.txt` + `next-sitemap.config.js`, suppressing dynamic trip route indexing.

## Context
SmartEnPlus homepage (`pages/homepagev2.js`). ISR revalidate=60s. Team: Structured Data + Technical SEO + Performance auditors + Leader. Audited 2026-05-21.

---

## Specialist A: Structured Data Audit

### Methodology
Files: `pages/homepagev2.js` (275–395), `lib/homepage/components/PopularRoutesStructuredData.js`, `lib/homepage/components/LocationsStructuredData.js`, `lib/homepage/components/ReviewsStructuredData.js`, `lib/homepage/components/BlogPostStructuredData.js`, `lib/homepage/components/ReviewsSection.js`, `helpers/constants.js`.

Schemas: WebPage (WebPageJsonLd), TravelAgency (raw script), BreadcrumbList (BreadcrumbJsonLd), ItemList/Trip (PopularRoutes), ItemList/TouristDestination (Locations), LocalBusiness+Review+AggregateRating (Reviews), ItemList/BlogPosting (BlogPost).

### Findings

**SD1 — TravelAgency telephone hardcoded fake** | Critical | `pages/homepagev2.js:295`
`"telephone": "+66-2-123-4567"`. Real: `COMPANY_PHONE_NUMBER = '+66-61-465-5695'` at `helpers/constants.js:63`. Google rejects mismatched contact.
Fix: Import `COMPANY_PHONE_NUMBER`, replace literal.

**SD2 — TravelAgency streetAddress placeholder** | Critical | `pages/homepagev2.js:297-302`
`"streetAddress": "123 Sukhumvit Road"`, `"postalCode": "10110"`. No address constant in `helpers/constants.js`. False address risks manual action.
Fix: Add `COMPANY_ADDRESS` constant, reference in schema.

**SD3 — TravelAgency aggregateRating hardcoded, live data available** | Major | `pages/homepagev2.js:310-314`
`"ratingValue": "4.5"`, `"reviewCount": "128"` are literals. `lastTopReviewData.average_rating` + `review_count` already in `getStaticProps`. `ReviewsStructuredData` uses live data; TravelAgency block does not.
Fix: Pass `lastTopReviewData` into inline schema.

**SD4 — TravelAgency sameAs missing** | Major | `pages/homepagev2.js:286-318`
No `sameAs` array. `FACEBOOK_URL`, `INSTAGRAM_URL`, `X_URL` in `helpers/constants.js:60-62` not imported.
Fix: Import constants, add `"sameAs": [FACEBOOK_URL, INSTAGRAM_URL, X_URL]`.

**SD5 — TravelAgency logo missing** | Minor | `pages/homepagev2.js:286-318`
No `logo` property. Assets exist in constants.
Fix: Add `"logo": { "@type": "ImageObject", "url": "https://smartenplus.co.th/smartenplus.png" }`.

**SD6 — WebPageJsonLd lastReviewed 2 years stale** | Major | `pages/homepagev2.js:278`
`lastReviewed="2024-05-26T05:59:02.085Z"`. ISR revalidates every 60s.
Fix: Replace with `new Date().toISOString()`.

**SD7 — WebSite + SearchAction schema missing** | Major | `pages/homepagev2.js`
No `WebSite` schema. Required for Sitelinks Search Box. Trip search (`/trips/{from}/{to}?date=`) maps to `SearchAction`.
Fix: Add WebSite schema with `potentialAction: { "@type": "SearchAction", "target": "https://smartenplus.co.th/trips/{from}/{to}?date={date}", "query-input": "required name=from" }`.

**SD8 — LocationsStructuredData GeoCoordinates missing lat/lng** | Minor | `lib/homepage/components/LocationsStructuredData.js:51-53`
`"geo": { "@type": "GeoCoordinates", "addressCountry": "TH" }`. `addressCountry` invalid on `GeoCoordinates`; needs `latitude`/`longitude`.
Fix: Add lat/lng from API, or remove malformed `geo` block.

**SD9 — PopularRoutesStructuredData Trip missing departureTime/arrivalTime** | Minor | `lib/homepage/components/PopularRoutesStructuredData.js:22-65`
Trip items have location but no temporal data. Recommended for travel rich results.
Fix: Map from API schedule data if available; else omit.

**SD10 — subcategoriesData fetched, no FAQPage schema** | Minor | `pages/homepagev2.js:493-495`
WordPress `helpSubcategories` fetched + rendered in `CustomerServiceSection`, never converted to `FAQPage` schema. FAQ schema captures featured snippets.
Fix: Add FAQPage schema mapping `subcategoriesData` Q&A pairs.

**SD11 — TravelAgency contactPoint missing** | Minor | `pages/homepagev2.js:286-318`
No `contactPoint`. Enables ContactPage rich results.
Fix: Add `contactPoint` with `COMPANY_PHONE_NUMBER`, `contactType: "customer support"`, `availableLanguage: ["Thai", "English"]`.

---

## Specialist B: Technical SEO Audit

### Methodology
Files: `pages/_app.js`, `pages/_document.js`, `components/FrontPage/Seo.js`, `next-sitemap.config.js`, `next.config.js`, `lib/homepage/hooks/useHomeSeoData.js`, `public/robots.txt`, `pages/index.js`. Glob for `pages/server-sitemap.xml.js` = no results.

### Findings

**TS1 — No DefaultSeo in _app.js** | Major | `pages/_app.js`
`_app.js` has only viewport + GSC meta in `<Head>`. No `<DefaultSeo>` from next-seo. Pages without `<NextSeo>` get no title/description/OG.
Fix: Add `<DefaultSeo>` with fallback title, description, OG config.

**TS2 — _document.js missing preconnect/dns-prefetch** | Major | `pages/_document.js:1-26`
`_document.js` bare skeleton — `Html/Head/Main/NextScript` only. GTM, both S3 buckets, API domain missing resource hints.
Fix: Add `<link rel="preconnect" href="https://www.googletagmanager.com" />`, `<link rel="dns-prefetch" href="https://smartenplus-bucket.s3.amazonaws.com" />`, `<link rel="dns-prefetch" href="https://smartenplus-wp-s3.s3.us-west-2.amazonaws.com" />`.

**TS3 — og:site_name missing** | Minor | `components/FrontPage/Seo.js:31-44`
`openGraph` missing `siteName`. `siteName = "SmartEnPlus"` at `helpers/constants.js:30`.
Fix: Add `siteName: siteName` to `openGraph`.

**TS4 — og:locale missing** | Minor | `components/FrontPage/Seo.js:31-44`
No `locale` in openGraph. Thai market requires `th_TH`.
Fix: Add `locale: 'th_TH'` to openGraph.

**TS5 — twitter:site handle missing** | Minor | `components/FrontPage/Seo.js:45-50`
Twitter config has `cardType`/`title`/`description`, no `site`. Handle: `@smartenplus`.
Fix: Add `site: '@smartenplus'` to twitter config.

**TS6 — server-sitemap.xml referenced, does not exist (active 404)** | Critical | `next-sitemap.config.js:12`, `public/robots.txt:17`
`additionalSitemaps: ['https://www.smartenplus.co.th/server-sitemap.xml']` declared. `Sitemap: https://www.smartenplus.co.th/server-sitemap.xml` in robots.txt. Glob for `pages/server-sitemap.xml.js` = no files. Googlebot 404s, GSC sitemap error, suppresses crawl credits for dynamic trip routes.
Fix (hotfix): Remove reference from `next-sitemap.config.js` + `robots.txt`.
Fix (proper): Create `pages/server-sitemap.xml.js` using `getServerSideSitemap` fetching live trip routes.

**TS7 — robots.txt duplicate User-agent blocks** | Major | `public/robots.txt:1-9`
Two `User-agent: *` blocks. RFC 9309 parsers use first match only — second `Allow: /` ignored by strict parsers.
Fix: Merge into one `User-agent: *` group.

**TS8 — Missing HSTS, CSP, Permissions-Policy** | Major | `next.config.js:84-113`
`headers()` sets only `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`. HSTS/CSP/Permissions-Policy absent.
Fix: Add `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` minimum.

**TS9 — domainURL canonical may include query string** | Minor | `lib/homepage/hooks/useHomeSeoData.js:13`
`domainURL = \`${aboutURL}${router.asPath}\``. UTM params on `asPath` produce query string in canonical — Google treats as different URL.
Fix: Use `router.pathname` instead of `router.asPath`.

**TS10 — og:image uses build-hash-dependent path** | Minor | `components/FrontPage/Seo.js:8-9`
`bgDefault.src` resolves to `/_next/static/media/...hash....webp`. Hash changes per build, breaks cached OG previews.
Fix: Move OG image to `/public/og-image.jpg`, reference as stable URL.

---

## Specialist C: Page Performance Audit

### Methodology
Files: `components/UI/FeaturedImageHeader.js`, `helpers/imageOptimization.js`, `pages/homepagev2.js` (86–155, 330–395), `next.config.js` (1–70), `package.json` (1–70).

### Findings

**PP1 — DynamicProductSearchForm ssr:false CLS on desktop** | Major | `pages/homepagev2.js:145-152`, `line 350`
Container line 350: `md:min-h-0 md:h-[104px]`. `md:min-h-0` collapses to 0 during JS load. Spinner `h-16` (64px) ≠ final `h-[104px]`. CLS every desktop cold load.
Fix: `md:min-h-0` → `md:min-h-[104px]`.

**PP2 — Hero banner setInterval hard-swaps, no crossfade** | Major | `pages/homepagev2.js:181-187`
`setInterval` 5000ms increments `heroBannerIndex`, changes `imgUrl` on `MemoizedImage`. No opacity transition = visible flash. Different banner dimensions = CLS risk.
Fix: Add `transition-opacity duration-500` + opacity state in `FeaturedImageHeader.js`.

**PP3 — generateBlurDataURL ignores imageUrl** | Minor | `helpers/imageOptimization.js:12-17`
`imageUrl` param ignored — always returns brand-blue SVG. Comment claims CLS prevention but function is just a color placeholder.
Fix: Rename to `generateColorPlaceholder()`, or implement real LQIP.

**PP4 — No preconnect for GTM or S3** | Major | `pages/_document.js:1-26`
Zero resource hints. S3 hero images need DNS + TLS on cold load. GTM = script dependency. Cold-load penalty ~300–600ms on 4G. Same as TS2.
Fix: Add preconnect/dns-prefetch in `_document.js`.

**PP5 — Next.js 14.2.5 fetchpriority="high" correct** | Info | `package.json:53`
`"next": "^14.2.5"`. `MemoizedImage` `priority={true}` at `FeaturedImageHeader.js:24`. No action needed.

**PP6 — Hero sizes missing 640px breakpoint** | Minor | `helpers/imageOptimization.js:27`
`'(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px'`. Missing 640px (iPhone landscape). Functionally correct, semantically incomplete.
Fix: Add `(max-width: 640px) 100vw,` prefix.

**PP7 — colorthief dynamic import + requestIdleCallback** | Minor | `components/UI/FeaturedImageHeader.js:58-78`
Dynamic `import('colorthief')` inside `requestIdleCallback` timeout 2000. Non-blocking, correct. `colorCache` Map works across navigations. No fix needed.

**PP8 — minimumCacheTTL/compress/standalone correct** | Info | `next.config.js:8,11,62`
`compress: true`, `output: 'standalone'`, `minimumCacheTTL: 86400`. No action needed.

**PP9 — getOptimalImageQuality SSR/CSR mismatch** | Minor | `helpers/imageOptimization.js:62-87`, `components/UI/FeaturedImageHeader.js:26`
Reads `navigator.connection` (client-only). Returns 85 SSR vs 75 on 3G — different `quality` = different image URL between SSR/CSR.
Fix: Fixed `quality={85}` for hero `MemoizedImage`; `getOptimalImageQuality()` for CSR-only below-fold.

**PP10 — No preload for actual LCP image (CMS hero)** | Major | `pages/homepagev2.js:265-328`
`priority={true}` preloads `bgDefault` (SSR fallback). Actual LCP = `heroBannerImage` from S3, set after hydration. No `<link rel="preload">` emitted. Browser fetches real LCP only after JS hydrates.
Fix: Extract first banner URL in `getStaticProps`, add `<link rel="preload" as="image" href={firstHeroBannerUrl} />` in SEO block.

---

## Discussion

**D1 — AggregateRating: hardcode vs live**
Live data already on page. `ReviewsStructuredData` does it right; TravelAgency block outdated.
**Verdict:** Wire it. Two prop reads. Hardcoded schema risks suppression on mismatch. Effort: trivial.

**D2 — server-sitemap.xml 404 priority**
Trip routes uncrawlable without dynamic sitemap. File confirmed missing, `robots.txt` ref live.
**Verdict:** P0. Hotfix (remove from `next-sitemap.config.js` + `robots.txt`) = 5 min, kills GSC error. Proper fix (`pages/server-sitemap.xml.js`) = sprint task.

**D3 — DefaultSeo: P0 or P1?**
Any new page without `<NextSeo>` = zero fallback metadata. Current pages all have explicit `<NextSeo>`.
**Verdict:** P1. No current page broken. One-line fix prevents future gaps.

**D4 — CLS from ssr:false form**
CLS = Core Web Vitals ranking signal.
**Verdict:** P2. One Tailwind class: `md:min-h-0` → `md:min-h-[104px]`. Effort: trivial.

**D5 — og:image vs LCP preload**
PP10 (LCP preload) + TS10 (og:image hash) = different images, different impact. LCP → ranking; og:image → social conversion.
**Verdict:** PP10 first (ranking). TS10 second (P3 conversion).

---

## Leader Synthesis

Homepage SEO substantially built — 7 schema types, ISR 60s, `priority={true}` correct, `next-seo` consistent. Critical failures in two areas: structured data accuracy (fake phone/address, stale ratings/dates) + infrastructure gap (`server-sitemap.xml` 404). Not architecture problems — maintenance gaps from adding components without updating inline TravelAgency schema.

Most critical: `server-sitemap.xml` 404. Googlebot logs as crawl budget waste. Trip routes = primary booking entry. Two-line hotfix (remove from `next-sitemap.config.js` + `robots.txt`) = 5 min. `server-sitemap.xml.js` build = sprint task. Pattern documented in `[[blog-seo-performance-2026-05-20]]`.

Fastest wins after P0: replace fake constants (SD1/SD2, 10 min), wire aggregateRating (SD3, 5 min), add sameAs (SD4, 5 min), add `og:site_name`/`og:locale`/`twitter:site` (TS3/TS4/TS5, 10 min). P1 total < 30 min. Performance fixes (PP1 CLS, PP10 LCP preload, PP4 preconnect) = single-component changes.

---

## Priority Fix Queue

**P0 — Correctness (breaks rich results / active 404)**
1. SD1: Replace `"+66-2-123-4567"` with `COMPANY_PHONE_NUMBER` in `homepagev2.js:295`
2. SD2: Add `COMPANY_ADDRESS` constant; replace `"123 Sukhumvit Road"` in `homepagev2.js:297-302`
3. TS6: Remove `server-sitemap.xml` from `next-sitemap.config.js:12` + `public/robots.txt:17` (hotfix), then create `pages/server-sitemap.xml.js`

**P1 — Coverage gaps (missing rich results)**
4. SD3: Wire TravelAgency `aggregateRating` to `lastTopReviewData` in `homepagev2.js:310-314`
5. SD4: Add `sameAs: [FACEBOOK_URL, INSTAGRAM_URL, X_URL]` to TravelAgency schema
6. SD6: Replace hardcoded `lastReviewed` with `new Date().toISOString()` in `homepagev2.js:278`
7. SD7: Add WebSite + SearchAction schema for Sitelinks Search Box
8. TS1: Add `<DefaultSeo>` to `pages/_app.js`
9. TS3: Add `siteName` to openGraph in `Seo.js`
10. TS4: Add `locale: 'th_TH'` to openGraph in `Seo.js`
11. TS5: Add `site: '@smartenplus'` to twitter config in `Seo.js`

**P2 — Performance (Core Web Vitals)**
12. PP10: Add `<link rel="preload">` for first CMS hero banner in SEO block
13. PP1: `md:min-h-0` → `md:min-h-[104px]` in `homepagev2.js:350`
14. PP2: Add CSS crossfade to hero banner swap in `FeaturedImageHeader.js`
15. TS2/PP4: Add preconnect/dns-prefetch for GTM + S3 in `pages/_document.js`

**P3 — Completeness (quality signals)**
16. TS7: Merge duplicate `User-agent: *` blocks in `public/robots.txt`
17. TS8: Add `Strict-Transport-Security` to `next.config.js`
18. TS9: `router.asPath` → `router.pathname` in `useHomeSeoData.js:13`
19. TS10: Move og:image to `/public/og-image.jpg` in `Seo.js`
20. SD8: Fix `LocationsStructuredData` geo — remove invalid `addressCountry`
21. SD5: Add `logo` ImageObject to TravelAgency schema
22. SD11: Add `contactPoint` to TravelAgency schema
23. PP9: Fixed `quality={85}` for hero; `getOptimalImageQuality()` for CSR-only

**P4 — Future**
24. SD9: Add `departureTime`/`arrivalTime` to PopularRoutesStructuredData if API provides
25. SD10: Generate FAQPage schema from `subcategoriesData`
26. PP3: Rename `generateBlurDataURL` → `generateColorPlaceholder` or implement LQIP
27. PP6: Add 640px breakpoint to hero sizes in `imageOptimization.js`

---

## Key Files
- `pages/homepagev2.js` — P0: 295, 297-302; P1: 278, 310-314, 286-318; P2: 350
- `helpers/constants.js` — P0: add `COMPANY_ADDRESS`; import `COMPANY_PHONE_NUMBER`, `FACEBOOK_URL`, `INSTAGRAM_URL`, `X_URL`
- `components/FrontPage/Seo.js` — P1: siteName/locale/twitter; P3: stable og:image
- `pages/_app.js` — P1: DefaultSeo
- `pages/_document.js` — P2: preconnect/dns-prefetch
- `next-sitemap.config.js` — P0: remove server-sitemap.xml
- `public/robots.txt` — P0: remove Sitemap line; P3: merge User-agent
- `pages/server-sitemap.xml.js` — P0: create (missing)
- `components/UI/FeaturedImageHeader.js` — P2: crossfade; P3: quality fix
- `lib/homepage/hooks/useHomeSeoData.js` — P3: line 13 `router.pathname`
- `lib/homepage/components/LocationsStructuredData.js` — P3: 51-53 fix geo
- `next.config.js` — P3: HSTS header
- `helpers/imageOptimization.js` — P4: rename generateBlurDataURL

## Related
- [[homepage-ux-review-2026-05-21]]
- [[blog-seo-performance-2026-05-20]]
- [[seo-homepage-specialist-team]]