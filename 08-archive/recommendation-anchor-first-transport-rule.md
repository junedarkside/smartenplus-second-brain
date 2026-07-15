# Recommendation Anchor — First Transport Rule

## Summary
"People Also Book" recommendations anchor on the **first** transport item in cart, not the last. Using last causes circular recommendations when user adds cross-sell transports.

## Decision

`CheckoutRelatedTrips.js:26-27`:
```js
const anchorItem = transportItems.length > 0
  ? transportItems[0]   // first transport — stable anchor
  : (cartItems || []).find(item => !SKIP_CATS.includes(item.contract?.service_category));
```

## Why First, Not Last

**Problem with last transport:**
- User has Bangkok→Koh Samui ferry (anchor)
- Recommendations: packages for Koh Samui arrival (hotels, taxis, activities) ✓
- User books Koh Samui→Koh Phangan ferry from recommendations
- Anchor shifts to new ferry → recommendations now show "trips similar to Koh Samui→Koh Phangan"
- **Circular** — recommendations about the connecting trip, not the destination

**First transport is the original intent:**
- User booked Bangkok→Koh Samui = their destination anchor
- Any cross-sell adds don't change the intent
- Recommendations stay relevant to destination throughout checkout

## Anchor Selection Logic

`CheckoutRelatedTrips.js:22-32`:
1. Filter cart for `TRANSPORTATION` or `TRANSFER` items
2. If transport exists → anchor = `transportItems[0]` (first)
3. No transport → anchor = first non-ticket activity
4. `recType` = `'packages'` if transport, `'activity'` if not

## Edge Case: No Transport, User Adds Activity

Anchor shifts from null → first activity added. This is acceptable — user has no transport, so their first activity defines context. No circular risk because adding more activities doesn't change which was first.

## Related
[[people-also-book-checkout-audit]] [[recommendation-type-selection-by-service-category]] [[cross-sell-placement-strategy]]
