# Payment Self Heal Coverage Matrix

## Summary
M12 coverage gap map. Card 3DS charges are excluded from all self-heal sweeps. Missed `charge.complete` webhook for a 3DS card = stuck pending forever. New payment methods silently inherit the card 3DS exclusion. The matrix is the source of truth for what heals what.

## Context
Three self-heal paths exist in the payment system:

1. **Polling self-heal** — `GET /orders/{id}/orderdetails/` calls `finalize_payment` when status is in the reconcile gate. See [[payment-reconcile-gate-extension]] for the gate contents (`ordering` / `payment_failed` / `payment_pending`).
2. **Celery sweep** — `sync_pending_charges` (`tasks.py:76-80`) reconciles pending charges with Omise API by polling Omise for the latest charge status.
3. **Celery expiry** — `expire_stale_payments` runs via beat schedule for `METHOD_EXPIRY` entries (`billings/models.py:103-127`). Expires orders whose underlying Omise charge has passed its TTL without completing.

Card 3DS charges are excluded from all three. The exclusion is a side effect of the original design (cards were "synchronous, no expiry") and was never revisited when 3DS redirect was added.

## Problem
M12 in [[payment-deep-review]]. Specific exclusions:
- `sync_pending_charges` skips cards (`tasks.py:76-80` filter is `source_type != CARD`)
- No `METHOD_EXPIRY` entry for cards (only PromptPay and TrueMoney have TTLs in `billings/models.py:103-127`)
- `expire_stale_payments` not in beat schedule for card expiry
- Reconcile gate excludes `payment_pending` (fixed by [[payment-reconcile-gate-extension]]), but that fix only matters for the polling self-heal — cards never reach the polling path in `payment_pending` state because the 3DS redirect creates the charge synchronously and the order goes straight to `paid` on webhook.

A lost `charge.complete` webhook for a 3DS card leaves the charge row with status `pending` and the order in `payment_pending`. No sweep heals it. The user paid (Omise captured); we don't know.

The "Card = no expiry (synchronous)" claim in `docs/technical/PAYMENT_SYSTEM.md` is false for 3DS redirect charges — they have a webhook dependency that the other self-heal paths don't cover. The doc drift is part of the bug.

## Details
Coverage matrix — source of truth for what heals what:

| Charge type | Polling self-heal | sync_pending_charges | expire_stale_payments | METHOD_EXPIRY entry | Notes |
|---|---|---|---|---|---|
| PromptPay (source) | yes (via reconcile gate) | yes | yes | yes (PP TTL) | Fully covered |
| TrueMoney | yes (via reconcile gate) | yes | yes | yes (TM TTL) | Fully covered |
| Card 3DS redirect | NO (order not in `payment_pending` at polling time) | NO (skipped) | NO (not in beat) | NO (no entry) | **GAP** |
| Card non-3DS sync | N/A (synchronous, `charge.complete` in same request) | N/A | N/A | N/A | Webhook not required |
| KakaoPay (FE broken) | yes | yes | yes | yes (inherits PP path) | See M17 — FE sends wrong method key |
| Alipay (FE broken) | N/A (FE never creates source) | N/A | N/A | N/A | See M17 |
| LINE Pay (FE/BE mismatch) | yes | yes | yes | yes | FE creates `line_pay` source, BE creates `rabbit_linepay` — separate charges |

The card 3DS row is the gap. The "synchronous" assumption doesn't hold for 3DS redirect: the user is redirected to their bank, completes 3DS, Omise fires `charge.complete` webhook asynchronously, and only then is the order `paid`. The webhook can be lost.

## Decision
Add card 3DS to the `sync_pending_charges` sweep. Implementation options:

- **Unified sweep** — remove the `source_type != CARD` filter at `tasks.py:76-80`. All pending charges get polled.
- **Separate task** — add `sync_pending_card_3ds` that only handles card charges > 5 minutes old. Isolated blast radius, isolated failure mode.

Recommend the separate task for blast-radius isolation. The codebase has multiple per-method expiry paths, so separate is the precedent. Implementation:

```python
# tasks.py
@shared_task
def sync_pending_card_3ds():
    """Poll Omise for pending card 3DS charges > 5 minutes old.
    Closes M12 self-heal gap: card 3DS webhooks are not always delivered.
    """
    cutoff = timezone.now() - timedelta(minutes=5)
    pending = GatewayCharge.objects.filter(
        status=PaymentStatus.PENDING,
        source_type=OmiseMethod.CREDIT_CARD,
        created_at__lt=cutoff,
    )
    for gc in pending:
        try:
            omise_charge = omise.Charge.retrieve(gc.gateway_charge_id)
            gc.status = map_omise_status(omise_charge.status)
            gc.save(update_fields=['status', 'updated_at'])
        except omise.errors.BaseError:
            continue  # Best-effort; next sweep retries
```

Add a `card_3ds` `METHOD_EXPIRY` entry with TTL of 30 minutes (Omise card 3DS webhook SLA). Wire `expire_stale_payments` into the beat schedule with the new entry.

Update `docs/technical/PAYMENT_SYSTEM.md` to:
- Remove the "Card = no expiry (synchronous)" claim
- Add a per-method self-heal coverage section
- Reference this atom

## Tradeoffs
- **Unified vs separate task.** Unified is one less task to maintain; separate is one less thing to break. Either works; choose based on existing convention. The codebase has multiple per-method expiry paths, so separate is the precedent. Mixed (unified for sweep, separate for expiry) is also valid.
- **TTL of 30 minutes.** Omise card 3DS webhooks typically arrive in <5 seconds, but network partitions and server restarts can extend this. 30 min is a reasonable upper bound. Shorter = more false-expires (real users whose webhook is in flight); longer = more stuck-pending window. 30 min matches the Omise `charge.expire` typical TTL.
- **5-minute sweep cutoff.** Avoids polling charges that are still in normal flight. A webhook that arrives at T+10s beats the sweep. A webhook that's lost is caught at T+5min. Tune based on production metrics.
- **Polling self-heal not relevant for 3DS.** The order doesn't exist in `payment_pending` state during 3DS — it's either `ordering` (pre-redirect) or `paid` (webhook fired). Adding `payment_pending` to the polling gate (done in [[payment-reconcile-gate-extension]]) doesn't help 3DS cards.
- **Beat schedule wire-up.** Each `METHOD_EXPIRY` entry needs a corresponding Celery beat schedule wire-up. Future entries MUST wire both. The pattern is in `celery.py` or settings.

## Consequences
- Closes the card 3DS stuck-pending dead-end
- Coverage matrix must be re-checked when adding any new payment method. The matrix is the source of truth.
- `docs/technical/PAYMENT_SYSTEM.md` must be updated to remove the "Card = no expiry (synchronous)" claim and add a section per method with self-heal coverage
- Each `METHOD_EXPIRY` entry needs a corresponding Celery beat schedule wire-up. Future entries MUST wire both.
- The 5-minute sweep cutoff is a magic number. Document inline.
- Test gap: "expire_stale_payments command (no test file)" in [[payment-deep-review]]. Add tests for both the new `sync_pending_card_3ds` task and the new `card_3ds` expiry entry.

## Related
- [[payment-celery-expiry-strategy]] — `METHOD_EXPIRY` model and beat schedule
- [[payment-status-enums]] — charge status vocabulary
- [[omise-api-reference]] — Omise 3DS charge lifecycle
- [[payment-reconcile-gate-extension]] — the polling self-heal side of the matrix
