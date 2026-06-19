# Operator Detail Page — SEO / AEO / GEO Audit

> **SHIPPED TO PROD 2026-06-16 (#124).** Fixes implemented (`21a4d4a`) → FE develop `6fff946`, deployed live. Backend-blocked items (operator `description` prose, per-type tab counts) remain open follow-ups.

## Status: FIXED 2026-06-16 (branch `fix/operators-seo-aeo-geo`)
Implemented frontend-only fixes, reusing trip-detail SEO pattern. New files: `helpers/seo/operatorDetailSEOUtils.js` (pure functions, mirrors `tripDetailSEOUtils.js`) + `components/operators/OperatorDetailSEO.js` (mirrors `TripDetailSEO.js`). Wired into `pages/operators/[slug].js` `getServerSideProps` (SEO built server-side → in initial HTML).

**Shipped:** title double-suffix fixed (now single brand via `_app.js` template); canonical via `getSiteUrl()` (forced https/www in prod); JSON-LD: `TravelAgency` (no aggregateRating — policy), `BreadcrumbList`, `ItemList` of routes (links to trip-detail), `FAQPage` (route count / services / rating-in-prose from real data); `og:locale: th_TH` + `localeAlternate`; `geo.region: TH` meta. Lint + build clean, verified live (200, all schema in HTML).

**Deliberately NOT done (justified, not debt):**
- **hreflang link tags** — dropped. Site serves one URL per operator (no per-language URLs to point at), and next-seo dedupes same-href alternates to one anyway. og:locale carries the locale signal instead. Trip-detail's hreflang has the same latent no-op; not propagated here.
- **ISR migration** (MED) — left as `getServerSideProps`. SSR already puts content in initial HTML (what schema needs); ISR is a separate perf concern, out of scope for this SEO fix.
- **aggregateRating schema** — intentionally absent on the operator Org node (Google policy). Ratings appear in human-readable FAQ prose only. Per-trip rating stays on trip-detail Product schema.
- **"About operator" prose** (GEO HIGH) — backend-blocked (no `description` field). FAQ + ItemList + entity schema partially compensate; real prose still needs the backend field.

---

## Summary
3-specialist audit (SEO / AEO / GEO) of `/operators/[slug]` (e.g. `/operators/silaphat`), `pages/operators/[slug].js`, just post-redesign (merged `8853cb2`). Headline: page emits **zero JSON-LD**, has a **double brand-suffix `<title>` bug**, and is **structurally thin for GEO** (no operator prose, backend-blocked). Most fixes are frontend-only and reuse the trip-detail SEO pattern shipped earlier today. One hard gate: rating-schema placement (policy). Read-only — no code changed.

## Context
Sibling precedent: [[trip-detail-seo-aeo-geo-audit-2026-06-16/r2-leader-synthesis]] — same audit type, just shipped, established the reusable helpers (`helpers/seo/tripDetailSEOUtils.js`, `helpers/seo/dayTripSEOUtils.js`, `utils/blog/seoHelper.js:getSiteUrl()`, `helpers/JsonLd.js`, `next-seo` JsonLd components). This audit recommends operators page adopt that same pattern — REUSE-first, no new infra.

Rating provenance (hand-verified, backend `operators/views.py:2959-2969`): `summaryData.average_rating`/`review_count` come from `dialogue.Review` filtered `is_approved=True` on `Contract` content-type — **first-party, moderated platform reviews** aggregated to operator level. This determines where `aggregateRating` schema may legally attach (see AEO-H3).

## Findings (severity-tagged, hand-verified)

### SEO (traditional search)
- **HIGH — Double brand suffix in `<title>`.** `_app.js:37` sets `titleTemplate="%s | SmartEnPlus"`; page title (`[slug].js`) is already `${operator.name} Trips & Services | SmartEnPlus` → renders `Silaphat Trips & Services | SmartEnPlus | SmartEnPlus`. Hand-verified: no `titleTemplate` override on the page. Trip-detail avoids this (its title carries no brand, lets the template add it once). **Fix**: drop the ` | SmartEnPlus` from the page title and let the template add it (cleaner), or set `titleTemplate: null` in the page `seo` object.
- **HIGH — Canonical/OG-url can emit relative/non-normalized URL.** `[slug].js`: `aboutURL = process.env.NEXT_PUBLIC_DOMAIN || ''` then canonical = `${aboutURL}${router.asPath.split('?')[0]}`. If env unset → relative canonical + relative OG `url` (OG requires absolute). No forced https/www. **Fix**: build from `getSiteUrl()` (`utils/blog/seoHelper.js`) + `operator.slug`, exactly as `tripDetailSEOUtils.js` does — hardcodes https/www fallback, one-line fix.
- **MED — `getServerSideProps` on a rarely-changing page.** SSR-every-request (2 sequential API calls) adds TTFB/crawl-budget cost vs trip-detail's `getStaticProps`+ISR. Filter/sort/page are query params (not path) so they don't fragment a static cache → clean ISR fit. **Fix**: migrate to `getStaticProps`+`revalidate`+`getStaticPaths(fallback:'blocking')`. (CLAUDE.md gotcha: deploy must clear `smartenplus_next_cache` volume.)
- **MED — OG image fallback shares the empty-`aboutURL` relative-URL risk**; consider adding image `type` via existing `getSeoImageType()`. Same `getSiteUrl()` fix covers it.
- **LOW — Heading hierarchy skip**: subheading "Available Trips and Services" is `<p>` not `<h2>`; contract titles are `<h3>` → H1→H3 skip. Promote subheading to H2.
- **FINE (verified, do not "fix")**: query-param duplicate content (canonical strips all query → bare-slug canonical, correct; tabs/search use JS `router.push` not crawlable `<a>`, so no filtered-URL crawl explosion); sitemap inclusion (`server-sitemap.xml/index.js` emits `/operators/{slug}` with `lastmod` from `updated_at`); no noindex; Twitter `site` handle inherits from `DefaultSeo`.
- **NOTE**: `StandardBreadcrumb` is `dynamic(ssr:false)` → visible breadcrumb absent from initial HTML. Ties into AEO-H1 below.

### AEO (answer engines — AI Overviews, snippets, Perplexity)
- **HIGH — Zero structured data.** No Organization, BreadcrumbList, aggregateRating, Product/Offer, FAQPage. Headline AEO gap.
- **HIGH — Emit BreadcrumbList JSON-LD** (server-side, since the visible crumb is `ssr:false` and invisible to crawlers). Reuse `next-seo` `BreadcrumbJsonLd` or the dayTrip/seoHelper breadcrumb generators. Cheapest zero-risk win.
- **HIGH — Emit `TravelAgency`/`Organization` entity** (`name`, `url`, `logo: operator.image`) via `CustomJsonLd` (`helpers/JsonLd.js`). Single most citable addition for "what is [operator]" queries.
- **HIGH (policy gate) — `aggregateRating` must NOT attach to the operator Organization node.** Google bans self-serving review markup on your own Org/LocalBusiness, and marking another company's reviews as Org aggregateRating is a manual-action risk. Provenance confirmed first-party/moderated (good), but the legitimate placement is on the **bookable item** (Product/TouristTrip per contract) — exactly what trip-detail already does (`tripDetailSEOUtils.js`). **Safe path**: emit contracts as an `ItemList` of `Product`/`Offer`, let rating live at trip level (or link to trip-detail pages which already carry it). Do NOT bolt rating onto the operator node.
- **MED — FAQPage** generatable now from existing data ("What routes does [operator] run?" from contract list/`pagination.count`; "What services?" from distinct `service_category`/`type`). Reuse `dayTripSEOUtils.js` FAQ generator pattern. (Rating-based FAQ only if it lives on eligible items per above.)
- **MED — Entity-definition prose** ("[Operator] is a Thailand ferry/bus/van operator running N routes…") is what AI Overviews quote verbatim. Generatable NOW from existing data (name + distinct types + route count) WITHOUT waiting on the backend description field — recommend a one-line server-rendered intro rather than blocking.

### GEO (generative engines — ChatGPT/Gemini/Claude/Perplexity synthesis & citation)
- **HIGH — Structurally thin until backend operator content exists.** Only operator-specific prose is name + stat trio + static "Available Trips and Services". No who-they-are / service-area / what-makes-them-distinct text. LLM can extract only a bare route list + a number → weakly citable for "best ferry operator X→Y / is [operator] good" queries. The `// About operator: reserved for future` comment confirms it's **backend-blocked** (no `description` field). Honest verdict: route-list-only is not GEO-competitive for recommendation queries.
- **HIGH — No JSON-LD** (overlaps AEO) — directly governs LLM entity disambiguation. Frontend-fixable now (Organization + ItemList).
- **MED — Geo/locale signals missing vs trip-detail.** Page's own `openGraph` overrides `DefaultSeo`'s `locale: 'th_TH'` without re-setting it → likely emits no og:locale. No `localeAlternate`, no `geo.region: TH`/`geo.placename`, no hreflang. Trip-detail sets all of these (`tripDetailSEOUtils.js`). Frontend-only fix.
- **MED — Thai geographic signals present but weakly extractable.** Route departure/arrival stations DO server-render into `<h3>` titles (good, e.g. "Hat Yai to Koh Lipe"); but service category is icon-bound, and there's no operator-level "serves routes between X, Y, Z" summary. Partially frontend-fixable (derive from contracts).
- **LOW — AI-bot crawlability PASS.** `robots.txt` + `next-sitemap.config.js`: only `User-agent: *` with disallows for `/orders /checkout /account /profile /bookings /guest-order /dev`. No GPTBot/ClaudeBot/PerplexityBot/Google-Extended blocks; operators NOT disallowed. Recent site-wide SEO audit did not accidentally block it.
- **LOW — Freshness adequate**: sitemap `lastmod` from `updated_at`; SSR = fresh per request. Minor: no visible freshness text.

## Cross-cutting root cause
Single biggest lever: **the page emits no JSON-LD at all.** Fixing that (BreadcrumbList + Organization + ItemList of contracts) addresses the top finding in all three lenses simultaneously, and all of it reuses helpers shipped earlier today for trip-detail. The `<title>` double-suffix is an unrelated quick HIGH-severity fix. The GEO content-depth gap is the one genuinely backend-blocked item (operator `description` field).

## Fixable-now vs backend-blocked
- **Frontend-only now**: title fix, `getSiteUrl()` canonical/OG, BreadcrumbList + Organization + ItemList JSON-LD, FAQPage from existing data, locale/geo/hreflang meta, data-derived intro prose + route summary, heading hierarchy, (optional) ISR migration.
- **Backend-blocked**: authoritative "about this operator" prose (needs `description` field) — until then the page stays thin for recommendation-style LLM queries regardless of meta.
- **Hard gate before ANY rating schema**: keep `aggregateRating` on eligible bookable items only (Product/TouristTrip), never the operator Organization node — even though provenance is first-party.

## Recommended priority order
1. Title double-suffix fix (HIGH, trivial).
2. `getSiteUrl()` canonical + OG url (HIGH, one-line, fixes SEO + feeds correct URLs into schema).
3. BreadcrumbList + Organization JSON-LD (HIGH, zero-risk, data on hand).
4. ItemList of contracts as Product/Offer; rating only at item level (HIGH, respects policy gate).
5. locale/geo/hreflang meta (MED).
6. FAQPage + data-derived intro prose (MED).
7. ISR migration, heading hierarchy (MED/LOW).
8. Backend follow-up: operator `description` field → unblocks real GEO prose.

## Related
- [[operator-detail-page-redesign-2026-06-16]] — the redesign this audits (same page, merged `8853cb2`).
- [[trip-detail-seo-aeo-geo-audit-2026-06-16/r2-leader-synthesis]] — sibling audit, source of all reusable SEO helpers.
- Token/design work: branch merged to develop `8853cb2`.

## Files referenced
`pages/operators/[slug].js`, `pages/_app.js:37` (titleTemplate), `helpers/seo/tripDetailSEOUtils.js` + `dayTripSEOUtils.js` (reuse), `utils/blog/seoHelper.js:getSiteUrl()`, `helpers/JsonLd.js`, `next-seo` JsonLd exports, `server-sitemap.xml/index.js` (sitemap), `smartenplus-backend/operators/views.py:2959-2969` (rating provenance).
