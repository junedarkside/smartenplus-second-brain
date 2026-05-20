# MUI + Tailwind CSS Specificity Conflict

## Summary

Tailwind utility classes (`className`) on MUI components get overridden by MUI's Emotion-generated CSS. Affects color, display, and other visual properties.

## Context

SmartEnPlus frontend uses MUI v5 (Emotion) + Tailwind v3.4.4. Two CSS systems compete for specificity on shared DOM elements. MUI wins.

## Problem

MUI v5 uses Emotion (`@emotion/react`) to generate scoped CSS classes (`css-[hash]`). These have higher specificity than Tailwind utility classes applied via `className`. Result: Tailwind classes silently ignored on MUI components.

**Affected component types:**
- `IconButton` — `text-white`, `hidden md:block` ignored
- `Button` — `text-white` ignored
- `SvgIcon` (all MUI icons) — `hidden md:block`, `text-gray-*` ignored
- Any MUI component accepting `className`

**Not affected:**
- Plain HTML elements (`div`, `span`, `nav`) — Tailwind works fine
- Non-MUI React components

## Root Cause

1. MUI Emotion classes injected at runtime with higher CSS specificity
2. Tailwind classes are global utilities, lower in cascade
3. `tailwind.config.js` has no `important: true` — no specificity boost
4. No `StyledEngineProvider` configured to change injection order

This is **inherent** to MUI + Tailwind coexistence, not a configuration bug.

## Decision

**Rule: MUI components use `sx` prop. Plain HTML uses Tailwind `className`.**

### Patterns

```jsx
// BAD — Tailwind className on MUI component (silently fails)
<IconButton className='text-white bg-black bg-opacity-25'>

// GOOD — sx prop for MUI styling, Tailwind for layout-only
<IconButton className='bg-black/25 hover:bg-black/40' sx={{ color: 'white' }}>

// GOOD — wrap in div for display control (hidden/block)
<div className="hidden md:block">
  <HelpOutlineOutlinedIcon className="text-gray-500" />
</div>

// GOOD — Tailwind on plain HTML (always works)
<div className="text-white bg-black/25">
  <span>Share</span>
</div>
```

### What goes where

| Property | On MUI component | On plain HTML |
|----------|-----------------|---------------|
| color | `sx={{ color: 'white' }}` | `className="text-white"` |
| display | Wrap in `<div className="hidden md:block">` | `className="hidden md:block"` |
| background | `className` usually works (MUI doesn't set bg) | `className="bg-black/25"` |
| padding/margin | `sx` or `className` (both usually work) | `className="p-2 mx-4"` |
| hover states | `sx={{ '&:hover': { ... } }}` | `className="hover:bg-black/40"` |

## Consequences

- Must audit all MUI components using Tailwind `className` for color/display
- `sx` prop is MUI-specific — not portable to other frameworks
- Div wrappers add minor DOM overhead (negligible)

## Related

- [[nextjs-patterns]]
- [[design-systems]]
