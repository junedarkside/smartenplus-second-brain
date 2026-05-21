# Design Systems

## Summary
Token-based design system approach. SmartEnPlus uses `helpers/designSystem.js` with `COLORS`, `SPACING`, `BORDER_RADIUS`, `TYPOGRAPHY_SCALE`. Tokens consumed by MUI + Tailwind.

## Token Categories

### Colors
Semantic naming: primary, secondary, success, warning, error, neutral shades. No raw hex in components.

### Spacing
Consistent scale (4px base). `SPACING.xs` through `SPACING.xl`. Prevents arbitrary margin/padding values.

### Border Radius
`BORDER_RADIUS.sm`, `.md`, `.lg`. Consistent rounding across all components.

### Typography Scale
Named sizes: `TYPOGRAPHY_SCALE.body`, `.heading`, `.caption`. Ensures visual hierarchy.

## Why Tokens
- Single source of truth — change token, update everywhere
- AI-readable — LLM can suggest correct values from token names
- Prevents design drift — no arbitrary values in components
- Audit-able — grep for raw hex or magic numbers to find violations

## Lessons
- Start with tokens early, retrofit is expensive
- Keep token file flat and simple — no computed values
- MUI theme overrides + Tailwind config should reference tokens, not duplicate values

## MUI + Tailwind Coordination

MUI components manage their own background/color via theme. Tailwind classes on inner elements only work if MUI doesn't override.

**AppBar:** Always set `color="inherit"` when using Tailwind bg classes. Without it, MUI injects `bgcolor: primary.main` which overrides Tailwind bg.

**Icon colors in dual-background header:** Use `text-white md:text-gray-600` pattern for icons/text in a header that switches background (brand blue mobile → white desktop). CartButton, ProfileButton, hamburger, logo all use this pattern.

**overflow:hidden ancestors:** MUI AppBar has internal `overflow:hidden`. Any child using negative position offsets (badges, chevrons) must be contained within their parent Box — size the Box to include the overflow, don't rely on the parent being `overflow:visible`.

## Related
- [[architecture]]
- [[nav-header-redesign]]
