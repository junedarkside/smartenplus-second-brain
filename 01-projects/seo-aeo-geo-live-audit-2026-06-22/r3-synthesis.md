---
title: "SEO / AEO / GEO Live Production Audit 2026-06-22"
type: audit
status: open
date: 2026-06-22
scope: live-production
target: https://www.smartenplus.co.th
last-updated: 2026-06-26
update-source: r4-peer-review + r5-live-reaudit + r6-external-reconciliation + r7-code-review
---

# Live Production SEO / AEO / GEO Audit — 2026-06-22

> **Updated 2026-06-22** after live re-audit (r5) + peer review (r4). Several findings from the original audit were wrong. See [[r4-peer-review]] and [[r5-live-reaudit]] for full correction log. Struck-through items are superseded.

> ⚠️ **r6 correction (2026-06-25):** **P0-A (AI crawler block) is now OBSOLETE.** A live robots.txt fetch on 2026-06-25 shows all 10 AI UAs `Allow: /` with no Cloudflare managed block — the CF "AI Scrapers and Crawlers" toggle was disabled since r5. The GEO ceiling is lifted; revise **3/10 → ~6–7/10**. Re-confirm with `curl /robots.txt` before closing. A third-party external audit was also reconciled against code in r6 — it corroborates r1–r5 and surfaces net-new defects (help `[...slug]` notFound, destinations `station_name` guard, manifest Thai, `availableLanguage:["en","th"]`), but ~50% of its fixes are wrong-as-written (assumes App Router; repo is Pages Router) and its `/operators` canonical claim is a false-positive. Full scorecard: [[r6-external-reconciliation-2026-06-25]].

> **r7 code re-review (2026-06-26):** all r6-r9 fixes verified landed + correct; `FaqJsonLd` build-break regression cleared repo-wide. Re-scores **SEO 6.5→8.2 · AEO 3.5→6.5 · GEO 3.0→5.5**. 2 coverage-miss regressions found — r6/r7 fixes were incomplete: `useRouteSeo.js:76` still `availableLanguage:['English','Thai']`, `useDayTripSEO.js:166` still `locale:'th_TH'`. Plus title double-brand (6 pages) + vault doc line 80. Full table + backlog delta: [[r7-code-review-2026-06-26]].

## Summary

Whole-site **live production** audit of `https://www.smartenplus.co.th` across three lenses. Distinct from prior per-page **code-scoped** audits (trip detail, operator, route) — this measures what the public web and AI/answer engines actually receive today.

**Composite scores (live re-audit 2026-06-22):**
- **SEO (Technical): 6.5/10** — foundations strong; sitemap poison unresolved; /help canonical/og still broken; double-brand on 4 pages; og:locale th_TH site-wide.
- **AEO (Answer Engine): 3.5/10** — ~~bimodal; product pages excellent~~ **CORRECTED:** route listing has zero FAQPage in HTML (FilterTripsSEO drops prop); /help/faqs FAQPage empty (WP GraphQL broken); activity detail FAQ text SSR-visible but no schema. Only homepage ItemList schemas are new positives.
- **GEO (Generative Engine): 3/10** — ~~1.5/10~~ raised: taxID/sameAs confirmed present, CitationSection URLs correct, llms.txt exists, /ref pages return 200. P0-A (AI crawler block) still fully active — caps effective ceiling.

**One-line thesis:** Site is **still invisible to all generative engines** (robots block unchanged), has **41 sitemap-0.xml URLs 404ing**, and the route-listing + /help/faqs FAQ schemas that the original audit counted as "working" are **both broken in production**. The real fix count is higher than originally estimated.

## The 3 decisive findings (read these first)

### 🔴 P0-A · robots.txt blocks all AI crawlers → GEO = ~0 (Cloudflare)
`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `meta-externalagent`, `Bytespider`, `Applebot-Extended`, `Amazonbot` all `Disallow: /`. **Live verified 2026-06-22 — UNCHANGED.** A new `Content-Signal: search=yes,ai-train=no` directive appeared (Cloudflare EU DSM Article 4) but does NOT replace explicit per-crawler rules. **Fix: Cloudflare dashboard → Security → Bots → "AI Scrapers and Crawlers" → DISABLE.** Keep `ai-train=no`. Add frontend allowlist to `next-sitemap.config.js` robots section as backup (if CF removed, next deploy would lose the policy). Full evidence + spec: [[r1-geo]].

### 🔴 P0-B · 41 `/ref/article/*` URLs in sitemap-0.xml return 404 — **URL direction was inverted in original audit**
~~Bonus bug: pages self-canonical to `/ref/{slug}` (wrong path; real URL is `/ref/article/{slug}`)~~

**CORRECTED (live verified 2026-06-22):** The live URL format is `/ref/{slug}` (no `/article/` segment) — these return **HTTP 200**. The path `/ref/article/{slug}` is what 404s. `server-sitemap.xml` correctly uses `/ref/{slug}`. `CitationSection.js` correctly generates `/ref/${slug}` URLs.

**What is actually broken:** `sitemap-0.xml` lists 41 `/ref/article/{slug}` URLs — these 404. Fix is to regenerate sitemap-0 to use `/ref/{slug}` format (matching `server-sitemap.xml`), not the other way around. The page component at `pages/ref/article/[slug].js:91` sets `canonical: https://www.smartenplus.co.th/ref/${slug}` — this is correct (canonical matches live URL); the original audit's "wrong path" call was backwards.

Root cause + fix: [[r5-live-reaudit]].

### 🔴 P0-C · `/help` ships zero schema + canonical → apex host; `/help/faqs` FAQPage broken in prod
`pages/help/index.js:21` hardcodes `canonical: 'https://smartenplus.co.th/help'` (apex, 301→www = canonical chain); `og:url` = homepage root (not /help); title double-brands; zero JSON-LD. **Live verified unchanged.**

~~`/help/faqs` has working SSR FAQPage schema~~ **CORRECTED:** `/help/faqs` FAQPage schema is present in SSR HTML but `mainEntity: []` — the WordPress GraphQL query `POSTS_BY_FAQ_CATEGORY` returns empty data in production. A FAQPage with zero Q/A pairs is invalid for rich results and may be penalized. Additionally, `og:url` on `/help/faqs` also points to homepage root. **Fix requires two steps:** (1) debug WP GraphQL data fetch, (2) fix `og:url` on both /help pages.

## Prioritized action list (corrected)

### P0 — do first
| # | Action | Lens | File(s) | Effort |
|---|--------|------|---------|--------|
| 1 | Disable CF "AI Scrapers and Crawlers" toggle + add frontend robots allowlist as backup | GEO | Cloudflare dashboard + `next-sitemap.config.js` | 10 min |
| 2 | Remove `/ref/article/*` from `sitemap-0.xml`; redeploy + clear ISR cache | SEO | `next-sitemap.config.js` | 30 min |
| 3 | `/help/index.js`: fix canonical→www, fix `og:url`→`/help`, drop double-brand from title | SEO/AEO | `pages/help/index.js:19-23` | 30 min |
| 4 | Debug `/help/faqs` WordPress `POSTS_BY_FAQ_CATEGORY` GraphQL returning empty; fix `og:url` on /help/faqs | AEO | `pages/help/faqs.js` + WP backend | 1–2 hr |

### P1 — high value
| # | Action | Lens | File(s) | Note |
|---|--------|------|---------|------|
| 5 | Fix `FilterTripsSEO.js:41–55` — render `faqMainEntity` prop + move FAQ data from `useRouteSeo` hook to `getStaticProps` | AEO | `components/trips/search/FilterTripsSEO.js`, trips page | Prop silently dropped; route listing has zero FAQPage live |
| 6 | Wire `generateFAQSchema` into activity detail `getStaticProps` + `DayTripDetailSEO.js` | AEO | `pages/activities/detail/[...slug].js:124–139`, `DayTripDetailSEO.js` | Schema util exists at `dayTripSEOUtils.js:321`; just not wired |
| 7 | Fix `og:locale: 'th_TH'`→`'en_US'` across all 6 files | SEO | `pages/_app.js:41`, `helpers/seo/dayTripSEOUtils.js:126`, `helpers/seo/tripDetailSEOUtils.js:34`, `helpers/seo/operatorDetailSEOUtils.js:42`, `components/FrontPage/Seo.js:59`, `pages/about/index.js:49` | ~~1 line~~ **6 files** — page-level utils override DefaultSeo |
| 8 | `/airport-transfer`: add BreadcrumbList + FAQPage schema; fix double-brand title | SEO/AEO | `pages/airport-transfer/index.js:51` | Station list already SSR-rendered; schema entirely absent |
| 9 | Add homepage FAQPage (4–6 Q/A, SSR) via `SEOSection.js` | AEO | `pages/homepagev2.js`, `components/SEO/SEOSection.js` | Component exists, unused |
| 10 | Add `about/index.js` `TravelAgency` schema with TAT license `identifier` | GEO | `pages/about/index.js` | Currently zero JSON-LD; TAT/VAT data exists in page text |
| 11 | Fix `help/[...slug].js:82` canonical collapse — all /help/* category pages self-canonical to /help root | SEO | `pages/help/[...slug].js:82` | Higher-impact than index.js apex bug |

### P2 — polish
| # | Action | Lens | Note |
|---|--------|------|------|
| 12 | Enrich `public/llms.txt` — add TAT license 11/06622, VAT 0105554078213, founding year, route/operator stats | GEO | File exists (200 OK) — content-thin only |
| 13 | Normalize `sameAs` array across all schema nodes — `homepagev2.js` (3 entries), `/blog` Organization (1), `BlogPostSchemaGenerator.js` (1) | GEO | Add GBP URL, Wikidata, Naver, LINE OA, YouTube |
| 14 | Add TAT license as `identifier` PropertyValue in homepage TravelAgency schema | GEO | `homepagev2.js:265` — `taxID` already present; TAT license missing |
| 15 | Blog: consolidate dual-origin (main domain + blog.smartenplus.co.th WP); fix duplicate `@graph` schema conflict | SEO/GEO | Two competing BlogPosting schemas on blog post pages |
| 16 | Add `definedTerm`/glossary content to `/ref` pages | AEO/GEO | |

### ~~Removed from action list~~
- ~~Action #8 "Add sameAs/taxID/areaServed"~~ — `homepagev2.js:243–265` already has all three. **Done.**
- ~~Action #12 "Confirm operators/locations in sitemap"~~ — `server-sitemap.xml` already covers both (36 + 176 URLs). **Done.**
- ~~Action #14 "Add llms.txt"~~ — `/public/llms.txt` exists (HTTP 200). Changed to "enrich" (P2 above).

## Lens scores

| Lens | Original score | Live re-audit score | Key delta |
|------|:---:|:---:|---|
| SEO (Technical) | **7/10** | **6.5/10** | /help og:url = root (not /help), /help/faqs og:url = root, double-brand on 4 pages confirmed |
| AEO | **5.5/10** | **3.5/10** | Route listing 8.5→2/10 (FAQPage prop dropped); /help/faqs 0→1/10 (empty mainEntity); activity detail 7→5/10 |
| GEO | **1.5/10** | **3/10** | taxID/sameAs/CitationSection/llms.txt/ref-pages all confirmed present; AI block unchanged |

### AEO per-page scores (corrected)

| Page | Original | Corrected | Reason |
|---|:---:|:---:|---|
| Homepage | 3/10 | 4/10 | +1: ItemList schemas (routes + destinations) added |
| /help index | 2/10 | 2/10 | Unchanged — zero JSON-LD confirmed |
| /help/faqs | (not scored) | 1/10 | FAQPage present but `mainEntity:[]`; WP GraphQL broken |
| Activity detail | 7/10 | 5/10 | FAQ text in SSR HTML; zero FAQPage schema |
| Route listing | 8.5/10 | 2/10 | FilterTripsSEO drops faqMainEntity; zero JSON-LD in prod HTML |
| Airport transfer | 5/10 | 3/10 | Zero JSON-LD confirmed; station data SSR but not schematized |

## CWV snapshot (homepage, headless — real-user floor)
Desktop: TTFB 1023ms · FCP 1284ms · LCP 1628ms · CLS 0 · 935KB / 98 JS req / 139 total. Mobile (iPhone 13): TTFB 1155ms · FCP 1384ms · LCP 1716ms · CLS 0 · 943KB / 62 JS req. No render-blocking scripts; hero preloaded `fetchpriority=high`. JS bundle fragmentation (98 chunks desktop) is the persistent risk. Full table + caveats: [[r1-seo]]. **Recommend real PSI/CrUX field-data pass** (this run underestimates throttled mobile).

## What's actually good (live-verified)
- `/ref/{slug}` pages return HTTP 200 with Article schema — the citation system works.
- `CitationSection.js` generates correct `/ref/${slug}` URLs — the peer review's "URL bug" claim was wrong.
- Homepage TravelAgency schema: `taxID`, `sameAs` (3 social), `areaServed` all present.
- `public/llms.txt` exists (HTTP 200) — product description present.
- `server-sitemap.xml`: operators (36) + locations (176) + activities + trips + /ref + /help all indexed.
- Security headers, HSTS preload, CSP, ISR warmth, Cloudflare CDN/HTTP2/h3, image preload/lazy/`fetchpriority`.
- Homepage ItemList schemas for routes and destinations (new since r1 audit).

## ~~What's already good (original — partially wrong)~~
- ~~"Trip-detail + route-listing schema is best-in-class (FAQ live, prior fix working). They are the model."~~
  **CORRECTED:** Route listing has zero FAQPage in live HTML. Trip detail is fine; remove route listing from "model pages."

## Cross-references — UPDATE vs cite
**Cite (no edit):** [[trip-detail-seo-aeo-geo-audit-2026-06-16]] · [[operator-detail-seo-aeo-geo-audit]] · [[seo-sitemap-whole-site-audit-2026-06-11]] · [[canonicalization-audit-checklist]] · [[core-web-vitals-budget]] · [[build-experience-faq-items-pure-function]] · [[isr-client-rtk-stats-seo-pattern]] · [[nextseo-v6-jsonld-silent-drop]] · [[og-image-1200x630-webp]] · [[gsc-crawled-not-indexed-investigation-2026-06-05]].

**Consider UPDATE after fixes land:**
- [[frontend-url-canonical-www-not-apex]] — `/help` apex-canonical live instance; add example once fixed.
- [[wordpress-faqpage-deprecation-note]] — tie to `/help/faqs` WP GraphQL empty-data fix decision.
- [[canonicalization-audit-checklist]] — add "sitemap URLs must match live URL format exactly" + "FAQPage mainEntity must be non-empty."
- [[trip-route-page-seo-aeo-geo-audit]] — update: route listing FAQPage not live (FilterTripsSEO drops prop).

## Verification (post-implementation)
1. `curl /robots.txt` — no AI-UA `Disallow: /` lines (P0-A lifted).
2. `curl /sitemap-0.xml | grep ref/article` — zero results (P0-B sitemap poison cleared).
3. `curl /help` — canonical = `https://www.smartenplus.co.th/help`, `og:url` = `https://www.smartenplus.co.th/help`, single brand in title.
4. `curl /help/faqs` — FAQPage `mainEntity` non-empty (≥1 Q/A), `og:url` = `/help/faqs`.
5. `curl /trips/bkk-phuket | grep FAQPage` — FAQPage present in SSR HTML (P1-5 fix verified).
6. `curl /activities/detail/{slug} | grep FAQPage` — FAQPage present.
7. `grep "og:locale" _app.js dayTripSEOUtils.js tripDetailSEOUtils.js operatorDetailSEOUtils.js FrontPage/Seo.js about/index.js` — all `en_US`.
8. `cat public/llms.txt | grep -i "TAT\|11/06622\|founding"` — credentials present.
9. Re-run PSI/CrUX for field data.
10. GSC + Perplexity/ChatGPT spot-check for citations over 1–2 weeks after P0-A fix.

## Out of scope
- Applying any fix (this audit is read-only; specs drafted only).
- Backend entity/serializer changes flagged in prior page audits.
- GSC live data (no access).

---
**Raw findings:** [[r1-seo]] · [[r1-aeo]] · [[r1-geo]]  ·  **Peer review:** [[r4-peer-review]]  ·  **Live re-audit:** [[r5-live-reaudit]]  ·  Audit folder: `01-projects/seo-aeo-geo-live-audit-2026-06-22/`
