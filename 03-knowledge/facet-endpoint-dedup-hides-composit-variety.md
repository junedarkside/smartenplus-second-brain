---
name: facet-endpoint-dedup-hides-composit-variety
description: A filter-facet endpoint that dedupes to one row per operator (cheapest wins) can silently omit combos that still exist in the actual results endpoint, if that endpoint has no such dedup. The filter UI never offers the omitted combo as an option, so users can never select it — even though it's bookable.
type: knowledge-atom
date: 2026-08-15
parent: available-transport-filter-chip-fix
---

# Facet-Endpoint Dedup Hides Composit Variety

## Summary
`products/views.py`'s `TripFilter` endpoint (serves `unique_transport_composit_list`, the data that populates filter chips) dedupes contracts to one per operator per trip — cheapest wins (`operator_best` dict, `_get_display_rate` comparison). The separate results endpoint (`FindTripViewSet`, serves the actual trip cards) has no such dedup. If one operator sells two composits on the same trip at different prices (e.g. Van Standard + Van VIP), only the cheaper composit's shape becomes a selectable filter chip — the VIP composit's contracts still render in results, but no filter chip exists to select them by, and any *other* active filter silently excludes them since they never match a visible option.

## Context
Found auditing the Available Transport filter bug at `/trips/hatyai/koh-lipe` (#318). Not the bug that was reported (that was a string-normalization + `parseOption` display bug, fixed separately) — found as a side effect while tracing why the filter-facet endpoint and the results endpoint could disagree on what composits exist for a trip.

## Problem

### Symptom
A trip has an operator selling both "Van Standard" (cheap) and "Van VIP" (expensive) on the same route. The Available Transport row shows one "Van" chip. Selecting it correctly returns the Standard contracts. The VIP contracts are present in the unfiltered results but become **unreachable** the moment any transport-option filter is active — no chip exists for a user to select them by, and the active-filter match logic (`FilteredTripList.js`) legitimately excludes anything that doesn't match a selected chip's exact composit signature.

### Root cause
Two endpoints serving the same conceptual "what transport options exist on this trip" question apply different dedup rules. `TripFilter.list()` (views.py, `operator_best` per-operator-cheapest) feeds the chip UI; `FindTripViewSet` (no dedup) feeds the actual cards. The dedup was written for a different purpose (avoid overwhelming the facet UI with every rate variant an operator has) and was never checked against "does this hide a real, distinct, bookable option."

## Decision
Not fixed — flagged, not resolved. Reasoning: "fix" isn't obviously right. Removing the dedup could flood the filter row with near-duplicate chips (every rate variant, not just meaningfully different composits). Porting the dedup logic to the results endpoint instead would be worse — it would hide real inventory from the actual trip list, an availability/upsell decision, not a display bug. Needs product input on the intended behavior (should every priced variant get its own chip? should chips dedupe by composit shape only, ignoring price/operator?) before writing code.

## Related
[[ratecard-category-mixing-price-bug]] — same session family (`/trips/hatyai/koh-lipe` audits), same lesson shape: a shortcut (`Math.max` across categories / dedup-to-cheapest across variants) that's correct *most* of the time produces a silent, hard-to-notice gap the rest of the time.
