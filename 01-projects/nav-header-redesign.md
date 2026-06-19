# Nav/Header Redesign

## Summary
SmartEnPlus navigation system evolution. Phase 0 (label changes) through Phase 3 (backend API + bug fixes). 6-agent validation converged on label-first, dropdown-later approach.

## Context
Prev header: two-tone (blue mobile / gray-50 desktop), pipe-separated nav links, no active state, no keyboard a11y, profile icon clipped on Mac mini.

---

## Initial Redesign (commit 082a154, 2026-05-19)

Files: `components/layout/main-header.js`, `components/layout/layout.js`, `components/auth/ProfileImage.js`

### Desktop
- `bg-white` replaces `bg-gray-50`. `border-b border-gray-200` separator.
- `<nav aria-label="Primary navigation">` replaces div with pipe spans
- Active link: `text-brand-primary border-b-2 border-brand-primary` (tab indicator)
- Hover: `hover:text-gray-900 hover:border-gray-300`
- Focus: `focus-visible:ring-2 focus-visible:ring-brand-primary focus-visible:ring-inset`
- `aria-current="page"` on active link
- Skip-to-content `<a href="#main-content">` (sr-only, visible on focus)
- `max-w-7xl` replaces hardcoded `max-w-[1200px]`

### Mobile
- Brand blue `bg-fb-blue` preserved
- Consistent icon color: `text-white md:text-gray-600`
- Drawer: `IconButton` replaces bare div for close button
- Drawer active item: left border + `primaryLight` bg + `aria-current="page"`

### Decisions

**MUI AppBar `color="inherit"` required:** MUI defaults `color="primary"` → injects bgcolor → overrides Tailwind bg. `color="inherit"` makes AppBar transparent. Rule: Tailwind bg inside AppBar → always `color="inherit"`.

**`justify-end` not `justify-between`:** `justify-between` spreads right icon cluster across 900px+, pushes icons off-screen. Rule: Right clusters use `justify-end` + `gap-*`.

**ProfileImage Box size:** Badge at `bottom:-2, right:-2` overflows. MUI AppBar `overflow:hidden` clips. Fix: expand Box to `width:44, height:44`.

---

## Phase 0 — Label Changes (2026-05-24)

| Old Label | New Label | URL | Phase 0 | Phase 1+ |
|-----------|-----------|-----|---------|----------|
| Destinations | Explore Thailand | `/destinations` | Label only | + dropdown (later) |
| Locations | Routes | `/locations` | Label only | + dropdown (later) |
| Trips | Journeys | `/trips` | Label only | + dropdown (later) |
| Activities | Experiences | `/activities` | Label only | dropdown works NOW |
| Blogs | Guides | `/blog` | Label only | + dropdown (later) |
| Airports | — (removed) | — | Removed | — |

**6-agent validation:** Phase 1 dropdown UI provides NO real navigation differentiation — all submenu links go to same base page. Best path: label changes now, dropdown when URL params work.

### Component Reuse

| Component | Verdict | Notes |
|---|---|---|
| CategoryMenu.js | Adaptable | Extract `anchorEl`/`Menu` pattern for desktop dropdown |
| PassengerAssignment.js | Adaptable | Accordion state pattern for mobile |
| MUI Accordion | Use directly | Don't build custom |
| Redux ui-slice | Not applicable | All commented out. Local `useState` correct |

---

## Phase 1 — Experiences Dropdown Only

Only Experiences because `/activities` supports `?category=` via `useDayTripFilters`.

**`constants/navConfig.js`** (new) — Experiences section with children.
**`components/layout/NavDropdown.js`** (new) — desktop dropdown, hover-triggered.

---

## Phase 2 — Full Dropdown + URL Param Enhancement

1. Add URL param support to `/destinations`, `/locations`, `/trips`
2. Expand `navConfig.js` with all sections + working URLs
3. Add NavDropdown for all sections on desktop
4. (Optional) Mobile accordion via MUI Accordion

---

## Phase 3 — Backend Data (2026-05-25)

- `NavigationSection` + `NavigationItem` models created, migrated (0010)
- `NavigationViewSet` at `/api/v1/pages-info/navigation/` — 1hr server cache
- `store/api/navigationApi.js` RTK Query + static `navConfig.js` fallback
- Fallback fix: `transformResponse` returns `undefined` (not `[]`) on bad response so `navConfig` fires

### Phase 3 Nav Submenu Audit (2026-05-25)

**Experiences submenu — REMOVED:** `SERVICE_CATEGORIES` in `dayTripConstants.js` already drives `CategoryFilter` chips. Submenu = second source of truth. Fix: `navConfig.js` Experiences → `children: null`. Future: derive from `SERVICE_CATEGORY_LABELS`.

**Explore Thailand submenu — REMOVED:** `?filter=islands` was text search, not geographic category. `Location` model has no `location_type` field. Fix: `navConfig.js` Explore Thailand → `children: null`. Future: add `location_type` CharField to `stations/models.py`.

**Current navConfig (2026-05-25):** All 5 nav items are plain links, no children.

### Phase 3 Bug Fixes

| Bug | Fix | Commit |
|-----|-----|--------|
| `/api/v1/pages-info/navigation/` 404 | Explicit path before `<slug:slug>` catch-all | `6f5286e` |
| Nav disappears when API fails | `transformResponse` returned `[]` (truthy) → `[] || navConfig` = `[]`. Fixed to return `undefined` | `6e299d5` |
| 4x DAY_TOUR duplicate hrefs | Replaced with 7 distinct backend categories | 2026-05-25 |
| Dead `navLinks` export | Deleted from `main-header.js` | `3feafaa` |

See [[adr-experiences-nav-category-filtering]].

---

## A11y Baseline for Nav

- `<nav aria-label="Primary navigation">` — nav landmark
- `aria-current="page"` — current page signal
- `focus-visible:ring` — visible keyboard focus
- Skip-to-content link (`sr-only focus:not-sr-only`) + `id="main-content"` on `<main>`
- Close buttons as `<IconButton>` not bare `<div>`

---

## Deferred Issues

| Issue | Why |
|---|---|
| Mobile accordion | stopPropagation a11y trap, focus management complexity |
| Full dropdown | URL params don't work yet |
| Experiences submenu | Single source of truth violation. Re-add only by deriving from `dayTripConstants.js` |
| Explore Thailand submenu | `?filter=` was text search not category. Needs `location_type` field first |

---

## Related

- [[header-redesign-2026-spec]] — Redesign spec
- [[header-redesign-2026-implementation]] — Implementation notes
- [[adr-experiences-nav-category-filtering]] — Category filtering ADR
- [[design-systems]] — Design tokens
- [[smartenplus/architecture]] — System architecture
- [[admin-dashboard-component-patterns]] — Admin patterns
