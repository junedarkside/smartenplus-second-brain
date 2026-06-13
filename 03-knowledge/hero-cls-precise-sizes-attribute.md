# Hero CLS Precise Sizes Attribute

## Summary
For `next/image` rendering inside a CSS grid (e.g. `grid-cols-4`), the `sizes` attribute must match the actual grid breakpoints. For `grid-cols-N` galleries: `(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw`. Wrong `sizes` = wrong srcset variant selected = bandwidth waste + Cumulative Layout Shift.

## Context
`next/image` picks a srcset variant based on viewport width AND the `sizes` hint. If `sizes` claims the image is rendered at 50vw but the CSS actually displays it at 25vw, the browser downloads a larger file than needed. If `sizes` is too small, the browser downloads a smaller file and the image upscales — causing CLS.

## Problem
`LocationGridComponent.js:59` was a real production bug: a `grid-cols-4` location grid with `sizes="50vw"` was downloading 2x larger images than needed on desktop, costing real bandwidth and LCP regression. The bug recurs because `sizes` is treated as a guessable string, not a derived attribute.

## Details
Derive `sizes` from the actual grid configuration:

```jsx
// For grid-cols-4 with Tailwind breakpoints sm:640, md:768, lg:1024
<Image
  src={location.photo}
  alt={location.name}
  width={400}
  height={300}
  sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
  priority={false}
/>
```

Mapping rule:
- `grid-cols-1` (mobile-first): `(max-width: 640px) 100vw, 25vw`
- `grid-cols-2` mobile + 4 desktop: `(max-width: 640px) 100vw, (max-width: 768px) 50vw, 25vw`
- `grid-cols-1 → 2 → 3 → 4`: `(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw`

Use Chrome DevTools Network tab throttling to verify the downloaded variant matches the rendered CSS width. The `priority` flag is independent — only the LCP image needs it.

## Decision
Make `sizes` a code-review checklist item for every `next/image` in a grid. Reject any PR where `sizes` doesn't include breakpoints matching the grid's Tailwind class.

## Tradeoffs
- Pro: correct srcset = faster LCP, lower bandwidth, no CLS.
- Pro: predictable test surface (you can assert the string).
- Con: the `sizes` string drifts when the grid changes — must update both the class and the prop together.
- Con: easy to leave stale `sizes` on refactored grids.

## Consequences
- Every `next/image` in a grid is suspect until proven correct.
- LCP regression hunts should always start with `sizes` audit.
- Future grid components should export `sizes` as a derived constant from the grid config.

## Related
- [[structured-data-schema-patterns]] — `image` field in schema needs to match the actual rendered URL, not the srcset variant.
