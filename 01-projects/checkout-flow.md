# SmartEnPlus — Checkout Flow

## Summary
Multi-step checkout, SSR off. Sort by travel date. Guest + auth users. Redux state, RTK Query APIs.

## Checkout SSR Disabled
`pages/checkout/index.js` exported via `dynamic(() => Promise.resolve(Index), { ssr: false })`. Never add `getServerSideProps` or re-enable SSR. Cart data in Redux (client-side), no server session.

## Cart
- Item keys: `item.id` (stable_id removed 2026-02-13)
- Cart state in Redux `cart` slice
- `cartActions.resetCart()` only on order confirmation pages, NOT in payment hooks

## Chronological Sorting
All checkout steps sort by `traveling_date` (earliest first). Applied across passenger assignment, confirmation, payment steps. Never sort by other field.

## Passenger Assignment
- `item.id` as key
- Generate default assignments for same passenger counts
- Assignment data in `passenger` Redux slice

## Guest Mode
- `isGuestMode` in `checkout-slice` Redux state
- Persisted via redux-persist (no raw localStorage)
- Dispatch `setIsGuestMode(bool)` to toggle
- Guest order tracking: `/guest-order/{id}?email=...`

## DatePicker Handling
Date objects in Formik state. Format to string ONLY when sending to API. Never store string dates in Formik — causes comparison bugs.

## Operational Day Check
`isOperationalDay(date, operational_days)` from `helpers/checkAdvanceHour.js`. Used to:
- Gate `contractAvailable` in trip detail
- Disable booking button in trip item
- Show "Not operating on this day" in booking form
Never inline this logic.

## Contract Fetch Loading
Pass `isContractFetching` bool (from `useCheckContractQuery`) through component chain → `TripDetail2` → `TripDetailBooking`. Shows "Checking availability..." during CSR refresh. Don't show stale price while fetching.

## Checkout Steps
1. **Passenger info** — select/enter passengers for each cart item
2. **Contact info** — email, phone (guest) or use profile (auth)
3. **Payment method** — select from backend-driven options via `/gateway-fee/`
4. **Confirmation** — review all details, submit order
5. **Payment** — Omise charge creation, QR polling, or redirect

## Related
- [[README]]
- [[architecture]]
- [[payment-system]]

## Orphan Link-Backlog (Linked 2026-06-13)
- [[checkout-step-flow]] — checkout step flow overview (canonical pattern)
- [[booking-widget-availability-error-display]] — availability-error display pattern
- [[check-your-booking-redesign]] — check-your-booking redesign decision (15 days old)
- [[checkout-uxui-audit]] — UX/UI audit of checkout step (3 days old)