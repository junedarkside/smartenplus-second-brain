# Contract Confidence Score Algorithm

## Summary
Backend-computed `confidence_score` (0–100) on `ContractSerializer` combines rating/popularity/admin-override signals with reweighted formula to fix broken `sortContractsByScore`.

## Why It Matters
Current `sortContractsByScore` sorts on `contract.score` (raw nullable admin field) → meaningless when `null` (most contracts). New algorithm gives meaningful Recommended sort + ranking signal for cards/hero.

## Detail
**Field:** `confidence_score = SerializerMethodField` on `ContractSerializer`. Refactor `get_average_rating`, `get_review_count`, `get_confidence_score` to share `_get_review_stats(obj)` internal method → avoids 3 N+1 queries.

**Formula:**
```python
rating_component = (average_rating / 5)          * 0.45
review_trust     = min(review_count / 50, 1)     * 0.25
popularity       = min(booked_count / 500, 1)    * 0.20
score_bonus      = (score / 100)                 * 0.10  # admin override only
confidence_score = round((rating_component + review_trust + popularity + score_bonus) * 100)
```

**Validation example:** established operator (30 reviews @ 4.2, 200 bookings, score=null) = 0 + 0.378 + 0.15 + 0.08 = **61/100**. New operator with `booked_count=10` cold-start seed → `confidence_score ≈ 0`.

**Tiebreaker chain:** `confidence_score` → `average_rating` → `booked_count` → `id` (stable).

## Constraints / Gotchas
- `booked_count` default=10 is **cold-start seed, not real bookings** — `min(10/500, 1) * 0.20 = 0.004`, essentially zero.
- `score` field manually admin-set, no auto-compute — 40% original weight was dead weight for untouched contracts.
- `average_rating`/`review_count` both `SerializerMethodField` — N+1 per contract (lines 323-340). Share one query in `_get_review_stats`.
- Cold-start: new operator → score ≈ 0. Either exclude from Recommended (<10) or have admin set `score=50` on onboarding.

## Related
- [[trip-search-results-redesign-2026-06-14]] (parent)
- [[trip-search-results-implementation-plan-2026-06-14]] (Phase 1 spec)
- [[quick-filter-pills-direct-refundable]] (related sort/filter logic)
