The CLI needs a real file path and calls Claude API. Since user pasted text directly, I'll compress inline.

# Payment Checkout E2E Testing — 2026-05-17

## Summary
E2E suite blocked by infra issues. Manual test guide created instead. Multiple session bugs found + fixed in follow-up.

## Context
Follow-up to `payment-checkout-architecture-audit-2026-05-17`. 20/20 audit pass. Playwright specs written via 6-agent team. E2E infra broken — MSW intercepts wrong URL (`api.smartenplus.co.th` vs `localhost:3000`). Specs deleted, manual test guide created.

## Bugs Found & Fixed

### Bug 1: Missing chargeId in cart 409 response
- `helpers/savePassengerAssignmentsToCart.js:123` — backend returns `charge_id` but frontend didn't extract
- Fix: `err.chargeId = errorData?.charge_id || null`
- Commit: `38c7320`

### Bug 2: Cart endpoint 409 missing charge_id
- `carts/views.py:171-183` — `_check_payment_pending` returned 409 without `charge_id`
- Fix: Lookup latest GatewayCharge, include in response
- Backend now returns `{'error': 'payment_pending', 'charge_id': '...'}`

### Bug 3: InlinePassengerSelector RTK mutation didn't extract charge_id
- RTK Query wraps errors differently: `error.status === 409`, `error.data.charge_id`
- Old code checked `error.error` — only works for raw fetch path
- Fix: Added `pendingChargeIdRef` + RTK error detection in InlinePassengerSelector.js

### Bug 4: session.user guard wrong — RESOLVED
- Session structure: `{ id, email, accessToken }` — no `user` wrapper
- `InlinePassengerSelector.js` + `EditableCartItem.js` cancel handlers used `!session?.user`
- Fix: Changed to `!session?.id`

### Bug 5: session?.user?.email in checkout/index.js — RESOLVED (2026-05-17)
- Root bug: `pages/checkout/index.js:46` — `const email = session?.user?.email || null`
- `session?.user` always `undefined` → `email` always `null` for all auth users
- Null propagated to 3 places:
  1. RTK cart query `{ cartId, email }` — always `email: null` for auth users
  2. `Itineraries.js:37` — `session?.user?.email || email` both null → cancel silently failed (early return)
  3. `savePassengerAssignmentsToCart.js:92` — dead code `session?.user?.email` condition never true
- Fix: `session?.user?.email` → `session?.email` in index.js
- Fix: `Itineraries.js` cancel handler rewritten — auth-aware (Bearer token for auth, email param for guests)
- Fix: `savePassengerAssignmentsToCart.js` dead email URL param removed

## Files Modified

| File | Change |
|------|--------|
| `carts/views.py` | Return charge_id in 409 response |
| `InlinePassengerSelector.js` | RTK 409 detection + chargeIdRef + session.id fix |
| `EditableCartItem.js` | Same as above |
| `savePassengerAssignmentsToCart.js` | chargeId extraction + remove dead session.user.email branch |
| `pages/checkout/index.js` | `session?.user?.email` → `session?.email` |
| `components/forms/checkout/Itineraries.js` | Auth-aware cancel handler with Bearer token |

## Key Lesson

Session structure: `{ id, email, accessToken }` — no `user` wrapper.
- Auth check: `session?.id`
- Email: `session?.email`
- Never: `session?.user?.email` or `session?.user`

## Expected Behavior (NOT bugs)

409 PAYMENT_PENDING on step 2 Next while cart locked = correct backend behavior.
Alert + "Cancel This Payment" button in FormCard = intended UX.
`FormCard.handleCancelPayment` uses Bearer token for auth users — correct.

## Manual Test Guide Created

**File:** `docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md`

## Related
- [[payment-checkout-architecture-audit-2026-05-17]]
- [[payment-system]]
- [[checkout-flow]]
- [[docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md]]
- [[docs/testing/PAYMENT_CHECKOUT_AUDIT.md]]