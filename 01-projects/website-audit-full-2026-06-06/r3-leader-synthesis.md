---
name: r3-leader-synthesis
description: Leader synthesis — final 12 P0-P3 items with sprint plan, file change inventory, regression test matrix.
type: synthesis
parent: website-audit-full-2026-06-06
role: Leader
date: 2026-06-06
---

# R3 — Leader Synthesis

## Pre-flight Wins (NOT work to do)

6 audit items already addressed in current codebase:
- **C1** compress: true (`next.config.js:8`) ✓
- **H1** WebP/AVIF config (`next.config.js:16`) ✓
- **M4** GTM deferred (`_app.js:80-85`) ✓
- **Identity P2** InArticleCTA exists and used (`BlogPostDisplay.js:200, 217`) ✓
- **AI Gap 2** ProductJsonLd on Experience (`DayTripDetailSEO.js:31`) ✓
- **AI Gap 3** BreadcrumbList on Experience (`DayTripDetailSEO.js:34`) ✓

## Final 12 — Ranked P0 → P3

### Final 1 — Search input 14px → 16px (P0)
- **Sprint:** 1
- **Effort:** 30 min
- **What Audit Found:** iOS Safari zooms on inputs <16px (MM1)
- **Skeptic Verdict:** KEEP — confirmed in `ProductSearchForm2.js:231, 260, 283, 311, 329`
- **Implementation:**
  - `components/search/ProductSearchForm2.js:231, 260, 283, 311, 329` — `text-sm` → `text-base`
  - `components/search/SearchDialogTrigger.js:19` — `text-sm` → `text-base`
  - `helpers/designSystem.js:188` — `INPUT_CONFIG.base` already has `text-base` (enforcement by example)
- **Estimated LoC:** 5-8 lines
- **Verify:** Chrome DevTools + iOS Simulator — focus From input on `/`, page does not zoom. iOS Safari 17+.

### Final 2 — Touch target 44×44px (P0)
- **Sprint:** 1
- **Effort:** 1-2 hrs
- **What Audit Found:** 13/18 interactive elements <44px (MC1)
- **Skeptic Verdict:** KEEP — `TOUCH_TARGET.minHeight: '44px'` token exists (`designSystem.js:210-213`) but components don't use it
- **Implementation:**
  - Add `min-h-[44px] min-w-[44px]` to:
    - `components/search/CurrencySelector.js:55` (40×24 button)
    - `components/auth/ProfileButton.js:367` (40×40 dropdown)
    - `components/cart/CartButton.js:116` (icon button)
    - `components/search/ProductSearchForm2.js:225, 285, 320` (swap, date, passenger buttons)
    - Carousel prev/next arrows in `lib/homepage/components/*Carousel.js`
  - **Mitigation:** Test at 320px (iPhone SE) before merge — may overflow at 320-360px
- **Estimated LoC:** 15-20 lines
- **Verify:** Playwright at 320px + 360px + 414px viewports, no horizontal overflow on `/` or `/search`. Lighthouse a11y >90.

### Final 3 — WhatsApp button 44×44 wrapper (P0)
- **Sprint:** 1
- **Effort:** 1 hr
- **What Audit Found:** WhatsApp icon 20×20px (MC2)
- **Skeptic Verdict:** KEEP — 4 sites use `fontSize="small"` (20px)
- **Implementation:**
  - Wrap each WhatsApp icon in `min-h-[44px] min-w-[44px]` container with `aria-label`:
    - `components/UI/ShareButton.js:176-183`
    - `components/layout/footer.js:18`
    - `components/search/Passenger.js:339-340`
    - `components/pages-info/ContactUs.js:37`
- **Estimated LoC:** 12-16 lines
- **Verify:** Lighthouse a11y score >90. Manual tap test on iPhone SE WhatsApp icon — opens WhatsApp app.

### Final 4 — Inter font self-host via next/font (P1)
- **Sprint:** 2
- **Effort:** 2-3 hrs
- **What Audit Found:** Inter loaded via render-blocking stylesheet (H2)
- **Skeptic Verdict:** MERGE PERF-1 + PERF-3 — use `next/font/google` not hand-rolled preload
- **Implementation:**
  - `pages/_app.js` — `import { Inter } from 'next/font/google'; const inter = Inter({ subsets: ['latin'], display: 'swap' })`
  - Apply `className={inter.className}` to `<main>` or `<body>`
  - Remove `pages/_document.js:20-22` preconnect + stylesheet links (next/font handles)
  - `tailwind.config.js:64-66` — `fontFamily.sans: ['var(--font-inter)', ...]`
- **Estimated LoC:** 10-15 lines + config
- **Risk:** high — global font swap affects every page. FOUT/CLS regressions possible.
- **Verify:** Lighthouse before/after FCP + CLS at /, /trips, /blog/[slug]. No FOUT in slow 3G throttle. Rollback if CLS >0.1.
- **Rollback:** keep `_document.js:20-22` commented (not deleted) until next/font proven in production. Revert by uncommenting + removing `next/font` import.

### Final 5 — Carousel scroll-snap (P1)
- **Sprint:** 2
- **Effort:** 1-2 hrs
- **What Audit Found:** No scroll-snap on carousels (MC3) — horizontal swipe broken on mobile
- **Skeptic Verdict:** KEEP — Embla has `align: 'start'` option, no new pattern needed
- **Implementation:**
  - `lib/homepage/components/DestinationsCarousel.js` — add `align: 'start'` to emblaOptions
  - `lib/homepage/components/PopularRoutesCarousel.js` — same
  - All other Embla carousels in `lib/homepage/`
  - Reference [[carousel-design-standard]] for breakpoint values
- **Estimated LoC:** 5-10 lines
- **Verify:** Manual swipe on iPhone SE in `/destinations` and `/` — cards snap to start position, no overflow off-screen.

### Final 6 — Dedupe "Routes" in navConfig (P1)
- **Sprint:** 2
- **Effort:** 5 min
- **What Audit Found:** Two "Routes" entries in nav (M2)
- **Skeptic Verdict:** KEEP — confirmed `navConfig.js:14-23`
- **Implementation:**
  - `constants/navConfig.js:19-23` — rename `label: 'Routes'` (href `/locations`) → `label: 'Locations'`. Keep `label: 'Routes'` for href `/trips` (semantic = trip search).
  - Verify backend `NavigationSection` (RTK Query `pages-info/navigation/`) doesn't also have duplicate "Routes" — if yes, mirror rename.
- **Estimated LoC:** 1-2 lines
- **Verify:** Visual check on `/` — only one "Routes" nav item remains; "Locations" rendered for `/locations` link.

### Final 7 — OG image to WebP 1200×630 (P1)
- **Sprint:** 2
- **Effort:** 30 min
- **What Audit Found:** OG image is `smartenplus.png` 250×50 (M3) — too small for OG standard
- **Skeptic Verdict:** KEEP — real social card issue
- **Implementation:**
  - Design new OG image 1200×630 (collaborate with design)
  - Export as WebP → `public/og-image.webp`
  - `pages/_app.js:42-48` — update `url`, `width: 1200`, `height: 630`
  - Also update `public/smartenpus-...webp` → rename to `smartenplus-...webp` (typo fix)
- **Estimated LoC:** 5 lines + design asset
- **Verify:** Facebook Sharing Debugger + Twitter Card Validator render at 1200×630. LINE debugger also valid for Thai market.

### Final 8 — Search form mobile overflow (P1)
- **Sprint:** 2
- **Effort:** 1-2 hrs
- **What Audit Found:** From/To/Date/Passengers/SEARCH in one row overflows at 375px (MH3)
- **Skeptic Verdict:** KEEP — confirmed `ProductSearchForm2.js` flex row
- **Implementation:**
  - `components/search/ProductSearchForm2.js` — add `flex-wrap` on mobile + stack vertically at `md:`
  - Reference existing `StickySearchBar.js` pattern for mobile compact layout
  - Test at 320, 375, 414px
- **Estimated LoC:** 10-15 lines
- **Verify:** Playwright at 320/375/414px — search form fits on `/` and `/search`, all 5 inputs (From/To/Date/Passengers/Search) visible without horizontal scroll.

### Final 9 — Inline style extraction (top 5 files) (P2)
- **Sprint:** 3
- **Effort:** 3 hrs
- **What Audit Found:** 213 inline `style={{}}` in components/ (C3)
- **Skeptic Verdict:** SCOPE — only static `boxShadow` + colors in top 5 (ProfileMenu, OrderDetail, layout, ProductSearchForm2, ProductSearchForm). Skip dynamic transforms.
- **Implementation:**
  - `components/auth/ProfileMenu.js:20` — `boxShadow: '0 8px 24px ...'` → extract to `BUTTON_CONFIG.elevated.boxShadow`
  - `components/order/OrderDetail.js` — extract only static `boxShadow` strings (skip dynamic transforms/colors)
  - `components/layout/layout.js` — extract only static `boxShadow` strings
  - Add `ELEVATION_TOKENS = { none, sm, md, lg, xl }` to `designSystem.js`
- **Scope:** static values only. Dynamic transforms (loading spinners), conditional colors stay inline. (Per r2-skeptic verdict.)
- **Estimated LoC:** 30-50 lines (extraction + token additions)
- **Verify:** grep `style={{` in top 5 files — count reduced by static extractions only. No new `style={{` for dynamic values.

### Final 10 — Brand name consistency (P2)
- **Sprint:** 3
- **Effort:** 1 hr
- **What Audit Found:** "SmartEnPlus" vs "smartenplus" inconsistencies (Identity P3)
- **Skeptic Verdict:** KEEP — standardize on "SmartEnPlus" wordmark, URL stays. Add `BRAND_NAME` constant.
- **Implementation:**
  - `helpers/constants.js` — add `export const BRAND_NAME = 'SmartEnPlus';`
  - Replace all hardcoded `'SmartEnPlus'` strings with `BRAND_NAME`:
    - `pages/_app.js:34, 35, 41, 47` (DefaultSeo)
    - `lib/homepage/components/PopularRoutesStructuredData.js:31, 60` (provider)
    - `lib/homepage/components/LocationsStructuredData.js:65, 71` (provider)
    - `lib/homepage/components/ReviewsStructuredData.js:64, 66`
  - Rename `public/smartenpus-...webp` → `public/smartenplus-...webp` (typo fix)
  - Update imports in `components/blog/BlogPostHeader.js:5`
- **Estimated LoC:** 15-20 lines
- **Verify:** grep `'SmartEnPlus'` — only `BRAND_NAME` constant declaration + `import { BRAND_NAME }` lines remain.

### Final 11 — FAQPage content + schema (P2)
- **Sprint:** 3
- **Effort:** 2 hrs
- **What Audit Found:** FAQPage schema has 5 questions, no visible FAQ matching (AI Gap 4)
- **Skeptic Verdict:** KEEP — content work, not just schema
- **Implementation:**
  - Audit `pages/homepagev2.js:493-495` (per prior SEO audit SD10) — `helpSubcategories` exists
  - **Pre-check:** grep `helpSubcategories` to confirm data shape. If categories (not Q&A), find real FAQ source in `lib/homepage/` schema files before proceeding.
  - Add FAQPage schema using verified Q&A source
  - Add visible FAQ section (5 collapsible `<details>`) to homepage or `/faq` page
  - Reference [[structured-data-schema-patterns]] for FAQPage format
- **Risk:** medium — `helpSubcategories` may be subcategory metadata, not Q&A content. Pre-check required.
- **Estimated LoC:** 30-40 lines (schema + UI)

### Final 12 — Fixed-width container audit (P3)
- **Sprint:** 4
- **Effort:** 15 min
- **What Audit Found:** `width: 1280px` containers overflow mobile (MH2)
- **Skeptic Verdict:** KEEP — `designSystem.js:200` already uses `max-w-[1200px]`, but audit may find legacy usages
- **Implementation:**
  - `grep -rn "width: 1280px\|w-\[1280px\]" components/ pages/`
  - Replace any with `max-w-[1200px]`
  - Add to CLAUDE.md as lint rule (avoid hardcoded widths)
- **Estimated LoC:** 0-5 lines (audit only)
- **Verify:** grep returns 0 hits for `width: 1280px` and `w-[1280px]` in `components/` and `pages/`.

## Sprint Plan

| Sprint | Days | Items | Effort |
|--------|------|-------|--------|
| Sprint 1 | Day 1-2 | Final 1, 2, 3 (P0 batch) | ~3 hrs |
| Sprint 2 | Day 3-4 | Final 4, 5, 6, 7, 8 (P1 batch) | ~7 hrs |
| Sprint 3 | Day 5-7 | Final 9, 10, 11 (P2 batch) | ~6 hrs |
| Sprint 4 | Day 8+ | Final 12 + mobile testing matrix | ~2 hrs |

**Total: ~18 hours frontend work over 8-10 days**

## File Change Inventory

| # | File | Changes | Effort | Risk |
|---|------|---------|--------|------|
| 1 | `components/search/ProductSearchForm2.js` | 14px → 16px (5 lines), 44px buttons, mobile flex-wrap | 2 hrs | low |
| 2 | `components/search/SearchDialogTrigger.js` | 14px → 16px | 5 min | low |
| 3 | `components/search/CurrencySelector.js` | 44px min-h/w | 15 min | low |
| 4 | `components/auth/ProfileButton.js` | 44px min-h/w | 15 min | low |
| 5 | `components/cart/CartButton.js` | 44px min-h/w | 15 min | low |
| 6 | `components/UI/ShareButton.js` | WhatsApp 44px wrapper | 15 min | low |
| 7 | `components/layout/footer.js` | WhatsApp 44px wrapper | 15 min | low |
| 8 | `components/search/Passenger.js` | WhatsApp 44px wrapper | 15 min | low |
| 9 | `components/pages-info/ContactUs.js` | WhatsApp 44px wrapper | 15 min | low |
| 10 | `pages/_app.js` | next/font Inter + DefaultSeo keywords + BRAND_NAME | 3 hrs | high |
| 11 | `pages/_document.js` | Remove font preconnect/stylesheet (next/font handles) | 5 min | low |
| 12 | `tailwind.config.js` | fontFamily.sans = ['var(--font-inter)'] | 5 min | low |
| 13 | `lib/homepage/components/*Carousel.js` | align: 'start' option | 1-2 hrs | low |
| 14 | `constants/navConfig.js` | Dedupe "Routes" | 5 min | low |
| 15 | `public/og-image.webp` | NEW asset (1200×630) | 30 min | n/a |
| 16 | `public/smartenpus-...webp` | RENAME → smartenplus-...webp | 5 min | low |
| 17 | `components/auth/ProfileMenu.js` | boxShadow → token | 30 min | low |
| 18 | `components/order/OrderDetail.js` | 18 inline styles → audit | 1 hr | low |
| 19 | `components/layout/layout.js` | 14 inline styles → audit | 1 hr | low |
| 20 | `helpers/constants.js` | BRAND_NAME constant | 5 min | low |
| 21 | `helpers/designSystem.js` | ELEVATION_TOKENS, TOUCH_TARGET enforcement | 1 hr | low |
| 22 | `pages/homepagev2.js:493-495` | FAQPage schema + visible FAQ | 2 hrs | low |
| 23a | `lib/homepage/components/PopularRoutesStructuredData.js` | provider name → `BRAND_NAME` (lines 31, 60) | 10 min | low |
| 23b | `lib/homepage/components/LocationsStructuredData.js` | provider name → `BRAND_NAME` (lines 65, 71) | 10 min | low |
| 23c | `lib/homepage/components/ReviewsStructuredData.js` | provider name → `BRAND_NAME` (lines 64, 66) | 10 min | low |

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

## Out of Scope (this round)

- Backend schema/API changes
- Major nav restructure (hamburger nav at ≤768px)
- Cloudflare Insights removal (server-side config)
- BusTrip `departureTime` schema (API team)
- Audit H4 (deferred stylesheet investigation — likely Cloudflare)
- Audit C2 "10 sync scripts" (misinterpreted — GTM already deferred)

## Related

[[r1-performance]] · [[r1-mobile-ux]] · [[r1-seo-ai]] · [[r2-skeptic]] · [[homepage-seo-performance-deep-review-2026-05-21]] · [[carousel-design-standard]] · [[mobile-header-analysis-2026-05-26]]
