# Recommendation Engine — Feedback vs Codebase Gap + Roadmap

## Summary

3-agent review (FE / BE / Business-UX) of external "Travel Completion Engine" feedback doc against the live recommendation codebase. Reviewed 2026-06-18.

**Verdict:** Current engine is ~8/10 on UI/checkout, ~5/10 on intelligence/cross-sell. The feedback's *direction* is correct (shift from "People Also Book" → travel completion), but its P1/P2/P3 **sequencing is wrong for a thin catalog**. Measurement + never-empty fallback must come before zones/rules/AI. Two of the feedback's flagship ideas (weekly social proof, inventory urgency) are **trust risks for EU/US travelers** and should be skipped until backed by real data.

No code changed this review.

## Catalog reality (constrains everything)

- Small SKU depth; cross-sell chains (spa→ferry→transfer) not built.
- No real-time inventory/seats system exists at all.
- Koh Lipe (highest-yield cross-sell destination) inventory still a BD blocker — `CROSS-SELL-BD-INVENTORY`. Widget auto-hides on 0 recs → slot disappears for the best destination.
- Markets EU/US/Asia — different tolerance for urgency/scarcity patterns.

---

## Combined gap table

| Feedback proposal | Exists today | Gap | Verdict |
|---|---|---|---|
| **Analytics → revenue funnel** (view→click→open→add_cart→purchase→revenue) | view/click/accordion/empty only (`CheckoutRelatedTrips.js:78,105,94,120`). No open / add_cart / purchase events. | 3 missing GTM events. `add_cart` hole in `RecommendationBookingModal.js:157-170` (no dataLayer push after success). `open` hole in `RecommendationCard.js:103-108`. | **NOW** — highest ROI. Every % lift claim is unvalidatable without it. |
| **Never-empty fallback hierarchy** | `CheckoutRelatedTrips.js:119-130` returns `null` on 0 recs. `find_similar_contracts` returns `[]` (services.py:321). `MIN_SIMILARITY_SCORE=50` silently empties. | No fallback cascade. Slot vanishes for thin-inventory destinations. | **NOW** — directly monetizes the slot that dies for Koh Lipe. |
| **2s timeout guard** | `recommendationsApi.js` `fetchBaseQuery` has no `timeout`. | Add `AbortController` 2s in query fn. | **NOW** — 5-line, bundle with other API change. |
| **Fix render-path GTM bug** | `checkout_recommendation_empty` fires in render body, not `useEffect` (`CheckoutRelatedTrips.js:120-128`). | Move to `useEffect`. Pre-existing correctness bug. | **NOW** — fix in same analytics pass. |
| **Destination intelligence** (anchor by destination) | `Contract.primary_location` (FK) + `service_areas` (M2M) EXIST, already queried (`find_activity_contracts:530`, `find_nearby_activities:580`). | Data-ops gap (population), not schema gap. Time-windowed popularity (7d/30d/ctr) absent. | **LATER (parallel w/ BD)** — the actual AOV unlock; useless until Koh Lipe SKUs exist. |
| **recommendation_rules table** (source→target→priority) | `get_recommendations:616` hardcoded `if rec_type` branches + `RECOMMENDATION_SETTINGS` dict (numeric tuning only). | New `RecommendationRule` model + 1 migration. Refactor dispatch to loop. | **LATER** — build data model, defer admin UI. Premature for ~3 cross-sell cats. |
| **3-zone layout** (Must Add / Popular / Upgrade) | Single flat list. Context-aware title only (`:145`). | New API envelope (zones) + render rework + cache-key change. | **LATER** — mobile scroll-fatigue risk; needs mobile UX validation first. |
| **Multi-factor ranking** (complementary/destination/bestseller/rating/margin/recency) | 6-factor formula exists but ONLY in `find_similar_contracts` (`calculate_trip_similarity:87-176`). Other finders use FLAT hardcoded scores (90/80/70). | Unify finders to shared `rank_contract()`. Add `last_booked_at`, margin field. | **LATER** — correctness fix (flat scores pollute hybrid sort). |
| **Weekly/trending social proof** ("booked 32× this week") | Lifetime `booked_count` only (`RecommendationCard.js:154`). | New weekly/monthly counters + reset task + trending_score. | **SKIP** until real auditable data — fake "this week" = dark pattern, EU/US trust risk. |
| **Inventory urgency** ("only 5 seats left") | No inventory system exists anywhere. | Platform feature, not widget feature. | **SKIP** — fabricated scarcity = trust-destroying for EU/US (Booking.com / EU dark-pattern precedent). |
| **AI personalization (P3)** | none | Cold-start on small catalog = confidently wrong recs. | **SKIP 12mo** — revisit after traffic/catalog scale + 6mo event data. |

---

## What the feedback gets WRONG about current code

1. **"PRIVATE/VIP type filter" for UPSELL** — `Contract.type` choices are `JOIN / PRIVATE / CHARTER` (models.py:220-224). There is **no `VIP`** at contract level. `VIP_UPGRADE` is a `ContractAddon.addon_type` (different model). UPSELL zone = `type='PRIVATE'` (or `CHARTER`), not VIP.
2. **Implies `primary_location`/`service_areas` must be added** — both already exist (migration 0045) and are queried. Gap is production data population, not code.
3. **Treats `booked_count` as absent** — exists (models.py:270), already serialized. Note: `default=10` artificially boosts new contracts → will skew any trending formula using raw counts.
4. **Assumes `get_recommendations` is unstructured** — it's partly rule-like (validates `valid_types`, dispatches per type, config dict). Baseline better than doc implies.

---

## Engine correctness risks (found, independent of feedback)

- **Flat-score finders pollute ranking**: `find_package_contracts`=90, `find_activity_contracts`=80, `find_alternative_contracts`=70 override per-contract signal. In `hybrid`, a relevant similar contract (score 65) loses to every package (90) regardless of fit (sort `services.py:712`). Correctness fix, not just enhancement.
- **`MIN_SIMILARITY_SCORE=50` + no fallback** = new/niche contracts return zero recs silently. Highest-priority gap before zones/trending.
- **`daily_counter` orphan**: field exists, no reset task visible → grows unbounded, meaningless as signal. Any new weekly/monthly counter needs reset mechanism shipped same deploy.
- **Cache key omits zone**: if `?zone=` added, key format `recommendations:{id}:{type}:{limit}:{date}` must update or it serves wrong-zone cached results.

---

## Realistic lift assessment

- Doc claims +5-10% CTR / +10-20% AOV.
- **AOV caveat**: same-category recs (current dominance) = basket cannibalization, NOT AOV lift. Only genuine cross-category (destination intelligence) grows AOV. +20% unsupportable until that ships.
- **Honest near-term**: fallback prevents zero-rec disappearance (+visibility), analytics establishes first real baseline. No defensible AOV claim yet.

---

## Corrected roadmap (re-sequenced for thin catalog)

**P1 — Measure & Survive (week 1-2):**
1. Analytics tagging: add `recommendation_modal_open`, `recommendation_add_cart`, `recommendation_purchase`; fix render-path `empty` bug. *(FE only, no deps.)*
2. Never-empty fallback: remove hard `return null`, backend `find_global_fallback(location, category)` cascade (destination bestsellers → category bestsellers → editor picks). Add `is_editor_pick` bool + curate ~5-8 SKUs/destination.
3. 2s timeout guard in `recommendationsApi.js`.

**P2 — Cross-category foundation (week 3-6, parallel w/ BD Koh Lipe):**
4. Destination intelligence backend grouping (data model + finder, no UI). Gate UI on Koh Lipe having ≥5 cross-sell SKUs.
5. Unify finders → shared `rank_contract()` (kills flat-score pollution). Add `last_booked_at`.
6. `RecommendationRule` data model (no admin UI yet).

**P3 — Rules & zones (month 2-3):**
7. Rules-table-driven dispatch + admin UI.
8. 3-zone layout — ONLY after mobile UX validation.
9. Weekly social proof — ONLY if booking event pipeline live + counts real/auditable.

**Deferred indefinitely:** AI personalization, inventory urgency, manufactured scarcity.

---

## Highest-ROI single bet

**Analytics tagging infrastructure first.** Without impression→CTR→add_cart→revenue attribution, no widget performance is knowable, no A/B test is defensible, no % lift claim is provable, and BD can't make the ROI case for closing the Koh Lipe blocker. ~2-3 days eng + 1 day BD curation for fallback SKUs delivers week-1 baseline.

## Related
[[people-also-book-checkout-audit]] [[cross-sell-placement-strategy]] [[recommendation-type-selection-by-service-category]] [[recommendation-anchor-first-transport-rule]] [[activity-to-activity-cross-sell]] [[django-m2m-location-join-recommendations]]
