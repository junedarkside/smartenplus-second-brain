# Header Redesign 2026 — Team Review Report

**Date:** 2026-05-28 (updated 2026-05-28 with final decisions)
**Specialists:** Design · UX · Frontend + Second audit: UX Architecture · Visual Design · Frontend Engineering
**Subject:** Deep audit of `header-redesign-2026-spec.md` before implementation

> **See [[header-redesign-2026-spec]] for FINAL spec with all decisions locked.**
> This doc preserves the audit trail and open questions that were resolved.

---

## Final Verdict (Updated)

**Spec v1 had one critical architectural flaw: "single-row everywhere" was wrong.**
Second audit caught it. Final design uses Type A/B adaptive split — see spec.
All blockers below now have locked decisions.

**Spec v1 identified 5 files. Actual count: 12 files.** Four critical components with hardcoded white colors were missed. All decisions now resolved.

---

## Decisions Locked

| Decision | Resolution |
|----------|------------|
| B-1: rows prop / Type A vs Type B | **Type A/B split.** ONE_ROW_PATHS = transactional only. /blog removed from list → Type B. |
| B-2: Mobile hide-on-scroll | **Keep Slide behavior.** 56px viewport gain. |
| B-3 (new): 2-row nav on browse pages | **Type B keeps Row 2** on /, /destinations, /locations, /trips, /activities, /blog. All 5 nav items including Explore Thailand stay. |
| M-4: Remove Explore Thailand | **REJECTED.** All 5 nav items stay. |
| Layout offset | **Dynamic:** 80px (Type A) / 96px (Type B). |
| StickySearchBar top | **Dynamic via HeaderRowsContext:** 80px or 96px. |
| MUI AppBar sx | **Optional** — globals.css:736-740 already handles it. |

---

## Verdict (Original — Preserved)

**Spec is directionally correct. NOT implementation-ready as written.**

Spec identifies 5 files. Actual count: **10 files**. Four critical components with hardcoded white colors were missed. Two open UX decisions block full implementation. Two MUI conflicts require explicit overrides.

---

## Critical Blockers (Fix Before Coding)

### B-1: `rows` Prop Behavior Undefined in New Design
**Where:** `layout.js:143`, `main-header.js:112`

Current `rows={1}` hides nav on `/checkout`, `/payment`, `/login`, `/register`, `/search`, `/blog`. Spec says "single-row everywhere" but doesn't address this.

**Decision needed:** Does nav disappear on ONE_ROW_PATHS in the new single-row design?
- Answer YES → keep `rows` prop logic as-is (just hides center nav, not whole row)
- Answer NO → remove ONE_ROW_PATHS, nav appears on all pages

**Recommendation:** Keep. Shows nav on most pages, hides on transactional pages. Zero refactor cost.

---

### B-2: Mobile Header Hide-on-Scroll
**Where:** `main-header.js:24-26, 56`

`useScrollTrigger` drives TWO behaviors: (1) glass class toggle — removing ✓; (2) `<Slide>` hide header on scroll down — spec doesn't mention.

**Decision needed:** Should mobile header hide when user scrolls down?
- Current behavior: yes, hides via Slide
- Spec is silent

**Recommendation:** Keep Slide behavior. Removing it costs 56px viewport height on mobile. Spec only removes glass, not this.

---

## High Priority Issues

### H-1: 5 Files Missing From Spec (Total: 10)

| # | File | Issue |
|---|------|-------|
| 1 | `components/search/SearchDialogTrigger.js` | Line 34: `border-white bg-white bg-opacity-20 text-white` (mobile); Line 46: `bg-gray-800 bg-opacity-80 text-white` (desktop) — invisible on white |
| 2 | `components/cart/CartButton.js` | Line 116: `text-white/70 hover:text-white` — icon invisible on white header |
| 3 | `components/auth/ProfileButton.js` | Line 367: `text-white/70 hover:text-white` — icon invisible on white header |
| 4 | `components/layout/NavDropdown.js` | Line 50: active = `text-brand-primary border-brand-primary` (blue) — spec requires `text-gray-900 border-gray-900` |
| 5 | `components/search/HeaderSearchSummary.js` | Multiple `text-white / text-white/80 / text-white/40` — all invisible on white |

**All 5 are BLOCKING** — user would see invisible icons, invisible search summary, wrong-colored active nav.

---

### H-2: Mobile Header Currently Uses `bg-fb-blue`, Not Glass
**Where:** `main-header.js:47, 58`

Spec says white header replaces glassmorphism. But mobile is actually hardcoded `bg-fb-blue` (Facebook blue), not glass. This changes the visual delta: mobile goes from **blue → white** (more dramatic than desktop glass → white).

WCAG contrast win: white bg + gray text passes AA. Blue bg + white text also passes. Both are valid. But the visual change on mobile is more significant than spec implies.

---

### H-3: MUI AppBar Needs Explicit Color Override
**Where:** `main-header.js:79-87` (desktop AppBar)

MUI AppBar without `color="inherit"` or `sx={{ bgcolor: 'transparent' }}` defaults to primary theme color. `.solid-header` CSS sets `background: #FFFFFF` on the child div, not AppBar itself. MUI injects background-color on the root element which may override CSS class.

**Fix:**
```jsx
<AppBar
  position="fixed"
  sx={{ top: 0, zIndex: 1100, bgcolor: 'transparent', color: 'inherit' }}
  elevation={0}
>
```

Note: `globals.css` already has `.MuiAppBar-root { background-color: transparent !important }` (line 736-740) — this may cover it. But explicit `sx` is safer and more reliable.

---

## Medium Priority Issues

### M-1: Hero Bleed Removal Creates 56px Gap on Mobile
**Where:** `SearchCover.js:144`, `pages/homepagev2.js:388`

Current: `-mt-[56px]` pulls hero behind fixed header (glass = seamless).
After removal: 56px white gap between solid white header and hero image.

**Options:**
- (A) Remove bleed + increase hero `min-h` from `500px` to `556px` (preferred — clean solution)
- (B) Keep `-mt-[56px]` with solid white header — hero starts behind white bar, intentional overlap (needs visual test)
- (C) Add `pt-[56px]` inside FeaturedImageHeader on mobile

**Recommendation:** Option A. Clean, predictable.

---

### M-2: StickySearchBar Z-Index Visual Layering
**Where:** `StickySearchBar.js:78-84` (z-40), `main-header.js` (z-1100)

On `/trips/` pages, both header (z-1100) and StickySearchBar (z-40) sit at `fixed top-0`. Header wins z-stack. When sticky bar shows, white header floats above it.

Current dark glass bar: visual discontinuity is acceptable (different textures).
New white-on-white: when sticky bar transitions in at z-40 below white header, top portion is clipped by header.

**Actual layout behavior**: StickySearchBar appears below the header (covered by 80px), not replacing it. Users see sticky bar starting at 80px from top. Route text gets covered.

**Fix needed:** Adjust `StickySearchBar` top to compensate for header height:
```jsx
style={{ top: isMobile ? 56 : 80 }}  // Or use CSS: top-14 / top-20
```

Or use `top-[80px]` on desktop, `top-[56px]` on mobile.

---

### M-3: HeaderSearchSummary Truncation on 1024px Desktop
**Where:** `HeaderSearchSummary.js:123-159` (horizontal mode)

Single-row: Logo (~160px) + Nav (hidden when searchBarContent) + Summary (flex-1) + Utilities (~120px).
When summary is active, nav hides. Available width for summary at 1024px breakpoint: ~744px.

Summary content: `Route → Date · TripMode · Passengers · Edit` — ~480px minimum.

**Risk:** If route text is long ("Hat Yai → Ko Lipe"), truncation kicks in. Station names are long by design.

**Already handled:** `truncate` class on route span + `min-w-0` on flex container. Tablets will see truncated route — acceptable.

**No code change needed** — but should be visually verified at 768px.

---

### M-4: navConfig.js Has 5 Items, Spec v1 Said 4 ~~RESOLVED — KEEP ALL 5~~
**Where:** `constants/navConfig.js`

~~Spec drops "Explore Thailand". navConfig still has it.~~

**DECISION (2026-05-28):** Keep all 5 nav items. Explore Thailand stays. Do not remove. User requirement explicit — Type B discovery pages need all 5.
- `constants/navConfig.js` — NO CHANGES
- Backend NavigationSection — NO CHANGES

---

## Low Priority Findings

### L-1: No Custom Font Loaded
Spec calls for Inter/General Sans/Satoshi. Current font: system-ui stack. No Google Fonts import in `_document.js` or Tailwind config.

**Recommendation:** Out of scope for this implementation phase. Font swap is a separate PR with CLS impact testing required.

---

### L-2: Border/Shadow Tokens Not in designSystem.js
`designSystem.js` has color tokens but no border/shadow semantic tokens. Spec hardcodes `rgba(0,0,0,0.06)` etc. as CSS values.

**Recommendation:** Acceptable for now. Add to `BORDERS` / `SHADOWS` exports in a follow-up cleanup.

---

### L-3: `useScrollTrigger` Import Unused After Refactor
Once glass classes are removed (mobile trigger only drove glass toggle, Slide uses it too — see B-2), `useScrollTrigger` stays. But if Slide is eventually removed, clean up import.

---

## Complete File Change Inventory

**Spec said 5. Actual: 10.**

| # | File | Changes Required | Spec Included? |
|---|------|-----------------|----------------|
| 1 | `styles/globals.css` | Add `.solid-header` + `.solid-header-elevated` | ✓ |
| 2 | `components/layout/main-header.js` | Single-row 80px, `solid-header` class, dark text, MUI `color="inherit"`, remove glass classes | ✓ |
| 3 | `components/search/StickySearchBar.js` | White surface, dark text, `top-[80px]` desktop / `top-[56px]` mobile, remove dark glass | ✓ |
| 4 | `components/layout/layout.js` | `md:pt-[80px]` | ✓ |
| 5 | `pages/homepagev2.js` | Remove `-mt-[56px]`, adjust hero min-height | ✓ |
| 6 | `components/search/HeaderSearchSummary.js` | All `text-white` → dark, Dot color | ✓ (mentioned at bottom) |
| 7 | `components/search/SearchDialogTrigger.js` | Button bg + text for white header | ✗ **MISSING** |
| 8 | `components/cart/CartButton.js` | Icon `text-white/70` → `text-gray-700` | ✗ **MISSING** |
| 9 | `components/auth/ProfileButton.js` | Icon `text-white/70` → `text-gray-700` | ✗ **MISSING** |
| 10 | `components/layout/NavDropdown.js` | Active state `brand-primary` → `gray-900`, focus ring | ✗ **MISSING** |
| 11 | `constants/navConfig.js` | Remove "Explore Thailand" entry | ✗ **MISSING** |

---

## Recommended Color Changes (Complete Map)

| Component | Property | Before | After |
|-----------|----------|--------|-------|
| `main-header` mobile bg | background | `bg-fb-blue` | `solid-header` (white) |
| `main-header` desktop bg | background | `glass-bg-scrolled` | `solid-header` (white) |
| `main-header` mobile icon (MenuIcon) | text | `text-white` | `text-gray-700` |
| `main-header` wordmark | text | `text-white` | `text-gray-900` |
| `main-header` nav inactive | text | `text-white/70 border-transparent` | `text-gray-500 border-transparent` |
| `main-header` nav active | text/border | `text-white border-white` | `text-gray-900 border-gray-900` |
| `main-header` nav focus ring | ring | `ring-white/50` | `ring-gray-400` |
| `CartButton` icon | text | `text-white/70 hover:text-white` | `text-gray-700 hover:text-gray-900` |
| `ProfileButton` icon | text | `text-white/70 hover:text-white` | `text-gray-700 hover:text-gray-900` |
| `NavDropdown` active | text/border | `text-brand-primary border-brand-primary` | `text-gray-900 border-gray-900` |
| `NavDropdown` focus | ring | `ring-brand-primary` | `ring-gray-400` |
| `HeaderSearchSummary` route | text | `text-white` | `text-gray-900` |
| `HeaderSearchSummary` meta | text | `text-white/80` | `text-gray-500` |
| `HeaderSearchSummary` dots | text | `text-white/40` | `text-gray-400` |
| `SearchDialogTrigger` mobile | bg/border/text | `bg-white/20 border-white/40 text-white` | `bg-gray-100 border-gray-300 text-gray-900` |
| `SearchDialogTrigger` desktop | bg/border/text | `bg-gray-800/80 text-white` | `bg-gray-100 border-gray-300 text-gray-900` |
| `StickySearchBar` bg | background | `bg-gray-900 bg-opacity-90 backdrop-blur-sm` | `bg-white` + `solid-header-elevated` CSS |
| `StickySearchBar` route text | text | `text-white` | `text-gray-900` |
| `StickySearchBar` badge | bg/border/text | `bg-white/20 border-white/40 text-white` | `bg-gray-100 border-gray-300 text-gray-600` |
| `StickySearchBar` passenger btn | bg/border/text | `bg-gray-800/60 border-gray-600 text-white` | `bg-white border-gray-300 text-gray-700` |

---

## Regression Test Matrix

| Page | Breakpoint | Test Points |
|------|-----------|-------------|
| Homepage `/` | 1440px, 768px, 375px | White header, dark logo/nav, hero gap, search form visible |
| Trip Results `/trips/[from]/[to]` | 1440px, 768px, 375px | Sticky bar white + dark text, HeaderSearchSummary readable, nav hidden |
| Checkout `/checkout` | 1440px | No nav, white header, cart/profile visible |
| Login `/login` | 1440px, 375px | No nav, white header |
| Blog `/blog` | 1440px, 768px | **Type B — Row 2 nav visible** (removed from ONE_ROW_PATHS) |
| Destinations `/destinations` | 1440px | Nav visible, no "Explore Thailand" item |
| Keyboard tab | All | Focus rings visible (not invisible white-on-white) |
| Scroll (mobile) | 375px | Header hides on scroll down (Slide behavior preserved) |

---

## Implementation Order

```
Day 1 — Color unblocks (no structure change)
  1. CartButton.js — icon color
  2. ProfileButton.js — icon color
  3. SearchDialogTrigger.js — button colors
  4. NavDropdown.js — active state + focus ring
  (constants/navConfig.js — NO CHANGES, keep all 5 items)

Day 2 — CSS + core header
  5. globals.css — verify glass usages, remove glass classes, add solid-header
  6. main-header.js — glass→solid, white→dark, mobile bg-fb-blue→white
  7. HeaderSearchSummary.js — all text-white → dark

Day 3 — Layout structure + sticky
  8. layout.js — remove /blog from ONE_ROW_PATHS, dynamic padding (80/96px), export HeaderRowsContext
  9. StickySearchBar.js — consume HeaderRowsContext, dynamic top, white surface

Day 4 — QA regression
  10. Regression matrix (updated matrix above — includes /blog as Type B)
  11. Keyboard/focus audit
  12. grep verify: zero text-white remaining in header/search/cart/auth components

Day 5+ (separate PRs)
  - Homepage hero height 500px → 320–360px
  - Custom font loading Inter/Satoshi (CLS testing required)
  - designSystem.js SHADOWS + BORDERS tokens
```

---

## Related
[[header-redesign-2026-spec]] · [[smartenplus-glassmorphism-header]] · [[nav-header-redesign-2026-05-24]]
