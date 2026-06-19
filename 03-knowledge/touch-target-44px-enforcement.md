---
name: touch-target-44px-enforcement
description: WCAG 2.5.5 enforcement strategy. TOUCH_TARGET token exists in designSystem.js but components don't use it. Batch-fix with min-h-[44px] min-w-[44px].
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06-overview
---

# Touch Target 44px Enforcement

## Summary
WCAG 2.5.5 Level AAA requires 44×44px minimum touch targets. `TOUCH_TARGET.minHeight: '44px'` token exists in `helpers/designSystem.js:210-213` but most components don't apply it.

## Context
Audit MC1: 13/18 interactive elements below 44px. Search inputs, currency button (40×24), account dropdown (40×40), swap/date/passenger buttons (0×0 SVG icons), carousel arrows, WhatsApp icons.

## Problem
Design system has the token but enforcement is per-component. No lint rule catches violations.

## Pattern
**Token** (`helpers/designSystem.js:210-213`):
```js
export const TOUCH_TARGET = {
  minHeight: '44px',     // WCAG 2.2 minimum
  compact: '36px',       // For dense UIs (exceptions only)
};
```

**Enforcement** — apply `min-h-[44px] min-w-[44px]` to interactive elements:
```jsx
<button className="min-h-[44px] min-w-[44px] p-2 ...">
  <SwapIcon fontSize="small" />
</button>
```

**Audit checklist** — 13 sites identified:
- `components/search/CurrencySelector.js:55` (40×24 button)
- `components/auth/ProfileButton.js:367` (40×40 dropdown)
- `components/cart/CartButton.js:116` (icon button)
- `components/search/ProductSearchForm2.js:225, 285, 320` (swap, date, passenger)
- `lib/homepage/components/*Carousel.js` (prev/next arrows)
- `components/UI/ShareButton.js:176-183` (WhatsApp tooltip)
- `components/layout/footer.js:18` (WhatsApp link)
- `components/search/Passenger.js:339-340` (WhatsApp inline)
- `components/pages-info/ContactUs.js:37` (WhatsApp)

## Decision
Batch-fix all 13 sites in Sprint 1 (F2 + F3). Test at 320px (iPhone SE) before merge — 44px may overflow at 320-360px.

## Tradeoffs
- **Pro:** WCAG 2.5.5 AAA compliance, INP improvement
- **Pro:** Single sweep vs per-component
- **Con:** Risk of mobile layout overflow at 320-360px viewport
- **Con:** Carousel arrows may visually exceed track size

## Consequences
Mitigation: test at 320px before merge. If overflow, use `flex-shrink: 0` on parent + reduce padding.

## Related
[[website-audit-full-2026-06-06-overview|website-audit-full-2026-06-06]] · [[r3-leader-synthesis]] · [[r1-mobile-ux]] · [[mobile-header-analysis]]
