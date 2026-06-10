# Implementation Plan — Cross-Sell Quick Wins
## Date: 2026-06-09 | Team: UX + Frontend + Backend + Scrutinizer

---

## Summary

4-agent review (UX/UI + Frontend Engineer + Backend Verifier + Design Scrutinizer) of the priority list from `next-priority-debate-2026-06-09.md`. Result: 2 blockers found, 1 claim confirmed stronger than stated, concrete line-level specs for all changes.

---

## Scrutiny Results — What the PM Debate Got Right/Wrong

| Claim | Status | Finding |
|-------|--------|---------|
| CheckoutRelatedTrips = 1 import + 1 JSX line | **CHALLENGED** | Mobile sidebar (`CheckOutSideBar.js`) is a separate component — 2 touch points, not 1 |
| RelatedExperiences swap = 0–1 days | **CHALLENGED** | `contractId` not a current prop; response shape change (`.map(r => r.contract)` unwrap required); 1–2 days honest |
| item_category = 3-line change | **CONFIRMED STRONGER** | Actually 1 line, not 3. `contract.service_category` confirmed present at `useOmisePayment.js:56` via 3 independent call sites |
| Post-booking multi-item fix = safe 1–2 days | **BLOCKED** | `analyzeBookingContext` is architecturally single-booking; multi-item orders silently return null today; fix requires query-layer redesign |
| Journey builder gate to Q4 | **CONFIRMED** | No code exists at all — greenfield; gate correctly set |

**Critical miss the team didn't catch:** `CheckoutRelatedTrips.js:38` reads `cartItems?.[0]?.contract_id` (flat snake_case). Must verify this field exists on the cart item shape at runtime — if missing, component silently skips query and renders nothing (invisible failure in manual testing).

---

## Priority 1 — GTM item_category

**Status: GREEN — ship immediately**

### Change
**File:** `hooks/useOmisePayment.js` line 56–59

```js
// BEFORE
const tripItems = useMemo(() => (
    trips.map(({ trip: { contract } }) => ({
        item_id: contract.id,
        item_name: contract.name,
    }))
), [trips]);

// AFTER
const tripItems = useMemo(() => (
    trips.map(({ trip: { contract } }) => ({
        item_id: contract.id,
        item_name: contract.name,
        item_category: contract.service_category,
    }))
), [trips]);
```

### Verification
`contract.service_category` confirmed present via:
- `TotalCartSummary.js:17-19` reads `item?.contract?.service_category`
- `capacityValidationHelper.js:46` reads `contract.service_category`
- Backend: `carts/serializers.py:76` includes `service_category` in `ContractSerializer.fields`

### Definition of Done
GA4 ecommerce reports show `item_category` field populated on next purchase event. Revenue breakdown by `DAY_TOUR` vs transport now possible.

---

## Priority 2 — Mount CheckoutRelatedTrips

**Status: YELLOW — ship with UX changes + mobile decision**

### UX Issues Found (must address before shipping)
1. **Collapsed-by-default kills conversion.** Component starts `collapsed={true}` → `useState(false)`. On desktop where space exists, collapsed = invisible. Fix: `collapsed={false}` on desktop, or keep collapsed only on mobile.
2. **RecommendationCard too data-dense for sidebar.** Card was designed for 4-column grids — renders ratecard table, operator logo, station names, duration, rating, reason text in a ~300px sidebar. Needs a simplified variant or `showBadges={false}` at minimum (already passed).
3. **contracts[0] single-seed is a UX risk.** Multi-item carts see recommendations seeded from first item only — irrelevant for multi-leg trips. Degrades trust at payment moment.

### Change — Desktop Sidebar
**File:** `components/checkout/CheckoutSidebar.js`

```js
// ADD after line 5 (imports)
import CheckoutRelatedTrips from '../recommendations/CheckoutRelatedTrips';
```

```jsx
// ADD after </TotalCartSummary> closing tag (line ~77), inside flex flex-col gap-3 div
<CheckoutRelatedTrips cartItems={items} collapsed={false} />
```

### Change — Mobile Sidebar (separate decision)
**File:** `components/forms/checkout/CheckOutSideBar.js`
- Mobile sidebar is `DynamicCheckOutSideBar`, completely separate from `CheckoutSidebar`
- `cartItems` prop already passed from `index.js:1096`
- Requires same import + JSX addition if mobile parity desired
- **Recommendation:** skip mobile for v1 — sidebar stacks below payment CTA on mobile, near-zero visibility anyway

### Verify Before Shipping
Confirm `cart_item[].contract_id` flat field exists in cart API response. Check `BookButton.js:191` — writes `contract_id: id` on add-to-cart. If present in API response, component works. If missing, `firstContractId` is `undefined` → query skipped → renders nothing (silent failure).

### Definition of Done
`checkout_recommendation_view` GTM event fires on checkout page load. `checkout_recommendation_click` fires on card click. At least 1 recommendation visible above the fold in desktop sidebar.

---

## Priority 3 — Wire RelatedExperiences to Scored API

**Status: YELLOW — 1–2 days, not 0–1**

### Change — RelatedExperiences.js
**File:** `components/activities/detail/RelatedExperiences.js`

```js
// BEFORE
import { useGetContractsQuery } from '../../../store/api/dayTripsApi';

export default function RelatedExperiences({ serviceCategory, currentSlug }) {
  const { data, isLoading } = useGetContractsQuery(
    { serviceCategory, pageSize: 4 },
    { skip: !serviceCategory }
  );

  const related = (data?.results || [])
    .filter((c) => c.slug !== currentSlug)
    .slice(0, 3);

// AFTER
import { useGetRecommendationsQuery } from '../../../store/api/recommendationsApi';

export default function RelatedExperiences({ contractId, currentSlug }) {
  const { data, isLoading } = useGetRecommendationsQuery(
    { contractId, type: 'similar', limit: 4 },
    { skip: !contractId }
  );

  const related = (data?.recommendations || [])
    .filter((r) => r.contract?.slug !== currentSlug)
    .map((r) => r.contract)
    .filter(Boolean)
    .slice(0, 3);
```

### Change — DayTripDetailPage.js callsite
**File:** `components/activities/detail/DayTripDetailPage.js` lines 230–233

```jsx
// BEFORE
<DynamicRelatedExperiences
  serviceCategory={contract.service_category}
  currentSlug={slug}
/>

// AFTER
<DynamicRelatedExperiences
  contractId={contract.id}
  currentSlug={slug}
/>
```

### UX Risk: Cold-start gap
Scored API may return fewer results for new/low-booking contracts. Current dumb filter almost always returns 3. Add fallback:

```js
// If recommendations empty, fall back to category filter
// OR: accept lower fill rate as acceptable tradeoff for quality
```
**Recommendation:** Accept the tradeoff for now. Low-traffic contracts showing 0-2 cards is better than showing 3 irrelevant ones.

### Pre-ship Verification
Confirm `recommendationsApi` reducer registered in Redux store (`store/index.js`). RTK Query silently fails if slice not mounted.

### Definition of Done
Activity detail page "You May Also Like" shows scored results, not random category sample. Verify in dev with a contract that has booking history.

---

## Priority 4 — SEO: Hat Yai → Koh Lipe

**Status: GREEN (zero engineering, content team action)**

- No code changes needed
- Start content this week — 3–6 month SEO lag
- Target: "hat yai airport to koh lipe" ($54.11 CPC)
- SmartEnPlus owns live cross-border Langkawi↔Lipe inventory — no other platform has this
- Content strategy doc: `02-areas/content-marketing-strategy-2026-06-03.md`

---

## Priority 5 — Post-Booking Multi-Item Fix

**Status: BLOCKED — do not ship yet**

### Why Blocked
`analyzeBookingContext` (called by `PostBookingRecommendations.js`) is architecturally single-booking:
- `booking.contract` (singular) → single `contractId`
- Multi-item orders where `booking.contract` is null + `booking.contracts[]` is array → silently returns `null` today (no error, no fallback)
- The fix requires redesigning `analyzeBookingContext` to iterate contracts array + deciding UX for multi-contract recommendation seeding (merge? use all? use primary leg?)

### What's Actually Needed
1. Redesign `analyzeBookingContext` to handle `booking.contracts[]` array
2. Decision: pass all contract IDs to API or pick the highest-value one
3. Backend: verify recommendations endpoint accepts or can handle multiple seeds
4. UX: post-booking grid currently `limit=12`, `maxItems=8` — too many cards on confirmation page for multi-item context

**Defer to sprint 2.** Not a 1–2 day fix as originally claimed.

---

## Implementation Order

| Order | Item | Effort | Status |
|-------|------|--------|--------|
| 1 | GTM item_category (`useOmisePayment.js:56`) | 1 line | GREEN — do today |
| 2 | Mount CheckoutRelatedTrips desktop sidebar | 1 import + 1 JSX + collapsed=false fix | YELLOW — do this sprint |
| 3 | Wire RelatedExperiences to recommendations API | ~20 lines across 2 files | YELLOW — do this sprint |
| 4 | SEO Hat Yai-Lipe content | Content only | GREEN — start now |
| 5 | Post-booking multi-item fix | Sprint 2 — redesign needed | BLOCKED |

---

## Open Questions Before Shipping Priority 2

- [ ] Confirm `cart_item[].contract_id` flat field exists in API response (check network tab or backend `carts/serializers.py`)
- [ ] Decide: mobile sidebar in scope for v1 or desktop-only?
- [ ] Decide: `collapsed={false}` on desktop only, or all breakpoints?

---

## Related

- [[next-priority-debate-2026-06-09]] — source priority list this plan implements
- [[business]] — roadmap: cross-sell = current step 3
- [[business-development-thesis-2026]] — gate: multi-booking rate rising → journey builder
- [[checkout-confirmation-payment-crash-2026-06-03]] — non-transport checkout now live
