---
title: "External SEO/AEO/GEO Audit Reconciliation (r6) 2026-06-25"
type: reconciliation
status: complete
date: 2026-06-25
scope: external-audit-vs-live-code
source: "/Users/charuwatnaranong/Desktop/SmartEnPlus/seo/seo-aeo-geo-audit-smartenplus.md"
specialists: SEO-r6 · AEO-r6 · GEO-r6
---

# r6 — External Audit Reconciliation (2026-06-25)

Reconciled a **third-party (Hermes) 1,500-line SEO/AEO/GEO audit** dated 2026-06-24 against the real Pages-Router codebase + this project's r1–r5 rounds. Three specialists (SEO/AEO/GEO) each verified their lens against `file:line`. **This is a reconciliation, not an ingest** — the external audit is correct in spirit but materially wrong in mechanism.

## Summary — the three headlines

1. **The external audit assumed App Router; the repo is Pages Router only.** Every code-fix snippet it provides (`generateMetadata`, `notFound()` from `next/navigation`, `metadata` objects, App Router `dangerouslySetInnerHTML`) is **wrong-as-written**. Correct fixes use `next-seo` `NextSeo`/`DefaultSeo` props, `return { notFound: true }` from `getStaticProps`/`getServerSideProps`, `<Head>` tags, and raw `<script type="application/ld+json">`. Also load-bearing: **next-seo v6 silently drops the `jsonLd` prop** ([[nextseo-v6-jsonld-silent-drop]]).

2. **r3-synthesis P0-A (AI crawler block) is now OBSOLETE.** r5 (2026-06-22) verified all 8 AI UAs `Disallow: /`. **Live robots.txt fetched 2026-06-25 shows all 10 AI UAs `Allow: /`, no Cloudflare managed block.** The CF "AI Scrapers and Crawlers" toggle has been disabled since r5. GEO ceiling is lifted; revise **3/10 → ~6–7/10**. This is the single biggest state change.

3. **Accuracy: ~70% of findings hold up as bugs, but ~50% have wrong root cause / wrong fix, and 1 is a false-positive.** The findings are still valuable — they corroborate r1–r5 and surface net-new defects — but no external fix snippet should be applied verbatim.

## Scorecard — all 22 findings + 2 praise items

| ID | External claim | Verdict | Real root cause (file:line) |
|---|---|---|---|
| **C1** | 7.3% sitemap dead URLs; *all* lastmod identical | **PARTIAL** (bug real; lastmod claim false) | `pages/server-sitemap.xml/index.js` — routes filter `:335` (`operator_count>0`); products(`:233`)/operators(`:373`)/locations(`:183`) do NOT. Timestamped entities use per-row `updated_at` (`:213,279,344`); only date-less rows fall back to one `currentDate` (`:314`). `/ref/article/*` poison is in **`sitemap-0.xml`** (next-sitemap), not server-sitemap → fix `next-sitemap.config.js` |
| **C2** | `/destinations/[slug]` "Travel to undefined" | **TRUE bug / ROOT CAUSE CORRECTED 2026-06-25** | Backend probe (`api.smartenplus.co.th/stationsinfo/{slug}`): `koh-samui` API **200 returns `station_name:"koh samui"`** yet the live page shows undefined → **ISR stale cache or prod-env mismatch, NOT a missing field**. `koh-lipe`/`bangkok` API **404** (stations deleted) but ISR serves a stale `200` "undefined" page. **Fix landed `fix/seo-r6`: `pages/destinations/[slug].js:172` graceful fallback `arrivalStation = data?.station_name \|\| slug-derived` (non-breaking, removes "undefined", never 404s good data). Full fix still needs: ISR cache flush/redeploy + backend deleted-station cleanup + the koh-samui prod-env investigation.** |
| **C3** | `/help/*` 500s; fix via App Router `notFound()` | **TRUE bug / WRONG-FIX** | `pages/help/[...slug].js:311-352` — NO `notFound`. On missing article returns `props.error`+`data:null`; can throw → 500 (sometimes 200+error-div). Fix: `return { notFound: true }` in `getServerSideProps` |
| **C4** | Two BlogPosting; Yoast `@graph`→`blog.smartenplus.co.th`; strip WP plugin | **TRUE / WRONG-FIX locus** | `components/blog/BlogPostSchemaGenerator.js:120-128` pushes raw `seoPost.seo.schema.raw` verbatim. Help route strips domain (`pages/help/[...slug].js:76`); blog does NOT. Fix in the FE component, not WP |
| **H1a** | `og:locale: th_TH` lie | **TRUE** (+ missed blog nuance) | `pages/_app.js:44`, `components/FrontPage/Seo.js:59`, 3 seo utils, `pages/about/index.js:49`. Blog overrides `en_US` (`BlogPostHeader.js:44`) |
| **H1b** | TravelAgency `availableLanguage:["en","th"]` | **TRUE (NEW vs vault)** | `pages/homepagev2.js:244` hardcoded literal |
| **H2** | PWA manifest Thai | **TRUE (NEW)** | `public/manifest.json:2,4,11` — `lang:"th"`, Thai strings |
| **H3** | Templated reviews "Great travel experience"/"Anonymous Traveler"; 4.9/16 "hardcoded" | **PARTIAL / WRONG-CAUSE** | Fallbacks ARE hardcoded literals (`lib/homepage/components/ReviewsStructuredData.js:34,36`) but only fire on missing API fields. `aggregateRating` 4.9/16 = **LIVE** `lastTopReviewData` API values (`homepagev2.js:266-272`), not literals. Symptom = data-layer thinness |
| **H4** | Meta desc over-long (5+ pages) | **TRUE** | Hardcoded strings in page `<NextSeo>`/`seoHelper.js` |
| **H5** | Person author `url`=homepage; build App Router author page | **TRUE / WRONG-FIX** | `components/blog/BlogPostSchemaGenerator.js:48` `url: authorNode.url \|\| undefined`; no `pages/author/` route. Fix = `pages/author/[slug].js` Pages Router |
| **H6** | Internal links 1–2/page | **TRUE** (CMS-class) | No autolink layer; blocked until C2 fixed |
| **M1** | Title collision (e.g. `/blog/categories` double-brand) | **TRUE** | `pages/_app.js:35` `titleTemplate` + page-level brand. CONFIRMS r1-seo |
| **M2** | `/activities` + `/operators` missing canonical | **PARTIAL — `/operators` FALSE-POSITIVE** | `/activities` TRUE: `pages/activities/index.js:27-45` raw `<Head>`, no NextSeo, apex fallback `:36`. `/operators` HAS it: `pages/operators/index.js:26` `canonical={domainURL}` |
| **M3** | FAQPage parse error on `/help/[slug]` | **WRONG-CAUSE / WRONG-ROUTE** | `[...slug].js` emits raw Yoast `jsonSchema` (`:129`) not a constructed FAQPage; undefined→malformed script. Real FAQPage gap is `/help/faqs` `mainEntity:[]` (empty WP GraphQL) — CONFIRMS r3 P0-C. Not the route the audit names |
| **M4** | Relative `og:image` on help pages | **TRUE (NEW)** | `pages/help/[...slug].js:89,109` `imgDefault.src` (relative `/_next/...`) |
| **M5** | No `dateModified` on most content | **PARTIAL** | True for hub pages; FALSE for `/ref/article/[slug].js:97-100` (already emits modifiedTime) |
| **M6** | Blog images missing width/height | **TRUE** (low) | `pages/blog/index.js` `<Image>` |
| **M7** | S3 bucket policy for image authorship | **PARTIAL / speculative** | AWS-side, out of FE scope; weak evidence basis |
| **L1–5** | og:type, apple-touch-icon, security.txt, humans.txt, 404 og:image | **NOT CONTESTED** (trivial config; not code-verified) | low priority |
| **Praise** | `llms.txt` well-written, ahead of market | **PARTIAL — SUPERSEDES r1-geo GEO-5** | `public/llms.txt` exists 26 lines, clean structure. r1-geo said "absent 0/10" — now stale. Still lacks credentials (r3 P2-#12) |
| **Praise** | All major AI crawlers allowed | **TRUE — RESOLVES CONTRADICTION** | Live `robots.txt` (2026-06-25): 10 AI UAs `Allow: /`. **r1-geo P0-A + r3 P0-#1 = OBSOLETE/DONE** |

## Delta vs r3-synthesis

**🔴 OBSOLETE / DONE (external audit corrects the vault):**
- **r3 P0-A / P0-#1** (CF AI-crawler toggle) — **DONE**. Toggle disabled since r5. Lifts GEO ceiling. Re-confirm via `curl /robots.txt`.
- **r1-geo GEO-5** (`llms.txt` absent) — **SUPERSEDED**. Exists.

**🟢 NET-NEW (not in r1–r5 — these are the deliverable's real value):**
- **C3** `return { notFound: true }` in `pages/help/[...slug].js` getServerSideProps — 53×500→404 (prior audits only filed `/help` *index* canonical, never the `[...slug]` 500).
- **C2** missing `station_name` field guard in `pages/destinations/[slug].js:497` — fixes 178 "undefined" pages.
- **C4 locus correction** — strip the raw Yoast append in `BlogPostSchemaGenerator.js:120-128`, not a WP plugin removal.
- **H1b** `availableLanguage:["en","th"]`→`["en"]` at `homepagev2.js:244` — entity-language lie.
- **H2** English `public/manifest.json` — entire file Thai.
- **M4** absolute `og:image` prefix on help pages (`getSiteUrl()`).
- **M2** `/activities` NextSeo + canonical (apex fallback `:36` also wrong).

**✅ CONFIRMS r1–r5:** C1 `/ref/article` sitemap poison, C4 dual-origin schema, H1a og:locale (6 files), M1 title double-brand, H6 internal links, M3 `/help/faqs` empty FAQPage, H4 meta desc.

**🚫 REJECT (false-positive — must NOT enter backlog):**
- **M2 `/operators` canonical** — already present at `pages/operators/index.js:26`.

## Internal contradiction surfaced
- `03-knowledge/structured-data-schema-patterns.md:75` recommends `availableLanguage: ["Thai","English"]` — **directly contradicts** the en-only policy + H1b fix. Flag for a follow-up lint edit.

## Backlog impact (`master-state.md`)
- **SEO-P1-BACKLOG**: add `/activities` canonical+NextSeo (M2), help `[...slug]` notFound (C3), destinations `station_name` guard (C2), manifest English (H2), `availableLanguage` fix (H1b). Do NOT add `/operators` canonical (false-positive).
- **SEO-P2-FIXES**: og:locale already there (H1a) — keep; add help relative og:image (M4).
- **GEO**: close P0-A as DONE; revise score 3/10 → ~6–7/10 pending entity-consistency fixes.

## Cross-references
**Updates/extends:** [[r3-synthesis]] (P0-A obsolete) · [[r5-live-reaudit]] (robots state changed) · [[seo-audit-reconciliation-2026-06-21]] (same reconciliation pattern, different tool) · [[ref-url-structure-live-vs-code]] · [[sitemap-filter-by-inventory-or-recency]] · [[nextseo-v6-jsonld-silent-drop]] · [[blog-canonical-url-wp-subdomain-bug]] · [[help-faqs-wp-graphql-broken-prod]] · [[seo-canonical-getsiteurl-pattern]] · [[defaultseo-fallback-pattern]] · [[structured-data-schema-patterns]] (contradiction line 75).

## Out of scope
- No frontend code changes (reconcile-only). Fixes here are documentation for the backlog.
- PageSpeed/Ahrefs/GSC re-runs (need creds).
- L1–5 low items not code-verified.

---
*Reconciliation by SEO-r6 · AEO-r6 · GEO-r6 specialists · 2026-06-25 · Source audit: `~/Desktop/SmartEnPlus/seo/seo-aeo-geo-audit-smartenplus.md`*
