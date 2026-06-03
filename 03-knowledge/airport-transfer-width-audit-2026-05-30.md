# Width Inconsistency Audit — airport-transfer post-calendar sections

**Date:** 2026-05-30
**Status:** UNRESOLVED — root cause identified, fix reverted
**Next team:** See Section 4

---

## Summary

User reported `/airport-transfer/hatyai-airport` (and `/airport-transfer/phuket-airport`) post-calendar sections visually narrower than calendar above. Investigation confirmed. Applied fix broke layout — reverted. No progress.

---

## What Was Investigated

### Agent team (3 parallel agents)

| Agent | Task |
|-------|------|
| `trips-snapshot` | Playwright browser read of `http://localhost:3000/trips/hatyai/koh-lipe` — post-calendar section structure |
| `airport-snapshot` | Playwright browser read of `http://localhost:3000/airport-transfer/hatyai-airport` — post-calendar section structure |
| `file-structure` | Codebase exploration of page files + shared wrappers for both pages |

### Key files examined

- `pages/airport-transfer/[slug].js:253-291` — post-calendar container
- `pages/trips/[...slug].js` + `components/trips/FilterTripsPage.js:266-283`
- `components/destinations/StationInformation.js`
- `components/destinations/GuidesSection.js`
- `components/image/ProductCardContainer.js`
- `components/airport-transfer/TripListingSection.js:104-127`

---

## Root Cause (Confirmed)

### Both pages use identical `max-w-[1200px]` container structure

| Page | Outer section | Inner container |
|------|--------------|-----------------|
| Trips page | `<section className='w-full mx-auto z-10'>` | `max-w-[1200px] mx-auto flex flex-col gap-2` |
| Airport-transfer | (none — inline `<div>`) | `max-w-[1200px] mx-auto flex flex-col gap-2` |

**No structural difference in container itself.**

### Problem: inner horizontal margins on StationInformation + GuidesSection

Both components sit INSIDE `max-w-[1200px]` but have additional horizontal constraints:

| Component | Element | Class | Effect |
|-----------|---------|-------|--------|
| `StationInformation.js:15` | outer `<section>` | `px-2 md:px-3` | Inner content narrower by ~32-48px |
| `StationInformation.js:25` | inner `<section>` | `mx-3` | Further narrows map link section by ~24px each side |
| `GuidesSection.js:12` | outer `<section>` | `px-2 md:px-3` | Inner content narrower by ~32-48px |
| `ProductCardContainer.js:28` | grid wrapper | `mx-2` | Grid cards narrower by ~16px each side |

Margins exist INSIDE `max-w-[1200px]` — content doesn't reach full width.

### HTML from user's snapshot confirms

```html
<!-- GuidesSection outer section -->
<section class="relative sm:rounded-lg bg-white flex flex-col gap-2 px-2 md:px-3">
  <!-- inner grid -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-2 mx-2">
```

---

## Attempted Fix (Reverted)

### Changes applied (then reverted)

**File 1:** `components/destinations/StationInformation.js`
- Line 15: removed `px-2 md:px-3` from outer `<section>`
- Line 25: removed `mx-3` from inner `<section>`

**File 2:** `components/destinations/GuidesSection.js`
- Line 12: removed `px-2 md:px-3` from outer `<section>`

**File 3:** `components/image/ProductCardContainer.js`
- Line 28: removed `mx-2` from grid wrapper

### Result

User reported "totally fuckup" — likely because:
- Removing `px-2 md:px-3` from GuidesSection outer section collapsed internal padding, breaking card layout
- Removing `mx-2` from ProductCardContainer removed only horizontal margin on grid, cards touch edges
- Components have content needing internal spacing — can't blanket-remove margins

### Files reverted to original state.

---

## Next Team: Correct Approach

### Real problem

Sections ARE inside `max-w-[1200px]`. Issue not the outer container — StationInformation + GuidesSection look narrower because:

1. White `bg-white` + `rounded-lg` backgrounds — visually distinct from page bg
2. Inner content (map, blog cards) has own padding/margins creating "content area" appearing narrower than section itself
3. Calendar above has NO such visual treatment — transparent/embedded, appears wider

### Recommended fix (DIFFERENT from attempted fix)

**Do NOT remove all padding.** Instead:

1. Identify what "full width" means visually — should white card sections extend to 1200px edges, or have internal padding?
2. If full-width white cards desired: `px-2 md:px-3` is correct — provides breathing room. Issue is PARENT `max-w-[1200px]` has `mx-auto` centering — card appears centered at 1200px max.
3. ACTUAL fix likely requires: ensure StationInformation and GuidesSection outer `<section>` spans full viewport width (`w-full`) and inner content constrained to `max-w-[1200px] mx-auto` — NOT current reversed structure.

### Specific files needing redesign

**Option A — Full-width sections with centered content:**
- `components/destinations/StationInformation.js` — outer `section` → `w-full`, inner wrapper → `max-w-[1200px] mx-auto`
- `components/destinations/GuidesSection.js` — same pattern

**Option B — Keep sections inside container, accept `px-2 md:px-3` padding:**
- Current behavior — sections correctly constrained. "Visual mismatch" may be perceived only because StationInfo/Guides have white bg vs calendar's transparent bg.
- If so: no code change needed — explanation to user sufficient.

---

## Verification Steps (for next team)

1. Run `npm run dev`
2. Navigate to `http://localhost:3000/airport-transfer/phuket-airport`
3. Inspect in DevTools:
   - Calendar section wrapper: measure width → should be `max-w-[1200px]` centered
   - StationInformation section: measure width → same?
   - GuidesSection: measure width → same?
4. If StationInfo/Guides appear narrower — use "Compute" tab to find which element/css constrains width
5. Compare with trips page at same viewport

---

## What NOT to do

- Do NOT blindly remove `px-2 md:px-3` or `mx-2` from components without understanding content flow
- `ProductCardContainer.js` shared across many pages — changing affects all uses
- Previous fix too aggressive — removed semantically necessary spacing

---

## Related Vault Pages

- `03-knowledge/transportation-category-audit-2026-05-30.md` — AT-1 redesign spec (separate issue)
- `docs/width-inconsistency-audit-2026-05-30.md` — earlier audit report (partial)