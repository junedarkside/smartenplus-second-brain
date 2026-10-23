# Stuck Payment Lock Runbook (non-dev ops)

## Summary
Alert "Order X is locked with no linked charge, but the Omise call may have happened. Lock kept, check Omise before releasing." = order is `payment_pending`, no `GatewayCharge` row, sweep refuses to release because a live Omise charge may exist.

## Context
`create_charge` (`payments/services.py`) calls Omise `Charge.create` FIRST, writes `GatewayCharge` + `IdempotencyKey` AFTER in one `transaction.atomic`. A worker death between the two leaves a live Omise charge with no DB trace. So "no idempotency key / No charges found" does NOT prove "no charge". Alert comes from `release_chargeless_locks` (`payments/stuck_sweep.py`), dedupe 24h.

Migration `orders/0044_order_charge_attempted_at` (2026-10-22) back-filled `charge_attempted_at = updated` on every chargeless lock, so alerts right after that deploy may be backfill artifacts, not real charges.

## Gotchas (learned the hard way)
- Admin URL is `/securelogin/`, not `/admin/`.
- Order page "Charge Information / No charges found" reads legacy `cards.Charge`, NOT `GatewayCharge`. Not evidence. Since the A2 change the Order page also shows a "Gateway charges" inline.
- Omise charge carries NO order id/metadata (open follow-up `OMISE-CHARGE-METADATA`). Searching Omise for the order number finds nothing. Match by time window + exact amount.
- Webhook for unknown charge id returns 200 `not_found` silently (`payments/views.py`), so no alert there.

## Steps
1. Admin > Orders > open order. Note `Updated` (lock time), `Locked amount`, `Charge attempted at`, status (Payment Lock group).
2. Admin > Payments > Gateway charges: search order id; also filter **By order = Empty** (orphan charges linked to nothing) and compare time + amount.
3. Admin > Payments > Idempotency keys: search `order-<ORDER_ID>-`.
4. Omise Dashboard (Live, not Test) > Charges: filter lock time ±15 min, exact amount. Write down charge id + status.
5. Decide:

| Omise result | Action |
|---|---|
| successful / paid | **Do NOT release.** Dev links charge to order, runs `reconcile_gateway_charge` (`services.py:246`) to finalize |
| pending | Wait, recheck. Do NOT release |
| failed / expired | Safe to release |
| no match in window | Safe to release (widen window to ±1h first) |

6. Release. **Preferred (BE branch `feat/admin-release-stuck-lock`, once deployed): `is_admin` opens the order in `/securelogin/`, clicks "Release stuck payment lock", re-does the Omise Live check from the page checklist, ticks the box, confirms.** Refused when: gateway charge linked, live idempotency key, lock younger than 15 min, or values changed since the page opened. Writes Order History + Telegram. Fallback (dev shell, never ops by hand-editing blindly): `status='ordering'`, `locked_amount=None`, `charge_attempted_at=None`, guarded by `status='payment_pending'`, `payment_finalized_at IS NULL`, no linked GatewayCharge. Mirrors `_revert_own_lock` (`services.py:504-521`).
7. Verify: order back to `ordering`; no new alert after the 1h cooldown (`RETRY_COOLDOWN_SECONDS`).

## Tradeoffs
Wrong release with a live successful charge = customer pays twice on retry. Wrong hold = order blocked until a dev acts. Hold is the cheap error, so default to hold when unsure.

## Related
[[payment-orphan-charge-expire-pattern]] · [[payment-pending-deadlock]] · [[payment-gateway-charge-architecture]] · [[omise-api-reference]] · [[payment-self-heal-coverage-matrix]]

## Tools built (BE develop `4cecbb8`, not deployed)
- Django admin `/securelogin/` > Payments > Gateway charges > "Check Omise for orphan charges" (`is_admin` only, POST calls Omise, built-in help panel with the locked-order table).
- Hourly Celery task `payments.tasks.alert_orphan_charges` (minute 20, 3h window, Telegram, 24h dedupe per charge). Needs celery beat restart after deploy.
- Dev fallback: `manage.py find_orphan_charges --hours 24 [--alert]`. All read-only; nothing links or releases.
- The existing sweep alert "locked with no linked charge" repeats at most once per 24h per order.

Admin release button (B) built 2026-10-23 on branch `feat/admin-release-stuck-lock` (BE `b7e8fa8`, `1c7f1d4`), payment-security reviewed, not deployed. Residual risk: if Omise made a charge but our DB never saved it, only the human Omise Live check catches it. Follow-ups (not built): `order_ref` metadata on `Charge.create` (E, declined for now), webhook unknown-charge alert (W), automatic Omise date-range check inside the release page.
