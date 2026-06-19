# Payment Cancel vs Expire Error Mapping

## Summary
Cancel/expire logic is 2× implemented 3×. `useCancelPayment` hook and `expirePendingCharge` helper are the canonical implementations. `handleCancelPendingPayment` in `PaymentComponent.js:146-160` re-implements the hook; two inline fetches in `PaymentComponent.js:362-367` and `:388-391` re-implement the helper. Use the existing helpers.

## Context
[[payment-deep-review]] identified the duplication in the "Duplication / reuse (FE)" section. The Batch 1 of the implement plan established the reuse contract:

- `useCancelPayment.js` — React hook for cancel-payment flows. Returns `{ cancelPayment, isCancelling, error }`. Handles loading state, error normalization, optimistic UI revert.
- `expirePendingCharge` in `getBillingAndOrder.js:201-231` — plain async function for expire-pending-charge flows. Takes `{ order_id, email }`. Posts to `/api/payments/expire-pending-charge/`. Returns `Promise<void>`.

Three callsites in `PaymentComponent.js` ignored the contract and re-implemented the logic inline. The duplication is not in a comment or a TODO — it's a working but divergent copy.

## Problem
Every new `PaymentComponent` feature re-rolls the cancel/expire logic. The inline implementations diverge over time:

- **Error handling differs.** The hook uses `handleApiError` (the project's standard). One inline fetch uses `try/catch` with `console.error`. Another uses `.then().catch()` with a toast. A third uses `.then().catch().finally()`. Four shapes, one semantic.
- **Loading state diverges.** The hook sets `isCancelling` (used for spinner + disabled state). Inline fetches set nothing — the user can click cancel twice, initiating two backend calls.
- **Optimistic UI updates differ.** The hook reverts `selectedPayment` to the default on cancel. Inline fetches don't — the user stays on the cancelled method until they manually change.
- **Error message translation.** The hook maps backend error codes to user-facing messages. Inline fetches show the raw error string. A `400 "Email mismatch"` shows as "Email mismatch" (acceptable) but a `500 "Internal Server Error"` also shows as "Internal Server Error" (not acceptable).

Net effect: cancel/expire bugs are fixed in the helper but re-emerge at the inline callsites. Re-discovery of the duplication at every audit.

## Details
Canonical implementations:

```js
// useCancelPayment.js — cancel a paid (or in-flight) payment
// Returns: { cancelPayment, isCancelling, error }
// Calls: POST /api/payments/cancel/  (or similar — see hook for current route)
// Handles: loading state, error normalization via handleApiError,
//          optimistic UI revert, user-facing error messages

// getBillingAndOrder.js:201-231 — expire a pending charge
// export async function expirePendingCharge({ order_id, email })
// Calls: POST /api/payments/expire-pending-charge/
//   with body: { order_id, email }
//   email is included for guest requests only (omitted for authenticated)
// Returns: Promise<void>
// Throws: handleApiError-normalized error
```

Re-implementations to remove:

```js
// PaymentComponent.js:146-160 — handleCancelPendingPayment
// ~15 lines: useState for isCancelling, inline fetch with manual error handling,
//   manual loading state reset, manual success/error dispatch
// Duplicates: useCancelPayment (which already does all of this)
// Fix: import useCancelPayment, replace body with `await cancelPayment()`

// PaymentComponent.js:362-367 — inline fetch in handleConfirmLeave
// ~6 lines: fetch with email-in-query-string for guest, no loading state, no error handling
// Duplicates: expirePendingCharge
// Fix: import expirePendingCharge, replace with `await expirePendingCharge({ order_id, email })`

// PaymentComponent.js:388-391 — inline fetch in handleCancelQRPayment
// ~4 lines: fetch with body, no loading state, no error handling, no return value
// Duplicates: expirePendingCharge
// Fix: same as above
```

## Decision
Replace all three re-implementations with the canonical helpers. The mechanical refactor:

1. Add `const { cancelPayment, isCancelling } = useCancelPayment()` near the top of `PaymentComponent`.
2. Replace `handleCancelPendingPayment` body with `await cancelPayment()`.
3. Add `import { expirePendingCharge } from 'helpers/getBillingAndOrder'` (or wherever it's exported from).
4. Replace the two inline fetches with `await expirePendingCharge({ order_id, email })`.
5. Wire `isCancelling` to the cancel button's `disabled` state.

Add an ESLint rule (or PR-checklist item) that flags any new `fetch()` call in `PaymentComponent.js` that posts to `/api/payments/cancel/` or `/api/payments/expire-pending-charge/`. Long-term: add unit tests to `useCancelPayment` and `expirePendingCharge` that the re-implementations lacked, making the helpers visibly more reliable.

## Tradeoffs
- **Helpers vs hooks.** `useCancelPayment` is a hook (React state), `expirePendingCharge` is a plain function. Different abstraction levels, but both are the single source of truth for their respective flows. Don't unify them — they have different ergonomics and different consumer patterns.
- **ESLint rule maintenance cost.** A custom rule for two endpoints is overhead. A simpler `// eslint-disable-next-line` + PR-review checklist is the right size for now. Add a custom rule only if the duplication reappears.
- **Tests first, fix second.** The helpers have no tests. Adding tests to `useCancelPayment` and `expirePendingCharge` before removing the re-implementations is the safe order. A regression in the helper caught by tests is cheaper than a regression in the inline callsite caught in production.
- **Don't bundle with the bug fix.** Removing the duplication is a refactor, not a bug fix. Ship separately, with a "no behavior change" test suite run before and after.
- **The `email` field.** The inline fetch in `handleConfirmLeave` puts `email` in the query string. The helper puts it in the body. Both are acceptable; body is the modern pattern. The refactor is a small behavior change (query → body) but no caller is affected.

## Consequences
- Cancel/expire bug fixes happen in one place
- New `PaymentComponent` features (e.g. recurring payment, saved methods) inherit correct cancel/expire behavior by default
- Loading state (`isCancelling`) becomes consistent across the flow. Cancel button can show a spinner.
- The pattern applies to any "FE has 2 helpers, multiple inline re-rolls" situation — add a `// Helpers — use these` comment to `getBillingAndOrder.js` and `useOmisePayment.js` exports
- The 3 callsites being identified by file:line is the proof that "extract a helper" is not enough — the helper must be the *only* way to do the operation, with a code review checklist enforcing it
- Test gap: no tests for `useCancelPayment` or `expirePendingCharge`. Add tests for: success path, error path, loading state transitions, guest vs authenticated email handling.
- Risk: the inline fetches have subtle behaviors (query-string email, no loading state) that the helpers don't. If those behaviors are load-bearing for some edge case, the refactor breaks it. Mitigation: read the surrounding code carefully, ask "is the loading state intentional or just missing?" before changing.

## Related
- [[payment-frontend-flow-mechanics]] — full FE flow including cancel/expire triggers
- [[payment-qr-polling-mechanics]] — QR-specific paths that use the same helpers
- [[payment-cancel-state-prevmethod-guard]] — the `cancelState.success` reset pattern in the same component
