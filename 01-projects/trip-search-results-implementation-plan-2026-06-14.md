# Trip Search Results — Implementation Plan

> **Audited 2026-06-14** — 3-agent code-truth audit applied (🔴 AUDIT markers). **Phase 4 rewritten** (SlideCalendar2 is live). **Phase 6 fixed** (`getMainPrice` 5-arg, Trip Score 1-49, `getTrustBadges` bug).
> **Scrutinized 2026-06-14 (round 2)** — outsider end-to-end trace (🔵 SCRUTINY markers). 3 Phase-6 issues caught: S1 prop hoisting (`departureTime`→`departure_time` map), S2 "top 3" banner collision, S3 exact `getMainPrice` import recipe + `useMemo`. Phase 2 + 5 traced SAFE.

## Summary
7-phase frontend implementation of the Travel Decision Engine redesign. 1 file per phase. Phase 0 (analysis) complete. Backend work required before Phase 5 + 6.

## Status: Round 1 SHIPPED · Round 2 NEARLY DONE · Round Trip UX SHIPPED (2026-06-15)
- Phase 0: COMPLETE — vault design doc + ADR written + audited
- Round 1 (phases 3-7): SHIPPED + MERGED to `develop` 2026-06-14
- Round 2: P2 DONE · P1/P3/P4/P5/P7/P8/P9/P10 CUT · **P6 + P11 remaining**
- **Round Trip UX fixes: SHIPPED to `develop` 2026-06-15** — see section below

---

## ROUND 2 STATUS (2026-06-14) — supersedes original phasing

### Round 1 SHIPPED + MERGED to `develop`
FE `develop` @ `933b1b6`, BE `develop` @ `64a2fce`. ~40% of spec done:
- Phase 3: `ResultsPageHeader` (route title + count + trust chips)
- Phase 4: fare-calendar price badges on all date tabs (±7d, advance_hr-aware)
- Phase 5: `QuickSortPills` sort shortcuts
- Phase 6: Top Pick badge on #1 card
- Phase 7: design polish (outlined chips, brand-blue pills, badge in card)
- Bug fixes: advance_hr in FareCalendarViewSet, operator cheapest-wins dedup, min_display_rate (JOIN=ADULT / PRIVATE-CHARTER=VEHICLE), hydration quality, TRUST-BADGE-BUG (`refund_percentage===100`).

### Round 2 BACKEND RE-INVESTIGATION (corrects original "Backend Prerequisites" below)
Proper model+serializer read changed the feasibility map:
- **Route legs — NO BE NEEDED.** `Contract.timeline → TimeLineSerializer.timeline_place[]` ALREADY serialized in trips response: each stop has `title`, `time`, `order`, `icon` (Van/Ferry/Pier). Real stepwise path with real times. Just render it.
- **Confidence score — NO new BE.** `score`/`average_rating`/`review_count`/`booked_count` already serialized. `helpers/computeConfidenceScore.js` already computes 0-100.
- **Social proof — NO BE.** `booking_count_yesterday`/`booking_count_30d` already serialized. `Contract.booked_count` default=**10** is a seed → THIS is the cause of the FE `BookedCounter` `/10` hack. Fix = use real counts.
- **Trust badges — NO BE.** `getTrustBadges.js` reads existing `extra[]`/`cancellation_policies`/`instant_confirmation`/`transport_composit`.
- **Seats-available — 1 small BE method, real data.** `vehicle_seat` − confirmed `BookingItem` for `traveling_date`. Exact pattern exists: `TimeSlot.get_current_bookings(date)` (`operators/models.py:898`). Gated on passing `date` into serializer context cleanly.
- **On-time % — CUT.** No field/signal anywhere in models. Would be fake.

### Round 2 — Status updated 2026-06-15

| # | Phase | Status | Note |
|---|-------|--------|------|
| 1 | **RouteIntelligenceHero** | ~~NO NEED~~ — CUT | Photo hero (`SearchCover`) kept. Not replacing. |
| 2 | Remove desktop sidebar from `TripsPageLayout` | ✅ DONE | Confirmed in code — single-column, no `aside`. |
| 3 | Trip-count on active date tab | ~~NO NEED~~ — CUT | `N departures` already shown in `SearchCover` hero. Duplicate. |
| 4 | `ConfidenceScore.js` component | ~~NO NEED~~ — CUT | No consumer (P8 cut). If ever needed, inline 6 lines in `TripItem`. No new file. |
| 5 | `RouteTimeline.js` | ~~NO NEED~~ — CUT | `JourneyTimeline` exists but booking-detail scale. `TripItem` already has `TransportItems`. Third route repr = over-engineering. |
| 6 | Trip card upgrade: score+route+trust+price typography | pending | Needs scoping — most already in `TripItem` |
| 7 | Fix `BookedCounter` `/10` → real counts | ~~NO NEED~~ — CUT | `booked_count` default=10 seed makes real counts misleading. |
| 8 | `RecommendedTripCard.js` | ~~NO NEED~~ — CUT | Top Pick badge (Round 1) sufficient. |
| 9 | `TravelInsight.js` + `getRouteInsight.js` | ~~NO NEED~~ — CUT | No API field backs this. Fake data / hardcoded strings = no fake metrics rule. |
| 10 | `seats_available` BE + "N seats left" FE | ~~NO NEED~~ — CUT | Deferred indefinitely. BE complexity not justified now. |
| 11 | SEO content order check | pending | Quick grep, non-destructive |

**Remaining:** P6 (needs scoping), P11 (quick check)
**Cut:** P1, P3, P4, P5, P7, P8, P9, P10

**Principles:** reuse-first, no tech debt, no fake metrics, small components.

---

### PHASE 1 — RouteIntelligenceHero FINAL SPEC (screenshot-validated 2026-06-14)

Live screenshot confirmed photo hero eats entire first screen (~540px before results). Spec accepted with 3 refinements + overlap resolution.

**New `components/trips/RouteIntelligenceHero.js`** — gradient (ocean-blue→seafoam), NO photo, 180px desktop / 140px mobile (max 220px):
- Back + Share row (reuse existing).
- **Leg badge** (round trip): `[OUTBOUND JOURNEY]` blue / `[RETURN JOURNEY]` green; none for one-way. From `isReturnJourneyActive` + `tripModeDisplay`.
- **Route title** active direction — return SWAPS to `Koh Lipe → Hat Yai` (like `activeFrom/activeTo`).
- **Stats:** `From ฿N` · duration RANGE `4h30m–6h` (never average) · `N departures` · `First HH:MM · Last HH:MM`.
- **Edit Search** trigger + passenger chip (reuse `SearchDialogTrigger` + passenger modal; NO inline form).
- < 200 lines.

**3 refinements from screenshot review:**
1. **ADD First/Last departure** — `Math.min/max(trip.departure_time)`. Real, cheap, genuine route intelligence.
2. **"From ฿N" must match bookable cards** — use advance_hr-filtered `min_display_rate` (same set as cards). Screenshot: cards ฿1,000 / strip ฿990 while a ฿700 contract was advance_hr-excluded → hero must NOT advertise unbookable ฿700.
3. **DROP "today"** — show `N departures` or `N departures on 16 Jun` (date-scoped, not literal today).

**Overlap resolution:** Hero owns route identity + stats. `ResultsPageHeader` reduces to **trust-chip row only** (drop duplicate "Hatyai → Koh Lipe · N departures"). Folded into Phase 2.

**CUT from hero (3-agent review consensus):** confidence score (no on-time/transfer data), trust badges (per-contract → card-level), travel insight (fake data), most-popular-departure (cold query, deferred).

**BLOCKED (separate track):** hero route viz — `Contract.timeline` per-contract, no canonical route path. Needs product/BE selection-rule decision.

**Files:** new `components/trips/RouteIntelligenceHero.js`; `FilterTripsPage.js` (swap `DynamicSearchCover`→hero, pass trips-derived stats); `ResultsPageHeader.js` (→chips only, Phase 2). Keep `SearchCover`/`FeaturedImageHeader` untouched (homepage/other pages).

**3-agent review record (2026-06-14):** FE-arch + UX + BE-data. Consensus: route viz blocked (per-contract timeline), confidence/trust/insight cut (no data / per-contract / fake), real route-level data = price + count + duration-range. New component not edits (SearchCover at 220-line limit, FeaturedImageHeader carries dead image machinery).

---

---

## Round Trip UX Fixes — SHIPPED 2026-06-15

4 commits on `develop`. FE `develop` @ `a3c328a`.

### Problems fixed

**1. `TripProgressIndicator` caused vertical stack bloat**
- Was a full card (`bg-white border shadow rounded-lg p-3`) = 44px of vertical space for 3 dots + label
- Grill+scrutinize debate: collapse into breadcrumb row (same horizontal line, right-aligned)
- Result: −44px before calendar on both desktop and mobile
- Files: `FilterTripsPage.js` + `TripProgressIndicator.js`
- Commits: `51dd135` (width fix) · `da00290` (collapse into breadcrumb row) · `53a85cc` (restore mobile icons)

**2. Hero showed wrong route during return step**
- `SearchCover` always received `fromSearch`/`toSearch` (URL slug, never reversed)
- During return step, trips fetched were `Koh Lipe → Hatyai` but hero showed `Hatyai → Koh Lipe`
- Fix: pass `activeFrom`/`activeTo` — swap props when `isReturnJourneyActive`
- `SearchCover` sets display state from props (not Redux) → Redux untouched, edit-search works correctly
- File: `FilterTripsPage.js:211-212`
- Commit: `a3c328a`

**3. Width inconsistency on `TripProgressIndicator`**
- Old: `md:mx-3` only — missing `mx-2` (mobile) and `xl:mx-0` (wide desktop)
- Sibling pattern: `mx-2 md:mx-3 xl:mx-0` (from `SlideCalendar2`, `QuickSortPills` row)
- Also: conflicting `px-2 md:px-0` wrapper div in `FilterTripsPage` fighting component's own margin
- Fix: align to sibling pattern, remove wrapper div
- Commit: `51dd135`

**4. Review label visible on desktop + mobile simultaneously**
- `"Review & Pay"` span missing `md:hidden` — showed alongside `"Review Booking & Proceed to Payment"` on desktop
- Fix: add `md:hidden` to match outbound/return label pattern
- Commit: `51dd135`

### New `TripProgressIndicator` design

Mobile: icon (arrow/grid/cart) + step counter `1/3` — inline right side of breadcrumb row  
Desktop: filled dots `●●○` + label text — inline right side of breadcrumb row  
No card chrome. No separate section. Zero added vertical space.

### Decisions NOT implemented (debated + rejected)

| Proposal | Rejected reason |
|---|---|
| `SelectedOutboundSummary` card (outbound trip details during return step) | Reverted — user requested redesign first. Data source confirmed: `useCheckCartIdQuery → cart_item[0].contract.trip.{route_route,departure_time,traveling_date}`. Ready to implement when UX direction confirmed. |
| "RETURN DATE" label on `SlideCalendar2` | Deferred with summary card — both are return-step context improvements |
| Airline-style stepper rebuild (`✓────●`) | Cut — cosmetic only, current dots already communicate progress |
| Hero "Step 2 of 2" | Cut — codebase is 3-step model. "2 of 2" would break review step |

### Open: `SelectedOutboundSummary`

When ready to implement:
- Gate: `routeParams.isReturnJourneyActive && routeParams.isReady`
- Insert: `FilterTripsPage.js` between `TripProgressIndicator` row and `TripSearchFilters`
- Data: `useCheckCartIdQuery({ cartId })` → `cart_item.find(i => i.contract?.trip?.departure_time)`
- Fields: `item.contract.trip.route_route`, `item.traveling_date`, `item.contract.trip.departure_time`
- Formatters: `formatDate` from `helpers/formatDate.js`
- States: `!cartId` → null | loading → skeleton `h-16 animate-pulse` | no item → null | success → green card
- Same component mobile + desktop (no separate layout)

---

## Related Vault Docs
- [[trip-search-results-redesign-2026-06-14]] — full 3-agent analysis (UX/UI + backend + frontend arch)
- [[adr-trip-confidence-score-algorithm-2026-06-14]] — formula decision + rationale

---

## Backend Prerequisites (before Phase 5 + 6)

| Item | File | Effort |
|------|------|--------|
| `confidence_score` SerializerMethodField on ContractSerializer | `products/serializers.py` | Medium |
| `_get_review_stats()` shared internal (avoid 3rd N+1) | `products/serializers.py` | Small |
| `has_direct_option: boolean` on TripFilter response | `products/views.py` lines 1620-1642 | Small |
| `has_refundable_option: boolean` on TripFilter | `products/views.py` | Small |
| `is_refundable: boolean` per contract in TripFilter results | `products/serializers.py` | Small |
| Document `score` as admin visibility lever, set to 50 on onboarding | Ops process | Zero code |

---

## Phase 0.5 — Pre-flight Fixes (UNBLOCKED — do FIRST)

> No dependencies. Two independent 1-line bug fixes that unblock Phase 6 trust signals and Phase 1 sort correctness.

### Step A — Fix `getTrustBadges` Free-Cancellation (TRUST-BADGE-BUG)

**File:** `helpers/getTrustBadges.js` line 19

Current (buggy):
```js
cancelDetails.some(d => d?.refund_percentage === 0 || d?.fixed_amount === 0)
```
Fix:
```js
cancelDetails.some(d => d?.refund_percentage === 100)
```

**Verify:** Contract with `refund_percentage=100` shows "Free Cancellation". Contract with `refund_percentage=0` does NOT.

### Step B — Fix `sortContractsByScore` to use `confidence_score`

**File:** `helpers/tripSorting.js` lines 7-13

Current (sorts on raw admin `score` field — mostly null):
```js
const scoreA = parseFloat(a.score) || 0;
const scoreB = parseFloat(b.score) || 0;
```
Fix:
```js
const scoreA = parseFloat(a.confidence_score || a.score) || 0;
const scoreB = parseFloat(b.confidence_score || b.score) || 0;
```

**Verify:** Recommended sort picks contract with highest `confidence_score` when backend field present; falls back to `score` otherwise.

✋ **USER CHECK:** Test both helpers in browser. Confirm Free-Cancellation badge appears/disappears correctly.
📦 **SESSION HANDOFF:** Run `/wrapup` → update master-state.md "Phase 0.5 DONE".

---

## Phase 1 — Confidence Score Helper

**File:** `helpers/computeConfidenceScore.js` (CREATE, ~25 lines)

Pure function, no imports, no side effects.

```js
export const computeConfidenceScore = (contract) => {
  const rating   = ((contract?.average_rating || 0) / 5) * 0.45;
  const reviews  = Math.min((contract?.review_count || 0) / 50, 1) * 0.25;
  const popular  = Math.min((contract?.booked_count || 0) / 500, 1) * 0.20;
  const bonus    = ((contract?.confidence_score || contract?.score || 0) / 100) * 0.10;
  return Math.round((rating + reviews + popular + bonus) * 100);
};
```

Uses backend `confidence_score` if present, falls back to raw `score`.

**Verify:** `computeConfidenceScore({})` returns 0. `computeConfidenceScore(null)` returns 0.

✋ **USER CHECK:** Run `computeConfidenceScore({})` in browser console → must return 0.
📦 **SESSION HANDOFF:** Run `/wrapup` → update master-state.md "Phase 1 DONE".

---

## Phase 2 — Remove Desktop Sidebar

**File:** `components/itinerary/TripsPageLayout.js` (MODIFY)

Remove `<aside className='hidden md:block md:w-[288px]'>` block containing `FilterTrip`. Single-column wrapper only. Sidebar → drawer only (already working via `isFilterDialogOpen`).

**Verify:** Page loads at `/trips/hatyai/koh-lipe`. Mobile filter dialog still opens.

✋ **USER CHECK:** Visit `/trips/hatyai/koh-lipe` on desktop (no sidebar) and mobile (drawer opens). Confirm layout correct.
📦 **SESSION HANDOFF:** Run `/wrapup` → update master-state.md "Phase 2 DONE".

---

## Phase 3 — Compact Header

**Files:**
- CREATE: `components/trips/ResultsPageHeader.js` (~80 lines)
- MODIFY: `components/trips/FilterTripsPage.js` (~5 line diff)

`ResultsPageHeader` props: `fromLocation`, `toLocation`, `date`, `departureCount`

Layout:
- Line 1: `"Hat Yai → Koh Lipe"` — `text-lg font-semibold`
- Line 2: `date | N departures` — `text-sm text-gray-600`
- Trust row: 4 `BadgeChip` chips — "Instant Confirmation", "Guaranteed Connection", "Secure Payment", "24/7 Support"
  - 🔴 AUDIT (M3): these 4 are **hardcoded static strings**, NOT from `getTrustBadges`. `getTrustBadges` only outputs "Hotel Pickup / Free Cancellation / Instant Confirmation / Top Rated / No Hidden Fees" and is per-contract. Header = static. Don't conflate.
- Use `COLORS` from `helpers/designSystem.js`

Wire into `FilterTripsPage.js` above `<TripSearchFilters>`. Props from existing: `fromSearch`, `toSearch`, `effectiveDepartureDate`, `contracts.length`.

**Verify:** Header renders. Trust chips visible on mobile.

✋ **USER CHECK:** Header renders on `/trips/hatyai/koh-lipe`. 4 trust chips visible on mobile.
📦 **SESSION HANDOFF:** Run `/wrapup` → update master-state.md "Phase 3 DONE".

---

## Phase 4 — Date Strip Fare Badge (LOCKED: Option A — Audit C1)

> 🔴 **AUDIT C1 — DO NOT REPLACE SlideCalendar2.** `components/search/SlideCalendar2.js` lines 463-1036 is a **full live component**: `date-fns` 7-day (desktop) / 5-day (mobile) tab calendar, Redux `calendarActions` sync, URL `router.push`, return-trip date validation, MUI modal picker (`CalendarDatePickerv2`), Skeleton/Alert. Lines 1-461 are old commented code. Blind replacement destroys date nav + Redux calendar state + return-trip validation for the whole search flow.

**Decision LOCKED 2026-06-14: Option A chosen.**

**Option A (recommended): Add fare badge to existing SlideCalendar2.**
- The "cheapest fare per day" is the ONLY net-new behavior in the vision. SlideCalendar2 already does the 7-day strip + nav + Redux + validation.
- MODIFY `components/search/SlideCalendar2.js` (live section): add a fare badge slot on the active tab showing `formatCurrency(minRate)` from `tripsFilterSet.min_rate` (via `useCurrency` for rate).
- No new DateStrip component. Smallest diff, zero regression risk to date nav.
- Per-day fares for non-active days = deferred (needs extra API calls).

**Option B: New DateStrip wrapping SlideCalendar2 behavior.**
- Only if Option A proves too coupled. DateStrip must port: Redux `calendarActions` sync, URL `router.push` with date param, return-trip date validation, mobile/desktop day count. ~250+ lines, high regression risk. Not recommended.

**Files (Option A):**
- MODIFY: `components/search/SlideCalendar2.js` — add active-day fare badge (~15 line diff)

**Verify:** Date nav still works (forward/back, tab select). Return-trip validation intact. Redux calendar state syncs. Active day shows fare. `npm run build` passes.

✋ **USER CHECK:** Click forward/back dates. Redux calendar state syncs. Return-trip validation intact. Active day shows fare.
📦 **SESSION HANDOFF:** Run `/wrapup` → update master-state.md "Phase 4 DONE".

---

## Phase 5 — Quick Filter Pills

> **Requires:** `has_direct_option` + `has_refundable_option` from backend.
> Interim: derive Direct client-side from `unique_transport_composit_list`.

**Files:**
- CREATE: `components/trips/QuickFilterPills.js` (~100 lines)
- MODIFY: `components/trips/TripSearchFilters.js` (~20 line diff)
- MODIFY: `components/trips/FilterTripsPage.js` (~5 line diff)

`QuickFilterPills` props: `filterData`, `setFilterData`, `tripsFilterSet`, `onOpenFilters`

| Pill | Action | Active when |
|------|--------|-------------|
| Fastest | `setFilterData(prev => ({...prev, sort: 'Fastest'}))` | `filterData.sort === 'Fastest'` |
| Cheapest | `setFilterData(prev => ({...prev, sort: 'Cheapest'}))` | `filterData.sort === 'Cheapest'` |
| Direct | set `filterData.transportOptions` to single-leg entries from `unique_transport_composit_list` | has single-leg entries in transportOptions |
| Refundable | set `filterData.conditions` to `[{ extra_type: 'FEATURE', extra_name: 'Free Cancellation' }]` | conditions contains free cancel |
| [FilterListIcon] Filters | `onOpenFilters()` | never |

> 🔴 AUDIT C4 — Refundable detection: do NOT rely on `getTrustBadges` (its Free-Cancellation check is inverted-buggy, `refund_percentage === 0`). The `filterData.conditions` FEATURE-extra approach only works if admin created a matching Extra item. Reliable source = backend `is_refundable` per contract (backend prerequisite). Confirm exact `extra_name` with backend before coding.

> 🔴 AUDIT M2 — Disabled-not-hidden is **net-new**. Existing `TransportationOptionsFilter.js:126` HIDES empty options (`return null`), no disabled state in codebase. No reference impl to copy — the disabled styling + `aria-disabled` + `tabIndex={-1}` below is all new code. Decision stands (disabled = better UX for returning users), just no copy source.

Disabled state (Direct/Refundable when unavailable): `text-gray-400 border-gray-200 bg-gray-50 cursor-not-allowed opacity-50 aria-disabled tabIndex={-1}`

Sort pills = mutually exclusive. Filter pills = stackable.

Style (plain `<button>`, no emoji, no `BadgeChip`):
- Default: `px-3 py-1.5 border border-gray-300 bg-white text-gray-700 text-sm rounded-md min-h-[44px] md:min-h-0`
- Active: `bg-[#3b5998] border-[#3b5998] text-white`

`FilterTripsPage.js` changes: thread `setFilterData` + `handleOpenFilterDialog` → `TripSearchFilters`. Guard: disable Filters pill when `!tripsFilterSet?.operator_list?.length`.

`TripSearchFilters.js` changes: add `<QuickFilterPills>` below date strip, remove mobile-only sort dropdown.

**Verify:** Pills render. Sort pills change trip order. Direct disables when no direct trips. Filters pill opens FilterTrip drawer.

✋ **USER CHECK:** Pills render. Sort pills change trip order. Direct pill disables when no direct trips. Filters pill opens drawer.
📦 **SESSION HANDOFF:** Run `/wrapup` → update master-state.md "Phase 5 DONE".

---

## Phase 6 — Recommended Trip Card

> **Requires:** Backend `confidence_score` field on contracts.
> Interim: use `computeConfidenceScore()` from Phase 1.

**Files:**
- CREATE: `components/trips/RecommendedTripCard.js` (~150 lines)
- MODIFY: `components/trips/FilteredTripList.js` (~40 line diff)

`RecommendedTripCard` props: `contract`, `departure_time`, `arrival_time`, `route`, `dateTrip`

> 🔵 SCRUTINY S1 — Data path: the recommended contract is one element of `contractsToRender`, which **hoists** camelCase fields onto each contract (`FilteredTripList.js:95-97`: `contract.departureTime`, `.arrivalTime`, `.route`). Caller MUST map them: `departure_time={recommendedContract.departureTime}`, `arrival_time={recommendedContract.arrivalTime}`, `route={recommendedContract.route}`. Same mapping `TripItem` gets at `FilteredTripList.js:130-133`. Without the camelCase→snake_case map, the card receives `undefined`.

Internal Redux (same pattern as `TripItem`):
```js
const { cartId } = useSelector(state => state.cart);
const { adult: ADULT, children: CHILD, infant: INFANT, total } = useSelector(state => state.passenger);
const { id: loginUserId } = useSession() ?? {};
```

Visual spec:
- Wrapper: `<UnifiedCard hover={false}>` + `border-l-2 border-[#3b5998] bg-[#EFF6FF]`
- Desktop: "Our Pick for This Route" label above card (external, flush left)
- Mobile: label as full-width bar inside card top (`px-3 py-1 bg-[#EFF6FF] text-[#3b5998] text-xs font-medium border-l-2 border-[#3b5998]`)
- Trip Score: 3 states (🔴 AUDIT M1 — 1-49 state added):
  - `>= 50`: show "Trip Score X/100" — green dot `#10B981` if ≥80, amber `#F59E0B` if 50-79, `text-xs`
  - `1-49` (real score, below threshold, NOT new operator): **suppress "Our Pick" label**, render as normal top card (no elevated treatment). Show justification line if rating/bookings available. Do NOT show "Our Pick" with a hidden score — confusing.
  - `0` + new operator: see new-operator state below
- Route viz: reuse `TripCard` — pass `contract.route.departure_station` + `.arrival_station`
- Price (🔴 AUDIT C3 + 🔵 SCRUTINY S3 — exact recipe from `TripItem.js`): → `text-2xl sm:text-4xl font-bold`
  ```js
  import { getMainPrice } from '../../helpers/getMainPrice';
  import { getMaxRate } from '../../helpers/getMaxRate';
  import { customSortData } from '../../helpers/formatDate';   // NOTE: from formatDate, not its own file
  import { useCurrency } from '../contexts/CurrencyContext';
  // ...
  const { currentRate, loading } = useCurrency();
  const mainPrice = useMemo(
    () => getMainPrice(contract, currentRate, formatCurrency, customSortData, getMaxRate),
    [contract, currentRate]
  );  // formatCurrency comes from useCurrency() too — confirm in CurrencyContext
  ```
  - Verbatim copy of `TripItem.js:334`. Calling `getMainPrice(contract)` alone returns `"N/A"`. All 5 args required.
- Trust signals: `getTrustBadges(contract, { includeTopRated: true })` → `✓ text` list
  - 🔴 AUDIT C4 — `getTrustBadges` "Free Cancellation" output is buggy (`refund_percentage === 0` = no refund). EXCLUDE "Free Cancellation" from displayed trust signals until helper fixed, OR use backend `is_refundable`. Other badges (Hotel Pickup, Instant Confirmation, Top Rated, No Hidden Fees) are fine.
- Social proof (data-conditional, priority order):
  1. `booking_count_yesterday > 0` → "X bookings today"
  2. `booking_count_30d > 0` → "~X bookings/day avg"
  3. Neither → suppress
- CTA: `<BookButton contract={contract} departure_time={departure_time} cartId={cartId} bookingDate={dateTrip} loginUserId={loginUserId} ADULT={ADULT} CHILD={CHILD} INFANT={INFANT} total={total} />`

New operator state (`score=0 AND rating=0 AND booked_count≤10`):
- Replace label → `BadgeChip type="status" variant="info"` — "New on SmartEnPlus"
- Hide Trip Score, hide social proof

DO NOT show: "12 seats left", "98% On-Time" — fields don't exist in API.

`FilteredTripList.js` changes:
```js
const recommendedContract = useMemo(() =>
  contractsToRender.length >= 2
    ? [...contractsToRender].sort((a, b) =>
        (b.confidence_score || b.score || 0) - (a.confidence_score || a.score || 0)
      )[0]
    : null,
  [contractsToRender]
);

const mainList = recommendedContract
  ? contractsToRender.filter(c => c.id !== recommendedContract.id)
  : contractsToRender;
```

Render `<RecommendedTripCard>` above `mainList.map(...)`. Hide if `recommendedContract === null`.

> 🔵 SCRUTINY S2 — Existing "top 3" banner collision: `FilteredTripList.js:138-145` injects a banner after `index === 2` ("You've seen the top {sort} 3 options"). Once the recommended trip is pulled out, the `.map` runs over `mainList` (list minus #1), so:
> - Keep the `index === 2` math relative to `mainList` (banner appears after the 3rd remaining trip).
> - **Update copy** from `You've seen the top ${filterData?.sort} 3 options...` to `"You've seen the top picks — scroll for more"`. The old "top 3" count is wrong once the recommended card sits above the list.

**CRITICAL:** Spread-copy before sort — never mutate `contractsToRender` in-place. (The existing `sortContractsBy*` helpers mutate via `.sort()` — `helpers/tripSorting.js:8`. The `[...contractsToRender]` spread in the recommended extraction is mandatory, else the main list order is corrupted.)

**Verify:** Card appears above list. Contract absent from main list. Book Now works. Confidence score displays. New operator state shows correct badge.

✋ **USER CHECK:** Recommended card above list. Contract absent from main list. Book Now works. Score displays.
📦 **SESSION HANDOFF:** Run `/wrapup` → update master-state.md "Phase 6 DONE".

---

## Phase 7 — Polish + Verification

Full check at `http://localhost:3000/trips/hatyai/koh-lipe`:

| # | Check |
|---|-------|
| 1 | Compact header: route name, date, count, trust chips |
| 2 | Date strip: active day highlighted, click navigates to new URL |
| 3 | Filter pills: Fastest/Cheapest change sort order |
| 4 | Direct pill: disabled when no direct trips available |
| 5 | Filters pill: opens existing FilterTrip drawer |
| 6 | Recommended card: above list, score, Book Now functional |
| 7 | Recommended contract: absent from main list |
| 8 | Mobile: no sidebar, pills horizontal scroll, drawer opens |
| 9 | FilterTrip drawer: unchanged, all filters still work |
| 10 | `npm run build` passes — no errors |

✋ **USER CHECK:** All 10 checklist items pass. `npm run build` exits 0.
📦 **SESSION HANDOFF:** Run `/wrapup` → mark TRIP-SEARCH-REDESIGN COMPLETE in master-state.md. Close branch.

---

## Reuse Checklist

| Feature | Component / Helper |
|---|---|
| Trust chips in header | `BadgeChip` — `components/UI/BadgeChip.js` |
| Card wrapper | `UnifiedCard` — `components/UI/UnifiedCard.js` |
| Trust badge strings | `getTrustBadges` — `helpers/getTrustBadges.js` (⚠️ Free-Cancellation buggy, see gotcha 8) |
| Price | `getMainPrice(contract, currentRateObj, formatFn, sortFn, getMaxFn)` — `helpers/getMainPrice.js` (⚠️ 5 args) |
| Route display | `TripCard` — `components/trips/TripCard.js` |
| Book button | `BookButton` — `components/UI/BookButton.js` |
| Sort | `sortContractsByScore` — `helpers/tripSorting.js` |
| Filter state shape | `filterData` from `hooks/useTripFilters.js` |
| Drag scroll pattern | `TransportationOptionsFilter.js` — copy mousedown/mousemove |
| Design tokens | `COLORS`, `BORDER_RADIUS_CLASSES` — `helpers/designSystem.js` |

---

## Key Gotchas for Audit Team

> All claims below code-truth verified 2026-06-14. 🔴 = audit correction overriding an earlier wrong claim.

1. **`trasportation_com` typo** — load-bearing (missing 'n'). Backend view line 1515 + `FilteredTripList.js` line 53. Dual-key pattern: `option?.transportation_com || option?.trasportation_com` ✓ VERIFIED
2. **`setFilterData` = full replacement** — always `prev => ({ ...prev, field: val })` spread. Direct `setFilterData({ sort: 'X' })` wipes all filters. ✓ VERIFIED
3. **`BookButton` does NOT read Redux** — only `useSession()`. All cart + passenger via props. ✓ VERIFIED
4. 🔴 **`FilteredTripList` SSR is per-import-site** — `ssr:false` in `TripsPageLayout` (search page), but `ssr:true` in `pages/destinations/[slug].js`. NOT blanket client-only. RecommendedTripCard is client-only in the search-page path.
5. **`contract.rate` is computed, not from API** — `FilteredTripList.js:91-99` adds via `Math.max(...ratecard.map(i => i.selling_rate))`. ✓ VERIFIED
6. 🔴 **`SlideCalendar2` is LIVE, NOT commented out** — lines 463-1036 full live component (Redux sync, URL push, return-trip validation, modal picker). The "renders nothing / safe to replace" claim was WRONG. See Phase 4 (rewritten) — extend, don't replace.
7. **`handleOpenFilterDialog` guard** — falsy when `!tripsFilterSet?.operator_list?.length`. Disable Filters pill until loaded. ✓ VERIFIED
8. 🔴 **`getTrustBadges` Free-Cancellation is inverted-buggy** — `helpers/getTrustBadges.js:19` checks `refund_percentage === 0` (= NO refund), should be `=== 100`. Will mislabel non-refundable trips. Exclude from card trust signals or fix helper first.
9. 🔴 **`getMainPrice` needs 5 args** — `getMainPrice(contract, currentRateObj, formatCurrencyFunc, customSortDataFunc, getMaxRateFunc)`. One-arg call returns `"N/A"`.
10. 🔴 **`RecommendationViewSet` exists** (`products/views.py:1685`, `GET /api/v1/recommendations/<contract_id>/`) — but it's cross-sell (related products from a contract), NOT search-results ranking. Audit it for reusable scoring before building `confidence_score`. Does not replace the search-results sort.

## Audit + Scrutiny Stamp
**Round 1 — Audited 2026-06-14** — 3-agent code-truth (backend + frontend + UX). 28/36 claims verified, 6 corrected (2 critical: SlideCalendar2 live, getTrustBadges bug). Applied inline (🔴) + design doc "Audit Corrections" + ADR "Rejected Alt B".

**Round 2 — Scrutinized 2026-06-14** — outsider end-to-end code trace. 3 new Phase-6 issues (🔵 S1/S2/S3), 2 areas traced SAFE (Phase 2 dialog, Phase 5 handler). All applied inline.

**Round 3 — Re-prioritized 2026-06-14** — Phase 0.5 (pre-flight fixes) added. Phase 4 locked to Option A. Session handoff gates added to all phases. Step atomization: 9 steps total (0.5A, 0.5B, 1, 2, 3a, 3b, 4, 5, 6, 7).

**Net implementer risk now:** Phase 6 is the highest-touch phase (prop mapping, banner copy, 5-arg price, 3-state score, getTrustBadges exclusion). Phase 4 locked to Option A (~15 line diff). Everything else is low-risk with verified reuse targets.
