---
name: seo-homepage-specialist-team
description: How to run the SEO specialist team review on the SmartEnPlus homepage. 3-role sequential audit (Structured Data + Technical SEO + Page Performance) synthesized by Leader into a vault report. Defines team composition, each specialist's scope, and invocation.
metadata:
  type: reference
---

# SEO Homepage Specialist Team

## Summary
3-specialist virtual team for deep SEO + performance audit of the SmartEnPlus homepage. Roles run sequentially inside one agent session. Leader synthesizes findings, debates conflicts, writes vault report.

## Context
Created 2026-05-21 after homepage UX/UI review (P0–P3 fixes complete). SEO infrastructure solid but has structured data errors and technical gaps not covered by UX review.

## Team Composition

| Role | Lens | Key Checks |
|------|------|-----------|
| **Specialist A — Structured Data** | JSON-LD schemas on the page | Hardcoded values, missing fields, invalid geo, stale dates, missing schema types |
| **Specialist B — Technical SEO** | Meta tags, sitemap, robots, _app.js | DefaultSeo gap, server-sitemap 404, og:locale, twitter:site, security headers |
| **Specialist C — Page Performance** | Core Web Vitals risks | CLS from ssr:false, hero banner swap, preconnect, LCP image, image sizes |
| **Leader** | Synthesis + conflict resolution | Debates cross-specialist conflicts, delivers verdict, writes vault report |

## How to Invoke

1. Start dev server: `npm run dev` → confirm http://localhost:3000 is live
2. Say: **"run seo team review on homepage"** or **"homepage seo audit"**
3. Agent `seo-homepage-auditor` runs phases A → B → C → Leader sequentially
4. Final report written to `01-projects/homepage-seo-performance-deep-review-YYYYMMDD.md`
5. Vault index + log updated, committed, pushed automatically

**Agent file:** `smartenplus-frontend/.claude/agents/seo-homepage-auditor.md`

## Pre-conditions
- Dev server running on port 3000 (agent self-checks, fails clearly if not)
- No other conditions — agent reads source files directly

## Known Issues Found on First Run (2026-05-21)
See [[homepage-seo-performance-deep-review-2026-05-21]] for full findings.

**Pre-identified gaps before audit:**
- TravelAgency `telephone` hardcoded fake number (`+66-2-123-4567`) — real number in `constants.js`
- TravelAgency `address` hardcoded `123 Sukhumvit` — not from any constant
- TravelAgency `aggregateRating` hardcoded `4.5/128` — live data already in component props
- TravelAgency `sameAs` missing — social URLs already exported from `constants.js`
- `WebPageJsonLd` `lastReviewed` hardcoded stale date (`2024-05-26`)
- No `WebSite` + `SearchAction` schema despite having a search form
- `server-sitemap.xml` handler missing — `next-sitemap.config.js` points to it but no `pages/server-sitemap.xml.js` exists → Google gets 404
- No `DefaultSeo` in `_app.js` — raw `<Head>` used; no global SEO fallback
- `og:locale`, `og:site_name`, `twitter:site` absent from `Seo.js`
- CLS risk: `DynamicProductSearchForm` with `ssr:false` inside `min-h-[300px]` hero

## Workflow Sequence

```
Phase 1: Specialist A
  → WebFetch http://localhost:3000 (extract all JSON-LD blocks)
  → Read: homepagev2.js, all *StructuredData.js files, constants.js
  → Output: FINDINGS_A (SD1–SDn)

Phase 2: Specialist B
  → WebFetch: /  /robots.txt  /sitemap.xml  /server-sitemap.xml
  → Read: _app.js, _document.js, Seo.js, next-sitemap.config.js, next.config.js
  → Output: FINDINGS_B (TS1–TSn)

Phase 3: Specialist C
  → WebFetch http://localhost:3000 (inspect img/link/script tags)
  → Read: FeaturedImageHeader.js, imageOptimization.js, homepagev2.js, package.json
  → Output: FINDINGS_C (PP1–PPn)

Phase 4: Leader
  → Read all findings
  → Debate cross-specialist conflicts (AggregateRating, server-sitemap, DefaultSeo, CLS)
  → Write vault report
  → Update index.md + log.md + commit + push
```

## Report Format

Follows same structure as [[homepage-ux-review-2026-05-21]]:
- Frontmatter (name, description, type: project)
- Summary (1-2 lines with issue counts)
- 3 specialist sections (findings labeled SD/TS/PP + severity + fix)
- Discussion (cross-specialist debates with Leader verdict)
- Leader Synthesis (2-3 paragraphs)
- Priority Fix Queue (P0–P4)
- Key Files + Related

## Related
- [[homepage-ux-review-2026-05-21]] — prior UX review (P0–P3 complete)
- [[homepage-seo-performance-deep-review-2026-05-21]] — first run report
- [[blog-seo-performance-2026-05-20]] — blog SEO patterns (WebSite+SearchAction to replicate)
- [[nav-header-redesign]] — header a11y patterns