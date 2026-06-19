---
name: designSystem
description: Canonical pointer to SmartEnPlus design system. Token file, semantic categories, audit guidance.
metadata:
  type: hub
  domain: design-system
---

# Design System (Hub)

Canonical reference for the SmartEnPlus design system. The single source file is `helpers/designSystem.js` in `smartenplus-frontend`. This note exists in the vault so wikilinks like `[[designSystem]]` resolve to a real page.

## What it is
Token-based design system consumed by MUI + Tailwind. Defines:
- `COLORS` — semantic colors (primary, secondary, success, warning, error, neutral shades)
- `SPACING` — scale tokens
- `BORDER_RADIUS` — radius tokens + Tailwind class map
- `TYPOGRAPHY_SCALE` — text size tokens
- `BUTTON_CONFIG` / `INPUT_CONFIG` / `CARD_CONFIG` — component presets
- `TOUCH_TARGET` — 44px minimum (WCAG 2.5.5)
- `CUSTOM_BREAKPOINTS` — Tailwind JIT extension

## Related
- [[design-systems]] — broader design system hub
- [[design-system-tokens-expansion]] — token expansion history
- [[design-system-phase1-migration]] — Phase 1 migration plan
- [[design-system-audit-2026-05-31]] — first audit
- [[design-system-audit]] — second audit (post-Phase 1)
- [[designsystem-shadow-border-tokens]] — shadow/border token rationale
- [[migrate-bootstrap-palette-to-ds-tokens]] — palette migration pattern
- [[design-token-caption-tailwind-gotcha]] — caption token gotcha
- [[unified-badge-system-pattern]] — badge geometry
- [[touch-target-44px-enforcement]] — 44px rule
- [[wcag-touch-target-enforcement]] — WCAG touch target

## Audit rules
When auditing a feature, check against `[[designSystem]]`:
1. No hardcoded hex in components — use `COLORS.*` tokens
2. No raw spacing values — use `SPACING.scale.*` or Tailwind aliases
3. No raw radius — use `BORDER_RADIUS_CLASSES.*` or `BORDER_RADIUS.*`
4. No raw font sizes — use `TYPOGRAPHY_SCALE.*`
5. Tap targets ≥ 44px (use `TOUCH_TARGET.minHeight`)
6. Run `scripts/design-token-audit.sh` (if exists) before merge
