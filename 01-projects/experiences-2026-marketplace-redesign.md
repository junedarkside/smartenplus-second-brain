# Experiences 2026 Marketplace Redesign

## Summary

Phase plan to redesign `/activities` into a world-class 2026 travel marketplace — Airbnb/Linear/Stripe-level UI. Sidebar filters, 4-col grid, premium card, sort bar. Zero route change. Zero backend work in Phase 1. No existing functionality broken.

---

## Context

Current state: `FilterDayTripsPage.js` — full-width layout, no sidebar, basic `DayTripCard.js` (~180px image, inline feature bullets, no sort). Design spec requests Airbnb Experiences / GetYourGuide-level browse page with sidebar filter panel, premium card design, horizontal category chips, sort bar, and full responsive strategy.

Codebase exploration confirmed all necessary primitives exist and are reusable. No new infrastructure needed for Phase 1.

---

## Decisions

| Decision | Resolution | Reason |
|----------|-----------|--------|
| Route | Keep `/activities` | SEO — no 301 risk, zero disruption |
| Card approach | Enhance `DayTripCard.js` in-place | Only caller is `DayTripList.js` — safe |
| Filter strategy | Phase it — backend-supported only in Phase 1 | No client-side filter hacks, no tech debt |
| Sidebar scope | Sidebar in Phase 1 | Core visual change, can't defer |
| Wishlist | Heart icon, `useState` only | No backend endpoint exists yet |
| Docs target | SmartEnPlus SB vault (this file) | Cross-project knowledge artifact |

---

## Codebase Map

### Files Modified in Phase 1

| File | Change |
|------|--------|
| `components/activities/browse/FilterDayTripsPage.js` | Layout → 2-col grid `lg:grid-cols-[280px_1fr]`. Move CategoryFilter into sidebar. Add SortBar row. Compact header. |
| `components/activities/browse/DayTripCard.js` | Image 180→220px. Wishlist heart (local state). Hover elevation. Shadow-sm border. Benefits row style. |
| `hooks/useDayTripFilters.js` | Add `sort` field, sync `ordering` query param. |
| `store/api/dayTripsApi.js` | Pass `ordering` param in `getContracts` query. |

### New Files in Phase 1

| File | Purpose |
|------|---------|
| `components/activities/browse/SortBar.js` | Results count + sort dropdown. ≤60 lines. |
| `components/activities/browse/ExperienceSidebar.js` | StickySidebar wrapper + CategoryFilter (vertical). Filter stubs for Phase 2. ≤80 lines. |

### Reused Without Change

| Component | Used For |
|-----------|---------|
| `components/UI/StickySidebar.js` | Sidebar sticky positioning |
| `components/UI/DynamicFilterList.js` | Filter list in sidebar (Phase 2+) |
| `components/activities/shared/PromotionalBadge.js` | Card badge overlay (keep as-is) |
| `components/activities/shared/RatingDisplay.js` | Card rating row |
| `components/activities/shared/PricingDisplay.js` | Card price display |
| `helpers/designSystem.js` | COLORS, BORDER_RADIUS, STICKY_CLASSES |

---

## Backend API (Current Capabilities)

**Endpoint:** `GET /api/v1/contract/`

| Param | Supported Now | Phase |
|-------|-------------|-------|
| `service_category` | ✓ | 1 |
| `location` | ✓ (location_name text) | 1 |
| `search` | ✓ full-text | 1 |
| `ordering` | ✓ (`score`, `-booked_count`, `-average_rating`) | 1 |
| `page`, `page_size` | ✓ | 1 |
| `min_price`, `max_price` | ✗ | 2 |
| `duration_type` | ✗ | 2 |
| `contract_type` | ✗ (model has `type`: JOIN/PRIVATE/CHARTER) | 2 |
| `features` | ✗ (model has `extra` ManyToMany) | 2 |
| `min_rating` | ✗ | 2 |

Phase 2 backend changes: add `FilterSet` to `ContractViewSet` in `products/views.py`.

---

## Phase Breakdown

### Phase 1 — Layout + Premium Card
**Git branch:** `260601-fix/activities-browse-audit` (current) or new branch  
**Checkpoint commit:** `feat(activities): Phase 1 — sidebar layout + premium card + sort bar`

- 2-col layout desktop (`lg:grid-cols-[280px_1fr]`)
- Sidebar with CategoryFilter (vertical chips → sidebar list)
- SortBar: results count + ordering dropdown
- DayTripCard: 220px image, wishlist heart, hover elevation, shadow-sm
- Header: compact, "Experiences in Thailand", subtitle line
- Sort wired to `ordering` API param

**Does not touch:** payment, checkout, cart, auth, any shared helpers.

---

### Phase 2 — Backend Filters
**Checkpoint commit:** `feat(activities): Phase 2 — full filter params frontend+backend`

Backend (`smartenplus-backend/products/views.py`):
- Add `min_price`, `max_price` → filter on `ratecards.selling_rate`
- Add `duration_type` → map to `tour_duration_days` or `duration` field ranges
- Add `contract_type` → filter on `type` (JOIN=Group, PRIVATE=Private)
- Add `features` → filter on `extra__item__icontains` or exact slug match
- Add `min_rating` → filter on `average_rating`

Frontend:
- `ExperienceSidebar.js` — activate Price/Duration/Type/Features/Rating filter sections
- `useDayTripFilters.js` — add new filter keys
- `dayTripsApi.js` — pass new params

---

### Phase 3 — Mobile
**Checkpoint commit:** `feat(activities): Phase 3 — mobile layout + bottom-sheet filters`

- Sidebar `hidden lg:block`
- Sticky bottom bar: Filter + Sort buttons (`fixed bottom-0 z-50`)
- MUI Drawer `anchor="bottom"` for filter sheet
- Category chips: `flex flex-nowrap overflow-x-auto` (no wrap mobile)
- Cards: `grid-cols-1` mobile

---

### Phase 4 — iPad + Polish
**Checkpoint commit:** `feat(activities): Phase 4 — iPad layout + polish`

- 1024px: 2-col card grid, filter drawer (not sidebar)
- `DayTripList.js` grid: `xs=12 sm=6 md=6 lg=4 xl=3`
- Skeletons match 220px card height
- Empty state redesign

---

## Design Spec (Source of Truth)

**Page:** `/activities` (NOT a homepage, NOT a travel guide)

**Tone:** Airbnb Experiences + GetYourGuide + Linear design system

**Desktop 1440px:**
- Header: compact intro ≤180px total height. "Experiences in Thailand" H1. Subtitle. Search bar.
- Categories: horizontal chips immediately below search
- Layout: 280px sidebar (filters) + main (4-col grid)
- SortBar above results: count + sort dropdown

**iPad 1024px:**
- 2-col card grid
- Filter drawer (not sidebar)

**Mobile 375px:**
- Single col cards
- Sticky Filter + Sort bottom buttons
- Bottom-sheet filters
- Horizontal category scroll

**Card anatomy:**
- 220px image
- Promotional badge overlay (Best Seller / Top Rated / Popular / Likely To Sell Out)
- Rating + review count
- Title (2-line clamp)
- Benefits: ✓ Free Cancellation ✓ Instant Confirmation ✓ Hotel Pickup
- Price (right-aligned)
- Wishlist heart (top-right corner, local state)
- Hover: elevation + `-translate-y-0.5`

**Avoid:** hero banners, marketing sections, travel guides, journey planning, route bundles, transfer products, dashboard styling.

---

## Constraints

- No route change (`/activities` stays)
- No SSR added to `pages/activities/index.js`
- No `useEffect` chains — single `setFilters` call per update
- No MUI Grid v2 migration
- All new components ≤200 lines
- No shared component API changes without full caller audit

---

## Verification Checklist

- [ ] `npm run dev` → `/activities` shows sidebar + 4-col grid
- [ ] Category chip → filters + URL updates
- [ ] Sort dropdown → results reorder via `ordering` param
- [ ] Card hover → elevation + translate
- [ ] Wishlist heart → toggles locally (no persist)
- [ ] Mobile 375px → single col, no sidebar
- [ ] `npm run build` → clean, no lint errors
- [ ] `/activities/detail/[slug]` → unaffected

---

## Related

- [[activities-day-tour-page-review-2026-06-01]] — prior code audit, P0/P1 fixes that should be resolved before this redesign
- [[activities-search-merge-review-2026-06-01]] — unified ActivitySearch (already shipped: `02f9adf`)
- [[layout-spacing-consistency-audit-2026-06-01]] — LAY-1 + LAY-2 fixes (already shipped: `09e0db3`)
- [[adr-experiences-nav-category-filtering-2026-05-25]] — URL param → API filter chain ADR
- [[smartenplus-wireframe-architecture]] — full platform wireframe including Experiences section
