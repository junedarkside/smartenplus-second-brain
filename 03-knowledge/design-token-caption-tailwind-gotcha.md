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

**Related JIT gotcha:** a Tailwind-class token stored as a JS string and used via `className={LAYOUT.pageContentClasses}` is only safe because Tailwind's content glob includes `./helpers/**/*.{js,ts,jsx,tsx}` (`tailwind.config.js`), so the literal class string is scanned there. Do NOT build classes by interpolating a breakpoint prefix onto a token (`` `sm:${TOKEN}` ``) — JIT scans static text, won't see the composed `sm:rounded-md`, class silently missing. Interpolate only whole token values, or write the prefixed class as a literal. (operators width-token work, #124)

Part of [[activities-day-tour-page-review-2026-06-01]] DS-1 finding.

## Related
- [[design-systems]]
- [[activities-day-tour-page-review-2026-06-01]]
