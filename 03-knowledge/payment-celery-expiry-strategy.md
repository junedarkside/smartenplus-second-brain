# Payment Celery Expiry Strategy

## Summary
`sync_pending_charges` Celery task handles expiry differently per payment method type. PromptPay uses deterministic TTL (no Omise query). Mobile banking polls Omise live. E-wallets use 30-minute fallback.

## Context
`payments/tasks.py`. Handles the case where Omise sends no expiry webhook (PromptPay, mobile banking). Three strategies because payment methods have different expiry signals.

## Strategy by Method Type

### PromptPay (tasks.py:20-54)
```python
# PP: deterministic TTL, NO Omise query
if (now - gc.created_at) > METHOD_EXPIRY[OmiseMethod.PROMPTPAY]:  # 10 min
    # Expire locally without querying Omise
    gc.status = 'expired'
    order.status = 'ordering'
    _send_payment_failed_notifications(order, reason='expired')
```
**Why no Omise query:** Omise sends no webhook for PP expiry. TTL is exact and reliable. Querying Omise would be wasted round-trip.

### Mobile Banking (tasks.py:57-72)
```python
# MB: query Omise after METHOD_EXPIRY threshold
if (now - gc.created_at) > METHOD_EXPIRY[OmiseMethod.MB_SCB]:  # 10 min
    live_charge = client.Charge.retrieve(gc.gateway_charge_id)
    if live_charge.status in ['expired', 'failed']:
        _finalize_payment_failed(gc, order)
    elif live_charge.status == 'successful':
        finalize_payment(order, triggered_by_gc=gc)  # recovery
```
**Why query:** Bank-side expiry can differ from Omise expiry. Charge may have succeeded mid-flight.

### E-Wallets / International (tasks.py:76-96)
```python
# E-wallets: 30-min fallback (no reliable expiry signal)
FALLBACK_THRESHOLD = timedelta(minutes=30)
if (now - gc.created_at) > FALLBACK_THRESHOLD:
    live_charge = client.Charge.retrieve(gc.gateway_charge_id)
    # same success/fail handling as mobile banking
```
**Why 30 min:** E-wallets (WeChat, Alipay, TrueMoney, etc.) don't have deterministic TTLs. 30 min chosen as reasonable stale threshold.

## Superseded Charge Guard (tasks.py:37-49)
Before marking failure, check if user created a newer non-terminal charge:
```python
newer = GatewayCharge.objects.filter(
    order=order, created__gt=gc.created
).exclude(status__in=['expired', 'failed']).exists()
if newer:
    return  # user switched method, skip failure
```
Prevents: PP expires → user switched to MB → Celery runs → incorrectly marks order payment_failed.

## Task Configuration
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_pending_charges(self):
    ...
    except Exception as exc:
        logger.error(...)
        # swallowed — does NOT re-raise
        # retry: self.retry(exc=exc) not called
```
**Note:** max_retries=3 and default_retry_delay=60s are defined but `self.retry()` is NOT called in the exception handler. Retry configured but not wired. Task failures are log-only.

**Schedule:** Not defined in tasks.py. Must be in celery beat schedule (likely `celeryconfig.py` or `settings.py`).

## Three Expiry Paths (all call same notification)
1. `sync_pending_charges` (Celery) — periodic
2. `ExpirePendingChargeView` — user-initiated
3. `expire_stale_payments` management command — manual/deploy

All three must call `_send_payment_failed_notifications(order, reason='expired')`. See [[promptpay-no-webhook-on-expiry]].

## Related
- [[payment-status-enums]] — METHOD_EXPIRY constants
- [[promptpay-no-webhook-on-expiry]] — why no Omise webhook on PP expiry
- [[payment-gateway-charge-architecture]] — ExpirePendingChargeView 6-case table
- [[payment-finalize-deep-dive]] — finalize_payment called on recovery
- [[payment-sentinel-idempotency]] — notification dedup
