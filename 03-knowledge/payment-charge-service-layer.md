# Payment Charge Service Layer

## Summary
Canonical charge operations: create, reconcile, sync. Idempotency via hash. Minor-unit conversion per currency.

## Context
Payment processing backend. All charge creation flows through here. Must be idempotent for retry safety.

## Problem
Duplicate charges = money lost. Currency conversion bugs = overcharge (JPY fixed 2026-05-13).

## Details

### `_to_minor_units(amount, currency)`
THB/EUR/USD ×100. JPY ×1 (zero-decimal).

```python
ZERO_DECIMAL_CURRENCIES = {'JPY'}
def _to_minor_units(amount, currency='THB'):
    if currency.upper() in ZERO_DECIMAL_CURRENCIES:
        return int(Decimal(str(amount)).quantize(Decimal('1')))
    return int((Decimal(str(amount)) * 100).quantize(Decimal('1')))
```

### `create_charge(idempotency_key, payment_method, amount_thb, currency, token, return_uri)`
1. Check `locked_amount`: if set and new amount ≠ locked, raise 409 `amount_locked` error. Same amount allowed (idempotent).
2. Hash(method, amount, currency) → idempotency key
3. Match → return cached. Mismatch → error (caller must use fresh key)
4. Compute `expires_at` via `METHOD_EXPIRY` for source-based payments
5. Create Omise source + charge per method:
   - **PromptPay:** source(type='promptpay') → charge(source=id)
   - **Credit/Debit:** charge(card=token, return_uri=)
   - **Mobile banking:** source(type=method) → charge(source=id, return_uri=)
   - **E-wallets:** source with HTTPS return_uri check
6. Store `GatewayCharge` + `IdempotencyKey`

### `reconcile_gateway_charge(gateway_charge)`
Polling fallback. Queries Omise live → updates local status.

```python
client.Charge.retrieve(gateway_charge.gateway_charge_id)
→ map_omise_status() → update GatewayCharge
```

### `_sync_order_status(order, gc_status)`
GatewayCharge.status → Order.status. `paid` → `finalize_payment()`. `expired/failed` → `finalize_payment_failed()`.

### IdempotencyKey Pattern
```python
def _idempotency_hash(payment_method, amount_thb, currency):
    return hashlib.sha256(json.dumps({
        'method': payment_method, 'amount': str(amount_thb), 'currency': currency,
    }, sort_keys=True).encode()).hexdigest()
```
Hash match → reuse. Mismatch → error.

**Staleness reuse:** If matching key found but linked charge is older than `METHOD_EXPIRY[method]`, treat key as stale. Delete old IdempotencyKey + GatewayCharge, create fresh. Prevents ghost charges from blocking retries after method expiry.

## Decision
Canonical charge = LATEST `GatewayCharge` per order. Historical charges must NOT trigger finalization/display.

## Tradeoffs
- Idempotency hash: small perf overhead on init. Worth it for retry safety.
- Minor-unit conversion: zero-decimal handling adds complexity. JPY bug proves it matters.

## Consequences
- Duplicate charge prevention at DB level
- JPY overcharge risk eliminated
- Polling fallback available for stuck charges

## Omise Response Extraction
All Omise SDK fields extracted via `_attributes` dict, NOT direct property access:
```python
# WRONG — silently returns None on missing keys
omise_charge.expires_at

# CORRECT
raw_expires = omise_charge._attributes.get('expires_at')
```
Affects: `expires_at`, `failure_code`, `failure_message`, `net`, `status`. See [[omise-client-integration]].

## 5-Second Reconciliation Throttle
`reconcile_gateway_charge()` skips Omise API call if `gc.updated < 5 seconds ago`:
```python
if (now() - gc.updated).seconds < 5:
    return gc  # already fresh
```
Called on every order-detail page load — throttle prevents 429 rate limit.

## Stale Charge Expiry (TOCTOU Guard)
`_handle_existing_charge()`: stale charge + new attempt → expire old first:
```python
with transaction.atomic():
    order = Order.objects.select_for_update().get(pk=order.pk)
    omise_charge.expire()  # lock BEFORE expire to block concurrent webhook finalization
    order.payment_notification_sent_at = None  # re-enable notification on next success
```
See [[payment-backend-charge-flow]] for full C3b pattern.

## Related
- [[payment-status-enums]]
- [[payment-gateway-charge-architecture]]
- [[payment-integration]]
- [[payment-sentinel-idempotency]] — staleness detection + IdempotencyKey lifecycle
- [[omise-client-integration]] — `_attributes` extraction, LINE_PAY rename, PromptPay QR URI
- [[payment-backend-charge-flow]] — DB constraint, TOCTOU guard, satang conversion, AllowAny auth