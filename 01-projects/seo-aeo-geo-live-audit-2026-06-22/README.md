# Project: Live Production SEO/AEO/GEO Audit (smartenplus.co.th)

## Summary
Multi-round whole-site SEO/AEO/GEO audit of the live production customer site, plus reconciliation of a third-party external audit against real code.

## Status
active

## Context
Track what the public web + AI/answer engines actually receive from `https://www.smartenplus.co.th` today, across classic SEO, AEO (answer-engine), and GEO (generative-engine) lenses. Distinct from per-page code-scoped audits (trip detail, operator, route) archived under `08-archive/`. Findings flow into the `SEO-P1-BACKLOG` / `SEO-P2-FIXES` rows in [[master-state]].

## Stack
- Next.js **Pages Router** (Next.js 14, `pages/`, `next-seo` v6) — NOT App Router
- WordPress (headless, blog + help FAQs) at `blog.smartenplus.co.th` (legacy)
- Cloudflare CDN

## Key Files (rounds)
- `r1-seo.md` · `r1-aeo.md` · `r1-geo.md` — three-lens initial audit (2026-06-22)
- `r3-synthesis.md` — merged scores + prioritized action list (SEO 6.5, AEO 3.5, GEO 3.0)
- `r4-peer-review.md` — peer review of synthesis
- `r5-live-reaudit.md` — live HTTP-fetch verification (2026-06-22)
- `r6-external-reconciliation-2026-06-25.md` — third-party (Hermes) audit reconciled vs code
- `r7-code-review-2026-06-26.md` — code-level review post r6-r9 implementation
- `r8-live-prod-2026-06-26.md` — live prod verification post r6-r9 deploy (SEO 8.4 · AEO 7.5 · GEO 6.5)
- `r9-live-prod-2026-06-26.md` — 5-specialist live prod audit post r10a+r10b (SEO 8.3 · AEO 6.5 · GEO 6.8 · CWV 6.8 · SD 5.5)
- `r10-live-prod-2026-06-26.md` — 5-specialist live prod audit post r11 (SEO 9.0 · AEO 9.5 · GEO 9.0 · CWV 7.0 · SD 7.0)

## Architecture
Pages Router + next-seo. Load-bearing gotchas: next-seo v6 silently drops the `jsonLd` prop ([[nextseo-v6-jsonld-silent-drop]]); page-level SEO utils override `DefaultSeo`; canonical must use `getSiteUrl()` (www, not apex) ([[seo-canonical-getsiteurl-pattern]]); `/ref/{slug}` is the live URL, `/ref/article/{slug}` 404s ([[ref-url-structure-live-vs-code]]). See [[structured-data-schema-patterns]].

## Active Tasks
- [x] r1 three-lens audit
- [x] r3 synthesis + r4 peer review + r5 live re-audit
- [x] r6 external-audit reconciliation (2026-06-25)
- [x] r7 code review (2026-06-26)
- [x] r8 live prod verification post r6-r9 deploy (2026-06-26)
- [x] r9 5-specialist live prod audit post r10a+r10b (2026-06-26)
- [x] **`robots.txt` AI-crawler allowlist** — all 11 UAs confirmed Allow: / (r9 GEO-live)
- [x] `availableLanguage: ["en"]` ISO — r10a fix confirmed live on trip routes (r9)
- [x] BlogPosting stripped from trip routes — r10a fix confirmed live (r9)
- [x] 404 title de-duped — r10b fix confirmed live (r9)
- [x] **r11 P0: `/activities` zero JSON-LD + double-brand title** — verified live r10 ✅
- [x] **r11 P0: `/destinations/[slug]` soft-404** — verified live r10 ✅
- [x] **r11 P1: Homepage `aggregateRating` removed** — verified live r10 ✅
- [x] **r11 P1: Homepage `TravelAgency` TAT `identifier`** — verified live r10 ✅
- [x] **r11 P1: `public/llms.txt`** — cross-border + TAT/VAT + Activities verified live r10 ✅
- [x] **r11 P1: Homepage meta description ≤155 chars** — 152 chars verified live r10 ✅
- [ ] **r11 P0: `/help/faqs` FAQPage** — WP/GraphQL ops issue (still open)
- [x] r10 5-specialist live prod audit post r11 (2026-06-26)
- [ ] **r12 P1: `/activities` ItemList missing `numberOfItems: 6`** — `pages/activities/index.js`
- [ ] **r12 P1: Homepage `REVALIDATE_SECONDS = 60` → 3600** — `lib/homepage/constants.js`
- [ ] **r12 P1: S3 domains missing `preconnect`** — `pages/_document.js`
- [ ] **r12 P2: Destination meta description >155 chars** — `pages/destinations/[slug].js:189`
- [ ] **r12 P2: TravelAgency missing `currenciesAccepted: "THB"`** — `pages/homepagev2.js` + `pages/about/index.js`

## Decisions
- External audits are reconciled against live code before trusting (precedent: [[seo-audit-reconciliation-2026-06-21]]). ~40–50% of external findings carry wrong root cause or wrong fix idiom.
- The repo is Pages Router — any audit fix using `generateMetadata`/`notFound()`/App Router patterns is inapplicable.

## Related
- [[r3-synthesis]] · [[r6-external-reconciliation-2026-06-25]]
- [[seo-audit-reconciliation-2026-06-21]] · [[ref-url-structure-live-vs-code]] · [[sitemap-filter-by-inventory-or-recency]]
- [[nextseo-v6-jsonld-silent-drop]] · [[blog-canonical-url-wp-subdomain-bug]] · [[help-faqs-wp-graphql-broken-prod]]
- [[seo-canonical-getsiteurl-pattern]] · [[defaultseo-fallback-pattern]] · [[structured-data-schema-patterns]]
- [[master-state]] (SEO-P1/P2 backlogs)
- Sibling audits: [[operator-detail-seo-aeo-geo-audit]] · [[trip-route-page-seo-aeo-geo-audit]] · `08-archive/trip-detail-seo-aeo-geo-audit-2026-06-16/`
