---
name: recommendation-mincartprice-floor-suppresses-complementary
description: `minCartPrice` floor bug suppresses cheap complementary add-ons. Cart minimum threshold prevents recommending low-cost extras (SIM cards, snacks). Lost revenue from impulse buys.
metadata:
  type: knowledge
  status: shipped
  date: 2026-06-22
  parent: recommendation-engine-completion-roadmap
---

# Recommendation minCartPrice Floor — Suppresses Complementary

## Summary
`minCartPrice` floor bug suppresses cheap complementary add-ons. Cart minimum threshold prevents recommending low-cost extras (SIM cards, snacks). Lost impulse-buy revenue.

## Why It Matters
Customer completes transport booking → no add-on suggestions because cart value below `minCartPrice` threshold. Missed revenue on cheap but high-margin items.

## Detail
**Bug code:**
```python
def get_cross_sell_recommendations(order):
    if order.total < minCartPrice:  # e.g., 1000 THB
        return []  # NO RECOMMENDATIONS
    # ... return add-ons
```

**Problem:** Order value 800 THB (transport only) → no SIM card (50 THB) recommended, even though highly relevant and high-margin.

**Fix:** Remove floor for complementary items:
```python
def get_cross_sell_recommendations(order):
    # Don't filter by cart total
    # Instead, sort by: relevance (high) × margin (high) × price (low)
    recs = AddOn.objects.filter(
        active=True,
        category__in=['SIM_CARD', 'SNACK', 'INSURANCE']
    ).order_by(
        F('margin') * F('relevance_score') / F('price')
    )[:5]
    return recs
```

**OR** keep floor for high-ticket items only (tours, activities), exempt cheap add-ons.

## Constraints / Gotchas
Don't over-recommend cheap items → limit to top 5. Use relevance score (past purchase, destination) to avoid noise.

## Related
- [[recommendation-engine-completion-roadmap]] — parent (P0 revenue gap)

## Resolution
Shipped 2026-06-18 (#133, FE `5777f84a`). Floor removed entirely — `CheckoutRelatedTrips.js` now comments "NO price floor". Verified by 3-agent audit 2026-07-15.
