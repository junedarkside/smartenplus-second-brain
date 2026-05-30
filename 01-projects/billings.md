# Billings — Payment Methods

## Summary
Checkout billing profiles. `BillingProfile.get_or_new()` handles authenticated + guest checkout. `PaymentMethod` encodes Thai payment types with fees and polling intervals.

---

## Models

### BillingProfile
Checkout billing profile. Links `Account` (nullable for guest). `slug` = unique ID (email or generated). `customer_id` = Omise customer ID, auto-created on first save via `pre_save_customer_id_field`.

**`get_or_new(request, email=None)` manager method:**
- Authenticated → look up `(user, active=True)`
- Guest → look up `(user__isnull=True, slug=email)`
- Not found → deactivate old profiles for same user/email, create new
- Returns `(billing_profile, created)` tuple

Guest checkout: `user=None`, `slug=email`, `guest_email=email`. No Account needed.

### PaymentMethod
Payment type config. Drives frontend payment selector via `/gateway-fee/` API.

**Payment types:**
| Type | Category | Notes |
|------|----------|-------|
| `CC` | Credit Card | |
| `DEBIT_CARD` | Debit Card | |
| `PP` | PromptPay | QR, polling required |
| `WECHAT_PAY` | E-Wallet | |
| `ALIPAY` / `ALIPAY_CN` / `ALIPAY_HK` | E-Wallet | |
| `KAKAO_PAY` | E-Wallet | |
| `TRUEMONEY` | E-Wallet | |
| `LINE_PAY` | E-Wallet | |
| `MB_SCB` / `MB_KTB` / `MB_KBANK` / `MB_BBL` / `MB_BAY` | Mobile Banking | SCB, KTB, KBANK, BBL, BAY |
| `GP` | Digital Wallet | Google Pay |
| `APPLE_PAY` | Digital Wallet | Apple Pay |
| `PAYPAL` | Digital Wallet | |

**Fields:** `fee` (decimal, default 0.03 = 3%), `polling_interval` (ms, default 5000), `description`, `actived`, `sort_order`.

---

## Related
- [[backend-architecture]]
- [[accounts]] (Account model)
- [[payment-system]] (Omise integration, charge flow)