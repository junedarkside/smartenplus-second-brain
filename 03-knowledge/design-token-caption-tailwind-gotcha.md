# Design Token Gotcha — TYPOGRAPHY_SCALE.caption is a Tailwind String

## Summary

`TYPOGRAPHY_SCALE.caption` in `helpers/designSystem.js` equals `'text-xs'` — a Tailwind utility class string, not an object. Accessing `.fontSize` returns `undefined`. Passing `undefined` to MUI `sx` silently drops the style.

## Problem

```js
// WRONG — .fontSize is undefined on a Tailwind string
sx={{ fontSize: TYPOGRAPHY_SCALE.caption.fontSize }}

// Result: font size not applied, no error thrown, bug invisible
```

## Context

`designSystem.js` mixes two conventions: some tokens are objects (e.g. `TYPOGRAPHY_SCALE.h1 = { xs: '1.5rem', sm: '2rem' }` for responsive MUI `sx` use), others are Tailwind strings (`TYPOGRAPHY_SCALE.caption = 'text-xs'` for className use). The two conventions are incompatible — you can't use a Tailwind class string inside MUI `sx`.

## Fix

Option A — use raw value (safe for MUI sx):
```js
sx={{ fontSize: '0.75rem' }}  // 12px = text-xs equivalent
```

Option B — add a parallel MUI token to designSystem.js:
```js
export const MUI_FONT_SIZES = {
  caption: '0.75rem',
  body: '0.875rem',
};
// then: sx={{ fontSize: MUI_FONT_SIZES.caption }}
```

Option C — use Tailwind class on className, not sx:
```jsx
<Typography className="text-xs">...</Typography>
```

## Rule

Never use `TYPOGRAPHY_SCALE.*` in MUI `sx` props unless you verify it's an object (responsive map) not a Tailwind string. Check `designSystem.js` before use.

## Discovery

Caught during scrutinize pass on `activities-day-tour-page-review-2026-06-01`. DS-1 finding — incorrectly recommended `TYPOGRAPHY_SCALE.caption.fontSize` as fix, scrutinize corrected it.

## Related

- [[activities-day-tour-page-review-2026-06-01]] — DS-1
- `helpers/designSystem.js` — token source
