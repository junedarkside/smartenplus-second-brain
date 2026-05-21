# Payments — Deep Dive

## Summary
`payments/services.py` is the canonical source. `create_charge()` for charge creation, `reconcile_gateway_charge()` for polling, `_sync_order_status()` for order sync. `_to_minor_units()` handles JPY zero-decimal correctly.

---

## `_to_minor_units(amount, currency)`

Converts base currency to Omise minor units. THB/EUR/USD ×100. JPY ×1.

```python
ZERO_DECIMAL_CURRENCIES = {'JPY'}

def _to_minor_units(amount, currency='THB'):
    if currency.upper() in ZERO_DECIMAL_CURRENCIES:
        return int(Decimal(str(amount)).quantize(Decimal('1')))
    return int((Decimal(str(amount)) * 100).quantize(Decimal('1')))
```

Bug fixed 2026-05-13: previous `_to_satang()` multiplied JPY by 100 → 100× overcharge.

---

## `create_charge(idempotency_key, payment_method, amount_thb, currency='THB', token=None, return_uri=None)`

1. Compute `request_hash = _idempotency_hash(method, amount, currency)`.
2. Check existing `IdempotencyKey` — if found and hash matches, return cached charge (idempotent reuse).
3. If hash mismatches → raise `ValueError` (caller must use fresh idempotency key).
4. Compute `expires_at` for source-based payments (QR, mobile banking, e-wallets) via `METHOD_EXPIRY`.
5. Create Omise source + charge based on payment method:
   - **PromptPay:** source(type='promptpay') → charge(source=id)
   - **Credit/Debit:** charge(card=token, return_uri=)
   - **Mobile banking:** source(type=method) → charge(source=id, return_uri=)
   - **E-wallets (LINE Pay etc):** source with HTTPS return_uri check
6. Store `GatewayCharge` + `IdempotencyKey`.

---

## `reconcile_gateway_charge(gateway_charge)`

Polling fallback. Queries Omise live for charge status → updates local `GatewayCharge.status`.

```python
client.Charge.retrieve(gateway_charge.gateway_charge_id)
→ map_omise_status(omise_status) → PaymentStatus mapping
→ update GatewayCharge status
```

Called from:
- `sync_pending_charges` celery task (mobile banking/redirect, expired pending)
- `orders/views.py` orderdetails polling endpoint

---

## `_sync_order_status(order, gc_status=None)`

Syncs `GatewayCharge.status` → `Order.status`. Called after `reconcile_gateway_charge()`.

If `gc_status == 'paid'` → calls `finalize_payment(order)`.
If `gc_status in ('expired', 'failed')` → calls `finalize_payment_failed(order)`.

---

## IdempotencyKey Pattern

```python
def _idempotency_hash(payment_method, amount_thb, currency):
    return hashlib.sha256(json.dumps({
        'method': payment_method,
        'amount': str(amount_thb),
        'currency': currency,
    }, sort_keys=True).encode()).hexdigest()
```

On charge request: lookup key → hash match → reuse existing charge. Hash mismatch → error (caller must reset key).

---

## Payment Processing Banner (`isPaymentProcessing`)

Frontend-only feature. Shows countdown banner during active payment across all tabs via redux-persist.

**Lifecycle:**
- **Set:** `useOmisePayment.js` `processPayment()` — after charge creation succeeds (status 200/201). Dispatches `setPaymentProcessing({ timestamp, expiresAt })`
- **expiresAt:** Backend-sourced from charge response `expires_at`. QR/mobile banking: matches `METHOD_EXPIRY`. Card/redirect: `null` → 15-min fallback
- **Clear:** order detail pages (paid status), `ORDER_ALREADY_PAID`, `alreadyPaid` 409, general errors, 5-min timeout on `expiresAt`, 30-min stale rehydration guard
- **Component:** `GlobalPaymentWarning` uses `AlertMessage` with `warning` type. Rendered in `checkout/index.js` under step nav
- **No hardcoded timing:** `qr_expiry_minutes` removed from frontend payload. Backend `METHOD_EXPIRY` is source of truth

**Redux state:** `paymentStatusSlice.js` — `{ isPaymentProcessing, paymentInitiatedAt, expiresAt }`

**Rehydration guard:** `reconcileStaleProcessing` — auto-clears if `paymentInitiatedAt` >30 min on store rehydration

---

## Related
- [[payment-system]]
- [[backend-architecture]]
- [[celery-tasks]] (sync_pending_charges task)