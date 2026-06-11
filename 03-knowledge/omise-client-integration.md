# Omise Client Integration Patterns

## Summary
5 non-obvious Omise SDK patterns: lazy module-level init, `_attributes` dict extraction, LINE_PAY→rabbit_linepay rename, `reversed`→PENDING status mapping, PromptPay QR URI nested path.

## Context
`payments/gateway.py`, `payments/services.py`. These patterns cause silent failures if unknown. Direct property access on Omise objects is unreliable — always use `_attributes`.

## Patterns

### 1. Lazy Client Init (`payments/gateway.py:5-7`)
```python
import omise
from decouple import config

def get_omise_client():
    omise.api_secret = config('OMISE_SEC_KEY')
    return omise  # returns MODULE, not instance
```
- Sets `omise.api_secret` on **module object** at call time, not import time
- Returns the `omise` module itself (not a client object — no `OmiseClient()` constructor)
- Thread-safe: Python GIL + same value each call = safe module-level mutation
- `OMISE_PUB_KEY` env var exists but frontend-only; backend never uses it
- Call `get_omise_client()` at top of each function that needs Omise — don't cache the return value across requests

### 2. `_attributes` Dict Extraction (`payments/services.py:164-172, 215-222`)
```python
# WRONG — may return None even if field exists in Omise response
omise_charge.expires_at

# CORRECT — always use _attributes
raw_expires = omise_charge._attributes.get('expires_at')
if raw_expires:
    expires_at = dateutil.parser.parse(raw_expires)
```
Omise SDK wraps raw JSON response in `__dict__['_attributes']`. Direct property access delegates to `__getattr__` which can silently return `None` on missing keys. All date/time fields must be extracted via `_attributes.get()` with try-except on parse.

Fields typically accessed via `_attributes`:
- `expires_at` / `expired_at`
- `failure_code` / `failure_message`
- `net` (settlement amount in minor units)
- `status` (always use this path for status comparisons)

### 3. LINE_PAY Source Type Rename (`payments/services.py:140`)
```python
# OmiseMethod.LINE_PAY value is 'line_pay'
# But Omise source API requires:
source_type = 'rabbit_linepay'  # NOT 'line_pay'
```
Omise's branding for LINE Pay is "Rabbit LINE Pay". Source type must be `rabbit_linepay`. All other methods use their `OmiseMethod` enum value directly as `source.type`. This is the only exception.

### 4. `OMISE_STATUS_MAP` — `reversed` → PENDING (`payments/services.py:16-25`)
```python
OMISE_STATUS_MAP = {
    'successful': PaymentStatus.PAID,
    'pending':    PaymentStatus.PENDING,
    'failed':     PaymentStatus.FAILED,
    'expired':    PaymentStatus.EXPIRED,
    'reversed':   PaymentStatus.PENDING,   # intentional — not a terminal state
    'authorized': PaymentStatus.PAID,      # no local capture distinction
}
# Unmapped statuses also default to PENDING
```
`reversed` = Omise's "authorization reversed" (authorized but never captured). Maps to PENDING because local system never distinguishes capture stage. `authorized` maps to PAID — finalization is amount-based, not capture-based.

### 5. PromptPay QR URI — Nested Path (`payments/services.py:78-96`)
```python
# PromptPay: QR code is deeply nested
qr_code_uri = omise_charge.source.scannable_code.image.download_uri

# All other methods: authorize_uri at charge level
authorize_uri = omise_charge.authorize_uri
# Note: PromptPay's authorize_uri is EMPTY — don't use it for PP
```
PromptPay creates a Source, then a Charge. The QR image URL lives at `charge.source.scannable_code.image.download_uri`. All non-PromptPay source methods use `charge.authorize_uri` for the redirect URL.

## Related
- [[payment-charge-service-layer]] — create_charge orchestration
- [[payment-status-enums]] — OmiseMethod constants, OMISE_STATUS_MAP
- [[payment-backend-charge-flow]] — full charge creation flow including DB constraint
- [[omise-webhook-security]] — Event.retrieve() verification pattern
- [[omise-api-reference-2026-06-12]] — full Omise API catalog
