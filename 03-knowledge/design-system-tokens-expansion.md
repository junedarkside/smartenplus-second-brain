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

SHADOWS, BORDERS, BORDER_RADIUS_CLASSES token definitions + affected components migration table extracted to atomic note.
→ See [[designsystem-shadow-border-tokens]]

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
