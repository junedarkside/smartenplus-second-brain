---
name: r1-seo-ai
description: SEO + AI Recognition specialist findings — M1-M4, identity analysis, AI classification gaps. Maps audit to file:line evidence.
type: specialist-finding
parent: website-audit-full-2026-06-06
specialist: SEO + AI Recognition Specialist
date: 2026-06-06
---

# R1 — SEO + AI Recognition Specialist

## Pre-existing wins (NOT work to do)

- `pages/_app.js:33-66` — DefaultSeo with og:locale `th_TH`, siteName `SmartEnPlus`, twitter `@smartenplus`, alternate hreflang
- `pages/homepagev2.js:270-339` — TravelAgency schema with `sameAs`, dynamic `aggregateRating`, `WebSite + SearchAction`, `Service` with `hasOfferCatalog`
- `pages/server-sitemap.xml` exists (referenced `next-sitemap.config.js:10-12`)
- `next-sitemap.config.js:5-9` — robots.txt with allow/disallow policies
- `lib/homepage/components/PopularRoutesStructuredData.js:50-63` — `offers` with `price` already in BusTrip schema (when `lowest_price` exists)
- `lib/homepage/components/LocationsStructuredData.js:51-57` — `geo` only emitted if `lat/lng` exist (no malformed GeoCoordinates)
- `lib/homepage/components/ReviewsStructuredData.js:72-80` — `aggregateRating` with `ratingValue` + `reviewCount` (dynamic)
- `components/activities/detail/DayTripDetailSEO.js:31-34` — `ProductJsonLd` + `BreadcrumbJsonLd` + `Organization` provider (Experience schema done!)
- `components/blog/InArticleCTA.js` — booking CTA component exists, **already used** in `BlogPostDisplay.js:200, 217`

## Findings (file:line evidence)

### SEO-1 — Duplicate "Routes" in navConfig (Audit M2)
- **Severity:** Moderate
- **Audit ID:** M2
- **File:line:** `constants/navConfig.js:14-23`
- **Evidence:**
  ```js
  {
    label: 'Routes',
    href: '/locations',
    children: null,
  },
  {
    label: 'Routes',
    href: '/trips',
    children: null,
  },
  ```
  TWO entries with `label: 'Routes'`, different hrefs.
- **Fix:** Either:
  - (A) Merge: keep `/trips` only, redirect `/locations` → `/trips`
  - (B) Differentiate: rename one to "Locations" (matches `/locations` semantic)
  - (C) Backend source: check `pages-info/navigation/` RTK Query endpoint for duplicate
- **Recommendation:** Option B — rename to "Locations" to match `href: '/locations'`. Also confirm this matches backend `NavigationSection`.
- **Impact:** SEO clarity, prevents Google confusion on duplicate anchor text
- **Effort:** trivial (5 min)
- **Risk:** low

### SEO-2 — Missing `<meta name="keywords">` (Audit M1)
- **Severity:** Low
- **Audit ID:** M1
- **File:line:** `pages/_app.js:33-66` (DefaultSeo) + `components/FrontPage/Seo.js` (per-page overrides)
- **Evidence:** DefaultSeo has `defaultTitle`, `titleTemplate`, `description`, `openGraph`, `twitter`, `additionalLinkTags`. **NO `keywords` field.**
- **Fix:** Add `keywords="bus, ferry, train, Thailand, booking, travel, Phuket, Krabi, Koh Phi Phi, airport transfer"` to `<DefaultSeo>` in `_app.js:36`.
- **Impact:** Marginal — Bing + Thai-local search engines may still use. Google ignores since 2009.
- **Effort:** trivial (5 min)
- **Risk:** low — search engines ignore keywords anyway

### SEO-3 — OG image is `smartenplus.png` (PNG, not WebP) (Audit M3)
- **Severity:** Moderate
- **Audit ID:** M3
- **File:line:** `pages/_app.js:42-48`
- **Evidence:**
  ```js
  images: [{
    url: `${process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'}/smartenplus.png`,
    secureUrl: `${process.env.NEXT_PUBLIC_DOMAIN || 'https://www.smartenplus.co.th'}/smartenplus.png`,
    width: 250,
    height: 50,
    alt: 'SmartEnPlus',
  }]
  ```
  Image is `smartenplus.png` (250×50 — also too small for OG standard 1200×630).
- **Fix:** Replace with WebP version, dimensions 1200×630 (OG standard):
  ```js
  url: `${siteUrl}/og-image.webp`,
  width: 1200,
  height: 630,
  ```
  Place `og-image.webp` in `public/` (similar to `smartenpus-transportation-booking-online.webp` in `public/`).
- **Impact:** Better social card rendering (LINE, Facebook). Some scrapers reject PNG for OG.
- **Effort:** small (30 min — design + deploy)
- **Risk:** low

### SEO-4 — GTM strategy="afterInteractive" but not preloaded (Audit M4)
- **Severity:** Moderate
- **Audit ID:** M4
- **File:line:** `pages/_app.js:80-85`
- **Evidence:**
  ```jsx
  <GoogleTagManager
    gtmId={process.env.NEXT_PUBLIC_GOOGLE_TAG_MANAGER}
    strategy="afterInteractive"
  />
  ```
  Already `afterInteractive` (non-blocking) ✓. Audit says "not preloaded" — meaning no `<link rel="preload">` for the GTM script itself.
- **Fix:** Add preconnect to GTM (already in `_document.js:16` ✓) + consider `<link rel="preload" as="script">` for GTM container if frequently used.
- **Verdict:** Partially addressed. GTM is already deferred. No action needed unless analytics shows load delay.
- **Effort:** 0 (skip — already optimized)
- **Risk:** low

## Identity Analysis (Audit P1-P3)

### SEO-5 — Brand name inconsistency: "SmartEnPlus" vs "smartenplus" (Audit Identity P3)
- **Severity:** Moderate
- **Audit ID:** Identity P3
- **File:line:** Multiple — used in:
  - Logo wordmark: "SmartEnPlus" (with capital E)
  - URL: `smartenplus.co.th` (lowercase, no E)
  - DefaultSeo: "SmartEnPlus" (capital E)
  - Schema provider.name: "SmartEnPlus"
  - `defaultImage from '../../public/smartenpus-transportation-booking-online.webp'` (TYPO: "smartenpus" not "smartenplus")
  - `PopularRoutesStructuredData.js:32, 60` — `url: "https://smartenplus.co.th"` (no www)
- **Evidence:** Grep `SmartEnPlus` vs `smartenplus` across codebase. URL wins for user trust (cannot change easily — SEO debt).
- **Fix:**
  - (A) Standardize on "SmartEnPlus" wordmark in display, "smartenplus.co.th" in URL (current state)
  - (B) Standardize on "smartenplus" everywhere (rename logo file `smartenpus-...webp` → `smartenplus-...webp`)
  - (C) Document decision in `03-knowledge/branding.md`
- **Recommendation:** Option A. Logo wordmark = "SmartEnPlus", URL stays. Add constant `BRAND_NAME = 'SmartEnPlus'` in `helpers/constants.js` and replace all hardcoded strings.
- **Impact:** Brand consistency, fewer "which is correct?" debates
- **Effort:** small (1 hr)
- **Risk:** low — display-only change

### SEO-6 — Blog already has booking CTAs via InArticleCTA (Audit Identity P2)
- **Severity:** RESOLVED
- **Audit ID:** Identity P2
- **File:line:** `components/blog/InArticleCTA.js` (component) + `components/blog/BlogPostDisplay.js:200, 217` (used)
- **Evidence:**
  ```js
  const DynamicInArticleCTA = dynamic(() => import('./InArticleCTA'), { ssr: false });
  ```
  `InArticleCTA` has `'route' | 'newsletter' | 'booking' | 'social'` types. Already used in 2 places in BlogPostDisplay.
- **Verdict:** DONE. Audit claim is outdated. The booking CTAs exist.
- **Note:** Skeptical pre-objection ("does codebase have reusable `<BookingCTA>` component?") is FALSE. Component exists. Cross-link to [[section-contentcard-wrapper-pattern]] in knowledge base.
- **Effort:** 0 (skip)
- **Risk:** n/a

## AI Recognition Gaps (audit "What's Missing")

### SEO-7 — Product schema on Experience pages (Audit AI Gap 2)
- **Severity:** RESOLVED
- **Audit ID:** AI Gap 2
- **File:line:** `components/activities/detail/DayTripDetailSEO.js:31`
- **Evidence:** `<ProductJsonLd {...productJsonLd} />` already in use. Server-generated in `getStaticProps` via `helpers/seo/dayTripSEOUtils.js`.
- **Verdict:** DONE. Experience pages have Product + Breadcrumb + Organization schema.
- **Effort:** 0 (skip)
- **Risk:** n/a

### SEO-8 — BreadcrumbList on route pages (Audit AI Gap 3)
- **Severity:** RESOLVED
- **Audit ID:** AI Gap 3
- **File:line:** `components/activities/detail/DayTripDetailSEO.js:34`
- **Evidence:** `<BreadcrumbJsonLd itemListElements={breadcrumbItems} />` — passed from `[...slug].js` `getStaticProps`.
- **Verdict:** DONE for Experience pages. NOT yet for `/trips/[from]/[to]` pages.
- **Remaining:** Audit trip pages (`pages/trips/[from]/[to].js`) for BreadcrumbList.
- **Effort:** small (30 min if needed)
- **Risk:** low

### SEO-9 — Price in BusTrip/Offer (Audit AI Gap 1)
- **Severity:** Partial
- **Audit ID:** AI Gap 1
- **File:line:** `lib/homepage/components/PopularRoutesStructuredData.js:50-63`
- **Evidence:**
  ```js
  ...(route.lowest_price && {
    "offers": {
      "price": route.lowest_price,
      "priceCurrency": "THB",
      "priceValidUntil": PRICE_VALID_UNTIL,
    }
  })
  ```
  Price is included when `route.lowest_price` exists. Skipped otherwise.
- **Verdict:** PARTIALLY addressed. Backend may not always provide `lowest_price`. Audit to see % of routes with this field. If <80%, ask API team to ensure all routes have `lowest_price` in the contract endpoint.
- **Effort:** 0 (code done) + small coordination with API team
- **Risk:** low

### SEO-10 — FAQPage content matching schema (Audit AI Gap 4)
- **Severity:** Low
- **Audit ID:** AI Gap 4
- **File:line:** `pages/homepagev2.js:493-495` per `homepage-seo-performance-deep-review.md` SD10 — `helpSubcategories` fetched, FAQPage not generated
- **Evidence:** Prior audit noted `helpSubcategories` exists in getStaticProps but no FAQPage schema generated.
- **Fix:** Add FAQPage schema generation using `helpSubcategories` data. Visible FAQ section should be added to homepage OR FAQ data converted to `<details>` blocks in a `/faq` page.
- **Impact:** Featured snippet eligibility
- **Effort:** medium (2 hrs for schema + visible FAQ)
- **Risk:** low — content work, not code

## Top 3 Wins

1. **SEO-1 — Dedupe navConfig "Routes"** (5 min, config fix)
2. **SEO-5 — Brand name constant + rename `smartenpus` typo** (1 hr, brand consistency)
3. **SEO-3 — OG image to WebP 1200×630** (30 min, social card)

## Key Files

- `constants/navConfig.js` — duplicate Routes (M2)
- `pages/_app.js` — DefaultSeo (og:locale ✓, missing keywords M1, OG image M3)
- `lib/homepage/components/PopularRoutesStructuredData.js` — BusTrip + price (partial)
- `components/activities/detail/DayTripDetailSEO.js` — Product + Breadcrumb ✓
- `components/blog/InArticleCTA.js` + `BlogPostDisplay.js:200, 217` — booking CTA ✓
- `pages/homepagev2.js:270-339` — TravelAgency, WebSite, Service ✓
- `next-sitemap.config.js:10-12` — server-sitemap ref ✓ (file exists)
- `public/smartenpus-transportation-booking-online.webp` — typo in filename

## Related

[[homepage-seo-performance-deep-review]] (30 findings, most already fixed) · [[blog-seo-performance]] · [[structured-data-schema-patterns]]
