# Payment Cancel State Prevmethod Guard

## Summary
`cancelState.success` in `PaymentComponent.js` must reset only when `selectedPayment` *actually* changes. Guard with `prevMethodRef` to prevent one-frame flash of "Payment Cancelled" alert on re-renders. The pattern is reusable for any "transient success state" UI.

## Context
`PaymentComponent.js` tracks a `cancelState` object: `{ success: bool, message: string }`. When the user changes payment method (QR → Card, Card → TrueMoney, etc.), the prior method's transient cancel state should reset. The original `useEffect` keyed on `[selectedPayment]` and unconditionally set `cancelState = { success: false, message: '' }` on every effect run.

React's `useEffect` dep comparison is `Object.is`, not deep-equal. For string values (payment method keys are always strings: `'promptpay'`, `'truemoney'`, `'credit_card'`), `Object.is` is correct in the simple case. The bug is different: a parent re-render can re-reference the same string and the effect re-runs. Even when the value is identical, the effect fires.

Wait — `Object.is('promptpay', 'promptpay')` is true, and React would not re-run the effect on identical deps. So why does the effect fire?

The actual bug: `selectedPayment` is a Redux selector or a derived value, and on a parent re-render the value is re-derived. If the derivation produces a new object (e.g. `{ key: 'promptpay', label: 'PromptPay' }`) and the effect reads `selectedPayment.key`, then `Object.is` compares the wrapper object, sees it as different, re-runs the effect. The `cancelState` reset happens even though the user-visible payment method didn't change.

Falsification: maybe the reset is intentional on every render? — No, the alert would flash on every keystroke in unrelated inputs. The user-visible bug is the flash on cancel → navigate.

## Problem
M3 in [[payment-deep-review]]. Effect at `PaymentComponent.js:523-527` clears `cancelState.success` instantly. On any re-render that touches `selectedPayment` (e.g. a parent state update that re-references the same string, or a selector that re-derives an object), the effect re-runs, the cancel alert disappears for one frame, then a re-render restores it. User sees a flash of "Payment Cancelled" alert after the order page has already navigated away. Looks like a glitch; erodes trust in the cancel affordance.

The flash is intermittent — only when the right re-render sequence happens. Hard to reproduce in isolation, easy to reproduce in production where many state updates happen per second.

## Details
Fix pattern: compare `selectedPayment` to a ref-tracked previous value.

```jsx
const prevMethodRef = useRef(selectedPayment);

useEffect(() => {
  if (selectedPayment !== prevMethodRef.current) {
    setCancelState({ success: false, message: '' });
    prevMethodRef.current = selectedPayment;
  }
}, [selectedPayment]);
```

The ref comparison is the gate. Same value → no-op. Different value → reset + update ref.

This works whether `selectedPayment` is a primitive string (ref compares string-to-string) or an object (ref compares object-to-object by reference, which is what `Object.is` does anyway). The win is that the reset is gated on a *user-intent* change, not on a render-cycle change.

An alternative — `useMemo` for `cancelState` — would re-derive on every render and not solve the "user actually changed method" semantic. `useEffect` with ref guard is the right shape: it runs on prop change, but only acts on *real* change.

## Decision
Use a `useRef` mirror of the prop, compare inside the effect. The pattern is generic enough to extract to a `usePrevious(value)` hook if it appears 3+ times. With 1 known use, inline the ref.

```jsx
function usePrevious(value) {
  const ref = useRef(value);
  useEffect(() => { ref.current = value; }, [value]);
  return ref.current;
}
```

Then:
```jsx
const prevMethod = usePrevious(selectedPayment);
useEffect(() => {
  if (selectedPayment !== prevMethod) {
    setCancelState({ success: false, message: '' });
  }
}, [selectedPayment, prevMethod]);
```

The hook form is cleaner. Use it from the start.

## Tradeoffs
- **Ref is not a state.** Doesn't trigger re-render. Good — the goal is to *suppress* a re-render, not cause one.
- **One ref per "prev" dependency.** Multiple dependencies that need this guard (e.g. `selectedPayment` + `paymentType` + `currency`) each need their own ref. If the list grows past 3, extract `usePrevious`.
- **Not the same as `useEffect` with deep-equal dep.** React's `useEffect` dep comparison is `Object.is`. For string values (payment method keys are always strings), `Object.is` is correct — no need for deep-equal. The ref guard solves a different problem: "user changed method" vs "render happened".
- **Custom hook has a subtle bug** — `usePrevious` updates the ref in a `useEffect`, which runs *after* render. So the first render, `prevMethod` is the initial value (also the current value). The comparison `selectedPayment !== prevMethod` is false on first render. Correct. On second render with a change, `prevMethod` is the value from the first render, `selectedPayment` is the new value, comparison is true. Correct.
- **The hook's `useEffect` updates the ref unconditionally.** That's intentional — we want the ref to always reflect the latest value, even if the consumer skips the comparison.

## Consequences
- The flash bug is gone
- The pattern applies to any "transient success state" UI: success toasts, error toasts, copy-confirmed states, save-confirmed states, form-submit-confirmed states. Reuse this ref-guard pattern elsewhere.
- Risk on refactor: a maintainer sees `useEffect([selectedPayment])` and "simplifies" by removing the ref. Without the ref, the bug returns. The atom is the only safeguard.
- `usePrevious` is now a de-facto shared hook. If a second use appears, move it to `hooks/usePrevious.js` and import. If 3+ uses, add unit tests.
- Single-use component pattern — re-usable in any transient-state component
- The flash bug is intermittent and may not reproduce in dev. Hard to write a regression test for. Add a comment in the source linking to this atom.

## Related
- [[payment-frontend-flow-mechanics]] — full FE payment flow and where `cancelState` is consumed
- [[payment-qr-polling-mechanics]] — QR-specific cancel flows that have the same shape
- [[payment-cancel-vs-expire-error-mapping]] — the cancel API call itself
