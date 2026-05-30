# Payment Checkout E2E Testing

## Summary
E2E suite blocked by MSW intercept bug. Manual test guide created. 5 bugs found + fixed in follow-up.

## Context
20/20 audit pass. Playwright specs written via 6-agent team. MSW intercepted wrong URL (`api.smartenplus.co.th` vs `localhost:3000`). Specs deleted, manual test guide created.

## Bugs Found & Fixed

### Bug 1: Missing chargeId in cart 409 response
Backend returns `charge_id` but frontend didn't extract.
Fix: `err.chargeId = errorData?.charge_id || null`

### Bug 2: Cart endpoint 409 missing charge_id
`_check_payment_pending` returned 409 without `charge_id`.
Fix: Lookup latest GatewayCharge, include in response.

### Bug 3: InlinePassengerSelector RTK mutation didn't extract charge_id
RTK Query wraps errors differently: `error.status === 409`, `error.data.charge_id`.
Old code checked `error.error` — only works for raw fetch path.
Fix: Added `pendingChargeIdRef` + RTK error detection.

### Bug 4: session.user guard wrong
Session structure: `{ id, email, accessToken }` — no `user` wrapper.
`!session?.user` always true → auth check broken.
Fix: Changed to `!session?.id`

### Bug 5: session?.user?.email in checkout
`session?.user` always `undefined` → `email` always `null` for all auth users.
Null propagated to: RTK cart query, Itineraries cancel handler, savePassengerAssignmentsToCart dead code.
Fix: `session?.user?.email` → `session?.email`

## Session Structure Rule
```javascript
// Auth check
session?.id
// Email
session?.email
// Never
session?.user?.email
session?.user
```

## Expected Behavior (NOT bugs)
- 409 PAYMENT_PENDING on step 2 Next while cart locked = correct backend behavior
- Alert + "Cancel This Payment" button in FormCard = intended UX
- `FormCard.handleCancelPayment` uses Bearer token for auth users — correct

## Consequences
- RTK 409 detection now works across all mutation paths
- Auth session access normalized
- Manual test guide covers all critical payment flows

## Related
- [[payment-gateway-charge-architecture]]
- [[checkout-flow]]
- [[nextauth-session-shape]]