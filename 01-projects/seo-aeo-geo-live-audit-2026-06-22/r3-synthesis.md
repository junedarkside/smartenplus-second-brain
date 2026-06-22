---
title: "SEO / AEO / GEO Live Production Audit 2026-06-22"
type: audit
status: open
date: 2026-06-22
scope: live-production
target: https://www.smartenplus.co.th
---

# Live Production SEO / AEO / GEO Audit — 2026-06-22

## Summary

Whole-site **live production** audit of `https://www.smartenplus.co.th` across three lenses. Distinct from prior per-page **code-scoped** audits (trip detail, operator, route) — this measures what the public web and AI/answer engines actually receive today.

**Composite scores:**
- **SEO (Technical): 7/10** — foundations strong; one P0 sitemap-poison defect + page-level canonical/title/schema regressions.
- **AEO (Answer Engine): 5.5/10** — bimodal. Product pages excellent (FAQ live in SSR), hub pages (/help, home, airport) have zero FAQ + client-only content.
- **GEO (Generative Engine): 1.5/10** — almost entirely gated by a single defect: **`robots.txt` blocks every AI crawler** (Cloudflare-managed). The site is invisible to ChatGPT, Claude, Gemini, Perplexity, Meta AI.

**One-line thesis:** Strong latent SEO/AEO quality on booking pages, but the site is **deliberately invisible to all generative engines**, has **41 sitemap URLs 404ing**, and its **two highest-intent Q&A pages ship zero structured data**. Fixing 4 frontend files + 1 Cloudflare toggle unlocks the bulk of the value.

## The 3 decisive findings (read these first)

### 🔴 P0-A · robots.txt blocks all AI crawlers → GEO = ~0 (Cloudflare)
`GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot`, `meta-externalagent`, `Bytespider`, `Applebot-Extended`, `Amazonbot` all `Disallow: /`. Auto-injected by Cloudflare ("BEGIN Cloudflare Managed content"); frontend `next-sitemap.config.js` cannot override it. → Site cannot appear in any AI answer. **Fix: Cloudflare dashboard → Security → Bots → "AI Scrapers and Crawlers" → DISABLE.** Keep `ai-train=no`. Drafted frontend allowlist in [[r1-geo]] for clarity/drift-resistance. Full evidence + spec: [[r1-geo]].

### 🔴 P0-B · 41 `/ref/article/*` URLs in sitemap return 404 (sitemap poison)
10/10 sampled 404. Pre-rendered at build from WP slugs that no longer resolve; `next-sitemap` wrote them; `getStaticProps` returns `notFound`. Bonus bug: those pages self-canonical to `/ref/{slug}` (wrong path; real URL is `/ref/article/{slug}`). Crawl-budget waste + "Crawled, not indexed" surface. Also kills the site's best GEO/AEO reference content. Root cause + fix: [[r1-seo]] SEO-1.

### 🔴 P0-C · `/help` (the FAQ hub) ships zero schema + canonical → apex host
`pages/help/index.js:21` hardcodes `canonical: 'https://smartenplus.co.th/help'` (apex, which 301→www = canonical chain); `og:url` inherits homepage; title double-brands; Q/A content is client-only (`ssr:false` breadcrumb + WP fetch). The single highest-AEO-ROI page on the site is the worst-marked-up. Fix: [[r1-aeo]] + [[r1-seo]] SEO-2.

## Prioritized action list

### P0 — do first (highest impact, frontend + 1 infra)
| # | Action | Lens | File(s) | Effort |
|---|--------|------|---------|--------|
| 1 | Disable CF "AI Scrapers and Crawlers" toggle (allow grounding, keep `ai-train=no`) | GEO | Cloudflare dashboard | 5 min |
| 2 | Remove 404 `/ref/article/*` from `sitemap-0.xml`; fix canonical `/ref/{slug}`→`/ref/article/{slug}`; redeploy + clear ISR cache | SEO/GEO | `pages/ref/article/[slug].js:91`, `next-sitemap.config.js`, deploy | 1–2 hr |
| 3 | `/help`: fix canonical→www, fix `og:url`, add FAQPage schema, SSR the Q/A list, drop double-brand from title | SEO/AEO | `pages/help/index.js:19-23` | 2–3 hr |
| 4 | Add homepage FAQPage (6–8 Q/A in SSR HTML) | AEO | homepage SEO (`components/SEO/JsonLd.js` / `generateFAQSchema`) | 2 hr |
| 5 | Fix `og:locale: 'th_TH'`→`'en_US'` site-wide | SEO | `pages/_app.js:41` | 1 line |

### P1 — high value
| # | Action | Lens | File(s) |
|---|--------|------|---------|
| 6 | `/airport-transfer`: add ItemList + FAQPage schema; SSR station list; drop "Page 1" + leading brand from title | SEO/AEO | `pages/airport-transfer/index.js:51` |
| 7 | Activity/day-trip detail: add FAQPage (reuse `helpers/seo/dayTripSEOUtils.js`); trim 131-char title | AEO | activity detail SEO util |
| 8 | Add Organization `sameAs` (GBP, social, Naver) + `taxID`/`identifier` (TAT 11/06622) + `areaServed: TH` | GEO | `components/SEO/LocalBusinessSchema.js` / homepage org node |
| 9 | Route-listing title 76 chars → trim to ≤60 | SEO | `helpers/seo/*SEOUtils.js` |
| 10 | Stop double-brand: pages pass bare title, template adds `\| SmartEnPlus` (`help`, `airport-transfer`, 404) | SEO | `pages/help/index.js:19`, `pages/airport-transfer/index.js:51` |
| 11 | Grow + recent-ize reviews (citation trust) | GEO/AEO | review pipeline |

### P2 — polish
| # | Action | Lens |
|---|--------|------|
| 12 | Confirm `/operators/*`, `/locations/*` in `server-sitemap.xml` (absent from `sitemap-0`) | SEO |
| 13 | Blog: consolidate to `/blog` OR ensure AI-allow on subdomain; fix WP double-brand + empty desc | SEO/GEO |
| 14 | Add `llms.txt` | GEO |
| 15 | Deduplicate security headers (CF + Next layering) | SEO |
| 16 | Add `definedTerm`/glossary (restore `/ref` terminology) | AEO/GEO |

## Lens scores

| Lens | Score | Why |
|------|------:|-----|
| SEO (Technical) | **7/10** | canonical/og/sitemap/security/ISR/CWV healthy; minus sitemap-poison, /help canonical, og:locale, title regressions |
| AEO | **5.5/10** | trip detail + route listing = 8–8.5; homepage/help/airport = 2–5 |
| GEO | **1.5/10** | gated by robots block; strong latent schema but invisible to engines |

## CWV snapshot (homepage, headless — real-user floor)
Desktop: TTFB 1023ms · FCP 1284ms · LCP 1628ms · CLS 0 · 935KB / 98 JS req / 139 total. Mobile (iPhone 13): TTFB 1155ms · FCP 1384ms · LCP 1716ms · CLS 0 · 943KB / 62 JS req. No render-blocking scripts; hero preloaded `fetchpriority=high`. JS bundle fragmentation (98 chunks desktop) is the persistent risk. Full table + caveats: [[r1-seo]]. **Recommend real PSI/CrUX field-data pass** (this run underestimates throttled mobile).

## What's already good (don't touch)
- Trip-detail + route-listing schema is best-in-class (FAQ live, prior fix working). They are the model.
- Security headers, HSTS preload, CSP, ISR warmth, Cloudflare CDN/HTTP2/h3, image preload/lazy/`fetchpriority`.
- Sitemap cleanup to 107 URLs (post [[seo-sitemap-whole-site-audit-2026-06-11]]).

## Cross-references — UPDATE vs cite
**Cite (no edit):** [[trip-detail-seo-aeo-geo-audit-2026-06-16]] · [[operator-detail-seo-aeo-geo-audit]] · [[trip-route-page-seo-aeo-geo-audit]] · [[seo-sitemap-whole-site-audit-2026-06-11]] · [[canonicalization-audit-checklist]] · [[core-web-vitals-budget]] · [[build-experience-faq-items-pure-function]] · [[isr-client-rtk-stats-seo-pattern]] · [[nextseo-v6-jsonld-silent-drop]] · [[og-image-1200x630-webp]] · [[gsc-crawled-not-indexed-investigation-2026-06-05]].

**Consider UPDATE after fixes land:**
- [[frontend-url-canonical-www-not-apex]] — the `/help` apex-canonical is a live instance of this atom; add a `/help` example once fixed.
- [[wordpress-faqpage-deprecation-note]] — tie to `/help` re-markup decision (raw `<script>` not `<NextSeo jsonLd>`).
- [[canonicalization-audit-checklist]] — add "sitemap URLs must resolve (no 404)" check from SEO-1.

## Verification (post-implementation, future)
1. `curl /robots.txt` shows no AI-UA `Disallow: /` (GEO-1 lifted).
2. `/ref/article/*` removed from `sitemap-0.xml`; remaining resolve 200; canonical path-correct.
3. `/help` canonical = www, `og:url` = /help, FAQPage present in SSR HTML, single brand in title.
4. Homepage FAQPage present in SSR HTML.
5. `og:locale` = `en_US` across templates.
6. Re-run this Playwright CWV script with throttling + PSI for field data.
7. GSC + Perplexity/ChatGPT spot-check for citations over 1–2 weeks.

## Out of scope
- Applying any fix (this audit is read-only; specs drafted only).
- Backend entity/serializer changes flagged in prior page audits.
- GSC live data (no access).

---
**Raw findings:** [[r1-seo]] · [[r1-aeo]] · [[r1-geo]]  ·  Audit folder: `01-projects/seo-aeo-geo-live-audit-2026-06-22/`
