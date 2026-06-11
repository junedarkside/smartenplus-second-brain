# Payment Status Enums

## Summary
PaymentStatus state machine, OmiseMethod constants, REDIRECT_METHODS duplicate guard, METHOD_EXPIRY TTLs.

## Context
Payment method routing and charge lifecycle. Required reading before touching payment code.

## Problem
Wrong status = double-charge, stale QR, silent failures. Method constants scattered.

## Details

### PaymentStatus
```
pending → processing → paid
pending → failed
pending → expired
paid → refunded
paid → partial_refunded
```

**Status Machine Guards:** `clean()` enforced in Django admin only. NOT runtime `.save()`. Runtime accepts any state transition.

### Omise `authorized` Status (not-yet-captured)
Omise can return `authorized` (charge approved but not yet captured). Maps to SmartEnPlus `paid` on webhook finalization (webhook triggers `finalize_payment()` which is oblivious to capture state). Same flow as `successful`. No local distinction needed — finalization is amount-based, not capture-based.

### OmiseMethod
| Constant | Value | Category |
|---------|-------|----------|
| `PROMPTPAY` | `promptpay` | QR code |
| `CREDIT_CARD` | `credit_card` | Card |
| `DEBIT_CARD` | `debit_card` | Card |
| `WECHAT_PAY` | `wechat_pay` | E-wallet |
| `ALIPAY` | `alipay` | E-wallet |
| `KAKAO_PAY` | `kakao_pay` | E-wallet |
| `TRUEMONEY` | `truemoney` | E-wallet |
| `LINE_PAY` | `line_pay` | E-wallet |
| `MB_SCB` | `mobile_banking_scb` | Mobile banking |
| `MB_KTB` | `mobile_banking_ktb` | Mobile banking |
| `MB_KBANK` | `mobile_banking_kbank` | Mobile banking |
| `MB_BBL` | `mobile_banking_bbl` | Mobile banking |
| `MB_BAY` | `mobile_banking_bay` | Mobile banking |

### REDIRECT_METHODS
Frozenset of all OmiseMethod values **except** `PROMPTPAY`. Redirect methods need user to complete on external page — duplicate pending charge = money lost. PP excluded: inline QR, safe to regenerate.

Block if another PENDING redirect charge → 409 `pending_charge_exists`.

### METHOD_EXPIRY
```python
METHOD_EXPIRY = {
    OmiseMethod.PROMPTPAY: timedelta(minutes=10),
    OmiseMethod.MB_SCB:    timedelta(minutes=10),
    OmiseMethod.MB_KTB:    timedelta(minutes=10),
    OmiseMethod.MB_KBANK:  timedelta(minutes=10),
    OmiseMethod.MB_BBL:    timedelta(minutes=10),
    OmiseMethod.MB_BAY:    timedelta(minutes=10),
}
```
Cards/e-wallets: no expiry (synchronous or webhook). E-wallet stale reconciliation: methods not in `METHOD_EXPIRY` reconciled after 30 min.

### CURRENCY_MIN_AMOUNT
```python
CURRENCY_MIN_AMOUNT = {
    'THB': Decimal('20.00'), 'JPY': Decimal('100'),
    'SGD': Decimal('1.00'),  'MYR': Decimal('1.00'),
}
```

## Decision
`payment_failed` is recoverable: `ordering → payment_failed → paid` valid lifecycle. `finalize_payment_failed()` does NOT set `payment_finalized_at`.

## Tradeoffs
- METHOD_EXPIRY 10-min TTL: short enough to avoid stale QR, long enough for banking flows.
- E-wallets excluded from METHOD_EXPIRY: no reliable expiry signal. Reconciled after 30 min instead.

## Consequences
- QR expiry = 10 min hard limit
- Double-redirect charge blocked at API level
- `payment_failed` treated as non-terminal

## Related
- [[payment-charge-service-layer]]
- [[payment-gateway-charge-architecture]]
- [[payment-integration]]