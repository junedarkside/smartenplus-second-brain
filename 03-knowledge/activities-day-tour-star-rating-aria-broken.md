---
name: activities-day-tour-star-rating-aria-broken
description: Star rating component ARIA broken — multiple simultaneous `aria-pressed` true on all stars. Violates WCAG 1.3.1 (name/role). Screen reader announces all stars pressed simultaneously.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: activities-day-tour-page-review
---

# Activities Day-Tour — Star Rating ARIA Broken

## Summary
Star rating component ARIA broken — multiple simultaneous `aria-pressed=true` on all stars. WCAG 1.3.1 violation. Screen reader announces all stars pressed.

## Why It Matters
Accessibility blocker. Blind users can't determine rating value. Compliance risk (WCAG AA required for many markets).

## Detail
**Bug pattern:**
```jsx
{[1,2,3,4,5].map(rating => (
  <button
    aria-pressed={selectedRating === rating}  // WRONG — multiple true
    onClick={() => setSelectedRating(rating)}
  >
    ★
  </button>
))}
```

When user clicks 3 stars, buttons 1-3 all have `aria-pressed=true`. Screen reader: "star pressed, star pressed, star pressed" — ambiguous.

**Fix:**
```jsx
<button
  aria-pressed={selectedRating === rating ? 'true' : 'false'}  // Single true
  aria-label={`Rate ${rating} stars`}
  onClick={() => setSelectedRating(rating)}
>
  ★
</button>
```

**Better:** Use radiogroup pattern (single choice):
```jsx
<div role="radiogroup" aria-label="Rating">
  {[1,2,3,4,5].map(rating => (
    <input
      type="radio"
      name="rating"
      value={rating}
      checked={selectedRating === rating}
      aria-label={`${rating} stars`}
    />
  ))}
</div>
```

## Constraints / Gotchas
Visual component must update to match accessible markup. Radios need custom styling to look like stars.

## Related
- [[activities-day-tour-stored-xss-page-crash]] — companion Critical bugs
- [[activities-day-tour-page-review]] — parent audit
