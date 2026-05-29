# Hero Section Comprehensive Audit — 2026-05-26

## Summary
9-agent audit (gap analysis + cross-page hero audit + homepage synthesis). Header-hero 88px gap root cause identified. Cross-page hero inconsistencies documented. Priority actions defined.

## Context
Branch: `260528-feat/header-redesign-2026`. Follows [[header-redesign-2026-spec]] and [[header-redesign-2026-implementation]].

---

## Part 1: The 88px Header-Hero Gap

88px white gap on non-homepage pages between header bottom and hero image. Root cause: double-offset from `position: sticky` reserving 88px + `pt-[88px]` on `<main>` adding another 88px. Homepage uses `fixed` so no gap. Homepage hero child `pt-[88px]` is redundant leftover from `isCinematic` removal.

See full analysis → [[hero-88px-gap-root-cause]]

**Fix (Option A):** Remove `pt-[88px]` from layout.js main, remove redundant `pt-[88px]` from homepagev2.js hero child, add `pt-[88px]` to non-homepage hero content divs.

---

## Part 2: Cross-Page Hero Audit

12 pages audited. 10 use `FeaturedImageHeader`, 2 have no hero (Activities Browse, Trip Detail by ID). Key issues: homepage `min-h-screen` vs others `md:min-h-[460px]`, Blog H1 67% larger than others, Trip Detail uses `font-semibold` vs `font-bold`, no consistent CTA treatment, ColorThief gradient homepage-only.

See full component usage matrix → [[featured-image-header-usage-matrix]]

### Priority Issues
- **P0:** Activities Browse + Trip Detail by ID have no hero
- **P0:** 88px gap on non-homepage → [[hero-88px-gap-root-cause]]
- **P1:** Homepage hero too tall for 2026 direction → [[smartenplus-2026-ux-direction]]
- **P1:** H1 typography inconsistent (Blog `text-5xl`, Trip Detail `font-semibold`)
- **P2:** CTA treatment varies (white panel / SearchBar / WP Search / none)

---

## Part 3: Mobile Header Changes

Mobile header changed from dynamic (relative + Slide hide/show) to permanently fixed (no scroll behavior). Spacer `<Toolbar />` removed from layout.js. Desktop/mobile code paths diverged into two separate DOM structures.

See full analysis → [[mobile-header-scroll-behavior-change]]

---

## Priority Actions

| Priority | Action | Pages Affected |
|----------|--------|----------------|
| P0 | Add `FeaturedImageHeader` hero | Activities Browse, Trip Detail |
| P0 | Fix 88px header-hero gap (Option A) | layout.js, homepagev2, destinations, trips |
| P1 | Reduce homepage hero to 55-60vh | Homepage |
| P1 | Standardize H1: `text-3xl font-bold` everywhere | Blog, Trip Detail |
| P2 | Unify CTA treatment | All hero pages |
| P3 | Replace hardcoded 88px with CSS custom property | All pages |

---

## Related

- [[hero-88px-gap-root-cause]] — 88px gap root cause analysis
- [[featured-image-header-usage-matrix]] — Cross-page hero component comparison
- [[mobile-header-scroll-behavior-change]] — Mobile header behavior change
- [[smartenplus-2026-ux-direction]] — 2026 UX direction (45-60vh hero)
- [[header-redesign-2026-spec]] — Header redesign spec
- [[design-systems]] — Design system tokens
