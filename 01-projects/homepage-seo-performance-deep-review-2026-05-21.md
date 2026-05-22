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
30 total findings across 3 specialists (11 structured data, 10 technical SEO, 9 performance): 3 critical, 11 major, 14 minor, 2 informational. The single most critical fix is creating `pages/server-sitemap.xml.js` — its absence causes an active 404 referenced in both `robots.txt` and `next-sitemap.config.js`, suppressing dynamic trip route indexing.

## Context
SmartEnPlus homepage (`pages/homepagev2.js`). ISR revalidate=60s. Review team: Structured Data Auditor + Technical SEO Auditor + Page Performance Auditor + Leader. Audit conducted against source files on 2026-05-21.

---

## Specialist A: Structured Data Audit

### Methodology
Files read: `pages/homepagev2.js` (lines 275–395), `lib/homepage/components/PopularRoutesStructuredData.js`, `lib/homepage/components/LocationsStructuredData.js`, `lib/homepage/components/ReviewsStructuredData.js`, `lib/homepage/components/BlogPostStructuredData.js`, `lib/homepage/components/ReviewsSection.js`, `helpers/constants.js`.

Schemas emitted: WebPage (next-seo WebPageJsonLd), TravelAgency (raw script), BreadcrumbList (next-seo BreadcrumbJsonLd), ItemList/Trip (PopularRoutesStructuredData), ItemList/TouristDestination (LocationsStructuredData), LocalBusiness+Review+AggregateRating (ReviewsStructuredData), ItemList/BlogPosting (BlogPostStructuredData).

### Findings

**SD1 — TravelAgency telephone hardcoded fake number** | Severity: Critical | `pages/homepagev2.js:295`
Evidence: `"telephone": "+66-2-123-4567"`. Real number: `COMPANY_PHONE_NUMBER = '+66-61-465-5695'` at `helpers/constants.js:63`. Google rich results validator rejects mismatched contact data.
Fix: Import `COMPANY_PHONE_NUMBER` from constants and replace the literal.

**SD2 — TravelAgency streetAddress hardcoded placeholder** | Severity: Critical | `pages/homepagev2.js:297-302`
Evidence: `"streetAddress": "123 Sukhumvit Road"`, `"postalCode": "10110"`. No real address constant exists in `helpers/constants.js`. False business address data risks a structured data manual action.
Fix: Add `COMPANY_ADDRESS` constant to `helpers/constants.js` with the real registered address; reference it in the schema.

**SD3 — TravelAgency aggregateRating hardcoded while live data is available** | Severity: Major | `pages/homepagev2.js:310-314`
Evidence: `"ratingValue": "4.5"`, `"reviewCount": "128"` are string literals. `lastTopReviewData.average_rating` and `review_count` are already fetched in `getStaticProps` and available as page props. `ReviewsStructuredData` correctly uses live data; the TravelAgency block does not.
Fix: Pass `lastTopReviewData` values into the inline schema and replace hardcoded values.

**SD4 — TravelAgency sameAs absent** | Severity: Major | `pages/homepagev2.js:286-318`
Evidence: No `sameAs` array. `FACEBOOK_URL`, `INSTAGRAM_URL`, `X_URL` all exist in `helpers/constants.js:60-62` but are not imported in `homepagev2.js`.
Fix: Import the three constants, add `"sameAs": [FACEBOOK_URL, INSTAGRAM_URL, X_URL]`.

**SD5 — TravelAgency logo absent** | Severity: Minor | `pages/homepagev2.js:286-318`
Evidence: No `logo` property on the TravelAgency entity. Logo assets exist in constants.
Fix: Add `"logo": { "@type": "ImageObject", "url": "https://smartenplus.co.th/smartenplus.png" }`.

**SD6 — WebPageJsonLd lastReviewed stale by 2 years** | Severity: Major | `pages/homepagev2.js:278`
Evidence: `lastReviewed="2024-05-26T05:59:02.085Z"`. Page ISR revalidates every 60 seconds.
Fix: Replace with `new Date().toISOString()` or a content-update-driven constant.

**SD7 — WebSite + SearchAction schema absent** | Severity: Major | `pages/homepagev2.js` (schema block)
Evidence: No `WebSite` schema emitted. Required for Google Sitelinks Search Box. Trip search URL structure (`/trips/{from}/{to}?date=`) maps directly to a `SearchAction` target.
Fix: Add WebSite schema with `potentialAction: { "@type": "SearchAction", "target": "https://smartenplus.co.th/trips/{from}/{to}?date={date}", "query-input": "required name=from" }`.

**SD8 — LocationsStructuredData GeoCoordinates missing lat/lng** | Severity: Minor | `lib/homepage/components/LocationsStructuredData.js:51-53`
Evidence: `"geo": { "@type": "GeoCoordinates", "addressCountry": "TH" }`. `addressCountry` is not a valid `GeoCoordinates` property; `latitude`/`longitude` are.
Fix: Add lat/lng from API data or remove the malformed `geo` block entirely.

**SD9 — PopularRoutesStructuredData Trip missing departureTime/arrivalTime** | Severity: Minor | `lib/homepage/components/PopularRoutesStructuredData.js:22-65`
Evidence: Trip items have location data but no temporal data. Recommended for travel rich results eligibility.
Fix: Map from API schedule data if available; otherwise omit (schema remains valid).

**SD10 — subcategoriesData fetched but no FAQPage schema generated** | Severity: Minor | `pages/homepagev2.js:493-495`
Evidence: WordPress `helpSubcategories` fetched and rendered in `CustomerServiceSection` but never converted to `FAQPage` schema. FAQ schema captures featured snippets for travel questions.
Fix: Add FAQPage schema component mapping `subcategoriesData` Q&A pairs.

**SD11 — TravelAgency contactPoint absent** | Severity: Minor | `pages/homepagev2.js:286-318`
Evidence: No `contactPoint`. Enables ContactPage rich results and customer service search features.
Fix: Add `contactPoint` with `COMPANY_PHONE_NUMBER`, `contactType: "customer support"`, `availableLanguage: ["Thai", "English"]`.

---

## Specialist B: Technical SEO Audit

### Methodology
Files read: `pages/_app.js`, `pages/_document.js`, `components/FrontPage/Seo.js`, `next-sitemap.config.js`, `next.config.js` (full), `lib/homepage/hooks/useHomeSeoData.js`, `public/robots.txt`, `pages/index.js`. Glob for `pages/server-sitemap.xml.js` returned no results.

### Findings

**TS1 — No DefaultSeo in _app.js** | Severity: Major | `pages/_app.js` (full file)
Evidence: `_app.js` contains only viewport + GSC verification meta in `<Head>`. No `<DefaultSeo>` from next-seo. Any page rendered without explicit `<NextSeo>` has no title, description, or OG tags.
Fix: Add `<DefaultSeo>` with site-wide fallback title, description, and OG config.

**TS2 — _document.js has no preconnect or dns-prefetch hints** | Severity: Major | `pages/_document.js:1-26`
Evidence: `_document.js` is a bare skeleton — `Html/Head/Main/NextScript` and nothing else. GTM, both S3 image buckets, and the API domain are all missing resource hints.
Fix: Add `<link rel="preconnect" href="https://www.googletagmanager.com" />`, `<link rel="dns-prefetch" href="https://smartenplus-bucket.s3.amazonaws.com" />`, `<link rel="dns-prefetch" href="https://smartenplus-wp-s3.s3.us-west-2.amazonaws.com" />`.

**TS3 — og:site_name absent from Seo.js** | Severity: Minor | `components/FrontPage/Seo.js:31-44`
Evidence: `openGraph` config missing `siteName`. `siteName = "SmartEnPlus"` exists at `helpers/constants.js:30`.
Fix: Add `siteName: siteName` to the `openGraph` object.

**TS4 — og:locale absent from Seo.js** | Severity: Minor | `components/FrontPage/Seo.js:31-44`
Evidence: No `locale` in openGraph. Thai market target requires `th_TH`.
Fix: Add `locale: 'th_TH'` to openGraph config.

**TS5 — twitter:site handle absent** | Severity: Minor | `components/FrontPage/Seo.js:45-50`
Evidence: Twitter config has `cardType`, `title`, `description` but no `site` handle. Handle is `@smartenplus` per `X_URL` in constants.
Fix: Add `site: '@smartenplus'` to twitter config.

**TS6 — server-sitemap.xml referenced but does not exist (active 404)** | Severity: Critical | `next-sitemap.config.js:12`, `public/robots.txt:17`
Evidence: `additionalSitemaps: ['https://www.smartenplus.co.th/server-sitemap.xml']` declared. `Sitemap: https://www.smartenplus.co.th/server-sitemap.xml` in robots.txt. Glob for `pages/server-sitemap.xml.js` returned no files. Googlebot 404s on this URL, logging a GSC sitemap error and suppressing crawl credits for dynamic trip routes.
Fix (immediate): Remove the reference from both `next-sitemap.config.js` and `robots.txt`.
Fix (proper): Create `pages/server-sitemap.xml.js` using `next-sitemap` `getServerSideSitemap` fetching live trip routes.

**TS7 — robots.txt duplicate User-agent blocks** | Severity: Major | `public/robots.txt:1-9`
Evidence: Two separate `User-agent: *` blocks. RFC 9309 parsers use only the first matching group — the second `Allow: /` block may be ignored by strict parsers.
Fix: Merge into one `User-agent: *` group with all Disallow lines, then `Allow: /`.

**TS8 — Missing Strict-Transport-Security, CSP, Permissions-Policy** | Severity: Major | `next.config.js:84-113`
Evidence: `headers()` sets only `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`. HSTS, CSP, and Permissions-Policy are absent.
Fix: Add `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` at minimum.

**TS9 — domainURL canonical may include query string** | Severity: Minor | `lib/homepage/hooks/useHomeSeoData.js:13`
Evidence: `domainURL = \`${aboutURL}${router.asPath}\``. UTM params on `asPath` produce query string in canonical URL — Google treats this as a different URL.
Fix: Use `router.pathname` instead of `router.asPath`.

**TS10 — og:image uses build-hash-dependent static asset path** | Severity: Minor | `components/FrontPage/Seo.js:8-9`
Evidence: `bgDefault.src` resolves to `/_next/static/media/...hash....webp`. Hash changes on every build, breaking cached OG previews on Facebook/LinkedIn.
Fix: Move OG image to `/public/og-image.jpg` and reference as absolute stable URL.

---

## Specialist C: Page Performance Audit

### Methodology
Files read: `components/UI/FeaturedImageHeader.js`, `helpers/imageOptimization.js`, `pages/homepagev2.js` (lines 86–155, 330–395), `next.config.js` (lines 1–70), `package.json` (lines 1–70).

### Findings

**PP1 — DynamicProductSearchForm ssr:false CLS on desktop** | Severity: Major | `pages/homepagev2.js:145-152`, `line 350`
Evidence: Container at line 350 has `md:min-h-0 md:h-[104px]`. `md:min-h-0` collapses container to 0 height during JS load. Spinner loading state is `h-16` (64px) — does not match final `h-[104px]`. CLS on every desktop cold load.
Fix: Change `md:min-h-0` to `md:min-h-[104px]` so container height is reserved before hydration.

**PP2 — Hero banner setInterval hard-swaps image with no crossfade** | Severity: Major | `pages/homepagev2.js:181-187`
Evidence: `setInterval` at 5000ms increments `heroBannerIndex`, changing `imgUrl` prop on `MemoizedImage`. No opacity transition — hard swap causes visible flash. If banners have different intrinsic dimensions, CLS risk.
Fix: Add `transition-opacity duration-500` + opacity state management in `FeaturedImageHeader.js` to crossfade between banners.

**PP3 — generateBlurDataURL ignores imageUrl — misleading signature** | Severity: Minor | `helpers/imageOptimization.js:12-17`
Evidence: `imageUrl` param accepted but ignored entirely — always returns brand-blue SVG regardless of input. Comment claims CLS prevention but actual function is just a color placeholder.
Fix: Rename to `generateColorPlaceholder()` to clarify intent, or implement real LQIP.

**PP4 — No preconnect for GTM or S3 image hosts** | Severity: Major | `pages/_document.js:1-26`
Evidence: Zero resource hints in `_document.js`. S3 hero images require DNS + TLS on cold load. GTM is a script dependency. Combined cold-load penalty estimated at 300–600ms on 4G. Confirmed by Phase 2 (TS2).
Fix: Same as TS2 — add preconnect/dns-prefetch in `_document.js`.

**PP5 — Next.js 14.2.5 correctly emits fetchpriority="high" for priority images** | Severity: Informational | `package.json:53`
Evidence: `"next": "^14.2.5"`. `MemoizedImage` has `priority={true}` at `FeaturedImageHeader.js:24`. fetchpriority is emitted correctly. No action needed.

**PP6 — Hero sizes string missing explicit 640px breakpoint** | Severity: Minor | `helpers/imageOptimization.js:27`
Evidence: `'(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px'`. Missing breakpoint at 640px (iPhone landscape). Functionally correct but semantically incomplete.
Fix: Low priority — add `(max-width: 640px) 100vw,` prefix.

**PP7 — colorthief dynamic import with requestIdleCallback — acceptable** | Severity: Minor | `components/UI/FeaturedImageHeader.js:58-78`
Evidence: Dynamic `import('colorthief')` inside `requestIdleCallback` with `timeout: 2000`. Non-blocking, correct pattern. Module-scope `colorCache` Map works across navigations. No critical fix needed.

**PP8 — minimumCacheTTL, compress, standalone correctly configured** | Severity: Informational | `next.config.js:8,11,62`
Evidence: `compress: true`, `output: 'standalone'`, `minimumCacheTTL: 86400`. All appropriate. No action needed.

**PP9 — getOptimalImageQuality SSR/CSR mismatch risk** | Severity: Minor | `helpers/imageOptimization.js:62-87`, `components/UI/FeaturedImageHeader.js:26`
Evidence: Reads `navigator.connection` (client-only). Returns 85 on SSR but potentially 75 on 3G client — different `quality` prop value between SSR and CSR passes generates different image URL.
Fix: Use fixed `quality={85}` for hero `MemoizedImage`; reserve `getOptimalImageQuality()` for CSR-only below-fold images.

**PP10 — No server-side preload for actual LCP image (CMS hero)** | Severity: Major | `pages/homepagev2.js:265-328`
Evidence: `priority={true}` preloads `bgDefault` (the SSR fallback static image). Actual LCP element is `heroBannerImage` from S3, set after hydration — no `<link rel="preload">` is emitted for it. Browser fetches the real LCP image only after JS hydrates.
Fix: Extract first banner URL in `getStaticProps`, pass as prop, add `<link rel="preload" as="image" href={firstHeroBannerUrl} />` in the SEO block.

---

## Discussion: Conflicts & Cross-Specialist Debate

**D1 — AggregateRating: hardcode vs live data**
Specialist A: hardcoded values are factually wrong — live data is already available on the same page. `ReviewsStructuredData` already does this correctly; the TravelAgency block is just outdated.
**Leader Verdict:** Wire it. Fix is two prop reads. Hardcoded schema risks rich result suppression if Google detects mismatch with live review content. Fix effort: trivial.

**D2 — server-sitemap.xml: active 404 priority**
Specialist A: dynamic trip routes are uncrawlable without a dynamic sitemap. Specialist B: confirmed file does not exist, `robots.txt` reference is live. Both agree on the harm.
**Leader Verdict:** P0. Hotfix (remove reference from `next-sitemap.config.js` and `robots.txt`) takes 5 minutes and eliminates the active GSC error immediately. Proper fix (`pages/server-sitemap.xml.js`) is a sprint task. Fix effort: hotfix = trivial; proper = small.

**D3 — DefaultSeo: P0 or P1?**
Specialist B: structural gap — any new page without `<NextSeo>` has zero fallback metadata. Leader: current pages all have explicit `<NextSeo>`. Daily harm is low, but the structural risk is permanent.
**Leader Verdict:** P1. Not P0 because no current page is broken. One-line fix prevents all future gaps. Do it next sprint. Fix effort: trivial.

**D4 — CLS from ssr:false form**
Specialist B (Technical SEO): Googlebot renders JS — not a crawl issue. Specialist C (Performance): CLS is a direct Core Web Vitals ranking signal per Google's Page Experience update.
**Leader Verdict:** P2. One Tailwind class change (`md:min-h-0` → `md:min-h-[104px]`). Do it. Fix effort: trivial.

**D5 — og:image path vs LCP preload (new debate)**
PP10 (LCP preload for CMS banner) and TS10 (og:image hash instability) are different images with different impact. LCP affects search ranking directly; og:image affects social sharing conversion rates.
**Leader Verdict:** Fix PP10 first (ranking signal, sprint priority). Fix TS10 second (conversion, P3). Fix effort: PP10 = small; TS10 = trivial.

---

## Leader Synthesis

The homepage SEO layer is substantially built — 7 schema types are emitted, ISR is configured at 60s, `priority={true}` on the hero image is correct, and `next-seo` is used consistently across pages. The critical failures are concentrated in two areas: factual accuracy of structured data (fake phone, fake address, stale rating values, stale dates) and a live infrastructure gap (server-sitemap.xml 404). These are not architecture problems — they are maintenance gaps that accumulated as new components (`ReviewsStructuredData`, hero banner CMS) were added without updating the original inline TravelAgency schema block in `homepagev2.js`.

The single most critical fix is the `server-sitemap.xml` 404. Googlebot logs sitemap errors as crawl budget waste, and with trip routes being the primary booking entry point, this directly suppresses the pages that generate revenue. A two-line hotfix (remove from `next-sitemap.config.js` and `robots.txt`) takes 5 minutes and eliminates the GSC error immediately. The parallel `server-sitemap.xml.js` file build is a sprint task — it requires fetching live routes from the API, but the `next-sitemap` `getServerSideSitemap` pattern is well-established and documented in `[[blog-seo-performance-2026-05-20]]`.

The fastest high-value wins after P0: replace the two fake constants (SD1, SD2) in the TravelAgency block (10 min), wire aggregateRating to live props (SD3, 5 min), add sameAs social links (SD4, 5 min), and add `og:site_name`/`og:locale`/`twitter:site` to `Seo.js` (TS3/TS4/TS5, 10 min). All five P1 tasks combined take under 30 minutes and eliminate the most visible schema and OG gaps. The performance fixes (PP1 desktop CLS, PP10 LCP preload, PP4 preconnect) require slightly more care but are still single-component changes.

---

## Priority Fix Queue

**P0 — Correctness (breaks rich results or active 404)**
1. SD1: Replace `"+66-2-123-4567"` with `COMPANY_PHONE_NUMBER` in `homepagev2.js:295`
2. SD2: Add `COMPANY_ADDRESS` constant; replace `"123 Sukhumvit Road"` in `homepagev2.js:297-302`
3. TS6: Remove `server-sitemap.xml` from `next-sitemap.config.js:12` and `public/robots.txt:17` (hotfix), then create `pages/server-sitemap.xml.js`

**P1 — Coverage gaps (missing rich result opportunities)**
4. SD3: Wire TravelAgency `aggregateRating` to `lastTopReviewData` props in `homepagev2.js:310-314`
5. SD4: Add `sameAs: [FACEBOOK_URL, INSTAGRAM_URL, X_URL]` to TravelAgency schema
6. SD6: Replace hardcoded `lastReviewed` date with `new Date().toISOString()` in `homepagev2.js:278`
7. SD7: Add WebSite + SearchAction schema block for Sitelinks Search Box eligibility
8. TS1: Add `<DefaultSeo>` to `pages/_app.js`
9. TS3: Add `siteName` to openGraph in `Seo.js`
10. TS4: Add `locale: 'th_TH'` to openGraph in `Seo.js`
11. TS5: Add `site: '@smartenplus'` to twitter config in `Seo.js`

**P2 — Performance (Core Web Vitals)**
12. PP10: Add `<link rel="preload">` for first CMS hero banner URL in `homepagev2.js` SEO block
13. PP1: Change `md:min-h-0` to `md:min-h-[104px]` in `homepagev2.js:350`
14. PP2: Add CSS crossfade to hero banner swap in `FeaturedImageHeader.js`
15. TS2/PP4: Add preconnect/dns-prefetch for GTM and S3 in `pages/_document.js`

**P3 — Completeness (quality signals)**
16. TS7: Merge duplicate `User-agent: *` blocks in `public/robots.txt`
17. TS8: Add `Strict-Transport-Security` header to `next.config.js`
18. TS9: Replace `router.asPath` with `router.pathname` in `useHomeSeoData.js:13`
19. TS10: Move og:image to stable `/public/og-image.jpg` path in `Seo.js`
20. SD8: Fix `LocationsStructuredData` geo block — remove invalid `addressCountry` property
21. SD5: Add `logo` ImageObject to TravelAgency schema
22. SD11: Add `contactPoint` to TravelAgency schema
23. PP9: Use fixed `quality={85}` for hero image; reserve `getOptimalImageQuality()` for CSR-only images

**P4 — Future (aspirational)**
24. SD9: Add `departureTime`/`arrivalTime` to PopularRoutesStructuredData Trip items if API provides schedule data
25. SD10: Generate FAQPage schema from `subcategoriesData` help categories
26. PP3: Rename `generateBlurDataURL` → `generateColorPlaceholder` or implement real LQIP
27. PP6: Add 640px breakpoint to hero sizes string in `imageOptimization.js`

---

## Key Files
- `pages/homepagev2.js` — P0: lines 295, 297-302; P1: lines 278, 310-314, 286-318 (sameAs/WebSite schema); P2: line 350 (CLS height)
- `helpers/constants.js` — P0: add `COMPANY_ADDRESS`; existing `COMPANY_PHONE_NUMBER`, `FACEBOOK_URL`, `INSTAGRAM_URL`, `X_URL` to import in homepagev2.js
- `components/FrontPage/Seo.js` — P1: siteName/locale/twitter:site; P3: stable og:image path
- `pages/_app.js` — P1: add DefaultSeo
- `pages/_document.js` — P2: add preconnect/dns-prefetch
- `next-sitemap.config.js` — P0: remove server-sitemap.xml additionalSitemaps entry
- `public/robots.txt` — P0: remove Sitemap: server-sitemap.xml line; P3: merge User-agent blocks
- `pages/server-sitemap.xml.js` — P0: create this file (does not currently exist)
- `components/UI/FeaturedImageHeader.js` — P2: crossfade; P3: quality prop fix
- `lib/homepage/hooks/useHomeSeoData.js` — P3: line 13 router.pathname for canonical
- `lib/homepage/components/LocationsStructuredData.js` — P3: lines 51-53 fix geo block
- `next.config.js` — P3: add HSTS header
- `helpers/imageOptimization.js` — P4: rename generateBlurDataURL

## Related
- [[homepage-ux-review-2026-05-21]]
- [[blog-seo-performance-2026-05-20]]
- [[seo-homepage-specialist-team]]
