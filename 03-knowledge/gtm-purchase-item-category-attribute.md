# GTM Purchase Item Category Attribute

> **STATUS: SHIPPED (verified 2026-06-13 live read).** `hooks/useOmisePayment.js:59` builds `item_category: contract.service_category` in `tripItems`; `hooks/useOmisePayment.js:144` pushes it in the `purchase` event (`ecommerce.items: tripItems`). The pattern guidance below stands as precedent for future events (`add_to_cart`, `refund`, `view_item`).

## Summary
GTM `purchase` event `tripItems[]` map must include `item_category: contract.service_category` — without it, GA4 cannot break revenue by product type (DAY_TOUR vs transport), making any cross-sell experiment unmeasurable.

## Context
GTM ecommerce data layer in `pages/_app.js` (or equivalent tracking helper) is the single source of truth for GA4 purchase events. The `tripItems[]` array is the line-item payload that drives GA4's item-scoped dimensions. `service_category` lives on the `Contract` model in Django and is set per-operational-template (e.g. `DAY_TOUR`, `PRIVATE_TRANSFER`, `SHARED_TRANSFER`).

## Problem
GA4 reports for purchase events currently show revenue as a single number with no segmentation by product type. Every cross-sell experiment (A/B test of cross-sell placement, rec type, surface) needs to be measurable by revenue lift per category. Without `item_category` in the data layer, you cannot answer "did transport cross-sell lift DAY_TOUR revenue?" — you only see total revenue, which is contaminated by seasonality and other surfaces.

This blocks the entire BD measurement story. Every experiment team would have to file a tag/data-layer request before shipping.

## Details
Add one line to the GTM dataLayer push inside the purchase event:

```js
window.dataLayer.push({
  event: 'purchase',
  transaction_id: order.id,
  value: order.total,
  currency: order.currency,
  tripItems: order.items.map(item => ({
    item_id: item.contract_id,
    item_name: item.contract_name,
    item_category: item.service_category,   // ← this line
    price: item.price,
    quantity: item.quantity,
  })),
});
```

`service_category` is already fetched in the order response — no backend change needed. The frontend just needs to map it through to GTM.

## Decision
Add `item_category: contract.service_category` to the `tripItems[]` map at the point of purchase event push. Reuse the same mapping for any GTM ecommerce event that needs category attribution (`add_to_cart`, `view_item`, `begin_checkout`).

## Tradeoffs
- Pro: 1-line frontend change, no schema work
- Pro: Unlocks all future cross-sell + product-type measurement in GA4
- Pro: Pattern is reusable for any category-attribution use case
- Con: Depends on `service_category` being non-null in the order response — verify the contract serializer always populates it (it does for current contract types, but a future contract type without category would silently break attribution)
- Con: GA4 data-layer changes are hard to QA in dev — must verify via GA4 DebugView before merge

## Consequences
Every future GTM ecommerce event push in this codebase MUST include `item_category` for line items. If you add a new event type (`refund`, `add_to_cart`), mirror this pattern. Future devs touching `pages/_app.js` or any analytics helper should grep for `tripItems` to find the precedent.

This also means the analytics team can now ask category-level revenue questions directly, which is a forcing function for the data team to keep `service_category` clean on the backend.

## Related
- [[gtm-impression-dedup-sessionstorage]] — sibling GTM dedup pattern for impression events
- [[cross-sell-placement-strategy]] — the cross-sell measurement story that depends on this
