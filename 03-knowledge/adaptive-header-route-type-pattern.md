# Adaptive Header: Type A/B Route-Type Pattern

## Summary
Header adapts row structure by route type. Type A (transactional) = single 80px row. Type B (discovery) = dual 96px rows. Dynamic offset via React Context — no prop-drilling, no hardcoded pixels.

## Context
`header-redesign-2026-team-review.md` (2026-05-28). Header specced "single-row everywhere" — incorrect. Actual taxonomy needs two layouts.

## Problem
Original spec assumed one header height. Transactional pages (`/checkout`, `/payment`, `/login`, `/register`, `/search`) need logo + utilities only. Discovery pages (`/`, `/destinations`, `/locations`, `/trips`, `/activities`, `/blog`) need logo + nav + utilities. Single-height broke nav visibility on browse pages.

## Decision

### Type A — Single Row (80px)
Transaction pages. `ONE_ROW_PATHS` list. No Row 2 nav. Top padding: `80px`.

### Type B — Dual Row (96px)
Discovery pages. All 5 nav items visible including "Explore Thailand". Top padding: `96px`.

### ONE_ROW_PATHS
```js
const ONE_ROW_PATHS = ['/checkout', '/payment', '/login', '/register', '/search', '/blog'];
```
`/blog` removed from Type A — needs Row 2 nav.

### HeaderRowsContext
```jsx
// layout.js exports
export const HeaderRowsContext = React.createContext({ rows: 1, offset: 80 });

// In layout.js
const rows = isOneRowPath ? 1 : 2;
const offset = rows === 1 ? 80 : 96;
<HeaderRowsContext.Provider value={{ rows, offset }}>
 {children}
</HeaderRowsContext.Provider>
```

### StickySearchBar Offset
```jsx
const { offset } = React.useContext(HeaderRowsContext);
// style={{ top: isMobile ? 56 : offset }}
```
No hardcoded `top-[80px]` — adapts to route type automatically.

## Details

### Layout Offset Decision
| Route Type | Header Height | StickySearchBar Top |
|------------|---------------|---------------------|
| Type A (transactional) | 80px | 80px |
| Type B (discovery) | 96px | 96px |

### Mobile StickySearchBar
Always `56px` on mobile — mobile header is 56px fixed.

### Nav Items (Type B)
All 5 items from `constants/navConfig.js`. "Explore Thailand" NOT removed (rejected M-4 decision).

## Tradeoffs
- Context adds provider layer in layout.js — minimal overhead
- Type detection relies on path matching — maintain `ONE_ROW_PATHS` when adding routes
- 16px height delta intentional — nav row breathing room on discovery pages

## Consequences
- StickySearchBar must consume context (no hardcoded values)
- `layout.js` sets dynamic padding: `md:pt-[80px]` or `md:pt-[96px]`
- Regression matrix covers `/blog` as Type B (Row 2 visible)

## Related
- [[header-redesign-2026-spec]] — full spec with locked decisions
- [[sidebar-sticky-2col-responsive-grid]] — sticky positioning patterns