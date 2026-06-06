---
name: r2-skeptic
description: Skeptic challenges to R1 findings. Caps at 12 final items, rejects off-brand/backend-debt, downgrades miscounted audits.
type: debate
parent: website-audit-full-2026-06-06
role: Skeptic
date: 2026-06-06
---

# R2 — Skeptic Challenges

## Pre-audit findings reclassified as ALREADY DONE

| Audit ID | Original Claim | Reality | Verdict |
|----------|---------------|---------|---------|
| C1 | HTML 308KB, no compress | `next.config.js:8` `compress: true` ✓ | **DROP** — done |
| H1 | 18 non-WebP images | `next.config.js:16` `formats: ['image/webp', 'image/avif']` ✓ + `convertToWebP()` in imageOptimization.js:41 | **DROP** — config done |
| M2 | Duplicate "Routes" nav | CONFIRMED in `navConfig.js:14-23` | **KEEP** (real) |
| Identity P2 | Blog no booking CTAs | `InArticleCTA.js` exists + used in `BlogPostDisplay.js:200, 217` | **DROP** — done |
| AI Gap 2 | No Product schema on Experience | `DayTripDetailSEO.js:31` has `<ProductJsonLd>` ✓ | **DROP** — done |
| AI Gap 3 | No BreadcrumbList on routes | `DayTripDetailSEO.js:34` has `<BreadcrumbJsonLd>` ✓ (for Experience; trip pages TBD) | **PARTIAL** — keep only trip-page audit |
| C2 | 10 sync scripts blocking FCP | Only GTM via `next/script strategy="afterInteractive"` in `_app.js:80-85`. 3rd-party widgets (Omise) unavoidable. Most "scripts" are bundle chunks, not sync. | **DOWNGRADE** — GTM already deferred; not P0 |
| MH1 | Only 4 mobile media queries | Tailwind JIT — only USED breakpoints in CSS. Default sm/md/lg/xl are sufficient. | **DROP** — no action needed |
| M4 | GTM not preloaded | `_app.js:80-85` already `strategy="afterInteractive"`. Preconnect in `_document.js:16` ✓ | **DROP** — done |
| H4 | 1 deferred stylesheet (data-href) | 0 hits in source. Likely from external Cloudflare. | **DEFER-P3** — investigate via DevTools |

## Skeptic Challenges on KEEP items

### C1 — PERF-1 (Inter preload)
- **Specialist claim:** H2, FCP -0.3s
- **Skeptic counter:** True. `_document.js:22` is render-blocking stylesheet. But `next/font/google` is the better fix (eliminates 3rd-party CSS entirely). Recommend PERF-3 (next/font) over hand-rolled preload.
- **Verdict:** **MERGE** with PERF-3. Final fix = switch to `next/font/google`. Effort 2-3 hrs.

### C2 — PERF-2 (213 inline styles)
- **Specialist claim:** 213 in components/, FCP -0.5s
- **Skeptic counter:** Top 5 files (ProfileMenu 20, OrderDetail 18, layout 14) dominated by `boxShadow` — STATIC, can extract to tokens. Don't propose CSS modules. Don't try to eliminate all 213 — only static ones.
- **Verdict:** **KEEP** but scope to top 5 files + static values only. Skip dynamic transforms (loading spinners).

### C3 — PERF-6 / MOB-1 (14px input font)
- **Specialist claim:** iOS zoom fix, 30 min
- **Skeptic counter:** Confirmed in `ProductSearchForm2.js:231, 260, 283, 311, 329` and `SearchDialogTrigger.js:19`. Critical UX bug.
- **Verdict:** **KEEP** at P0. Update `INPUT_CONFIG.base` in `designSystem.js:188` to enforce.

### C4 — MOB-2 (44px touch targets)
- **Specialist claim:** WCAG 2.5.5, 1-2 hrs
- **Skeptic counter:** TOUCH_TARGET.minHeight: '44px' token already in `designSystem.js:210-213`. Not all components use it. Risk: at 320-360px viewport, 44px targets may overflow. **Test at 320px before merge.**
- **Verdict:** **KEEP** at P0 with mitigation note (test at 320px).

### C5 — MOB-3 (WhatsApp 20×20)
- **Specialist claim:** WCAG, 1 hr
- **Skeptic counter:** Real. 4 sites (ShareButton, footer, Passenger, ContactUs). 20px MUI small.
- **Verdict:** **KEEP** at P0.

### C6 — MOB-4 (Carousel scroll-snap)
- **Specialist claim:** 1-2 hrs
- **Skeptic counter:** Embla has `align: 'start'` option. Add to all `*Carousel.js`. Reference [[carousel-design-standard]] (no new patterns).
- **Verdict:** **KEEP** at P1.

### C7 — MOB-7 (Search form mobile overflow)
- **Specialist claim:** 1-2 hrs
- **Skeptic counter:** Confirmed `ProductSearchForm2.js` has flex row. Add `flex-wrap` + responsive stacking. Low risk.
- **Verdict:** **KEEP** at P1.

### C8 — SEO-1 (Duplicate Routes nav)
- **Specialist claim:** 5 min config fix
- **Skeptic counter:** Trivial. Rename one to "Locations". Confirm backend `NavigationSection` doesn't also duplicate.
- **Verdict:** **KEEP** at P1 (low effort, clear win).

### C9 — SEO-3 (OG image to WebP 1200×630)
- **Specialist claim:** 30 min
- **Skeptic counter:** Current `smartenplus.png` is 250×50 — too small for OG. Real impact: social card shareability. Design work needed.
- **Verdict:** **KEEP** at P1.

### C10 — SEO-5 (Brand consistency)
- **Specialist claim:** 1 hr
- **Skeptic counter:** URL cannot change (SEO debt). Standardize on "SmartEnPlus" wordmark + rename `smartenpus-...webp` file typo to `smartenplus-...webp`. Add `BRAND_NAME` constant.
- **Verdict:** **KEEP** at P2.

### C11 — SEO-10 (FAQPage)
- **Specialist claim:** 2 hrs
- **Skeptic counter:** Visible FAQ content needed, not just schema. Real content work (5 questions). Defer to P2.
- **Verdict:** **KEEP** at P2 (downgrade from P1).

### C12 — MOB-6 (Fixed-width containers)
- **Specialist claim:** 15 min grep
- **Skeptic counter:** `designSystem.js:200` already uses `max-w-[1200px]`. Grep may find none. Trivial.
- **Verdict:** **KEEP** at P3 (audit only).

## Mandatory Rejections (auto-DROP)

| Item | Reason |
|------|--------|
| Cloudflare Insights beacon removal | Not in code, server-side config — defer to devops |
| Hamburger nav at ≤768px | Major nav restructure — defer to [[nav-header-redesign]] |
| BusTrip `departureTime` schema | Backend field missing — defer to API team |
| Major 414/768/1024 media query expansion | Tailwind JIT handles; no action |

## Verdict Summary

15 audit issues → **12 final items** (3 cap due to: 5 already done + backend-deferred + over-scoped).

Ranked by ROI:
1. **MOB-1/PERF-6** (14px input fix) — 30 min, P0
2. **MOB-2** (44px touch targets) — 1-2 hrs, P0
3. **MOB-3** (WhatsApp 44×44 wrapper) — 1 hr, P0
4. **PERF-1+3** (Inter font switch to next/font) — 2-3 hrs, P1
5. **MOB-4** (Carousel scroll-snap) — 1-2 hrs, P1
6. **SEO-1** (Routes dedupe) — 5 min, P1
7. **SEO-3** (OG image WebP 1200×630) — 30 min, P1
8. **MOB-7** (Search form mobile overflow) — 1-2 hrs, P1
9. **PERF-2** (Inline style extraction top 5) — 3 hrs, P2
10. **SEO-5** (Brand name constant) — 1 hr, P2
11. **SEO-10** (FAQPage content + schema) — 2 hrs, P2
12. **MOB-6** (Fixed-width grep) — 15 min, P3
