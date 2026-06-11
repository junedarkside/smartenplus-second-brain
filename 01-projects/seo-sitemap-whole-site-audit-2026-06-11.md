# SEO + Sitemap Whole-Site Audit — 2026-06-11

## Summary
3-agent audit (sitemap infra / on-page meta+schema / technical rendering) of smartenplus-frontend, code + live. 40+ findings. Top risks: possible Googlebot WAF block, fabricated review schema (Google policy violation), sitemap shipping ~20 private URLs, broken `noindex` on checkout/orders/account, malformed activities canonical.

## Context
User-requested whole-site audit → vault report. Branch `develop` @ `7107516`. **Live-check caveat:** Cloudflare WAF returned 403 to all automated fetches on every path except `/robots.txt` — live sitemap XML, redirects, soft-404 status, llms.txt all unverified. That blockage is itself finding P0-1.

## Findings — Priority Order

### P0 — Critical

**P0-1. Cloudflare WAF 403 — verify Googlebot not blocked.** All fetchers got 403 sitewide. If the bot rule catches Googlebot/Bingbot, every other fix is moot; also neutralizes `public/llms.txt`. *Verify:* GSC URL Inspection "Test live URL" + Sitemaps report; allowlist verified crawlers in Cloudflare. (Agents 1+3 independently hit this.)

**P0-2. Fabricated reviews + aggregateRating in Product JSON-LD — 3 sources.** Google review-snippet policy violation; manual-action risk.
- `components/SEO/seoConfig.js:139-150` — hardcoded 5/5 review + `reviewCount: '1000'` on every route page
- `pages/destinations/[slug].js:364-384` — fake review published by **"TwoVit"** (other company's name, copy-paste artifact) + fake 4.4/89 on every destination page
- `components/review/productProperties.js:100-106` — fallback `'5.0'`/`'1000'` when trip has zero reviews
*Fix:* emit review/aggregateRating only from real data; delete hardcoded objects.

**P0-3. Static sitemap ships ~20 private/dev/duplicate URLs.** `next-sitemap.config.js:14` excludes only checkout/orders/test-*. `public/sitemap-0.xml` contains `/account/*` (9 URLs), `/dev/*` (4, noindexed — direct contradiction), `/rate-review` (noindexed — contradiction), `/bookings`, `/profile`, `/guest-order`, `/homepagev1`, `/homepagev2`, `/trips/detail`, `/blog/search`, `/forum/createtopic`, even `/server-sitemap.xml` as a page URL. Erodes GSC sitemap trust. *Fix:* expand `exclude` list.

**P0-4. `noindex` silently broken on private pages.** `pages/checkout/index.js:883-889` + `pages/orders/index.js:194-197` use `<NextSeo robots={{...}}>` — **next-seo v6 has no `robots` prop**; ignored. `pages/orders/[orderid].js`, `pages/profile/index.js`, `pages/account/*` have no robots meta at all. Private order URLs indexable. *Fix:* `noindex`/`nofollow` props. Note prior deferral: [[seo-wave2-audit-2026-05-23]] auth-page noindex blocked by ProtectedComponent null-SSR — re-check that constraint.

**P0-5. Activities detail canonical malformed.** `pages/activities/detail/[...slug].js:132` — `baseURL.replace('/api','')` on `https://api.smartenplus.co.th` eats `api` from `https://api` → canonical `https:/.smartenplus.co.th/...` on every activity page. *Fix:* use `NEXT_PUBLIC_DOMAIN` like trip detail (`pages/trips/detail/[...slug].js:122`).

**P0-6. No origin HTTP→HTTPS / host canonicalization.** `nginx/sites-available/smartenplus.conf:6-16` port-80 block proxies full content instead of 301; `test.smartenplus.co.th` + apex + www all serve 200. Up to 6 duplicate URL variants. Cloudflare edge may mask this (unverified, P0-1). *Fix:* nginx single-hop 301s to `https://www.smartenplus.co.th`.

### P1 — High

**P1-1. ~480 lines of trip-detail JSON-LD never render.** `hooks/useTripSEO.js:108-112,561-585` builds Breadcrumb/Org/LocalBusiness/FAQ/TouristTrip into `seoConfig.jsonLd`; `TripDetailSEO.js:61` spreads into NextSeo — **no `jsonLd` prop exists**. Dead pipeline; trip pages emit only Product. *Fix:* render via existing `components/SEO/JsonLd.js` pattern or delete.

**P1-2. Schema URLs point at API domain.** `useTripSEO.js:94-95,249,454,475` + `helpers/seo/dayTripSEOUtils.js:241,251,284-298` — Organization/seller/breadcrumb URLs = `https://api.smartenplus.co.th`. *Fix:* swap `baseURL` → `NEXT_PUBLIC_DOMAIN`.

**P1-3. Soft-404 on `/trips/*` — but DO NOT blanket-fix.** `pages/trips/[...slug].js:99-101` returns 200+empty for any garbage 2-segment slug; `pages/trips/[tripId].js:151-175` is a catch-all 200 for any 1-segment slug. Agent recommends `notFound: true` — **overruled by [[gsc-crawled-not-indexed-investigation-2026-06-05]]:** blanket `notFound` already OVERTURNED (14 Koh Lipe seasonal routes go legitimately empty). Follow that note's 3-phase plan (sitemap filter → surgical noindex → three-tier model). `[tripId].js` catch-all validation is still safe to do independently.

**P1-4. Homepage canonical keeps query string.** `lib/homepage/hooks/useHomeSeoData.js:13` — no `.split('?')[0]`; `?gclid`/`?utm` self-canonicalize. Also feeds og:url, WebPage @id, SearchAction. *Fix:* strip like `useRouteSeo.js:12`.

**P1-5. hreflang invalid sitewide.** `pages/_app.js:56-67` emits `th` + `x-default` pointing at homepage on every page; `components/SEO/seoConfig.js:53-58` emits en/en-US/th/x-default all same URL. No real language variants exist. *Fix:* remove all hreflang until real alternates ship.

**P1-6. Duplicate homepage + empty-shell routes.** `/homepagev1` (SSR), `/homepagev2` (ISR) routable duplicates of `/`; `pages/trips/detail/index.js` re-exports `/trips` component without its data fetch → empty 200 shell. *Fix:* 301 or delete.

**P1-7. Server-sitemap xmlns wrong.** `pages/server-sitemap.xml/index.js:562` uses `https://www.sitemaps.org/...` — protocol mandates `http://`. Strict parsers may reject whole file. One-char fix.

**P1-8. Sitemap silent shrink on API failure.** Help + routes generators return `""` on fetch error; blog `break`s mid-pagination (`index.js:36,146-151,318-324`). Outage during crawl window = truncated sitemap cached 1h, no alert. *Fix:* throw/serve last-good or alert with per-section counts.

**P1-9. `/activities` hub CSR-only.** `pages/activities/index.js` has no data fetching — listing invisible in raw HTML, and it's the target of permanent `/daytrips` 301. *Fix:* ISR getStaticProps (mirror `locations/index.js:216`).

**P1-10. Double brand suffix in titles.** `_app.js:37` titleTemplate `%s | SmartEnPlus` + page titles already containing brand → `… | SmartEnPlus | SmartEnPlus` on day trips (`dayTripSEOUtils.js:66`), route fallback (`seoConfig.js:9`), locations (`locations/[slug].js:50`).

### P2 — Medium (condensed)

- **Conflicting duplicate TravelAgency on homepage** — `homepagev2.js:239-290` vs `ReviewsStructuredData.js:61-81` (different name, non-www URL, separate ratings). All 5 `lib/homepage/components/*StructuredData.js` hardcode non-www host.
- **SearchAction targets nonexistent `/search` page** (`homepagev2.js:325-332`); `WebPageJsonLd image={bgDefault}` passes object not URL (`:236`).
- **`offers` typed `Trip` not `Offer`** in Product schema + uses `Math.max` (highest price) — `seoConfig.js:119-129`.
- **9 sequential awaits in server-sitemap** `getServerSideProps` (`index.js:583-591`) → slow TTFB; `Promise.all` one-block fix.
- **Fake lastmod**: all 128 static URLs build-stamped; ~14 server entries stamped per-request `new Date()`. Google distrusts.
- **No XML escaping** of interpolated slugs in server-sitemap — one `&` in backend slug breaks whole file.
- **Test products in sitemap**: `sitemap-0.xml:43-68` (`smart-en-plus-co-ltdeddd-day-tour-118`, opaque-ID trips).
- **`/trips` emitted twice** in server-sitemap; ref articles under 2 URL forms (`/ref/{slug}` + `/ref/article/{slug}`).
- **locations vs destinations dual emission** per station — pages are distinct products (consolidation overturned, see [[homepage-terminology-audit-2026-06-05]]) but schema disagrees on canonical place URL (`useStructuredData.js:43` vs `LocationsStructuredData.js:45`); differentiate titles/intent.
- **`/destinations/[slug]` frozen**: success path has no `revalidate` (`destinations/[slug].js:548-558`) + dead `query` destructuring from getStaticProps context.
- **GTM inside `next/head`** (`_app.js:82-87`) — next/script forbidden in Head, may drop/duplicate.
- **Deploy default `NEXT_PUBLIC_DOMAIN=smartenplus.co.th`** schemeless, no www (`scripts/deploy-ghcr.sh:273`) — defeats code fallback, invalid canonicals on apex. Related: [[og-image-inferred-audit-2026-05-23]].
- **nginx 1y `immutable` on all public images** (`smartenplus.conf:88-94`) incl. og-image.webp — stale social cards up to 1 year.
- **Locations pagination**: `?page=N` canonicalizes to page 1 (`locations/[slug].js:57`).
- **Blog publisher/author JSON-LD blocks lack `@context`** (`BlogPostSchemaGenerator.js:11-24,43-52`); Organization `@id` inconsistent across 4 builders.
- **Broken service worker dead code** (`public/service-worker.js:299` SyntaxError) — unregistered today; delete.

### P3 — Low (notable)
Dead SEO twins to delete: `helpers/seoConfig.js` (all commented), `helpers/seoHelpers.js` (never imported, would throw), `hooks/useDayTripSEO.js` (370-line dead near-duplicate containing the old review-schema bug pattern), `components/blog/BlogPostSEO.js`. `<Html lang="en">` vs `og:locale th_TH` vs manifest `"lang": "th"`. manifest.json contradicts llms.txt (tour operator vs not). `/ref/[type]` `fallback: true` (others use blocking). `/blog/categories/[slug]` + `/blog/tags/[slug]` in no sitemap. keywords meta bloat. AirportTransferSEO 2-word description.

## Confirmed Healthy
ISR cache volume cleared on deploy (`deploy-ghcr.sh:168`). notFound correct on trip/activity/blog/location/operator detail. Fonts via next/font swap; Omise afterInteractive; no sync 3rd-party scripts. robots.txt disallows match checkout/orders excludes. middleware.js no-op.

## Recommended Fix Order
1. **Verify Googlebot vs WAF** (P0-1, GSC — no code)
2. Delete fabricated reviews (P0-2) + fix broken noindex (P0-4) + activities canonical (P0-5) — small diffs, policy/privacy risk
3. Sitemap exclude list (P0-3) + xmlns (P1-7) + nginx 301s (P0-6)
4. Schema host fixes (P1-2, P2 non-www) + homepage canonical query (P1-4) + remove hreflang (P1-5)
5. Route soft-404: follow [[gsc-crawled-not-indexed-investigation-2026-06-05]] 3-phase plan — no blanket notFound
6. Rendering: `/activities` ISR (P1-9), destinations revalidate, dedupe homepage routes (P1-6)
7. Dead-code sweep (P3) + server-sitemap Promise.all/escaping/fallback hardening

## Implementation — 2026-06-12

**Branch `fix/seo-audit-2026-06-11`, commit `1f3f7a2`** (26 files, +361/−756). Merged → develop `d88f50b` + pushed 2026-06-12.

**Fixed:**
- **P0-2** fake reviews deleted from **4 sources** — audit found 3; implementation grep found 4th: `components/SEO/AirportTransferJsonLd.js:75-93` (same TwoVit/Jim block as destinations). `productProperties.js` aggregateRating now conditional on `averageRating > 0 && reviews.length > 0`.
- **P0-3** sitemap exclude expanded; result: **128 → 86 URLs**, 0 private. robots.txt +5 disallows (account/profile/bookings/guest-order/dev).
- **P0-4** noindex fixed: `noindex={true} nofollow={true}` on checkout/orders/bookings (was no-op `robots` prop); ADDED to `orders/[orderid].js` + `account/profile.js` (had none). SSR constraint from [[seo-wave2-audit-2026-05-23]] was a false blocker — NextSeo already sits outside ProtectedComponent.
- **P0-5** activities canonical → `NEXT_PUBLIC_DOMAIN`.
- **P1-1** dead 480-line jsonLd pipeline deleted from `useTripSEO.js` (63% rewrite; hook now returns only `seoConfig`+`productProps`+`baseSEOData`+`ogImagePath`). Sole consumer `TripDetailSEO.js` unaffected.
- **P1-2** schema URLs off API domain in useTripSEO + dayTripSEOUtils (module-level `siteUrl` const).
- **P1-4** homepage canonical strips query. **P1-5** hreflang removed (_app + seoConfig). **P1-6** 301s for /homepagev1, /homepagev2, /trips/detail. **P1-7** xmlns http://. **P1-9** /activities ISR shell (`revalidate: 60`). **P1-10** brand stripped from 3 title strings.
- **P2 batch:** server-sitemap Promise.all + escapeXml on all dynamic slugs; destinations/[slug] `revalidate: 3600` + dead `query` destructure removed (getStaticProps has no query); GTM out of `<Head>`; deploy `NEXT_PUBLIC_DOMAIN` default → `https://www.smartenplus.co.th`; 5 homepage StructuredData files → www; blog Organization/Person JSON-LD +`@context`.

**Verified:** `npm run build` exit 0; postbuild sitemap regenerated clean; 8 regression greps all 0 hits; `next-sitemap.config.js` loads; lint warnings pre-existing only.

**Remaining (not this branch):**
- P0-1 WAF/Googlebot — GSC manual verify (no code)
- P0-6 nginx HTTP→HTTPS/www 301s — infra
- P1-3 route soft-404 — per [[gsc-crawled-not-indexed-investigation-2026-06-05]] 3-phase plan
- P1-8 sitemap silent-shrink hardening — deferred
- P3 dead-code sweep (helpers/seoConfig.js, helpers/seoHelpers.js, hooks/useDayTripSEO.js, BlogPostSEO.js) — separate chore
- Deploy to prod (NOTE: P0-3/P1-7 only take effect after rebuild+deploy; ISR cache volume cleared by deploy-ghcr.sh)

## Related
[[gsc-crawled-not-indexed-investigation-2026-06-05]] · [[website-audit-full-2026-06-06-overview]] · [[seo-wave2-audit-2026-05-23]] · [[homepage-seo-performance-deep-review-2026-05-21]] · [[homepage-terminology-audit-2026-06-05]] · [[og-image-inferred-audit-2026-05-23]] · [[blog-canonical-url-wp-subdomain-bug]] · [[structured-data-schema-patterns]] · [[seo-homepage-specialist-team]] · [[persistgate-ssr-suppresses-head-component]]
