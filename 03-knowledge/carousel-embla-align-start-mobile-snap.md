---
name: carousel-embla-align-start-mobile-snap
description: Embla carousel align: 'start' option for scroll-snap on mobile. Reference carousel-design-standard.md for breakpoint values.
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06
---

# Carousel Embla Align Start Mobile Snap

## Summary
Add `align: 'start'` to emblaOptions in all `*Carousel.js` components. Enables `scroll-snap-align: start` for horizontal swipe on mobile. Reuse existing `carousel-design-standard.md` for breakpoint-specific itemsPerScreen.

## Context
Audit MC3: carousels in `lib/homepage/components/*Carousel.js` lack scroll-snap. `overflow-x: visible`, no `scroll-snap-type`. Horizontal swipe broken on mobile — cards overflow off-screen.

## Problem
Embla default options (`loop`, `dragFree`) don't enable scroll-snap. Need explicit `align: 'start'` to trigger `scroll-snap-align: start` on each slide.

## Pattern
**Before:**
```js
const emblaOptions = {
  loop: false,
  dragFree: false,
};
```

**After:**
```js
const emblaOptions = {
  align: 'start',     // scroll-snap-align: start
  loop: false,
  dragFree: false,
};
```

**Optional CSS fallback** (for non-Embla carousels):
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

## Decision
Add `align: 'start'` to all Embla carousels. No new CSS pattern — reuse [[carousel-design-standard]] for breakpoint-specific `itemsPerScreen`, `gap`, `card width`.

## Tradeoffs
- **Pro:** Mobile swipe UX functional
- **Pro:** No new pattern — `align: 'start'` is Embla built-in
- **Pro:** Aligns with existing carousel-design-standard
- **Con:** Test at 320-414px to verify snap behavior

## Consequences
Apply to:
- `lib/homepage/components/DestinationsCarousel.js`
- `lib/homepage/components/PopularRoutesCarousel.js`
- All other Embla carousels in `lib/homepage/`

## Related
[[website-audit-full-2026-06-06]] · [[r1-mobile-ux]] · [[r3-leader-synthesis]] · [[carousel-design-standard]]
