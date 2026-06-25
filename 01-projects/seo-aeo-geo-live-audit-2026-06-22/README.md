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

## Architecture
Pages Router + next-seo. Load-bearing gotchas: next-seo v6 silently drops the `jsonLd` prop ([[nextseo-v6-jsonld-silent-drop]]); page-level SEO utils override `DefaultSeo`; canonical must use `getSiteUrl()` (www, not apex) ([[seo-canonical-getsiteurl-pattern]]); `/ref/{slug}` is the live URL, `/ref/article/{slug}` 404s ([[ref-url-structure-live-vs-code]]). See [[structured-data-schema-patterns]].

## Active Tasks
- [x] r1 three-lens audit
- [x] r3 synthesis + r4 peer review + r5 live re-audit
- [x] r6 external-audit reconciliation (2026-06-25)
- [ ] **Re-confirm `curl /robots.txt`** — AI-crawler block reported lifted in r6; verify then close r3 P0-A
- [ ] SEO-P1 backlog: `/activities` canonical+NextSeo, help `[...slug]` notFound, destinations `station_name` guard, English `manifest.json`, `availableLanguage:["en"]`
- [ ] Lint fix: [[structured-data-schema-patterns]] line 75 `availableLanguage:["Thai","English"]` contradicts en-only policy

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
