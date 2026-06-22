---
name: recommendation-flat-score-finder-pollution
description: Flat-score finder pollution — package=90, activity=80, alternative=70 overrides per-contract signal. Pollutes recommendation quality with high-score but irrelevant items. Crowds out genuine recommendations.
metadata:
  type: knowledge
  status: active
  date: 2026-06-22
  parent: recommendation-engine-completion-roadmap
---

# Recommendation Flat-Score Finder Pollution

## Summary
Flat-score finder pollution: package=90, activity=80, alternative=70 override per-contract signals. High-score but irrelevant items crowd out genuine recommendations.

## Why It Matters
Customer sees recommendations not relevant to their booking (wrong category, wrong destination). Conversion drops, trust erodes.

## Detail
**Bug code:**
```python
def score_recommendation(item, user_context):
    base_score = item.popularity_score
    # OVERRIDE per contract (pollutes)
    if item.contract_type == 'package':
        base_score = 90  # Arbitrary boost
    elif item.category == 'activity':
        base_score = 80
    elif item.is_alternative:
        base_score = 70
    return base_score
```

**Problem:** User books tour → gets package recommendations (score 90) even though they only want activities. Signal not contextual.

**Fix:** Remove flat overrides. Score = weighted sum of:
- Popularity (bookings, views)
- Similarity (location, category, price band)
- Personalization (past history, seasonality)

```python
def score_recommendation(item, user_context):
    return (
        item.popularity_score * 0.4 +
        similarity_score(item, user_context) * 0.4 +
        personalization_score(item, user_context) * 0.2
    )
```

## Constraints / Gotchas
Some contracts genuinely underperform → boost via `boost_factor` field (admin-controlled), not hardcoded override.

## Related
- [[recommendation-anchor-priority-experience-before-transport]] — companion priority bug
- [[recommendation-engine-completion-roadmap]] — parent (engine correctness risks)
