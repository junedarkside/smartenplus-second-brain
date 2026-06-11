# Omise SDK: `_attributes` Dict Extraction

## Summary
Omise Python SDK wraps raw JSON in `_attributes` dict. Direct property access silently returns `None` on missing keys. Always use `_attributes.get()`.

## Pattern
```python
# WRONG — silently None even if present in Omise response
charge.expires_at
charge.failure_code

# CORRECT
expires_raw = charge._attributes.get('expires_at')
failure_code = charge._attributes.get('failure_code')
```

## Why
Omise SDK `__getattr__` delegates to `_attributes` but returns `None` on `KeyError` instead of raising. No AttributeError = silent bug. Particularly dangerous for date fields where `None` skips expiry scheduling without any error.

## Fields That Need This
- `expires_at` / `expired_at`
- `failure_code` / `failure_message`
- `net` (settlement amount)
- `status`
- Any field from nested objects (source, scannable_code, etc.)

## SmartEnPlus Usage
`payments/services.py:164-172, 215-222`

## Related
- [[omise-client-integration]] — full Omise SDK integration patterns
