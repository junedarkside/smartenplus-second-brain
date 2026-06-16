# Header Redesign 2026 — Team Review Report

**Date:** 2026-05-28 (updated with final decisions)
**Specialists:** Design · UX · Frontend + Second audit: UX Architecture · Visual Design · Frontend Engineering
**Subject:** Deep audit of `header-redesign-2026-spec.md` before implementation

> **See [[header-redesign-2026-spec]] for FINAL spec with all decisions locked.**
> This doc preserves audit trail and resolved questions.

## Final Verdict (Updated)

**Spec v1 had one critical architectural flaw: "single-row everywhere" was wrong.**
Second audit caught it. Final design uses Type A/B adaptive split — see spec.
All blockers resolved.

**Spec v1 identified 5 files. Actual count: 12.** Four critical components with hardcoded white colors were missed. All decisions resolved.

## Decisions Locked

| Decision | Resolution |
|----------|------------|
| B-1: Type A vs Type B | **Type A/B split.** ONE_ROW_PATHS = transactional only. /blog → Type B. |
| B-2: Mobile hide-on-scroll | **Keep Slide behavior.** 56px viewport gain. |
| B-3: 2-row nav on browse pages | **Type B keeps Row 2** on all browse pages. All 5 nav items including Explore Thailand stay. |
| M-4: Remove Explore Thailand | **REJECTED.** All 5 nav items stay. |
| Layout offset | **Dynamic:** 80px (A) / 96px (B). |
| StickySearchBar top | **Dynamic via HeaderRowsContext:** 80px or 96px. |
| MUI AppBar sx | **Optional** — globals.css already handles. |

## Critical Blockers (All Resolved)

### B-1: `rows` Prop Behavior Undefined
**Where:** `layout.js:143`, `main-header.js:112`

Current `rows={1}` hides nav on `/checkout`, `/payment`, `/login`, `/register`, `/search`, `/blog`. Spec v1 said "single-row everywhere" but didn't address this.

**Resolution:** Keep `rows` prop logic. Shows nav on most pages, hides on transactional. Type A/B split formalizes this.

### B-2: Mobile Header Hide-on-Scroll
**Where:** `main-header.js:24-26, 56`

`useScrollTrigger` drives TWO behaviors: (1) glass class toggle — removing ✓; (2) `<Slide>` hide header on scroll down — spec v1 silent.

**Resolution:** Keep Slide behavior. 56px viewport gain on mobile. Spec only removes glass, not this.

## High Priority Issues (All Resolved)

### H-1: 5 Files Missing From Spec (Total: 12)

| # | File | Issue |
|---|------|-------|
| 1 | `components/search/SearchDialogTrigger.js` | Line 34: `border-white bg-white bg-opacity-20 text-white` (mobile); Line 46: `bg-gray-800 bg-opacity-80 text-white` (desktop) |
| 2 | `components/cart/CartButton.js` | Line 116: `text-white/70 hover:text-white` |
| 3 | `components/auth/ProfileButton.js` | Line 367: `text-white/70 hover:text-white` |
| 4 | `components/layout/NavDropdown.js` | Line 50: active = `text-brand-primary border-brand-primary` → needs `gray-900` |
| 5 | `components/search/HeaderSearchSummary.js` | Multiple `text-white / text-white/80 / text-white/40` |

**All resolved** — addressed in spec with color map.

### H-2: Mobile Header Currently Uses `bg-fb-blue`
**Where:** `main-header.js:47, 58`

Mobile is hardcoded `bg-fb-blue`, not glass. Visual change: blue → white (more dramatic than desktop glass → white).

WCAG contrast: both valid. But visual change on mobile more significant than spec implied.

**Resolution:** Addressed in spec.

### H-3: MUI AppBar Needs Explicit Color Override
**Where:** `main-header.js:79-87`

MUI AppBar without `color="inherit"` or `sx={{ bgcolor: 'transparent' }}` defaults to primary.

**Resolution:** `globals.css` already has `.MuiAppBar-root { background-color: transparent !important }` — covers it. Optional explicit `sx` is safer.

## Medium Priority Issues

### M-1: Hero Bleed Removal Creates 56px Gap on Mobile
**Where:** `SearchCover.js:144`, `pages/homepagev2.js:388`

Current: `-mt-[56px]` pulls hero behind header. After removal: 56px white gap.

**Options:**
- (A) Remove bleed + increase hero `min-h` 500px → 556px (preferred)
- (B) Keep `-mt-[56px]` with solid white header — intentional overlap
- (C) Add `pt-[56px]` inside FeaturedImageHeader on mobile

**Recommendation:** Option A. Clean, predictable.

### M-2: StickySearchBar Z-Index Visual Layering
**Where:** `StickySearchBar.js:78-84` (z-40), `main-header.js` (z-1100)

On `/trips/` pages, header (z-1100) floats above StickySearchBar (z-40). White-on-white: top portion clipped by header.

**Fix:** Adjust `StickySearchBar` top to compensate for header height:
```jsx
style={{ top: isMobile ? 56 : 80 }}
```

**Resolution:** Addressed in spec via `HeaderRowsContext`.

### M-3: HeaderSearchSummary Truncation on 1024px Desktop
**Where:** `HeaderSearchSummary.js:123-159`

Single-row: Logo (~160px) + Nav (hidden) + Summary (flex-1) + Utilities (~120px). Available width ~744px at 1024px.

Risk: long route text ("Hat Yai → Ko Lipe") truncates. Already handled: `truncate` class on route span. Acceptable.

### M-4: navConfig.js Has 5 Items — KEEP ALL
**Where:** `constants/navConfig.js`

**DECISION:** Keep all 5 nav items. Explore Thailand stays. Type B discovery pages need all 5.
- `constants/navConfig.js` — NO CHANGES
- Backend NavigationSection — NO CHANGES

## Low Priority Findings

### L-1: No Custom Font Loaded
Spec calls for Inter/General Sans/Satoshi. Current: system-ui.

**Recommendation:** Separate PR with CLS impact testing.

### L-2: Border/Shadow Tokens Not in designSystem.js
No border/shadow semantic tokens. Spec hardcodes `rgba(0,0,0,0.06)`.

**Recommendation:** Acceptable now. Add to `BORDERS` / `SHADOWS` in follow-up.

### L-3: `useScrollTrigger` Import Unused After Refactor
Once glass removed, `useScrollTrigger` stays for Slide. If Slide eventually removed, clean up import.

## Complete File Change Inventory

**Spec v1 said 5. Actual: 12.**

| # | File | Changes Required | Spec Included? |
|---|------|-----------------|----------------|
| 1 | `styles/globals.css` | Add `.solid-header` + `.solid-header-elevated` | ✓ |
| 2 | `components/layout/main-header.js` | Single-row 80px, `solid-header`, dark text, MUI `color="inherit"`, remove glass | ✓ |
| 3 | `components/search/StickySearchBar.js` | White surface, dark text, dynamic top, remove dark glass | ✓ |
| 4 | `components/layout/layout.js` | `md:pt-[80px]` | ✓ |
| 5 | `pages/homepagev2.js` | Remove `-mt-[56px]`, adjust hero min-height | ✓ |
| 6 | `components/search/HeaderSearchSummary.js` | All `text-white` → dark | ✓ |
| 7 | `components/search/SearchDialogTrigger.js` | Button bg + text | ✓ (was missing) |
| 8 | `components/cart/CartButton.js` | Icon `text-white/70` → `text-gray-700` | ✓ (was missing) |
| 9 | `components/auth/ProfileButton.js` | Icon `text-white/70` → `text-gray-700` | ✓ (was missing) |
| 10 | `components/layout/NavDropdown.js` | Active `brand-primary` → `gray-900`, focus ring | ✓ (was missing) |
| 11 | `constants/navConfig.js` | **NO CHANGE** — keep all 5 items | ✓ |
| 12 | `pages/_document.js` | Custom font loading (separate PR) | ✓ |

## Regression Test Matrix

| Page | Breakpoint | Test Points |
|------|-----------|-------------|
| Homepage `/` | 1440, 768, 375 | White header, dark logo/nav, hero gap, search form visible |
| Trip Results `/trips/[from]/[to]` | 1440, 768, 375 | Sticky bar white + dark, HeaderSearchSummary readable, nav hidden |
| Checkout `/checkout` | 1440 | No nav, white header, cart/profile visible |
| Login `/login` | 1440, 375 | No nav, white header |
| Blog `/blog` | 1440, 768 | **Type B — Row 2 nav visible** |
| Destinations `/destinations` | 1440 | Nav visible, all 5 items incl Explore Thailand |
| Keyboard tab | All | Focus rings visible (not white-on-white) |
| Scroll (mobile) | 375 | Header hides on scroll down (Slide preserved) |

## Implementation Order

```
Day 1 — Color unblocks (no structure)
  1. CartButton.js
  2. ProfileButton.js
  3. SearchDialogTrigger.js
  4. NavDropdown.js
  (constants/navConfig.js — NO CHANGES)

Day 2 — CSS + core header
  5. globals.css — verify glass usages, remove, add solid-header
  6. main-header.js — glass→solid, white→dark, mobile bg-fb-blue→white
  7. HeaderSearchSummary.js — all text-white → dark

Day 3 — Layout structure + sticky
  8. layout.js — remove /blog from ONE_ROW_PATHS, dynamic padding (80/96px), export HeaderRowsContext
  9. StickySearchBar.js — consume HeaderRowsContext, dynamic top, white surface

Day 4 — QA regression
  10. Regression matrix
  11. Keyboard/focus audit
  12. grep verify: zero text-white remaining

Day 5+ (separate PRs)
  - Homepage hero height 500px → 320–360px
  - Custom font loading Inter/Satoshi (CLS testing)
  - designSystem.js SHADOWS + BORDERS tokens
```

## Related
[[header-redesign-2026-spec]] · [[smartenplus-glassmorphism-header]] · [[nav-header-redesign]]
