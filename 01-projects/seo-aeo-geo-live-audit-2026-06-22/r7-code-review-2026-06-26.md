---
title: "SEO/AEO/GEO Code Re-Review (r7) 2026-06-26"
type: code-review
status: complete
date: 2026-06-26
scope: code-only — current develop repo (post r6-r9 + faqpage fix `e143ccb`)
specialists: SEO-r7 · AEO-r7 · GEO-r7
baseline: r3-synthesis (SEO 6.5 / AEO 3.5 / GEO 3.0)
---

# r7 — Code Re-Review post r6-r9 (2026-06-26)

3-specialist **code-only** re-review of `develop` after the r6-r9 fix batches. Verified every fix landed + correct, confirmed remaining, hunted regressions (a `FaqJsonLd`→`FAQPageJsonLd` build-break had slipped through earlier on an empty-data path), re-scored. Live/prod verification is the separate SEO-R6-R9-DEPLOY step — not in scope here.

## Headlines
1. **All r6-r9 fixes FIXED** (file:line below). The `FaqJsonLd` regression is cleared repo-wide (0 refs).
2. **2 coverage-miss sites** found (both **pre-existing**, blame-confirmed — NOT regressions introduced by r6-r9; the r6/r7 fixes were incomplete). **1 live** (`useRouteSeo.js:76` availableLanguage, every route listing) + **1 dead code** (`useDayTripSEO.js:166` locale — 0 callers, 0 live impact). **Both now FIXED `fix/seo-r7-coverage` (`455b094`).**
3. **Re-scores: SEO 6.5→8.2 · AEO 3.5→6.5 · GEO 3.0→5.5.**

## Fix-verification (all FIXED)
| Batch | Fix | file:line |
|---|---|---|
| r6 | help notFound guard | `pages/help/[...slug].js:345-346` |
| r6 | destinations arrivalStation fallback | `pages/destinations/[slug].js:176-177` |
| r6 | manifest EN | `public/manifest.json` (`lang:"en"`) |
| r6 | availableLanguage `["en"]` (homepage) | `pages/homepagev2.js:244` |
| r6 | /activities NextSeo+canonical | `pages/activities/index.js:8,32-41` |
| r6 | help absolute og:image | `pages/help/[...slug].js:89,109` |
| r7 | sitemap `/ref/article/*` exclude | `next-sitemap.config.js:37-38` |
| r7 | Yoast `@graph` append removed | `components/blog/BlogPostSchemaGenerator.js:119-124` |
| r7 | og:locale en_US (6 files) | `_app.js:44`, `FrontPage/Seo.js:59`, 3 seo utils, `about/index.js:50` |
| r8 | synthetic reviews filter | `lib/homepage/components/ReviewsStructuredData.js:35-42` |
| r8 | About TravelAgency + `@id` merge + TAT | `pages/about/index.js:52-78` ↔ `homepagev2.js:235` |
| r9 | route listing FAQPage | `components/trips/search/FilterTripsSEO.js:2,49` (`FAQPageJsonLd` correct) |
| r9 | activity detail FAQPage | `pages/activities/detail/[...slug].js:131,143,153` → `DayTripDetailSEO.js:41-43` |
| fix | FaqJsonLd→FAQPageJsonLd build-break | `FilterTripsSEO.js:2` (0 `FaqJsonLd` refs repo-wide) |

## NEW findings (coverage-misses — pre-existing, NOT regressions; now FIXED)

### 🔴 COVERAGE-MISS (live, pre-existing) — `availableLanguage` — **FIXED `455b094`**
`hooks/useRouteSeo.js:76` — Organization `contactPoint.availableLanguage: ['English', 'Thai']`. Pre-existing (blame `bd46bfc`, not an r6-r9 commit). The r6 fix hit `homepagev2.js:244` but **missed this route-detail template** (renders on every `/trips/{from}/{to}`) — incomplete coverage, not a regression. **Fixed `fix/seo-r7-coverage` → `['English']`.**

### 🔵 DEAD CODE (pre-existing, 0 live impact) — `og:locale` — **FIXED for consistency `455b094`**
`hooks/useDayTripSEO.js:166` — `locale: 'th_TH'`. Pre-existing (blame `3fe82b9`). `useDayTripSEO.js` has **0 callers repo-wide** (dead code, like `SEOSection.js`) — the `th_TH` never renders. Fixed to `en_US` for en-only consistency so no future dev re-leaks it; deleting the dead hook is out of scope.

### 🟠 Title double-brand (SEO, pre-existing — newly documented)
`pages/_app.js:40` `titleTemplate="%s | SmartEnPlus"` + pages passing titles already ending `| SmartEnPlus` → `… | SmartEnPlus | SmartEnPlus`. Affected: `pages/rate-review/index.js:51`, `pages/rate-review/submit-review/[...slug].js:28`, `pages/rate-review/[reviewSlug].js:116`, `pages/privacy/index.js:27`, `pages/blog/index.js:117`, `pages/forum/[...slug].js:46,130`. Fix: drop trailing `| SmartEnPlus` from those titles (template adds it) OR `titleTemplate={null}` per-page.

### 🟡 Vault doc contradiction
`03-knowledge/structured-data-schema-patterns.md:80` still instructs `og:locale: 'th_TH'` (line 75 was fixed to en-only, line 80 missed). Will mislead the next dev into reverting. **Fix: `en_US`.**

### 🔵 Latent (zero live impact)
`components/SEO/SEOSection.js:7` — `{isFAQ && <FAQPageJsonLd mainEntity={mainEntity} />}` lacks the `mainEntity?.length > 0` guard every other site uses. **Dead code** (no callers) — if reactivated, emits malformed empty FAQPage. Add the guard before wiring.

### Info (no action)
- `public/robots.txt` is gitignored (build artifact); source of truth = `next-sitemap.config.js`. In sync. Editing the static file directly is silently lost at next build.
- Residual `blog.smartenplus.co.th` refs in `pages/api/graphql.js`, `pages/api/track-blog-view.js`, `store/blogApi.js` are legit WP-backend env fallbacks — not canonical/schema leaks (Yoast @graph disabled).

## Re-scores (vs r3)
| Lens | r3 | r7 | Delta |
|---|:---:|:---:|---|
| SEO | 6.5 | **8.2** | +1.7 — dual BlogPosting gone, help 500→404, og:locale unified, sitemap poison cut |
| AEO | 3.5 | **6.5** | +3.0 — FAQPage on route+activity+operator, synthetic reviews purged, org `@id` dedup |
| GEO | 3.0 | **5.5** | +2.5 — AI crawler allowlist, TAT/VAT identifiers, About entity merge. Capped by 2 en-policy leaks above |

## Remaining confirmed (known, not new)
C1-B (server-sitemap deleted-entity filtering) · C2 destinations root cause (ISR/backend) · M3 `/help/faqs` FAQ (WP GraphQL empty) · homepage FAQPage (content) · H4 meta desc · H5 author page + `Person.url` · H6 internal links · sameAs normalization · hreflang absent · llms.txt enrichment · polish (apple-touch-icon/security.txt/humans.txt).

## Net backlog delta (→ master-state SEO-P1-BACKLOG / P2-FIXES)
- **+P1**: REGRESSION-1 `useRouteSeo.js:76` availableLanguage→`['English']`; REGRESSION-2 `useDayTripSEO.js:166` locale→`en_US`.
- **+P2**: title double-brand (6 pages); vault `structured-data-schema-patterns.md:80` locale doc; SEOSection guard (if reactivated).

## Out of scope
- Live/prod verification (SEO-R6-R9-DEPLOY).
- Implementing findings (review-only — fixes next session).

---
*Re-review by SEO-r7 · AEO-r7 · GEO-r7 specialists · 2026-06-26 · develop `e143ccb`*
