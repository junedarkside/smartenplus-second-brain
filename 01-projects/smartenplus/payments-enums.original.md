# Payments — Enums & Constants

## Summary
`payments/enums.py` defines payment system constants. `PaymentStatus` drives GatewayCharge state machine. `OmiseMethod` maps all supported Thai payment methods. `REDIRECT_METHODS` frozenset is critical for duplicate charge prevention. `METHOD_EXPIRY` defines charge TTL for QR/redirect methods.

---

## PaymentStatus
Domain statuses for `GatewayCharge`.

```
pending → processing → paid
pending → failed
pending → expired
paid → refunded
paid → partial_refunded
```

---

## OmiseMethod
All supported payment methods:

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

---

## REDIRECT_METHODS
Frozenset of all `OmiseMethod` values **except** `PROMPTPAY`.

**Why:** Redirect methods (mobile banking, e-wallets) require user to complete payment on external page. If user retries before completing, duplicate pending charge is created → money lost.

**PromptPay excluded:** inline QR code, safe to regenerate multiple times.

**In `initiate_order_charge`:** Step C3 — block if another PENDING redirect charge exists for same order → 409 `pending_charge_exists`.

---

## METHOD_EXPIRY
Charge TTL (time-to-live) for source-based payments:

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

All others (card, e-wallets) have no expiry — charge completes synchronously or waits for webhook.

**E-wallet stale reconciliation (2026-05-18):** Methods not in `METHOD_EXPIRY` (truemoney, line_pay, alipay, alipay_cn, alipay_hk, kakao_pay, wechat_pay) are reconciled after 30 min in `sync_pending_charges` Celery task. Credit/debit cards excluded (synchronous, never stale).

**In `create_charge()`:** `expires_at` computed as `now() + METHOD_EXPIRY[method]` for methods in dict.

---

## CURRENCY_MIN_AMOUNT
Minimum chargeable amount per currency:

```python
CURRENCY_MIN_AMOUNT = {
    'THB': Decimal('20.00'),
    'JPY': Decimal('100'),
    'SGD': Decimal('1.00'),
    'MYR': Decimal('1.00'),
}
```

Omise rejects charges below minimum. Backend should validate before creating charge.

---

## Related
- [[payment-system]] (charge creation flow, ExpirePendingChargeView)
- [[payments-deep-dive]] (create_charge, _to_minor_units)