# Multi-Item Cart Anchor: Last Transport

## Summary
For cross-sell recommendations on multi-item carts, anchor = last transport cart item (final destination). Fall back to first non-skip activity item. Rec type logic: `packages` if transport present, `activity` otherwise. Skip EVENT_TICKET/ATTRACTION_TICKET-only carts.

## Context
Cross-sell surfaces (checkout sidebar, post-booking, post-add-to-cart) all need to compute "what to recommend given the user's current cart." A cart can hold a mix of transport + activity + ticket items, and the right anchor determines whether recommendations are coherent (transport in Phuket → day tours in Phuket) or random.

## Problem
Naive cross-sell uses `cart[0]` or the most-recently-added item as anchor. For a user who added a hotel transfer first, then a day tour, then an attraction ticket, this anchors on the hotel (low-signal) and misses the day tour (high-signal). Worse, for EVENT_TICKET-only carts (a concert ticket), the anchor returns the event venue — recommendations become irrelevant ("you bought a concert ticket, want a day tour?").

## Details
Decision tree:

```js
function getCrossSellAnchor(cart) {
  // Skip ticket-only carts entirely
  const bookableItems = cart.filter(i =>
    i.service_category !== 'EVENT_TICKET' &&
    i.service_category !== 'ATTRACTION_TICKET'
  );
  if (bookableItems.length === 0) return null;

  // Prefer last transport item (final destination)
  const transports = bookableItems.filter(i =>
    i.service_category === 'PRIVATE_TRANSFER' ||
    i.service_category === 'SHARED_TRANSFER'
  );
  if (transports.length) return transports[transports.length - 1];

  // Fall back to first non-skip activity item
  return bookableItems[0];
}

function getRecType(cart) {
  const hasTransport = cart.some(i =>
    i.service_category === 'PRIVATE_TRANSFER' ||
    i.service_category === 'SHARED_TRANSFER'
  );
  return hasTransport ? 'packages' : 'activity';
}
```

The `last transport` rule is "final destination" because the cart is ordered by add-time and transport additions typically come last (after the user has planned their day activities). The first non-skip fallback handles day-tour-only carts.

## Decision
- Anchor = last transport item, else first non-skip activity item
- Rec type = `packages` if transport present, else `activity`
- Skip event/attraction-ticket-only carts (return null, no recs)
- Codify as `getCrossSellAnchor(cart)` + `getRecType(cart)` in a shared helper

## Tradeoffs
- Pro: Codifies BD signal intent — transport = bundle anchor, activity = standalone anchor
- Pro: Skipping ticket-only carts avoids forcing irrelevant cross-sells
- Pro: Pure function, easy to unit test across cart shapes
- Con: "Last transport" assumes cart add-order is meaningful. If a user adds a return transfer first then an outbound, the anchor becomes the return transfer (different city). Edge case, not catastrophic.
- Con: New service categories added later (e.g. `RENTAL`) need explicit handling or they'll fall through to the activity branch

## Consequences
Every cross-sell surface in the codebase MUST use this helper, not its own anchor logic. Centralizing in one helper means: (1) one place to update when service categories change, (2) one place to test, (3) consistent rec quality across surfaces. Future devs adding a new cross-sell entry point should import `getCrossSellAnchor` and `getRecType` from the helper, never inline the logic.

## Related
- [[cross-sell-placement-strategy]] — the broader placement strategy this anchor logic serves
