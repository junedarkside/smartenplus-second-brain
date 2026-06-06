---
name: website-audit-full-2026-06-06
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

Prior code-level audit: [[homepage-seo-performance-deep-review-2026-05-21]] (30 findings, file:line refs, structured data schema errors in code).

## SEO & Speed

### Scores
| Category | Score | Status |
|---|---|---|
| SEO | 75/100 | Moderate |
| Speed | 40/100 | Poor |
| Accessibility | 85/100 | Good |

### Critical — Speed

**C1: HTML Page Size 308 KB (should be <100 KB)**
3x recommended size. 66 inline style blocks, 34 JS chunks.
Fix: Enable Next.js compress, maximize SSG. Fragment page if needed.

**C2: 10 Synchronous Scripts Blocking First Paint**
10 of 34 chunks are synchronous — block FCP and LCP.
Fix: Mark non-critical scripts `defer`/`async`. Use `next/script strategy="lazyOnload"`.

**C3: 66 Inline `<style>` Blocks**
Every carousel card/section injects CSS inline. Blocks rendering, kills caching.
Fix: Use CSS modules or global stylesheets instead of Tailwind arbitrary inline classes.

### High — Speed

**H1: 18 Non-WebP Images** (11 WebP ✅, 18 PNG/JPG ❌, 35/36 lazy-loaded ✅)
Fix: Convert all destination/carousel images to WebP. Target `<picture>` with AVIF fallback.

**H2: No Font Preload for Inter**
Only preconnect to Google Fonts — no preload for the Inter woff2 file. Causes FOIT.
Fix: `<link rel="preload" as="font" href="/_next/static/media/...inter.woff2" crossorigin>`

**H3: No width/height on Images — CLS Risk**
None of 36 images have explicit `width`/`height`. Causes Cumulative Layout Shift.
Fix: Add `width={X} height={Y}` to all `<Image>` components.

**H4: 1 Deferred Stylesheet (data-href)**
Lazy-loaded stylesheet via `data-href` pattern. Can cause FOUC.
Fix: Investigate which component defers its stylesheet. Load inline or preload.

**H5: Cloudflare Insights Beacon (~50ms overhead)**
`https://static.cloudflareinsights.com/beacon.min.js` adds DNS lookup + latency per page.
Fix: Remove if not actively monitored. If needed, defer.

### Moderate — SEO

**M1: Missing `<meta name="keywords">` tag**
Bing + Thai-local search engines may still use it.
Fix: Add `bus, ferry, train, Thailand, booking, travel, Phuket, Krabi, Koh Phi Phi, airport transfer`

**M2: Duplicate H2 "Routes" in navigation**
Two nav links both labeled "Routes" — config bug.
Fix: Deduplicate nav items.

**M3: OG Image — Local WebP May Not Render in Social Sharing**
`/_next/static/media/smartenpus-transportation-booking-online.9ae7d65f.webp`
Social crawlers (Facebook, LINE) may not reliably render Next.js-served WebP.
Fix: Test in Facebook Debugger + LINE debugger. Serve OG image from CDN with cache headers.

**M4: GTM Not Preloaded**
Preconnect exists but GTM script not preloaded. ~100ms overhead.
Fix: Audit GTM container. If 1-2 tags, inline them. Otherwise preload the GTM script.

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
[[homepage-seo-performance-deep-review-2026-05-21]] · [[structured-data-schema-patterns]] · [[carousel-design-standard]] · [[nextjs-patterns]] · [[seo-homepage-specialist-team]] · [[blog-seo-performance-2026-05-20]]
