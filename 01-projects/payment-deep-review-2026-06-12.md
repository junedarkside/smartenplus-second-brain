# Payment Deep Review — FE + BE (2026-06-12)

## Summary

3-agent team (frontend reviewer, backend reviewer, cross-repo contract reviewer) + leader hand-verification of every HIGH + debug-mantra falsification pass (2026-06-12). Scope: entire Omise payment surface, both repos. Extends [[booking-payment-e2e-audit-2026-06-11]] (closed) — zero overlap re-derived; focus on charge initiation, webhooks, refunds, expiry, contracts. **Result: 5 HIGH (all leader-verified + falsified), ~18 MEDIUM, ~15 LOW, 10 named test gaps, 4 doc drifts.** Report only — no code changed.

---

## HIGH — leader-verified + falsification-tested

### H1 — Charge amount client-controlled, never validated against order total (BE)
**Fail path:** `payments/views.py:117-119` computes `amount_thb = (Decimal(str(grand_total)) / 100 / currency_rate_val)` from request body only. `initiate_order_charge` (`services.py:556+`) never calls `order.get_total_cost_after_discount()` for comparison. `locked_amount` (`services.py:683`) and finalize's mismatch check (`services.py:304-315`) both derive from same client value — self-validating closed loop. Floor check (`views.py:122-124`) is per-currency minimum, not order total.

**Repro (no runtime needed):** Send `POST /payments/order-charge/` with `grandTotal: 2000` (= 20 THB) against a 5,000 THB order. View accepts it, `initiate_order_charge` transitions to `payment_pending`, Omise charged 20 THB, webhook fires, `finalize_payment` called with `gc.amount=20` — `locked_amount=20` so mismatch check passes — order finalized as paid.

**Falsification attempt:** Could CheckoutSnapshot block it? → `services.py:~318-322` comment: "log-only — do NOT block payment". Attempt fails; H1 stands.

**Fix:** In `initiate_order_charge` after line 576 (after `amount_thb`/`fee` Decimal-cast), add:
```python
order_total = order.get_total_cost_after_discount()
if order_total and abs((amount_thb - fee) - order_total) > Decimal('1.00'):
    raise ValueError(f"Amount mismatch: submitted {amount_thb - fee}, order total {order_total}")
```
**⚠️ Why `amount_thb - fee`:** FE sends `grandTotal = trip_total + fee - discount` (fee-inclusive, `PaymentComponent.js:257-261`), so `amount_thb` is fee-inclusive. `order.get_total_cost_after_discount()` returns trip-cost minus discount only — no fee (`orders/models.py:260-266`). `order.gateway_fee_and_vat` is set AFTER `initiate_order_charge` returns (`services.py:723`), so it's not yet available. Comparing `amount_thb` directly against order total would false-positive on every payment. Subtracting the `fee` param (already passed in, in THB) makes the comparison equivalent. Tolerance 1.00 THB covers rate-conversion rounding. **Currency note:** `fee_calculated` is always in THB — `GET /api/payment-methods/{order_id}/` computes it as a percentage of the THB order total (`orders/views.py:1582-1589`), regardless of display currency. Fix assumes no non-THB payments reach this path (consistent with current FX-rate-based approach in the same view).

---

### H2 — Legacy webhook live, unverified, bypasses finalize_payment (BE)
**Fail path:** `orders/urls.py:28` → `PaymentWebhookViewSet` (`orders/views.py:759`). Verification block `orders/views.py:766-772` commented out with `# if not verify_omise_event(...)`. `AllowAny`. For any matching `cards.Charge` row: sets `order.status='paid'` directly (`views.py:913-914`), re-increments coupon (`views.py:975-978`), re-confirms bookings — no `payment_finalized_at`, no `select_for_update`. Bypasses `finalize_payment` SSOT.

**Repro:** POST forged `{"key":"charge.complete","data":{"id":"chrg_xxx"}}` to `/api/payments/webhook-legacy/` where `chrg_xxx` is any `cards.Charge.gateway_charge_id`. No auth required. Order set paid, coupon over-decremented.

**Falsification attempt:** Are there zero remaining `cards.Charge` rows? → `PlaceOrderViewSet` (M10, `apis/urls.py:37`) still creates them. Cannot assume zero rows.

**Fix:** Delete route (or `lambda r: HttpResponse("Deprecated", status=410)` matching the stripe-webhook pattern 2 lines below in `orders/urls.py:30`). Verify zero prod traffic in access logs first.

---

### H3 — Idempotent order-reuse returns wrong response shape → breaks checkout refetch (contract)
**Fail path (shape mismatch):** Reuse branches return bare `OrderSerializer(order).data` — `orders/views.py:272-274` (key-match) and `:283-289` (cart-match). Create path returns `{"message": "...", "order": serializer.data}` — `views.py:535-539`. FE always reads the wrapped shape: `orderData?.order?.billing_profile_slug` (`usePaymentInitialization.js:58`) and **unguarded** `orderData.order.order_id` (`:74`) → `TypeError: Cannot read properties of undefined (reading 'order_id')` → caught at `:83` → `GENERIC_ERROR` → "Payment processing failed" toast.

**Fail path (NameError):** Keyless branch `views.py:278-289` uses `cart` in `Order.objects.filter(cart=cart,...)`. `cart` first assigned at `views.py:326` (after billing profile steps). Any client omitting `X-Idempotency-Key` header with an existing order → `NameError: name 'cart' is not defined` → 500.

**Trigger scope:** FE always sends `X-Idempotency-Key: ${cartId}:${total}` (`usePaymentInitialization.js:38-44`), stable while cart unchanged. Every same-cart refetch hits the key-match reuse branch: coupon apply (`usePaymentCouponManager.js:26`), cancel-pending recovery (`PaymentComponent.js:157`).

**Repro:** Start checkout → reach payment step (order created) → apply a coupon code → observe "Payment processing failed" toast. No edge case needed; happens on first coupon attempt after order creation.

**Falsification attempt:** Could `orderData?.order` optional-chaining at line 58 prevent the TypeError? → Yes for line 58 (`billingSlug` = undefined), but line 74 is **unguarded**: `await getCreateBooking(orderData.order.order_id, ...)` — no optional chaining → throws. Falsification fails; H3 stands.

**Extra breadcrumb:** `setOrderCreationSuccess` guard (`usePaymentInitialization.js:55`) checks `orderData.message === "Order created successfully"`. Create response uses key `"message"` (correct, `views.py:536`). Reuse response is bare — no `"message"` key → `undefined !== string` → `setOrderCreationSuccess` always false on reuse path. Already subsumed by H3.

**Fix (BE, ~4 lines):**
```python
# Key-match reuse branch (views.py:272-274) — variable is existing_idempotency_order:
return Response({"message": "Order reused", "order": OrderSerializer(existing_idempotency_order).data}, status=200)
# Cart-match reuse branch (views.py:283-289) — variable is existing_cart_order:
return Response({"message": "Order reused", "order": OrderSerializer(existing_cart_order).data}, status=200)
# Keyless NameError fix: move cart fetch to before the idempotency key check (line 258)
cart = Cart.objects.filter(id=cart_id).first()  # move above line 258
```

---

### H4 — Explicit QR cancel never expires the charge: `charge_id` dropped from orderDetails (FE)
**Fail path:** BE order-charge response includes `charge_id` (from `GatewayChargeSerializer`) and `charge_created_at` (`payments/views.py:161-162`). `useOmisePayment.js:118-128` destructures only 8 fields — no `charge_id`, no `charge_created_at`. `orderDetails` object at `:148-157` omits both. `handleConfirmLeave` reads `qrState.orderDetails?.charge_id` (`PaymentComponent.js:385`) — always `undefined` → `if (chargeId)` at `:386` is false → expire call skipped → user navigates away → order stays `payment_pending` + `locked_amount` set until C3b proactive PP expiry runs.

**Secondary effect:** `QRPaymentForm.js:71-75` reads `orderDetails.charge_created_at` for countdown total → always `undefined` → `initialTotalRef` never set → countdown always falls back to 600s regardless of actual charge expiry window.

**Reverse drift (dead code):** FE destructures `billing_profile_slug`/`total`/`coupon` at `useOmisePayment.js:120-125` — none of these are in the BE order-charge response (`payments/views.py:155-166`); always `undefined`. BE also sends `failure_code` (`GatewayChargeSerializer:62`) which FE never reads — critical consequence covered by M13.

**Repro:** Generate QR → click cancel/navigate away → check order status → still `payment_pending` with locked amount; next cart action 409s until TTL.

**Falsification attempt:** Could `qrState` be populated from a different source that includes `charge_id`? → `qrState.orderDetails` is only set from `handleQRPayment` result at `PaymentComponent.js:313` and `handleOmiseRedirectPayment` at `:484` — both from `triggerOmiseSourcePayment` → `useOmisePayment.processPayment` return value → the `orderDetails` object in scope. No other writer. Attempt fails.

**Fix (2 lines in `useOmisePayment.js:148-157`):**
```js
const orderDetails = order_id ? {
    order_id, billing_profile_slug, total, grand_total,
    currency, coupon, expires_at, polling_interval,
    charge_id: data.charge_id,           // ADD
    charge_created_at: data.charge_created_at,  // ADD
} : null;
```

---

### H5 — Paid-but-unfinalized order invisible and unrecoverable in UI (contract)
**Fail path A — amount mismatch:** Webhook `_handle_order_paid` (`payments/views.py:271-285`) catches `PaymentAmountMismatchError` and swallows it (by design — re-raise would rollback the `GatewayCharge.status=PAID` row). Charge = `paid` at Omise + in DB. Order stays `payment_pending`. No recovery path is triggered.

**Fail path B — lost webhook:** Polling GET `/orders/{id}/orderdetails/` self-heal gate is `order.status in ('ordering', 'payment_failed')` (`orders/views.py:634`). `payment_pending` is explicitly excluded. If the webhook is lost/delayed, no amount of polling heals the order.

**FE consequence:** `useQRPolling.js:88-91` stops polling and sets success when `charge_status === 'paid'`; `QRPaymentForm.js:180-196` redirects to order page with "Payment Successful". Order page polls 30s then displays pending. No email. No booking confirmation. No UI recovery affordance.

**Repro (path A):** Requires a charge amount mismatch — only possible if H1 is also exploited (client sends wrong amount) or if `locked_amount` drift occurs via race. Low frequency in production. **Runtime confirmation needed before marking confirmed.**

**Repro (path B):** Omise webhook delivery fails (network partition, server restart) while order is `payment_pending` with a paid charge. Deterministic from code; manual test: block outbound webhooks, complete PromptPay scan → order never finalizes.

**Falsification attempt:** Does explicit `/reconcile` POST cover `payment_pending`? → `orders/views.py:661` — `ReconcileView` is a separate POST, not called automatically. FE `getReconcileOrder` helper has zero callers (confirmed earlier audit). So no automatic reconciliation path exists. H5 stands.

**Fix:**
- BE: add `'payment_pending'` to the reconcile gate at `orders/views.py:634` (the finalize branch immediately below already handles this case). Safe: `payment_finalized_at` guard in `finalize_payment` (`services.py:294-302`) prevents double-finalization. Minor DB overhead: reads latest `GatewayCharge` on each polling GET during normal in-flight state, but the early-exit when `gc.status != PAID` is cheap.
- FE: in order page polling logic, treat `charge_status='paid'` + `order_status='payment_pending'` as "Processing — if this persists contact support" rather than re-polling indefinitely

---

## MEDIUM

Leader-verified: M1 ✓, M4 ✓, M5 ✓ (corrected), M8 ✓. Others agent-cited with file:line; spot-check each claim before fixing.

- **M1 ✓ (FE)** PromptPay lacks `pendingCharge` branch — `handleQRPayment` (`PaymentComponent.js:307-337`) handles `amountLocked`/`alreadyPaid` only; 409 `pending_charge_exists` falls to generic "Failed to generate QR code". Card/source flows have the branch at `:437-448`. Fix: add `else if (result?.pendingCharge)` mirroring `:440-446`.
- **M2 (FE)** `alreadyPaid`/`amountLocked` unconsumed in card/redirect flows (`PaymentComponent.js:437-470`) → PAY NOW silent no-op when order already paid or amount locked.
- **M3 (FE)** `cancelState.success` cleared instantly by method-change effect with no prev-method check (`PaymentComponent.js:523-527`) — "Payment Cancelled" alert flashes one frame.
- **M4 ✓ (contract)** GAP-2 cross-order 409 body `{error:'payment_pending'}` (`services.py:660-664`) not in FE's 409-mapping table (`useOmisePayment.js:169-178` checks `pending_charge_exists` only) → generic toast, no cancel affordance despite `charge_id` supplied.
- **M5 ✓ corrected (BE)** Order transitions to `payment_pending`+`locked_amount` at `services.py:683` before `create_charge` call at `:737`. If `create_charge` raises `omise.errors.BaseError` (Omise API down/gateway error), it re-raises bare (`services.py:155-158`) → not in view's catch list (`views.py:140-154`) → 500. Order stuck `payment_pending` with no `GatewayCharge` row. **Correction from original:** `IntegrityError` is caught inside `create_charge` and re-raised as `ValueError` (`:192-194`) — view catches this as 409, not 500. Only `omise.errors.BaseError` (gateway failure) produces the stuck state. Fix: wrap `create_charge` in `except omise.errors.BaseError` in `initiate_order_charge`; on failure revert `status='ordering', locked_amount=None`.
- **M6 (BE)** Lock contention: `ApplyCouponView` locks Coupon via `select_for_update()` (`orders/views.py:1184`) then writes Order. `finalize_payment` locks Order via `select_for_update()` (`services.py:294`) then issues `UPDATE SET times_used = times_used + 1` on Coupon (`services.py:356-357`) — PostgreSQL UPDATE acquires an implicit row lock. If `ApplyCouponView` holds the Coupon lock concurrently, `finalize_payment` blocks until `ApplyCouponView` commits. **Not a classic AB-BA deadlock** (`ApplyCouponView` does not wait for the Order lock) but a blocking contention window during `status='ordering'`. Risk: `finalize_payment` delayed on every concurrent coupon apply; under high concurrency this could trigger webhook timeout retries. Fix: add `select_for_update()` on `order.coupon` inside `finalize_payment`'s existing Order lock scope to make lock ordering consistent.
- **M7 (BE)** Refunds: no over-refund guard in either recorder. Two live endpoints: `POST /admin-dashboard-charge/refund/` → `cards/views.py:53-140` (admin-dashboard-facing, mounted via `Smartenplus/urls.py:31`); `POST /payments/refund/` → `payments/views.py:322-351` (API-facing, mounted via `urls.py:36`). Neither validates cumulative sum. Order math in `cards/views.py:88-90` sums refunds across ALL charges for the order vs one charge's `total_amount` — can show misleading partial/full state. `GatewayCharge.status` never transitions to `refunded`/`partial_refunded`. Coupon `times_used` never decremented on refund. Fix priority: guard in both views — reject when `existing_refunds_total + request_amount > charge.amount`; set `GatewayCharge.status` accordingly.
- **M8 ✓ (BE/contract)** Guest charge initiation requires no email match — `payments/views.py:109` looks up by `user__isnull=True` only; FE sends `email` in body but BE never reads it. Any user knowing a guest `order_id` can initiate charges on it. Fix: validate `order.email == data['email']` for unauthenticated requests (mirror `payments/views.py:374-377`).
- **M9 (BE) narrowed** Concurrent `create_charge`: the `IntegrityError` path inside `create_charge` re-raises as `ValueError` → view returns 409 (NOT 500 + stuck — corrected). The orphaned-charge scenario requires both concurrent requests to complete the Omise API call (`client.Charge.create`) before either writes the `GatewayCharge` row. Narrow window (Omise latency ~200ms), low but non-zero probability. If the losing request's Omise charge is then paid by the user, webhook returns `not_found` → money captured, order never finalized. Fix confirmed feasible: at `services.py:192`, `omise_charge` IS in scope (Omise API call precedes the `transaction.atomic()` insert block) — `omise_charge.expire()` is callable. Add inside the `except IntegrityError` handler before re-raise.
- **M10 (BE)** `PlaceOrderViewSet` still routed (`apis/urls.py:37` → `carts/views.py:281-413`) — creates legacy `cards.Charge`, sets `order.status='paid'` directly, deletes cart. Second finalization path; feeds H2 attack surface. Fix: 410.
- **M11 (BE)** `OrderViewSet.create` guest `get_or_create(user=None, status='ordering')` with no cart filter (`orders/views.py:120-135`) matches ANY other guest's in-flight order globally. Fix: deroute or add `cart=cart`.
- **M12 (BE)** Card 3DS charges excluded from all self-heal sweeps: `sync_pending_charges` skips cards (`tasks.py:76-80`); no `METHOD_EXPIRY` card entry; `expire_stale_payments` not in beat schedule; reconcile gate excludes `payment_pending`. Missed `charge.complete` webhook → stuck pending forever.
- **M13 (FE)** Charge response `status`/`failure_message` never read (`useOmisePayment.js:118-128`) — declined card returning 201 `status='failed'` (`create_charge` sets `status=map_omise_status('failed')=PaymentStatus.FAILED`, view returns HTTP 201 unconditionally). `processPayment` returns `{success:true}` with no `authorize_uri`. `PaymentComponent.js` `handleClick` sees `result.success === true`, sets no state, dispatches nothing — completely silent. User left on payment form with `payment_pending` order and no error message. Fix: read `data.status` after destructure; if `status === 'failed'`, set `success:false` + surface `data.failure_message`.
- **M14 (FE)** Coupon `isProcessing` stuck `true` if refetch throws (`usePaymentCouponManager.js:19-32`) — reset only in order-change effect at `:69`. Subsequent coupon clicks silently swallowed. Compounded by H3.
- **M15 (FE)** Polling silently stops on any 4xx (`useQRPolling.js:122-125`, `:258-261`) with no UI state — QR looks live; success undetectable after.
- **M16 (FE)** `usePaymentInitialization` cleanup closes over registering-run's `formStep` (always false, `:199-204`); `initialized.current` never reset by navigation; stale booking payload on back-navigate with unchanged total.
- **M17 (contract)** KakaoPay dead end-to-end: FE sends `'kakaopay'` (`paymentMethods.js:74`); `PAYMENT_METHOD_MAP` has `'KP'` → `OmiseMethod.KAKAO_PAY='kakao_pay'` only (`payments/views.py:35-49`); `OmiseMethod.values` fallback also won't match `'kakaopay'` vs `'kakao_pay'` → 400 after Omise source already created. ALIPAY dead FE-side: no `OMISE_SOURCE_TYPES` key. Fix: add `'kakaopay': OmiseMethod.KAKAO_PAY` to `PAYMENT_METHOD_MAP`; add `ALIPAY: 'alipay'` to FE `OMISE_SOURCE_TYPES`.
- **M18 (contract)** `Payment.amount_paid = amount_thb + fee` (`services.py:706`) double-counts fee (FE `grandTotal` already fee-inclusive per `PaymentComponent.js:254-261`); Payment row never updated by `finalize_payment` — stays `authorized` forever. Reporting only; charge flow correct.

---

## LOW (terse)

**FE:** dead `cartActions` import `useOmisePayment.js:7` · OmiseScriptLoader dead exports (`OmiseCard`/`OmiseInstance` never assigned/imported) + retry non-looping + linear backoff under "exponential" comment (`:39-56, :51`) · card-dialog amount unrounded (`useOmisePayment.js:282`) · `ALIASES`/`PAYMENT_UI_CONFIG` zero importers (`paymentMethods.js:6-20, :49-68`) · GTM `purchase` fires at charge creation not payment success (`useOmisePayment.js:135-146`) · `hasSuccessfulCharge` "any paid charge" scan inert-but-contra-canonical on both order pages (`[orderid].js:106-110`) · missing `qrCodeImage` dep (`PaymentComponent.js:502-507`) · dead `onPaymentRedirect` prop (`:740-743`) · derived `paymentState` in useEffect not useMemo (`:240-271`) · `TERMINAL_STATUSES` uses `'cancelled'`/`'confirmed'` which backend never emits; misses `canceled`/`refunded` (`pages/orders/[orderid].js:14`) · QR polling formats 2–4 dead + empty-order `[]` truthy polls to timeout (`useQRPolling.js:57-60`) · legacy order-status checks `'FAILED'/'EXPIRED'` dead (`:105-111`) · `getReconcileOrder` posts to wrong path, zero callers (`getBillingAndOrder.js:242`) · `partial_refunded` missing from BE terminal list → FE polls forever (`orders/serializers.py:339`).

**BE:** expire-view inner except swallows "already paid" → customer sees failure-then-success (`payments/views.py:414-421` — inner except unconditionally marks EXPIRED; outer reconcile branch `:431-448` unreachable; same in `expire_stale_payments.py:43-49`) · `reversed`/unknown Omise statuses default PENDING forever; `PROCESSING`/`PARTIAL_REFUNDED` never assigned (`services.py:16-25`) · `polling_interval` lookup compares Omise long codes to `PP`-style choices — never matches, always 10000 (`views.py:165` vs `billings/models.py:103-127`) · dead signal `payment_charge_created`; sent signals have no prod receivers (`signals.py:5`) · `RefundCreateView` bare `except Exception` mislabels all errors as duplicate-ID (`views.py:344-345`) · LINE Pay: FE creates orphan `line_pay` source BE never reads; BE makes its own `rabbit_linepay` (`useOmisePayment.js:199-233` vs `services.py:140`).

---

## Duplication / reuse (FE)
- Expire-charge implemented 3×: helper `expirePendingCharge` (`getBillingAndOrder.js:201-231`) + 2 inline fetches (`PaymentComponent.js:362-367`, `:388-391`) — use the helper.
- Order-redirect URL built 5× (`PaymentComponent.js:328, 347, 618`; `QRPaymentForm.js:188`; `useOmisePayment.js:76`) — one `buildOrderRedirectUrl(session, orderId, email)` justified.
- `handleCancelPendingPayment` (`PaymentComponent.js:146-160`) re-implements `useCancelPayment.js:14-46`.

Size (refactor-on-touch only): `checkout/index.js` 1201 · `PaymentComponent.js` 787 · `getBillingAndOrder.js` 470 · `QRPaymentForm.js` 366 · `useCartSync.js` 335.

---

## Carried-over open items (status 2026-06-12)
- `stable_id`: now comment-only in source + 2 test files; `useCartSync` Effect 6 still present (`:317-335`) — finish sweep.
- `BookButton`: line 41 `checkCart` now used; residual dead `useCheckCartIdQuery` import (line 8) + unused `[result, setResult]` (line 45).
- Celery retry wired-but-uncalled: CONFIRMED (`tasks.py:14` config inert; per-item swallowing is correct behavior — delete the retry kwargs).
- `OrderDetailsViewSet` throttle: global `AnonRateThrottle` 500/h applies (`settings.py:405-415`) — not unthrottled, just untightened.
- `random.choice` order IDs: confirmed (`orders/utils.py:34-43`).

---

## Verified clean (this pass)
`finalize_payment` SSOT across all 6 modern call sites; `select_for_update` + `payment_finalized_at` guard; `locked_amount` set/enforce/reset symmetric; `payment_failed` recoverable; all 3 expiry paths call `_send_payment_failed_notifications()`; webhook dedup double-layer + superseded guard + EXPIRED→successful recovery; canonical = latest charge both lookups; `expires_at` ISO + `USE_TZ=True` correct, FE `new Date()` handles offset; minor units round-trip exact THB + correct JPY; all CLAUDE.md FE gotchas re-verified compliant (polling vocab `'successful'||'paid'`, cart reset/reprovision on order pages, guest email rules, 409 mapping for 3 known codes, `isPaymentLocked` manual-clear only, countdown from backend `expires_at`).

---

## Test gaps (payments/tests/)
`PaymentAmountMismatchError` raise + swallow paths · webhook EXPIRED→successful recovery · `expire_stale_payments` command (no test file) · charge-creation `omise.errors.BaseError` failure leaving order stuck (M5) · `ChargeOrderView` amount math + non-THB/JPY · concurrent `create_charge` IntegrityError + orphaned Omise charge (M9) · over-refund cumulative amount · reconcile throttle + superseded skip · expire-vs-webhook TOCTOU · guest cross-user charge initiation (M8).

---

## Doc drift (PAYMENT_SYSTEM.md)
- Polling self-heal gate (`ordering`/`payment_failed` only, excludes `payment_pending`) undocumented
- "Card = no expiry (synchronous)" false for 3DS redirect charges
- State machine omits `payment_failed→payment_pending` and `canceled→ordering` transitions
- Legacy webhook + `placeorder` routes undocumented, contradicting SSOT claim
- **`payment-backend-charge-flow.md` §5** (added by verification pass 2026-06-12) — claims `ChargeOrderView` validates `email` for guest; code shows it's only in `ExpirePendingChargeView`. Edit §5 to clarify.

---

## Overturned / corrected (discipline record)
- **H1 fix formula:** original used `amount_thb` vs `order.get_total_cost_after_discount()` directly — would false-positive on every payment (fee-inclusive vs fee-exclusive). Corrected to `(amount_thb - fee)` vs order total. Fee is already a param.
- **H3 variable names:** original fix used `existing_order` — not a real variable. Corrected to `existing_idempotency_order` / `existing_cart_order` per actual branch names.
- **M5 IntegrityError path:** original doc said IntegrityError → 500 + stuck. CORRECTED: `create_charge` catches `IntegrityError` internally, re-raises as `ValueError` → view returns 409. Only `omise.errors.BaseError` (gateway failure) leaks as 500. M5 scope narrowed.
- **M9 IntegrityError impact:** downgraded from "500 + stuck" to "409, stays `payment_pending`". Orphaned-charge risk narrowed to the specific window where both concurrent requests complete the Omise API call before either DB insert.
- **BE-F9 currency confusion:** overturned — `amount_thb` is a misnomer; `grand_total/100/rate` + `_to_minor_units` produce the correct display-currency pair. Not a money bug.
- DRF pagination envelope — no `DEFAULT_PAGINATION_CLASS` configured; flat array confirmed; polling formats 2–4 are dead defensive code, not live.
- `expires_at` timezone skew — `USE_TZ=True` makes all datetimes offset-aware; `new Date()` handles correctly.
- `processing` status reaching FE — never assigned anywhere in `payments/`; unreachable.
- Plus 9 self-overturned items inside original agent reports.

---

## Suggested fix order (simplest-first, production-safe)

1. **H3** (BE ~4 lines: wrap both reuse responses) + **H4** (FE 2 lines: add `charge_id`/`charge_created_at`) — trivial, kill two user-facing breakages immediately.
2. **H2 + M10** — delete/410 two legacy routes (pure removal; verify zero prod traffic in access logs first).
3. **H1** (one server-side amount comparison in `initiate_order_charge`) + **M8** (guest email validation in `ChargeOrderView`) — security pair.
4. **H5** (add `'payment_pending'` to reconcile gate at `orders/views.py:634`) + **M5** (try/except `omise.errors.BaseError` with status revert in `initiate_order_charge`) — resilience pair.
5. M1–M3, M17 — small FE branches + KakaoPay/Alipay fixes; then LOW dead-code sweep batched with stable_id carry-over. **M4 RETRACTED (subsumed by M1)** per verification pass 2026-06-12.

---

## Grill pass corrections (2026-06-12)

Issues found by /grill interrogation after debug-mantra pass. All fix descriptions corrected in-place above; this section records the reasoning.

**H1 fix was wrong as originally written.** `amount_thb` is fee-inclusive (`grandTotal = total + fee - discount`, `PaymentComponent.js:257`). `order.get_total_cost_after_discount()` is fee-exclusive (`models.py:260-266`). Direct comparison would false-positive on every payment. Correct comparison: `(amount_thb - fee)` vs order total — `fee` is already a param of `initiate_order_charge`. Fixed above.

**H3 fix had wrong variable names.** Reuse branches use `existing_idempotency_order` (key-match) and `existing_cart_order` (cart-match), not a generic `existing_order`. Fixed above.

**H5 reconcile gate change is safe.** Adding `payment_pending` triggers `finalize_payment` on polling GET when latest charge is PAID. Double-finalize guarded by `payment_finalized_at` (`services.py:294-302`). Minor DB overhead only. Confirmed above.

**M7: both refund endpoints are live.** `POST /admin-dashboard-charge/refund/` (admin-facing) + `POST /payments/refund/` (API-facing). Neither has over-refund guard. Fix needed in both. Confirmed above.

**M9: best-effort expire() is feasible.** `omise_charge` in scope at `IntegrityError` catch site (`services.py:192`) — Omise API call precedes the `transaction.atomic()` block. Confirmed above.

---

## Scrutinize pass corrections (2026-06-12)

End-to-end trace of every fix path + edge cases. Four corrections applied in-place above; reasoning recorded here.

**H1 fee currency note added.** `fee_calculated` always in THB — computed as percentage of THB order total at `orders/views.py:1582-1589` regardless of display currency. Original doc implied this but didn't state it. Clarified in fix annotation.

**H4 reverse drift: `failure_code` added to dead-field list.** `GatewayChargeSerializer:62` also sends `failure_code` which FE never reads. Minor completeness addition; M13 covers the user-visible consequence.

**M6 reclassified from "deadlock" to "contention/block".** Traced lock acquisition order: `finalize_payment` holds Order lock → issues UPDATE on Coupon (implicit lock). `ApplyCouponView` holds Coupon lock → writes Order (no lock). `ApplyCouponView` does NOT wait for Order lock — so no circular wait. Not AB-BA deadlock; `finalize_payment` can block waiting for `ApplyCouponView` to release Coupon, but `ApplyCouponView` completes independently. Risk is latency + webhook timeout under high concurrency, not deadlock. Fix updated: acquire Coupon lock inside `finalize_payment`'s Order lock scope.

**M13 failure UX traced in full.** Declined card: `status='failed'` in 201 response → `processPayment` returns `{success:true}` → `handleClick` sets no state → completely silent. Confirmed card decline produces zero user feedback. Fix direction added.

**No findings retracted.** All 5 HIGHs remain correct after 4 passes. Fix order in Suggested fix order section remains unchanged.

---

## Verification pass (2026-06-12) — 3-agent KB cross-check

3 Explore verifier agents cross-checked all 5 HIGHs + 18 MEDIUMs against ~1700 lines of vault payment/omise KB + read-only code spot-checks. **Result: 20 CONFIRMED · 2 REFINED (H1, M17) · 1 REFUTED (M4) · 1 KB inaccuracy (M8) · 12 KB gaps surfaced.** Full report: [[payment-deep-review-verification-2026-06-12]].

### M4 — RETRACTED (subsumed by M1)

**Original claim:** "GAP-2 cross-order 409 body `{error:'payment_pending'}` (`services.py:660-664`) not in FE's 409-mapping table (`useOmisePayment.js:169-178` checks `pending_charge_exists` only) → generic toast, no cancel affordance despite `charge_id` supplied."

**Why retracted:** KB ([[payment-exception-catalog]] "Exception Reference" row 1: `PendingChargeError` → 409 → `{error: 'pending_charge_exists', charge: {...}}`) and code (`useOmisePayment.js:170` maps `pending_charge_exists`) confirm the canonical error code is `pending_charge_exists`, **not** `payment_pending`. The 409 IS mapped by FE. The "no cancel affordance" concern is real but is the **same** UX surface as M1 (PromptPay QR path missing `pendingCharge` branch). M1 already covers it.

**Action:** Drop M4 from Suggested fix order. M1 implementation is the only fix needed for the underlying UX concern.

### M8 — KB inaccuracy discovered

**Original M8:** Guest charge initiation requires no email match (CONFIRMED by verifier).

**KB inaccuracy surfaced:** [[payment-backend-charge-flow]] §5 states `ChargeOrderView` validates `email` for guest requests ("Both must match the order record"). **Code contradicts this** — `payments/views.py:106-109` guest path uses `user__isnull=True` only; `email` never read. Email validation exists **only** in `ExpirePendingChargeView` (`payments/views.py:375-376`).

**Action:** Edit [[payment-backend-charge-flow]] §5 to clarify guest email validation is **only** in `ExpirePendingChargeView`, **missing** in `ChargeOrderView`. Add to doc drift list below.

### Refinement deltas

- **H1** (REFINED): finding stands, fix spec correct (grill-correction). KB silent on server-side amount validation — flag for KB write `[[payment-amount-validation-rule]]`.
- **M17** (REFINED): KakaoPay half stands. Alipay half may be overstated — `AP → ALIPAY` and `APC → ALIPAY_CN` both exist in `payments/views.py:38-39`. FE `OMISE_SOURCE_TYPES` gap is a separate, smaller issue.

### KB gaps (atomization candidates)

12 distinct KB gaps surfaced. Top 6 priority for next `/lint-vault`:
1. `[[payment-amount-validation-rule]]` (H1)
2. `[[payment-legacy-deprecation-map]]` (H2, M10)
3. `[[payment-charge-service-layer]]` add IntegrityError cleanup pattern (M9)
4. `[[django-booking-creation-validation-gate]]` (M11)
5. Self-heal coverage matrix add to `[[payment-status-enums]]` (M12)
6. `[[payment-charge-service-layer]]` (M18)

Full list with all 12 in [[payment-deep-review-verification-2026-06-12]] "KB Gaps Surfaced" section.

### Verdict tally

| Verdict | Count | Findings |
|---------|-------|----------|
| CONFIRMED | 20 | H2, H4, H5, M1, M2, M3, M5, M6, M7, M8, M9, M10, M11, M12, M13, M14, M15, M16, M18 |
| REFINED | 2 | H1, M17 |
| REFUTED (→ RETRACTED) | 1 | M4 |
| KB inaccuracy | 1 | M8 (in `[[payment-backend-charge-flow]]` §5) |
| KB gaps surfaced | 12 | (see above) |

### Implementation status (2026-06-12)

**Batch 1 (H3 + H4) — SHIPPED to local branches:**
- BE H3 committed: `d7af0e9` on `smartenplus-backend` `fix/payment-deep-review-2026-06-12`
- FE H4 committed: `a3c8c80` on `smartenplus-frontend` `fix/payment-deep-review-2026-06-12`
- No push (manual PRs pending).

**Remaining:** Batch 2 (H2 + M10) → Batch 3 (H1 + M8) → Batch 4 (H5 + M5) → Batch 5 (M1–M3, M17, LOW sweep). See [[payment-implement-plan-2026-06-12]] for full sequence.

---

## Related
[[booking-payment-e2e-audit-2026-06-11]] · [[payment-integration]] · [[payment-gateway-charge-architecture]] · [[payment-charge-service-layer]] · [[payment-status-enums]] · [[omise-webhook-security]] · [[payment-finalize-deep-dive]] · [[payment-qr-polling-mechanics]] · [[payment-celery-expiry-strategy]] · [[omise-api-reference-2026-06-12]] · [[refund-flow]] · [[payment-checkout-5-principles]] · [[payment-deep-review-verification-2026-06-12]] · [[payment-implement-plan-2026-06-12]]

## Related Atoms (Extracted 2026-06-13)
- [[payment-amount-validation-rule]] — H1: `(amount_thb - fee) == order.get_total_cost_after_discount()` ±1.00 THB
- [[payment-legacy-deprecation-map]] — 410-returning routes: `/api/payments/webhook-legacy/`, `/api/placeorder/`
- [[payment-orphan-charge-expire-pattern]] — M9: IntegrityError catch → `omise_charge.expire()` before re-raising
- [[payment-reconcile-gate-extension]] — H5: `finalize_payment` accepts `ordering`/`payment_failed`/`payment_pending` (guarded by `payment_finalized_at`)
- [[payment-guest-email-guard-mirror]] — M8: every charge entry point validates `order.email == data['email']` for unauth
- [[payment-cancel-state-prevmethod-guard]] — M3: `cancelState.success` reset guarded by `prevMethodRef`
- [[payment-idempotency-key-cart-total]] — H3: `X-Idempotency-Key: ${cartId}:${total}`; wrapped `{"message","order"}` shape
- [[payment-self-heal-coverage-matrix]] — M12: per-method self-heal coverage table (Card 3DS excluded)
- [[payment-cancel-vs-expire-error-mapping]] — reuse `useCancelPayment` hook + `expirePendingCharge` helper
