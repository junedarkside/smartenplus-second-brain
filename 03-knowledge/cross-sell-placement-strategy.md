# Cross-Sell Placement Strategy

## Summary
Industry-standard cross-sell placement for travel booking platforms. Post-booking confirmation = highest ROI. Trip detail = highest volume. Checkout sidebar = abandon risk, avoid.

## Context
4-agent debate (UX + Design + BD + Frontend) on 2026-06-09. Competitive analysis: Klook, Viator, GetYourGuide, 12Go Asia, Booking.com, Omio. Scrutinizer pass + multi-item cart audit + 10-category engine design + implementation on 2026-06-10.

---

## Industry Standard Placements (Ranked by Conversion)

### 1. Post-Booking Confirmation — HIGHEST CONVERSION
- **Why:** User just committed money. Emotional high. Booking immutable — no abandonment risk.
- **Who does it:** Klook, Booking.com ("Complete your trip"), Viator, 12Go (return trip prompt)
- **What to show:** Return trip, activities at destination, onward transport
- **Format:** Full-width grid, 4–6 cards, expanded by default
- **SmartEnPlus status:** LIVE — `PostBookingRecommendations` mounted in `BookingDetailMain.js`, enabled by default (`NEXT_PUBLIC_POST_BOOKING_RECOMMENDATIONS_ENABLED !== 'false'`)

### 2. Trip Detail Page — HIGHEST VOLUME
- **Why:** Research mode. No friction to leave page.
- **Who does it:** All major OTAs — "You may also like", "Similar experiences"
- **What to show:** Same destination activities, alternative routes, complementary products
- **Format:** Grid at bottom of page
- **SmartEnPlus status:** LIVE — `RelatedExperiences` component (migrated to recommendations API on 2026-06-10)

### 3. Checkout Step 0 Inline — BD VALIDATION PLACEMENT
- **Why:** User committed (in checkout, reviewing itinerary) but still in planning mode. Cleanest BD signal: click = genuine multi-product intent.
- **Step:** formStep=0 (Itineraries review) — before passenger entry, before payment
- **Format:** Expanded accordion (`CheckoutRelatedTrips`, `collapsed={false}`). Title: "People also book". Non-blocking.
- **Rec type logic:** See cross-sell matrix below — depends on cart composition.
- **Multi-item cart:** Anchor = last transport item (final destination). Falls back to first non-skip activity item.
- **Back-navigation:** `sessionKey` prop persists open/closed + de-dups GTM view event via sessionStorage. Prevents double-counting on 0→1→0.
- **BD signal:** `checkout_recommendation_click` rate ≥5% over 60 days → unlocks Journey Builder investment
- **GTM clock start:** When first `checkout_recommendation_view` fires with `recommendation_count > 0`. Section auto-hides when engine returns 0 — clock does NOT start.
- **Branches:** frontend `260609-feat/cross-sell-gtm-recommendations` (commit `61f2ec2`), backend `260610-feat/cross-sell-activity-recommendations` (commit `4877d65`)
- **SmartEnPlus status:** IMPLEMENTED (2026-06-10). Monitoring 60-day BD gate. Blocked by BD inventory (engine returns 0 until BD creates contracts).

### 4. Post-Add-to-Cart Modal — BACKLOG
- **Why:** Peak booking momentum right after "Book Now" click.
- **Resolution:** Two-tier by product type:
  - Transport buyer → NO modal (5-8% abandonment risk)
  - DAY_TOUR/SPA buyer → modal viable when inventory exists
- **SmartEnPlus status:** BACKLOG. Build when ≥1 DAY_TOUR/SPA contract exists at destination.
- **Implementation:** `BookButton.js` line 241 — intercept `router.push('/checkout')` with modal state. Reuse `CheckoutRelatedTrips`. 3-4 hours.

### 5. My Bookings / Order History — LOW CONVERSION
- **SmartEnPlus status:** Not implemented, low priority

### 6. Checkout Sidebar (During Payment) — AVOID
- **Why:** User entering payment details. Cross-sell = doubt = abandonment. All major OTAs suppress.
- **SmartEnPlus decision:** Removed from `CheckoutSidebar.js` 2026-06-09. Do not re-add.

### 7. Homepage / Search Results — LOWEST CONVERSION
- **SmartEnPlus status:** Not applicable — no recommendation context without source contract

---

## Service Category Data Structure

| Category | Has `trip` | Has stations | Has `primary_location` |
|---|---|---|---|
| TRANSPORTATION | ✅ | ✅ dep + arr | ❌ |
| TRANSFER | ✅ | ✅ dep + arr | ❌ |
| DAY_TOUR | ❌ null | ❌ | ✅ |
| MULTI_DAY_TOUR | ❌ null | ❌ | ✅ |
| SPA_WELLNESS | ❌ null | ❌ | ✅ |
| EVENT_TICKET | ❌ null | ❌ | ✅ |
| ATTRACTION_TICKET | ❌ null | ❌ | ✅ |
| FOOD_DINING | ❌ null | ❌ | ✅ |
| ACCOMMODATION | ❌ null | ❌ | ✅ |
| OTHER | ❌ null | ❌ | ✅ |

Non-transport: `trip` always NULL (enforced by `sanitize_category_fields()` in admin). Location authority = `primary_location` (FK) + `service_areas` (M2M).

---

## Cross-Sell Matrix

| Cart item | Rec type | What returns | BD value | Engine support |
|---|---|---|---|---|
| TRANSPORTATION | `packages` | Return trip + onward connections | HIGH | ✅ `find_package_contracts` |
| TRANSFER | `packages` | Return transfer + onward | MED | ✅ `find_package_contracts` |
| DAY_TOUR | `activity` | Other tours + spa at same location | MED | ✅ `find_activity_contracts` |
| SPA_WELLNESS | `activity` | Transport to location + tours | LOW | ✅ `find_activity_contracts` |
| ACCOMMODATION | `activity` | Transport + activities near property | MED | ✅ `find_activity_contracts` |
| FOOD_DINING | `activity` | Transport + nearby activities | LOW | ✅ `find_activity_contracts` |
| MULTI_DAY_TOUR | `activity` | Similar packages at location | MED | ✅ `find_activity_contracts` |
| Mixed (transport + activity) | `packages` on last transport item | Transport-anchored (highest value) | HIGH | ✅ |
| EVENT_TICKET only | skip | Low checkout intent (BD decision) | — | N/A |
| ATTRACTION_TICKET only | skip | Low checkout intent (BD decision) | — | N/A |
| EVENT_TICKET/ATTRACTION_TICKET only | skip | No viable anchor → query skipped | — | N/A |

---

## Backend Recommendation Types (`products/services.py`)

| Type | Function | What it queries | Works for |
|---|---|---|---|
| `similar` | `find_similar_contracts` | Same arrival station, any departure | TRANSPORTATION only |
| `alternatives` | `find_alternative_contracts` | Same exact route, different operator | TRANSPORTATION only |
| `packages` | `find_package_contracts` | Return trip (arr→dep) + connecting from arr | TRANSPORTATION + TRANSFER |
| `activity` | `find_activity_contracts` | `primary_location` OR `service_areas` at arrival location | TRANSPORTATION → non-transport recs at destination |
| `hybrid` | all combined | similar + alternatives + packages | TRANSPORTATION (post-booking) |

**`find_activity_contracts`** (added 2026-06-10, commit `4877d65`):
- Source: transport contract's `arrival_station.location_name` (Location FK)
- Filter: `Q(primary_location=loc) | Q(service_areas=loc)` + `.distinct()` (M2M requires it)
- Categories: DAY_TOUR, MULTI_DAY_TOUR, SPA_WELLNESS, EVENT_TICKET, ATTRACTION_TICKET, FOOD_DINING, ACCOMMODATION
- Pattern: reuses `products/views.py:462-475` location filter (proven)
- `hybrid` NOT changed — post-booking placements unaffected

---

## Frontend Logic (`CheckoutRelatedTrips.js`, 161 lines)

**Anchor + rec type selection:**
```js
const TRANSPORT_CATS = ['TRANSPORTATION', 'TRANSFER'];
const SKIP_CATS = ['EVENT_TICKET', 'ATTRACTION_TICKET'];

const transportItems = cartItems.filter(i => TRANSPORT_CATS.includes(i.contract?.service_category));
const anchorItem = transportItems.length > 0
  ? transportItems[transportItems.length - 1]           // last transport = final destination
  : cartItems.find(i => !SKIP_CATS.includes(i.contract?.service_category)); // first non-skip activity

const recType = transportItems.length > 0 ? 'packages' : 'activity';
const sourceContractId = anchorItem?.contract?.id || null; // null → query skips
```

**Also fixed:** old bug `cartItems?.[0]?.contract_id` (wrong path) → `anchorItem?.contract?.id`.

---

## Filtering Rules

### Backend
1. **Exclude same contract** — `exclude(id=source_contract.id)`
2. **Exclude same route** — station-level primary, location-level fallback when stations null
3. **Exclude unavailable on date** — `filter(operational_day__name=weekday)` when `rate_date` provided

### Frontend (checkout only)
4. **Price floor** — hide recs cheaper than lowest-priced cart item (all items, not just first)
5. **No same-route filter for `packages`/`activity`** — packages = opposite route, activity = different category

---

## SmartEnPlus Inventory Gap (BD action required)

Engine returns 0 until BD creates:
- **Return route: Koh Lipe → Hatyai Airport** — unlocks `packages` type (HIGH BD value)
- **DAY_TOUR contracts at Koh Lipe** (snorkeling, island hopping) — unlocks `activity`
- **SPA_WELLNESS contracts at Koh Lipe** — unlocks `activity`

60-day BD gate clock starts on first `checkout_recommendation_view` with `recommendation_count > 0`.

---

## Branches

| Repo | Branch | Key commits |
|---|---|---|
| smartenplus-frontend | `260609-feat/cross-sell-gtm-recommendations` | `16b725e` rec engine wiring, `61f2ec2` checkout mount |
| smartenplus-backend | `260610-feat/cross-sell-activity-recommendations` | `4877d65` find_activity_contracts + activity type |

---

## Related
- [[recommendation-system]]
- [[cross-sell-debate-review-2026-06-09]]
- [[business-development-thesis-2026]]
