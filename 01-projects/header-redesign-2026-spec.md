# Header Redesign 2026 — Final Design Spec

**Status:** FINAL — supersedes single-row spec. All decisions locked 2026-05-28.

## Summary
Replace dark glassmorphism header with adaptive solid white navigation system. Two header types: Type A (operational, single-row) for transactional pages; Type B (discovery, two-row) for browse/content pages. "Modern operating system for traveling across Thailand."

## Context
Current header (as of 2026-05-27 revert): dark glass overlay (`glass-bg-scrolled`, `glass-header`), white text, 2-row desktop. Designed for cinematic hero photography. 2026 direction: operational clarity — Google Flights / Linear / Notion UX, not tourism aesthetics.

Platform is a hybrid product — transportation utility + route discovery + travel exploration. Header must adapt to user intent. Single layout across all pages was wrong.

## Decision
Solid `#FFFFFF` adaptive header. Type A/B split. No glassmorphism. No blur. No transparency.

Reference: [[smartenplus-glassmorphism-header]] (deprecated), [[mobile-header-redesign-glassmorphism]] (superseded)

---

## TYPE A — Operational Header

**Used on:** `/search` `/checkout` `/payment` `/booking` `/login` `/register`

**Purpose:** Maximize focus. No navigation distraction during task completion.

```
┌──────────────────────────────────────────┐
│ Logo | Compact Search Summary | Utilities│
└──────────────────────────────────────────┘
```

- Left: SmartEnPlus logo
- Center: Compact search summary (Bangkok → Chiang Mai)
- Right: Currency · Cart · Account
- Height: 80px desktop / 56–64px mobile
- No secondary browse nav row

---

## TYPE B — Discovery / Browse Header

**Used on:** `/` `/destinations` `/locations` `/trips` `/activities` `/blog`

**Purpose:** Support browsing, category exploration, editorial navigation.

### Row 1 (operational layer) — 52px
```
┌──────────────────────────────────────────┐
│ Logo | Compact Search Summary | Utilities│
└──────────────────────────────────────────┘
```

### Row 2 (discovery nav) — 40–48px
```
┌──────────────────────────────────────────┐
│ Explore Thailand | Routes | Journeys |   │
│ Experiences | Guides                     │
└──────────────────────────────────────────┘
```

- **All 5 nav items kept.** DO NOT remove Explore Thailand.
- Total header height: ~96px
- Row 2: `variant="dense"` MUI Toolbar, calm typography, subtle hover underline

**CRITICAL:** `/blog` is discovery/editorial. Must use Type B. "Guides" links to `/blog` — nav continuity requires Row 2 visible. Remove `/blog` from ONE_ROW_PATHS.

---

## Global Header Style

```css
.solid-header {
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}
.solid-header-elevated {
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}
```

No: backdrop-blur · transparency · dark overlay · floating glass

---

## Color System

| Element | Value |
|---------|-------|
| Header background | `#FFFFFF` |
| Alt page bg | `#FAFAF8` / `#F7F7F5` |
| Primary text | `#1F2937` = `text-gray-800` |
| Nav inactive | `text-gray-500` |
| Nav active | `text-gray-900 border-b-2 border-gray-900` |
| Nav focus ring | `ring-gray-400` |
| Icons | `text-gray-700 hover:text-gray-900` |
| Border | `rgba(0,0,0,0.06)` |
| Shadow | `rgba(0,0,0,0.03)` |

---

## Complete Color Change Map

| Component | Property | Before | After |
|-----------|----------|--------|-------|
| `main-header` mobile bg | background | `bg-fb-blue` | `solid-header` (white) |
| `main-header` desktop bg | background | `glass-bg-scrolled` | `solid-header` (white) |
| `main-header` mobile MenuIcon | text | `text-white` | `text-gray-700` |
| `main-header` wordmark | text | `text-white` | `text-gray-900` |
| `main-header` nav inactive | text | `text-white/70 border-transparent` | `text-gray-500 border-transparent` |
| `main-header` nav active | text/border | `text-white border-white` | `text-gray-900 border-gray-900` |
| `main-header` nav focus ring | ring | `ring-white/50` | `ring-gray-400` |
| `CartButton` icon | text | `text-white/70 hover:text-white` | `text-gray-700 hover:text-gray-900` |
| `ProfileButton` icon | text | `text-white/70 hover:text-white` | `text-gray-700 hover:text-gray-900` |
| `NavDropdown` active | text/border | `text-brand-primary border-brand-primary` | `text-gray-900 border-gray-900` |
| `NavDropdown` focus ring | ring | `ring-brand-primary` | `ring-gray-400` |
| `HeaderSearchSummary` route | text | `text-white` | `text-gray-900` |
| `HeaderSearchSummary` meta | text | `text-white/80` | `text-gray-500` |
| `HeaderSearchSummary` dots | text | `text-white/40` | `text-gray-400` |
| `SearchDialogTrigger` mobile | bg/border/text | `bg-white/20 border-white/40 text-white` | `bg-gray-100 border-gray-300 text-gray-900` |
| `SearchDialogTrigger` desktop | bg/border/text | `bg-gray-800/80 text-white` | `bg-gray-100 border-gray-300 text-gray-900` |
| `StickySearchBar` bg | background | `bg-gray-900 bg-opacity-90 backdrop-blur-sm` | `solid-header-elevated` class |
| `StickySearchBar` route text | text | `text-white` | `text-gray-900` |
| `StickySearchBar` badge | bg/border/text | `bg-white/20 border-white/40 text-white` | `bg-gray-100 border-gray-300 text-gray-600` |
| `StickySearchBar` passenger btn | bg/border/text | `bg-gray-800/60 border-gray-600 text-white` | `bg-white border-gray-300 text-gray-700` |

---

## Mobile Header

- Height: 56–64px
- Background: solid white (`solid-header`)
- Layout: `[Hamburger] [Logo] | [Currency · Cart · Account]`
- Icons: `text-gray-700`
- Hide-on-scroll: keep `<Slide>` behavior (56px viewport gain)
- No: dark overlay · glass blur · `bg-fb-blue`

---

## Layout Offset System

Header height is NOT uniform. Padding must be dynamic.

```javascript
// layout.js
const ONE_ROW_PATHS = ['/checkout', '/payment', '/login', '/register', '/search'];
// /blog REMOVED — now Type B (2-row, 96px)

const headerRows = ONE_ROW_PATHS.some(
  p => router.pathname === p || router.pathname.startsWith(p + '/')
) ? 1 : 2;

const layoutPaddingTop = headerRows === 1 ? 'md:pt-[80px]' : 'md:pt-[96px]';

// main element:
<main className={`mx-auto w-full flex-grow no-scrollbar ${layoutPaddingTop}`}>
```

---

## StickySearchBar Dynamic Offset

Must sit below fixed header — needs `HeaderRowsContext`:

```javascript
// layout.js — add:
export const HeaderRowsContext = React.createContext(2);

// StickySearchBar.js — consume:
const headerRows = useContext(HeaderRowsContext);
// className: headerRows === 1 ? 'top-[80px]' : 'top-[96px]'
```

---

## Progressive Search Compression UX

Expanded search on page load → compresses to sticky summary on scroll:
```
┌────────────────────────────────────┐
│ Bangkok → Chiang Mai      Edit ✎  │
└────────────────────────────────────┘
```
Click → desktop: centered modal dialog / mobile: full-screen search editor.

---

## Files to Change (12 Total)

| # | File | Change | Priority |
|---|------|--------|----------|
| 1 | `styles/globals.css` | Remove glass classes; add `.solid-header` + `.solid-header-elevated` | P0 |
| 2 | `components/layout/layout.js` | Remove `/blog` from ONE_ROW_PATHS; dynamic padding; export `HeaderRowsContext` | P0 |
| 3 | `components/layout/main-header.js` | `glass-bg-scrolled` → `solid-header`; all white text → dark; mobile `bg-fb-blue` → white | P0 |
| 4 | `components/search/HeaderSearchSummary.js` | All `text-white*` → dark | P0 |
| 5 | `components/search/SearchDialogTrigger.js` | Mobile + desktop button colors | P0 |
| 6 | `components/search/StickySearchBar.js` | Dark → white surface; dynamic top via `HeaderRowsContext` | P0 |
| 7 | `components/cart/CartButton.js` | `text-white/70` → `text-gray-700` | P0 |
| 8 | `components/auth/ProfileButton.js` | `text-white/70` → `text-gray-700` | P0 |
| 9 | `components/layout/NavDropdown.js` | Active: `brand-primary` → `gray-900`; focus ring → `ring-gray-400` | P1 |
| 10 | `constants/navConfig.js` | **NO CHANGE** — keep all 5 items including Explore Thailand | — |
| 11 | `pages/homepagev2.js` | Hero 500px → 320–360px (separate PR) | P2 |
| 12 | `pages/_document.js` | Custom font loading Inter/Satoshi (separate PR) | P2 |

**Post-change verify:**
```bash
grep -rn "text-white" components/layout/ components/search/ components/cart/ components/auth/ --include="*.js"
# Expected: zero results
```

---

## Implementation Order

```
Day 1 — Color unblocks (no structure change)
  1. CartButton.js — icon color
  2. ProfileButton.js — icon color
  3. SearchDialogTrigger.js — button colors
  4. NavDropdown.js — active state + focus ring
  (constants/navConfig.js — NO CHANGES)

Day 2 — CSS + core header
  5. globals.css — verify glass usages, remove glass classes, add solid-header
  6. main-header.js — glass→solid, white→dark, mobile bg-fb-blue→white
  7. HeaderSearchSummary.js — all text-white → dark

Day 3 — Layout structure + sticky
  8. layout.js — remove /blog from ONE_ROW_PATHS, dynamic padding, HeaderRowsContext
  9. StickySearchBar.js — consume HeaderRowsContext, dynamic top, white surface

Day 4 — QA regression
  10. All regression tests (matrix below)
  11. grep verify zero text-white remaining

Day 5+ (separate PRs)
  - Homepage hero height 500px → 320–360px
  - Custom font loading Inter/Satoshi (CLS testing required)
  - designSystem.js SHADOWS + BORDERS tokens
```

---

## Regression Test Matrix

| Page | Breakpoint | Header Type | Test Points |
|------|-----------|-------------|-------------|
| `/` | 1440, 768, 375 | Type B | White header, dark logo/nav, Row 2 visible |
| `/destinations` | 1440, 768 | Type B | Row 2 visible, all 5 items incl Explore Thailand |
| `/locations` | 1440, 768 | Type B | Row 2 nav visible |
| `/trips/*` | 1440, 768, 375 | Type B | Row 2 visible; StickySearchBar white+dark; HeaderSearchSummary readable |
| `/activities` | 1440 | Type B | Row 2 nav visible |
| `/blog` | 1440, 768 | **Type B** | Row 2 visible (removed from ONE_ROW_PATHS) |
| `/checkout` | 1440 | Type A | No nav row, white header, cart/profile visible, 80px offset |
| `/login` | 1440, 375 | Type A | No nav row, white header |
| `/search` | 1440 | Type A | No nav row, search summary in header |
| Keyboard tab | All | Both | Focus rings visible (not white-on-white) |
| Mobile scroll | 375 | Both | Header hides on scroll (Slide preserved) |
| StickySearchBar | 1440 + 375 | Both | Top = 80px (Type A) or 96px (Type B), not hidden behind header |

---

## Key Decisions Locked

| Decision | Answer |
|----------|--------|
| Single-row everywhere | No — Type A/B split |
| Keep Explore Thailand | Yes — all 5 nav items stay |
| `/blog` header type | Type B — discovery, 2-row, nav visible |
| Mobile hide-on-scroll | Keep Slide behavior |
| Layout offset | Dynamic — 80px Type A / 96px Type B |
| MUI AppBar sx | Optional — globals.css:736-740 already covers |
| Font swap | Separate PR — CLS risk |
| Hero height | Separate PR — layout risk |

---

## Tradeoffs
- Loses dramatic hero overlap (intentional — not a tourism site)
- Gains: WCAG contrast, operational clarity, discovery nav continuity, dynamic layout system
- Glass classes: run `grep -rn "glass-bg\|glass-header\|hero-top-gradient"` before deleting — other usages may exist

## Related
[[header-redesign-2026-team-review]] · [[smartenplus-glassmorphism-header]] · [[nav-header-redesign-2026-05-24]] · [[mobile-header-redesign-glassmorphism]]
