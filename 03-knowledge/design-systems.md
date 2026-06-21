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

### Component Configs & Tokens
- `BUTTON_CONFIG` / `INPUT_CONFIG` / `CARD_CONFIG` — component presets
- `TOUCH_TARGET` — 44px minimum (WCAG 2.5.5)
- `CUSTOM_BREAKPOINTS` — Tailwind JIT extension

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

## Audit Rules
When auditing a feature, check against `helpers/designSystem.js`:
1. No hardcoded hex in components — use `COLORS.*` tokens
2. No raw spacing values — use `SPACING.*` or Tailwind aliases
3. No raw radius — use `BORDER_RADIUS.*`
4. No raw font sizes — use `TYPOGRAPHY_SCALE.*`
5. Tap targets ≥ 44px (use `TOUCH_TARGET.minHeight`)

## Related
- [[architecture]]
- [[nav-header-redesign]]
- [[carousel-design-standard]] — Embla carousel items-per-screen, breakpoints, gap, focus ring
- [[design-system-tokens-expansion]] — token expansion history
- [[design-system-phase1-migration]] — Phase 1 migration plan
- [[design-system-audit]] — post-Phase 1 audit
- [[designsystem-shadow-border-tokens]] — shadow/border token rationale
- [[migrate-bootstrap-palette-to-ds-tokens]] — palette migration pattern
- [[design-token-caption-tailwind-gotcha]] — caption token gotcha
- [[unified-badge-system-pattern]] — badge geometry
- [[touch-target-44px-enforcement]] — 44px rule