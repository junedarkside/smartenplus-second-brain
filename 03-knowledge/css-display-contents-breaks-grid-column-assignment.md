---
name: css-display-contents-breaks-grid-column-assignment
description: Tailwind `contents` (display:contents) on a CSS Grid child dissolves its box and promotes its own children into the grid's auto-placement — they scatter across all columns/rows instead of staying confined to the parent's assigned cell.
metadata:
  type: knowledge
  status: active
  date: 2026-08-14
  parent: trip-card-cta-column-redesign
---

# CSS `display:contents` Breaks Grid Column Assignment

## Summary
Using `display:contents` (Tailwind `contents`, e.g. `sm:contents`) on an element inside a CSS Grid does not make its children "count as" the parent's grid cell. It dissolves the parent's box entirely — its children become direct grid items themselves, auto-placed by the grid algorithm across all available columns/rows, not confined to wherever the dissolved wrapper would have sat.

## Why It Matters
Produced a real, user-visible bug: a 3-column grid meant to be "left zone | divider | CTA column" instead smeared every element (times, journey stepper, trust chips, price, button) into one horizontal row/scattered cells, because the left-zone wrapper used `sm:contents` hoping its children would visually stack within column 1. They didn't — CSS Grid doesn't retain the dissolved element's cell assignment for its children.

## Detail
**Broken pattern:**
```jsx
<div className="sm:grid sm:grid-cols-[1fr_auto_auto]">
  <div className="sm:contents">  {/* dissolves — does NOT confine children to col 1 */}
    <TimesRow />
    <StepperRow />
    <ChipsRow />
  </div>
  <Divider />
  <CtaColumn />
</div>
```
`TimesRow`, `StepperRow`, `ChipsRow` become direct children of the grid and get auto-placed left-to-right across the 3 columns, wrapping to new rows only when a row's cells fill — not stacking vertically in column 1 as intended.

**Correct pattern:**
```jsx
<div className="sm:grid sm:grid-cols-[1fr_auto_auto]">
  <div className="flex flex-col gap-2 min-w-0">  {/* real box = one grid item */}
    <TimesRow />
    <StepperRow />
    <ChipsRow />
  </div>
  <Divider />
  <CtaColumn />
</div>
```
A real box (flex-col or block) is exactly one grid item occupying one cell; everything inside stacks normally via its own flex/block layout.

## Constraints / Gotchas
- `display:contents` is for when you want an element's children to participate in the **parent's** layout algorithm directly (e.g. flattening a wrapper so its children can be flex/grid items of a grandparent) — it is not a tool for "this group of things should visually cluster together" inside a grid cell. Those are opposite goals.
- If you need a semantic wrapper (for styling/testing hooks) around content that must span one grid cell, use a real box, not `contents`.

## Related
- [[trip-card-cta-column-redesign]] — where this bug surfaced (#309, `TripItemLayoutV2.js`)
