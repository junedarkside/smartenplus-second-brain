# Trip Search Results Redesign — Travel Decision Engine

> **Audited 2026-06-14** — 3-agent code-truth audit: 28/36 claims verified, 6 corrected. See "## Audit Corrections" at bottom. **Two plan-breaking findings: SlideCalendar2 is live (not commented out); `getTrustBadges` Free-Cancellation check is inverted-buggy.**

## Summary
Redesign `/trips/[from]/[to]` from sidebar-filter marketplace into decision engine. 3-agent analysis complete (backend + frontend arch + UX/UI). Phase 0 done. Implementation starts Phase 1.

---

# Backend API Feasibility Analysis

**Date:** 2026-06-14
**Scope:** 3-feature feasibility for trip search results redesign

---

## Feature 1: Confidence Score Algorithm

→ Extracted to [[contract-confidence-score-algorithm]] (formula + cold-start + N+1 fix + tiebreakers). Decision: backend `SerializerMethodField` on `ContractSerializer` with reweighted formula (rating 0.45 / review-trust 0.25 / popularity 0.20 / admin-override 0.10).

---

## Feature 2: Recommended Pick Algorithm

### Current Bug: `sortContractsByScore` is broken

`helpers/tripSorting.js` lines 7-13 sorts on `contract.score` (raw null admin field). If all operators have `score=null` → flat zero-tie → "Recommended" sort is currently meaningless.

**Fix:** Update `sortContractsByScore` to sort on `confidence_score` once backend field exists.

### No Recommended Endpoint

`RecommendationItemSerializer` scaffold exists in `products/serializers.py` lines 1203-1235 but zero views wire to it. For this sprint: client-side sort on backend `confidence_score` field is sufficient. Dedicated endpoint waits for personalization.

### Tiebreaker Chain
1. `confidence_score` descending
2. `average_rating` descending
3. `booked_count` descending
4. `id` ascending (stable)

---

## Feature 3: Quick Filter Pills — Direct + Refundable

### Direct Pill

`trasportation_com.length === 1` = single-leg direct trip (confirmed from `products/views.py` lines 1514-1526).

`ContractForFilterSerializer` only exposes `['id', 'name', 'start_date', 'end_date']` — does NOT expose `transport_composit`. TripFilter metadata lacks per-contract direct info.

**Backend must add:** `has_direct_option: boolean` to TripFilter metadata response.

**Frontend interim:** derive from `tripsFilterSet.unique_transport_composit_list` — check if any entry has `trasportation_com.length === 1`. If none → disable pill.

### Refundable Pill

Two parallel cancellation models:
- `CancellationPolicy` (old): `free_refund = CharField(choices=['yes','no'])`
- `CancellationPolicies` + `CancellationDetail` (new): `refund_percentage == 100`

Client-side detection unreliable. Frontend has NO refundable filter today.

**Backend must add:**
- `has_refundable_option: boolean` to TripFilter metadata
- `is_refundable: boolean` per contract in results

Implementation cost: Low — no migrations, add computed keys to TripFilter `list` view (lines 1620-1642).

### Known Schema Issues

1. **`trasportation_com` typo** — load-bearing, both BE view line 1515 and FE FilteredTripList.js line 53 use it. Match exactly.
2. **Dual cancellation model** — Contract FK to both old `CancellationPolicy` and new `CancellationPolicies`. Any refundable check must handle both.
3. **N+1 in serializer** — `get_average_rating` + `get_review_count` each fire separate queries. Adding `get_confidence_score` without refactor = 3rd N+1. Fix with shared `_get_review_stats()`.
4. **`booking_count_yesterday` bug** — filters `created__gte=yesterday_start` (last 24h, not calendar yesterday). Not a blocker.

---

# Frontend Architecture Analysis

**Source:** Direct code analysis of hooks, components, and helpers.

---

## filterData Shape (Exact)

Source: `hooks/useTripFilters.js` lines 5-17.

```js
{
  sort: 'Recommended',      // string: 'Recommended'|'EarlyArrival'|'Fastest'|'Cheapest'|'EarlyDeparture'|'TopRated'|'default'
  priceRange: [0, 100],     // [number, number] — overwritten by tripsFilterSet min/max on load
  transportationMode: [],   // string[] — contract.type values: 'JOIN'|'PRIVATE'|'CHARTER'
  operatorList: [],         // { operator_name: string }[] — object array, not strings
  transportOptions: [],     // object[] — full entries from tripsFilterSet.unique_transport_composit_list
  arrTimes: [],             // string[] — contract.arrivalTime e.g. '14:00:00'
  depTimes: [],             // string[] — contract.departureTime
  conditions: [],           // { extra_type: string, extra_name: string }[]
  amenities: [],            // { extra_type: string, extra_name: string }[]
  departureStations: [],    // string[]
  arrivalStations: [],      // string[]
}
```

**Sort string values:**

| Pill | filterData.sort value |
|------|----------------------|
| Best Value / Recommended | `'Recommended'` |
| Fastest | `'Fastest'` |
| Cheapest | `'Cheapest'` |

**`setFilterData` behavior:** Full replacement via React `useState` setter. Always use `prev => ({ ...prev, field: value })` spread pattern. Route change resets all array fields, preserves `sort`.

---

## transportOptions Shape

Each entry from `tripsFilterSet.unique_transport_composit_list`:
```js
{
  trasportation_com: [  // TYPO — "trasportation" not "transportation" — load-bearing
    { type_class: string, vehicle_class: string }
    // more items = multi-leg trip
  ]
}
```

Dual-key access pattern (from `TransportationOptionsFilter.js` line 8):
```js
const transportationData = option?.transportation_com || option?.trasportation_com;
```

All new code touching this field must use dual-key pattern.

---

## conditions Filter vs getTrustBadges — Two Different Data Paths

- `filterData.conditions` → filters `contract.extra[].type / .item` (FEATURE type extras)
- `getTrustBadges` → reads `contract.cancellation_policies.cancellation_details`

**Incompatible paths.** "Refundable" pill using `filterData.conditions` needs backend to add `is_refundable` per contract. Confirm with backend before committing to either path.

---

## Prop Threading Plan

Current prop chain:
```
FilterTripsPage
  ├─ TripSearchFilters  ← NO setFilterData, NO handleOpenFilterDialog (must add)
  └─ TripSearchResults
       └─ TripsPageLayout
            ├─ FilterTrip sidebar  ← has setFilterData
            └─ FilteredTripList    ← NO setFilterData (read-only consumer)
```

**To add QuickFilterPills to TripSearchFilters — only 2 files change:**
1. `FilterTripsPage.js` lines 252-264: add `setFilterData={setFilterData}` + `handleOpenFilterDialog={handleOpenFilterDialog}` to `<TripSearchFilters>`
2. `TripSearchFilters.js`: destructure + pass to `<QuickFilterPills>`

**`handleOpenFilterDialog` guard** (FilterTripsPage.js line 168):
```js
const handleOpenFilterDialog = useCallback(
  () => tripsFilterSet?.operator_list?.length && setFilterDialogOpen(true),
  [tripsFilterSet]
);
```
Guard is falsy when data not loaded. Disable "Filters" pill button when guard is falsy.

---

## contractsToRender Data Shape

Flat array built in `FilteredTripList.js` lines 91-99:
```js
items?.flatMap(trip =>
  trip.contract.map(contract => ({
    ...contract,                    // all API contract fields
    tripId: trip.id,
    departureTime: trip.departure_time,  // hoisted from parent trip
    arrivalTime: trip.arrival_time,      // hoisted from parent trip
    route: trip.route,                   // hoisted from parent trip
    rate: Math.max(...contract.ratecard.map(i => i.selling_rate)),  // computed, not from API
  }))
)
```

`departure_time`, `arrival_time`, `route` are hoisted — available on each element.

---

## TripCard Props

```js
TripCard({
  departureTime: string,    // '08:00:00' — shows first 5 chars
  arrivalTime: string,      // '14:30:00'
  departureStation: string, // from contract.route.departure_station
  arrivalStation: string,   // from contract.route.arrival_station
  onTripClick: function,    // default: () => {}
  productSlug: string,
})
```
Pure presentation, no Redux, no hooks. Safe to reuse.

---

## BookButton Props

```js
BookButton({
  contract: object,      // REQUIRED
  departure_time: string,
  cartId: string,        // REQUIRED — validated: non-null, non-'null', typeof string
  bookingDate: string,   // 'YYYY-MM-DD'
  loginUserId: string,
  ADULT: number,
  CHILD: number,
  INFANT: number,
  total: number,
  disabled: boolean,
  redirect: boolean,
  onSuccess: function,
  buttonText: string,
  variant: string,
  showIcon: boolean,
  iconOnly: boolean,
})
```

**BookButton does NOT read Redux.** Only calls `useSession()` internally for email. `RecommendedTripCard` must own its own `useSelector` calls for cart + passenger data (same pattern as `TripItem`).

---

## Cold Start Sort Behavior

`sortContractsByScore` uses `parseFloat(a.score) || 0`. Score `null/undefined/0` → sorts to bottom. When all scores = 0, output order = V8 stable sort input order (API order). `RecommendedTripCard` should independently sort a spread-copy to derive recommended contract, regardless of current `filterData.sort`.

---

# UX/UI Design Spec

**Date:** 2026-06-14
**Scope:** `/trips/hatyai/koh-lipe`

---

## Recommended Trip Card

### Placement

Below filter strip, above first standard result. Page order:
1. SearchCover
2. Breadcrumb
3. TripProgressIndicator (round trips only)
4. TripSearchFilters (date strip + pills)
5. **Recommended Card** ← here
6. Standard TripItem list

Not before filters (loading sequencing + ad-like). Not sticky (z-index reserved for search header at z-20).

Only shows when `trips.length >= 2`. Single result = suppress card.

### Visual Treatment

- `UnifiedCard` wrapper
- Left accent: `border-l-2 border-[#3b5998]`
- Background: `bg-[#EFF6FF]` (brand.primaryLight token)
- Other 3 borders: unchanged `border-gray-200`
- Label: "Our Pick for This Route" — `text-xs font-medium text-[#3b5998]`
- No accordion — fully expanded by default

**Desktop:** External label sits above card, flush left, outside card boundary.
**Mobile:** Label collapses to full-width bar inside card top: `16px tall, px-3 py-1, bg-[#EFF6FF], text-[#3b5998], text-xs font-medium, border-l-2 border-[#3b5998]`

### Secondary Justification Line

Below operator name — data-conditional, priority order:
1. `average_rating >= 4.0` AND `booked_count >= 10` → "Rated [X] by [N] travellers"
2. `average_rating >= 4.0` only → "Rated [X] stars"
3. Neither → suppress entirely (no placeholder)

### Animation

Renders with results (not after). Fade-in 300ms `ease-in-out` same as other results. No separate entrance animation.

### New Operator State

Threshold: `score === 0 AND (average_rating === null OR === 0) AND (booked_count === null OR <= 10)`.
- Replace label with `BadgeChip type="status" variant="info"` → "New on SmartEnPlus"
- Suppress Trip Score
- Suppress justification line

### Edge Cases

| Case | Behavior |
|------|----------|
| `trips.length < 2` | Suppress card |
| All `score` fields null | Suppress card |
| Recommended trip filtered out by active filters | Suppress card |
| Score > 100 | Display "Trip Score 100/100", cap at 100 |
| Return trip step | Card reads from `filteredTrips` scoped to current step — correct without extra logic |

---

## Confidence Score Display

### Format

**"Trip Score [value]/100"** — text fraction, not ring/gauge.

- No SVG precedent in codebase
- Fraction format understood in SEA market (OTA standard)
- `contract.score` is nullable admin field — precise gauge format misleading

Label: **"Trip Score"** (not "Confidence", "Reliability", "Trust").
- "Reliability" implies on-time data that doesn't exist
- "Confidence" leaks internal vocab
- "Trip Score" = neutral, matches existing "Recommended" sort naming

### Placement

**Only on Recommended Card.** Not on every TripItem row — leaderboard effect removes decision incentive, increases cognitive load.

### Color Coding

- 80–100: `COLORS.status.success` `#10B981` (green)
- 50–79: `COLORS.status.warning` `#F59E0B` (amber)
- 1–49: **Hide Trip Score element entirely** — don't show red, undermines recommended card trust

Color applied as 8px filled dot preceding text. Text in `text-xs`.

### Mobile

Trip Score renders left of price in header row. If insufficient space on 375px → drops to second line below price, right-aligned. Never truncates mid-number.

---

## Quick Filter Pills

### Visual Style

Default: `px-3 py-1.5 border border-gray-300 bg-white text-gray-700 text-sm rounded-md min-h-[44px] md:min-h-0`

Active: `bg-[#3b5998] border-[#3b5998] text-white`

No emoji. No checkmark icon in active state. Filled background = sufficient active indicator.

### Pill Labels (MVP)

1. Fastest
2. Cheapest
3. Direct
4. Refundable
5. [FilterListIcon] Filters

**"Best Value" deferred** — no BestValue sort key in `sortingStrategies`. Adding pill for undefined key silently falls through to default sort.

### Placement

Merged with existing `TransportationOptionsFilter` into single scrollable row on desktop, separated by `1px solid #E5E7EB` vertical rule `h-4 mx-1`. Quick Filter Pills first, then transport type pills.

On mobile: two separate rows (single row too wide on 375px).

### Interaction Model

**Sort pills (mutually exclusive):** Fastest, Cheapest → write to `filterData.sort`. Selecting one deselects other.

**Filter pills (stackable):** Direct, Refundable → independently stackable. Both can be active simultaneously. Filter pill does not reset sort pill and vice versa.

Mobile sort dropdown and pills share `filterData.sort` — automatically in sync, no extra logic.

### Active State Reset

"Clear All" in `FilterTrip.js` dialog resets all pills. No standalone "Clear" in pill strip itself — avoids duplicate affordances.

### Direct Pill Gating

No direct trips → disabled state: `text-gray-400 border-gray-200 bg-gray-50 cursor-not-allowed opacity-50`
Tooltip: "No direct routes available for this date."
`aria-disabled="true"`, `tabIndex={-1}` when disabled.

**Disabled not hidden** — hiding confuses returning users.

Interim frontend detection: check `tripsFilterSet.unique_transport_composit_list` for any entry with `trasportation_com.length === 1`. Backend to add `has_direct_option: boolean` to TripFilter response.

### Refundable Pill Gating

Same disabled visual + tooltip: "No refundable options available for this route."

Writes to `filterData.conditions` using existing schema: `[{ extra_type: 'FEATURE', extra_name: 'Free Cancellation' }]`. Keeps pill + FilterTrip dialog in sync — same filter key.

Exact `extra_name` value must be confirmed with backend (dual cancellation model). Backend to add `has_refundable_option: boolean` to TripFilter + `is_refundable: boolean` per contract.

### Accessibility

- All pill buttons: `aria-pressed` reflecting active state (follow `TransportationOptionsFilter.js` `OptionButton` pattern exactly)
- Recommended card label: in card's accessible name or `aria-label`
- Disabled pills: `aria-disabled="true"`, `tabIndex={-1}`, tooltip via `aria-describedby` (not just `title` attr)

### Mobile Pill Scroll

`overflow-x-auto scrollbar-hide`. Copy drag-scroll gesture from `TransportationOptionsFilter.js` (`useRef + mousedown/mousemove/mouseup`) — not a simplified version.

---

# Phased Implementation Plan

**Phase 0: COMPLETE** — this document is the deliverable.

Backend work needed before Phases 4-6:
- `confidence_score` SerializerMethodField on ContractSerializer
- `_get_review_stats()` internal to avoid N+1
- `has_direct_option: boolean` on TripFilter response
- `has_refundable_option: boolean` on TripFilter + `is_refundable: boolean` per contract

Frontend phases (1 file per phase):

| Phase | Deliverable | Depends on |
|-------|-------------|-----------|
| 1 | `helpers/computeConfidenceScore.js` | Nothing (pure function, validated weights) |
| 2 | `TripsPageLayout.js` — remove sidebar | Nothing |
| 3a | `ResultsPageHeader.js` (create) | Nothing |
| 3b | `FilterTripsPage.js` — add ResultsPageHeader | Phase 3a |
| 4a | `DateStrip.js` (create) | Nothing |
| 4b | `TripSearchFilters.js` — **extend/wrap** SlideCalendar2 (NOT swap — see Audit C1) | Phase 4a |
| 5a | `QuickFilterPills.js` (create) | Nothing |
| 5b | `TripSearchFilters.js` + `FilterTripsPage.js` — add pills + prop threading | Phase 5a + backend `has_direct_option` |
| 6a | `RecommendedTripCard.js` (create) | Phase 1, backend `confidence_score` |
| 6b | `FilteredTripList.js` — extract recommended, render card | Phase 6a |
| 7 | Polish + vault report | All phases |

---

---

# Audit Corrections (2026-06-14)

3-agent code-truth audit (backend + frontend + UX) verified every factual claim against real code. **28/36 verified, 6 corrected.** Findings below override any conflicting statement earlier in this doc.

## CRITICAL

### C1 — SlideCalendar2 is LIVE (not commented out)
`components/search/SlideCalendar2.js`: lines 1-461 = old commented version, **lines 463-1036 = full live component** — `date-fns` 7-day (desktop) / 5-day (mobile) tab calendar, Redux `calendarActions` sync, URL `router.push`, return-trip date validation, MUI modal picker (`CalendarDatePickerv2`), Skeleton/Alert states.

**Impact:** Phase 4 cannot "swap / replace" it as an empty shell. DateStrip must **extend or wrap** the existing component, or carefully port its Redux-sync + URL-push + return-trip-validation. Blind replacement destroys date navigation, Redux calendar state, and return-trip validation for the entire trip search flow.

### C4 — `getTrustBadges` "Free Cancellation" is inverted-buggy
`helpers/getTrustBadges.js:18-20` pushes "Free Cancellation" when `refund_percentage === 0 || fixed_amount === 0`. `refund_percentage === 0` = NO refund (backwards). Correct check = `=== 100` (full refund).

**Impact:** Pre-existing codebase bug. Will show "Free Cancellation" on non-refundable trips, hide it on refundable ones. Do NOT use `getTrustBadges` for refundable signal on the recommended card. Use backend `is_refundable` field (already a backend prerequisite). Fix the helper separately before launch.

## MEDIUM

### M1 — Trip Score 1-49 third state was undefined
Spec covered ≥50 (show score) and score=0 new-operator (badge). The **1-49 range** (real score, below threshold, not new operator) was undefined — card would show "Our Pick" with no score and no badge.
**Resolution:** for 1-49, show justification line (rating/bookings) if available; if no supporting data, **suppress "Our Pick" label** and render as a normal top card (no elevated treatment).

### M3 — Header trust chips are hardcoded, not from `getTrustBadges`
`getTrustBadges` produces only: "Hotel Pickup", "Free Cancellation", "Instant Confirmation", "Top Rated", "No Hidden Fees". The Phase 3 header chips ("Guaranteed Connection / Secure Payment / 24/7 Support") are **hardcoded static strings**. Keep the two separate: header = static; card badges = `getTrustBadges` per-contract.

## MINOR (line-number precision)
- `'Fastest'` sort → `sortContractsByDuration` (duration-based proxy)
- Sort map in FilteredTripList = lines 105-116 (not 105-117)
- `average_rating`/`review_count`: declarations 265-266, method bodies 323-331 + 333-340
- `FilteredTripList` is `ssr:false` in `TripsPageLayout` but `ssr:true` in `pages/destinations/[slug].js` — not blanket client-only
- `ContractForFilterSerializer` fields = lines 942-946

## VERIFIED (no change)
All design tokens (`#10B981`, `#F59E0B`, `#EFF6FF`, `#3b5998`), `TOUCH_TARGET.minHeight=44px`, `Z_INDEX.sticky=20`, `BadgeChip` status/info, `filterData` shape, `setFilterData` full-replacement, `trasportation_com` typo + dual-key, `contractsToRender` flatMap, `BookButton` no-Redux, `TripCard` props, `sortContractsByScore` raw-score bug, `handleOpenFilterDialog` guard, prop-threading gap, dual cancellation model, all reuse targets exist.

---

## Related
- [[activities-sort-filter-ux]]
- [[sidebar-sticky-2col-responsive-grid]]
- [[adr-trip-confidence-score-algorithm-2026-06-14]]
- [[trip-search-results-implementation-plan-2026-06-14]]
- [[tour-system-status]]
- [[operators]]
