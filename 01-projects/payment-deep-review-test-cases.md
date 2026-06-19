# Payment Deep Review — Test Cases (2026-06-12)

## Summary

Test cases for 5-batch payment deep review fix (H1–H5, M1–M3, M5, M8–M10, M17). M4 retracted. M7 deferred. All fixes on branch `fix/payment-deep-review` in both repos.

## Pre-flight Results (2026-06-12)

| Check | Result | Notes |
|-------|--------|-------|
| FE lint | ✅ PASS | No new warnings — only pre-existing |
| FE build | ✅ PASS | `next build` clean exit, zero errors |
| BE ruff (changed files) | ✅ PASS | No new issues — only pre-existing |
| BE syntax compile | ✅ PASS | All 5 files compile |
| BE unit tests | ✅ PASS | **20/20 pass** — `payments/tests/test_deep_review_fixes.py` commit `6937f39`. Fixed pre-existing migration bug (operators/0050 dependency on bookings/0042). |
| FE jest tests | ✅ PASS | **84/84 pass** — 5 suites. Commit `478a2bf`. paymentMethods (15), useOmisePayment (18), useQRPolling (15), useCancelPayment (6), PaymentComponent (12). |

---

## 1. Smoke Tests (curl, developer-run)

### TC-S1: H2 — Legacy webhook returns 410

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/payments/webhook-legacy/
# Expected: 410
```

### TC-S2: M10 — PlaceOrder returns 410

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/placeorder/
# Expected: 410
```

### TC-S3: H1 — Amount mismatch rejected

```bash
# First create a real order, then:
curl -X POST http://localhost:8000/api/payments/order-charge/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "<REAL_ORDER_ID>", "grandTotal": 2000, "fee_calculated": 0, "selected_payment": "PP", "billing_profile_id": "<SLUG>", "current_rate": {"rate": "1.0", "currency": "THB"}}'
# Expected: 400 with "Amount mismatch" error (order total ≠ 20 THB)
```

### TC-S4: H1 — Correct amount accepted

```bash
# Same order with correct grandTotal (order_total * 100 + fee * 100):
curl -X POST http://localhost:8000/api/payments/order-charge/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "<REAL_ORDER_ID>", "grandTotal": <CORRECT_AMOUNT>, "fee_calculated": <FEE>, "selected_payment": "PP", "billing_profile_id": "<SLUG>", "current_rate": {"rate": "1.0", "currency": "THB"}}'
# Expected: 201 with charge data
```

### TC-S5: M8 — Guest email mismatch rejected

```bash
curl -X POST http://localhost:8000/api/payments/order-charge/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "<GUEST_ORDER_ID>", "email": "wrong@email.com", ...}'
# Expected: 403 with "Email mismatch" error
```

### TC-S6: M8 — Guest correct email accepted

```bash
curl -X POST http://localhost:8000/api/payments/order-charge/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "<GUEST_ORDER_ID>", "email": "<ORDER_EMAIL>", ...}'
# Expected: 201 with charge data
```

### TC-S7: M17 — KakaoPay route works

```bash
curl -X POST http://localhost:8000/api/payments/order-charge/ \
  -H "Content-Type: application/json" \
  -d '{"order_id": "<ORDER_ID>", "selected_payment": "kakaopay", ...}'
# Expected: 201 (not 400 "Unknown payment method")
```

### TC-S8: H3 — Order reuse returns wrapped shape

```bash
# Send same request twice (idempotency key from cartId:total):
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "X-Idempotency-Key: <CART_ID>:<TOTAL>" \
  -d '...'
# Second response must have: {"message": "Order reused", "order": {...}}
# NOT bare OrderSerializer data
```

---

## 2. Manual Test Cases (QA, UI-based)

### TC-M1: H3 + H4 — Coupon apply after order creation (no toast error)

**Steps:**
1. Add trip to cart → proceed to checkout
2. Fill passenger details → reach payment step
3. Apply a coupon code
4. **Expected:** Coupon applies successfully. No "Payment processing failed" toast.
5. Remove coupon → re-apply → still works.

**Why:** Before H3 fix, coupon apply re-fetches order (idempotency reuse) → response shape mismatch → TypeError → generic error toast.

### TC-M2: H4 — QR cancel expires charge correctly

**Steps:**
1. Select PromptPay → generate QR code
2. Click "Cancel Payment" button
3. **Expected:** Order status returns to `ordering`. Countdown disappears.
4. Switch to another payment method → should work without 409.
5. Verify: `charge_created_at` is present → countdown shows real expiry window (not hardcoded 600s).

**Why:** Before H4 fix, `charge_id` was dropped from orderDetails → cancel button skipped expire call → order stuck `payment_pending`.

### TC-M3: M1 — QR path shows PendingChargeNotice on 409

**Steps:**
1. Start checkout → generate QR (order becomes `payment_pending`)
2. Open same cart in second tab → try to generate QR again
3. **Expected:** `PendingChargeNotice` appears with cancel affordance (not generic "Failed to generate QR code").
4. Click cancel on the notice → should expire the pending charge.

**Why:** Before M1 fix, QR path had no `pendingCharge` branch → 409 fell to generic error toast.

### TC-M4: M2 — Card flow handles alreadyPaid/amountLocked

**Steps:**
1. Start checkout → select credit card → complete 3DS payment
2. Do NOT close the page. Click "PAY NOW" again on the same form
3. **Expected:** Either redirect to order page (alreadyPaid) or show PendingChargeNotice (amountLocked). NOT silent no-op.

**Repeat for redirect payment (e.g., TrueMoney):**
1. Start TrueMoney payment → complete redirect
2. On return to checkout page, observe behavior
3. **Expected:** Same — redirect to order page or show PendingChargeNotice.

### TC-M5: M3 — Cancel state doesn't flash on method change

**Steps:**
1. Generate QR → click cancel → observe "Payment Cancelled" success state
2. Switch to credit card payment method
3. **Expected:** Cancel state clears silently. No "Payment Cancelled" alert flashes for one frame before clearing.
4. Switch back to PromptPay → no flash.

**Why:** Before M3 fix, `cancelState.success` cleared on every `selectedPayment` change (including re-renders where method didn't actually change) → one-frame flash of cancel UI.

### TC-M6: M17 — KakaoPay/Alipay method selection

**Steps:**
1. Start checkout → select KakaoPay (if available)
2. Click PAY NOW
3. **Expected:** No 400 error. Omise source created, redirect to KakaoPay.
4. If Alipay available: select Alipay → click PAY NOW → same expectation.

**Why:** Before M17 fix, FE sent `'kakaopay'` but BE PAYMENT_METHOD_MAP only had `'KP'` → 400. FE also lacked `ALIPAY` in `OMISE_SOURCE_TYPES`.

### TC-M7: H5 — Polling self-heals payment_pending with paid charge

**Steps (requires webhook block or timing):**
1. Generate PromptPay QR
2. Scan and pay the QR (complete PromptPay payment)
3. If webhook is delayed/lost, polling GET should still finalize the order
4. **Expected:** Order transitions from `payment_pending` → `paid` via polling self-heal within ~10s of polling.
5. Redirect to order confirmation page.

**Why:** Before H5 fix, reconcile gate excluded `payment_pending` → paid-but-unfinalized orders stuck forever with no recovery.

---

## 3. E2E / Integration Test Specs (developer-writes)

### TC-E1: H1 — Amount validation in `initiate_order_charge`

```python
# File: payments/tests/test_charge_security.py
class TestAmountValidation(TestCase):
    def test_mismatch_rejected(self):
        """H1: amount_thb - fee != order_total → ValueError"""
        # Create order with total 5000 THB
        # Call initiate_order_charge with amount_thb=20 + fee=0
        # Assert ValueError "Amount mismatch"

    def test_within_tolerance_accepted(self):
        """H1: within 1.00 THB tolerance → passes"""
        # Create order with total 5000.00 THB
        # Call initiate_order_charge with amount_thb=5000.50 + fee=0.50
        # Assert no error (0.00 diff)

    def test_fee_subtracted_correctly(self):
        """H1: fee-inclusive amount compared against fee-exclusive total"""
        # Create order with total 1000.00 THB
        # Call initiate_order_charge with amount_thb=1050 + fee=50
        # Assert no error (1050 - 50 = 1000)
```

### TC-E2: M8 — Guest email guard

```python
class TestGuestEmailGuard(TestCase):
    def test_guest_wrong_email_rejected(self):
        """M8: guest with mismatched email → 403"""
        # Create guest order with email='a@b.com'
        # POST order-charge with email='x@y.com'
        # Assert 403 "Email mismatch"

    def test_guest_correct_email_accepted(self):
        """M8: guest with matching email → proceeds"""
        # Create guest order with email='a@b.com'
        # POST order-charge with email='a@b.com'
        # Assert not 403

    def test_authenticated_user_skips_email_check(self):
        """M8: authenticated user → no email validation"""
        # Create user order
        # POST order-charge without email
        # Assert proceeds normally
```

### TC-E3: H5 — Reconcile gate includes `payment_pending`

```python
class TestReconcileGateExtension(TestCase):
    def test_payment_pending_self_heal(self):
        """H5: order in payment_pending + paid charge → finalize on GET"""
        # Create order with status='payment_pending'
        # Create GatewayCharge with status='paid'
        # GET /orders/{id}/orderdetails/
        # Assert order.status now 'paid'
        # Assert payment_finalized_at is set

    def test_double_finalize_guarded(self):
        """H5: already finalized order → no error on re-reconcile"""
        # Create order with status='paid', payment_finalized_at set
        # GET /orders/{id}/orderdetails/
        # Assert no exception, status stays 'paid'
```

### TC-E4: M5 — BaseError reverts order state

```python
class TestBaseErrorRevert(TestCase):
    @patch('payments.services.create_charge')
    def test_gateway_failure_reverts_order(self, mock_create):
        """M5: omise.errors.BaseError → order back to ordering"""
        # Create order with status='ordering'
        # Mock create_charge to raise omise.errors.BaseError
        # Call initiate_order_charge
        # Assert order.status == 'ordering'
        # Assert order.locked_amount is None
```

### TC-E5: M9 — Orphaned charge expired on IntegrityError

```python
class TestOrphanChargeExpire(TestCase):
    @patch('payments.gateway.get_omise_client')
    def test_integrity_error_expires_orphan(self, mock_client):
        """M9: concurrent IntegrityError → orphaned Omise charge expired"""
        # Mock omise_charge object with .expire() method
        # Mock IdempotencyKey save to raise IntegrityError
        # Call create_charge
        # Assert omise_charge.expire() was called
        # Assert ValueError raised
```

### TC-E6: H2 + M10 — Legacy routes return 410

```python
class TestLegacyRouteDeprecation(TestCase):
    def test_webhook_legacy_410(self):
        """H2: POST /api/payments/webhook-legacy/ → 410"""
        response = self.client.post('/api/payments/webhook-legacy/', {})
        self.assertEqual(response.status_code, 410)

    def test_placeorder_410(self):
        """M10: POST /api/placeorder/ → 410"""
        response = self.client.post('/api/placeorder/', {})
        self.assertEqual(response.status_code, 410)
```

### TC-E7: H3 — Order reuse response shape

```python
class TestOrderReuseResponseShape(TestCase):
    def test_idempotent_reuse_wrapped(self):
        """H3: reuse returns {"message", "order": {...}} not bare data"""
        # Create order via POST with idempotency key
        # POST again with same key
        # Assert response.data has keys "message" and "order"
        # Assert response.data["order"]["order_id"] exists
```

---

## Test Coverage Matrix

| Finding | Smoke | Manual | E2E Unit | Status |
|---------|-------|--------|----------|--------|
| H1 amount validation | TC-S3, TC-S4 | — | TC-E1 | ✅ syntax OK |
| H2 legacy webhook 410 | TC-S1 | — | TC-E6 | ✅ syntax OK |
| H3 order-reuse shape | TC-S8 | TC-M1 | TC-E7 | ✅ syntax OK |
| H4 charge_id in orderDetails | — | TC-M2 | — | ✅ build OK |
| H5 reconcile gate | — | TC-M7 | TC-E3 | ✅ syntax OK |
| M5 BaseError revert | — | — | TC-E4 | ✅ syntax OK |
| M8 guest email guard | TC-S5, TC-S6 | — | TC-E2 | ✅ syntax OK |
| M9 orphan charge expire | — | — | TC-E5 | ✅ syntax OK |
| M10 PlaceOrder 410 | TC-S2 | — | TC-E6 | ✅ syntax OK |
| M1 QR pendingCharge | — | TC-M3 | — | ✅ build OK |
| M2 card/redirect branches | — | TC-M4 | — | ✅ build OK |
| M3 cancelState flash | — | TC-M5 | — | ✅ build OK |
| M17 KakaoPay/Alipay | TC-S7 | TC-M6 | — | ✅ both OK |

**Total:** 8 smoke tests · 7 manual tests · 7 E2E test classes

---

## Related

[[payment-deep-review]] · [[payment-deep-review-verification]] · [[payment-implement-plan]] · [[payment-checkout-5-principles]] · [[payment-gateway-charge-architecture]]
