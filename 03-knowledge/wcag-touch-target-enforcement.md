---
name: wcag-touch-target-enforcement
description: 3-part pattern for WCAG 2.5.5 compliance: (a) TOUCH_TARGET design token, (b) Tailwind min-h-[44px] min-w-[44px] + MUI sx minWidth/minHeight, (c) Playwright boundingBox regression spec at 320/375/414 viewports.
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06
---

# WCAG 2.5.5 Touch Target Enforcement

## Summary
WCAG 2.5.5 (AAA) / 2.2.1 (AA) require interactive controls ≥44×44 CSS px. Enforce via 3-part pattern: (1) `TOUCH_TARGET.minHeight: '44px'` token in `helpers/designSystem.js`, (2) apply via Tailwind arbitrary values OR MUI `sx` prop, (3) Playwright regression spec at smallest mobile viewports using `boundingBox()`. Reusable for any a11y compliance batch.

## Context
`website-audit-full-2026-06-06` r1-mobile-ux: 13/18 touch targets <44px in header + search. F2 batch raised 5 specific components. F3 (WhatsApp 20×20 wrapper) and WA-5 (footer + SearchDialogTrigger) extend. Pattern codified to prevent regression.

## Problem
- iOS HIG: 44pt minimum touch target
- Material Design: 48dp recommended
- WCAG 2.5.5 (AAA): 44×44 CSS px
- Common offenders: icon-only buttons, swap buttons, carousel arrows, social icons
- 1px button height changes often invisible to designers but break WCAG
- No automated check without custom Playwright spec

## Pattern (3 parts)

### Part 1: Design Token
```js
// helpers/designSystem.js:210
export const TOUCH_TARGET = {
  minHeight: '44px',     // WCAG 2.2 minimum
  minWidth: '44px',
};
```
- Source of truth for "what does 44px mean" in this codebase
- Avoids hardcoded `44` scattered across files
- Use in conditional logic (e.g., `sx={{ minHeight: TOUCH_TARGET.minHeight }}`)

### Part 2: Apply via Tailwind OR MUI sx

**Tailwind arbitrary values** (preferred for native HTML/Tailwind components):
```jsx
<button className="min-h-[44px] min-w-[44px] flex items-center justify-center ...">
  <SwapVertOutlinedIcon />
</button>
```

**MUI sx prop** (required for MUI IconButton/Button — className doesn't override MUI defaults):
```jsx
<IconButton sx={{ minWidth: 44, minHeight: 44 }} aria-label="Swap origin and destination">
  <SwapVertOutlinedIcon />
</IconButton>
```

**When to use which:**
- Native `<button>`, `<div role="button">`, `<a>` → Tailwind arbitrary
- MUI `<Button>`, `<IconButton>` → sx prop (MUI Emotion overrides Tailwind)
- Mix: add BOTH (`className="min-h-[44px] min-w-[44px]"` + `sx={{ minHeight: 44, minWidth: 44 }}`) for belt-and-suspenders

**Common MUI override fix:**
```jsx
// BAD — IconButton defaults to 40x40
<IconButton size="small"><SwapIcon /></IconButton>

// GOOD — explicit 44x44
<IconButton sx={{ minWidth: 44, minHeight: 44 }}><SwapIcon /></IconButton>
```

### Part 3: Playwright Regression Spec
```typescript
// e2e/a11y/touch-targets.spec.ts
import { test, expect, Locator } from '@playwright/test';

async function box(locator: Locator) {
  return locator.boundingBox().catch(() => null);
}

test.describe('F2 — 44×44px touch targets (WCAG 2.5.5)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentLoaded');
    await page.waitForTimeout(2000);
  });

  test('header: cart button ≥ 44px', async ({ page }) => {
    const b = await box(page.getByRole('button', { name: /shopping cart/i }).first());
    test.skip(!b, 'cart not in DOM');
    expect(b!.width, 'cart width').toBeGreaterThanOrEqual(44);
    expect(b!.height, 'cart height').toBeGreaterThanOrEqual(44);
  });
  // ... more tests for each F2-targeted component
});
```

**Why `boundingBox()` not `isVisible()`:**
- `isVisible()` requires viewport intersection
- Off-screen elements (carousel arrows at scroll position 0) → false negative
- `boundingBox()` returns null only if element is hidden
- Use `test.skip(!b, ...)` to allow optional elements

**Why `domcontentloaded` + 2s settle not `networkidle`:**
- Next.js dev mode keeps HMR WebSocket open
- `networkidle` never fires in dev → test timeout
- `domcontentloaded` + 2s gives components time to mount

**Run on multiple mobile projects** (per `playwright.config.ts`):
```bash
npx playwright test e2e/a11y/touch-targets.spec.ts \
  --project=chromium-mobile \
  --project=chromium-mobile-320 \
  --project=chromium-mobile-375 \
  --project=chromium-mobile-414
```
- 320px (iPhone SE 1st gen — smallest modern)
- 375px (iPhone SE 2nd/3rd gen, standard mobile)
- 414px (iPhone Plus, large mobile)
- Default mobile (varies by Playwright version)

## Audit Workflow
1. **Find offenders:** Playwright audit script logs all `boundingBox()` < 44px on mobile viewport
2. **Classify by impact:** header/search (P0), footer (P1), social/decorative (P2)
3. **Apply Part 2** to each offender (1-line Tailwind or sx change)
4. **Add Part 3** assertion to regression spec
5. **Verify:** `npx playwright test e2e/a11y/touch-targets.spec.ts`

## Tradeoffs
- **Pro:** 1-line fix per offender (Tailwind arbitrary)
- **Pro:** Token + spec prevent regression
- **Pro:** Multi-viewport (320/375/414) catches small-screen-only issues
- **Con:** Playwright spec adds 2s to CI (acceptable)
- **Con:** MUI + Tailwind dual approach increases decision surface
- **Con:** Visual height bumps (e.g., ProfileImage 36→44) can break anchored elements (see [[mui-menu-paper-overflow-guard]])

## Real-World Triggers
- Icon-only button with `<IconButton size="small">` (defaults 40x40)
- Carousel arrow with `p-1` padding (insufficient)
- `div role="button"` with `py-2` (32px) — needs `min-h-[44px]`
- WhatsApp/social icon 20×20 PNG (F3) — wrap in `min-h-[44px] min-w-[44px]`
- Footer link with `text-sm` (14px) — needs `min-h-[44px]` on anchor

## F2 Batch Reference
5 files modified, 8 assertions added:
- `components/UI/CurrencySelector.js` — cap removed, `min-h-[44px] min-w-[44px]`
- `components/auth/ProfileImage.js` — desktop pill 36→44
- `components/cart/CartButton.js` — `sx={{ minWidth: 44, minHeight: 44 }}`
- `components/search/ProductSearchForm2.js` — 3 buttons + 3 divs
- `components/UI/CarouselArrowButtons.js` — both arrows
- `e2e/a11y/touch-targets.spec.ts` — NEW spec, 8 tests

## Out of Scope (deferred)
- Footer secondary nav links (WA-5) — separate mini-batch
- Social icon decorative wrappers — accept under-44 if not interactive
- Text-only links inside paragraphs (not full buttons)

## Related
- [[mui-menu-paper-overflow-guard]] — companion for height-change regressions
- [[ios-zoom-input-16px-rule]] — companion iOS rule
- [[website-audit-full-2026-06-06]] — parent audit project
