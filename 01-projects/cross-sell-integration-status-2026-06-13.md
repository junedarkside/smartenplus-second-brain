# Cross-Sell Integration Status Audit — 2026-06-13

## Summary
Live code verification of all 4 cross-sell surfaces. All surfaces mounted. Vault knowledge partially stale (UX blockers + GTM + activity-detail accuracy already resolved in code). **Only open engineering item: multi-item post-booking recommendations (Sprint 2, not urgent).** Primary gate to activation = BD inventory, not engineering.

> **Correction (verified 2026-06-13 live read):** This note originally listed GTM `item_category` and activity-detail accuracy as open work. Both were already shipped. See "Already Shipped" section below.

## Context
Session #108. User asked "where should cross-sell be in the project, which pages already integrated." Live code read against vault knowledge. Vault atoms `[[cross-sell-debate-review-2026-06-09]]` and `[[implementation-plan-cross-sell-2026-06-09]]` had stale "4 UX blockers" list — those fixes already shipped in `CheckoutRelatedTrips.js`.

## Verified Live Surfaces

| Page | Component | Mount | Notes |
|------|-----------|-------|-------|
| Checkout step 0 | `CheckoutRelatedTrips` | `pages/checkout/index.js:1008` | formStep === 0 only |
| Trip Detail | `RelatedTripsSection` | `pages/trips/detail/[...slug].js:367` | dynamic import SSR disabled |
| Activity Detail | `RelatedExperiences` | `components/activities/detail/DayTripDetailPage.js:231` | dumb filter (unscored) |
| Post-Booking | `PostBookingRecommendations` | `components/bookings/BookingDetailMain.js:161` | feature-flagged |

## Checkout Cross-Sell — Current Props

```jsx
<CheckoutRelatedTrips
  cartItems={data?.cart_item}
  collapsed={false}
  maxItems={3}
  placement="checkout"
  sessionKey={`checkout-cross-sell-${data?.id}`}
/>
```

Component internally handles (already coded, vault atoms were stale):
- Price filter: `lowestPrice < minCartPrice` → hidden (`CheckoutRelatedTrips.js:51-56`)
- Cart dedup: same contract already in cart → hidden
- GTM `checkout_recommendation_view` — fires once per sessionKey
- Anchor: `transportItems[0]` (first transport) → `recType = 'packages'`; else first non-skip → `recType = 'activity'`

## Pages Without Cross-Sell (Intentional)

- Checkout step ≥ 1 (passengers/payment): component only mounts at formStep === 0
- Homepage/Search: no source contract
- My Bookings list: low intent

## Already Shipped (verified 2026-06-13 live read)

### ✅ GTM `item_category` — SHIPPED
- Was listed as "~3 line quick win". Already in code.
- `hooks/useOmisePayment.js:59` builds `item_category: contract.service_category` in `tripItems`
- `hooks/useOmisePayment.js:144` pushes it: `purchase` event → `ecommerce.items: tripItems`
- (Original note had wrong path `useOmisePayment.js:56` — actual is `hooks/useOmisePayment.js`)

### ✅ Activity Detail Accuracy — SHIPPED
- Was listed as "1–2 day migration to recommendations API". Already migrated.
- `components/activities/detail/RelatedExperiences.js:7` calls `useGetRecommendationsQuery({ contractId, type: 'similar', limit: 4 })`
- Mounted via `DynamicRelatedExperiences` at `DayTripDetailPage.js:231` (props: `contractId`, `currentSlug`)
- No longer a dumb `service_category` filter — scored backend recs.

## Open Engineering Work

### 1. Post-Booking Multi-Item (ONLY open item)
- **Problem:** `analyzeBookingContext()` is single-booking only; multi-item orders pick one contract
- **File:** `helpers/bookingContext.js:33` — returns single `contractId`
- **Effort:** Sprint 2 — needs query redesign + UX decision (which anchor for multi-item order)
- **Status:** Not urgent (single-booking works)

## BD Blockers (No Eng Work)

Cross-sell auto-hides when backend returns 0 results. 60-day gate clock won't start until:

| Missing | Rec Type | BD Action |
|---------|----------|-----------|
| Return route: Koh Lipe → Hat Yai Airport | `packages` | Create route |
| DAY_TOUR contracts at Koh Lipe | `activity` | Create inventory |
| SPA_WELLNESS contracts at Koh Lipe | `activity` | Create inventory |

## Stale Vault Knowledge (Fix Needed)

`[[cross-sell-placement-strategy]]` says "checkout sidebar = avoid" — OUTDATED. Checkout IS integrated and live.
`[[cross-sell-debate-review-2026-06-09]]` lists 4 UX blockers — OUTDATED. All already in `CheckoutRelatedTrips.js`.
`[[implementation-plan-cross-sell-2026-06-09]]` has "Mount CheckoutRelatedTrips" as todo — OUTDATED. Already mounted.

## Decision
No new engineering work needed to activate cross-sell. It is live on all 4 surfaces, and GTM `item_category` + activity-detail accuracy are already shipped (verified live). BD inventory is the primary and only gate. The single open eng item (multi-item post-booking) does not block activation.

## Related
- [[CheckoutRelatedTrips]] — `components/recommendations/CheckoutRelatedTrips.js`
- [[cross-sell-debate-review-2026-06-09]] — debate (stale re: blockers)
- [[implementation-plan-cross-sell-2026-06-09]] — impl plan (stale re: mount status)
- [[cross-sell-placement-strategy]] — placement strategy (stale re: checkout)
- [[gtm-purchase-item-category-attribute]] — GTM prereq atom
- [[activity-to-activity-cross-sell]] — activity detail rec type spec
