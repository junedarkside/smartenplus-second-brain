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

## Type A / Type B Split (HeaderRowsContext)

Header height varies by route: **Type A** (operational/transactional: `/checkout`, `/payment`, `/login`, `/register`, `/search`) = 80px single row. **Type B** (discovery/browse: homepage, `/blog`, most pages) = 96px two rows. `StickySearchBar` top offset + `main` padding must consume a `HeaderRowsContext` to stay in sync with the active type. The static `pt-[88px]` in the snippet above is a Type-B average; see [[header-rows-context-dynamic-offset]] for the full Context-based pattern.

`FeaturedImageHeader` accepts `isCinematic` prop — when true, renders full-bleed, no back/share controls, `inset-0` positioning. Used on trip-detail cinematic hero.

## Related

- [[smartenplus-glassmorphism-header]] — cinematic hero implementation context
- [[header-rows-context-dynamic-offset]] — Type A/B split
- [[header-glass-to-solid-migration]] — glass→solid migration recipe
- [[mui-tailwind-css-specificity]] — why MUI props > Tailwind className