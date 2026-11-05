# Stuck card payment CSL4045824

## Summary
Order CSL4045824 (2000 THB + 81.28 card fee = 2081.28) was PAID at Omise on 2 Nov 2026 but stayed `payment_pending` in our DB for 3 days. Fixed the safety net (card poll), a double-fee display bug and visibility (Payment Issues page). Root cause of the lost webhook is NOT confirmed yet.

## What happened
- Customer tried 3 cards. Card 1015 declined twice (10:50, 10:51), card 3150 charged 10:53:25 and PAID 10:53:42 after 3DS. Only one paid charge, no double charge.
- Telegram showed two "New Order Received / declined / N/A" (mislabelled failures), then "Payment Pending / credit_card / 2081.28", then nothing.
- DB: `GatewayCharge` pending, `Payment` AUTHORIZED, `payment_finalized_at` empty, lock held. Omise dashboard: paid.
- Owner set the order to `paid` by hand in Django admin. That does NOT finalize: booking, email, operator dispatch and `payment_finalized_at` stay unset. Reconcile cannot fix it either (it only handles `payment_pending`).

## Root cause (ranked, from code reading only)
1. `charge.complete` webhook lost or rejected. Suspects: Coolify migration 31 Oct (2 days before), `ALLOWED_HOSTS`, wrong `OMISE_SEC_KEY` after the move (every event 400 `verification_failed`). The Omise URL in use, `/admin-dashboard-orders/payments/webhook/`, is a valid alias of the same view, so the URL itself is likely fine.
2. No safety net: `sync_pending_charges` skipped cards. This was the known gap in [[payment-self-heal-coverage-matrix]] since June.
3. Possible crash inside `finalize_payment`, or the return-page reconcile failing.
To confirm: Omise Settings > Webhooks delivery log for `chrg_69jkpjnfll8h751prwg` (Live mode), `payments_webhookevent` row, `OMISE_SEC_KEY` vs live key.

## Fixes (merged to `main` by owner in BE `6a54916` and AD `a3d6f31`; deploy not verified)
Backend:
- `a06672c` Payment amount no longer double-counts the card fee (`amount_thb` already includes it; use `set_amount`). Failed attempts notify as `failed`, not `declined`. Old rows keep the wrong amount (display-only, no backfill).
- `80e2d68` `sync_pending_charges` polls card charges pending 30 min to 7 days, only if latest charge, order `payment_pending`, `payment_finalized_at` null.
- `b1c744d` Per-charge cooldown 1h (cache key `card_poll:<id>`, fails open, cleared on Omise error) so abandoned 3DS charges cannot eat the 40-call budget.
- `6a3e5b8` `GET /payments/admin/issues/` staff-only, read-only (`payments/issues.py`): paid_not_finalized, amount_mismatch, order_paid_unfinalized, card_pending_stale, webhook_unprocessed. Opus-tier security review: clean after one fix (malformed payload).
Admin-dashboard: `a3d6f31` Payment Issues page + sidebar entry; Reconcile button only for the two types reconcile can finalize.
Customer frontend: unchanged (planned PR C dropped; backend poll covers it).

## Pre-deploy check
Pending-card list that the poll would pick up = 0 (run via `manage.py shell` in the app container). No surprise confirmation emails expected.

## Open
- Verify BE + AD deploys finished and Celery beat + worker restarted.
- Confirm webhook root cause via Omise delivery log; check `OMISE_SEC_KEY`.
- CSL4045824 still hand-set to paid: finalize properly or leave. A backend "finalize manually-paid order" action is not built.
- Order History in admin: who set PAID (not checked).

## Lessons
- A manual PAID edit hides the problem and skips every side effect. Use reconcile for `payment_pending`.
- Coolify app terminal has no `psql`; use `python manage.py shell -c`. Pasted multi-line code gains 2-space indents: wrap in `exec(__import__('textwrap').dedent('''...'''))`.
- Test DB `test_smartenplus_db` is shared; parallel sessions break `manage.py test` ("being accessed by other users"). Retry in a loop.
- The `payment_pending` unique-pending-redirect-charge constraint means a test cannot hold two pending card charges on one order.

## Related
[[payment-self-heal-coverage-matrix]] · [[payment-pending-deadlock]] · [[omise-webhook-security]] · [[celery-beat-payment-scheduling]]
