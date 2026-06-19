# Payment Guest Email Guard Mirror

## Summary
Every charge entry point (`ChargeOrderView`, `ExpirePendingChargeView`, etc.) must validate `order.email == data['email']` for unauthenticated requests. Missing in `ChargeOrderView` is the M8 bug. The fix is to mirror the `ExpirePendingChargeView` pattern, not invent a new one.

## Context
Guest users create orders with `user=None` and an `email` field. The order-charge and expire-pending-charge views both look up orders by guest markers. The two views have asymmetric authorization:

- `ExpirePendingChargeView` (`payments/views.py:374-377`) — checks `order.email == request.data.get('email')` for unauthenticated requests. Returns 403 on mismatch.
- `ChargeOrderView` (`payments/views.py:109`) — matches `user__isnull=True` only. Does NOT check `order.email`. The FE sends `email` in body, BE never reads it.

This asymmetry is the M8 attack surface. Any user who knows a guest `order_id` can initiate charges on someone else's order: charge the wrong card, expire the wrong QR, lock the wrong amount, all by replaying the standard `POST /payments/order-charge/` request with the victim's `order_id` and any email.

The KB (`docs/operations/CHECKOUT.md` and the historical comments at `views.py:374-377`) implies email is checked everywhere. Code shows it isn't. This drift between docs and code is the bug.

## Problem
M8 in [[payment-deep-review]]. The fix is to mirror the existing `ExpirePendingChargeView` pattern to all charge entry points. The mirror is small (4 lines) and the contract is clear.

Specifics:
- The `order_id` is exposed in URLs like `/ordersummary/{id}/`, in email links, in user-facing pages. Not a secret.
- An attacker who has the `order_id` can already view the order's email (it's rendered in the order summary page). The guard is not about secrecy — it's about authorization for the action.
- Symmetric attack: a user who creates a guest order and forgets the email can be locked out by an attacker who changes the email... no, the guard is the other direction. The guard protects the order owner from unauthorized charges. It does not protect an order owner from impersonation by an attacker who knows both the `order_id` and the `email`. That requires stronger auth (magic link, OTP).

## Details
Add to `ChargeOrderView` after the `Order.objects.filter(id=..., user__isnull=True).first()` lookup:

```python
if not request.user.is_authenticated and order.email != request.data.get('email'):
    return Response({"detail": "Email mismatch"}, status=403)
```

Mirror invariant — any view that:
1. Takes an `order_id` and operates on a guest order, AND
2. Mutates order or charge state, AND
3. Is reachable by unauthenticated requests

MUST check `order.email` against request body `email` for unauthenticated requests. The check pattern (in order):
1. After order lookup (so the email is available)
2. Before any state mutation (so the check is the gate, not a post-hoc audit)
3. Only for unauthenticated requests (`request.user.is_authenticated` is False)
4. Return 403 (not 404) — the order exists, the caller is just not authorized

The `request.data.get('email')` is None-safe. If FE omits `email`, `None != order.email` → 403. This is intentional — omitting email is not a way to bypass the check.

## Decision
Mirror the existing `ExpirePendingChargeView` pattern exactly. No new abstraction (no helper, no mixin) — one extra 4-line block per view. Reuse > abstraction when 2 sites and no third on the horizon.

The 403 response shape is consistent with the existing `ExpirePendingChargeView` response shape. FE error handling already handles 403 from this endpoint. No new FE code needed.

The `not request.user.is_authenticated` guard is critical. For authenticated requests, the `user__isnull=False` filter is the check. Don't double-validate — an authenticated user requesting a charge on their own order should not need to send `email` in body.

## Tradeoffs
- **2 sites only** — premature to extract a mixin. If a 3rd view needs this pattern (likely: future refund-initiation guest view, or guest re-charge), extract `assert_guest_email_match(request, order)` then. Don't predict the 3rd site.
- **403 vs 404.** 403 leaks order existence. Acceptable: the attacker already has the `order_id` (it's in the URL). 404 would be misleading ("order doesn't exist" when it does). 403 is the honest response.
- **No rate limiting added.** Existing `AnonRateThrottle` (500/h global) covers brute force. Per-endpoint throttle on order-charge is a separate concern. Adding it now mixes concerns.
- **Email in body is the FE's responsibility.** The check trusts that FE sends the email. If FE ever stops sending it (e.g. a refactor moves email out of body to header), the check breaks silently. Add a test that sends a request without email and asserts 403.
- **Doesn't protect authenticated users.** The M8 fix only covers guest flows. An attacker who has a valid auth token can still charge any order they own. That's a different threat model (account takeover) and a different fix (MFA, session management).

## Consequences
- M8 attack surface closes
- KB (`docs/operations/CHECKOUT.md` and inline comments) is now consistent with code
- Future charge entry points (refund-initiate, capture, void, re-charge) MUST copy this pattern. Add to PR-review checklist.
- A new guest-flow view (e.g. guest order history, guest re-book) inherits the same email-guard responsibility
- Test gap: "guest cross-user charge initiation (M8)" is missing test in [[payment-deep-review]]; add one. Test cases: (a) guest tries to charge another guest's order → 403, (b) guest charges own order → success, (c) authenticated user charges own order without email in body → success, (d) authenticated user charges another user's order → 403 (existing `user__isnull=False` check).
- The `request.data.get('email')` shape is now part of the contract for guest order endpoints. Document in `docs/api/PAYMENT_API.md`.

## Operational notes

**Why the check goes in the view, not the serializer.** The serializer validates the *request shape* (required fields, types). The email-match check is *authorization* — does this caller have the right to operate on this order? Authorization lives in the view, alongside the order lookup. Putting it in the serializer couples the serializer to the order model, which is wrong.

**Why `request.data.get('email')` and not a header.** The FE already sends `email` in the request body for the order-charge flow. Moving it to a header would require a FE change for no benefit. The body is the standard place for order-creation data. Headers are for cross-cutting concerns (auth tokens, idempotency keys, content-type).

**Why `not request.user.is_authenticated` and not `request.user.is_anonymous`.** DRF's `request.user` is a Django user object (or `AnonymousUser`). `is_authenticated` is a property that's `True` for real users, `False` for anonymous. `is_anonymous` is the inverse. Both work; `is_authenticated` is more common in the codebase.

**The `Email mismatch` message.** Deliberately generic. Don't include the order's email in the response (info leak: confirms the order exists, helps an attacker narrow down which `order_id` they have). Don't include the request's email (the attacker already knows what they sent). The minimum-viable message: "Email mismatch".

**The 403 status code.** 403 Forbidden is the right code — the request is well-formed, the caller is just not authorized. 401 Unauthorized would imply the caller needs to authenticate (they don't — guest flows are deliberately auth-less). 404 Not Found would imply the order doesn't exist (it does). 400 Bad Request would imply the request is malformed (it's not). 403 is correct.

**Failure mode: FE omits email entirely.** `request.data.get('email')` returns `None`. `None != order.email` is always true (assuming `order.email` is a non-empty string). The check fires, returns 403. This is the correct behavior — a guest who doesn't provide their email can't prove they own the order. The FE is expected to send email; this is a contract.

**Failure mode: FE sends wrong email.** User A creates a guest order with `user@acme.com`. Attacker B knows the `order_id`, sends `POST /payments/order-charge/` with `email: 'attacker@evil.com'`. Check: `'user@acme.com' != 'attacker@evil.com'` → 403. Attacker B can't initiate a charge. Correct.

**Failure mode: Authenticated user accesses another user's order.** The `user__isnull=False` filter at the order lookup already handles this — the user only sees their own orders. The email check is a no-op for authenticated users (the `not request.user.is_authenticated` guard). No double-validation.

**Failure mode: User A is logged in, initiates a charge on their own order.** `user__isnull=False` filter matches, order found, `request.user.is_authenticated` is True, email check skipped, charge proceeds. Correct — the user is authorized by their auth token, not by email.

**The `ExpirePendingChargeView` is the pattern donor.** It already does this check at `payments/views.py:374-377`. The fix for `ChargeOrderView` is to copy that block. The atom exists to make sure the next view that needs it (likely: `RefundCreateView` guest flow, or a future `ReChargeOrderView`) copies the pattern, not invents a new one.

**The 4-site threshold for extraction.** With `ChargeOrderView` and `ExpirePendingChargeView` both having the check, that's 2 sites. Add a 3rd (e.g. guest refund-initiate) and extract a helper: `def assert_guest_email_match(request, order): ...`. Until then, inline duplication of 4 lines is fine. Premature abstraction is worse than duplication.

**Test cases to add (per [[payment-deep-review]] M8 gap).**
- Guest A tries to charge Guest B's order → 403
- Guest A charges own order with correct email → 200
- Guest A charges own order with wrong email → 403
- Guest A charges own order without email in body → 403
- Authenticated user U charges own order without email in body → 200 (auth is the check)
- Authenticated user U tries to charge user V's order → 403 (existing `user__isnull=False` filter)

## Related
- [[payment-backend-charge-flow]] — view layout and order lookup patterns
- [[payment-integration]] — overall gateway charge architecture
- [[payment-legacy-deprecation-map]] — `PlaceOrderViewSet` (also guest-charge-related, also deprecation-candidate)
