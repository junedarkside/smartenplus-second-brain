# Header Rows Context for Dynamic Offset

## Summary
Header height varies by route — Type A (operational, transactional) = 80px, Type B (discovery, browse) = 96px. Layout padding + StickySearchBar top must consume a `HeaderRowsContext` to stay in sync. Type A paths: `/checkout`, `/payment`, `/login`, `/register`, `/search`. Note: `/blog` is Type B (2-row with nav).

## Context
The site header has two variants: Type A is a single-row operational header (logo + auth actions, no nav) used on transactional routes. Type B is a 2-row discovery header (logo + search + nav) used on browse routes. The two have different heights (80px vs 96px). Below the header, the page content + StickySearchBar must reserve the right amount of vertical space — otherwise the StickySearchBar overlaps content or leaves a gap.

## Problem
Hardcoding `padding-top: 80px` (or 96px) in CSS makes every page off by one row on the wrong route type. The StickySearchBar's `top` value must match the header height exactly, or the bar floats over content / sits below the header with a gap. A context that exposes the current header height lets consumers (page layouts, sticky elements, modals) consume it dynamically.

The pattern is fragile: if you add a new Type A route and forget to update the path predicate, the wrong header height is used. If you add a new sticky element, it must also consume the context.

## Details
The context:

```js
// contexts/HeaderRowsContext.js
import { createContext, useContext } from 'react';

const HeaderRowsContext = createContext({ height: 96, type: 'B' });

export const HeaderRowsProvider = HeaderRowsContext.Provider;
export const useHeaderRows = () => useContext(HeaderRowsContext);
```

The provider lives in the route-aware layout (e.g., `components/Header/index.js`):

```js
const TYPE_A_PATHS = ['/checkout', '/payment', '/login', '/register', '/search'];

function getHeaderType(pathname) {
  if (TYPE_A_PATHS.some(p => pathname.startsWith(p))) return { height: 80, type: 'A' };
  return { height: 96, type: 'B' };  // includes /blog
}

export function Header({ router }) {
  const { height, type } = getHeaderType(router.pathname);
  return (
    <HeaderRowsProvider value={{ height, type }}>
      {type === 'A' ? <TypeAHeader /> : <TypeBHeader />}
    </HeaderRowsProvider>
  );
}
```

Consumers:

```js
// components/StickySearchBar.js
const { height } = useHeaderRows();
return <div style={{ top: height, position: 'sticky' }}>...</div>;

// pages/checkout.js
const { height } = useHeaderRows();
return <main style={{ paddingTop: height }}>...</main>;
```

`/blog` is intentionally Type B — the blog has a nav row below the logo (categories, recent posts) even though it's a content surface, not a discovery surface. Don't classify it as Type A.

## Decision
- Use `HeaderRowsContext` to expose `{ height, type }` to all layout-level consumers
- Type A predicate: `pathname` starts with `/checkout`, `/payment`, `/login`, `/register`, `/search`
- Type B is the default (includes `/blog`, `/help`, `/`, `/activities`, etc.)
- All sticky elements + page-level `padding-top` MUST consume the context
- New Type A routes must be added to the predicate explicitly

## Tradeoffs
- Pro: One source of truth for header height
- Pro: Consumers can react to type changes (e.g., show different CTAs)
- Pro: Adding a new sticky element is just `useHeaderRows()` — no height hardcoding
- Con: The path predicate is a string list — easy to forget a new route. Mitigate with a comment + audit.
- Con: Context adds a render dependency. Components that consume it re-render when the value changes (rare, but worth knowing).
- Con: If the header gets a third type (e.g., minimal `/embed/*` route), the context shape and predicate both need updating.

## Consequences
Header + StickySearchBar coordination is the most fragile layout pattern in the app. The context enforces correctness. Future devs adding a new sticky element, modal, or floating CTA MUST consume `useHeaderRows()`. Hardcoding `top: 80` or `top: 96` in CSS is a red flag.

The Type A path list is a config surface — any new transactional route (e.g., `/account/orders/[id]`) needs an explicit entry. Document this in the route-type review checklist.

## Related
- [[nextjs-fixed-header-per-route]] — sibling pattern for per-route header behavior
