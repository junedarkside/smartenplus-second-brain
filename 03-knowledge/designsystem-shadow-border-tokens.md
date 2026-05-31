# Design System — Shadow & Border Token Definitions

## Summary
Canonical SHADOWS, BORDERS, and BORDER_RADIUS_CLASSES token definitions for `helpers/designSystem.js`. Replaces hardcoded `rgba()` values scattered across card/dropdown components.

## Context
Extracted from [[design-system-tokens-expansion]]. Gap found in [[header-redesign-2026-team-review]] (L-2) + [[destinations-redesign-review]] (Q1). Existing designSystem.js has COLORS/SPACING/BORDER_RADIUS/TYPOGRAPHY_SCALE — missing elevation + border semantic tokens.

## Details

```js
// helpers/designSystem.js — add these exports

export const SHADOWS = {
  sm: '0 1px 2px rgba(0,0,0,0.05)',
  md: '0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)',
  lg: '0 10px 15px rgba(0,0,0,0.10), 0 4px 6px rgba(0,0,0,0.05)',
  xl: '0 20px 25px rgba(0,0,0,0.10), 0 10px 10px rgba(0,0,0,0.04)',
  dropdown: '0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)',
  elevated: '0 4px 12px rgba(0,0,0,0.15)',
};

export const BORDERS = {
  light: '1px solid #E5E7EB',
  medium: '1px solid #D1D5DB',
  focus: '2px solid #3B82F6',
  brand: '2px solid #3b5998',
};

export const BORDER_RADIUS_CLASSES = {
  sm: 'rounded',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',       // 12px — editorial image cards
  '2xl': 'rounded-2xl',   // 16px — large cards
  full: 'rounded-full',
  imageCard: 'rounded-xl', // explicit token for image cards
};
```

### Components Using Hardcoded Values (Migration Targets)

| Component | Current hardcoded value | Replace with |
|-----------|------------------------|--------------|
| `ProfileButton.js` | `boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)'` | `SHADOWS.dropdown` |
| `NavDropdown.js` | dropdown shadow | `SHADOWS.dropdown` |
| `ContentCard` | card shadow | `SHADOWS.md` |
| `PopularRouteImageCard` | `hover:shadow-lg` | stays Tailwind — no change needed |
| `AirportTransferRouteCard` | `hover:shadow-lg` | stays Tailwind — no change needed |

### Token Drift Already Correct
- `DiscoverySection.js` `rounded-xl` = matches `imageCard` token
- Search hero `rounded-xl` = matches `imageCard` token
- `AccountCard.js` `rounded-xl` = matches `imageCard` token

## Tradeoffs
- Adding tokens without immediate adoption is safe — zero runtime impact
- Full adoption requires grep + replace across ~15 components (defer to later PR)
- `LocationGridComponent` uses `rounded` (4px) — minor drift, acceptable

## Related
- [[design-system-tokens-expansion]] — migration strategy + full context
- [[design-systems]] — existing token docs
