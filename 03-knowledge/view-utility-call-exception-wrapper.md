# View-Layer Utility Call Exception Wrapper

## Summary
When a DRF view calls a utility function that can raise, wrap the call in `try/except` at the view boundary. Convert unhandled exceptions to `ValidationError` so DRF returns JSON 400 — not Django HTML 500.

## Why It Matters
DRF's exception handler only catches DRF exceptions (`APIException` subclasses). Any `AttributeError`, `ValueError`, or generic `Exception` from internal utility code propagates to Django's 500 handler, which returns an HTML page. RTK Query receives `PARSING_ERROR` (string status) and the frontend sees a generic crash — the real cause is hidden.

Reusable for any view → utility call where the utility has weak internal exception handling (especially anything reading model fields that may be `None`).

## Detail
**Pattern in `carts/views.py`:**
```python
try:
    advance_ok = check_advance_hour(contract_id, traveling_date_str)
except Exception:
    logger.exception("[CartItem] check_advance_hour crashed for contract_id=%s", contract_id)
    raise ValidationError("Unable to validate booking time. Please try again.")
```

The wrapper is *not* a fix to `check_advance_hour` itself (that needs internal null guards). It's a defense-in-depth boundary that ensures the *API contract* (JSON 400 with a message) holds even if the utility regresses or hits a new edge case.

**Companion: log the call site context.** `logger.exception` records the full traceback server-side so the root cause is debuggable from logs even though the user sees only "try again."

## Constraints / Gotchas
- The wrapper is **not** a substitute for fixing the utility's own null guards. Internal guards at `carts/utils.py:591` (`contract.trip.departure_time if contract.trip else None`) are the primary fix; the wrapper is a backstop.
- Use `except Exception`, not `except` (bare). Bare catches `BaseException` including `KeyboardInterrupt` and `SystemExit` — wrong.
- Re-raise as `ValidationError`, not return a JSON response. The view's serializer context handles the response shape.
- Frontend may still mis-handle `PARSING_ERROR` (string `status` from RTK Query) when the response is HTML — fix `error.status >= 500` checks separately. See [[cartitems-500-error-analysis-2026-06-02]] Bug 3.

## Related
- [[cartitems-500-error-analysis-2026-06-02]] — origin story (production 500 on `/carts/{id}/cartitems/`)
- [[contract-trip-null-non-transport-pattern]] — internal null-guard fix at `carts/utils.py:591`
- [[payment-checkout-architecture-audit]] — broader error handling patterns
