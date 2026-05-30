# Payments — Enums & Constants

## Summary
`payments/enums.py`. `PaymentStatus` drives GatewayCharge state machine. `OmiseMethod` maps Thai payment methods. `REDIRECT_METHODS` for duplicate charge prevention. `METHOD_EXPIRY` defines charge TTL.

## PaymentStatus
```
pending → processing → paid
pending → failed
pending → expired
paid → refunded
paid → partial_refunded
```

## OmiseMethod

| Constant | Value | Category |
|---------|-------|----------|
| `PROMPTPAY` | `promptpay` | QR code |
| `CREDIT_CARD` | `credit_card` | Card |
| `DEBIT_CARD` | `debit_card` | Card |
| `WECHAT_PAY` | `wechat_pay` | E-wallet |
| `ALIPAY` | `alipay` | E-wallet |
| `ALIPAY_CN` | `alipay_cn` | E-wallet (China) |
| `ALIPAY_HK` | `alipay_hk` | E-wallet (HK) |
| `KAKAO_PAY` | `kakao_pay` | E-wallet |
| `TRUEMONEY` | `truemoney` | E-wallet |
| `LINE_PAY` | `line_pay` | E-wallet |
| `MB_SCB` | `mobile_banking_scb` | Mobile banking |
| `MB_KTB` | `mobile_banking_ktb` | Mobile banking |
| `MB_KBANK` | `mobile_banking_kbank` | Mobile banking |
| `MB_BBL` | `mobile_banking_bbl` | Mobile banking |
| `MB_BAY` | `mobile_banking_bay` | Mobile banking |

## REDIRECT_METHODS
Frozenset of all OmiseMethod values **except** `PROMPTPAY`. Redirect methods need user to complete on external page — duplicate pending charge = money lost. PP excluded: inline QR, safe to regenerate.

In `initiate_order_charge`: Step C3 — block if another PENDING redirect charge → 409 `pending_charge_exists`.

## METHOD_EXPIRY

```python
METHOD_EXPIRY = {
    OmiseMethod.PROMPTPAY: timedelta(minutes=10),
    OmiseMethod.MB_SCB:    timedelta(minutes=10),
    OmiseMethod.MB_KTB:    timedelta(minutes=10),
    OmiseMethod.MB_KBANK:   timedelta(minutes=10),
    OmiseMethod.MB_BBL:     timedelta(minutes=10),
    OmiseMethod.MB_BAY:     timedelta(minutes=10),
}
```

Cards/e-wallets: no expiry (synchronous or webhook). E-wallet stale reconciliation: methods not in `METHOD_EXPIRY` reconciled after 30 min in `sync_pending_charges`. CC/debit excluded (never stale).

In `create_charge()`: `expires_at = now() + METHOD_EXPIRY[method]`.

## CURRENCY_MIN_AMOUNT

```python
CURRENCY_MIN_AMOUNT = {
    'THB': Decimal('20.00'), 'JPY': Decimal('100'),
    'SGD': Decimal('1.00'),  'MYR': Decimal('1.00'),
}
```

## Related
- [[payment-system]]
- [[payments-deep-dive]]
