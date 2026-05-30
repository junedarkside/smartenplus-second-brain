# Airport Transfers Section Redesign — 2026-05-30

**Branch:** `260528-feat/header-redesign-2026`
**Scope:** Homepage airport transfer section — UX/UI redesign + backend API extension

---

## Debate

### Problem

Old section: station grid (gray boxes, airport name only, no routes, no prices). Zero booking intent. Violated the 2-second Airport → Destination → Price → Click rule.

### Options Evaluated

| Option | Description | Decision |
|--------|-------------|----------|
| A: Static hardcoded routes | 4 curated route configs with manual prices | Rejected — prices stale, maintenance burden |
| B: Filter `home_routes` client-side | Parse station_type from existing home_routes payload | Rejected — brittle, station_type not guaranteed in payload |
| C: New `airport_routes` key in FrontPage API | Backend adds dedicated query filtered by `station_type='airport'` | **Chosen** — real prices, cacheable, clean separation |

---

## Decision

**Option C.** Backend `FrontPageViewSet` adds `_fetch_airport_routes_data()` method — mirrors existing `_fetch_home_routes_data()` pattern but filters `Route` queryset by `departure_station__station_type='airport'`. Returns `HomeSerializer` shape (same as `home_routes`). Cached via existing frontpage cache TTL (300s).

Frontend gets `airport_routes` key from `frontPageData` — dedicated array, no client-side filtering.

---

## Implementation

### Backend — `pages_info/views.py`

**Imports added:**
```python
from django.db.models import Subquery, OuterRef, Exists
from datetime import date
from products.models import Route, Trip
from operators.models import Contract, Contract_RateCard
```

**New method:** `FrontPageViewSet._fetch_airport_routes_data(request, parsed_query_limit)`
- Queries `Route` filtered by `departure_station__station_type='airport'`
- Filters: must have active Trip + active non-expired Contract
- Annotates: `lowest_price` (Subquery on Contract_RateCard), `operator_count`
- Orders by `-query_count` (most popular first)
- Default limit: 4 (homepage shows 4 cards)
- Uses existing `HomeSerializer` — no new serializer

**Added to `list()`:**
```python
response_data["airport_routes"] = self._fetch_airport_routes_data(request, parsed_query_limit)
```

### Frontend — 3 files

**NEW:** `components/airport-transfer/AirportTransferRouteCard.js`
- Text-only card (no images — Omio style)
- Props: `{ route, onClick }` — route = HomeSerializer shape
- Layout: airport name (IATA) / destination arrow / price / "View Route →"
- Link: `/airport-transfer/{departure_station.slug}/`
- `rounded-2xl` (16px radius per brief), hover shadow

**REWRITTEN:** `lib/homepage/components/AirportTransferSection.js`
- Header: `✈ Airport Transfers` + subtitle + right-aligned "View all →"
- Grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`
- GTM event: `airport_transfer_click` on card click
- Prop: `airportRoutes` (new), drops `airportTransferData`/`SimpleStationGridComponent`

**UPDATED:** `pages/homepagev2.js`
- Added `const airportRoutes = frontPageData?.airport_routes;`
- Updated prop: `<AirportTransferSection airportRoutes={airportRoutes} error={error} />`
- Added `airport_routes: []` to error fallback

---

## Tech Debt Score

| Category | Score | Notes |
|----------|-------|-------|
| No hardcoded data | ✅ | All from API |
| No new serializers | ✅ | Reuses HomeSerializer |
| No new endpoints | ✅ | Extends existing FrontPageViewSet |
| No new dependencies | ✅ | Reuses all existing imports/components |
| Component size | ✅ | RouteCard <60 lines, Section <60 lines |
| Complexity | ✅ | Single responsibility each |
| **Total debt** | **0** | Clean |

---

## Reuse Audit

| Asset | Reused From | Notes |
|-------|-------------|-------|
| `HomeSerializer` | `products/serializers.py` | Same shape as home_routes |
| `Section`, `ContentCard` | `components/common/` | Unchanged |
| `capitalizeWords` | `helpers/textDecoration.js` | |
| `isGTMEnabled`, `sendGTMEvent` | `helpers/gtmUtils.js` | GTM pattern from PopularRoutesSection |
| `formatPrice` | Inline (pattern from PopularRouteImageCard) | 7 lines |

---

## Next Auditor Notes

1. **`airportTransferData` prop removed** from `AirportTransferSection` — was `frontPageData?.stations` (station objects, no routes/prices). No longer needed. `stations` key still in API for other uses.

2. **Mobile UX:** Cards are `grid-cols-1` on mobile — full width stack. If horizontal scroll is preferred (like PopularRoutes carousel), wrap in `CardCarouselContainer`. Current decision: stack is simpler and avoids horizontal scroll on airport-specific discovery.

3. **Pricing fallback:** If `lowest_price` is null (no active contract), card shows "Check price" text and still links to station page. Non-blocking.

4. **Backend cache:** `airport_routes` is included in the same frontpage cache TTL (300s). If airport pricing changes frequently, consider separate cache key with shorter TTL in `_fetch_airport_routes_data`.

5. **ISR:** `homepagev2.js` uses `getStaticProps` with ISR. Backend data refreshes via revalidation period. For real-time pricing, this is fine — prices update on next revalidation.

6. **Link target:** Cards link to `/airport-transfer/{departure_station.slug}/` — the station's trip listing page. This is intentional (browse all routes from that airport). No deep-link to specific route needed for homepage discovery.

---

## Style Consistency Audit — 2026-05-30 (Pass 2)

Audited against PopularRoutesSection, LocationsSection, ReviewsSection, designSystem.js.

### Issues Found & Fixed

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | 🔴 HIGH | Card `rounded-2xl` (16px) vs design system `rounded-md` (6px) | Fixed → `rounded-md` |
| 2 | 🔴 HIGH | Hover border `gray-300` instead of `fb-blue` | Fixed → `hover:border-fb-blue` |
| 3 | 🔴 HIGH | Hover shadow `shadow-md` instead of `shadow-lg` | Fixed → `hover:shadow-lg` |
| 4 | 🔴 HIGH | Header `<div>` instead of `<header>` semantic tag | Fixed → `<header>` |
| 5 | 🟡 MED | `ContentCard` wrapper — other sections don't use it | Removed |
| 6 | 🟡 MED | Header padding `px-2` instead of `pl-2` | Fixed → `pl-2` |
| 7 | 🟡 MED | GTM event reading wrong field paths (`station_name` not in payload) | Fixed → `location.location_name` |
| 8 | 🟡 MED | `transition-all` instead of `transition-colors` | Fixed → `transition-colors` |

### Issues Kept (by design)

| # | Severity | Issue | Reason Kept |
|---|----------|-------|-------------|
| 9 | 🟡 MED | Subtitle `<p>` below header | Airport transfers needs context sentence — other sections have self-explanatory icons |
| 10 | 🟢 LOW | `min-h-[120px]` card height | Removed — let content define height |
| 11 | 🟢 LOW | `group-hover:underline` on "View Route →" | Minor, no regression |

### Files Changed (Pass 2)
- `lib/homepage/components/AirportTransferSection.js` — removed ContentCard, fixed header structure/padding/semantics
- `components/airport-transfer/AirportTransferRouteCard.js` — fixed radius, hover shadow, hover border, transition
