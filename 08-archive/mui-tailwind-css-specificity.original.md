# MUI + Tailwind CSS Specificity Conflict

## Summary
Tailwind `className` on MUI components → overridden by MUI Emotion CSS. Affects color, display, visual props.

## Context
MUI v5 (Emotion) + Tailwind v3.4.4. Two CSS systems compete. MUI wins on MUI components.

## Problem

MUI Emotion scoped classes (`css-[hash]`) > Tailwind utility classes. Tailwind silently ignored on MUI components.

**Affected:** `IconButton`, `Button`, `SvgIcon` (all MUI icons), any MUI component accepting `className`.
**Not affected:** Plain HTML (`div`, `span`, `nav`), non-MUI React components.

## Root Cause

1. MUI Emotion classes injected runtime with higher specificity
2. Tailwind global utilities lower in cascade
3. No `important: true` in tailwind.config.js
4. No `StyledEngineProvider` configured

Inherent to MUI + Tailwind coexistence.

## Responsive Breakpoints (sx prop)

MUI `sx` responsive values (`display: { xs: 'none', md: 'block' }`) generate `@media` rules via Emotion at runtime. **Fail without Emotion cache provider.**

`_app.js` has `ThemeProvider` but no `CacheProvider`/`StyledEngineProvider`. Responsive `sx` may not inject — especially `display` breakpoints. Tailwind compiled `@media` always works.

**Rule: responsive display → Tailwind `className` on plain div wrapper. Never MUI `sx` responsive breakpoints.**

Affected: `components/layout/main-header.js` help icon (commit a0e7aea tried MUI Box sx, reverted to Tailwind div).

## Decision

**MUI components → `sx` prop. Plain HTML → Tailwind `className`.**

### Patterns

```jsx
// BAD — Tailwind on MUI component (silently fails)
<IconButton className='text-white bg-black bg-opacity-25'>

// GOOD — sx for MUI styling
<IconButton className='bg-black/25 hover:bg-black/40' sx={{ color: 'white' }}>

// GOOD — div wrapper for display control
<div className="hidden md:block">
  <HelpOutlineOutlinedIcon className="text-gray-500" />
</div>

// GOOD — Tailwind on plain HTML (always works)
<div className="text-white bg-black/25"><span>Share</span></div>
```

### What goes where

| Property | MUI component | Plain HTML |
|----------|--------------|------------|
| color | `sx={{ color: 'white' }}` | `className="text-white"` |
| display | Wrap in `<div className="hidden md:block">` | `className="hidden md:block"` |
| background | `className` usually works | `className="bg-black/25"` |
| padding/margin | `sx` or `className` | `className="p-2 mx-4"` |
| hover | `sx={{ '&:hover': { ... } }}` | `className="hover:bg-black/40"` |

## Consequences
- Audit all MUI components using Tailwind `className` for color/display
- `sx` prop is MUI-specific — not portable
- Div wrappers: minor DOM overhead (negligible)

## Related
- [[nextjs-patterns]]
- [[design-systems]]
