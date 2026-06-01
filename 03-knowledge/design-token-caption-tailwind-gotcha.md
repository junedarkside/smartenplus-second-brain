# Design Token Gotcha — TYPOGRAPHY_SCALE.caption

**Issue:** `TYPOGRAPHY_SCALE.caption = 'text-xs'` (Tailwind string). `.fontSize` is `undefined`.

**Wrong:**
```js
sx={{ fontSize: TYPOGRAPHY_SCALE.caption }}  // undefined — breaks MUI
```

**Right:**
```js
sx={{ fontSize: '0.75rem' }}  // raw value
// OR add to designSystem.js:
MUI_FONT_SIZES: { caption: '0.75rem' }
sx={{ fontSize: MUI_FONT_SIZES.caption }}
```

**Impact:** `CategoryFilter.js`, `DayTripCard.js` ×5 instances. Never use Tailwind string tokens in MUI `sx` prop.

**Principle:** Separate token layers: Tailwind tokens (`text-xs`) for className, MUI tokens (`rem` values) for sx.

Part of [[activities-day-tour-page-review-2026-06-01]] DS-1 finding.

## Related
- [[design-systems]]
- [[activities-day-tour-page-review-2026-06-01]]
