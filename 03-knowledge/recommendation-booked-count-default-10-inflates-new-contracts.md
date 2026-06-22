---
name: recommendation-booked-count-default-10-inflates-new-contracts
description: `booked_count` default=10 inflates new contracts. New contracts with 0 real bookings appear popular due to synthetic floor. Misleads customers, harms sort fidelity.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: recommendation-engine-completion-roadmap
---

# Recommendation booked_count Default=10 — Inflates New Contracts

## Summary
`booked_count` default=10 inflates new contracts. New contracts with 0 real bookings appear popular. Misleads customers, harms sort fidelity.

## Why It Matters
New launch contract gets default 10 bookings → appears in "Popular" list → customer clicks → zero real demand signal. Sort algorithm polluted.

## Detail
**Bug code:**
```python
class Contract(models.Model):
    booked_count = models.IntegerField(default=10)  # WRONG
```

**Problem:** New contract has 0 real bookings, but `booked_count=10` → sorted as popular. Old contracts with real bookings buried.

**Fix:**
```python
class Contract(models.Model):
    booked_count = models.IntegerField(default=0)  # Honest zero
```

**Backfill:** Run migration to set accurate initial values from actual booking counts.

**Better:** Use computed field:
```python
@property
def booked_count(self):
    return self.booking_set.filter(status='confirmed').count()
```

(Or cache if query expensive.)

## Constraints / Gotchas
`default=0` exposes new contracts to sort-order problem (no data). Solution: exclude contracts with <5 bookings from "Popular" UI; use "New" filter instead.

## Related
- [[precompute-popular-contracts-audit]] — popularity computation
- [[recommendation-engine-completion-roadmap]] — parent (data quality)
