# Manual QA Test Plan — Payment Deep Review Skipped Tests

## Summary

Runbook for the 8 Playwright tests skipped in [[payment-deep-review-2026-06-12]] due to missing test data + dev/staging environment. Each section = one skipped test converted to manual steps. Source spec: `smartenplus-frontend/e2e/checkout/payment-deep-review.spec.ts` lines 141-256.

**Coverage by fix:**
- H3 — orders/views.py response shape (BE `d7af0e9`)
- H4 — useOmisePayment.js charge_id + charge_created_at (FE `a3c8c80`)
- H5 — orders/views.py reconcile gate (BE `6a481df`)
- M1 — useOmisePayment.js pendingCharge branch (FE `294c8fc`)
- M2 — useOmisePayment.js alreadyPaid + amountLocked branches (FE `294c8fc`)
- M3 — PaymentComponent cancelState prevMethodRef guard (FE `294c8fc`)
- Full smoke — end-to-end PromptPay QR

## Prerequisites

**Environment:**
- Staging deploy of `fix/payment-deep-review-2026-06-12` (BE + FE)
- Staging admin access + Django shell
- Test user account (email + password)
- Active trip with inventory (use a Koh Lipe or Bangkok tour trip)
- Browser (Chrome) logged in to test user

**Tools:**
- Django shell: `docker exec -it <be> python manage.py shell`
- Browser DevTools network tab (capture API calls)
- curl for API tests

**Pass criteria:** each test section ends with a checkbox you mark PASS/FAIL/BLOCKED with notes.

## Fixture Setup

Run these in Django shell to create reusable test orders. Replace IDs as needed.

```python
from orders.models import Order
from payments.models import GatewayCharge
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()
test_user = User.objects.get(email='qa@example.com')  # your test user

# ── Fixture A: pending order (no charge) ──
order_pending = Order.objects.create(
    user=test_user, status='ordering', grand_total=12000,
    # add required fields per your Order model
)
print(f"order_pending.id = {order_pending.id}")

# ── Fixture B: order with pending PP charge ──
order_with_pending = Order.objects.create(
    user=test_user, status='payment_pending', grand_total=12000,
)
charge_pending = GatewayCharge.objects.create(
    order=order_with_pending, gateway='omise', method='PP',
    status='pending', amount=12000, currency='THB',
    gateway_charge_id=f'chrg_test_{uuid.uuid4().hex[:8]}',
    expires_at='2026-12-31 23:59:59+00:00',  # far future
)
print(f"order_with_pending.id = {order_with_pending.id}, charge.id = {charge_pending.id}")

# ── Fixture C: order with paid charge (for H5 self-heal test) ──
order_paid_charge = Order.objects.create(
    user=test_user, status='payment_pending', grand_total=12000,
)
charge_paid = GatewayCharge.objects.create(
    order=order_paid_charge, gateway='omise', method='PP',
    status='paid', amount=12000, currency='THB',
    gateway_charge_id=f'chrg_test_{uuid.uuid4().hex[:8]}',
)
print(f"order_paid_charge.id = {order_paid_charge.id}, charge.id = {charge_paid.id}")

# ── Fixture D: already-paid order (for M2a) ──
order_paid = Order.objects.create(
    user=test_user, status='paid', grand_total=12000,
)
print(f"order_paid.id = {order_paid.id}")

# ── Fixture E: order with locked amount (for M2b) ──
# Locked = has a pending charge that hasn't expired
order_locked = order_with_pending  # reuse fixture B
print(f"order_locked.id = {order_locked.id}")
```

Save the printed IDs. Reference them in tests below.

---

## Test 1: H3 — Order reuse returns wrapped response

**Fix:** BE `d7af0e9` (orders/views.py response shape)

**Prereqs:** test user logged in, valid cart with 1 trip, fixture A (pending order) NOT needed (this test creates its own).

**Steps:**
1. Open browser, add a trip to cart.
2. Fill passenger details, proceed to payment.
3. Submit order creation. Capture response in DevTools → Network tab.
4. **Without refreshing**, submit the same order again (e.g., click "Place Order" twice quickly, or use the same idempotency key).

**Expected:**
- First response: `{ order: {...}, ... }` (full OrderSerializer)
- Second response: `{ message: "Order reused", order: {...} }` (wrapped)
- Order ID is the same in both
- UI shows success state in both cases

**Verify via API (alternative):**
```bash
# Get cart, then POST to /api/orders/create/ twice with same payload
curl -X POST $API_URL/api/orders/create/ -H "Cookie: sessionid=..." \
  -d '{"cart_id":"<cart_id>","passengers":[...]}' -i
# Repeat and compare response shapes
```

**Pass criteria:** [ ] Second response body contains `message: "Order reused"` key

---

## Test 2: H4 — QR cancel expires charge correctly

**Fix:** FE `a3c8c80` (useOmisePayment.js charge_id + charge_created_at)

**Prereqs:** test user, active cart with trip.

**Steps:**
1. Add trip to cart → checkout → fill passengers.
2. At payment, select PromptPay, click "Generate QR".
3. Wait for QR image to render.
4. Observe countdown timer — note the initial value (e.g., 14:59, 14:58).
5. Wait 30 seconds. Countdown should decrease (real `expires_at` from BE, not 600s hardcoded).
6. Click "Cancel" button.
7. Observe UI: order should return to "ordering" state (or show "Payment Cancelled" success message).
8. Check Django shell: `GatewayCharge.objects.filter(order_id=<order_id>).latest('created_at').status` should be `expired` (or `cancelled`).
9. Wait 60s. Refresh the order page. Should be back at "select payment method" state.

**Expected:**
- Countdown uses real `expires_at` (typically 15min, NOT 600s/10min)
- Cancel button works
- Charge transitions to `expired` in DB within ~1 min
- Order returns to `ordering` state

**Pass criteria:**
- [ ] Countdown starts at ~15:00 (not 10:00)
- [ ] Countdown decreases in real time
- [ ] Cancel → success message
- [ ] DB: charge.status = `expired` after cancel

---

## Test 3: H5 — Self-heal for payment_pending orders

**Fix:** BE `6a481df` (reconcile gate extension in orders/views.py)

**Prereqs:** fixture C (order_paid_charge with `status='payment_pending'` + paid GatewayCharge).

**Steps:**
1. Note `order_paid_charge.id` from fixture C.
2. Browser: open `https://staging.example.com/orders/<order_paid_charge.id>/orderdetails/` while logged in as test user.
3. Observe order status badge/text.
4. If "Payment Pending", wait 5-10s and refresh.
5. Status should self-heal to "Paid" (the reconcile gate notices the paid charge + payment_pending order).

**Expected:**
- Order detail page shows "Paid" status
- DB: `Order.objects.get(id=<id>).status` = `paid` after reconcile

**Verify via API:**
```bash
curl $API_URL/api/orders/<order_paid_charge.id>/orderdetails/ \
  -H "Cookie: sessionid=<test_user_session>"
# Response should show status="paid"
```

**Pass criteria:**
- [ ] Order detail page shows "Paid" within 10s of load
- [ ] DB confirms status = "paid"

---

## Test 4: M1 — QR flow shows PendingChargeNotice

**Fix:** FE `294c8fc` (pendingCharge branch in useOmisePayment.js)

**Prereqs:** fixture B (order_with_pending with active pending PP charge).

**Steps:**
1. Note `order_with_pending.id` from fixture B.
2. Browser: navigate to `https://staging.example.com/checkout/payment?order=<order_with_pending.id>`.
3. Select PromptPay.
4. Click "Generate QR".
5. Observe UI response.

**Expected:**
- NOT a generic error toast
- Shows `PendingChargeNotice` component (data-testid="pending-charge-notice" per spec line 29)
- Text indicates an existing charge is pending, with cancel option
- No new charge created in DB

**Pass criteria:**
- [ ] PendingChargeNotice renders (not generic error)
- [ ] DB: no NEW GatewayCharge created for this order (count stays at 1)

---

## Test 5: M2a — Card flow redirects to order page when alreadyPaid

**Fix:** FE `294c8fc` (alreadyPaid branch in useOmisePayment.js)

**Prereqs:** fixture D (order_paid with status='paid').

**Steps:**
1. Note `order_paid.id` from fixture D.
2. Browser: navigate to `https://staging.example.com/checkout/payment?order=<order_paid.id>`.
3. Select Credit Card.
4. Click "Pay Now" or trigger card flow.

**Expected:**
- NOT a new card charge attempt
- Redirects to `/orders/<order_paid.id>/` (order detail / confirmation page)
- No Omise charge call fired

**Verify in DevTools → Network:**
- No POST to Omise `/charges` endpoint
- 302/JS navigation to `/orders/<id>/`

**Pass criteria:**
- [ ] Lands on order page (not payment form)
- [ ] No Omise charge API call in Network tab

---

## Test 6: M2b — Redirect flow shows PendingChargeNotice when amount locked

**Fix:** FE `294c8fc` (amountLocked branch in useOmisePayment.js)

**Prereqs:** fixture B (order_with_pending). Works for any redirect method (credit card, Alipay, KakaoPay).

**Steps:**
1. Note `order_with_pending.id` from fixture B.
2. Browser: navigate to `https://staging.example.com/checkout/payment?order=<order_with_pending.id>`.
3. Select Credit Card OR Alipay OR KakaoPay (any redirect method).
4. Click "Pay Now".

**Expected:**
- NOT a redirect to Omise gateway
- Shows `PendingChargeNotice` (same component as Test 4)
- Message indicates amount is locked by existing pending charge
- User can cancel the existing charge or wait for expiry

**Pass criteria:**
- [ ] PendingChargeNotice renders
- [ ] No redirect to Omise hosted page
- [ ] Existing charge still pending in DB (not duplicated)

---

## Test 7: M3 — cancelState no flash on method change

**Fix:** FE `294c8fc` (cancelState prevMethodRef guard in PaymentComponent)

**Prereqs:** test user, active cart with trip. **This is a UI animation test — needs careful observation.**

**Steps:**
1. Add trip to cart → checkout → fill passengers → reach payment page.
2. Select PromptPay → click "Generate QR" → wait for QR.
3. Click "Cancel" → observe "Payment Cancelled" success message.
4. **Without refreshing**, click "Credit Card" payment method button.
5. Observe UI transition closely (record screen if possible).

**Expected:**
- No flash of "Payment Cancelled" alert on the credit card form
- Credit card form renders cleanly
- `cancelState.success` cleared on method switch (via prevMethodRef guard)

**Pass criteria:**
- [ ] No "Payment Cancelled" toast/alert visible after switching to credit card
- [ ] Credit card form renders normally
- [ ] (Optional) Record screen + check no flicker in 2x playback

---

## Test 8: Full checkout → payment PromptPay QR smoke

**Fix:** Validates full integration of all 5 batches end-to-end.

**Prereqs:** test user, active trip with real inventory, valid cart.

**Steps:**
1. Open browser, navigate to a trip detail page.
2. Click "Book Now" → adds to cart.
3. Go to cart → click "Checkout".
4. Fill contact info (email, phone).
5. Fill passenger details (first name, last name, etc.).
6. Click "Continue to Payment".
7. Select PromptPay.
8. Click "Generate QR".
9. Verify QR code image appears (wait up to 10s).
10. Verify countdown timer shows.
11. **STOP HERE** — do not pay (or use a sandbox Omise key to complete).

**Expected:**
- All steps complete without error
- QR code renders
- Countdown shows real expiry (H4 fix)
- No console errors
- No 4xx/5xx in Network tab (except the expected 200/202 from `/api/payments/order-charge/`)

**Pass criteria:**
- [ ] End-to-end flow completes to QR generation
- [ ] QR code visible
- [ ] Countdown timer visible and decreasing
- [ ] No console errors
- [ ] No unexpected 4xx/5xx in Network tab

---

## Results Template

Copy this into a comment / issue when done:

```
Payment Deep Review Manual QA — 2026-06-12
============================================
Tester: <name>
Staging deploy: <commit hash>
Date: <date>

Test 1 (H3 order reuse wrap):     [ PASS / FAIL / BLOCKED ]  Notes: ...
Test 2 (H4 QR cancel expires):    [ PASS / FAIL / BLOCKED ]  Notes: ...
Test 3 (H5 self-heal pending):    [ PASS / FAIL / BLOCKED ]  Notes: ...
Test 4 (M1 QR PendingCharge):     [ PASS / FAIL / BLOCKED ]  Notes: ...
Test 5 (M2a card alreadyPaid):    [ PASS / FAIL / BLOCKED ]  Notes: ...
Test 6 (M2b redirect amountLock): [ PASS / FAIL / BLOCKED ]  Notes: ...
Test 7 (M3 cancelState no flash): [ PASS / FAIL / BLOCKED ]  Notes: ...
Test 8 (Full smoke):              [ PASS / FAIL / BLOCKED ]  Notes: ...

Overall: [ ALL PASS / N FAIL / N BLOCKED ]
PAYMENT-FIX: [ READY TO CLOSE / NEEDS FIX ]
```

## Related

- [[payment-deep-review-2026-06-12]] — source review
- [[payment-implement-plan-2026-06-12]] — fix sequence
- [[payment-deep-review-verification-2026-06-12]] — KB verification pass
- [[payment-deep-review-test-cases-2026-06-12]] — test case doc
- `smartenplus-frontend/e2e/checkout/payment-deep-review.spec.ts` — source spec (skipped tests at lines 141-256)
