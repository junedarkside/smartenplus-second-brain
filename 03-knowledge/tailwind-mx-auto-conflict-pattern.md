# Tailwind `mx-auto` Conflict Pattern

## Summary

`mx-auto` + any `mx-{n}` on same element = centering broken. Last utility wins (Tailwind JIT), so `mx-2` overrides `mx-auto` and left-shifts the container.

## Problem

```jsx
// BROKEN — mx-2 overrides mx-auto
<section className="max-w-[1200px] mx-auto mx-2 md:mx-3 xl:mx-0">
```

`mx-auto` sets `margin-left: auto; margin-right: auto`. `mx-2` sets `margin-left: 0.5rem; margin-right: 0.5rem`. Both expand to the same CSS property. Tailwind JIT generates both classes; browser applies last matching rule → centering lost.

## Fix

Two-layer approach: outer handles centering + max-width, inner handles edge breathing room via **padding** (not margin).

```jsx
// CORRECT — centering + edge spacing separated
<section className="max-w-[1200px] mx-auto">
  <div className="px-2 md:px-3 xl:px-0">
    {children}
  </div>
</section>

// OR — if section itself needs padding, use px- directly on it
<section className="max-w-[1200px] mx-auto px-2 md:px-3 xl:px-0">
  {children}
</section>
```

## Site-Wide Spacing Pattern (SmartEnPlus)

| Layer | Classes | Files |
|-------|---------|-------|
| Container centering | `max-w-[1200px] mx-auto` | All browse/detail pages |
| Edge breathing (tight) | `px-2 md:px-3 xl:px-0` | Trip detail, RelatedTrips |
| Edge breathing (standard) | `px-4 xl:px-0` | Homepage sections |
| Card inner padding | `p-4` or `p-4 md:p-5` or `p-4 md:p-6` | ContentCard, RelatedTrips inner |

Never mix `mx-auto` with `mx-{n}` on same element. Keep centering on outer, breathing room via `px-` on same or inner element.

## Where Found

`pages/trips/detail/[...slug].js` — FAQ section had `max-w-[1200px] mx-auto mx-2 md:mx-3 xl:mx-0`. Fixed session #259 (`1e6eaec0`).

## Related

- [[layout-spacing-consistency-audit]] — canonical spacing values per page type
- [[design-token-caption-tailwind-gotcha]] — other Tailwind class conflict patterns
