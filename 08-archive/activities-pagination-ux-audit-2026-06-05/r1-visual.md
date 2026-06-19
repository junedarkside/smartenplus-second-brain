---
name: r1-visual
description: Specialist B — Visual Designer. Grid + rhythm. min-h on outer wrapper is the bigger visual problem than orphan cells.
metadata:
  type: specialist-r1
  role: visual-designer
  page: gyg-card-conventions
  smartenplus_route: /activities
---

# R1-Visual — Visual Designer (Pagination)

**Goal:** address grid rhythm + dead space concerns beyond the orphan card pattern.

**Visual principles:**
- Grid should breathe, not stutter
- No dead space on short result lists (premium calm)
- Card width consistent across breakpoints

---

## Patterns (3 candidates)

| # | Pattern | ROI | Brand-fit | Effort |
|---|---------|-----|-----------|--------|
| V-1 | Remove `min-h-[calc(100vh-6rem)]` on outer grid (line 116) | **high** (no dead space) | yes (premium calm) | trivial (delete 1 class) |
| V-2 | Use CSS grid `auto-fill, minmax(280px, 1fr)` for true responsive card width | med (variable col count) | maybe (changes card width) | medium |
| V-3 | Reduce desktop `md=4` → `md=3` keeping `lg=4 lg=4 xl=4` | low (reflow only) | yes | trivial |

## Why V-1 is P0 (paired with UX-1)

`min-h-[calc(100vh-6rem)]` on the outer 2-col grid (sidebar + results) means: when results list is short, the entire wrapper stays at viewport-minus-6rem height. Result column shows blank space below cards. This compounds the orphan problem visually — empty cells + empty space = "broken page" perception.

**Without removing min-h:** even with 12 cards, dead space remains below the grid.

**With min-h removed:** page collapses to content height. No visual dead space.

## Why V-2 Auto-Drop

CSS grid `auto-fill, minmax(280px, 1fr)` is mathematically elegant (variable col count by viewport, no media queries) BUT:
- Changes card width unpredictably — risk of regression in card anatomy
- Conflicts with existing MUI `Grid` breakpoints
- Effort > risk

Defer to dedicated reflow task.

## Why V-3 Auto-Drop

Cosmetic only. The 16-card orphan is the real issue, not column count. Reducing md col to 3 doesn't help — orphan still appears when 16/3=5.33.

## Implementation Hint (V-1)

`components/activities/browse/FilterDayTripsPage.js:116`:

```jsx
// BEFORE
<div className="grid gap-6 min-h-[calc(100vh-6rem)] lg:grid-cols-[240px_1fr]">
// AFTER
<div className="grid gap-6 lg:grid-cols-[240px_1fr]">
```

1 LoC. Pure CSS class removal.

## Related

- [[r1-ux]]
- [[r1-performance]]
- [[r2-skeptic]]
- [[r3-leader-synthesis]]
