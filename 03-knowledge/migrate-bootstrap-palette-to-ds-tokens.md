# Migrate Bootstrap Palette to DS Tokens

## Summary
Replace Bootstrap legacy palette in `styles/globals.css` (`.primary #007bff`, `.success #28a745`, etc.) with `COLORS.status.*` tokens from `designSystem.js`. Bootstrap legacy = brand color drift surface.

## Context
The SmartEnPlus design system lives in `helpers/designSystem.js` as a single source of truth: `COLORS.brand.primary`, `COLORS.status.success`, `COLORS.text.muted`, etc. Components should import from `designSystem.js` and reference tokens, not hardcoded hex. The legacy `styles/globals.css` still contains Bootstrap-style utility classes (`.primary`, `.success`, `.danger`, `.warning`, `.info`) that override with hardcoded hex codes.

## Problem
Two problems with the legacy Bootstrap palette:
1. **Brand color drift.** When the brand team updates a color, the `designSystem.js` token updates and all component imports follow. The legacy CSS class does NOT follow — it still applies the old hex. Designers see "I updated the brand color in Figma, but the .primary button is still the old blue." This is a brand-consistency bug, not a code bug.
2. **Inconsistency surface.** A `<Button className="primary">` looks different from `<Button style={{ backgroundColor: COLORS.brand.primary }}>`. The two should be visually identical but aren't, because `.primary` uses the old hex.

The Bootstrap legacy classes are a tax on the design system: every color update has to touch both the token AND the legacy CSS. Most teams forget the legacy CSS, leading to silent drift.

## Details
Migration in `styles/globals.css`:

```css
/* Before — Bootstrap legacy hardcoded */
.primary { background-color: #007bff !important; color: #fff !important; }
.success { background-color: #28a745 !important; color: #fff !important; }
.danger  { background-color: #dc3545 !important; color: #fff !important; }
.warning { background-color: #ffc107 !important; color: #000 !important; }
.info    { background-color: #17a2b8 !important; color: #fff !important; }

/* After — DS token reference */
.primary { background-color: var(--ds-brand-primary); color: #fff; }
.success { background-color: var(--ds-status-success); color: #fff; }
.danger  { background-color: var(--ds-status-danger);  color: #fff; }
.warning { background-color: var(--ds-status-warning); color: #000; }
.info    { background-color: var(--ds-status-info);    color: #fff; }
```

The CSS custom properties `--ds-*` are defined in `:root` of `globals.css` from the `designSystem.js` token values (one-time copy, automated by build step or manually synced). Components import `COLORS` from `designSystem.js` for inline styles; the legacy classes now reference the same source.

`!important` can be dropped from most cases once the cascade is clean — legacy Bootstrap used it as a hammer to override MUI/Tailwind; with proper token usage, specificity is naturally correct.

## Decision
Migrate all legacy Bootstrap palette classes in `styles/globals.css` to reference `COLORS.status.*` tokens. Remove `!important` where the cascade allows. Audit all uses of `.primary`, `.success`, `.danger`, `.warning`, `.info` in components and migrate to direct token imports over time (separate effort).

## Tradeoffs
- Pro: Single source of truth for colors
- Pro: Brand color updates propagate automatically
- Pro: No more "which blue is the right blue" conversations
- Con: CSS custom properties add an indirection layer. Dev tools show `var(--ds-status-success)` instead of the hex — slightly less obvious during debugging.
- Con: The migration is one-time but the cleanup (migrating component call sites off the legacy classes) is ongoing
- Con: If the `designSystem.js` → CSS var sync is manual, the two can drift. Build-step automation or a CI check prevents this.

## Consequences
After migration, the design system has one source of truth. The legacy Bootstrap classes are now thin wrappers over the same tokens. New components should never use `.primary`/`.success`/etc — they should import `COLORS.status.*` directly. The legacy classes are kept for backward compatibility but should be removed in a follow-up sweep.

A grep for hardcoded hex codes in `styles/globals.css` should return zero matches after migration. CI check enforces.

## Related
- [[design-system-audit]] — broader design system audit
