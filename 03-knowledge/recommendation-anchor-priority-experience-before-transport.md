---
name: recommendation-anchor-priority-experience-before-transport
description: Anchor priority inversion — TRANSPORTATION=100 > DAY_TOUR=80 is wrong. Experience-first marketplace means activities should have higher anchor priority. Reference to stale [[recommendation-anchor-first-transport-rule]] to retire.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: recommendation-engine-completion-roadmap
---

# Recommendation Anchor Priority — Experience Before Transport

## Summary
Anchor priority inversion: TRANSPORTATION=100 > DAY_TOUR=80 is WRONG. Experience-first marketplace means activities higher priority. Retire stale `[[recommendation-anchor-first-transport-rule]]`.

## Why It Matters
Customer books trip → gets transport recommendations (priority 100) instead of activity cross-sells (priority 80). Misaligned with business strategy (experiences revenue growth).

## Detail
**Current code:**
```python
ANCHOR_PRIORITIES = {
    'TRANSPORTATION': 100,
    'DAY_TOUR': 80,
    'ATTRACTION_TICKET': 70,
    # ...
}
```

**Fix:**
```python
ANCHOR_PRIORITIES = {
    'DAY_TOUR': 100,           # Experience-first
    'ATTRACTION_TICKET': 95,
    'ACTIVITY': 90,
    'TRANSPORTATION': 70,     # Complementary
    'TRANSFER': 60,
}
```

**Rationale:** Marketplace strategy 2026 = experiences growth. Transport supports the trip but isn't primary revenue driver.

## Constraints / Gotchas
Update `people-also-book` algorithm to respect new priorities. Sort by: `anchor_priority * relevance_score`, not anchor alone.

## Related
- [[recommendation-flat-score-finder-pollution]] — companion score issue
- [[recommendation-engine-completion-roadmap]] — parent (strategy update)
