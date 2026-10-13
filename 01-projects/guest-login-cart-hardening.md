# Guest login/logout x cart hardening

## Summary
SWE+BD review of guest login/logout with and without cart items found 3 security holes and several silent cart-loss paths. All fixed on BE+FE `develop` 2026-10-13. NOT deployed. Passenger picker redesigned (search count only, never writes the cart), see below.

## Context
Guest cart = `Cart` row + `CartItem(user=None)`. Login merges it into user cart (`PUT /logincart/<id>/`, run server-side in NextAuth `authorize()` / social `signIn`). Logout deletes the cart row. Failures were silent, so customers saw an empty cart and lost sales.

## What shipped (all merged to `develop`)
| Area | Fix | Commit |
|---|---|---|
| BE security H1-H3 | `/logincart/` uses `request.user`; `CartItemViewSet` owner check | BE `a2c0552` |
| BE merge M1/M2/M6 | key = contract+date+time slot, add-ons carried, `merge_service.py` | BE `2e38896` |
| BE O1/M3 | `Cart.destroy` and merge return 409 `payment_pending` | BE `66b828e` |
| BE hardening | user-row lock (`no_key`), JOIN rate-card carry, `or 0`, guard inside merge | BE `b2728f7` |
| BE-C chooser | `CartMergeConflict` table, opt-in `detect_conflicts`, `/cart-conflicts/` | BE `901880a` |
| BE `?email=` leak | owner check on `CartViewSet.retrieve`, flag `CART_EMAIL_READ_ENFORCE` default OFF | BE `937dc94` |
| FE-A | socials best-effort, per-request `cartId` closure (no module state), `updateCart` retry+timeout | FE `39b7faea` |
| FE-B | conflict modal "Saved vs New" mounted in `_app.js` | FE `732f16d6` |
| FE Bearer | `checkCartId` sends Bearer when email present, 401 retries without header+email | FE `ffb9a6c0` |
| FE picker | search count only, `touched` seed guard, checkout card resync | FE `8cfbd3b8`, `62b35992` (supersedes `81aabbf0`) |

## Passenger picker (final design, session #488)
- First fix `81aabbf0` made the global search picker PATCH every TRANSPORTATION cart item. That was wrong: counts belong to each item, so the dialog changed existing items and a new trip add looked like it changed the old ones.
- Final: `Passenger.js` only dispatches Redux (search count). It never touches the cart (`c9b2d8d5`, 6 tests). Counts per item are edited at checkout (`InlinePassengerSelector`).
- Reseeders (`check-and-createcart.js`, `CartButton.js`) use `seedPassenger`, applied only while the picker is untouched. First version tested "untouched" as count == 1/0/0, so picking exactly 1 adult then refreshing let the cart (3/1/1) overwrite it and `?people=5` came back. Fix: persisted `touched` flag set by inc/dec (`91c2327e`, 5 tests). Verified live: pick 1, reload, stays 1.
- Checkout card resync after "Use new": `hooks/useServerSyncedPassengers.js` (`cd3a7380`, 7 tests), card follows server counts, keeps an in-flight click.
- Merged to `develop` 2026-10-13: `8cfbd3b8` (picker) then `62b35992` (resync). Not deployed.
- Live test (book 3/1/1 trip with 3 existing 1/1/1 items): only the new item got 3/1/1, existing untouched. Not reproduced: "add new changes existing".
- Behaviour: `touched` is permanent per browser until logout/store reset; a later cart never reseeds the picker. Forced `signOut` in `authUtils.js:38` does not reset the store.
- Lessons: 1/0/0 is both the default and a legal choice, never use a default value as "untouched"; test persistence by reloading; check which branch the dev server runs before reporting a bug.
- Known/accepted: shared link `?people=5` with Redux at 1 searches 5 but shows 1; `data.cart_item[0]` order unstable for seeding; `InlinePassengerSelector` debounced fn frozen at first render (null `cartId` at mount drops edits); `BookButton.js:140-141` mutates `contract`; `CartItemViewSet.get_queryset` filters by body `user`; `tripdetail.js:70` reads `state.passenger.childern` (typo).

## Decisions
- Add-to-cart duplicate trip+date keeps the "already in your cart" toast (user chose keep as is). Counts are edited on checkout or the picker.
- `?email=` read kept with owner check, not switched to `request.user`: merge flow needs guest-by-UUID reads while logged in.
- Conflict chooser is opt-in so old FE behaves as before when BE deploys first.

## Deploy order (one time)
1. FE. Clear `smartenplus_next_cache` Docker volume.
2. BE with flag off. Migration `carts.0018` must apply on prod. Watch logs for the warning.
3. Set `CART_EMAIL_READ_ENFORCE=True`, restart BE.
BE first breaks logged-in cart reads on old FE (403 to empty cart).

## Test status
- Email login: merge, conflict modal verified. Google: guest item to account PASS (user-run).
- NOT run live: "Use new"/"Keep saved" at checkout, Test B (conflict modal after Google login, needs LOGGED-OUT guest cart), Test C (empty guest cart), Facebook/LINE real login, failure toast in browser.
- Baselines: BE `carts orders payments` 501 tests, 44 `carts` errors pre-existing. FE 39 jest suites fail on clean `develop`.

## Open items
- `CartViewSet.destroy` has no owner check (UUID is the capability, payment-guarded). Accepted.
- `.env-sample` lacks `CART_EMAIL_READ_ENFORCE`; `docs/api/PUBLIC_ENDPOINTS.md` unchecked.
- Merge key (with slot) vs `AddCartSerializer` (contract+date only) mismatch, owner question.
- `fixedCacheKey` comment at `api-slice.js:171-173` misleading.
- Tooling gotcha: `next build` overwrites `.next` and blanks a running dev server; restart it.

## Related
[[shared-transfer-seat-cap-fix]] [[django-400-vs-409-duplicate-cart-item]] [[rtk-cart-tag-invalidation-auto-refetch]] [[cart]] [[checkout-flow]]
