---
name: r1-mobile-ux
description: Mobile UX/Accessibility specialist findings — 13/18 touch targets <44px, no scroll-snap, 14px input font, fixed-width containers. Maps audit MC1-MC3 + MH1-MH3 + MM1-MM2 to file:line evidence.
type: specialist-finding
parent: website-audit-full-2026-06-06
specialist: Mobile UX & Accessibility Specialist
date: 2026-06-06
---

# R1 — Mobile UX & Accessibility Specialist

## Pre-existing wins (NOT work to do)

- `helpers/designSystem.js:210-213` — `TOUCH_TARGET.minHeight: '44px'` token already exists ✓
- `helpers/designSystem.js:144-151` — `BREAKPOINTS` uses Tailwind defaults (sm/md/lg/xl) ✓
- `tailwind.config.js:67-69` — `smallphone: '321px'` custom breakpoint exists
- `pages/_app.js:68-71` — viewport meta correct
- `helpers/designSystem.js:66-73` — `TYPOGRAPHY_SCALE.body: 'text-sm sm:text-base'` (14px → 16px responsive)

## Findings (file:line evidence)

### MOB-1 — Search inputs use 14px (iOS zoom) (Audit MM1)
- **Severity:** Critical
- **Audit ID:** MM1
- **WCAG:** iOS Safari accessibility — inputs <16px trigger auto-zoom on focus
- **File:line:** `components/search/ProductSearchForm2.js:231, 260, 283, 311, 329`
- **Evidence:**
  ```
  className={`text-sm md:text-sm text-decoration-none ...`}
  ```
  Multiple `text-sm` (14px) classes on search inputs.
- **Fix:** Replace `text-sm` → `text-base` in search input fields. Also update `INPUT_CONFIG.base` in `designSystem.js:188` (`'w-full px-4 py-3 text-base border border-gray-200'`) to enforce globally.
- **Impact:** Fixes iOS auto-zoom. Mobile UX critical.
- **Effort:** trivial (30 min)
- **Risk:** low
- **Note:** `BODY_TYPEGRAPHY_SCALE.body: 'text-sm sm:text-base'` (14→16 responsive) — but search forms break this pattern. Audit claim of "1 input at 16px" matches: only `INPUT_CONFIG.base` uses 16px.

### MOB-2 — Currency/Account/Swap/Date/Passenger touch targets <44px (Audit MC1)
- **Severity:** Critical
- **Audit ID:** MC1
- **WCAG:** WCAG 2.5.5 Target Size (Level AAA) — 44×44px minimum
- **File:line:** Audit identifies 13/18 elements failing. Need to find source:
  - Currency button (40×24) — likely `components/search/CurrencySelector.js` (line 55 per master-state HD-1)
  - Account dropdown (40×40) — `components/auth/ProfileButton.js`
  - Swap/Date/Passenger (0×0 SVG) — `components/search/ProductSearchForm2.js:225-330`
  - Carousel prev/next (0×0) — `components/UI/CarouselArrow.js` or similar
- **Fix:** Enforce `min-h-[44px] min-w-[44px]` on all interactive buttons in:
  - `components/search/` (CurrencySelector, ProductSearchForm2, DateField, Passenger, SwapButton)
  - `components/cart/CartButton.js`
  - `components/auth/ProfileButton.js`, `ProfileMenu.js`
  - All carousel arrow components
- **Implementation hint:** Add `min-h-[44px] min-w-[44px]` to `BUTTON_CONFIG.primary.base` in `designSystem.js:172` and audit each button consumer.
- **Impact:** WCAG AAA compliance, INP improvement
- **Effort:** small-medium (1-2 hrs for batch)
- **Risk:** medium — may break mobile layout at 320-360px (skeptic challenge valid — see r2)
- **Mitigation:** Test at 320px (iPhone SE) and 360px (Galaxy) before merge

### MOB-3 — WhatsApp button 20×20px (Audit MC2)
- **Severity:** Critical
- **Audit ID:** MC2
- **WCAG:** WCAG 2.5.5
- **File:line:** Multiple WhatsApp references:
  - `components/UI/ShareButton.js:176-183` — `<Tooltip title="Share on WhatsApp">`
  - `components/layout/footer.js:6, 18` — `<WhatsAppIcon fontSize="small" />`
  - `components/search/Passenger.js:339-340` — `<WhatsAppIcon fontSize="small" />` inside `<Link>`
  - `components/pages-info/ContactUs.js:5, 37` — `<WhatsAppIcon />`
- **Evidence:** `fontSize="small"` = 20px (MUI small default). No wrapper with min-h/min-w.
- **Fix:** Wrap each WhatsApp icon in a 44×44px touch container:
  ```jsx
  <Link href={...} className="inline-flex items-center justify-center min-h-[44px] min-w-[44px]" aria-label="Contact via WhatsApp">
    <WhatsAppIcon fontSize="small" />
  </Link>
  ```
- **Impact:** WCAG compliance, accessibility for motor-impaired users
- **Effort:** small (1 hr for 4-5 sites)
- **Risk:** low

### MOB-4 — No scroll-snap on carousels (Audit MC3)
- **Severity:** Critical
- **Audit ID:** MC3
- **File:line:** `lib/homepage/components/DestinationsCarousel.js`, `PopularRoutesCarousel.js` (Embla-based)
- **Evidence:** `overflow-x: visible` likely + no `scroll-snap-type`. Embla by default has options for `loop`, `dragFree` but not scroll-snap.
- **Fix:**
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
  Apply to all Embla containers in `lib/homepage/components/*Carousel.js`.
- **Implementation hint:** Add `align: 'start'` to `emblaOptions`. Reference [[carousel-design-standard]] for breakpoint-specific `itemsPerScreen` values.
- **Impact:** Mobile swipe UX functional
- **Effort:** small (1-2 hrs to add `align: 'start'` to all carousels)
- **Risk:** low — aligns with existing `carousel-design-standard.md`

### MOB-5 — Media query coverage: only `smallphone: '321px'` custom (Audit MH1)
- **Severity:** Moderate
- **Audit ID:** MH1
- **File:line:** `tailwind.config.js:67-69` — only custom breakpoint
- **Evidence:** Uses Tailwind defaults (sm:640, md:768, lg:1024, xl:1280). Audit claims only 4 mobile MQ in CSS.
- **Fix:** Audit actual CSS for media query count (via Chrome DevTools "Find all media queries"). Likely Tailwind purges unused breakpoints, leaving only used ones in CSS.
- **Verdict:** Audit partially wrong. Tailwind is JIT — only USED breakpoints appear in CSS. Code uses `md:`, `lg:` prefixes. No code change needed.
- **Effort:** 0 (skip)
- **Risk:** n/a

### MOB-6 — Fixed-width containers `width: 1280px` (Audit MH2)
- **Severity:** High
- **Audit ID:** MH2
- **File:line:** `helpers/designSystem.js:200, 204` — `HOMEPAGE_SECTION.outer: 'w-full flex flex-col justify-center gap-2 max-w-[1200px] mx-auto'` (already has `max-w-[1200px]` ✓)
- **Evidence:** Design system already uses `max-w-[1200px]`. Audit may refer to legacy `width: 1280px` in other components.
- **Fix:** `grep -rn "width: 1280px\|w-\[1280px\]" components/ pages/` — replace any with `max-w-[1200px]`.
- **Impact:** Mobile container fit
- **Effort:** trivial (15 min grep+replace)
- **Risk:** low

### MOB-7 — Search form overflow on mobile (Audit MH3)
- **Severity:** High
- **Audit ID:** MH3
- **File:line:** `components/search/ProductSearchForm2.js` — From/To/Date/Passengers/SEARCH in one row
- **Evidence:** `ProductSearchForm2.js:224-330` — multiple inputs in single flex row
- **Fix:** Add `flex-wrap` on mobile + responsive stacking at `md:` breakpoint. Reference existing `StickySearchBar.js` pattern.
- **Impact:** Mobile search form usable
- **Effort:** small (1-2 hrs)
- **Risk:** low

### MOB-8 — H1 30px not scaling on mobile (Audit MM2)
- **Severity:** Moderate
- **Audit ID:** MM2
- **File:line:** Audit cites `text-3xl`. `designSystem.js:67` has `h1: 'text-2xl sm:text-3xl md:text-4xl'` (24→30→36 responsive) ✓
- **Evidence:** Design system already handles this. Likely older components don't use `TYPOGRAPHY_SCALE.h1`.
- **Fix:** Audit `text-3xl` usages in homepage/hero. Replace with `TYPOGRAPHY_SCALE.h1` token.
- **Impact:** Mobile H1 readability
- **Effort:** trivial (30 min)
- **Risk:** low

## Mobile Testing Checklist (from audit)

- [ ] iPhone SE (375px) — Search form overflow?
- [ ] iPhone 14 (390px) — Nav items wrap or overflow?
- [ ] Samsung Galaxy S21 (360px) — Carousel swipe works?
- [ ] iPad Mini (768px) — Hamburger menu visible?
- [ ] Tap WhatsApp — Opens on mobile?
- [ ] Focus input on iOS Safari — Page zooms in?

## Top 3 Wins

1. **MOB-1 — 14px → 16px search inputs** (30 min, iOS zoom fix)
2. **MOB-2 — 44×44px touch targets batch** (1-2 hrs, WCAG AAA + INP)
3. **MOB-4 — Carousel scroll-snap** (1-2 hrs, mobile UX)

## Key Files

- `components/search/ProductSearchForm2.js` — 14px inputs, overflow risk
- `components/search/CurrencySelector.js` — 40×24 currency button
- `components/auth/ProfileButton.js` — 40×40 account dropdown
- `components/cart/CartButton.js` — header cart icon
- `components/UI/ShareButton.js` — WhatsApp tooltip
- `components/layout/footer.js` — WhatsApp link
- `components/search/Passenger.js` — WhatsApp inline link
- `lib/homepage/components/*Carousel.js` — Embla scroll-snap
- `helpers/designSystem.js` — TOUCH_TARGET, INPUT_CONFIG, TYPOGRAPHY_SCALE tokens
- `tailwind.config.js` — breakpoints (default Tailwind sufficient)

## Related

[[carousel-design-standard]] · [[mobile-header-analysis]] · [[homepage-ux-review]]
