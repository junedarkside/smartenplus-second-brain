# Checkout HOC Architecture

## Summary
3 key HOCs wrap checkout and cart pages. `withCartValidation` is the critical one — creates/validates cart on mount with ref-based deduplication. `withComponent` has an infinite refetch risk. `withCheckCartValidation` prevents "null" cart queries.

## Context
`components/HOC/`. HOCs inject infrastructure concerns (cart creation, feature gating, cart validation) so page components stay clean. Chain matters — wrong order = double cart creation or feature check fires before cart exists.

## HOC Reference

### withCartValidation (`check-and-createcart.js:12-131`)
**Used by:** trip detail, search results, homepage BookButton pages (not checkout itself)
**Injects:** cart creation + validation on mount

```js
// createCartCallback stored in ref — prevents recreation on re-render
const createCartRef = useRef(createCartFn)

// Dual-condition guard prevents duplicate creation:
if (operationInProgress.current || isValidCartId(cartId)) return

// Only 404 clears cartId — 500s/network errors keep it
if (error?.status === 404) dispatch(setCartId(null))
// else: transient failure, cart still valid
```
**Critical:** pages with `BookButton` NOT wrapped in `withCartValidation` must call `createCart()` manually after `resetCart()`. See [[cart-reprovision-after-reset]].

### withCheckCartValidation (`check-cart.js:38-73`)
**Used by:** checkout entry point
**Does:** validates cart exists before showing checkout; skips query if `cartId === 'null'` (string)

```js
// Prevent /carts/null/ request:
const { data } = useCheckCartIdQuery(
  { cartId },
  { skip: !cartId || cartId === 'null' }
)
```
If cart invalid (404): redirects to trip page with error param. If valid: renders children.

### withComponent (`withComponent.js:51-88`)
**Used by:** feature-gated UI elements
**Does:** fetches `/frontend-profile/smartenplus-default/` to show/hide component

```js
// RISK: frontendProfile set in effect callback, used as dependency
useEffect(() => {
  fetchFrontendProfile().then(data => setFrontendProfile(data))
}, [frontendProfile])  // ← triggers re-fetch whenever frontendProfile changes
```
**Bug risk:** if `fetchFrontendProfile()` returns a new object reference each call, this effect never stabilizes. Observed to be benign in practice (profile rarely changes) but avoid adding more dependencies to this effect.

## HOC Composition Order
Pages that need both cart + feature gating:
```js
// Correct order:
export default withCartValidation(withComponent(MyPage, 'feature-flag'))
// Cart created first, then feature check runs with valid cart context
```

## isValidCartId Helper
```js
// shared guard used by all HOCs:
const isValidCartId = (id) =>
  id && id !== 'null' && typeof id === 'string'
```
See [[rtk-query-advanced-patterns]] for why `'null'` string check is needed.

## Related
- [[cart-reprovision-after-reset]] — manual cart creation for non-HOC pages
- [[rtk-query-advanced-patterns]] — cartId 'null' string guard
- [[checkout-state-persistence]] — what checkout persists after HOC validates cart
- [[redux-store-architecture]] — cart-slice setCartId
