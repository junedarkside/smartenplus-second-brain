# Checkout Confirmation/Payment Crash — 2026-06-03

## Summary
Checkout crashes at Confirmation/Payment step for non-transport cart items. Two unguarded accesses in `Confirmation.js` + one fragile pattern in `TripsConfirmation.js`.

## Status
OPEN — reproduction steps documented. Fix pending.

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
