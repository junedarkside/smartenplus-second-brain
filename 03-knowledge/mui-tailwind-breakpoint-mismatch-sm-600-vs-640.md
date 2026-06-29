---
name: mui-tailwind-breakpoint-mismatch-sm-600-vs-640
description: MUI `sm=600` (medium screen breakpoint) vs Tailwind `sm=640` (640px breakpoint) mismatch causes responsive layout misalignment. Components switch columns at different widths → jank, overlap, or gaps.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: design_system-audit
---

# MUI/Tailwind Breakpoint Mismatch — sm=600 vs 640

## Summary
MUI `sm=600` (medium screen) vs Tailwind `sm=640` (640px breakpoint) mismatch. Responsive layout misalignment — columns switch at different widths.

## Why It Matters
Mixed MUI + Tailwind projects break responsively. User at 620px width sees one layout at 2 columns, another component still at 1 column → overlap/gaps.

## Detail
**MUI breakpoints:**
```jsx
<Grid item sm={6} md={4} lg={3}>
// sm=600px, md=960px, lg=1280px
```

**Tailwind breakpoints:**
```jsx
<div className="sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
// sm=640px, md=768px, lg=1024px
```

**Conflict:** At 620px width, MUI switches to 6-column layout (`sm=600` triggers) but Tailwind still uses 1-column (`sm=640` not yet triggered). Layout breaks.

**Fix:** Standardize on Tailwind breakpoints (recommended) — create MUI theme with matching breakpoints:
```jsx
const theme = createTheme({
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
  },
});
```

**OR** remap Tailwind config to match MUI.

## Constraints / Gotchas
Global change. Affects ALL MUI/Tailwind混合 components. Test responsive at 600-640px width range thoroughly.

## Related
- [[design-system-audit]] — parent audit (token coverage, violations, 5-phase roadmap)
