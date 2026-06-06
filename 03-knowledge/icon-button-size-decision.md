---
name: icon-button-size-decision
description: 40px is the default for icon buttons in dense UI (Material Design 3 medium). 44px reserved for primary CTAs. Reverted 3 components from F2's 44px after user feedback ("too big").
type: knowledge-atom
date: 2026-06-06
parent: website-audit-full-2026-06-06
---

# Icon Button Size Decision (40px default)

## Summary
Icon-only buttons in dense UI default to **40×40px** (Material Design 3 medium, MUI `size="medium"`), not 44×44px. 44px reserved for primary CTAs and standalone actions. F2 of the website audit (commit `0f9df12`) raised swap/currency/profile to 44px. User feedback: too big. Reverted 3 components in `fbdca15`. Apply 40px to F3 (WhatsApp) and future icon-button work for visual consistency.

## Context
F2 (`0f9df12`, 2026-06-06) shipped 5 components at 44×44px to meet WCAG 2.5.5 AAA. User tested in browser: swap button fills 46/48 = 96% of 48px label row → "pushed against edges". Currency pill out of proportion to 3-char "THB" label. Profile pill 44px height competes with header logo.

User asked 2-spl team to debate 40 vs 44. Cut short by user; direct decision: **revert 3 to 40, keep 44 for the other 2** (cart, carousel arrows — no complaints, primary-CTAs).

## Decision Matrix

| Size | Standard | Use case |
|------|----------|----------|
| 32px | MUI `size="small"` | Only when row height is <40px (exceptions only) |
| **40px** | **MUI `size="medium"` default, Material Design 3 standard** | **Default for icon buttons in dense UI (search bar, header row, inline actions)** |
| 44px | WCAG 2.5.5 AAA, iOS HIG 44pt | Primary CTAs, standalone action buttons (cart button, carousel arrows), or where density isn't a concern |
| 48px | Material Design 3 large | Mobile-first CTAs, FABs |

## Reverted Components (`fbdca15`)

| Component | Before F2 | After F2 (44) | After `fbdca15` (40) | Why reverted |
|---|---|---|---|---|
| Swap `<IconButton>` | 32 (`size="small"`) | 44 (sx) | **40 (sx)** | Decorative in dense search bar row |
| `CurrencySelector` button | 40 (max cap) | 44 (min) | **40 (min)** | 3-char label proportional to 40px |
| `ProfileImage` | 36 (mobile) / 36 (desktop pill) | 44 | **40** | Header pill height competes with logo at 44 |

## Kept at 44 (no complaints)

- `CartButton` — primary action, single-tap purpose
- `CarouselArrowButtons` — standalone navigation, no row density issue
- Search form date/return/passenger row `<div>`s — `min-h-[44px]` ensures row height, primary input surface

## Pattern

**Icon button in dense row (search bar, header):**
```jsx
<IconButton sx={{ minWidth: 40, minHeight: 40 }}>
  <SwapHorizOutlinedIcon style={{ maxWidth: 20, maxHeight: 20 }} />
</IconButton>
```

**Primary CTA / standalone action:**
```jsx
<IconButton sx={{ minWidth: 44, minHeight: 44 }}>
  <ShoppingCartIcon />
</IconButton>
```

**Tailwind equivalent:**
```jsx
<button className="min-h-[40px] min-w-[40px] ...">{icon}</button>  // dense UI
<button className="min-h-[44px] min-w-[44px] ...">{icon}</button>  // primary CTA
```

## Tradeoffs
- **Pro:** 40px (Material medium) is widely accepted as "mobile-friendly" (Material Design 3, Google, Apple web guidelines). Visual harmony with adjacent text/icons.
- **Pro:** Loses only WCAG AAA badge, keeps AA (2.2.1 has no min, only requires "operable").
- **Con:** Below 44px means failing 2.5.5 (AAA). Acceptable for non-AAA sites.
- **Con:** `TOUCH_TARGET` token in `helpers/designSystem.js:210` still says `minHeight: '44px'` — token-vs-reality drift. Defer token update.

## Anchoring Math
For icon button with absolute positioning in a flex row, the `left: -(buttonWidth/2 + borderWidth)` centering pattern must update when button size changes:
- 32px button + 2px border = 34px → `left: -17px`
- 40px button + 2px border = 42px → `left: -21px`
- 44px button + 2px border = 46px → `left: -23px`

F2 follow-up `1e4c549` updated `left: -17px` → `-23px` for the 44px swap. `fbdca15` updated `-23px` → `-21px` for the 40px revert.

## WCAG Reality Check
- **WCAG 2.5.5 (AAA)** = 44×44 CSS px. Voluntary target.
- **WCAG 2.2.1 (AA)** = no minimum size, only "operable". Most production sites aim for AA.
- **WCAG 2.5.8 (AA, new in 2.2)** = 24×24 CSS px target size (October 2023). Below 40px clears this with sufficient spacing.
- 40px passes both 2.2.1 (AA, no min) and 2.5.8 (AA, 24px min). Only fails 2.5.5 (AAA, 44px).

## Out of Scope (deferred)

- Update `TOUCH_TARGET.minHeight: '44px'` token to `40px` (or add `compact: '40px'` field). Token-vs-reality drift.
- Apply 40px to F3 WhatsApp wrapper. Use the same pattern when implementing.
- Audit other 44px components (cart, carousel) — user said no complaints, no change.

## Related
- [[wcag-touch-target-enforcement]] — original 3-part pattern (token, Tailwind/MUI, Playwright spec)
- [[mui-menu-paper-overflow-guard]] — companion for F2's anchor shift regression
- [[website-audit-full-2026-06-06]] — parent audit
