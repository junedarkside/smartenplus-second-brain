# Non-transport trip=None — Full Flow Fix — 2026-06-03

## Summary
Non-transport contracts (DAY_TOUR, SPA_WELLNESS etc.) always have `contract.trip = None`. This caused crashes at every stage of the user flow: checkout confirmation, payment, order page, booking detail page. All crash sites fixed + booking detail page now receives full contract info from API.

## Status
RESOLVED — Merged to develop 2026-06-03. Frontend branch `260603-fix/non-transport-trip-none-guard` merged at commit `0c3bb14`. Backend merged at `9ef2752` (develop, merged main 2026-06-02). Non-transport booking (DAY_TOUR, SPA_WELLNESS) fully live on B2C.

## Atoms Extracted
- [[contract-trip-null-non-transport-pattern]] — frontend `contract?.trip` guard pattern
- [[copy-cartitem-trip-none-guard]] — backend `copy_cartitem_to_bookingitem` null guard
- [[contract-serializer-non-transport-fields-2026-06-03]] — serializer fields expansion
- [[service-detail-non-transport-display]] — booking detail page field-name contract
- [[checkout-null-contract-scan-2026-06-03]] — full checkout scan results

## All Fixes Applied (session 1 + 2)

### Frontend — `260603-fix/non-transport-trip-none-guard`
| File | Fix |
|------|-----|
| `components/forms/checkout/Confirmation.js:111,115` | `formData.passengers?.length ?? 0` + `|| []` |
| `components/forms/checkout/TripsConfirmation.js:18-20` | `?.substring(0, 5) ?? '--:--'` |
| `components/order/OrderDetail.js:171-183` | 5 props null-guarded with `?.` + `?? null` |
| `components/bookings/BookingInfoDialog.js:44` | `trip?.route \|\| {}` |
| `components/bookings/BookingDetail/ServiceTabbedInfo.js` | `?.general_information?.description` + `refund_hours` |
| `components/bookings/BookingDetail/ServiceDetail.js` | Contract name h2 + `customFormatDuration` |
| `helpers/designSystem.js` | `COLORS.badge.category/tourTypePrivate/tourTypeCharter` |

### Backend — `260603-fix/non-transport-trip-none-guard`
| File | Fix |
|------|-----|
| `carts/utils.py` | `_trip/_route` null guards before `BookingItem.objects.create()` |
| `operators/serializers.py` | Extended `ContractSerializer` with 10 non-transport fields + 3 helper serializers |

## Root Cause

`Confirmation.js` renders `formData.passengers` without null guard. If `formData.passengers` is null/undefined (race condition on refetch, or state not fully hydrated for non-transport flow), two lines throw TypeError at render time.

Non-transport contracts (DAY_TOUR, SPA_WELLNESS, EVENT_TICKET) have `contract.trip = None` by design. Previous fixes guarded render-root and Passengers step. Confirmation step not yet guarded.

## Crash Sites

### CRITICAL — Confirmation.js:111
```js
<span>Passenger Details ({formData.passengers.length})</span>
```
`formData.passengers` no null guard. Crashes if undefined/null.

### CRITICAL — Confirmation.js:115
```js
{formData.passengers.map((item, index) => {
```
Same — `.map()` on null throws immediately.

### MEDIUM — TripsConfirmation.js:19 (fragile, not crashing yet)
```js
const departureTime = item.contract?.trip?.departure_time
    ? item.contract.trip.departure_time.substring(0, 5)
    : '--:--';
```
Currently safe — ternary guard prevents line 19 reaching when `trip=null`. But fragile pattern — one refactor away from crash. Should use full optional chain.

## Safe Files (verified)
- `TripsConfirmation.js:13-14` — `contract?.trip?.departure_station` — safe
- `PaymentComponent.js:682` — `item.contract?.name || 'Trip'` — safe
- `PassengerAssignment.js:373` — `item.contract?.translated_name` — safe
- `pages/checkout/index.js:700-end` — no direct contract access

## How to Reproduce in Development

### Step 1 — Create DAY_TOUR contract with trip=None

```bash
cd /Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend
python manage.py shell -c "
from operators.models import Contract, Operator, RateCard, Contract_RateCard, DaysOfTheWeek
from datetime import date, timedelta
from decimal import Decimal

op = Operator.objects.first()
c = Contract.objects.create(
    name='Dev Test - DAY_TOUR trip=None',
    operator=op,
    trip=None,
    service_category='DAY_TOUR',
    type='JOIN',
    is_actived=True,
    confirm=True,
    start_date=date.today(),
    end_date=date(2027, 12, 31),
    advance_hr=timedelta(hours=48),
    instant_confirmation=True,
    mobile_ticket_enabled=True,
)
c.operational_day.set(DaysOfTheWeek.objects.all())
for rc_value in ['ADULT', 'CHILD']:
    rc = RateCard.objects.filter(value=rc_value).first()
    if rc:
        Contract_RateCard.objects.create(contract=c, ratecard=rc, selling_rate=Decimal('600'), bar_rate=Decimal('500'), is_active=True)
print(f'Contract ID={c.id} slug={c.slug} trip={c.trip}')
"
```

### Step 2 — Navigate to product page + add to cart

1. Start frontend: `npm run dev` (ensure `NEXT_PUBLIC_API_URL=http://localhost:8000`)
2. Go to `http://localhost:3000/activities/<slug>`
3. Select date, click Book Now → adds to cart

### Step 3 — Go to checkout

1. Navigate to `http://localhost:3000/checkout`
2. Step 0 (Itinerary) — should load without crash ✓ (already fixed)
3. Click Next → Step 1 (Passengers) — should load without crash ✓ (already fixed)
4. Fill passenger details, click Next → Step 2 (Confirmation) → **CRASH HERE**
   - `TypeError: Cannot read properties of undefined (reading 'length')` at `Confirmation.js:111`

### Step 4 — Confirm crash

Open browser DevTools → Console. Should see:
```
TypeError: Cannot read properties of undefined (reading 'length')
  at Confirmation.js:111
```

## Fix (pending implementation)

**File:** `components/forms/checkout/Confirmation.js`

```js
// Line 111 — BEFORE
<span>Passenger Details ({formData.passengers.length})</span>
// AFTER
<span>Passenger Details ({formData.passengers?.length ?? 0})</span>

// Line 115 — BEFORE
{formData.passengers.map((item, index) => {
// AFTER
{(formData.passengers || []).map((item, index) => {
```

**File:** `components/forms/checkout/TripsConfirmation.js`

```js
// Line 18-20 — BEFORE (fragile)
const departureTime = item.contract?.trip?.departure_time
    ? item.contract.trip.departure_time.substring(0, 5)
    : '--:--';
// AFTER (full optional chain)
const departureTime = item.contract?.trip?.departure_time?.substring(0, 5) ?? '--:--';
```

## Related
[[checkout-null-contract-scan-2026-06-03]]
[[contract-trip-null-non-transport-pattern]]
