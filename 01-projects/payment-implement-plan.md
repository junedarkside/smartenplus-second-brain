# Payment Implement Plan (2026-06-12)

## Summary

5-batch production-safe fix sequence from [[payment-deep-review]] + [[payment-deep-review-verification]]. **20 findings confirmed, 1 REFUTED (M4 → retract, subsumed by M1), 1 KB inaccuracy (M8 in [[payment-backend-charge-flow]] §5).** No code changed yet — this is the implementer playbook.

## Pre-flight (mandatory)

1. Read [[payment-deep-review]] in full (HIGHs, MEDIUMs, Suggested fix order, Overturned/Corrected).
2. Read [[payment-deep-review-verification]] in full (per-finding verdicts, M4 refutation detail, KB inaccuracy note).
3. Verify your branch: `git -C smartenplus-backend status --short && git -C smartenplus-frontend status --short` must be clean (or only known carry-overs).
4. **Before Batch 2:** verify zero prod traffic on legacy routes:
   ```bash
   sudo grep -i "webhook-legacy\|placeorder" /var/log/nginx/access.log | wc -l
   # expect: 0
   ```
   If nonzero, escalate to user before proceeding.

## Code reuse contract (no new helpers, reuse what exists)

- **Expire charge:** `expirePendingCharge(email, chargeId, orderId, session)` in `getBillingAndOrder.js:201-231`. H4 + M1 fixes call this; delete inline fetches at `PaymentComponent.js:362-367`, `:388-391`.
- **Cancel payment:** `useCancelPayment` hook at `useCancelPayment.js:14-46`. M3 fix reuses this; delete `handleCancelPendingPayment` at `PaymentComponent.js:146-160`.
- **Order redirect URL:** extract `buildOrderRedirectUrl(session, orderId, email)` — 5× duplication (`PaymentComponent.js:328,347,618`; `QRPaymentForm.js:188`; `useOmisePayment.js:76`). Place in `helpers/payment/`. Out of scope for batches below; do not refactor unless touching the file.

---

## Batch 1 — H3 + H4 (~6 lines, kill 2 UX breakages)

### H3 (BE) — wrap reuse responses + move `cart` fetch
**File:** `smartenplus-backend/orders/views.py:258-289`

```python
# Move cart fetch above line 258 (idempotency check)
cart = Cart.objects.filter(id=cart_id).first()  # NEW

# Key-match reuse branch (existing_idempotency_order) — line 272-274
return Response({"message": "Order reused", "order": OrderSerializer(existing_idempotency_order).data}, status=200)  # CHANGE

# Cart-match reuse branch (existing_cart_order) — line 283-289
return Response({"message": "Order reused", "order": OrderSerializer(existing_cart_order).data}, status=200)  # CHANGE
```

**Verify:** apply coupon after order creation → no 500, success state.

### H4 (FE) — add `charge_id` + `charge_created_at` to `orderDetails`
**File:** `smartenplus-frontend/hooks/payment/useOmisePayment.js:148-157`

```js
const orderDetails = order_id ? {
    order_id, billing_profile_slug, total, grand_total,
    currency, coupon, expires_at, polling_interval,
    charge_id: data.charge_id,                    // ADD
    charge_created_at: data.charge_created_at,    // ADD
} : null;
```

**Verify:** generate QR → click cancel → wait 5s → `order.status` should be `ordering` (not `payment_pending`); countdown shows real expiry window.

---

## Batch 2 — H2 + M10 (delete legacy routes)

**Pre-check:** zero `webhook-legacy` and `placeorder` in nginx access logs (see pre-flight #4).

### H2 (BE) — 410 legacy webhook
**File:** `smartenplus-backend/orders/urls.py:28`

```python
# Replace PaymentWebhookViewSet route with:
path('webhook-legacy/', lambda r: HttpResponse("Deprecated", status=410)),
```

Verify: `git -C smartenplus-backend grep -i "webhook-legacy" payments/ cards/ orders/ webhooks/ 2>/dev/null` returns zero non-test hits (allow test fixtures).

### M10 (BE) — 410 PlaceOrderViewSet route
**File:** `smartenplus-backend/apis/urls.py:37`

```python
# Replace router.register('placeorder', ...) with:
path('placeorder/', lambda r: HttpResponse("Deprecated", status=410)),
```

Verify: same grep pattern for `placeorder` returns zero non-test hits.

---

## Batch 3 — H1 + M8 (security pair)

### H1 (BE) — server-side amount validation
**File:** `smartenplus-backend/payments/services.py` (after `initiate_order_charge` Decimal-casts at `:576`)

```python
order_total = order.get_total_cost_after_discount()
if order_total and abs((amount_thb - fee) - order_total) > Decimal('1.00'):
    raise ValueError(f"Amount mismatch: submitted {amount_thb - fee}, order total {order_total}")
```

**Critical fee note:** `fee_calculated` is always in THB — computed as percentage of THB order total at `orders/views.py:1582-1589` regardless of display currency. Compare `(amount_thb - fee)` vs `order_total` (fee-inclusive amount - fee = fee-exclusive net).

**Verify:** `POST /payments/order-charge/ {grandTotal: 2000}` against a 5000 THB order → 400 with mismatch error. Tolerance 1.00 THB covers FX rate rounding.

### M8 (BE) — guest email validation
**File:** `smartenplus-backend/payments/views.py:106-109`

Mirror the pattern at `payments/views.py:375-376`:
```python
if not request.user.is_authenticated:
    if not data.get('email') or order.email != data['email']:
        return Response({'error': 'Email mismatch'}, status=403)
```

**Verify:** guest with mismatched email → 403.

---

## Batch 4 — H5 + M5 (resilience pair)

### H5 (BE) — extend reconcile gate to `payment_pending`
**File:** `smartenplus-backend/orders/views.py:634`

```python
# Change: order.status in ('ordering', 'payment_failed')
# To:     order.status in ('ordering', 'payment_failed', 'payment_pending')
```

**Safety:** `payment_finalized_at` guard in `finalize_payment` (`payments/services.py:294-302`) prevents double-finalize. Minor DB overhead only (reads latest `GatewayCharge` on polling GET during in-flight).

### H5 (FE) — `useQRPolling` UX on stuck `payment_pending`
**File:** `smartenplus-frontend/hooks/payment/useQRPolling.js:88-91`

When `charge_status='paid'` + `order_status='payment_pending'`: treat as "Processing — contact support if persistent" rather than re-polling forever. Stop polling, surface message.

### M5 (BE) — catch `omise.errors.BaseError` and revert
**File:** `smartenplus-backend/payments/services.py` in `initiate_order_charge`, around the `create_charge` call at `:737`

```python
try:
    gateway_charge = create_charge(...)
except omise.errors.BaseError:
    order.status = 'ordering'
    order.locked_amount = None
    order.save(update_fields=['status', 'locked_amount'])
    raise
```

**Verify:** monkeypatch `omise.errors.BaseError` in test → order reverts to `ordering`; no `payment_pending` stuck state.

### H5 end-to-end verify
Block outbound webhooks (firewall) + complete PromptPay scan → polling GET should trigger `finalize_payment` via the extended gate.

---

## Batch 5 — M1–M4 (M4 retracted), M17, LOW sweep

### M1 (FE) — add `pendingCharge` branch in QR path
**File:** `smartenplus-frontend/components/Payment/PaymentComponent.js:307-337`

Add `else if (result?.pendingCharge)` between `:326` and `:331`, mirroring the card/redirect branch at `:440-446`.

### M2 (FE) — consume `alreadyPaid`/`amountLocked` in card/redirect
**File:** `smartenplus-frontend/components/Payment/PaymentComponent.js:437-470`

Add branches for `result?.alreadyPaid` (order already paid) and `result?.amountLocked` (amount locked). Surface UI state, not silent no-op.

### M3 (FE) — guard `cancelState` reset effect
**File:** `smartenplus-frontend/components/Payment/PaymentComponent.js:523-527`

Add `prevMethodRef` to skip reset if method didn't actually change. Prevents one-frame flash.

### M17 (contract) — KakaoPay + Alipay
- **BE:** `smartenplus-backend/payments/views.py:35-49` — add `'kakaopay': OmiseMethod.KAKAO_PAY` to `PAYMENT_METHOD_MAP`.
- **FE:** `smartenplus-frontend/helpers/payment/paymentMethods.js` — verify `OMISE_SOURCE_TYPES` has `ALIPAY: 'alipay'`. Add if missing.

### M4 — RETRACT
M4 is subsumed by M1 (both target `pendingCharge` UX surface in QR path). Update [[payment-deep-review]] to add a "Retracted" section noting M4 → retracted (M1 covers it).

### LOW sweep (batched, low-risk)

**FE dead code:**
- `useOmisePayment.js:7` — dead `cartActions` import
- `useOmisePayment.js:39-56` — `OmiseScriptLoader` dead exports
- `useOmisePayment.js:51` — linear backoff labeled "exponential" (fix comment)
- `useOmisePayment.js:282` — round card-dialog amount
- `paymentMethods.js:6-20, :49-68` — unused `ALIASES`/`PAYMENT_UI_CONFIG`
- `useOmisePayment.js:135-146` — move GTM `purchase` to `finalize_payment` success
- `pages/orders/[orderid].js:106-110` — fix `hasSuccessfulCharge` "any paid" scan
- `PaymentComponent.js:502-507` — add `qrCodeImage` dep
- `PaymentComponent.js:740-743` — dead `onPaymentRedirect` prop
- `PaymentComponent.js:240-271` — move `paymentState` derivation to `useMemo`
- `pages/orders/[orderid].js:14` — fix `TERMINAL_STATUSES` vocab (add `canceled`/`refunded`, remove `cancelled`/`confirmed`)
- `useQRPolling.js:57-60` — remove dead polling formats 2-4 + empty-order `[]` truthy poll
- `useQRPolling.js:105-111` — remove `'FAILED'/'EXPIRED'` dead status checks
- `getBillingAndOrder.js:242` — delete `getReconcileOrder` zero-caller

**BE dead/bug fixes:**
- `orders/serializers.py:339` — add `'partial_refunded'` to terminal list
- `payments/views.py:414-421` + `payments/management/commands/expire_stale_payments.py:43-49` — fix inner except (outer reconcile branch unreachable)
- `payments/services.py:16-25` — add `reversed`/unknown Omise status default + `PROCESSING`/`PARTIAL_REFUNDED` assignments
- `payments/views.py:165` vs `billings/models.py:103-127` — fix `polling_interval` lookup mismatch
- `payments/signals.py:5` — delete dead `payment_charge_created` signal
- `payments/views.py:344-345` — fix `RefundCreateView` bare `except Exception` (currently mislabels all errors as duplicate-ID)
- `useOmisePayment.js:199-233` vs `payments/services.py:140` — unify LINE Pay source creation (pick one owner)

**Carry-overs:**
- `useCartSync.js:317-335` — finish `stable_id` sweep (now comment-only in source)
- `BookButton.js:8` — dead `useCheckCartIdQuery` import
- `BookButton.js:45` — unused `[result, setResult]`

### M7 — over-refund guard (deferred to separate audit)
Both refund endpoints (`POST /admin-dashboard-charge/refund/` at `cards/views.py:53-140` and `POST /payments/refund/` at `payments/views.py:322-351`) need cumulative sum guard. Defer to a dedicated refund audit; do not bundle with PAYMENT-FIX.

---

## Doc drift fixes (`smartenplus-backend/docs/technical/PAYMENT_SYSTEM.md`)

After Batch 2 ships:
- Document polling self-heal gate (`ordering`/`payment_failed`/`payment_pending` per H5).
- Correct "Card = no expiry (synchronous)" → false for 3DS redirect charges (per M12).
- Add `payment_failed→payment_pending` and `canceled→ordering` to state machine.
- Add legacy webhook + `placeorder` routes as 410 (or remove after Batch 2).

After Batch 5:
- Add `partial_refunded` to terminal list.
- Add KakaoPay + Alipay to method contract.
- Document over-refund guard pattern (M7, after deferred fix).

---

## Test gaps to close (`smartenplus-backend/payments/tests/`)

- `PaymentAmountMismatchError` raise + swallow paths
- Webhook EXPIRED→successful recovery
- `expire_stale_payments` command (no test file)
- `omise.errors.BaseError` failure leaving order stuck (M5)
- `ChargeOrderView` amount math + non-THB/JPY
- Concurrent `create_charge` IntegrityError + orphaned Omise charge (M9)
- Over-refund cumulative amount (M7, deferred)
- Reconcile throttle + superseded skip
- Expire-vs-webhook TOCTOU
- Guest cross-user charge initiation (M8)
- Reuse response shape (H3)
- `payment_pending` reconcile gate (H5)

---

## KB corrections to ship with this work

1. `payment-backend-charge-flow.md` §5 — clarify guest email validation is **only** in `ExpirePendingChargeView`, **missing** in `ChargeOrderView`.
2. 12 KB gaps (atomization candidates) — defer to next `/lint-vault` session (split into 2 sessions: 1–6 first, 7–12 follow).

---

## Verification (end-to-end, after each batch)

```bash
# Batch 1
curl -X POST /api/orders/create/ -H "X-Idempotency-Key: ${cartId}:${total}" -d '...'
# expect: response.order.order_id present
# UI: generate QR → cancel → order.status = 'ordering'

# Batch 2
curl -X POST /api/payments/webhook-legacy/ -d '{...}'
# expect: HTTP 410 "Deprecated"
git -C smartenplus-backend grep -i "webhook-legacy\|placeorder" payments/ cards/ orders/ apis/

# Batch 3
curl -X POST /api/payments/order-charge/ -d '{"grandTotal": 2000, "email": "x@y.com"}'
# expect: 400 (mismatch) for valid order_id
curl -X POST /api/payments/order-charge/ -d '{"grandTotal": X, "email": "wrong@email.com"}'
# expect: 403 (email mismatch) for guest

# Batch 4 (manual + simulated)
# Block outbound webhooks → complete PP scan → polling GET should finalize
# Monkeypatch omise.errors.BaseError → verify order reverts to ordering

# Lint + test
cd smartenplus-frontend && pnpm lint && pnpm test
cd smartenplus-backend && ruff check . && python manage.py test payments
```

After all batches: re-run the "Verified clean" checklist from `master-state.md` #101 (finalize_payment SSOT, select_for_update, locked_amount symmetry, payment_failed recoverable, 3 expiry paths, polling vocab, 409 mapping, cart reset/reprovision, isPaymentLocked manual-clear, countdown from backend `expires_at`).

---

## Out of scope (deliberate)

- M7 over-refund guard (deferred to dedicated refund audit)
- KB atomization (12 gaps, defer to `/lint-vault`)
- LOW items not in this doc
- Cross-sell / BD / AT-1 workstreams

## Related

[[payment-deep-review]] · [[payment-deep-review-verification]] · [[omise-api-reference]] · [[payment-checkout-5-principles]] · [[payment-gateway-charge-architecture]] · [[payment-finalize-deep-dive]] · [[payment-exception-catalog]] · [[payment-charge-service-layer]] · [[payment-frontend-flow-mechanics]] · [[payment-qr-polling-mechanics]] · [[refund-flow]] · [[payment-status-enums]] · [[payment-backend-charge-flow]]
