# FeaturedImageHeader — Width Bug Post-Mortem

## Summary
Hero image in `FeaturedImageHeader` was overflowing viewport on sub-1200px screens. Bug introduced via a misguided "fix", then overcorrected, then resolved. Documented for future reference.

## Problem
`/trips/hatyai/koh-lipe` and all trip/activity pages using `FeaturedImageHeader`: hero image caused horizontal scroll on mobile/tablet.

## Root Cause Chain

### Commit `d5f1029` (2026-05-26) — Correct baseline
```jsx
<div className="flex justify-center">
  <div className={`absolute max-w-[1200px] mx-auto w-full min-h-...`}>
```
**Correct.** `max-w-[1200px]` clamps image width. `w-full` fills up to that max. Works on all viewport widths.

### Commit `0ebd755` (2026-05-30) — Bug introduced
Reasoning in commit message: _"w-full + max-w-[1200px] = full viewport width. Removed w-full, used explicit w-[1200px]"_

Changed `w-full` → `w-[1200px]` (hardcoded):
```jsx
<div className="max-w-[1200px] mx-auto flex justify-center">
  <div className={`absolute max-w-[1200px] mx-auto w-[1200px] min-h-...`}>
```

**This reasoning was wrong.** `max-w-[1200px]` correctly clamps `w-full` to ≤1200px. The author saw the image appearing "full width" at viewport ≥1200px (correct behavior — fills up to 1200px) and misread it as broken. Replacing `w-full` with `w-[1200px]` hardcodes 1200px, which overflows every viewport < 1200px.

### This session — Overcorrection
"Fix" collapsed two divs into `absolute inset-0`. Removed 1200px constraint entirely. Image became full-bleed (100vw). Wrong direction — design intent is constrained hero, not full-bleed.

### Final fix — Restored correct baseline
Reverted `w-[1200px]` back to `w-full`. Current state matches `d5f1029` baseline.

## CSS Mechanics (for future AI/devs)

**Why `max-w-[1200px]` + `w-full` works on `absolute` elements:**

`absolute` elements get their width from `w-full` = 100% of the containing block (nearest `position: relative` ancestor = the `<header>`, which is `w-full` = 100vw). So `w-full` alone = 100vw. But `max-w-[1200px]` directly on the `absolute` div clamps it to ≤1200px. Result: `min(100vw, 1200px)` — responsive and capped. Correct.

**Why `w-[1200px]` breaks it:**

Hardcoded width bypasses responsiveness. At 375px viewport: element is 1200px wide, overflows by 825px. Horizontal scroll. `max-w` does nothing when `w` is already explicit.

**Rule: never use `w-[Npx]` hardcoded on layout-spanning elements. Use `w-full` + `max-w-[Npx]`.**

## Guardrail
```
NEVER: w-[1200px] on absolute/layout divs
ALWAYS: w-full + max-w-[1200px] for constrained-but-responsive width
```

## Correct Pattern (current, verified)
```jsx
<div className="max-w-[1200px] mx-auto flex justify-center">
  <div className={`absolute max-w-[1200px] mx-auto w-full ${minHeight}`}>
    {/* Next/Image fill + objectFit cover */}
  </div>
</div>
```

## File
`components/UI/FeaturedImageHeader.js:120–121`

## Related
[[airport-transfer-width-audit-2026-05-30]] [[header-redesign-2026-spec]]
