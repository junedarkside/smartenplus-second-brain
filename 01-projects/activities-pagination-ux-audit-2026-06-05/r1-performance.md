---
name: r1-performance
description: Specialist C — Frontend Performance. Pagination + min-h trigger layout shift. CLS improvement if min-h removed.
metadata:
  type: specialist-r1
  role: performance-engineer
  page: gyg-card-conventions
  smartenplus_route: /activities
---

# R1-Performance — Frontend Performance (Pagination)

**Goal:** address layout shift (CLS), paint cost, and time-to-interactive concerns.

**Performance principles:**
- Minimize CLS (Cumulative Layout Shift) — Google Core Web Vital
- No forced paint of empty area
- Fast TTI (Time to Interactive)

---

## Patterns (3 candidates)

| # | Pattern | ROI | Brand-fit | Effort |
|---|---------|-----|-----------|--------|
| P-1 | Replace `min-h-[calc(100vh-6rem)]` with `min-h-0` or remove | high (CLS improvement) | yes | trivial |
| P-2 | SSR/SSG the first page (no client wait for `useGetContractsQuery`) | med (TTI improvement) | yes (already in 2026-06-04 plan) | large (separate task) |
| P-3 | Lazy-load images beyond first 6 cards | low (CLS) | yes | small |

## Why P-1 = P0 (paired with V-1)

`min-h-[calc(100vh-6rem)]` on outer 2-col grid:
- Forces browser to reserve viewport-minus-6rem height on initial paint
- Even if results list is 200px tall, page claims 600-700px
- Creates layout shift when content actually loads (CLS)
- Wastes paint cycles on empty area

Removing it: page collapses to content height. No reserved space. No shift.

## Why P-2 Deferred

SSR/SSG first page = `getServerSideProps` or `getStaticProps` returning initial contracts. Then `useGetContractsQuery` re-fetches on client for freshness. Big TTI win but:
- Requires backend SSR endpoint optimization
- Conflicts with filter state hydration
- Already noted in 2026-06-04 plan as separate task

Defer.

## Why P-3 Deferred

Images already `loading="lazy"` (DayTripCard.js:142). Beyond-first-6 lazy is a small win, not core perf. Defer to image-optimization task.

## Implementation Hint (P-1)

Same as V-1 — pure class removal. Pairs with V-1.

## Related

- [[r1-ux]]
- [[r1-visual]]
- [[r2-skeptic]]
- [[r3-leader-synthesis]]
- [[../gyg-page-analysis-2026-06-04]] — sibling: detail page audit
