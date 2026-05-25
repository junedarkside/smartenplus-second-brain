# Next.js: Fixed Header on One Route, Sticky on Others

## Summary

Use `router.pathname` to toggle MUI `AppBar` between `position="fixed"` (homepage cinematic) and `position="sticky"` (all other pages).

## Problem

Homepage needs header to float over full-viewport hero image (`position: fixed`). All other pages need the header to participate in normal document flow (`position: sticky`). MUI AppBar doesn't support per-route positioning out of the box.

## Pattern

**`main-header.js`:**
```jsx
const route = useRouter();
const isHomepage = route.pathname === '/';

<AppBar position={isHomepage ? 'fixed' : 'sticky'} sx={{ top: 0, zIndex: 1100 }}>
```

**`layout.js`:**
```jsx
const isHomepage = router.pathname === '/';

<main className={`...${isHomepage ? '' : ' pt-[88px]'}`}>
```

The `pt-[88px]` offset on non-homepage routes prevents content from hiding under the fixed-height header (88px = Row 1 48px + Row 2 40px).

Homepage needs no offset — the hero section fills the full viewport behind the fixed header intentionally.

## Why Not CSS Only

MUI's `position` prop maps to CSS `position` AND controls internal MUI layout behavior. Setting via Tailwind class alone won't override MUI's internal positioning logic — must go through the prop.

## Tradeoffs

| Pro | Con |
|-----|-----|
| Clean separation — homepage gets cinematic, others get normal | `pt-[88px]` hardcoded to header height — must update both if header height changes |
| No context/prop drilling required | `isHomepage` computed in two places (main-header + layout) |
| Works with MUI AppBar without fighting the library | |

## Related

- [[smartenplus-glassmorphism-header]] — cinematic hero implementation context
- [[mui-tailwind-css-specificity]] — why MUI props > Tailwind className
