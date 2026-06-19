# Header Redesign 2026 — Implementation Handoff

**Status:** Days 1–3 COMPLETE. Day 4 QA pending.
**Branch:** `260528-feat/header-redesign-2026`
**Commit:** `a4158b0`
**Date:** 2026-05-28

---

## Summary

Replaced glassmorphism dark header with adaptive solid white header system. 10 files changed, 1 commit. No structural regressions — pure color/surface swap + layout context.

---

## What Changed

### CSS (`styles/globals.css`)
- Removed: `.glass-header`, `.glass-header-scrolled`, `.glass-bg`, `.glass-bg-scrolled`
- Kept: `.hero-top-gradient` (still used by `FeaturedImageHeader.js`)
- Added: `.solid-header` (white + subtle border + shadow) + `.solid-header-elevated` (white + stronger shadow for StickySearchBar)

### Mobile Header (`main-header.js`)
- `bg-fb-blue` → `solid-header` (both search-active + normal branches)
- `MenuIcon`: `text-white` → `text-gray-700`
- Wordmark: `text-white` → `text-gray-900`

### Desktop Header (`main-header.js`)
- `glass-bg-scrolled` → `solid-header`
- Wordmark: `text-white` → `text-gray-900`
- Nav inactive: `text-white/70 hover:text-white` → `text-gray-500 hover:text-gray-900`
- Nav active: `text-white border-white` → `text-gray-900 border-gray-900`
- Nav focus ring: `ring-white/50` → `ring-gray-400`

### Utility Icons
- `CartButton.js`: `text-white/70 hover:text-white` → `text-gray-700 hover:text-gray-900`
- `ProfileButton.js`: same

### Search Trigger (`SearchDialogTrigger.js`)
- Mobile: `bg-white/20 border-white/40 text-white` → `bg-gray-100 border-gray-300 text-gray-900`
- Desktop: `bg-gray-800/80 text-white` → `bg-gray-100 border-gray-300 text-gray-900`

### NavDropdown (`NavDropdown.js`)
- Active: `text-brand-primary border-brand-primary` → `text-gray-900 border-gray-900`
- Focus ring: `ring-brand-primary` → `ring-gray-400`

### Header Search Summary (`HeaderSearchSummary.js`)
- Route text: `text-white` → `text-gray-900`
- Meta text: `text-white/80` → `text-gray-500`
- Dots: `text-white/40` → `text-gray-400`
- Passenger/edit buttons: `text-white/80 hover:text-white` → `text-gray-500 hover:text-gray-900`

### Layout System (`layout.js`)
- Exported `HeaderRowsContext = createContext(2)`
- Removed `/blog` from `ONE_ROW_PATHS` → blog now Type B (2-row, 96px)
- Dynamic padding: `md:pt-[80px]` (Type A) / `md:pt-[96px]` (Type B)
- Wrapped children in `<HeaderRowsContext.Provider value={headerRows}>`

### Sticky Search Bar (`StickySearchBar.js`)
- Consumes `HeaderRowsContext` → `top-[80px]` (Type A) or `top-[96px]` (Type B)
- Surface: `bg-gray-900 bg-opacity-90 backdrop-blur-sm` → `solid-header-elevated`
- Border: `border-gray-700` → `border-gray-200`
- Route text: `text-white` → `text-gray-900`
- Badge: `bg-white/20 border-white/40 text-white` → `bg-gray-100 border-gray-300 text-gray-600`
- Passenger btn: `bg-gray-800/60 border-gray-600 text-white` → `bg-white border-gray-300 text-gray-700`

---

## Architecture Notes

### HeaderRowsContext
- Defined in `layout.js`, exported as named export
- Provides `1` (Type A) or `2` (Type B) to children
- `StickySearchBar` consumes via `useContext(HeaderRowsContext)`
- Pattern reusable for any future component needing header-height awareness

### Type A vs Type B
| Type | Pages | Header height | Padding |
|------|-------|--------------|---------|
| A | `/checkout` `/payment` `/login` `/register` `/search` | 80px | `md:pt-[80px]` |
| B | all others incl. `/blog` | 96px | `md:pt-[96px]` |

### What Was NOT Changed
- `constants/navConfig.js` — all 5 nav items kept, Explore Thailand stays
- `FeaturedImageHeader.js` — `hero-top-gradient` intentionally preserved
- `footer.js` — dark footer `bg-fb-blue` + `text-white` intentional
- `SearchCover.js` — hero search on dark bg, white text intentional
- `Passenger.js`, `ProductSearchForm*.js` — `bg-fb-blue` search buttons intentional

---

## Day 4 QA Checklist (Pending)

Run regression matrix from spec before merging to main:

| Page | Breakpoint | Check |
|------|-----------|-------|
| `/` | 1440, 768, 375 | White header, dark logo, Row 2 visible |
| `/destinations` | 1440, 768 | Row 2 visible, all 5 items |
| `/blog` | 1440, 768 | Row 2 visible (removed from ONE_ROW_PATHS) |
| `/trips/[from]/[to]` | 1440, 375 | StickySearchBar white+dark, correct top offset |
| `/checkout` | 1440 | No Row 2, white header, 80px offset |
| `/login` | 1440, 375 | No Row 2, white header |
| Keyboard tab | all | Focus rings visible (not white-on-white) |
| Mobile scroll | 375 | Header hides on scroll (Slide preserved) |

**Final verify command:**
```bash
grep -rn "text-white" components/layout/ components/search/ components/cart/ components/auth/ --include="*.js"
# Expected: zero results
```

---

## Remaining Work (Separate PRs)

| Item | File | Notes |
|------|------|-------|
| Homepage hero height 500px → 320–360px | `pages/homepagev2.js` | Layout risk — separate PR |
| Custom font Inter/Satoshi | `pages/_document.js` | CLS testing required — separate PR |
| `designSystem.js` SHADOWS + BORDERS tokens | `helpers/designSystem.js` | Design debt |

---

## Related
[[header-redesign-2026-spec]] · [[header-redesign-2026-team-review]]
