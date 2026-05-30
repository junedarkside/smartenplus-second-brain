# Payments — Deep Dive

## Summary
`payments/services.py` = canonical source. `create_charge()`, `reconcile_gateway_charge()`, `_sync_order_status()`, `_to_minor_units()`.

## `_to_minor_units(amount, currency)`

THB/EUR/USD ×100. JPY ×1.

```python
ZERO_DECIMAL_CURRENCIES = {'JPY'}
def _to_minor_units(amount, currency='THB'):
    if currency.upper() in ZERO_DECIMAL_CURRENCIES:
        return int(Decimal(str(amount)).quantize(Decimal('1')))
    return int((Decimal(str(amount)) * 100).quantize(Decimal('1')))
```

Bug fixed 2026-05-13: `_to_satang()` multiplied JPY by 100 → 100× overcharge.

## `create_charge(idempotency_key, payment_method, amount_thb, currency, token, return_uri)`

1. Compute `request_hash = _idempotency_hash(method, amount, currency)`
2. Check existing `IdempotencyKey` — hash match → return cached charge (idempotent)
3. Hash mismatch → `ValueError` (caller must use fresh key)
4. Compute `expires_at` via `METHOD_EXPIRY` for source-based payments
5. Create Omise source + charge per method:
   - **PromptPay:** source(type='promptpay') → charge(source=id)
   - **Credit/Debit:** charge(card=token, return_uri=)
   - **Mobile banking:** source(type=method) → charge(source=id, return_uri=)
   - **E-wallets:** source with HTTPS return_uri check
6. Store `GatewayCharge` + `IdempotencyKey`

## `reconcile_gateway_charge(gateway_charge)`

Polling fallback. Queries Omise live → updates local status.

```python
client.Charge.retrieve(gateway_charge.gateway_charge_id)
→ map_omise_status() → update GatewayCharge
```

Called from: `sync_pending_charges` celery task, orderdetails polling endpoint.

## `_sync_order_status(order, gc_status)`

GatewayCharge.status → Order.status. `paid` → `finalize_payment()`. `expired/failed` → `finalize_payment_failed()`.

## IdempotencyKey Pattern

```python
def _idempotency_hash(payment_method, amount_thb, currency):
    return hashlib.sha256(json.dumps({
        'method': payment_method, 'amount': str(amount_thb), 'currency': currency,
    }, sort_keys=True).encode()).hexdigest()
```

Hash match → reuse. Mismatch → error.

## Payment Processing Banner (`isPaymentProcessing`)

Frontend-only. Shows countdown during active payment across tabs via redux-persist.

**Lifecycle:**
- **Set:** `useOmisePayment.js` after charge creation (200/201). `setPaymentProcessing({ timestamp, expiresAt })`
- **expiresAt:** Backend `expires_at`. QR/MB: `METHOD_EXPIRY`. Card: null → 15-min fallback
- **Clear:** paid status, `ORDER_ALREADY_PAID`, errors, 5-min timeout, 30-min stale guard
- **Component:** `GlobalPaymentWarning` via `AlertMessage` warning type. Rendered in `checkout/index.js`
- **No hardcoded timing:** Backend `METHOD_EXPIRY` = source of truth

**Redux:** `paymentStatusSlice.js` — `{ isPaymentProcessing, paymentInitiatedAt, expiresAt }`
**Rehydration guard:** `reconcileStaleProcessing` — auto-clears if >30 min

## Related
- [[payment-system]]
- [[backend-architecture]]
- [[celery-tasks]]
