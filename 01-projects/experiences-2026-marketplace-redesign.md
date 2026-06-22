No file path given — user pasted text inline. Compressing manually per skill rules:

---

# Experiences 2026 Marketplace Redesign

## Summary

Phase plan to redesign `/activities` into world-class 2026 travel marketplace — Airbnb/Linear/Stripe-level UI. Sidebar filters, card grid, premium card, sort bar. Zero route change. Zero backend work in Phase 1. No existing functionality broken.

> **2026-06-01 update:** 4-agent review (UX, Frontend, Backend, Design) identified blocking issues + spec gaps. All resolved below. Read Decisions table before starting Phase 1.

---

## Context

Current state: `FilterDayTripsPage.js` — full-width layout, no sidebar, basic `DayTripCard.js` (~180px image, inline feature bullets, no sort). Design spec requests Airbnb Experiences / GetYourGuide-level browse page with sidebar filter panel, premium card design, horizontal category chips, sort bar, full responsive strategy.

Codebase exploration confirmed all necessary primitives exist + reusable. No new infrastructure needed for Phase 1.

---

## Decisions

| Decision | Resolution | Reason |
|----------|-----------|--------|
| Route | Keep `/activities` | SEO — no 301 risk, zero disruption |
| Card approach | Enhance `DayTripCard.js` in-place | Only caller is `DayTripList.js` — safe |
| Filter strategy | Phase it — backend-supported only in Phase 1 | No client-side filter hacks, no tech debt |
| Sidebar scope | Sidebar in Phase 1 | Core visual change, can't defer |
| Wishlist | Heart icon, `useState` only (per-card) | No backend endpoint yet. Per-card state — never lift to page level (causes 80 re-renders per click) |
| Docs target | SmartEnPlus SB vault (this file) | Cross-project knowledge artifact |
| Grid system | Tailwind grid for page layout; MUI Grid inside card list | Keep MUI Grid in `DayTripList.js`, wrap in Tailwind 2-col outer layout |
| Card columns at 1440px | 4-col with 240px sidebar | 240px sidebar → ~(1440-240-48)/4 ≈ **288px** per card. Matches Airbnb (286px). Use `lg:grid-cols-[240px_1fr]` |
| Image aspect ratio | 4:3, 220px height, `object-cover`, lazy-loaded | Travel/activity cards — matches GetYourGuide. NOT 16:9 (too wide). NOT 3:2 (Airbnb accommodation pattern). |
| Hover animation | `translateY(-2px)` + shadow elevation, `duration-200` | 2px lift matches industry. Current code has `transform: none` — must remove. |
| Transition duration | 200ms | Industry standard (Airbnb 150–200ms). Code has 300ms — fix to 200ms. |
| CategoryFilter location | Sidebar ONLY | Removed from header. Mobile: bottom sheet (Phase 3). No dual placement. |
| Sort options Phase 1 | 3 options only: Recommended / Most Popular / Highest Rated | `min_rate`/`-min_rate` removed — backend Phase 2 only |
| Focus states | WCAG 2.1 AA required | `focus-visible:ring-2 ring-offset-2` on all interactive elements |
| Rating threshold | Min 5 reviews before showing rating | Prevents noise from 1-review tours |
| Sort active indicator | Required | Show "Sorted by: X" label when non-default sort active |
| Sidebar width token | `SIDEBAR_CONFIG` in `helpers/designSystem.js` | No hardcoded px values in layout |
| `-average_rating` ordering | Requires ORM annotation in `get_queryset()` before Phase 1 | Not model field — computed from Review model. Must annotate. |
| `-booked_count` ordering | Acceptable Phase 1, document as low fidelity | `booked_count` is static field (default=10). Not real booking data. |

---

## Codebase Map

### Files Modified in Phase 1

| File | Change |
|------|--------|
| `components/activities/browse/FilterDayTripsPage.js` | Layout → Tailwind 2-col `lg:grid-cols-[240px_1fr]`. Remove CategoryFilter from header. Add SortBar row. Compact header. |
| `components/activities/browse/DayTripCard.js` | Image 180→220px. Remove `transform: none` from hover. Add `translateY(-2px)` + shadow. `duration-200`. Wishlist heart (per-card `useState`). |
| `hooks/useDayTripFilters.js` | Add `sort: ''` to DEFAULT_FILTERS. Sync `ordering` query param in URL. |
| `store/api/dayTripsApi.js` | Add `ordering` arg to `getContracts`. Pass as `params.append('ordering', ordering)`. |
| `helpers/designSystem.js` | Add `SIDEBAR_CONFIG = { widthValue: 240, width: 'w-[240px]', responsive: 'hidden lg:block' }` |
| `smartenplus-backend/products/views.py` | Annotate `avg_rating = Avg(...)` in `ContractViewSet.get_queryset()` for `-average_rating` ordering |

### New Files in Phase 1

| File | Purpose |
|------|---------|
| `components/activities/browse/SortBar.js` | Results count + sort dropdown. Phase 1: 3 options only. ≤60 lines. |
| `components/activities/browse/ExperienceSidebar.js` | StickySidebar wrapper + CategoryFilter (vertical). Filter stubs for Phase 2. ≤80 lines. |

### Reused Without Change

| Component | Used For |
|-----------|---------|
| `components/UI/StickySidebar.js` | Sidebar sticky positioning. **IMPORTANT: never add `overflow-y-auto` to sidebar — breaks sticky positioning.** |
| `components/UI/DynamicFilterList.js` | Filter list in sidebar (Phase 2+) |
| `components/activities/shared/PromotionalBadge.js` | Card badge overlay (keep as-is) |
| `components/activities/shared/RatingDisplay.js` | Card rating row |
| `components/activities/shared/PricingDisplay.js` | Card price display |
| `helpers/designSystem.js` | COLORS, BORDER_RADIUS, STICKY_CLASSES, SIDEBAR_CONFIG (new) |

---

## Layout Structure (Phase 1)

```jsx
<section className="max-w-[1536px] mx-auto px-4 sm:px-6">
  {/* Full-width above grid */}
  <Box header />
  <ActivitySearch />

  {/* 2-col grid below */}
  <div className="lg:grid-cols-[240px_1fr] gap-6 mt-4">
    {/* Left col: sidebar */}
    <StickySidebar className="hidden lg:block">
      <ExperienceSidebar />  {/* CategoryFilter + Phase 2 stubs */}
    </StickySidebar>

    {/* Right col: results */}
    <div>
      <SortBar count={total} sort={filters.sort} onSortChange={updateSort} />
      <DayTripList contracts={contracts} />
      <Pagination />
    </div>
  </div>
</section>
```

**StickySidebar constraint:** `max-h-[calc(100vh-100px)] overflow-y-auto` must be on inner content wrapper, NOT on StickySidebar itself. Sticky breaks if sticky element is scroll container.

---

## Backend API (Current Capabilities)

**Endpoint:** `GET /api/v1/contract/`

| Param | Supported Now | Phase | Notes |
|-------|-------------|-------|-------|
| `service_category` | ✓ | 1 | |
| `location` | ✓ (location_name text) | 1 | |
| `search` | ✓ substring (not full-text/fuzzy) | 1 | Document as substring search |
| `ordering` | ✓ (`score`, `-booked_count`, `-average_rating`) | 1 | `-average_rating` requires ORM annotation. `-booked_count` uses legacy static field (low fidelity). |
| `page`, `page_size` | ✓ | 1 | Default `page_size=10`. Frontend use 12 or 16 for even grid fill. |
| `min_price`, `max_price` | ✗ | 2 | Filter on `ratecards.selling_rate`. Use `annotate(min_rate=Min(...)).distinct()` — no raw JOIN (N+1 risk). |
| `duration_type` | ✗ | 2 | See Phase 2 mapping table |
| `contract_type` | ✗ (model has `type`: JOIN/PRIVATE/CHARTER) | 2 | |
| `features` | ✗ (model has `extra` ManyToMany) | 2 | Requires canonical slug list first |
| `min_rating` | ✗ | 2 | Same ORM annotation as `average_rating` |

Phase 2 backend changes: add `FilterSet` to `products/views.py` via `products/filters.py`.

---

## Phase Breakdown

> 4-phase architecture sequence extracted → [[experiences-marketplace-4-phase-architecture-sequence]]
> (Phase 1: layout + premium card, frontend-only → Phase 2: backend filters → Phase 3: mobile → Phase 4: iPad + polish)



## Design Spec (Source of Truth)

**Page:** `/activities` (NOT homepage, NOT travel guide)

**Tone:** Airbnb Experiences + GetYourGuide + Linear design system

**Desktop 1440px:**
- Container: `max-w-[1536px]`
- Header: compact intro ≤180px total height. "Experiences in Thailand" H1. Subtitle. Search bar.
- Layout: 240px sidebar + main (`lg:grid-cols-[240px_1fr]`)
- SortBar above results: count + 3-option sort dropdown + active sort indicator

**Card anatomy (220px height, 4:3 aspect ratio):**
- Image: 220px height, 4:3 aspect ratio (`object-cover`, lazy-loaded)
- Promotional badge overlay (Best Seller / Top Rated / Popular / Likely To Sell Out) — hidden when none applies, no empty space reserved
- Rating + review count — shown only if `review_count >= 5`
- Title (2-line clamp, `text-base font-semibold text-gray-900`)
- Benefits: ✓ Free Cancellation ✓ Instant Confirmation ✓ Hotel Pickup
- Price (right-aligned, same row as rating via flex spacer)
- Wishlist heart (top-right corner, per-card `useState`, `onClick: e.stopPropagation()`)
- Hover: `translateY(-2px)` + shadow elevation, `transition-all duration-200`
- Focus: `focus-visible:ring-2 ring-offset-2` (WCAG AA)
- Touch press: `active:scale-95`

**iPad 1024px:**
- 2-col card grid
- Filter drawer (not sidebar)

**Mobile 375px:**
- Single col cards
- Sticky Filter + Sort bottom buttons (`fixed bottom-0 z-40`)
- Bottom-sheet filters (MUI Drawer `anchor="bottom"`, max 70vh)
- Category chips: horizontal scroll with gradient fade-right edge

**Design tokens (mandatory):**
- Colors: `COLORS.*` from `helpers/designSystem.js` — no raw hex values
- Sidebar width: `SIDEBAR_CONFIG.widthValue` (240) — not hardcoded
- Typography: `TYPOGRAPHY_SCALE.*` for card text — not hardcoded px

**Accessibility (WCAG 2.1 AA):**
- All images: descriptive `alt` text
- Cards: keyboard navigable, Enter/Space triggers navigation
- Focus indicators visible on all interactive elements
- Ratings: `aria-label` with full text (e.g., "4.8 stars, 124 reviews")
- Color not sole indicator — icons + text for status/badges

**Avoid:** hero banners, marketing sections, travel guides, journey planning, route bundles, transfer products, dashboard styling.

---

## Constraints

- No route change (`/activities` stays)
- No SSR added to `pages/activities/index.js`
- No `useEffect` chains — single `setFilters` call per update
- No MUI Grid v2 migration
- All new components ≤200 lines
- No shared component API changes without full caller audit
- `transform: none` override in DayTripCard.js hover must be removed
- `SortBar` Phase 1: 3 options only (no price sort)
- Sidebar width from `SIDEBAR_CONFIG` — no hardcoded px in grid template
- Wishlist state: per-card `useState` only — never lifted to page level
- `StickySidebar`: never add `overflow-y-auto` to sticky element itself (breaks positioning)

---

## Verification Checklist

- [ ] `npm run dev` → `/activities` shows sidebar + card grid
- [ ] Category chip (in sidebar) → filters + URL updates
- [ ] Sort dropdown → 3 options only, results reorder via `ordering` param visible in network tab
- [ ] Active sort → "Sorted by: X" indicator visible in SortBar
- [ ] Card hover → 2px lift + shadow (not just shadow)
- [ ] Card focus (keyboard Tab) → visible ring
- [ ] Wishlist heart → toggles locally, heart state per-card
- [ ] Mobile 375px → single col, no sidebar, bottom bar visible
- [ ] `npm run build` → clean, no lint errors
- [ ] `/activities/detail/[slug]` → unaffected
- [ ] Rating hidden when review_count < 5

---

## Agent Review Notes (2026-06-01)

4-agent (UX, Frontend, Backend, Design) debate findings — all resolved above.

**Key discoveries:**
- `SortBar.js` already existed with `min_rate`/`-min_rate` options not supported by backend — must strip for Phase 1
- `useDayTripFilters.js` had no `sort` field — blocking
- `-average_rating` ordering requires Django ORM annotation — not model field
- `booked_count` is static legacy field (hardcoded default=10) — low fidelity sort, acceptable Phase 1
- Card hover had `transform: none` override — explicitly blocks lift animation
- Sidebar width 240px (not 280px) unlocks proper 4-col grid at 1440px (288px cards vs 270px)
- CategoryFilter must move to sidebar only — no dual placement
- Phase 2 N+1 risk on `min_price`/`max_price` filter — requires `annotate(min_rate=Min(...)).distinct()`

---

## Related

- [[activities-day-tour-page-review]] — prior code audit, P0/P1 fixes
- [[activities-search-merge-review]] — unified ActivitySearch (already shipped: `02f9adf`)
- [[layout-spacing-consistency-audit]] — LAY-1 + LAY-2 fixes (already shipped: `09e0db3`)
- [[adr-experiences-nav-category-filtering]] — URL param → API filter chain ADR
- [[smartenplus-wireframe-architecture]] — full platform wireframe including Experiences section

## Related Atoms (Extracted 2026-06-13)
- [[sidebar-sticky-2col-responsive-grid]] — 240px sidebar + 4-col 1440px card grid math
- [[orm-annotation-aggregate-min-rate]] — DRF `avg_rating` + `min_rate` annotation pattern
- [[wishlist-per-card-state-not-page]] — per-card `useState` for heart icon (avoid 80 re-renders/click)

## Orphan Link-Backlog (Linked 2026-06-13)
- [[carousel-embla-align-start-mobile-snap]] — Embla carousel align-start mobile-snap pattern
- [[section-render-order-principles]] — section render order principles (eager vs lazy, mobile vs desktop)
- [[experience-faq-architecture-review]] — FAQ architecture review (sub-concern of marketplace redesign)
- [[adr-activity-card-favorite-button]] — ADR for activity-card favorite button via bookmark API