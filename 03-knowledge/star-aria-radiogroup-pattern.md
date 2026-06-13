# Star Rating ARIA Radiogroup Pattern

**Date:** 2026-06-06
**File:** `components/RateAndReview/RateAndReviewForm.js`

## Wrong Pattern (aria-pressed)

```jsx
// WRONG — aria-pressed on star buttons
<div className="flex items-center gap-1">
  {[1,2,3,4,5].map((value) => (
    <IconButton
      aria-pressed={value <= rating}   // ← wrong semantics
      aria-label={`Rate ${value} stars`}
    >
```

`aria-pressed` signals toggle state (on/off). Stars are mutually exclusive selection — screen readers announce "pressed/not pressed" on every button instead of the selected value.

## Correct Pattern (radiogroup/radio)

```jsx
<div role="radiogroup" aria-labelledby="rating-label" className="flex items-center gap-1">
  {[1, 2, 3, 4, 5].map((value) => (
    <IconButton
      key={value}
      role="radio"
      aria-checked={value === rating}   // ← exact match only, not <=
      aria-label={`${value} star${value !== 1 ? 's' : ''} — ${ratingLabels[value]}`}
      onClick={() => setRating(value)}
    >
```

- `role="radiogroup"` on container + `aria-labelledby` pointing to label
- `role="radio"` + `aria-checked={value === rating}` on each button
- `aria-label` includes rating word label (e.g. "3 stars — Good")

## Why P0

WCAG 1.3.1 + 4.1.2. Screen reader announces radio group correctly: "Rating group, 1 star Poor, 2 stars Fair…" Tab navigation works. `aria-pressed` pattern causes each star to announce independently as a toggle with no group context.

## Companion Pattern

`IconButton` inside any click+keydown-handled card wrapper needs BOTH `onClick` and `onKeyDown` `stopPropagation` — see [[iconbutton-keydown-stoppropagation-card]]. The two patterns frequently co-occur in review cards (rate widget + favorite heart inside a clickable card).
