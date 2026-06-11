# Checkout Step Flow

## Summary
Checkout step count and step meanings change dynamically based on `hasMixedPassengerCounts`. Payment initialization uses cart-snapshot idempotency key. CONTRACT_INACTIVE auto-redirects to /checkout after 3 seconds.

## Context
`hooks/checkout/useStepValidation.js`, `hooks/usePaymentInitialization.js`, `pages/checkout/index.js`. Step logic is non-trivial — normal and mixed passenger flows have different step counts AND different meaning for step 2/3.

## Step Flow by Passenger Type

### Normal Flow (uniform passenger counts across all cart items)
```
Step 0: Cart review
Step 1: Passenger details
Step 2: Confirmation
Step 3: Payment
```

### Mixed Flow (different passenger type counts across items)
```
Step 0: Cart review
Step 1: Passenger details
Step 2: Passenger assignment (WHO rides which trip)
Step 3: Confirmation
Step 4: Payment
```

**Step 2 and 3 swap meaning** between flows. Hardcoded step references in code must account for this.

### `hasMixedPassengerCounts` Calculation (pages/checkout/index.js:174-177)
```js
// NOT: all items have same total passenger count
// ACTUALLY: max variation across adult/children/infant types
const hasMixed = calculatePassengerTypeBreakdown(cartItems)
  .some(type => type.max !== type.min)
```
Pool is: max(adult) + max(children) + max(infant) across all items, not sum. Edge case: 2 items both with 2 adults is NOT mixed even if different routes.

### Step Number Mapping (useCheckoutRouter.js:35-40)
```js
// logicalStep → actualStep
// Mixed flow: step >= 2 gets +1 to account for assignment step
const actualStep = hasMixedPassengerCounts && logicalStep >= 2
  ? logicalStep + 1
  : logicalStep
```
External step references (URLs, constants) use logical step numbers. UI rendering uses actual step numbers. Mixing them = off-by-one.

## Payment Initialization Patterns (usePaymentInitialization.js)

### Cart-Snapshot Idempotency Key (lines 38-44, 162-174)
```js
// Key = cartId:grandTotal hash
const idempotencyKey = generateIdempotencyKey(cartId, grandTotal)

// Reset key when cart total changes
useEffect(() => {
  if (prevTotal !== grandTotal) resetIdempotencyKey()
}, [grandTotal])
```
Prevents: user applies coupon (total changes) → same key → backend returns old order at old price.

Different from payment-layer idempotency (which hashes method+amount+currency). This is checkout-layer, scoped to cart state.

### CONTRACT_INACTIVE Auto-Redirect (lines 139-143)
```js
if (error?.data?.error === 'CONTRACT_INACTIVE') {
  setTimeout(() => router.push('/checkout'), 3000)
  setError({ type: 'CONTRACT_INACTIVE', message: '...' })
}
```
Product became inactive between cart add and payment. 3-second delay shows error message before redirect. No user action required — auto-navigates to restart checkout.

### Mixed Passenger Step Hardcode (lines 179-180)
```js
// Payment is always the last step
const paymentStep = hasMixedPassengerCounts ? 4 : 3
```
If a new step is added to either flow, this constant must be updated. No dynamic calculation.

## Stale Passenger Assignment Clearing (pages/checkout/index.js:190-204)
When `hasMixedPassengerCounts` becomes `false` (user edits cart to uniform counts):
```js
// Must clear BOTH locations:
dispatch(clearPassengerAssignments())  // Redux
setFormData(prev => ({ ...prev, assignments: {} }))  // local state
```
Prevents stale assignment data from leaking into normal flow confirmation step.

## Related
- [[checkout-state-persistence]] — useCartSync effect ordering, assignment sync
- [[checkout-hoc-architecture]] — HOC that validates cart before steps mount
- [[payment-frontend-flow-mechanics]] — payment step mechanics after step flow completes
- [[checkout-next-btn-disable-conditions]] — per-step disable conditions
