# Header Redesign 2026 — Final Design Spec

**Status:** FINAL — all decisions locked 2026-05-28. Supersedes single-row spec.

## Summary
Replace dark glassmorphism header with adaptive solid white navigation. Two types: Type A (operational, single-row) for transactional pages; Type B (discovery, two-row) for browse/content.

## Context
Current header (2026-05-27 revert): dark glass (`glass-bg-scrolled`), white text, 2-row desktop. 2026 direction: operational clarity — Google Flights/Linear/Notion UX. Platform is hybrid — utility + discovery. Header must adapt.

## Decision
Solid `#FFFFFF` adaptive header. Type A/B split. No glassmorphism. No blur.

## TYPE A — Operational Header

**Pages:** `/search` `/checkout` `/payment` `/booking` `/login` `/register`

**Layout:** `Logo | Compact Search Summary | Utilities` (Currency · Cart · Account)
- Height: 80px desktop / 56–64px mobile
- No secondary nav

## TYPE B — Discovery Header

**Pages:** `/` `/destinations` `/locations` `/trips` `/activities` `/blog`

**Row 1:** Same as Type A (52px)
**Row 2:** `Explore Thailand | Routes | Journeys | Experiences | Guides` (40–48px)

- All 5 nav items kept (DO NOT remove Explore Thailand)
- Total: ~96px
- Row 2: `variant="dense"` MUI Toolbar, hover underline

**CRITICAL:** `/blog` is Type B. Remove `/blog` from ONE_ROW_PATHS.

## Global Header CSS

```css
.solid-header { background: #FFFFFF; border-bottom: 1px solid rgba(0,0,0,0.06); box-shadow: 0 2px 12px rgba(0,0,0,0.03); }
.solid-header-elevated { background: #FFFFFF; border-bottom: 1px solid rgba(0,0,0,0.08); box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
```

No: backdrop-blur · transparency · dark overlay · floating glass

## Color Tokens

| Element | Value |
|---------|-------|
| Header bg | `#FFFFFF` |
| Page bg alt | `#FAFAF8` / `#F7F7F5` |
| Primary text | `#1F2937` (gray-800) |
| Nav inactive | `text-gray-500` |
| Nav active | `text-gray-900 border-b-2 border-gray-900` |
| Focus ring | `ring-gray-400` |
| Icons | `text-gray-700 hover:text-gray-900` |
| Border | `rgba(0,0,0,0.06)` |
| Shadow | `rgba(0,0,0,0.03)` |

## Color Change Map

| Component | Before | After |
|------------|--------|-------|
| main-header mobile bg | `bg-fb-blue` | `solid-header` (white) |
| main-header desktop bg | `glass-bg-scrolled` | `solid-header` (white) |
| main-header nav inactive | `text-white/70` | `text-gray-500` |
| main-header nav active | `text-white border-white` | `text-gray-900 border-gray-900` |
| CartButton/ProfileButton icon | `text-white/70` | `text-gray-700` |
| NavDropdown active | `brand-primary` | `gray-900` |
| HeaderSearchSummary route | `text-white` | `text-gray-900` |
| SearchDialogTrigger | `bg-white/20 text-white` | `bg-gray-100 text-gray-900` |
| StickySearchBar | `bg-gray-900 bg-opacity-90` | `solid-header-elevated` |

## Mobile Header

- Height: 56–64px, bg: solid white
- Layout: `[Hamburger] [Logo] | [Currency · Cart · Account]`
- Icons: `text-gray-700`
- Keep `<Slide>` hide-on-scroll (56px viewport gain)

## Layout Offset System

```javascript
// layout.js
const ONE_ROW_PATHS = ['/checkout', '/payment', '/login', '/register', '/search']; // /blog removed

const headerRows = ONE_ROW_PATHS.some(p => router.pathname === p || router.pathname.startsWith(p + '/')) ? 1 : 2;
const layoutPaddingTop = headerRows === 1 ? 'md:pt-[80px]' : 'md:pt-[96px]';
<main className={`mx-auto w-full flex-grow no-scrollbar ${layoutPaddingTop}`}>
```

## StickySearchBar Dynamic Offset

```javascript
// layout.js — add: export const HeaderRowsContext = React.createContext(2);
// StickySearchBar.js — consume:
const headerRows = useContext(HeaderRowsContext);
className: headerRows === 1 ? 'top-[80px]' : 'top-[96px]'
```

## Progressive Search UX

Expanded → sticky summary on scroll. Click → desktop: centered modal / mobile: full-screen editor.

## Files to Change (12)

| # | File | Priority |
|---|------|----------|
| 1 | `styles/globals.css` | Remove glass; add `.solid-header` | P0 |
| 2 | `components/layout/layout.js` | Remove `/blog` from ONE_ROW_PATHS; dynamic padding; export HeaderRowsContext | P0 |
| 3 | `components/layout/main-header.js` | `glass-bg-scrolled` → `solid-header`; white → dark; mobile `bg-fb-blue` → white | P0 |
| 4 | `components/search/HeaderSearchSummary.js` | All `text-white*` → dark | P0 |
| 5 | `components/search/SearchDialogTrigger.js` | Button colors | P0 |
| 6 | `components/search/StickySearchBar.js` | Dark → white; dynamic top | P0 |
| 7 | `components/cart/CartButton.js` | `text-white/70` → `text-gray-700` | P0 |
| 8 | `components/auth/ProfileButton.js` | `text-white/70` → `text-gray-700` | P0 |
| 9 | `components/layout/NavDropdown.js` | Active: `brand-primary` → `gray-900`; focus ring | P1 |
| 10 | `constants/navConfig.js` | **NO CHANGE** — keep all 5 items | — |
| 11 | `pages/homepagev2.js` | Hero 500px → 320–360px (separate PR) | P2 |
| 12 | `pages/_document.js` | Custom font loading (separate PR) | P2 |

**Verify:** `grep -rn "text-white" components/layout/ components/search/ components/cart/ components/auth/` → zero results

## Implementation Order

```
Day 1 — Color (no structure): CartButton, ProfileButton, SearchDialogTrigger, NavDropdown
Day 2 — CSS + core: globals.css, main-header.js, HeaderSearchSummary.js
Day 3 — Layout + sticky: layout.js, StickySearchBar.js
Day 4 — QA: regression tests, grep verify
Day 5+ — separate PRs: hero height, custom font, designSystem tokens
```

## Regression Tests

| Page | Type | Tests |
|------|------|-------|
| `/` `/destinations` `/locations` `/trips` `/activities` `/blog` | Type B | White header, dark logo/nav, Row 2 visible, all 5 items |
| `/checkout` `/login` `/search` | Type A | No nav, white header, 80px offset |
| All breakpoints | Both | Focus rings visible, Slide behavior, StickySearchBar top offset |

## Key Decisions

| Decision | Answer |
|----------|--------|
| Single-row everywhere | No — Type A/B split |
| Keep Explore Thailand | Yes — all 5 items |
| `/blog` header type | Type B — 2-row |
| Mobile hide-on-scroll | Keep Slide |
| Layout offset | Dynamic 80/96px |
| MUI AppBar sx | Optional — globals.css covers |
| Font swap | Separate PR |
| Hero height | Separate PR |

## Tradeoffs
- Loses: dramatic hero overlap (intentional)
- Gains: WCAG contrast, operational clarity, discovery nav continuity

## Related
[[header-redesign-2026-team-review]] · [[smartenplus-glassmorphism-header]] · [[nav-header-redesign-2026-05-24]] · [[mobile-header-redesign-glassmorphism]]

## Related Atoms (Extracted 2026-06-13)
- [[header-rows-context-dynamic-offset]] — Type A=80px / Type B=96px; StickySearchBar consumes `HeaderRowsContext`
- [[header-glass-to-solid-migration]] — glass→solid migration recipe; MUI AppBar `color="inherit"` gotcha
- [[nextjs-fixed-header-per-route]] — atomic pattern: fixed header on homepage, sticky elsewhere
