# Sidebar Sticky Two-Column Responsive Grid

## Summary
`lg:grid-cols-[240px_1fr]` layout with sidebar wrapper using `StickySidebar` (inner content `max-h-[calc(100vh-100px)] overflow-y-auto`, NOT on StickySidebar itself), 240px width from `SIDEBAR_CONFIG.widthValue` token, 4-col card grid at 1440px.

## Context
Card-grid pages with a left filter/category sidebar (experiences marketplace, activity browse, search results) all converge on the same 1440px-wide layout. The math — 240 sidebar + 48 gap + 4×288 cards = 1440 — recurs across redesigns and gets re-derived each time. During the 2026-06 experiences marketplace redesign the `overflow-y-auto` was placed on the `StickySidebar` component itself, which silently broke sticky positioning on the experience-detail page.

## Problem
Three recurring issues:
1. Re-deriving the 1440px math (which sidebar width, gap, card width) on every redesign.
2. Putting `overflow-y-auto` on the sticky element — this creates a new scroll container that defeats `position: sticky`.
3. Hardcoding `240px` directly in Tailwind classes instead of pulling from the design token.

## Details
The wrapper structure:

```jsx
<div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-12">
  <StickySidebar offsetTop={100}>
    <div className="max-h-[calc(100vh-100px)] overflow-y-auto pr-2">
      {/* filters */}
    </div>
  </StickySidebar>
  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
    {/* cards */}
  </div>
</div>
```

Key rules:
- `240px` must come from `SIDEBAR_CONFIG.widthValue` token (from `helpers/designTokens.js`).
- `StickySidebar` is a positioning helper — `overflow-y-auto` belongs on an inner `<div>`.
- The `max-h-[calc(100vh-100px)]` accounts for the sticky offset (100px header).
- At `lg` breakpoint the layout flips to 2-col; mobile/tablet use stacked single column.

## Decision
Standardize the 1440px math in the design token + codify the inner-overflow pattern in `CODE_PATTERNS.md`. Card width 288px + sidebar 240px + 48px gap × 3 = 1440, leaving the page padding of 96px (48 each side) inside the standard container.

## Tradeoffs
- A nested scroll container on long filter lists is necessary to keep the page header visible while filters scroll independently.
- Sticky breaks if any ancestor has `overflow: hidden` or its own `overflow` — keep the chain clean.
- 240px is tight for nested filter categories with labels in Thai; revisit if filter UX grows.

## Consequences
Future card-grid + sidebar pages (search results, category browse) must reuse this template. Audit `layout-spacing-consistency` on each new page to catch hardcoded `240` or misplaced `overflow-y-auto`. Adding the pattern to the design system means a single token change resizes all sidebar pages.

## Related
- [[carousel-design-standard]] — same 1440px container width; sibling pattern.
- [[section-contentcard-wrapper-pattern]] — card sizing inside the 4-col grid.
- [[layout-spacing-consistency-audit-2026-06-01]] — caught the misplaced `overflow-y-auto` and the hardcoded 240.
