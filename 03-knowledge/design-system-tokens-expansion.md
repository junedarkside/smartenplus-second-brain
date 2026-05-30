# Design System Tokens Expansion

## Summary
`helpers/designSystem.js` has color/spacing/typography tokens but lacks border/shadow semantic tokens. Components use hardcoded `rgba(0,0,0,0.06)` values. Token expansion needed.

## Context
`header-redesign-2026-team-review.md` (L-2) + `destinations-redesign-review.md` (Q1). Design system has `COLORS`, `SPACING`, `BORDER_RADIUS`, `TYPOGRAPHY_SCALE`. Missing: `BORDERS`, `SHADOWS`.

## Problem
Components hardcode shadow values:
```jsx
// ProfileButton.js
boxShadow: '0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)'

// Card components
shadow-md, shadow-lg — arbitrary Tailwind classes
```

No semantic tokens for:
- `shadow-sm`, `shadow-md`, `shadow-lg` — used across cards
- `border-light`, `border-medium` — used in dropdowns
- Dropdown-specific shadows (ProfileButton, NavDropdown)

## Decision

### Add SHADOWS Token Set
```js
// helpers/designSystem.js

export const SHADOWS = {
  sm: '0 1px 2px rgba(0,0,0,0.05)',
  md: '0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)',
  lg: '0 10px 15px rgba(0,0,0,0.10), 0 4px 6px rgba(0,0,0,0.05)',
  xl: '0 20px 25px rgba(0,0,0,0.10), 0 10px 10px rgba(0,0,0,0.04)',
  dropdown: '0 8px 24px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)',
  elevated: '0 4px 12px rgba(0,0,0,0.15)',
};
```

### Add BORDERS Token Set
```js
export const BORDERS = {
  light: '1px solid #E5E7EB',
  medium: '1px solid #D1D5DB',
  focus: '2px solid #3B82F6',
  brand: '2px solid #3b5998',
};
```

### Add BORDER_RADIUS_CLASSES Expansion
```js
export const BORDER_RADIUS_CLASSES = {
  sm: 'rounded',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl', // 12px — editorial image cards
  '2xl': 'rounded-2xl',   // 16px — large cards (verify before using)
  full: 'rounded-full',
  imageCard: 'rounded-xl', // 12px — explicit token for image cards
};
```

## Details

### Why Hardcoded rgba Values Exist
- `designSystem.js` was created for color/spacing/typography
- Border/shadow tokens were deprioritized
- Components were built with hardcoded values during design system gaps
- Tailwind `shadow-*` classes exist but lack semantic meaning

### Migration Strategy
1. Add tokens to `designSystem.js`
2. Grep for hardcoded shadow patterns across components
3. Replace with token references (defer to later PR — not blocking)
4. Update `tailwind.config.js` to use token values if needed

### Components Affected (Confirmed)
- `ProfileButton.js` — dropdown shadow
- `NavDropdown.js` — dropdown shadow
- `ContentCard` — card shadow
- `PopularRouteImageCard` — hover shadow
- `AirportTransferRouteCard` — hover shadow (fixed to `hover:shadow-lg`)

### Existing Token Drift
| Component | Current | Token Should Be |
|-----------|---------|-----------------|
| LocationGridComponent cards | `rounded` (4px) | `rounded-sm` or `rounded` |
| DiscoverySection.js | `rounded-xl` | `rounded-xl` (12px) — already correct |
| Search hero | `rounded-xl` | `rounded-xl` (12px) — already correct |
| AccountCard.js | `rounded-xl` | `rounded-xl` (12px) — already correct |

## Tradeoffs
- Adding tokens now and deferring adoption is acceptable — no runtime impact
- Full adoption requires grep + replace across ~15 components
- Token drift in codebase means some values already non-standard

## Consequences
- Semantic shadow tokens enable consistent elevation hierarchy
- Border tokens enable consistent focus/active states
- `imageCard: 'rounded-xl'` formalizes existing drift as official token

## Related
- [[design-systems]] — existing design system docs
- [[header-redesign-2026-team-review]] — L-2 finding
- [[destinations-redesign-review]] — Q1 rounding decision
