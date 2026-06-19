# Payment Legacy Deprecation Map

## Summary
Two routes return 410 and are dead: `POST /api/payments/webhook-legacy/` and `POST /api/placeorder/`. New code MUST NOT call them. Verify zero nginx traffic in access logs before deploy.

## Context
Two legacy routes predate the modern finalize-on-webhook architecture. They bypass `finalize_payment` SSOT, write `order.status='paid'` directly, and skip `select_for_update`. The combination is the highest-value attack surface in the payment system. A forged webhook (`{"key":"charge.complete","data":{"id":"chrg_xxx"}}`) to `/api/payments/webhook-legacy/` with any real `cards.Charge.gateway_charge_id` flips an order to paid with no auth, re-increments coupons, re-confirms bookings.

The verification block at `orders/views.py:766-772` is commented out:
```python
# if not verify_omise_event(...):
#     return HttpResponse(status=400)
```
The view is `AllowAny`. The legacy webhook acts on `cards.Charge` rows, and `PlaceOrderViewSet` (M10 in [[payment-deep-review]], `apis/urls.py:37` → `carts/views.py:281-413`) is the only remaining writer of those rows. Killing the writer narrows the attack surface; killing the reader eliminates it.

## Problem
H2 in [[payment-deep-review]]. The deprecation must be coordinated — killing the webhook but not the writer (or vice versa) leaves one half of the attack surface intact. Without a deprecation map, the next payment audit re-discovers these routes and re-writes the same risk analysis from scratch.

The 410 pattern is already established in the codebase: the stripe-webhook route at `orders/urls.py:30` returns `HttpResponse("Deprecated", status=410)`. Use the same pattern for both legacy routes.

## Details
Routes to deprecate (return `HttpResponse("Deprecated", status=410)`):

| Route | Mount | View | File |
|---|---|---|---|
| `POST /api/payments/webhook-legacy/` | `orders/urls.py:28` | `PaymentWebhookViewSet` | `orders/views.py:759` |
| `POST /api/placeorder/` | `apis/urls.py:37` | `PlaceOrderViewSet` | `carts/views.py:281-413` |

Both routes share these failure modes:
- Skip `finalize_payment` (no `payment_finalized_at` written)
- Skip `select_for_update` (concurrent write risk; re-confirm booking can race with a refund)
- Write `order.status='paid'` directly (`views.py:913-914`)
- Re-increment coupon (`views.py:975-978`) without `select_for_update` on Coupon
- Re-confirm bookings (no idempotency guard)

The deprecation shape, matching stripe-webhook:
```python
# In orders/urls.py:28
path('payments/webhook-legacy/', lambda r: HttpResponse("Deprecated", status=410)),
# In apis/urls.py:37
path('placeorder/', lambda r: HttpResponse("Deprecated", status=410)),
```

Lambda is intentional — the views are deleted, not just bypassed. A lambda stub is one line and clearly disposable.

## Decision
Return 410 on both routes after verifying zero prod traffic in access logs over a full business week (7 days minimum, prefer 14 to catch month-end / month-start cycles). Pure removal after that window. No deprecation shim — these have no legitimate callers. The pattern is already established (stripe-webhook deprecation at `orders/urls.py:30`).

Verification checklist before deploy:
1. `grep -c 'webhook-legacy' /var/log/nginx/access.log.*` — zero hits in 7+ days
2. `grep -c 'placeorder' /var/log/nginx/access.log.*` — zero hits in 7+ days (filter out `/api/placeorder/orders/` etc — the exact match must be the legacy POST endpoint)
3. `grep -r 'webhook-legacy' smartenplus-frontend/src/` — zero references in FE code
4. `grep -r '/api/placeorder' smartenplus-frontend/src/` — zero references in FE code (confirm against deprecated POST, not other endpoints)
5. `git log --all -- '**/webhook-legacy*'` — no in-flight branches
6. Notify admin-dashboard team — they have a separate frontend that may have legacy integrations

## Tradeoffs
- **One-week traffic check** is a soft constraint. Any caller broken for >1 week is dead. If callers exist (admin-dashboard CRM integration, old mobile app, internal script), fix them with a deprecation warning, then re-check.
- **No deprecation shim** means callers fail loud (410 "Deprecated"). Alternative: 302 redirect to the modern endpoint, or 200 with empty body. Both mask the removal and let broken callers silently no-op.
- **Lambda stub vs leaving the view.** Lambda is two lines and clearly disposable; leaving the view in place invites a maintainer to "fix the auth" instead of removing it. Lambda is the safer signal.
- **Verification load.** Access log analysis is per-deploy, not continuous. The routes remain exploitable in the verification window. Mitigation: the routes require matching `cards.Charge.gateway_charge_id` rows. Killing the writer first (`PlaceOrderViewSet` 410) narrows the attack surface to historical rows. Killing the reader second eliminates it.
- **Coupled with M10 fix.** `PlaceOrderViewSet` is the writer for the legacy webhook's data. Deprecating the reader without deprecating the writer still creates new attack data. Both go in the same PR.

## Consequences
- Any remaining `cards.Charge` row creation must be blocked (M10 fix in the same PR)
- Future deprecations MUST follow the 410 + access-log-verification pattern, not silent removal
- `cards/` app becomes a soft-archive target. `RefundCreateView` at `cards/views.py:53-140` is still alive for admin-dashboard. Not in this deprecation scope — separate audit.
- Re-discovery cost: zero, on next audit. The atom is the map.
- Test gap: there's no test that asserts these routes return 410. Add one to prevent regression. (`payments/tests/test_legacy_routes.py`)

## Operational notes

**Why the lambda stub, not a redirect.** A redirect (302) to the modern endpoint would mask the removal. A caller that's been broken for a month would suddenly start working against a different endpoint, with different semantics (different request shape, different response shape, different auth). The lambda stub returns 410 — explicit "this is gone, fix your code". The cost of a clear error is lower than the cost of a silent semantic shift.

**Why 410 Gone, not 404 Not Found.** 404 is the standard "I don't know what you're asking for". 410 is the specific "I used to handle this, I no longer do". The distinction matters for monitoring: 404s are normal, 410s are a signal that something is still trying to use the deprecated endpoint. A spike in 410s after deploy is an actionable alert.

**The 7-day traffic check window.** Why a full week: business cycles. A weekend integration might not fire during the work week. A month-end billing integration might not fire during the first 3 weeks. 7 days is the minimum to catch most cycles; 14 is safer. If the access logs show zero hits in 14 days, the routes are dead. Anything that has been broken for 14 days is dead code on the caller side.

**Coupling to M10 (PlaceOrderViewSet).** The legacy webhook (`/api/payments/webhook-legacy/`) acts on `cards.Charge` rows. Those rows are created by `PlaceOrderViewSet` (`/api/placeorder/`). If you 410 the webhook but leave `PlaceOrderViewSet` alive, the writer keeps creating rows that the dead reader never processes. The rows accumulate. Deprecate both in the same PR. The original audit lists this as M10.

**The verification command pattern.**
```bash
# In a pre-deploy hook or manual run:
zgrep -h 'POST /api/payments/webhook-legacy/' /var/log/nginx/access.log*.gz | wc -l
zgrep -h 'POST /api/placeorder/' /var/log/nginx/access.log*.gz | wc -l
# Both should return 0 over a 7-14 day window.
```

**Admin-dashboard may have legacy integrations.** The admin-dashboard repo has its own frontend that talks to the backend. It may have a legacy `/placeorder/` integration for historical order views or refund flows. Notify the admin-dashboard team before deploying the 410. They may need a parallel deprecation in their repo.

**Webhook signature verification — the missing line.** `orders/views.py:766-772` is the commented-out `if not verify_omise_event(...)` block. The deprecation removes the route entirely, so the verification never needs to be written. But: if any future webhook route is added, the verification MUST be uncommented (or copied from a working pattern). The pattern: verify signature, return 400 on failure, return 200 on success. See [[omise-api-reference]] for the signature construction.

**Cleanup after deprecation.** Once both routes return 410 and 7+ days pass:
1. Remove the route from `urls.py` entirely (not just the lambda stub)
2. Remove the view class (`PaymentWebhookViewSet`, `PlaceOrderViewSet`)
3. Remove the URL imports
4. Remove any tests that exercise these routes (replace with 410-assertion tests)
5. Remove any imports of these views in other modules (search: `grep -r "PaymentWebhookViewSet\|PlaceOrderViewSet" smartenplus-backend/`)
6. Update `docs/technical/PAYMENT_SYSTEM.md` to remove legacy references

The two-stage process (410 stub → removal) lets you detect callers in the wild. Going straight to removal hides any remaining integrations.

## Related
- [[payment-integration]] — overall gateway architecture
- [[payment-backend-charge-flow]] — modern finalize path that these bypass
- [[omise-api-reference]] — webhook signature verification pattern that should have been here
