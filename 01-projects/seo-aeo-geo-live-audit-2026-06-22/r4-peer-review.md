---
title: "SEO/AEO/GEO Live Audit 2026-06-22 — Peer Review"
type: peer-review
status: partially-superseded
date: 2026-06-22
scope: review-of-r1-seo · r1-aeo · r1-geo · r3-synthesis
reviewers: SEO-specialist · AEO-specialist · GEO-specialist
superseded-by: r5-live-reaudit (for items marked WRONG below)
---

> **⚠️ Partial supersession notice (2026-06-22):** Live re-audit (r5) found that several findings in this peer review are themselves incorrect. Items marked **[WRONG — see r5]** below have been overturned by live HTTP verification. See [[r5-live-reaudit]] for corrected facts.

# Peer Review: SEO/AEO/GEO Live Audit 2026-06-22

Three specialist agents independently reviewed `r1-seo`, `r1-aeo`, `r1-geo`, and `r3-synthesis` against actual frontend code. This doc records confirmed issues, factual errors, missed issues, and corrected priorities.

---

## Verdict on r3-synthesis

**Overall quality: GOOD with critical errors in 4 cells.**

Core thesis (robots block + sitemap poison + /help = top 3) is correct. Priority ordering is reasonable. Effort estimates and code paths are mostly accurate. However four action items contain factual errors that would waste sprint capacity or send devs to wrong files.

| Action | Error | Correct |
|--------|-------|---------|
| #5 "fix og:locale = 1 line" | 6 files, not 1 | `_app.js:41`, `dayTripSEOUtils.js:126`, `tripDetailSEOUtils.js:34`, `operatorDetailSEOUtils.js:42`, `FrontPage/Seo.js:59`, `about/index.js:49` |
| #8 "Add sameAs + taxID + areaServed" | Already done | `homepagev2.js:243–265` already emits all three |
| #12 "Confirm operators/locations in sitemap" | Already confirmed | `server-sitemap.xml/index.js` has both `generateOperatorsSitemap()` + `generateLocationsSitemap()` active |
| #14 "Add llms.txt" | File exists | `/public/llms.txt` present; needs enrichment, not creation |
| P1 "Route listing as model page / 8.5/10" | Wrong score | `FilterTripsSEO.js` receives `faqMainEntity` prop but never renders it — zero FAQPage in HTML |

---

## SEO — Confirmed, Missed, Corrected

### Confirmed (audit correct)
- `SEO-1` `/ref/article/[slug].js:91` — canonical is `/ref/${slug}` not `/ref/article/${slug}`. Also wrong in `ArticleJsonLd:110` and `BreadcrumbJsonLd:127`.
- `SEO-2` `help/index.js:21` — apex-host canonical (no `www`).
- `SEO-3` `og:locale: 'th_TH'` in `_app.js:41` — confirmed widespread.
- `SEO-4` double-brand — `help/index.js:19`, `airport-transfer/index.js:51`, `404.js:10`.

### Missed by audit
1. **`help/[...slug].js:82` canonical collapse** — all `/help/*` category pages (`/help/faqs`, `/help/cancellation-policy`, etc.) self-canonical to `/help` root. Worse than the `/help/index.js` apex bug the audit flagged. Fix: use `router.asPath.split('?')[0]` in `defaultSEO.canonical`.

2. **`server-sitemap.xml/generateRefArticlesSitemap` emits wrong URLs** — `index.js:548–555` generates `/ref/${article.slug}` (hits category page) not `/ref/article/${slug}`. The audit fixed the page-level canonical but the sitemap itself is the live source of wrong URLs. Both must be fixed together.

3. **`og:locale` requires 6-file change, not 1** — page-level SEO utils override `_app.js` DefaultSeo. Fixing only `_app.js` leaves activity, trip, operator, about pages still emitting `th_TH`.

4. **Double-brand uncounted instances** — `pages/trips/[tripId].js:22`, `pages/locations/index.js:24`, `pages/forum/index.js:69` also double-brand. Audit lists 3; actual count is 6+.

5. **`next-sitemap.config.js` has `generateRobotsTxt: true`** — if Cloudflare CF toggle is disabled without updating this, next deploy overwrites `public/robots.txt` with a clean file. The CF AI-crawler policy has no frontend backup.

### Corrected priorities
- `SEO-7` (operators/locations sitemap) is a **non-issue**. Both are in `server-sitemap.xml`. Remove from action list.
- 404 double-brand (`404.js:10`) is **moot** — page is `noindex`. Not a real SEO liability.

---

## AEO — Confirmed, Missed, Corrected

### Confirmed (audit correct)
- `help/index.js` — zero schema, apex canonical, client-only Q/A.
- Homepage — no FAQPage (removed 2026-06-07 per code comment at `homepagev2.js:366`).
- Activity detail — `generateFAQSchema` in `dayTripSEOUtils.js:321` exported but never imported/called in `pages/activities/detail/[...slug].js`.
- Airport transfer — zero JSON-LD, station list JS-gated.

### Missed by audit
1. **Route listing FAQPage is not in HTML** — `FilterTripsSEO.js` accepts `faqMainEntity` prop (line 25, JSDoc line 14) but JSX render block (lines 41–55) never emits `<FAQPageJsonLd>`. Prop received, silently dropped. Audit scored route listing 8.5/10 claiming "6Q/6A FAQPage live in SSR HTML" — **factually wrong**. Two-part fix: (a) render the prop in `FilterTripsSEO.js`; (b) move FAQ data from `useRouteSeo` client hook into `getStaticProps` for SSR.

2. **`/help/faqs.js` exists and has working FAQPage schema** — audit never mentions this page. It uses `getServerSideProps`, builds valid `FAQPage` schema, emits via `<JsonLd />` (raw `<script>` tag, correct approach), uses `<details>/<summary>` HTML. The P0-C fix for `/help` should redirect effort to linking/promoting `/help/faqs` rather than rebuilding FAQ infrastructure on `index.js`.

3. **`ExperienceFAQ` component (`components/activities/detail/ExperienceFAQ.js`)** — renders FAQ accordions (What to bring, age restrictions, cancellation) with no JSON-LD. Visual FAQs with zero AEO signal.

4. **`SEOSection.js` component (`components/SEO/SEOSection.js`)** — purpose-built to conditionally render `FAQPageJsonLd` via `isFAQ` + `mainEntity` props. Built, never wired to any page template. Reuse this before building new FAQ schema infrastructure.

5. **`help/faqs.js` title double-brands** — `pages/help/faqs.js:52` sets `title: 'Help & FAQs | SmartEnPlus'` → becomes `Help & FAQs | SmartEnPlus | SmartEnPlus`. Not in audit.

### Corrected priorities
- Route listing is **not** a model AEO page. Score should be ~5–6/10. Remove from "what's already good."
- P0-C effort should start from `/help/faqs.js` (existing working schema) not from scratch on `index.js`.
- `SEOSection.js` component should be used for homepage FAQPage (action #4) rather than building new infrastructure.

---

## GEO — Confirmed, Missed, Corrected

### Confirmed (audit correct)
- Cloudflare robots block — confirmed, all AI UAs `Disallow: /`.
- `/ref/article/[slug].js:91` canonical wrong path.
- `homepagev2.js` `sameAs` thin (Facebook, Instagram, X only — no GBP, Naver, LINE OA, YouTube).
- `og:locale: 'th_TH'` site-wide confirmed.
- Review count sourced from backend (`lastTopReviewData?.review_count`) — not hardcoded, directionally concerns valid.

### Missed by audit
1. **`llms.txt` exists** — `/public/llms.txt` present. Audit scored 0/10 "Absent." Correct score: ~2/10 content-thin. Action is enrich (no TAT license, no statistics, no founding year, no city-level data), not create.

2. **`about/index.js` has zero schema** — no `Organization`, `TravelAgency`, or `AboutPage` JSON-LD. This is the page AI engines would cite for "who is SmartEnPlus?" Currently returns pure prose. High-priority GEO miss not in audit.

3. **`CitationSection.js:32` URL bug** — builds `https://www.smartenplus.co.th/ref/${slug}` (no `/article/`). Every APA citation + Wikipedia template on all reference articles points to a 404. The audit caught the page-level canonical but missed this compound effect — the site's only deliberate GEO citation system is doubly broken.

4. **GEO fix target for org schema is wrong file** — audit says fix `components/SEO/LocalBusinessSchema.js`. That file emits `Place` schema for transport stations, not `Organization`. Real org schema is inline in `pages/homepagev2.js:229–286`. Editing `LocalBusinessSchema.js` produces a silent no-op.

5. **`taxID` already in schema** — `homepagev2.js:246` already emits `"taxID": "0105554078213"`. Missing piece is TAT license as `identifier` object (`{ "@type": "PropertyValue", "name": "TAT License", "value": "11/06622" }`), which is only in footer UI (`components/layout/footer.js:56`).

6. **`sameAs` inconsistent across schema nodes** — `homepagev2.js` has 3 entries, `pages/blog/index.js:58` has 1 (Facebook only), `BlogPostSchemaGenerator.js:21–23` has 1 (Facebook only). AI engines may see conflicting entity graphs. All nodes need the same `sameAs` array.

7. **No hreflang anywhere** — zero results site-wide. Site targets EU, USA, Asia/Thailand. Absence means AI engines can't determine locale targeting.

8. **Homepage FAQ is a regression, not a missing feature** — `homepagev2.js:366` comment: "F11 FAQ (removed 2026-06-07)". Action #4 should frame this as rollback decision, not new build.

### Corrected priorities
- **GEO-6 (`/ref` articles 404 + citation URLs wrong) should be P0, not P1** — the `/ref` section is the site's only deliberate GEO citation-bait system. It's doubly broken (page 404s + citation URLs wrong). Demoting it behind P0-C undervalues it.
- **GEO-2 fix target** — change from `LocalBusinessSchema.js` to `homepagev2.js:229–286` (org schema inline) and `pages/about/index.js` (no schema at all).
- **P2 action #8 (sameAs/taxID/areaServed)** — already done for homepage. Effort should go to (a) adding TAT license as `identifier`, (b) adding `about/index.js` schema, (c) normalizing `sameAs` across blog/post nodes.

---

## Corrected Priority Table

> Items marked **[WRONG — see r5]** are overturned by live re-audit.

### Real P0
| # | Action | Correct File(s) | r5 status |
|---|--------|-----------------|-----------|
| P0-A | CF AI-crawler toggle + add frontend robots backup | Cloudflare dashboard + `next-sitemap.config.js` | Confirmed — still blocked |
| P0-B | ~~Fix `/ref/article/[slug].js:91` canonical + fix `server-sitemap.xml:548–555` URL + fix `CitationSection.js:32`~~ **[WRONG — see r5]** Fix: remove `/ref/article/*` from `sitemap-0.xml` only | `next-sitemap.config.js` | Live URL is `/ref/{slug}` (200); citationSection URLs correct; server-sitemap correct |
| P0-C | `/help/index.js:21` canonical + fix `og:url` + debug /help/faqs WP GraphQL returning empty | `pages/help/index.js`, `pages/help/faqs.js` + WP backend | Confirmed — plus /help/faqs FAQPage mainEntity:[] discovered |

### Real P1 (reordered, one item added)
| # | Action | Correct File(s) | Note |
|---|--------|-----------------|------|
| P1-1 | Wire `generateFAQSchema` into activity detail `getStaticProps` + `DayTripDetailSEO` | `pages/activities/detail/[...slug].js:124–139`, `DayTripDetailSEO.js` | Schema util already exists |
| P1-2 | **Fix `FilterTripsSEO.js:41–55`** — render `faqMainEntity` prop + move FAQ data to `getStaticProps` | `FilterTripsSEO.js`, trips page `getStaticProps` | Route listing has zero FAQPage in HTML |
| P1-3 | Fix `og:locale` across **all 6 files** | `_app.js:41`, `dayTripSEOUtils.js:126`, `tripDetailSEOUtils.js:34`, `operatorDetailSEOUtils.js:42`, `FrontPage/Seo.js:59`, `about/index.js:49` | Not a 1-line change |
| P1-4 | Add `about/index.js` schema (`TravelAgency` + TAT license `identifier`) | `pages/about/index.js` | Currently zero schema |
| P1-5 | Add homepage FAQPage via `SEOSection.js` (reuse existing component) | `pages/homepagev2.js`, `components/SEO/SEOSection.js` | Component exists, unused |
| P1-6 | Airport transfer: ItemList + FAQPage + SSR station list + title fix | `pages/airport-transfer/index.js:51` | |
| P1-7 | Fix `help/[...slug].js:82` canonical collapse (all category pages → `/help`) | `pages/help/[...slug].js:82` | Higher impact than index.js apex bug |

### Drop from action list
- **Action #8** (sameAs/taxID/areaServed for homepage) — already implemented in `homepagev2.js:243–265`.
- **Action #12** (operators/locations sitemap) — already in `server-sitemap.xml`.
- **Action #14** (add llms.txt) — file exists, change to "enrich `/public/llms.txt`".

---

## What's Actually Good (verified, updated by r5)
- Trip detail schema (ProductJsonLd + BreadcrumbJsonLd + Org) — confirmed best-in-class.
- Security headers, HSTS, CSP — confirmed strong.
- `/ref/{slug}` pages return HTTP 200 with Article schema — citation system functional.
- `CitationSection.js` URLs are correct (`/ref/${slug}`) — the "URL bug" this review raised was **[WRONG — see r5]**.
- `homepagev2.js` org schema — taxID, sameAs (3 social), areaServed already present — confirmed live.
- `server-sitemap.xml` — covers operators (36), locations (176), activities, trips, /ref, /help — all correct.
- `public/llms.txt` — HTTP 200, content present (thin but exists).
- Homepage ItemList schemas for routes + destinations — new positive since r1 audit.

## Items from this review overturned by r5 live re-audit
| This review claimed | r5 live finding |
|---------------------|-----------------|
| `CitationSection.js:32` generates broken `/ref/article/` URLs | WRONG — generates `/ref/${slug}` which is the correct live format |
| `server-sitemap.xml:548–555` generates wrong `/ref/${slug}` URLs | WRONG — `/ref/${slug}` IS the correct live URL (200 OK); sitemap-0.xml is the broken one |
| `/help/faqs.js` has "working SSR FAQPage schema" | PARTIALLY WRONG — schema present but `mainEntity:[]`; WP GraphQL returns empty in prod |
| `pages/ref/article/[slug].js:91` canonical is wrong (should be `/ref/article/`)  | WRONG — canonical correctly uses `/ref/${slug}` matching live URL |

---

## Files to Fix (consolidated)

```
pages/ref/article/[slug].js          line 91, 94, 110       canonical + og:url + ArticleJsonLd URL
pages/server-sitemap.xml/index.js    line 548–555            /ref/${slug} → /ref/article/${slug}
components/UI/CitationSection.js     line 32                 same URL bug
pages/help/index.js                  line 19–23              canonical, og:url, title, add link to /help/faqs
pages/help/[...slug].js              line 82                 canonical collapse → use router.asPath
pages/activities/detail/[...slug].js line 124–139            import + call generateFAQSchema in getStaticProps
components/activities/detail/DayTripDetailSEO.js             emit faqJsonLd via <JsonLd />
components/trips/search/FilterTripsSEO.js line 41–55         render faqMainEntity prop
pages/_app.js                        line 41                 og:locale (+ 5 other files below)
helpers/seo/dayTripSEOUtils.js       line 126                og:locale
helpers/seo/tripDetailSEOUtils.js    line 34                 og:locale
helpers/seo/operatorDetailSEOUtils.js line 42                og:locale
components/FrontPage/Seo.js          line 59                 og:locale
pages/about/index.js                 line 49                 og:locale + add TravelAgency schema
pages/homepagev2.js                  line 265                extend sameAs (GBP, Naver, LINE OA, YouTube)
components/layout/footer.js          line 56                 TAT license already here → move to schema identifier
BlogPostSchemaGenerator.js           line 21–23              normalize sameAs array
public/llms.txt                                              enrich: TAT license, VAT, stats, founding year
```

---

## Verification Additions (post r3 checklist)

Add to r3 verification section:
- `grep "faqMainEntity\|FAQPageJsonLd" FilterTripsSEO.js` — confirm render block exists
- `curl /ref/article/{slug}` — confirm 200 (not 404) after ISR fix
- `curl /help/faqs` — confirm FAQPage in `<script type="application/ld+json">`
- Check `about/index.js` for `TravelAgency` JSON-LD in SSR HTML
- `grep "og:locale" _app.js dayTripSEOUtils.js tripDetailSEOUtils.js operatorDetailSEOUtils.js` — all `en_US`
- `cat public/llms.txt` — confirm TAT license, VAT, founding year present

---

*Reviewed by: SEO-specialist · AEO-specialist · GEO-specialist agents · 2026-06-22*
*Source audit: `01-projects/seo-aeo-geo-live-audit-2026-06-22/`*
