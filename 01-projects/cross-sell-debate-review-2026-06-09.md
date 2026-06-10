# Cross-Sell Implementation Review — 2026-06-09
## 4-Agent Debate: UX + BD Analyst + Backend + Code Auditor

---

## Status: DO NOT SHIP AS-IS — 3 blocking issues found

---

## Dimension Review: Route / Date / Time / Category

| Dimension | Current Behavior | Risk |
|-----------|-----------------|------|
| **Route** | `similar` filters by `arrival_station` only — same destination, any departure point | Medium — shows alternatives, not cross-sell |
| **Date** | No `traveling_date` filter — recommends contracts regardless of Jun 10 availability | **HIGH** — can recommend unavailable trips |
| **Time** | `time_proximity` weight=5 — promotes earlier departures over the cart item | High UX — regret trigger at payment step |
| **Category** | No `service_category` filter — auto-includes DAY_TOUR/SPA_WELLNESS when inventory exists | Correct design, but reason text will be confusing |

---

## Issue 1 — BLOCKER: Rate Table + Cheaper Alternatives Kill Conversion

**Agents:** UX + BD Analyst

**Problem:**
- Cards render full ADULT/CHILD/INFANT rate table with dual prices at payment step
- Results 3+4 are THB 800 vs cart item THB 1,000 — cheaper alternatives shown at payment moment
- Result 1: same route, same operator, 10:00 departure vs user's 11:30 → reads as "you booked the wrong trip"
- "Same route, same operator" reason text amplifies abandonment risk

**UX verdict:** HIGH risk. Do not ship with current card density in sidebar.

**Fixes needed before commit:**
1. Add `showRateTable={false}` prop to `RecommendationCard` — show `lowestPrice` ("from THB X") instead of full table
2. Filter results in `CheckoutRelatedTrips` where `lowestPrice < cartMinPrice` when `placement === 'checkout'` — don't show cheaper alternatives at payment
3. Add `service_category` chip to card face — when DAY_TOUR/SPA_WELLNESS appear, user must know it's a different product
4. Optionally suppress `departure_time` row for same-route results (or add `showTime` prop)

---

## Issue 2 — BLOCKER: BD Gate Cannot Fire Without Inventory

**Agent:** BD Analyst

**Problem:**
All 4 current results are TRANSPORT because zero DAY_TOUR/SPA_WELLNESS contracts exist at Koh Lipe `arrival_station`. The 60-day gate ("prove transport buyers cross-buy DAY_TOUR or SPA_WELLNESS") cannot produce a single qualifying signal on the most-booked route.

**Gate achievability: Conditional**

Three blockers:
1. **Inventory gap** (most critical): BD must create at least 1 DAY_TOUR or SPA_WELLNESS contract at Koh Lipe. Engine auto-surfaces it — no code change needed. Without this, 0 cross-sell signals accumulate in 60 days.
2. **Recommendation type wrong**: `type=similar` biases toward transport similarity. Switch to a new `type=cross_category` backend type that queries `arrival_station` + `service_category IN (DAY_TOUR, SPA_WELLNESS)`. Interim: `type=hybrid` is better than `similar` but still diluted with transport alternatives.
3. **Attribution gap**: No `item_list_id` in GTM purchase event linking sale back to recommendation click. GA4 session analysis is probabilistic. Add `item_list_id: "checkout_sidebar"` to `tripItems` in `useOmisePayment.js` when a recommendation click occurred in session.

---

## Issue 3 — BLOCKER: Date Availability Gap in Backend

**Agent:** Backend Architect

**Problem:**
`find_similar_contracts` filters only `arrival_station + is_actived=True`. No `operational_days` check against cart traveling_date. A contract that runs Mon/Wed/Fri only can appear as a recommendation for a Tuesday booking. User clicks → "no availability" → frustration.

**Fix (backend):** Thread `rate_date` param (already accepted by view) through to `find_similar_contracts`. Add `.filter(trip__operational_days__contains=weekday)` using weekday derived from cart date.

---

## Secondary Issues (not blocking commit if blocking issues addressed)

### Cart Dedup Gap — Medium
Backend only excludes source contract ID. If user has contracts 2+5 in cart, contract 5 appears as a recommendation. 

**Fix:** Frontend reads `cartItems.map(i => i.contract.id)`, passes as `?exclude_ids=2,5`. Backend adds `.exclude(id__in=exclude_ids)` — one query param change.

### GTM Double-Fire Risk — Minor (pre-commit fix)
`CheckoutRelatedTrips.js` GTM `useEffect` fires on every `recommendations` re-render. `useMemo` on nested `recommendationsData?.recommendations` creates new array reference on cache refresh → double-fire.

**Fix:** Add `hasFiredRef` guard:
```js
const hasFiredRef = React.useRef(false);
useEffect(() => {
  if (hasFiredRef.current || recommendations.length === 0) return;
  hasFiredRef.current = true;
  // push to dataLayer
}, [recommendations, placement]);
```

### Pricing Date Gap — Minor / Display Only
`RecommendationCard` falls back to today's date for rate deduplication when no `bookingDate` passed. Cart date is Jun 10 — displayed price may differ from actual.

**Fix:** Pass `bookingDate={cartItems?.[0]?.traveling_date}` from `CheckoutSidebar` through `CheckoutRelatedTrips` to `RecommendationCard`.

### Debug Banner — REQUIRED cleanup before commit
`CheckoutRelatedTrips.js` lines 134–143: remove entire dev debug banner block before commit.

---

## What Works Correctly

| Item | Status |
|------|--------|
| `contract_id` from cart item (`contract?.id`) | Fixed, working |
| `forceRefetch` null guard (`previousArg?.date`) | Fixed, safe |
| `item_category` in GTM purchase event | Implemented, confirmed safe |
| `recommendationsApi` Redux store registration | Confirmed correct |
| Backend `service_category` auto-mixing | Correct by design — will work when inventory exists |
| `RelatedExperiences` scored API swap | Confirmed correct |
| `DayTripDetailPage` contractId prop | Confirmed correct |

---

## Ranked Action List

| Priority | Action | Owner | Effort |
|----------|--------|-------|--------|
| 1 | Create DAY_TOUR/SPA_WELLNESS contracts at Koh Lipe destination | BD/Product | 1–2 days |
| 2 | Add `showRateTable={false}` + filter cheaper alternatives in checkout sidebar | Frontend | 2–3 hours |
| 3 | Add date availability filter to `find_similar_contracts` (operational_days) | Backend | 2–3 hours |
| 4 | Remove debug banner + add GTM `hasFiredRef` guard | Frontend | 30 min |
| 5 | Add `service_category` chip to `RecommendationCard` | Frontend | 1 hour |
| 6 | Pass `bookingDate` through to `RecommendationCard` | Frontend | 30 min |
| 7 | Build `type=cross_category` backend recommendation type | Backend | 1 day |
| 8 | Add cart `exclude_ids` dedup to frontend + backend | Full stack | 2 hours |
| 9 | Add `item_list_id: "checkout_sidebar"` to purchase GTM event for attribution | Frontend | 1 hour |

---

## Related

- [[implementation-plan-cross-sell-2026-06-09]] — original implementation spec
- [[next-priority-debate-2026-06-09]] — priority debate that spawned this work
- [[business-development-thesis-2026]] — BD gate: cross-sell conversion rate prerequisite
