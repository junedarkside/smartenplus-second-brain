# Payment Amount Validation Rule

## Summary
Server-side `initiate_order_charge` must validate `(amount_thb - fee) == order.get_total_cost_after_discount()` within a ±1.00 THB tolerance. Submitted amount is fee-inclusive; order total is fee-exclusive. Comparing `amount_thb` directly against the order total false-positives on every payment.

## Context
The payment flow has a fee-inclusive / fee-exclusive asymmetry between FE submission and BE order model:

- **FE submission** — `PaymentComponent.js:257-261` builds `grandTotal = trip_total + fee - discount` (fee-inclusive). The Omise charge is created against this amount.
- **BE order model** — `order.get_total_cost_after_discount()` (`orders/models.py:260-266`) returns the trip cost minus discount only. The fee lives on `order.gateway_fee_and_vat`.
- **Timing** — `order.gateway_fee_and_vat` is set AFTER `initiate_order_charge` returns (`services.py:723`). At validation time, the order's stored fee is not yet authoritative.
- **Fee param** — `fee` is passed to `initiate_order_charge` as a separate parameter, always in THB. `fee_calculated` is always in THB regardless of display currency (`orders/views.py:1582-1589`).

The original H1 fix proposed comparing `amount_thb` directly to the order total. Falsification: this would false-positive on every legitimate payment. The corrected formula subtracts `fee` first to convert fee-inclusive → fee-exclusive before comparison.

## Problem
H1 in [[payment-deep-review-2026-06-12]] — client-controlled charge amount never validated against order total. Self-validating closed loop: `initiate_order_charge` derives `amount_thb` from the request body; `locked_amount` (`services.py:683`) and the finalize mismatch check (`services.py:304-315`) both derive from the same client value. The "validation" is the value validating itself. Floor check at `views.py:122-124` is per-currency minimum, not order total — irrelevant to this attack.

Repro: `POST /payments/order-charge/` with `grandTotal: 2000` (20 THB) against a 5,000 THB order. View accepts it, `initiate_order_charge` transitions to `payment_pending`, Omise charged 20 THB, webhook fires, `finalize_payment` called with `gc.amount=20` → `locked_amount=20` so mismatch check passes → order finalized as paid. The user paid 20 THB for a 5,000 THB order. Our system marked it paid.

Falsification: `CheckoutSnapshot` cannot block — `services.py:~318-322` comment says "log-only — do NOT block payment". H1 stands.

## Details
The fix goes after `amount_thb` / `fee` are Decimal-cast, after `services.py:576` (post `views.py:117-119` computation):

```python
order_total = order.get_total_cost_after_discount()
if order_total and abs((amount_thb - fee) - order_total) > Decimal('1.00'):
    raise ValueError(f"Amount mismatch: submitted {amount_thb - fee}, order total {order_total}")
```

Invariants the fix relies on:
- `amount_thb` is the decimal-cast value of the client `grandTotal`, fee-inclusive
- `fee` is the decimal-cast fee param, always in THB
- `order_total` is `order.get_total_cost_after_discount()`, fee-exclusive
- Tolerance 1.00 THB covers rate-conversion rounding (minor units round-trip is exact for THB; JPY is the only other currency and is also exact)
- Fix assumes no non-THB payment reaches this path — consistent with the existing FX-rate-based approach at `orders/views.py:1582-1589`
- `ValueError` is caught by the view (`views.py:140-154`) and translated to 400/409

Edge cases handled by the formula:
- Zero-value orders (free coupon, 100% discount): `order_total` is 0, the `if order_total and ...` short-circuits → no validation
- Fee of 0 (no gateway fee configured for the method): `(amount_thb - 0) - order_total` is the same as `amount_thb - order_total` → direct comparison
- Decimal precision: all values are `Decimal`, not float. No IEEE-754 rounding surprises.

## Decision
Compare `(amount_thb - fee)` against `order.get_total_cost_after_discount()` with 1.00 THB tolerance. Reject with `ValueError` on mismatch. No new exception class (existing handler covers it). No pre-check on `fee_calculated` (it doesn't exist at this point in the flow). Single-point fix in the service layer, not the view — the view trusts the service to validate.

The 1.00 THB tolerance is a deliberate trade. It absorbs FX-rate rounding (negligible for current payment methods) without admitting unbounded underpayment. Document the rationale inline so the magic number isn't "simplified" to 0 in a future refactor.

## Tradeoffs
- **1.00 THB tolerance** is not zero. A bad actor could underpay by ~0.99 THB and not be caught. Per-charge that's negligible. Per-day at scale it could add up. Acceptable for current scale; revisit if fraud appears.
- **Currency assumption** (THB-only path). The current code path always converts via `grand_total/100/rate` to compute `amount_thb`. If multi-currency charging is added, validation must follow the same conversion — `amount_thb` may not be in THB at the validation site.
- **`ValueError` over `PaymentAmountMismatchError`.** Existing view catch list handles `ValueError`. New exception class would require handler wiring and a new import. Not worth it for one call site.
- **Validate in service, not view.** The view is the public API boundary; validating there couples view code to order model internals. The service layer is the right place.
- **No async / re-fetch of `order`.** The `order` is already in scope from the earlier lookup. Re-fetching risks a stale read if the order was modified between lookup and validation.

## Consequences
- Closes the single most-leveraged payment bug (false-positive fee-inclusion / underpayment attack)
- Future payment method additions MUST mirror this check, not rely on it
- Tolerance value (1.00) is a magic number — must be commented in source explaining FX rationale
- FE `grandTotal` formula in `PaymentComponent.js:257-261` is now load-bearing; changing it (e.g. moving fee to a separate line item) breaks the check
- The `order.get_total_cost_after_discount()` return shape is now part of the contract — any change to it (e.g. adding VAT) breaks the check. Add a test that locks the contract.
- The `fee` param passed to `initiate_order_charge` is now load-bearing — its value must match what the FE used to compute `grandTotal`. If FE and BE ever disagree on the fee formula, the check fails.

## Operational notes

**Why the tolerance is 1.00 THB and not 0.00.** Currency conversion is not lossless. The order total in the DB is in THB (the merchant currency). The `amount_thb` is computed from `grand_total / 100 / currency_rate_val`. For THB display currency, `currency_rate_val` is 1.0 → no rounding. For JPY, conversion goes through a rate that may have 4+ decimal places. A 5,000 THB order displayed in JPY is ~18,500 JPY; the round-trip back to THB can drift by 0.01-0.50 THB. 1.00 THB tolerance absorbs this. Zero tolerance would false-positive on JPY orders.

**Why Decimal, not float.** All `amount_thb`, `fee`, and `order_total` are `Decimal`. Float arithmetic introduces IEEE-754 rounding errors that compound across the subtraction and comparison. `Decimal('1.00')` is exact; `1.00` (float) is not. The cast at `views.py:117-119` (`Decimal(str(grand_total))`) is the conversion point. Don't `float()` anywhere downstream.

**Why this is in the service layer, not the view.** The view is the public API boundary; the service is the business logic. Validating the amount in the view couples the view to the order model. Validating in the service (`initiate_order_charge`) keeps the view thin and the validation co-located with the rest of the order math. The view translates `ValueError` to 400/409; the service decides if the value is valid.

**Falsification of the `CheckoutSnapshot` block.** `services.py:~318-322` has a comment: "log-only — do NOT block payment". The original audit checked if `CheckoutSnapshot` could be the gate; the comment says no. This is a deliberate design choice — `CheckoutSnapshot` is for audit/log, not authorization. The amount validation is the authorization.

**Failure mode: `order_total` is None.** The `if order_total and ...` guard handles the case where `get_total_cost_after_discount()` returns None (e.g. order has no line items, or a `DivisionByZero` upstream). In that case, the validation is skipped. This is a deliberate fail-open — if we can't compute the order total, we don't block the payment. The risk: an order with `order_total=None` is exploitable. Audit: are there any production code paths that produce `order_total=None`? If yes, fix the upstream. If no, the guard is dead code.

**Failure mode: fee is None or 0.** `(amount_thb - None)` raises `TypeError`. `(amount_thb - 0)` is `amount_thb`. The current callers always pass a non-None `fee`. If a future caller passes None, the `ValueError` from the cast is more informative than the `TypeError` from the subtraction. Add a guard: `if fee is None: fee = Decimal('0')` before the subtraction.

**Test cases to add.**
- Submit `grandTotal` matching order total exactly → success
- Submit `grandTotal` 0.99 THB below order total → success (within tolerance)
- Submit `grandTotal` 1.01 THB below order total → 400/409
- Submit `grandTotal` 0.99 THB above order total → success (within tolerance, attacker overpays)
- Submit `grandTotal` 1.01 THB above order total → 400/409 (attacker can't overcharge themselves — wait, this is wrong, attacker wants to underpay)
- `order_total=None` → no validation, payment proceeds
- JPY order with minor rounding drift → success (within tolerance)

## Related
- [[payment-charge-service-layer]] — `initiate_order_charge` location and full flow
- [[payment-integration]] — overall gateway charge architecture
- [[payment-pending-deadlock-2026-06-12]] — related H-class issue from same audit
- [[payment-frontend-flow-mechanics]] — FE submission formula and the round-trip
