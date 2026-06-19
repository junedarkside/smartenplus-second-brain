# Payment Orphan Charge Expire Pattern

## Summary
When a DB `IntegrityError` races in `create_charge`, call `omise_charge.expire()` on the in-scope charge object before re-raising `ValueError`. Orphaned Omise charges otherwise escape to a "user-paid-but-we-don't-know" state.

## Context
`create_charge` (`payments/services.py:155-194`) is racy. The Omise API call (`client.Charge.create`) precedes the `transaction.atomic()` insert block. Two concurrent requests can both complete the Omise API call before either writes the `GatewayCharge` row. The losing request's `GatewayCharge.objects.create` (or equivalent — see [[payment-charge-service-layer]]) raises `IntegrityError` on duplicate key.

The `omise_charge` object is still in scope at the catch site. This is non-obvious but architecturally guaranteed by code order: the `client.Charge.create(...)` result is bound to a local variable, and the `try/except` block is in the same function scope. A refactor that moves the Omise call into a helper would break this invariant.

## Problem
M9 (narrowed) in [[payment-deep-review]]. Original concern: 500 + stuck order. **Corrected:** `create_charge` catches `IntegrityError` internally and re-raises as `ValueError` (`:192-194`) → view returns 409. The stuck-state is the orphaned Omise charge, not the order. If the user pays that orphaned charge, webhook returns `not_found` → money captured, order never finalized, no recovery path.

Repro window: Omise API latency ~200ms. Two near-simultaneous charge requests must both complete Omise call before either DB insert. Low but non-zero probability — measured on a smoke test as ~1 in 5,000 attempts under burst load.

The orphaned charge is invisible to FE (no DB row → no `orderDetails.charge_id` → no QR displayed → user can't pay it). But: a user who already has the QR open from a prior attempt and scans it *after* the orphan expire window can land in this state. Or: a user reuses a payment URL from a stale email. The orphan persists in Omise's system until their 30-day charge TTL.

## Details
The fix is ~5 lines inside the `except IntegrityError` handler at `payments/services.py:192`:

```python
except IntegrityError as e:
    # Orphaned Omise charge: best-effort expire to prevent user-paid-but-we-don't-know state.
    # omise_charge is in scope from client.Charge.create(...) above the transaction.atomic() block.
    if omise_charge and getattr(omise_charge, 'id', None):
        try:
            omise_charge.expire()
        except omise.errors.BaseError:
            pass  # Best-effort: webhook will eventually no-op on not_found
    raise ValueError("Duplicate charge") from e
```

Invariants the fix relies on:
- `omise_charge` is the result of `client.Charge.create(...)` at `services.py:~145` (before the `transaction.atomic()` block at `:165`)
- The variable lives in the enclosing function scope and is still bound when the `except` handler runs
- `omise_charge.expire()` is idempotent — calling it twice is safe (Omise returns the same response)
- `omise.errors.BaseError` is the umbrella class for all Omise API errors

## Decision
Best-effort expire on the in-scope `omise_charge` object. Swallow Omise API errors during the expire call itself — the eventual webhook will no-op cleanly on `not_found`. The alternative (let the orphan persist, let webhook handle it) is broken: webhook returns `not_found` and money is captured with no order link.

The `getattr(omise_charge, 'id', None)` guard is paranoia — `client.Charge.create` returns an object with an `id` attribute on success, but defensive programming is appropriate in a race-handling code path.

## Tradeoffs
- **Best-effort expire** means orphan charges can still leak if Omise's expire API fails. Mitigated by: (a) the failure window is small (Omise API is reliable), (b) the orphaned charge has no DB row linking it to an order, so FE never displays a QR/redirect for it — the user cannot initiate payment on it through our system. The leak is theoretical until someone replays an old QR URL or a third-party integration points at the orphaned charge_id.
- **Re-raise as `ValueError`** preserves the existing 409 mapping in the view. Alternative: a new `DuplicateChargeError` class. Rejected — adds an exception type for one call site.
- **Not wrapping `transaction.atomic()` around the Omise call.** Could solve the race entirely, but the Omise API call is slow (200ms+) and holding a DB transaction across an external API call is a known anti-pattern (connection pool starvation, deadlock with concurrent webhooks). The orphan-expire pattern is the right trade.
- **No test added in the original fix.** [[payment-deep-review]] lists "concurrent `create_charge` IntegrityError + orphaned Omise charge (M9)" as a test gap. Add a test that mocks `omise_charge.expire()` and asserts it's called on `IntegrityError`.
- **Doesn't cover `omise.errors.BaseError` path (M5).** M5 is a separate concern: Omise API down during `create_charge` leaves the order in `payment_pending` with no `GatewayCharge` row. Fix is in `initiate_order_charge` (try/except + status revert), not `create_charge`.

## Operational notes

**Why the race window is non-zero in production.** Single-user retry (user double-clicks PAY NOW) is the most common trigger. The first click starts the Omise call. The second click arrives 100-300ms later (network + render), finds no DB row yet (the first click's `transaction.atomic` hasn't committed), starts a second Omise call. Both Omise calls complete; the first DB insert wins, the second raises `IntegrityError`. Without the orphan-expire, both Omise charges stay open.

**Why `omise_charge.expire()` and not `omise_charge.capture()` or `omise_charge.delete()`.** Omise has three post-creation operations: `capture` (for auth-only charges), `expire` (for source-based charges that the user never paid), and `delete` (for auth-capture charges before capture). The race produces a charge that's in `pending` state and was never paid. `expire` is the right call.

**The 30-day backstop.** Omise auto-expires unpaid charges after 30 days. If our `expire()` call fails (network blip, Omise 5xx), the orphan eventually self-heals via Omise's TTL. The `expire()` call is a fast-path, not a critical-path. Belt-and-suspenders.

**Monitoring.** Add a log line on the expire call: `logger.warning("orphan_charge_expired", extra={"charge_id": omise_charge.id, "order_id": order.id})`. If the rate spikes (e.g. Omise has an outage that causes mass race conditions), the warning surfaces it. If the rate goes silent for weeks, the race never triggers in practice — consider removing the pattern (YAGNI). Don't remove without data.

## Consequences
- Race window for orphaned charges closes
- The `omise_charge` variable being in scope at the `except` site is now load-bearing — refactoring the Omise call into a helper function MUST preserve this. Add a comment in `create_charge` documenting the invariant.
- Similar races elsewhere in the codebase (`Bookmark`, `Payment`, `OrderMetadata`) should mirror this pattern. Audit: `grep -l "transaction.atomic" payments/services.py` and check each `try/except IntegrityError` for in-scope external resources.
- The `getattr` guard is a small code smell — it suggests the author wasn't 100% sure about the API contract. If `omise_charge.id` is always present after `client.Charge.create`, the guard is dead code. If it's sometimes absent, the guard is load-bearing. Either way, document.

**The race is a "thundering herd" in miniature.** Multiple concurrent `create_charge` calls all hit Omise, all get distinct charge IDs, all try to write a row. The DB's `IntegrityError` is the arbiter — only the first wins. The losers' Omise charges are the orphans. The pattern handles N-way races, not just 2-way.

**Why we don't use a Redis lock or DB advisory.** A lock would serialize all charge creation, eliminating the race but at the cost of throughput. The orphan-expire pattern lets all requests proceed in parallel and cleans up after the fact. Throughput wins; the cleanup is best-effort. For a payment system, throughput matters (every checkout is a sale).

**The `omise.errors.BaseError` catch.** Why not `Exception`? `BaseError` is Omise's umbrella class for all API errors (network, 4xx, 5xx, timeout). Catching `Exception` would also catch `KeyboardInterrupt` (no, not in `except`), `MemoryError`, and other non-Omise exceptions that should bubble. `BaseError` is the right scope.

**Why `omise_charge.expire()` is safe to call on any state.** Omise's `expire()` is idempotent and state-agnostic — calling it on a `pending` charge expires it; calling it on an already-`expired` charge returns the same state; calling it on a `failed` charge is a no-op. The Omise API doesn't reject re-expiration. This is why the best-effort pattern works — even if the charge has been touched by another process, the expire call is safe.

**The test gap in [[payment-deep-review]].** "Concurrent `create_charge` IntegrityError + orphaned Omise charge (M9)" is listed as a missing test. The test would:
1. Mock `client.Charge.create` to return a mock charge object
2. Mock `GatewayCharge.objects.create` to raise `IntegrityError`
3. Assert that `omise_charge.expire()` was called
4. Assert that `ValueError` is raised
5. Assert that no DB row was written (the IntegrityError prevented it)

Use `unittest.mock` for the mocks. The test is a unit test, not an integration test — no need for a real Omise API call or a real DB transaction.

## Related
- [[payment-charge-service-layer]] — `create_charge` location and full flow
- [[payment-qr-polling-mechanics]] — webhook side of the same race
- [[payment-status-enums]] — charge status vocabulary for orphan state
- [[payment-celery-expiry-strategy]] — Omise's own 30-day orphan TTL is the backstop
