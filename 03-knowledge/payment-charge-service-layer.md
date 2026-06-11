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

## Decision
Canonical charge = LATEST `GatewayCharge` per order. Historical charges must NOT trigger finalization/display.

## Tradeoffs
- Idempotency hash: small perf overhead on init. Worth it for retry safety.
- Minor-unit conversion: zero-decimal handling adds complexity. JPY bug proves it matters.

## Consequences
- Duplicate charge prevention at DB level
- JPY overcharge risk eliminated
- Polling fallback available for stuck charges

## Related
- [[payment-status-enums]]
- [[payment-gateway-charge-architecture]]
- [[payment-integration]]