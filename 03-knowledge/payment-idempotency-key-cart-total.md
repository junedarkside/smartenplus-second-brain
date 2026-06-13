# Payment Idempotency Key Cart Total

## Summary
Frontend sends `X-Idempotency-Key: ${cartId}:${total}` for order creation. Reuse branches MUST return `{"message": "Order reused", "order": {...}}` (wrapped), not bare serializer data. FE always reads the wrapped shape. Bare-vs-wrapped shape mismatch has crashed FE twice.

## Context
FE `usePaymentInitialization.js:38-44` builds the idempotency key from `cartId:total`. Key is stable while cart unchanged. Same-cart refetch hits the key-match reuse branch at `orders/views.py:272-274`. The create path returns the wrapped shape at `views.py:535-539`:

```python
return Response({"message": "Order created successfully", "order": OrderSerializer(order).data}, status=201)
```

The reuse branches return bare `OrderSerializer(order).data` — a different shape. FE has been written for the wrapped shape everywhere, on the assumption that all order-create endpoints return the same envelope.

This assumption was implicit, not documented. It broke twice (coupon apply, cancel-pending recovery) before the pattern was made explicit.

## Problem
H3 in [[payment-deep-review-2026-06-12]]. Two distinct breakages:

- **Shape mismatch.** FE reads `orderData?.order?.billing_profile_slug` (`usePaymentInitialization.js:58`) and **unguarded** `orderData.order.order_id` (`:74`) → `TypeError: Cannot read properties of undefined (reading 'order_id')` → caught at `:83` → `GENERIC_ERROR` → "Payment processing failed" toast. Triggered on every coupon apply (`usePaymentCouponManager.js:26`) and cancel-pending recovery (`PaymentComponent.js:157`).
- **NameError.** Keyless branch `views.py:278-289` uses `cart` in `Order.objects.filter(cart=cart,...)`. `cart` first assigned at `views.py:326` (after billing profile steps). Any client omitting `X-Idempotency-Key` header with an existing order → `NameError: name 'cart' is not defined` → 500. Latent — FE always sends the key, so it doesn't trigger in production. But: any FE bug that drops the header exposes it.

Falsification: optional-chaining at line 58 prevents the TypeError there, but line 74 is unguarded. The bare-vs-wrapped shape mismatch is the bug.

Trigger scope: FE always sends `X-Idempotency-Key: ${cartId}:${total}` (`usePaymentInitialization.js:38-44`), stable while cart unchanged. Every same-cart refetch hits the key-match reuse branch: coupon apply, cancel-pending recovery. High frequency, deterministic failure.

## Details
Fix (BE, ~4 lines) — wrap both reuse responses:

```python
# Key-match reuse branch (views.py:272-274) — variable is existing_idempotency_order
return Response({"message": "Order reused", "order": OrderSerializer(existing_idempotency_order).data}, status=200)

# Cart-match reuse branch (views.py:283-289) — variable is existing_cart_order
return Response({"message": "Order reused", "order": OrderSerializer(existing_cart_order).data}, status=200)
```

Fix the latent NameError by moving the cart fetch to before the idempotency key check (currently `views.py:326`, move to before `:258`):

```python
cart = Cart.objects.filter(id=cart_id).first()  # move above line 258
```

`setOrderCreationSuccess` guard at `usePaymentInitialization.js:55` checks `orderData.message === "Order created successfully"`. Create response uses key `"message"` (correct, `views.py:536`). Reuse response currently has no `"message"` key → `undefined !== string` → guard false on reuse → `setOrderCreationSuccess` not called → `order_created` flag never set → downstream effects skip. Subsumed by the wrap fix.

The `"Order reused"` message string is distinct from `"Order created successfully"`. FE doesn't currently use this distinction, but logs and error tracking can. The literal string is the simplest discriminator.

## Decision
Wrap both reuse responses in the same `{"message", "order"}` shape as the create path. Use literal `"Order reused"` message (not `"Order created successfully"`) so FE can distinguish create vs reuse if needed in future. Move cart fetch to top of view to fix the latent NameError. Don't add a serializer wrapper class — the inline shape is consistent with the create branch and avoids a new import.

The two reuse branches (key-match, cart-match) are structurally similar. Both must wrap. The keyless branch (no `X-Idempotency-Key`) goes through cart-match, so the cart fetch needs to be available there too. Hence the move-`cart`-to-top fix.

## Tradeoffs
- **4 lines, not a new serializer.** Inline `Response({"message": ..., "order": OrderSerializer(...).data})` matches the existing create-path style. New `ReuseOrderResponseSerializer` would be more "DRY" but adds an import and obscures the shape. The wrapped response is a contract, not a domain object.
- **Cart fetch early.** Currently `cart` is only used in the keyless branch. Moving it to the top adds one query to every order-create call. Negligible (cart_id is already in the request, and `Cart.objects.filter(id=...).first()` is a primary key lookup). The early fetch also makes the `cart` variable available to the keyless branch, which is the point.
- **"Order reused" string.** Distinguishes from `"Order created successfully"`. FE doesn't currently use this, but logs and error tracking can. Cost: one extra string literal. Benefit: future-proofs the discriminator.
- **HTTP 200 vs 201 for reuse.** Reuse returns 200 (not 201) because no resource was created. Create returns 201. FE doesn't currently check status code, but the distinction is correct. Keep.
- **Idempotency key format `${cartId}:${total}`.** Currently a string. If `total` is a Decimal in the FE (it should be, per the fee-precision rules), the string conversion must be consistent. Test: idempotency key with `Decimal("100.00")` vs `"100"` should be the same key. If they differ, coupon apply with a minor formatting change creates a new order. Add a test.

## Consequences
- Closes both user-facing breakages (coupon apply + cancel-pending recovery) in one fix
- Bare-vs-wrapped shape is now a documented invariant. Any new branch returning order data MUST wrap. Code review check.
- The latent NameError is gone — but the keyless branch itself is now only reached if FE omits `X-Idempotency-Key`, which it never does. Still: fix the bug. Defensive programming.
- Future FE code that adds order-data response parsing gets to assume the wrapped shape. Document in `docs/api/PAYMENT_API.md`.
- The `"message"` discriminator is now a contract. If FE ever checks `orderData.message === "Order reused"` to skip a side effect, that check must be documented.
- The move-`cart`-to-top fix changes the query count for the create path. Monitor: `pg_stat_statements` for any regression.

## Operational notes

**Why the key is `${cartId}:${total}` and not `${cartId}` alone.** Cart can have multiple in-flight orders across different price points (e.g. user changes the booking date, total changes, new order is created with a new total). Keying on `cartId:total` ensures that a price-change-and-rebook creates a new order, not reuses the old one. Keying on `cartId` alone would either reuse the wrong order (if total is now different) or block re-booking (if the old order is in a non-reusable state).

**The key is a colon-separated string, not JSON.** A string is the simplest possible header value. JSON in headers requires escaping, base64-encoding, or content-negotiation. Don't. The colon is a delimiter; if `cartId` or `total` ever contains a colon, the parse breaks. Currently neither does (`cartId` is a UUID, `total` is a number). If that changes, switch to a different separator and document.

**Key reuse across requests.** The key is intentionally the same across multiple FE refetches of the same order. This is the "idempotent" semantic — same key = same order. If a user mutates the cart (adds a product, applies a coupon), the key SHOULD change to force a new order. The FE currently always sends the latest `total` in the key, so cart mutations correctly invalidate the key.

**The `setOrderCreationSuccess` guard.** At `usePaymentInitialization.js:55`, the guard checks `orderData.message === "Order created successfully"`. Before the fix, reuse returned no `message` key, so the guard was always false on reuse → `order_created` flag never set → `getCreateBooking` not called → order stuck in initialization. The fix (wrap reuse response) makes the guard fire on both paths. The guard is the "is this a successful order-create response" check; without a `message` key, it can't tell.

**FE TypeError location.** `usePaymentInitialization.js:74` — `await getCreateBooking(orderData.order.order_id, ...)`. Unguarded. The optional chain at `:58` (`orderData?.order?.billing_profile_slug`) protected one access, but `:74` was the unguarded one that threw. The falsification: "could `:58` be the only access?" — no, the booking creation at `:74` requires `order_id` and the throw cascades.

**`getCreateBooking` exists.** The function reads `orderData.order.order_id`, passes it to the booking creation endpoint, populates the booking state. If the throw at `:74` is caught at `:83` (`GENERIC_ERROR` catch-all), the booking never creates → the order page shows "Payment processing failed" toast → user confused. The wrap fix unblocks this.

**Monitoring.** Add a log line on the reuse path: `logger.info("order_reused", extra={"order_id": existing.id, "key": idempotency_key})`. If the rate spikes (e.g. FE starts re-fetching aggressively), the log surfaces it. If the rate is steady, the reuse path is operating as designed.

**Test gap: NameError on keyless path.** The latent NameError at `views.py:278-289` (cart used before assigned) only fires if FE omits `X-Idempotency-Key`. FE never does. But: a test that omits the header and asserts no 500 is a good regression guard. Add.

## Related
- [[payment-finalize-deep-dive]] — `finalize_payment` SSOT and the broader create/finalize flow
- [[payment-frontend-flow-mechanics]] — FE consumption of the response shape
- [[payment-charge-service-layer]] — service layer that consumes the order row
- [[payment-sentinel-idempotency]] — the X-Idempotency-Key header pattern more broadly
