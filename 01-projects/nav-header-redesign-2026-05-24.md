# Nav/Header Redesign 2026-05-24

## Summary

New SmartEnPlus navigation system. 6-agent validation (audit + implementation review) converged on **label changes first, dropdown later**.

**Status:** Phase 0 planned — label changes only, no new components.

## Strategic Shift

| Old Label | New Label | URL | Phase 0 | Phase 1+ |
|-----------|-----------|-----|---------|----------|
| Destinations | Explore Thailand | `/destinations` | Label only | + dropdown (later) |
| Locations | Routes | `/locations` | Label only | + dropdown (later) |
| Trips | Journeys | `/trips` | Label only | + dropdown (later) |
| Activities | Experiences | `/activities` | Label only | **dropdown works NOW** |
| Blogs | Guides | `/blog` | Label only | + dropdown (later) |
| Airports | — (removed) | — | Removed | — |

**Key insight from 6-agent validation:** Phase 1 dropdown UI provides NO real navigation differentiation because all submenu links go to the same base page (URL params don't work). Best path: label changes now, dropdown when URL params actually work.

## Validation Findings

### What 6 Agents Found

**Audit team (3 agents):**
- URL filter params broken on `/destinations`, `/locations`, `/trips` — pages don't read `router.query.filter`
- Mobile drawer is flat list — no accordion state, clicking closes drawer
- `navLinks` (desktop, 6 items) and `menuLinks` (mobile, 13 items) are separate, different arrays
- CategoryMenu.js is dropdown pattern, not accordion — wrong pattern for mobile

**Validation team (3 agents):**
- Phase 1 dropdown provides no real differentiation (all submenu links → same base page)
- Mobile accordion rework is severely underestimated — stopPropagation a11y trap, focus management complexity
- Simpler alternative: just change labels first (15 min, zero risk)
- Only Experiences dropdown has working URL params (`/activities?category=FOOD_DINING` works)

### Component Reuse Findings

| Component | Verdict | Notes |
|---|---|---|
| CategoryMenu.js | Adaptable | Extract `anchorEl`/`Menu` pattern for desktop dropdown. Strip search logic. |
| PassengerAssignment.js | Adaptable | Accordion state pattern (`expandedPanel`) for mobile accordion. |
| MUI Accordion | Use directly | Don't build custom accordion — use MUI's. |
| Redux ui-slice | Not applicable | All commented out. Local `useState` correct for nav state. |

## Implementation Plan

### Phase 0 — Label Changes Only (Do Now)

**Cost:** ~15 minutes. **Risk:** Near zero. **Gain:** 80% of naming improvement.

**`components/layout/main-header.js`** — change `navLinks` labels:
```js
{ href: "/destinations", label: "Explore Thailand" },
{ href: "/trips", label: "Journeys" },
{ href: "/activities", label: "Experiences" },
{ href: "/locations", label: "Routes" },
{ href: "/blog", label: "Guides" },
// Airports removed
```

**`components/layout/layout.js`** — change `menuLinks` labels, remove Airport Transfers:
- Same 5 label changes
- Remove "Airport Transfers" entry
- Do NOT add dropdown/accordion yet

### Phase 1 — Experiences Dropdown Only

**Why only Experiences?** `/activities` already supports `?category=` params via `useDayTripFilters`.

**`constants/navConfig.js`** (new) — Experiences section with children:
```js
{
  label: 'Experiences',
  href: '/activities',
  children: [
    { label: 'Food & Night Markets', href: '/activities?category=FOOD_DINING' },
    { label: 'Island Adventures', href: '/activities?category=DAY_TOUR' },
    { label: 'Wellness', href: '/activities?category=SPA_WELLNESS' },
  ]
}
```

**`components/layout/NavDropdown.js`** (new) — desktop dropdown, hover-triggered, no accordion.

**`components/layout/main-header.js`** — conditional render NavDropdown for Experiences only.

### Phase 2 — Full Dropdown + URL Param Enhancement

**Step 1:** Add URL param support to `/destinations`, `/locations`, `/trips`:
```js
// In pages/destinations/index.js
useEffect(() => {
  if (router.query.filter) setSearchTerm(router.query.filter)
}, [router.query.filter])
```

**Step 2:** Expand `navConfig.js` with all nav sections + working URLs.

**Step 3:** Add NavDropdown for all sections on desktop.

**Step 4 (optional):** Mobile accordion — use MUI Accordion in drawer. High complexity, defer if possible.

### Phase 3 — Backend Data ✅ DONE (2026-05-25)

- `NavigationSection` + `NavigationItem` models created, migrated (0010)
- `NavigationViewSet` at `/api/v1/pages-info/navigation/` — 1hr server cache
- `store/api/navigationApi.js` RTK Query + static `navConfig.js` fallback
- Fallback fix: `transformResponse` returns `undefined` (not `[]`) on bad response so `navConfig` fires correctly
- **Blocker remaining:** `NavigationSection` table empty — populate via Django admin

### Phase 3 Bug Fixes (2026-05-25)

| Bug | Fix | Commit |
|-----|-----|--------|
| `/api/v1/pages-info/navigation/` 404 | Explicit path in `apis/urls.py` before `<slug:slug>` catch-all | `6f5286e` |
| Nav disappears when API fails | `transformResponse` returned `[]` (truthy) → `[] \|\| navConfig` = `[]`. Fixed to return `undefined` | `6e299d5` |
| 4× DAY_TOUR duplicate hrefs | Replaced with 7 distinct backend categories | committed 2026-05-25 |
| Dead `navLinks` export | Deleted from `main-header.js` | `3feafaa` |

See [[adr-experiences-nav-category-filtering-2026-05-25]] for full category filtering architecture.

## SEO Notes

| Phase | Sitemap | URLs | Canonical |
|-------|---------|------|-----------|
| Phase 0 | No changes | Unchanged | No changes |
| Phase 1 | No changes | Unchanged | No changes |
| Phase 2 | No changes | Unchanged (params added) | Canonical to base for param pages |
| Phase 3 | Add new submenu pages | New pages added | Self-referential |

## Deferred Issues

| Issue | Why Deferred |
|---|---|
| Mobile accordion | stopPropagation a11y trap, focus management complexity, product decision on extra items (Operators, Q&A, etc.) |
| Full dropdown | URL params don't work yet, no real UX benefit in Phase 1 |
| Backend nav API | Depends on Phase 2 URL param work being validated |

## Related

- [[seo-homepage-specialist-team]] — SEO audit patterns used here
- [[nextjs-patterns]] — SSR/ISR patterns for the pages involved
- [[payment-system]] — not related but kept for context