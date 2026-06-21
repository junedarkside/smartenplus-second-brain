# SEO Audit Reconciliation — 2026-06-21

## Summary
External audit scored smartenplus.co.th (28 findings). Repro re-audit via debug-mantra (live HTTP + code-trace, frontend-only scope). **4 of 6 Criticals are PHANTOM** (apex-301 artifact + audit methodology). 10 real FE-fixable findings. 5 CMS-only. 2 WP. 7 defer/content.

**P0+P1 fixes shipped to production 2026-06-21** (FE `e5de5f5` → develop → main → prod). Live-verified same day. See Production Verification section below.

## Context
External audit ran against live HTTP from bare apex (`smartenplus.co.th`), which 301s to `www.`. Crawl didn't follow redirects → every URL appeared as "301/dead". Inflated phantom 404 counts. Re-audit run 2026-06-21 via `curl -L` (follow redirects) against `www.smartenplus.co.th` + code-trace of smartenplus-frontend repo. Team: 3 verifiers (A: routing/sitemap, B: metadata/OG, C: schema/images) + leader synthesis.

## Critical Cross-Cutting Fact
All apex URLs 301 → www. Any crawl tool not following redirects will report all pages as "301/dead". The audit's mass-404 claims (#1,#2,#5) are entirely this artifact.

## Verdict Table (28 findings)

| # | Claim | Verdict | Class | Fix file:line |
|---|-------|---------|-------|---------------|
| 1 | 730 dead URLs | REFUTED | phantom | apex-301 artifact |
| 2 | 36 operators 404 | REFUTED | phantom | apex-301 artifact |
| 3 | WP indexable | WP | WP | robots in WP |
| 4 | 41 /ref/article/* 404 | RECLASSIFIED | phantom | /ref/article/* = internal rewrite target; canonical = /ref/{slug} (200). Add `disallow: /ref/article` to robots if desired. next-sitemap.config.js:8 |
| 5 | /trips/detail 652 × 404 | REFUTED | phantom | apex-301 artifact; 10/10 real slugs = 200 |
| 6 | /ref/* doubled title + dup robots | CONFIRMED | FE-fixable | Strip ` \| SmartEnPlus` from: pages/ref/article/[slug].js:89, pages/ref/[type].js:127, pages/ref/index.js:110. Remove redundant robots meta pages/ref/article/[slug].js:107 |
| 7 | title >60 chars (home 94) | CONFIRMED | FE-fixable | Shorten title on home page (pages/index.js or pages/homepagev2.js) to ≤60 chars |
| 8 | meta desc truncated | CONFIRMED | FE/content | Cap per-page descriptions to ≤155 chars: pages/blog/index.js:112, utils/blog/seoHelper.js:136 |
| 9 | brand doubled in title | CONFIRMED | FE-fixable | Remove brand suffix from page-level titles that already append it before titleTemplate runs. pages/blog/index.js:111 · utils/blog/seoHelper.js:64,96,116,123,135 · components/blog/BlogPostSEO.js:23 (strip Yoast suffix before passing) |
| 10 | og:locale th_TH/en_US split | CONFIRMED | FE-fixable | Policy decision: blog en_US (correct for English content), rest th_TH (consistent). Document in _app.js:41. Single-line if unifying. |
| 11 | fake author "Traveler's Compass" | CMS-only | CMS | WP author display name. FE reads it: components/blog/BlogPostSEO.js:28 (has fallback) |
| 12 | dateModified = pub+1s | CMS-only | CMS | WP auto-save. FE pass-through: utils/blog/seoHelper.js:147 |
| 13 | weak internal links | CMS-only | CMS | Content authoring. No FE autolink layer. |
| 14 | no outbound links | CMS-only | CMS | utils/blog/processBlogContent.js has no rel-inject. Optional: add external-<a> rel="noopener" rewriter |
| 15 | og:url → homepage on /about | CONFIRMED | FE-fixable | pages/about/index.js:43-47 — add og:url + canonical. Pattern: any page not setting og:url inherits _app.js:42 (homepage URL) |
| 16 | /trips title "undefined" | REFUTED (general) | defer | Valid routes fine. Literal "undefined" slug = broken inbound link not FE bug. Optional: validate slugs in getServerSideProps |
| 17 | no JSON-LD most pages | CONFIRMED + root cause | FE-fixable | next-seo v6 silently ignores `jsonLd` key. pages/blog/index.js:60-117 emits 4 schemas via `jsonLd` in seoConfig — never renders. Fix: replace with raw `<script type="application/ld+json" dangerouslySetInnerHTML>` tags (same pattern as homepagev2.js:229-325) |
| 18 | blog images missing w/h | CONFIRMED (low) | defer | 2/10 blog imgs (author avatars) lack dimensions. Low CLS impact. |
| 19 | TravelAgency block #2 empty | CONFIRMED (recharacterized) | FE-fixable | Two competing TravelAgency entities: block 3 = complete (pages/homepagev2.js:229-280), block 7 = sparse DIFFERENT name "SmartEnPlus Travel Service" (lib/homepage/components/ReviewsStructuredData.js:61-81). Fix: ReviewsStructuredData.js:63 change @type from "TravelAgency" to embed review/aggregateRating inside main entity, or delete wrapper and merge into homepagev2.js:234 TravelAgency |
| 20 | no ContactPoint | CONFIRMED | FE-fixable | pages/homepagev2.js:238 — add contactPoint to main TravelAgency block. Pattern exists on /trips Organization block |
| 21 | breadcrumb visible mismatch | CONFIRMED | FE-fixable | Homepage BreadcrumbList = 1 item (Home only). pages/homepagev2.js:327 — drop homepage breadcrumb entirely (home needs none) |
| 22 | no FAQ schema /help | WP | WP | /help is WP-served. /trips pages do emit FAQPage from FE |
| 23 | 149 resources homepage | PARTIAL | defer | Static HTML has ~99 refs; audit's 149 = full loaded count. Plausible but needs Lighthouse/HAR |
| 24 | article:author = homepage URL | CMS-only | CMS | Yoast-injected article:author meta. Same root as #11 |
| 25 | no twitter:image:alt | CONFIRMED | FE-fixable | next-seo v6 Twitter type has no imageAlt field. Fix: pages/_app.js DefaultSeo + components/FrontPage/Seo.js — add `additionalMetaTags: [{name: 'twitter:image:alt', content: '...'}]` |
| 26 | hreflang x-default only | CONFIRMED (low) | defer | No multi-locale site currently; x-default only is correct single-locale behavior |
| 27 | home 748 words | CONFIRMED | content | Thin for money page. Content team. |
| 28 | og:image:type missing home | CONFIRMED | FE-fixable | pages/_app.js:44-50 + components/FrontPage/Seo.js:46-52 — add `type: 'image/webp'` to OG image object |

## Phantom Findings — Do NOT Fix

**#1, #2, #5** — apex 301 artifact. Crawl tool didn't follow redirects. All pages 200 at www. No FE action.
**#4** — /ref/article/* is the internal Next.js rewrite target (next.config.js:110-112). Canonical URL is /ref/{slug} (200). Audit synthesized non-public URLs from the rewrite rule.
**#16** — valid /trips routes title correctly. Audit hit a broken inbound link with literal "undefined" slug.

## FE-Fixable — Priority Order

**P0 (schema integrity)**
1. **#17** Blog JSON-LD dead code — highest impact. pages/blog/index.js:60-117: replace `jsonLd` key with raw `<script>` tags
2. **#19** Duplicate TravelAgency entity — conflicting signals. lib/homepage/components/ReviewsStructuredData.js:61-81
3. **#20** Add ContactPoint to TravelAgency — pages/homepagev2.js:238

**P1 (title/OG correctness)**
4. **#9** Double brand suffix — pages/blog/index.js:111, utils/blog/seoHelper.js:64-163, components/blog/BlogPostSEO.js:23
5. **#6** /ref/* title + robots dup — pages/ref/article/[slug].js:89,107; pages/ref/[type].js:127; pages/ref/index.js:110
6. **#15** og:url missing on /about — pages/about/index.js:43-47
7. **#7** Home title 94→≤60 chars — pages/index.js or homepagev2.js
8. **#28** og:image:type — pages/_app.js:44-50, components/FrontPage/Seo.js:46-52

**P2 (signals)**
9. **#25** twitter:image:alt — pages/_app.js DefaultSeo additionalMetaTags
10. **#21** Drop homepage 1-item breadcrumb — pages/homepagev2.js:327
11. **#10** og:locale policy — document or unify _app.js:41
12. **#8** Meta desc length — pages/blog/index.js:112, utils/blog/seoHelper.js:136

## Production Verification — 2026-06-21 (post-deploy live audit)

Verified against https://www.smartenplus.co.th after production deploy.

| Fix | Finding | Live result | Status |
|-----|---------|-------------|--------|
| Home title | #7 | "Book Bus, Ferry & Train Tickets in Thailand \| SmartEnPlus" (57 chars) ✓ | ✅ LIVE |
| Blog title | #9 | "Blogs \| SmartEnPlus" (no double brand) ✓ | ✅ LIVE |
| Blog post title | #9 | "Island Hopping in Trat: ... \| SmartEnPlus" (no double brand) ✓ | ✅ LIVE |
| Blog JSON-LD | #17 | 4 blocks live: Organization/WebSite/BreadcrumbList/CollectionPage ✓ | ✅ LIVE |
| og:image:type | #28 | image/webp on homepage ✓ | ✅ LIVE |
| TravelAgency dup | #19 | 1 TravelAgency entity only, name="SmartEnPlus" ✓ | ✅ LIVE |
| ContactPoint | #20 | contactPoint present on TravelAgency ✓ | ✅ LIVE |
| Homepage breadcrumb | #21 | No BreadcrumbList on homepage ✓ | ✅ LIVE |
| /ref title | #6 | "... \| Thailand Travel Reference \| SmartEnPlus" (single brand) ✓ | ✅ LIVE |
| /about og:url | #15 | **PARTIAL** — two og:url tags found: homepage URL + /about URL. DefaultSeo emits homepage, page adds /about. Both present = duplicate tag. Functional (crawlers take last) but not clean. | ⚠️ PARTIAL |

### Remaining issues found in production

**⚠️ /about double og:url** — two `<meta property="og:url">` tags render: DefaultSeo emits homepage URL, page adds `/about`. Fix: migrate pages/about/index.js from plain `<Head>` to `<NextSeo openGraph={{url: domain+'/about'}}>` so it overrides DefaultSeo rather than appending.

**⚠️ Blog robots dup** — two `name="robots"` tags on /blog: `index,follow` (DefaultSeo) + `index, follow, max-image-preview:large` (page additionalMetaTags). Not a regression — the max-image-preview tag was already there. The DefaultSeo emits base robots; page adds extra. Crawlers take union, so net effect = `index, follow, max-image-preview:large`. Low severity but worth cleaning: remove base robots from DefaultSeo or ensure page tag is the only one.

**❌ twitter:image:alt** — still missing sitewide (#25, P2, not yet fixed).

**❌ og:locale** — home=th_TH, blog=en_US (#10, P2 policy decision, not yet fixed).

## Code↔Live Drift — RESOLVED
**/blog 0 JSON-LD** was root cause: next-seo v6 silently drops `jsonLd` key. Fixed 2026-06-21 — now 4 blocks live. ✅

## CMS/WP-Only (not FE-fixable)
- **#11, #24** — author "Traveler's Compass" + article:author URL: WP author display name → fix in WP
- **#12** — dateModified+1s: WP auto-save on publish
- **#13** — internal linking: content authoring
- **#3, #22** — WP subdomain indexability, /help FAQ schema: WP robots/plugin config

## Method Note
Repro run against www.smartenplus.co.th (curl -L, follow redirects). Sample sizes honest: 10/10 /trips/detail slugs from server-sitemap (not fabricated), 5/5 /operators, 5+ /ref slugs. "Checked against codebase" has a deploy-truth asterisk — live site may lag repo. Known drift: blog JSON-LD (explained above by API misuse, not deploy lag).

## Related
- [[seo-sitemap-whole-site-audit-2026-06-11]] — prior whole-site SEO audit (different scope; P0-P2 implemented June 2026)
- [[operator-detail-seo-aeo-geo-audit]] — operator page SEO
- [[trip-detail-seo-aeo-geo-audit-2026-06-16]] — trip detail page SEO (7 HIGH fixed)
- [[trip-detail-server-side-seo-pattern]] — SSR schema pattern (reuse for blog fix)
- [[website-audit-full-2026-06-06-overview]] — full site audit (perf + a11y + SEO)
