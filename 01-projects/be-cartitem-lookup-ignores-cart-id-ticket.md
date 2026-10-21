# BE ticket — `CartItemViewSet` ignores the cart id in the URL for logged-in users

## Summary
`carts/views.py:99-117` `CartItemViewSet.get_queryset` picks the item by **user id alone** when the request body has `user` (and by `?email=` alone in the email branch). The `<cart id>` in `/carts/<carts_pk>/cartitems/<id>/` is used only in the guest branch (`cart_id=carts_pk, user__email=None`).

`create` (`:209`), `partial_update` (`:234`) and `destroy` (`:259`) call `_check_payment_pending(cart_id)` with the cart id **from the URL**, not the item's own `cart_id`. So the "payment in progress, cancel payment to edit cart" 409 (`:193-207`) checks whichever cart the client put in the URL.

## Impact (low, not proven)
- Not a privilege hole: the ownership gate (`request_owns_user_id` / `request_owns_email`) still limits an authenticated user to their own items.
- Gap: if the URL cart id and the item's real cart differ, an edit can pass the payment-pending guard of the URL cart while the item's real cart has an order in `payment_pending`. Payment guard bypass for the user's own cart, not other users' data.
- Today's frontend does not hit it: checkout passes `cartId` from Redux (`state.cart.cartId`), which only goes from null to an id there; `resetCart` runs on order pages only. Found by the payment-security review of FE R2-2 (FE `2dc8ea92`, which makes `InlinePassengerSelector` send the current `cartId`).
- **Not reproduced.** No test written, no prod data checked.

## Required
1. Write a failing test first: logged-in owner, item in cart A (order `payment_pending`), PATCH via `/carts/<B>/cartitems/<id>/` -> expect 404 (or 409), not 200.
2. In `get_queryset`, also filter `cart_id=carts_pk` in the `user` and `email` branches (owner check stays). Or make `_check_payment_pending` use the item's own `cart_id`. Pick one; the first is smaller.
3. Check every caller sends the right cart id before tightening: FE `store/api/api-slice.js` (`useUpdateCartItemMutation`, add, delete), the login "merge cart" flow (items move from a guest cart to the user's cart), admin-dashboard (no use known). A login merge that leaves a stale cart id in the URL would start returning 404 after the fix.
4. `payment-security-specialist` review (payment-adjacent endpoint). Model floor sonnet.
5. BE only change if callers are clean; deploy with a BE batch, FE first/after per whether any caller needs a change.

## Status
OPEN 2026-10-21. No code changed. Owner: user to decide priority. Related: [[be-bookingdetails-write-methods-ticket]], [[be-bookingpdf-permission-ticket]].
