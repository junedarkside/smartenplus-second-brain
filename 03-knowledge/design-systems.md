# Design Systems

## Summary
Token-based design system. `helpers/designSystem.js`: `COLORS`, `SPACING`, `BORDER_RADIUS`, `TYPOGRAPHY_SCALE`. Consumed by MUI + Tailwind.

## Token Categories

### Colors
Semantic naming: primary, secondary, success, warning, error, neutral shades. No raw hex in components.

### Spacing
4px base scale. `SPACING.xs` through `SPACING.xl`. Prevents arbitrary margin/padding.

### Border Radius
`BORDER_RADIUS.sm`, `.md`, `.lg`. Consistent rounding.

### Typography Scale
`TYPOGRAPHY_SCALE.body`, `.heading`, `.caption`. Visual hierarchy.

## Why Tokens
- Single source of truth — change token, update everywhere
- AI-readable — LLM suggests correct values from token names
- Prevents design drift — no arbitrary values
- Audit-able — grep for raw hex or magic numbers

## Lessons
- Start tokens early, retrofit expensive
- Keep token file flat + simple — no computed values
- MUI theme overrides + Tailwind config reference tokens, don't duplicate

## MUI + Tailwind Coordination

MUI manages own bg/color via theme. Tailwind on inner elements only works if MUI doesn't override.

**AppBar:** Always `color="inherit"` with Tailwind bg classes. Without it, MUI injects `bgcolor: primary.main`.

**Dual-background header:** `text-white md:text-gray-600` pattern for icons switching bg (brand blue mobile → white desktop). CartButton, ProfileButton, hamburger, logo use this.

**overflow:hidden ancestors:** MUI AppBar has `overflow:hidden`. Children with negative offsets (badges, chevrons) must be in sized Box — don't rely on parent `overflow:visible`.

## Related
- [[architecture]]
- [[nav-header-redesign]]
- [[carousel-design-standard]] — Embla carousel items-per-screen, breakpoints, gap, focus ring