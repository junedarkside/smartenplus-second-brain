---
name: website-audit-full-2026-06-06-overview
description: Full external website audit — SEO/speed scores, mobile UX, identity analysis, AI classification, 15 priority actions.
metadata:
  type: project
  date: 2026-06-06
  url: https://www.smartenplus.co.th/
  status: OPEN
---

# Full Website Audit — 2026-06-06

## Summary
External audit of smartenplus.co.th. SEO 75/100, Speed 40/100, Accessibility 85/100. Three critical speed blockers (308KB HTML, 10 sync scripts, 66 inline styles). Mobile has 13/18 touch targets below 44px minimum. Structured data is above average — TravelAgency + BusTrip + OfferCatalog correctly declared. Blog is outranking booking pages due to content depth gap.

## Context
Platform: Next.js 14, Thailand transport booking (bus, ferry, train, airport transfer, tours). Audit covers live production site. Scope: speed, SEO, mobile responsiveness, structured data, identity classification.

Prior code-level audit: [[homepage-seo-performance-deep-review]] (30 findings, file:line refs, structured data schema errors in code).

## SEO & Speed

→ Extracted to [[core-web-vitals-budget]] (HTML <100KB, all WebP+AVIF, async scripts, no inline `<style>`, font preload, explicit image dimensions). Scores: SEO 75/100, Speed 40/100, A11y 85/100. Speed: C1 HTML 308KB, C2 10 sync scripts, C3 66 inline style blocks. H1-H5 + M1-M4.

### Good — SEO ✅
Title, meta description, H1, heading hierarchy (H1×1, H2×9, H3×19), canonical URL, all OG tags, Twitter Card, robots meta, viewport, charset, all 36 images have alt text, skip links (×2), font-display swap, 35/36 images lazy-loaded, 6 external URLs only, Google site verification, semantic HTML (article×13, section×7, nav×2, main×2).

## Mobile Responsiveness

### Critical

**MC1: 13/18 Interactive Elements Below 44px (WCAG 2.5.5)**
| Element | W | H |
|---|---|---|
| THB currency button | 40px | 24px |
| Account dropdown | 40px | 40px |
| Swap button | 0px | 0px |
| Date picker | 0px | 0px |
| Passenger selector | 0px | 0px |
| Carousel prev/next | 0px | 0px |
0×0 = SVG icons in a11y tree with no hit area. Causes INP penalty (Core Web Vitals).
Fix: `min-height: 44px; min-width: 44px` on all `button` and `input`. `aria-label` on icon-only buttons.

**MC2: WhatsApp Button 20×20px**
Position: 3697px from top. Less than half WCAG minimum.
Fix: Wrap in 44×44px container or convert to sticky floating button.

**MC3: No Scroll-Snap on Carousels**
`overflow-x: visible`, `scroll-snap: none`, `flex-wrap: nowrap`. Horizontal swipe broken on mobile. Cards overflow off-screen.
Fix:
```css
.carousel-container {
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}
.carousel-card {
  scroll-snap-align: start;
  flex-shrink: 0;
}
```
See [[carousel-design-standard]] for Embla breakpoints/gap values.

### High

**MH1: Only 4 Mobile Media Queries**
CSS breakpoints for 375px, 480px, 640px only. Insufficient for responsive site.
Fix: Add 414px, 768px, 1024px. Use Tailwind `md:` `lg:` prefixes on all components.

**MH2: Fixed-Width Containers Without max-width**
`width: 1280px` with `maxW: "none"` overflow on mobile.
Fix: `max-w-[1200px]` at wrapper level.

**MH3: Search Form Overflows on Mobile**
From/To/Date/Passengers/SEARCH all in one row. Overflows at 375px.
Fix: Test at 375px, 414px, 428px. Stack inputs vertically or use `flex-wrap`.

### Medium

**MM1: Input Font Size 14px — Triggers iOS Zoom**
All inputs except one: `["16px", "14px", "14px", "14px", "14px"]`. iOS zooms on `<16px`.
Fix: All form inputs `font-size: 16px` minimum.

**MM2: H1 30px May Not Scale on Mobile**
`text-3xl` on narrow screens.
Fix: `text-2xl md:text-3xl` or `clamp()` for fluid typography.

### Good — Mobile ✅
Viewport meta, all 36 images have alt + srcset, 2 skip links, flex containers (not float), utf-8 for Thai.

## Identity Analysis

**Answer: Booking Platform — with blog identity crisis.**

| Section | Identity | Function |
|---|---|---|
| Homepage | Booking engine | Search form (From/To/Date/Passengers) |
| Destinations | Booking engine | 54 destinations, 173 stations |
| Routes | Booking engine | Route results with operators + prices |
| Experiences | Booking engine | Tours with booking + price filters |
| Guides | Blog | 15+ travel articles |
| Footer | Legitimate business | TAT License 11/06622, PCI DSS, VAT |

**Problem 1: Blog has more SEO authority than booking pages.**
Blog: 15+ articles, categories, search, dates, internal linking.
Booking pages: no structured data on route detail pages, thin product descriptions, no FAQ schema, no review snippets.
Google sees rich blog + thin booking engine → blog wins rankings.

**Problem 2: Blog drives traffic but doesn't convert.**
Articles about "Pai motorbike safety" attract informational queries with no path to book.
Fix: Add inline booking CTAs in blog posts. E.g. bottom of "Pai Curves" article: "Ready to book? Book a bus from Chiang Mai to Pai →"

**Problem 3: Brand name inconsistency.**
Logo: "SmartEnPlus" (with "e"). URL: "smartenplus.co.th" (without "e").
Fix: Choose one. Prefer "SmartEnPlus".

## AI Recognition (Structured Data)

SmartEnPlus already classified as booking platform by AI. Schema.org markup above average for Thai travel sites.

### Structured Data Inventory (9 JSON-LD blocks)
| Schema Type | Count | AI Impact |
|---|---|---|
| TravelAgency | 3× | Strong — declares business type |
| BusTrip | 8× | Very strong — structured inventory |
| TouristDestination | 6× | Strong — geographic context |
| OfferCatalog + Offer | 4+ | Strong — what you sell |
| Service | 5+ | Strong — product type |
| Review / AggregateRating | 16 reviews | Strong — trust signals |
| FAQPage | 1 | Medium — authority signals |
| WebPage | 1 | Basic — page classification |
| BreadcrumbList | 1 | Medium — site structure |

BusTrip schema is the gold standard — each route has departure/arrival locations, times, operator. TravelAgency has registered Thai address + phone + taxID.

### What's Missing for Full AI Classification
| Missing | Why It Matters |
|---|---|
| Price in BusTrip/Offer | Google can't see "From THB 700" — no Product rich results |
| Product schema on Experience pages | Tours have no price/offer schema |
| Reservation/Order hints | No signals bookings actually happen on-site |
| BreadcrumbList on route pages | Only homepage has it |
| FAQPage content matching schema | 5 Question entities in schema, no matching visible FAQ |

## Priority Actions

### Critical (Fix First)
| # | Issue | Impact | Effort |
|---|---|---|---|
| 1 | 10 sync scripts blocking render | LCP -1.5s, INP bad | 2 hrs |
| 2 | 66 inline style blocks | FCP blocked | 3 hrs |
| 3 | 18 non-WebP images | LCP -1.5s | 4 hrs |
| 4 | 13/18 touch targets <44px | INP penalty, a11y fail | 1 hr |
| 5 | 14px input font triggers iOS zoom | Broken mobile UX | 30 min |

### High Priority
| # | Issue | Impact | Effort |
|---|---|---|---|
| 6 | Add Product schema to Experience tours | AI classification, rich results | 2 hrs |
| 7 | Add price to BusTrip Offer | Product rich results eligibility | 1 hr |
| 8 | Fix carousel overflow-x: visible → auto + scroll-snap | Mobile swipe UX | 1 hr |
| 9 | Hamburger nav at ≤768px | Mobile nav | 2 hrs |
| 10 | Add booking CTAs to blog posts | Conversion path | 2 hrs |

### Medium Priority
| # | Issue | Impact | Effort |
|---|---|---|---|
| 11 | Font preload hints for Inter | FCP -0.3s | 30 min |
| 12 | Add keywords meta tag | Thai/Bing SEO | 10 min |
| 13 | Fix brand name consistency | Brand consistency | 1 hr |
| 14 | BreadcrumbList on route pages | SEO + navigation | 1 hr |
| 15 | FAQPage content matching schema | Featured snippets | 2 hrs |

### Estimated Speed Improvement
| Fix | LCP | FCP |
|---|---|---|
| Images → WebP/AVIF | -1.5s | -0.8s |
| Async scripts | -0.5s | -1.2s |
| Self-host fonts | -0.3s | -0.4s |
| Font preload | -0.2s | -0.3s |
| **Total potential** | **-2.5s** | **-2.7s** |

### Mobile Testing Checklist
- [ ] iPhone SE (375px) — Search form overflow?
- [ ] iPhone 14 (390px) — Nav items wrap or overflow?
- [ ] Samsung Galaxy S21 (360px) — Carousel swipe works?
- [ ] iPad Mini (768px) — Hamburger menu visible?
- [ ] Tap WhatsApp — Opens on mobile?
- [ ] Focus input on iOS Safari — Page zooms in?

## Overall Verdict
SmartEnPlus is a legitimate booking platform.
- Strong: Schema.org structured data, TAT License 11/06622, real booking functionality
- Weak: Blog winning SEO over booking pages (content depth), Speed 40/100 (308KB HTML, 10 blocking scripts, 66 inline styles), Mobile touch target failures
- Priority order: Fix speed → fix mobile touch targets → add booking CTAs to blog → add Product schema to tours

## Related
[[homepage-seo-performance-deep-review]] · [[structured-data-schema-patterns]] · [[carousel-design-standard]] · [[nextjs-patterns]] · [[seo-homepage-specialist-team]] · [[blog-seo-performance]]

---

# Team Review & Implementation Plan

**Reviewed by:** website-audit-team-orchestrator (3 specialists + skeptic + leader)
**Date:** 2026-06-06
**Session:** #56
**Working files:** [[r1-performance]] · [[r1-mobile-ux]] · [[r1-seo-ai]] · [[r2-skeptic]] · [[r3-leader-synthesis]]

## Summary

15 audit issues → **12 final implementation items** across 3 sprints. Top 3 wins: iOS zoom fix (14px→16px inputs, 30 min), WCAG 44×44 touch targets (1-2 hrs), self-host Inter font via `next/font` (2-3 hrs). 6 audit claims reclassified as ALREADY DONE (compress, WebP config, GTM deferred, InArticleCTA, ProductJsonLd on Experience, BreadcrumbList on Experience). Total ~18 hrs frontend work.

## Pre-Flight Wins (NOT work to do)

6 audit items already addressed in current codebase:

| Audit ID | Item | Evidence |
|----------|------|----------|
| C1 | compress: true | `next.config.js:8` |
| H1 | WebP/AVIF formats | `next.config.js:16` + `helpers/imageOptimization.js:41-53` |
| M4 | GTM deferred | `pages/_app.js:80-85` `strategy="afterInteractive"` |
| Identity P2 | InArticleCTA exists | `components/blog/InArticleCTA.js` used in `BlogPostDisplay.js:200, 217` |
| AI Gap 2 | ProductJsonLd on Experience | `components/activities/detail/DayTripDetailSEO.js:31` |
| AI Gap 3 | BreadcrumbList on Experience | `components/activities/detail/DayTripDetailSEO.js:34` |

## Specialist Verdicts (Top 3 per role)

### Performance/CWV Engineer (full: [[r1-performance]])

1. **PERF-1+3** — Inter via `next/font/google` (self-host) — `pages/_document.js:20-22` render-blocking, FCP -0.3s
2. **PERF-2** — 213 inline styles → extract `boxShadow` to `ELEVATION_TOKENS` in `designSystem.js` (top 5 files: ProfileMenu 20, OrderDetail 18, layout 14)
3. **PERF-6** — 14px `text-sm` in `ProductSearchForm2.js:231, 260, 283, 311, 329` → `text-base` (iOS zoom fix)

### Mobile UX & Accessibility Specialist (full: [[r1-mobile-ux]])

1. **MOB-1** — 14px search inputs (iOS auto-zoom) — `ProductSearchForm2.js:231+`, `SearchDialogTrigger.js:19`
2. **MOB-2** — 13/18 touch targets <44px (WCAG 2.5.5) — `TOUCH_TARGET` token in `designSystem.js:210-213` exists but unused. Test at 320px before merge.
3. **MOB-4** — Carousel scroll-snap broken — `lib/homepage/components/*Carousel.js` missing `align: 'start'` in Embla options

### SEO + AI Recognition Specialist (full: [[r1-seo-ai]])

1. **SEO-1** — Duplicate "Routes" in `navConfig.js:14-23` (5 min config fix)
2. **SEO-5** — Brand inconsistency: "SmartEnPlus" vs "smartenplus" — add `BRAND_NAME` constant, rename `smartenpus-...webp` typo
3. **SEO-3** — OG image `smartenplus.png` 250×50 too small — replace with `og-image.webp` 1200×630

## Skeptic Verdicts (Top 5 downgrades)

| Audit Claim | Skeptic Verdict | Reason |
|-------------|-----------------|--------|
| 10 sync scripts blocking FCP | DOWNGRADE to P3 | Only GTM via `next/script` exists. Already `afterInteractive`. Misread. |
| Only 4 mobile media queries | DROP | Tailwind JIT emits only USED breakpoints. No code change. |
| Blog lacks booking CTAs | DROP | InArticleCTA exists, used in `BlogPostDisplay.js:200, 217` |
| No Product schema on Experience | DROP | `DayTripDetailSEO.js:31` has `<ProductJsonLd>` |
| Hamburger nav ≤768px | DEFER | Major nav restructure — defer to [[nav-header-redesign]] |

## Final Priority Queue

### P0 — Critical (Sprint 1, ~3 hrs)

- [ ] **F1** — 14px input font → 16px (iOS zoom fix) — `ProductSearchForm2.js:231, 260, 283, 311, 329` + `SearchDialogTrigger.js:19`
- [ ] **F2** — 44×44px touch targets (WCAG 2.5.5) — `CurrencySelector.js:55`, `ProfileButton.js:367`, `CartButton.js:116`, swap/date/passenger buttons in `ProductSearchForm2.js`
- [ ] **F3** — WhatsApp 20×20px → 44×44 wrapper — `ShareButton.js:176-183`, `footer.js:18`, `Passenger.js:339-340`, `ContactUs.js:37`

### P1 — High impact (Sprint 2, ~7 hrs)

- [ ] **F4** — Self-host Inter via `next/font/google` (eliminates render-blocking CSS) — `pages/_document.js:20-22` + `pages/_app.js`
- [ ] **F5** — Carousel scroll-snap (`align: 'start'`) — `lib/homepage/components/*Carousel.js`
- [ ] **F6** — Dedupe "Routes" in navConfig — `constants/navConfig.js:14-23`
- [ ] **F7** — OG image to WebP 1200×630 — replace `smartenplus.png` 250×50 with `og-image.webp` 1200×630, update `_app.js:42-48`
- [ ] **F8** — Search form mobile overflow — `ProductSearchForm2.js` add `flex-wrap` + responsive stacking

### P2 — Structured data + identity (Sprint 3, ~6 hrs)

- [ ] **F9** — Inline style extraction (top 5 files) — `ProfileMenu.js:20` (boxShadow → `ELEVATION_TOKENS`), `OrderDetail.js` (18), `layout.js` (14)
- [ ] **F10** — Brand name consistency — add `BRAND_NAME` to `helpers/constants.js`, rename `smartenpus-...webp` → `smartenplus-...webp`
- [ ] **F11** — FAQPage content + schema — `pages/homepagev2.js:493-495` use `helpSubcategories` data, add visible FAQ section

### P3 — Polish (Sprint 4, ~2 hrs)

- [ ] **F12** — Fixed-width container audit — `grep -rn "width: 1280px\|w-\[1280px\]" components/ pages/` replace with `max-w-[1200px]`

## Sprint Plan

| Sprint | Days | Items | Effort |
|--------|------|-------|--------|
| **Sprint 1** | Day 1-2 | F1, F2, F3 (P0 batch) | ~3 hrs |
| **Sprint 2** | Day 3-4 | F4, F5, F6, F7, F8 (P1 batch) | ~7 hrs |
| **Sprint 3** | Day 5-7 | F9, F10, F11 (P2 batch) | ~6 hrs |
| **Sprint 4** | Day 8+ | F12 + mobile testing matrix | ~2 hrs |

**Total: ~18 hours frontend work over 8-10 days**

## File Change Inventory

| # | File | Changes | Effort | Risk |
|---|------|---------|--------|------|
| 1 | `components/search/ProductSearchForm2.js` | 14px→16px (5x), 44px buttons, mobile flex-wrap | 2 hrs | low |
| 2 | `components/search/SearchDialogTrigger.js` | 14px→16px | 5 min | low |
| 3 | `components/search/CurrencySelector.js` | 44px min-h/w | 15 min | low |
| 4 | `components/auth/ProfileButton.js` | 44px min-h/w | 15 min | low |
| 5 | `components/cart/CartButton.js` | 44px min-h/w | 15 min | low |
| 6 | `components/UI/ShareButton.js` | WhatsApp 44px wrapper | 15 min | low |
| 7 | `components/layout/footer.js` | WhatsApp 44px wrapper | 15 min | low |
| 8 | `components/search/Passenger.js` | WhatsApp 44px wrapper | 15 min | low |
| 9 | `components/pages-info/ContactUs.js` | WhatsApp 44px wrapper | 15 min | low |
| 10 | `pages/_app.js` | next/font Inter + DefaultSeo keywords + BRAND_NAME | 3 hrs | high |
| 11 | `pages/_document.js` | Remove font preconnect/stylesheet (next/font handles) | 5 min | low |
| 12 | `tailwind.config.js` | fontFamily.sans = `['var(--font-inter)']` | 5 min | low |
| 13 | `lib/homepage/components/*Carousel.js` | `align: 'start'` option | 1-2 hrs | low |
| 14 | `constants/navConfig.js` | Dedupe "Routes" | 5 min | low |
| 15 | `public/og-image.webp` | NEW asset (1200×630) | 30 min | n/a |
| 16 | `public/smartenpus-...webp` | RENAME → `smartenplus-...webp` (typo fix) | 5 min | low |
| 17 | `components/auth/ProfileMenu.js` | boxShadow → `ELEVATION_TOKENS` | 30 min | low |
| 18 | `components/order/OrderDetail.js` | 18 inline styles → audit | 1 hr | low |
| 19 | `components/layout/layout.js` | 14 inline styles → audit | 1 hr | low |
| 20 | `helpers/constants.js` | `BRAND_NAME` constant | 5 min | low |
| 21 | `helpers/designSystem.js` | `ELEVATION_TOKENS`, `TOUCH_TARGET` enforcement | 1 hr | low |
| 22 | `pages/homepagev2.js:493-495` | FAQPage schema + visible FAQ | 2 hrs | low |
| 23 | Multiple schema files | Use `BRAND_NAME` constant | 30 min | low |

## Regression Test Matrix

| Page | Breakpoint | Test |
|------|-----------|------|
| `/` | 375, 768, 1440 | Speed (LCP<2.5s), CLS<0.1, touch targets, FAQ renders |
| `/blog/[slug]` | 375, 768 | InArticleCTA renders, no CLS shift |
| `/destinations` | 375 | Carousel swipe works |
| `/search` | 375, 414 | Search form fits, no overflow |
| `/trips` | 375, 768 | Trip cards swipable |
| `/activities/detail/[slug]` | 375, 768 | Product schema validates (Rich Results Test) |
| Mobile focus test | 375, iOS Safari | No auto-zoom on input focus |
| Hamburger menu | 768 | Already implemented (verify) |
| WhatsApp tap | 375 | Tappable, opens WhatsApp |
| Lighthouse | 375, 1440 | Performance score >80 (was 40) |

## Key Files Referenced

**SmartEnPlus frontend:**
- `pages/_app.js`, `pages/_document.js`, `pages/homepagev2.js`
- `lib/homepage/components/*StructuredData*.js`, `*Carousel.js`
- `components/activities/detail/DayTripDetailSEO.js`
- `components/blog/InArticleCTA.js`, `BlogPostHeader.js`, `BlogPostDisplay.js`
- `components/search/ProductSearchForm2.js`, `SearchDialogTrigger.js`, `CurrencySelector.js`, `Passenger.js`
- `components/auth/ProfileButton.js`, `ProfileMenu.js`
- `components/cart/CartButton.js`
- `components/UI/ShareButton.js`, `FeaturedImageHeader.js`
- `components/layout/footer.js`
- `components/pages-info/ContactUs.js`
- `constants/navConfig.js`
- `helpers/constants.js`, `helpers/designSystem.js`, `helpers/imageOptimization.js`
- `next.config.js`, `next-sitemap.config.js`, `tailwind.config.js`
- `public/smartenpus-...webp` (typo)

**Vault working files (this review):**
- `01-projects/website-audit-full-2026-06-06/r1-performance.md`
- `01-projects/website-audit-full-2026-06-06/r1-mobile-ux.md`
- `01-projects/website-audit-full-2026-06-06/r1-seo-ai.md`
- `01-projects/website-audit-full-2026-06-06/r2-skeptic.md`
- `01-projects/website-audit-full-2026-06-06/r3-leader-synthesis.md`

## Out of Scope (deferred)

- **C2** "10 sync scripts" — GTM already `afterInteractive`. Bundle chunks are auto-split. Misread.
- **H4** deferred stylesheet (`data-href`) — 0 hits in source. Likely Cloudflare. Defer to devops.
- **H5** Cloudflare Insights beacon — server-side config, not code
- **MH1** "Only 4 mobile MQ" — Tailwind JIT handles. No action.
- **Hamburger nav at ≤768px** — major nav restructure, defer to [[nav-header-redesign]]
- **BusTrip `departureTime` schema** — backend field missing, defer to API team
- **Brand URL change** — cannot change URL (SEO debt). Wordmark = "SmartEnPlus", URL stays.

## Related

[[r1-performance]] · [[r1-mobile-ux]] · [[r1-seo-ai]] · [[r2-skeptic]] · [[r3-leader-synthesis]] · [[homepage-seo-performance-deep-review]] · [[carousel-design-standard]] · [[mobile-header-analysis]]

## Related Atoms (Extracted 2026-06-13)
- [[seo-canonical-getsiteurl-pattern]] — `getSiteUrl()` → `https://www.smartenplus.co.th` (www mandatory)
- [[og-image-1200x630-webp]] — F7: default OG = WebP 1200×630 at `public/og-image.webp`
- [[brand-name-constant-extraction]] — `BRAND_NAME` constant + `smartenpus`→`smartenplus` filename typo fix
