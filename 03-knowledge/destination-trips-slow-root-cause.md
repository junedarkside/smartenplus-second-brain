# Destination Trips API Slow — N+1 in RouteSerializer Descriptions

## Summary
`/destinations/[slug]` contract list was slow mainly because `RouteSerializer` ran a station-translation query per description field per route (~380 round-trips on a 94-route page). Introduced 2026-10-07 (`f0d3a04`, `d54a5c9`), fixed in `f2fa237` on BE `develop` (2026-10-09). Prod effect NOT yet measured — deploy, then one timed curl.

## Context
Example: `/destinations/koh-lipe-pattaya-beach` → FE calls `/api/v1/trips/All Destinations/Koh Lipe Pattaya Beach/` (`helpers/destinationPage.js` `DEPARTURE_STATION='All Destinations'`). Related: [[locations-destinations-product-split]], [[destinations-page-redesign]].

## Measured
- Prod (read-only GETs): `/trips` 26 trips / 68 contracts / 672 KB, TTFB 19.6s, repeat 32.8s, then 504 @60s. Late 504s = worker pool saturated; own probes contributed. **Do not loop-curl prod.**
- Clean `develop` baseline: `products.test_trips_perf` 10/16 failing. `/trips` = **142 queries** (bound 30); **114 were one repeated `stations_stationtranslation` lookup**. The trip search itself = 2 queries, ~18 ms each → **search is NOT the bottleneck**.
- After fix: 29 queries, test-dataset time 2.12s → 1.57s (local DB, near-zero latency; prod gain should be far larger).

## Root cause
`RouteSerializer._get_station_desc` (`products/serializers.py`) did `station.translations.filter(language=…, is_reviewed=True).first()` on every call: 4 description fields × (trips + contracts routes), +1 query for the Thai→English fallback. `.filter()` bypasses prefetch; `prefetching_list_serializer` skips `en`. Added without refreshing goldens or the query bound, so the existing N+1 guard test was already red and nobody noticed.

## Fix (shipped to develop, not deployed)
- `load_station_descriptions(cache, ids)`: ONE query for all stations' reviewed `en`/`th` rows.
- `RouteDescriptionPrefetchListSerializer` (used by `TripSerializer`) preloads route stations; `_get_station_desc` reads the cache (lazy 1 query per station elsewhere). Lookup order unchanged: lang → en → station's own text.
- Goldens refreshed (diff = only the 4 new keys). `products/test_station_description.py` compares against the original logic over 7 fallback cases.
- Full suite: 93 failures, none in products/stations; sampled modules fail identically on clean `develop` (stale fixtures: `create_user()` args, order contact constraint, `create_contract(advance_hour)`, indentation errors). Parallel test mode breaks payment concurrency tests — run serially.

## Still open (secondary, only if prod stays slow after deploy)
A cache serialized `/trips` payload (short TTL; price staleness is payment-adjacent, decision pending). B slim list serializer, opt-in (payload ~75% detail data: `timeline` 225 KB, `all_info` 113 KB; audit callers TripDetail3/TripDetailContent/ExtraItems/BookingDetail first). C FE seed RTK `initialData` from ISR props (`useTripData` ignores `initialTrips`). D `/stationsinfo/{slug}` trailing slash. E uWSGI worker count. `/tripfilter` repeats the search (2 heavy calls per view).

## Superseded
The two-step `fetch_trips` search rewrite (`products/trip_search.py`) was planned then **dropped**: measurement showed search ≈ 36 ms of the cost. Also wrong earlier: "response not cached is the main cause".

## Lessons
- Measure with the query-template output (`test_trips_perf -v 2`) BEFORE planning optimizations; the plan was built on a hypothesis that step 0 disproved.
- A red perf/golden test on `develop` is a signal, not noise. New serializer fields need golden + `BOUNDS` updates in the same commit.
- Per-instance DB calls inside `SerializerMethodField` are the usual N+1 source; batch in the list serializer.

## Related
[[precompute-popular-contracts-audit]] (different cache, not the cause) · [[contract-confidence-score-algorithm]] · [[isr-client-rtk-stats-seo-pattern]] · [[ad-first-page-timeout-investigation]] (same release, AD side)
