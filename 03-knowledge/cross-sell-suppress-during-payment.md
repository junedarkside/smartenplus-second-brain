# Cross-Sell Suppress During Payment

## Summary
DO NOT mount cross-sell UI during payment form interaction (checkout sidebar during card entry, payment page). Cross-sell during payment = doubt = abandonment. Industry-wide OTA pattern (Klook, Booking.com, Viator all suppress).

## Context
Cross-sell surfaces in the customer booking flow include checkout sidebar, post-add-to-cart modal, and post-booking confirmation. Payment is a separate funnel where the user is committing money. Cross-sell on a payment screen competes with the payment form for attention and injects doubt at the worst possible moment.

## Problem
A PM looking at "where else can we cross-sell?" will see the checkout/payment page as the highest-intent surface — user has already entered card details, surely they're buying. This is the exact wrong intuition. Industry data (and Klook/Booking.com/Viator patterns) shows cross-sell during payment correlates with abandonment, not with extra attach rate. The user is one keystroke from "Cancel" — showing them another thing to buy makes that keystroke more likely.

This is a counterintuitive "do not" rule that will be re-requested. Every new cross-sell initiative will propose payment-surface coverage. Codifying the suppression makes the conversation faster.

## Details
Rules for payment surfaces:
- No cross-sell sidebar on `/checkout` (or any route with the card-entry form mounted)
- No cross-sell on `/payment` (after card submit, while polling)
- No cross-sell on `/payment-processing` / `/payment-success` redirect
- Cross-sell MAY re-mount on `/order-confirmation` (post-payment, low risk)

```js
// pages/_app.js or layout-level gate
const SUPPRESS_CROSS_SELL_ROUTES = [
  '/checkout',
  '/payment',
  '/payment-processing',
];
const shouldShowCrossSell = !SUPPRESS_CROSS_SELL_ROUTES.some(r =>
  router.pathname.startsWith(r)
);
```

The gate is at the layout level, not per-component — easier to audit, harder to forget.

## Decision
Suppress cross-sell UI on any route where the payment form is interactive or the payment is being processed. Industry alignment (Klook, Booking.com, Viator) is the strongest argument.

## Tradeoffs
- Pro: Avoids measurable abandonment
- Pro: Industry-standard, defensible to PMs pushing for it
- Pro: One layout-level gate, no per-component decisions
- Con: Misses the (small) attach-rate opportunity on payment surfaces. The opportunity is real but smaller than the abandonment cost.
- Con: Suppression must be re-evaluated if the payment form UX changes (e.g. one-click Apple Pay removes the "card entry" step — does Apple Pay on `/checkout` count as "payment form interactive"? Default: yes, suppress.)

## Consequences
This is a negative-pattern rule that must be enforced via code review, not just docs. Any PR adding a cross-sell mount on a payment route should be flagged. Add a comment in the layout-level gate explaining WHY (so the next dev doesn't "optimize" it away). The rule also extends to upsell modals, exit-intent popups, and any "are you sure you want to leave?" patterns on payment routes.

## Related
- [[cross-sell-placement-strategy]] — broader cross-sell placement decisions
