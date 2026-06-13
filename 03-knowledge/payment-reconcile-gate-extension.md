# Payment Reconcile Gate Extension

## Summary
`finalize_payment` self-heal gate at `orders/views.py:634` accepts `ordering` / `payment_failed` / `payment_pending` statuses, not just the original two. Guarded by `payment_finalized_at` to prevent double-finalize.

## Context
The polling endpoint `GET /orders/{id}/orderdetails/` has a self-heal path that calls `finalize_payment` when the order is in a recoverable state. Original gate checked only `ordering` and `payment_failed`, missing `payment_pending`. With the original two-status gate, a lost or delayed `charge.complete` webhook (network partition, server restart, Omise outage, our deploy during a payment window) leaves an order stuck in `payment_pending` with a paid Omise charge forever. No amount of polling heals it.

This is the most important user-facing resilience fix in the payment system. The "I paid but it says pending" complaint that triggers support tickets at 1am is exactly this bug.

## Problem
H5 in [[payment-deep-review-2026-06-12]]. Two fail paths converge:

- **Path A — Amount mismatch swallowed.** Webhook `_handle_order_paid` (`payments/views.py:271-285`) catches `PaymentAmountMismatchError` and swallows it. Re-raising would rollback the `GatewayCharge.status=PAID` row, leaving the order and the charge in inconsistent states. Charge = `paid` at Omise + in DB. Order stays `payment_pending`. No recovery path is triggered.
- **Path B — Lost/delayed webhook.** Polling stops being a recovery path because the gate excludes `payment_pending`. The order is permanently in `payment_pending` until manual intervention.

FE consequence: `useQRPolling.js:88-91` sets success on `charge_status === 'paid'`, redirects to order page, order page polls 30s and shows pending. No email, no booking confirmation, no UI recovery affordance. User is stuck. Support escalates.

Falsification: does explicit `/reconcile` POST cover `payment_pending`? → `ReconcileView` at `orders/views.py:661` is a separate POST, not called automatically. FE `getReconcileOrder` helper has zero callers (confirmed earlier audit). No automatic reconciliation path exists. H5 stands.

## Details
Fix at `orders/views.py:634`:

```python
# Before:
if order.status in ('ordering', 'payment_failed'):
    finalize_payment(...)

# After:
if order.status in ('ordering', 'payment_failed', 'payment_pending'):
    finalize_payment(...)
```

The `finalize_payment` branch immediately below already handles the `payment_pending` case (it reads the latest `GatewayCharge`, checks `status == PAID`, and proceeds). Safety: `payment_finalized_at` guard at `services.py:294-302` prevents double-finalization. If `finalize_payment` is called twice (once by webhook, once by polling self-heal), the second call exits early on the `payment_finalized_at is not None` check.

Cost: one extra `SELECT` for the latest `GatewayCharge` per polling GET during normal in-flight state. Early-exit on `gc.status != PAID` is cheap. The polling endpoint is on a 30s cadence on the order page, so the load is bounded.

## Decision
Add `payment_pending` to the gate. Trust the `payment_finalized_at` guard for idempotency. Do NOT add a separate `ReconcileView` call from the polling path — the gate IS the self-heal. The `ReconcileView` exists for manual admin triggers; don't conflate.

The simpler-looking form (two statuses) is the trap. The atom exists specifically to prevent a future maintainer from "simplifying" the gate back to two statuses.

## Tradeoffs
- **Extra DB read per polling GET.** One `SELECT` against `GatewayCharge` with a status + order_id filter. Negligible vs the alternative of stuck orders. Caching options rejected — would mask the self-heal.
- **`payment_pending` is broad.** Includes orders where charge creation itself failed (e.g. M5 Omise `BaseError`). The `finalize_payment` early-exit on `gc.status != PAID` handles this — no false-finalize. The order stays `payment_pending` until a sweep catches it (see [[payment-self-heal-coverage-matrix]]).
- **FE UX not addressed in this fix.** Order page should treat `charge_status='paid'` + `order_status='payment_pending'` as "Processing — if this persists contact support" rather than re-polling indefinitely. Separate FE fix, not bundled here — different repo, different urgency.
- **Race with webhook arrival.** Webhook arrives at T+0.001s, polling self-heal runs at T+30s. Webhook wins; polling self-heal no-ops on `payment_finalized_at`. No double-finalize. The polling GET during T+0 to T+30s may hit the gate and call `finalize_payment` — same guard, same early-exit. Safe.
- **No throttle on polling self-heal.** A burst of polling requests could each call `finalize_payment`. The early-exit makes this cheap, but it's not free. Acceptable; revisit if polling QPS spikes.

## Consequences
- Entire paid-but-unfinalized dead-end class is now self-healing via polling
- Without this atom, next audit reverts the gate back to two statuses (the simpler-looking form is the trap)
- The `payment_finalized_at` invariant is now doubly important — any code that clears it manually re-opens the double-finalize window. Add a test: "calling `finalize_payment` twice in a row results in exactly one `payment_finalized_at` write".
- Test gap: "webhook EXPIRED→successful recovery" and "reconcile throttle + superseded skip" are missing tests in [[payment-deep-review-2026-06-12]]; add both.
- The "self-heal via polling" pattern is now the standard for any new charge-recovery path. Document in `docs/technical/PAYMENT_SYSTEM.md`.
- M5 (Omise `BaseError` → order stuck `payment_pending`) is partially mitigated by this fix — once Omise recovers and the next charge attempt completes, polling can finalize. But M5 needs its own status-revert fix; this is not a substitute.

## Operational notes

**The polling cadence on the order page is 30s.** A missed webhook heals within 30s of the user landing on the order page. This is fast enough that the user rarely notices — the page loads, polls, finds the order in `payment_pending` with a paid `GatewayCharge`, calls `finalize_payment`, returns `paid` on the next poll. The user sees a brief "Processing" then a "Paid" state. Acceptable.

**The gate fires on every polling GET during in-flight state.** Each `GET /orders/{id}/orderdetails/` checks the gate. If `payment_pending`, calls `finalize_payment`, which does a `SELECT` on `GatewayCharge` and an early-exit. Cost per poll: 1 extra query. Per order page session: ~5-10 polls over 5 minutes. Per day at 1000 orders: ~10k extra queries. Trivial.

**Why `payment_finalized_at` is the right guard, not a Celery lock or DB advisory.** `payment_finalized_at` is a column on the `Order` model. The guard reads it, checks if non-None, exits. No cross-process coordination, no lock acquisition cost, no deadlock risk. The webhook path and the polling path both check the same column. The column is the single source of truth for "is this order finalized?".

**Failure mode: webhook and polling finalize simultaneously.** Webhook arrives at T+0.001s. Polling fires at T+0.005s. Both call `finalize_payment`. Webhook acquires the Order row lock first (via `select_for_update` at `services.py:294`), writes `payment_finalized_at`, commits. Polling acquires the lock second, reads `payment_finalized_at is not None`, exits. No double-finalize. The DB lock is the real mutex; the column is the post-mutex check.

**Failure mode: webhook is delayed, polling wins, webhook arrives later.** Polling at T+0.001s calls `finalize_payment`, which sets `payment_finalized_at`. Webhook arrives at T+30s, tries to call `finalize_payment`, exits on the `payment_finalized_at is not None` check. No double-finalize. Webhook's later arrival is silently absorbed.

**Failure mode: polling never fires (user closes page).** Order stays `payment_pending` with `payment_finalized_at` unset. The Celery sweep `sync_pending_charges` and the card 3DS sweep (see [[payment-self-heal-coverage-matrix]]) are the backstop. They run on a schedule, not per-user. The polling self-heal is a fast path, not the only path.

**The gate's "ordering" entry is rarely hit in practice.** An order in `ordering` status with a paid `GatewayCharge` means the webhook fired *before* the order transitioned to `payment_pending`. This is unusual — the typical sequence is `ordering → payment_pending → paid`. The `ordering` entry in the gate covers the rare case where a webhook arrives during the brief `ordering` window. Don't remove it.

**The "payment_failed" entry is the recovery path.** An order in `payment_failed` with a paid `GatewayCharge` means the user retried after a failure. The original charge attempt failed, the user clicked PAY again, the new charge succeeded, the order is now `payment_failed` (from the old attempt) but the new `GatewayCharge` is `paid`. The gate catches this and finalizes. The `payment_failed → paid` transition is valid; see [[payment-charge-service-layer]] for the state machine.

**Why we don't use a separate `ReconcileView` call from the polling path.** The polling path IS the reconcile. Adding a `POST /reconcile/` call from the polling GET would be a separate round-trip for the same logic. The gate + `finalize_payment` is the in-place reconcile. `ReconcileView` exists for manual admin triggers (the "this order is stuck, force a reconcile" button in admin-dashboard). Don't conflate.

**The fix is one line of behavior, one line of risk.** The one line of behavior: `'payment_pending'` added to the tuple. The one line of risk: extra DB query per polling GET during in-flight state. The risk is bounded and acceptable. The behavior fix is the entire point. Don't over-engineer the change with config flags, feature toggles, or per-method logic.

**The pre-fix symptom in production.** Orders stuck in `payment_pending` for >30 minutes, support tickets created, manual DB intervention required. The pattern matches: webhook lost → order stuck → user complains → admin runs a script to set `payment_finalized_at` manually. The fix eliminates the pattern.

**The post-fix expectation.** Orders self-heal within 30 seconds of the user landing on the order page. Support tickets for "I paid but it says pending" drop to near-zero. The Celery sweep and card 3DS sweep are the backstops for the case where the user closed the page (no polling).

## Related
- [[payment-status-enums]] — order status vocabulary
- [[payment-finalize-deep-dive]] — `finalize_payment` SSOT
- [[payment-pending-deadlock-2026-06-12]] — related H-class issue from same audit
- [[payment-self-heal-coverage-matrix]] — what this gate does and doesn't cover across charge types
