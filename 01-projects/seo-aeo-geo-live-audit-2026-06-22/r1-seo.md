# r1-seo — Technical SEO Lens (Live Prod)

> Audit 2026-06-22 · Live production `https://www.smartenplus.co.th` · 8 templates + 1 WP subdomain. See [[r3-synthesis]] for merged priorities.

## Summary

Technical SEO **foundations are strong** (canonical/og/sitemap/security/ISR/CWV all healthy) but there is **one critical sitemap-poison defect** (41 `/ref/article/*` URLs return 404) and several **high-value page-level regressions**: `/help` canonical points to the **apex host** (canonical chain), `/help` and `/airport-transfer` ship **zero structured data**, `og:locale` is hardcoded `th_TH` on every English page, and several titles carry a **double brand** suffix. These are all frontend fixes — no backend work required for the SEO lens.

## Method

Live `curl` (UA `SEOAudit/1.0` + browser UA) + Web-Vitals collected via local Playwright (Chromium, headless, **no CPU/network throttling → real-user numbers will be worse**, especially on mobile/3G). Source traced in `smartenplus-frontend` for root cause.

Templates sampled (sitemap = 107 URLs):

| # | URL | Template | HTTP |
|---|-----|----------|------|
| 1 | `/` | Homepage | 200 |
| 2 | `/trips/detail/koh-lipe-to-khao-sok-national-bus-stop-110` | Trip detail | 200 |
| 3 | `/trips/phuket/koh-phi-phi` | Route listing | 200 |
| 4 | `/activities/detail/chiang-mai-to-chiang-rai-sightseeing-transfer-382` | Activity / day-trip detail | 200 |
| 5 | `/blog` | Blog index | 200 |
| 6 | `/help` | Help / FAQ | 200 |
| 7 | `/airport-transfer` | Airport transfer hub | 200 |
| 8 | `/ref/article/phi-phi-to-ao-nang-ferry-and-speedboat-route-thailand` | Reference article | **404** |
| 9 | `blog.smartenplus.co.th/` | WP blog home | 200 |

## Per-template findings

### SEO-1 · `/ref/article/*` sitemap poison — **P0**
- **41** `/ref/article/*` URLs present in `sitemap-0.xml`; **10/10 sampled return HTTP 404** ("Page Not Found - SmartEnPlus", zero JSON-LD, `<h1>404</h1>`).
- Root cause: `pages/ref/article/[slug].js` `getStaticPaths` pre-renders from WP `referenceArticles` at build → `next-sitemap` writes those paths. At request time `getStaticProps` returns `notFound: true` because the WP articles no longer resolve (deleted/renamed). Static pages were built + sitemapped but now 404.
- Impact: Google wastes crawl budget on 404s; "Crawled, currently not indexed" surface area; sitemap trust degraded. Compounds prior [[gsc-crawled-not-indexed-investigation-2026-06-05]].
- **Also**: that page's `canonical` is hardcoded `https://www.smartenplus.co.th/ref/${slug}` (`[slug].js:91`) but the **actual URL is `/ref/article/${slug}`** — even the valid articles self-canonical to a different path that hits `pages/ref/[type].js`. Canonical/URL mismatch independent of the 404.
- Fix (frontend): remove `/ref/article/*` from `sitemap-0.xml` until WP slugs verified; correct canonical to `/ref/article/${slug}`; consider `notFound()` + `noindex` on the catch page. Re-deploy + clear `smartenplus_next_cache` ISR volume ([[isr-revalidate-csr-vs-isr-field-matrix]]).

### SEO-2 · `/help` canonical → apex host — **P0**
- `pages/help/index.js:21` hardcodes `canonical: 'https://smartenplus.co.th/help'` (apex, no `www`).
- Live: `https://smartenplus.co.th/help` **301-redirects to** `https://www.smartenplus.co.th/help`. So the canonical tag points to a URL that redirects to the canonical host — a **canonical chain**. Google can resolve 301→canonical but it wastes a hop and signals inconsistency.
- Same page `og:url` is unset → inherits `_app.js` DefaultSeo `og:url` = homepage (`https://www.smartenplus.co.th`). og:url wrong for a sub-page.
- Fix: `canonical: 'https://www.smartenplus.co.th/help'`, add `openGraph: { url: ... }`.

### SEO-3 · `og:locale = th_TH` site-wide — **P1** (recurring)
- Hardcoded in `pages/_app.js:41` DefaultSeo `openGraph.locale: 'th_TH'`. Reproduces on homepage, trip detail, route listing, activity detail, help, airport-transfer. Content is **English**; only `/blog` (`en_US`) is correct.
- Prior flags: [[trip-detail-seo-aeo-geo-audit-2026-06-16]], [[homepage-seo-performance-deep-review]]. Still not fixed at the shared source.
- Fix: one-line change `_app.js:41` → `locale: 'en_US'` (or remove — Google infers from content/lang). Single fix clears 6 templates.

### SEO-4 · Double brand in titles — **P1**
- `_app.js:37` `titleTemplate="%s | SmartEnPlus"`. Pages that bake `SmartEnPlus` into their title string produce a double suffix:
  - `/help` → `Help Center | SmartEnPlus | SmartEnPlus` (`help/index.js:19` sets `title: 'Help Center | SmartEnPlus'`)
  - `/airport-transfer` → `SmartEnPlus All Airport Transfers - Page 1 | SmartEnPlus` (`airport-transfer/index.js:51`)
  - 404 → `Page Not Found - SmartEnPlus | SmartEnPlus`
  - `blog.smartenplus.co.th/` → `SmartEnPlus - SmartEnPlus` (WP theme, separate stack)
- Fix: page titles should pass the **bare** title and let the template append brand. Drop `| SmartEnPlus` from `help/index.js:19`, drop leading `SmartEnPlus` from airport title.

### SEO-5 · Title length regressions — **P1**
- Homepage `Book Bus, Ferry & Train Tickets in Thailand | SmartEnPlus` = **61 chars** (borderline; fine).
- Trip detail `Koh Lipe pattaya beach to Khao Sok Bus Stop | THB 1600 | SmartEnPlus` = **68 chars** (over 60; THB price useful for CTR, acceptable trade-off).
- Route listing `Phuket to Koh Phi Phi | Ferry, Bus, Van Tickets | from THB 700 | SmartEnPlus` = **76 chars** (truncates in SERP).
- Activity detail `Chiang Mai to Chiang Rai Sightseeing Transfer via Hot Spring, White Temple, Black House & Blue Temple | Day Tours | SmartEnPlus` = **131 chars** (severely truncated; move detail into H1/description, keep title ≤60).
- Airport transfer title carries ` - Page 1` on the first page — page 1 should not be paginated-branded.
- Fix: tighten templates in `helpers/seo/*SEOUtils.js` + the activity/trip title builders.

### SEO-6 · Duplicate security headers — **P3**
- `x-frame-options`, `referrer-policy`, `strict-transport-security`, `permissions-policy` each appear **twice** in the homepage response — once from Next/security headers, once from Cloudflare. Harmless (browsers take first/strictest) but indicates duplicated config layers. Low priority.

### SEO-7 · Sitemap coverage gaps — **P2**
- 107 URLs total. **No `/operators/*` and no `/locations/*` in sitemap-0.xml** despite both being real indexable templates. If those pages exist and should rank, they're invisible to crawlers via sitemap (may still be crawled via internal links).
- `server-sitemap.xml` (dynamic) may carry them — confirm. If not, add `additionalSitemaps`/paths.
- Also: `/ref` (index) and `/ref/[type]` present; `/ref/article` stale subset (see SEO-1).

## Core Web Vitals (homepage, headless — real-user floor)

| Metric | Desktop | Mobile (iPhone 13) | "Good" threshold | Verdict |
|--------|--------:|-------------------:|------------------|---------|
| TTFB | 1023 ms | 1155 ms | < 600 ms | ⚠️ needs improvement (CF edge + ISR HIT, but origin latency) |
| FCP | 1284 ms | 1384 ms | < 1800 ms | ✅ |
| LCP | 1628 ms | 1716 ms | < 2500 ms | ✅ (floor — add throttling/real device) |
| CLS | 0.000 | 0.000 | < 0.1 | ✅ excellent |
| INP | n/m | n/m | < 200 ms | not measurable headless (no real interaction) |
| DOM load | 1328 ms | 1452 ms | — | — |
| Transfer | 935 KB | 943 KB | < 1600 KB | ⚠️ JS-heavy |
| JS requests | **98** | **62** | — | ⚠️ bundle fragmentation (32 unique chunks) |
| Total requests | 139 | 99 | — | — |
| DOM nodes | 568 | 526 | < 1500 | ✅ |

**Caveat**: no CPU/network throttling → real mobile (mid-range Android, 3G/4G) LCP/INP will be materially higher. Recommend a real **PageSpeed Insights / CrUX field-data** pass for field CWV; this run is a relative-shape + budget tool.

**Perf hygiene (good):**
- ✅ All `<script src>` async/defer — **zero render-blocking** scripts (35 script tags, none blocking).
- ✅ Hero `<img>` preloaded with `fetchpriority="high"`; `next/image` responsive srcset; lazy-load + explicit width/height + `decoding="async"`.
- ✅ `preconnect`/`dns-prefetch` to GTM + both S3 buckets; font woff2 + CSS preloaded.
- ⚠️ 71 inline `<style>` blocks (MUI `sx`/styled-jsx) — bloats HTML, not blocking.
- ⚠️ Prior baseline [[website-audit-full-2026-06-06]] Speed 40/100 → appears improved, but JS bundle (98 req) is the persistent risk. See [[core-web-vitals-budget]].

## Structured data inventory (validity spot-check)

| Template | JSON-LD nodes | Key types | FAQPage | Verdict |
|----------|--------------:|-----------|:-------:|---------|
| Homepage | 167 | TravelAgency×34, Offer×24, Service, BusTrip×8, TouristDestination×8, Place×16, WebSite+SearchAction, AggregateRating, Review×3, ItemList | ❌ | Rich, valid. Missing FAQ (AEO gap). |
| Trip detail | 29 | Product, TouristTrip, Offer×3, Organization×4, BreadcrumbList, FAQPage(4Q/3A), Brand, Place | ✅ | Full — prior [[trip-detail-seo-aeo-geo-audit-2026-06-16]] fix live & valid. |
| Route listing | 132 | Product×20, Offer×39, Organization×23, FAQPage(6Q/6A), BreadcrumbList, ItemList, BlogPosting, WebSite | ✅ | Very rich + cross-links blog. |
| Activity detail | 12 | Product, Offer×2, Organization×3, BreadcrumbList | ❌ | **Thin** — no FAQ, no TouristTrip, no reviews. Gap vs trip detail. |
| Blog index | 30 | CollectionPage, ItemList, BlogPosting×10, BreadcrumbList, Organization, WebSite | ❌ | Good (blog doesn't need FAQ). |
| **Help/FAQ** | **0** | — | ❌ | **Zero schema** despite being the Q&A hub. P0 (also AEO). |
| **Airport transfer** | **0** | — | ❌ | **Zero schema**. P1. |
| `/ref/article` (404) | 0 | — | ❌ | 404 page (see SEO-1). |
| Blog WP home | 8 | WebSite, SearchAction, BreadcrumbList | ❌ | Minimal WP theme schema. |

Schema quality is **strong on product pages** (trip/route) and **absent on hub pages** (help, airport). See [[r1-aeo]] for the FAQ/AEO lens on the same gaps.

## What's already working (don't re-flag)
- ✅ Canonical present + correct www on all non-help pages; HSTS preload; detailed CSP; `x-content-type-options`, `referrer-policy`, `permissions-policy`.
- ✅ `google-site-verification` set; `robots: index,follow`; `twitter:card` + `og:image` 1200×630 webp with alt/secure_url/type ([[og-image-1200x630-webp]]).
- ✅ Sitemap index → `sitemap-0.xml` + `server-sitemap.xml` (post-cleanup, [[seo-sitemap-whole-site-audit-2026-06-11]]).
- ✅ ISR warm (`x-nextjs-cache: HIT`); Cloudflare CDN; HTTP/2; `alt-svc h3`.
- ✅ hreflang intentionally `x-default` only (single-locale, per prior audit — not a defect).

## Related
- [[r1-aeo]] · [[r1-geo]] · [[r3-synthesis]]
- [[canonicalization-audit-checklist]] · [[frontend-url-canonical-www-not-apex]] · [[seo-canonical-getsiteurl-pattern]]
- [[trip-detail-seo-aeo-geo-audit-2026-06-16]] · [[operator-detail-seo-aeo-geo-audit]] · [[trip-route-page-seo-aeo-geo-audit]]
- [[gsc-crawled-not-indexed-investigation-2026-06-05]] · [[core-web-vitals-budget]] · [[website-audit-full-2026-06-06]]
