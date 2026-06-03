# Next.js: Fixed Header on One Route, Sticky on Others

## Summary

Use `router.pathname` to toggle MUI `AppBar` between `position="fixed"` (homepage cinematic) and `position="sticky"` (all other pages).

## Problem

Homepage needs header float over full-viewport hero (`position: fixed`). Other pages need header in normal doc flow (`position: sticky`). MUI AppBar no per-route positioning out of box.

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

`pt-[88px]` offset on non-homepage routes prevents content hiding under fixed-height header (88px = Row 1 48px + Row 2 40px).

Homepage needs no offset — hero fills full viewport behind fixed header intentionally.

## Why Not CSS Only

MUI `position` prop maps to CSS `position` AND controls internal MUI layout behavior. Tailwind class alone won't override MUI internal logic — must go through prop.

## Tradeoffs

| Pro | Con |
|-----|-----|
| Clean separation — homepage cinematic, others normal | `pt-[88px]` hardcoded to header height — update both if height changes |
| No context/prop drilling | `isHomepage` computed in two places (main-header + layout) |
| Works with MUI AppBar without fighting library | |

## Related

- [[smartenplus-glassmorphism-header]] — cinematic hero implementation context
- [[mui-tailwind-css-specificity]] — why MUI props > Tailwind className