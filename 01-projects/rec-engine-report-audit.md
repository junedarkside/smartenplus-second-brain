# Rec-Engine Report Audit — 4-Specialist Review

## Summary

4-agent audit (BD / UX / BE-Django / FE-Next.js) of the 2026-07-15 rec-engine report (sub-project verdict, BE-HOMEPAGE-PRICE fix, REC-SLOT-WASTE analysis). Headline: **fix confirmed correct but deploy needs Redis flush; REC-SLOT-WASTE verdict flipped to DO NOTHING; Option A (`exclude_ids`) rejected by all 4 lenses.**

## Context

Session #249 produced: (1) sub-project verdict NO, (2) BE-HOMEPAGE-PRICE fix shipped (BE develop `06423c5`), (3) REC-SLOT-WASTE root-cause analysis + Option A/B fix proposal. This audit ran before the report becomes canon. Constraints governing all verdicts: no tech debt, no over-engineering, simplest solution, reuse first, zero side effects.

## Verdict Table

| # | Claim | Verdict | Key evidence |
|---|-------|---------|--------------|
| 1 | Sub-project NOT needed | **CONFIRMED** (all 4) | Catalog numbers verified vs [[products-live-catalog-audit]]: 7/10 categories empty, 1224 contracts, SPA single-operator, DAY_TOUR northern bias. Isolation means zero cost to deferral. |
| 2 | BE-HOMEPAGE-PRICE fix correct + complete | **CONFIRMED** | All 8 `Min()` sites patched (`services.py:356/439/520/551/611/662/717/777`). Other price paths already clean: `route_lowest_price_annotation` (:115), `PopularExperienceSerializer.get_min_price` (serializers.py:755), `get_lowest_price` fallback (:1113), `views.py:445`. No unfiltered `Min(selling_rate)` left in products/ or operators/. |
| 3 | "No migration, no FE change" for the fix | **REFINED** | True, BUT deploy needs one-off Redis flush (see Deploy Gotcha below). |
| 4 | REC-SLOT-WASTE root cause (BE caps before FE strips) | **CONFIRMED** | `find_transport_at_location` slices `[:limit]` at ORM (services.py:780); per-zone cap :903; cache set at get_recommendations level :954 — finders never see cart. FE strips at `CheckoutRelatedTrips.js:91-103`. |
| 5 | Severity escalation ("multi-item cart makes it worse") | **OVERTURNED** (UX+BD) | Empty ESSENTIAL zone when cart already holds 2 transport items = arguably CORRECT UX — user's transport need is met; more transport recs at payment page = friction. Header already adapts ("People also book" vs "Complete your trip", :206-208). Incidence near-zero today: the inventory needed to create the collision (Koh Lipe return routes, island DAY_TOURs) doesn't exist — [[cross-sell-integration-status-2026-06-13]]. |
| 6 | "Option A (`exclude_ids`) is correct" | **OVERTURNED** (all 4) | See Option A Rejection below. |

## Option A Rejection (unanimous)

1. **Cache fragmentation** — precompute writes 12 bounded keys/contract (`recommendations:{id}:{type}:{limit}:{rate_date}`, services.py:851). `exclude_ids` in key = unbounded per-cart key space = cache miss per unique cart = live queries on a 1-vCPU box with `concurrency=1` Celery (tasks.py:125). Perf regression, no upper bound.
2. **RTK cache churn** — `exclude_ids` in query args changes the RTK Query cache key on EVERY cart mutation → refetch + skeleton flash at the most conversion-sensitive moment. Isolated to checkout (other 2 surfaces don't pass it) but that's exactly where it hurts.
3. **Solves only half the drain** — `filterValidRecommendations` (advance-hour, capacity, stop-sale, seats) is a SECOND independent slot-drain path after the BE cap. `exclude_ids` does nothing for it; only over-fetch covers both. (FE audit's key finding.)

## Decision: DO NOTHING on REC-SLOT-WASTE

- Severity reclassified: **near-zero incidence today, medium impact when triggered, and the worst case is arguably correct behavior**.
- `checkout_recommendation_empty` GTM event already exists (`CheckoutRelatedTrips.js:183-190`) — measure before fixing. If it correlates with abandonment later, revisit.
- IF a fix is ever warranted, simplest path (BE audit): bump finder internal fetch `[:limit]` → `[:limit*2]` inside `find_transport_at_location` — one line, no API surface, no cache-key change (key uses caller's `limit`, not finder's slice).
- Leader correction to FE audit: bumping FE `maxItems` 4→8 only helps the transport-anchor (`packages`) path — the zone path ignores `limit` entirely (services.py:930-931 "must NOT be re-truncated to limit"). Not a general fix.

## Deploy Gotcha — Redis flush required (leader-verified)

Precompute skip-if-fresh guard (tasks.py:66-75): skips regeneration when remaining TTL > 22h. Keys written pre-fix can serve **stale prices up to 24h post-deploy**. After deploying `06423c5` to prod:

```bash
redis-cli --scan --pattern "recommendations:*" | xargs redis-cli del
```

Add to deploy checklist. Without it, worst case ~24h of wrong "From" prices (self-heals via TTL).

## New Revisit Trigger (BD)

Add to sub-project trigger list: **GTM funnel attribution shows measurable rec→purchase conversion worth optimizing** (funnel went live 2026-07-15; run ~30 days before further rec-engine architecture investment).

## Tradeoffs

- DO NOTHING accepts occasional 1-short zones at checkout — cheap vs cache blast radius (cache-key mismatch class already burned this codebase once — see [[precompute-popular-contracts-fix-plan]]).
- Redis flush is a manual deploy step (one-off) — acceptable vs building auto-bust machinery for a single event.

## Related

[[recommendation-engine-completion-roadmap]] · [[products-live-catalog-audit]] · [[cross-sell-integration-status-2026-06-13]] · [[precompute-popular-contracts-fix-plan]] · [[recommendation-system]] · [[master-state]]
