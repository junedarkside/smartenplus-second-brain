# Payment Checkout E2E Testing — 2026-05-17

## Summary
E2E test suite attempted but E2E infrastructure issues prevented running. Manual test guide created as alternative. Multiple session bugs found and fixed in follow-up session.

## Context
Follow-up to `payment-checkout-architecture-audit-2026-05-17`. 20/20 audit pass. Wrote Playwright specs via 6-agent team, found E2E infrastructure broken — MSW intercepts wrong URL (`api.smartenplus.co.th` vs `localhost:3000`). E2E specs deleted, manual test guide created instead.

## Bugs Found & Fixed

### Bug 1: Missing chargeId in cart 409 response
- `helpers/savePassengerAssignmentsToCart.js:123` — backend returns `charge_id` but frontend wasn't extracting it
- Fix: `err.chargeId = errorData?.charge_id || null`
- Commit: `38c7320`

### Bug 2: Cart endpoint 409 missing charge_id
- `carts/views.py:171-183` — `_check_payment_pending` returned 409 without `charge_id`
- Fix: Added lookup of latest GatewayCharge and include in response
- Backend now returns `{'error': 'payment_pending', 'charge_id': '...'}`

### Bug 3: InlinePassengerSelector RTK mutation didn't extract charge_id
- RTK Query wraps errors differently: `error.status === 409`, `error.data.charge_id`
- Old code checked `error.error` which only works for raw fetch path
- Fix: Added `pendingChargeIdRef` + RTK error detection in InlinePassengerSelector.js

### Bug 4: session.user guard wrong — RESOLVED
- Session structure: `{ id, email, accessToken }` — no `user` wrapper
- `InlinePassengerSelector.js` + `EditableCartItem.js` cancel handlers used `!session?.user` check
- Fix: Changed to `!session?.id` — correct authenticated check

### Bug 5: session?.user?.email in checkout/index.js — RESOLVED (2026-05-17)
- Root bug: `pages/checkout/index.js:46` — `const email = session?.user?.email || null`
- `session?.user` is always `undefined` → `email` always `null` for all authenticated users
- This null propagated to 3 places:
  1. RTK cart query `{ cartId, email }` — always sent `email: null` for auth users
  2. `Itineraries.js:37` — `session?.user?.email || email` both null → cancel silently failed (early return)
  3. `savePassengerAssignmentsToCart.js:92` — dead code `session?.user?.email` condition never true
- Fix: `session?.user?.email` → `session?.email` in index.js
- Fix: `Itineraries.js` cancel handler rewritten to be auth-aware (Bearer token for auth, email param for guests)
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

Session structure in this codebase: `{ id, email, accessToken }` — no `user` wrapper.
- Auth check: `session?.id`
- Email: `session?.email`
- Never: `session?.user?.email` or `session?.user`

## Expected Behavior (NOT bugs)

The 409 PAYMENT_PENDING when clicking Next on step 2 while cart is locked = correct backend behavior.
The alert + "Cancel This Payment" button in FormCard is the intended UX.
`FormCard.handleCancelPayment` correctly uses Bearer token for auth users.

## Manual Test Guide Created

**File:** `docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md`

## Related
- [[payment-checkout-architecture-audit-2026-05-17]]
- [[payment-system]]
- [[checkout-flow]]
- [[docs/testing/PAYMENT_CHECKOUT_MANUAL_TEST_GUIDE.md]]
- [[docs/testing/PAYMENT_CHECKOUT_AUDIT.md]]
