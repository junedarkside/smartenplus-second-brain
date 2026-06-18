# Recommendation Engine — Feedback vs Codebase Gap + Roadmap

## Summary

3-agent review (FE / BE / Business-UX) of external "Travel Completion Engine" feedback doc against the live recommendation codebase. Reviewed 2026-06-18.

**Verdict:** Current engine is ~8/10 on UI/checkout, ~5/10 on intelligence/cross-sell. The feedback's *direction* is correct (shift from "People Also Book" → travel completion), but its P1/P2/P3 **sequencing is wrong for a thin catalog**. Measurement + never-empty fallback must come before zones/rules/AI. Two of the feedback's flagship ideas (weekly social proof, inventory urgency) are **trust risks for EU/US travelers** and should be skipped until backed by real data.

No code changed this review.

> **Audit update 2026-06-18 (/grill):** the original report wrongly listed the FE change `recType 'activity'→'hybrid'` as a *done improvement*. Code verification proved it is a **P0 regression** for non-transport carts. See section below. The combined gap table's optimistic framing of "hybrid is more resilient" is **wrong** and corrected here.

---

## P0 REGRESSION — `hybrid` kills non-transport recommendations

**Symptom:** spa/tour/ticket-only cart → recommendation widget shows nothing (hides).

**Root cause (verified `services.py:692-709`):**
- FE `CheckoutRelatedTrips.js:37` sends `recType='hybrid'` for every non-transport cart.
- Backend `hybrid` runs ONLY `find_similar_contracts` + `find_alternative_contracts` + `find_package_contracts`.
- All three early-return `[]` when `source_contract.trip.route` is null (`services.py:235-237`, `421-423`, route-keyed query). **Every non-transport contract has no trip/route.**
- The ONLY branch that reaches location-based cross-sell (`find_activity_contracts` / `find_nearby_activities`) is `rec_type == 'activity'` (`services.py:704-709`) — which `hybrid` never enters.
- Net: non-transport `hybrid` = three empty lists = `[]` = widget hides. The old `'activity'` value was the only working path.

**Chosen fix — backend `hybrid` fallthrough (DECISION):**
In `get_recommendations`, before the route-based branches: if `rec_type == 'hybrid'` AND source has no `trip.route`, route to `find_nearby_activities(source, limit)` (location-based) instead. One backend edit, fixes ALL callers, keeps FE `'hybrid'` honest. Needs BE deploy.

```python
# get_recommendations, ~line 692
if rec_type == 'hybrid' and not (source_contract.trip and source_contract.trip.route):
    recommendations.extend(find_nearby_activities(source_contract, limit))
else:
    # existing similar + alternatives + packages branches
```

**Still data-gated:** `find_nearby_activities` needs `source.primary_location` or `service_areas.first()`, else `[]` (`services.py:562-566`). So the fix unblocks recs only for non-transport contracts that have a location populated — ties back to the `primary_location` data-ops gap + Koh Lipe blocker. Fix removes the *code* dead-end; data population removes the *empty result*.

**Why not FE revert to `'activity'`:** rejected — `'activity'` branch's first call (`find_activity_contracts`) also needs `trip.route` (`services.py:705`), only falling through to `find_nearby_activities`; backend fix is the single honest place and helps every caller.

---

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

**P0 — Regression fix (DO FIRST):** backend `hybrid` fallthrough to `find_nearby_activities` when source has no `trip.route` (see P0 section). Restores non-transport recs. ~5-line BE edit + deploy.

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

---

## Addendum 2026-06-18 — "Travel Completion" strategy doc review (2-agent: BD/UX + BE engine)

Second external doc proposes the **anchor→matrix** model: each `service_category` maps to PRIMARY/SECONDARY target categories, intent taxonomy ESSENTIAL/POPULAR/UPGRADE/DISCOVERY, 3 ordered zones, cap SIMILAR at 0-1. Explicitly says the rule *"a day tour should NOT recommend transport"* is **too restrictive**.

### Verdict correction (mine was too absolute)
Earlier session verdict "day tour should NOT recommend transport" → **corrected**. The doc is directionally right. Right rule for our catalog:

> Day-tour anchor prioritizes COMPLEMENTARY first (transfer/upgrade), then nearby experiences, then 0-1 similar. Transport qualifies as ESSENTIAL **only when** (a) same destination, (b) it serves a return/onward leg the traveler still needs, (c) not the anchor category. NOT blanket transport, NOT "5 more day tours."

The prior **seed-data fix** (detach dummy trip from 17 activity contracts → `find_nearby_activities`) solved the *data bug* (geographically-wrong Phi Phi/Samui recs for a Chiang Mai tour). It did NOT implement this strategy — it just makes recs same-destination activities. Strategy layer still unbuilt.

### Where the doc assumes inventory/schema we don't have
- **No tour-transfer product type.** Our 26 TRANSPORTATION contracts are point-to-point routes (ferries/vans), NOT "airport/hotel pickup for tour guests." Doc's PRIMARY "hotel/airport transfer" for a day tour = **0 buildable SKUs today**. BD must create them.
- **No JOIN↔PRIVATE upgrade link.** `Contract.type` has `PRIVATE` but there is **no `upgrade_of`/`variant_group` FK**. e.g. "Chiang Mai Elephant (Join)" id119 and "...(Private)" id124 are unrelated rows. UPGRADE zone = heuristic (same category+location+`type=PRIVATE`) with false-positive risk, OR needs a schema migration for reliability.
- **No `SUNSET_CRUISE`/`CRUISE` category.** Doc product labels must normalize to real enum (`DAY_TOUR`/`ATTRACTION_TICKET`).
- Catalog is THIN: SPA 3, FOOD_DINING 3, EVENT 3, ATTRACTION 3, ACCOMMODATION 2. Per-destination complementary hit rate ≈ 0-1.

### Engine capability gaps (services.py)
| Doc item | Current | Gap | Migration? |
|---|---|---|---|
| Intent taxonomy + zone orchestration | dispatch on string `rec_type` only | needs zone-aware orchestrator (call N finders, label by zone, dedupe) | no |
| Category MATRIX (anchor→targets) | `find_nearby_activities` does location cross-category, but `ACTIVITY_CATEGORIES` is **hardcoded + excludes TRANSPORTATION/TRANSFER** | replace static list with `CATEGORY_MATRIX` lookup keyed by anchor category | no |
| ⚠️ same-category +30 score | `find_nearby_activities:594` adds +30 when target category == source | **contradicts matrix intent** (rewards similar, not complementary) — must flip to matrix-priority score | no |
| ESSENTIAL transport-for-activity | excluded by the hardcoded list | matrix adds TRANSFER/TRANSPORTATION to primary targets for DAY_TOUR/SPA etc | no |
| UPGRADE (private twin) | no finder; no variant FK | heuristic finder (type=PRIVATE+same cat+loc) OR `upgrade_of` FK for reliability | **yes for reliable** |
| POPULAR (booked_count rank) | `booked_count` exists, **not wired into any finder** | add `.order_by('-booked_count')` or score boost | no |
| SIMILAR cap 0-1 | `limit` param already works | trivial | no |

### Empty-zone trap (BD flagged — critical)
Cap-similar-at-0-1 + thin complementary inventory ⇒ most checkouts render 1-2 cards or empty zones with headers. **Worse than today.** Required guardrails:
1. **Conditional zone render** — never show a zone header with 0 cards.
2. **3-card floor** — 0-1 similar cap is a *preference*, not a *floor*; backfill with SIMILAR up to 3 total when ESSENTIAL+POPULAR+UPGRADE < 3. Revisit hard cap when complementary ≥5 SKUs/destination.

### Highest-ROI move (both agents converge)
**Conditional POPULAR zone using the existing 9 non-tour complementary SKUs (SPA+FOOD_DINING+EVENT), destination-matched via populated `primary_location`, render-only-if-nonempty.** Zero BD work, zero schema change, no new product type — first genuine cross-category lift the platform ships. Plus flip the `+30` same-category bonus and add `booked_count` ordering.

### Sequencing for us (supersedes generic doc P1/P2/P3)
- **Now (eng only):** adopt taxonomy labels + zone orchestrator w/ conditional render + 3-card floor; matrix config (incl. flip +30 bonus, add booked_count); enable existing SPA/FOOD/EVENT as POPULAR for tour+transport anchors; narrow transport-as-ESSENTIAL rule.
- **BD sprint (4-6wk):** create tour-adjacent transfer SKUs per major destination (Chiang Mai/Samui/Krabi); wire upgrade twins for top-5 tours; close Koh Lipe `CROSS-SELL-BD-INVENTORY`.
- **Schema:** `upgrade_of` FK for reliable UPGRADE zone.

**Net:** doc is the right philosophy applied to a more mature catalog than ours. Adopt philosophy + the one zero-inventory win now; gate matrix rows that assume missing inventory on BD.

---

## Addendum 2026-06-18 — Zones SHIPPED + algorithm best-practice review

Built on branch `feat/checkout-recommendation-zones` (BE+FE). Activity-anchor checkout now renders labeled conditional zones.

### What the algorithm does now (activity anchor, no trip.route)
```
get_recommendations(hybrid):
  ESSENTIAL = find_transport_at_location  (transport whose ROUTE station
              location == anchor.primary_location; score 95-100; cap 2)
  POPULAR   = find_nearby_activities, cross-category items
              (matrix priority + booked_count + location + score; cap 4)
  SIMILAR   = find_nearby_activities, SAME-category items (cap 1)
  → dedupe by contract id, per-zone caps (ZONE_LIMITS 2/4/1), no global cut
FE groups by item.type, renders each non-empty zone:
  Getting there → Popular in <dest> → You might also like
```
Scoring fixes shipped: dropped the `+30 same-category` bonus (it rewarded "more day tours"); excluded zero/free-infant rates from `lowest_price` Min (was showing "Price on request").

Verified (Phuket demo anchor 185): ESSENTIAL 2 + POPULAR 4 + SIMILAR 1 = 7 cards, all priced.

### Best-practice verdict
**Correct / aligned with travel cross-sell norms:**
- Complementary-over-similar ranking — POPULAR (spa/food/transfer) scores above SIMILAR (more tours). Matches "complete the trip" > "show alternatives." ✓
- SIMILAR capped at 1 — avoids cannibalizing the anchor purchase (showing 5 rival tours lowers checkout confidence). ✓
- ESSENTIAL first + highest score — transport is genuinely trip-completing; right priority. ✓
- Conditional zone render (no empty headers) + per-zone caps — prevents the empty-section UX failure BD flagged. ✓
- Destination-scoped via `primary_location` / route-station bridge — location relevance is the strongest travel signal. ✓

**Gaps vs best practice (known, deferred — NOT debt-shipped):**
- **No UPGRADE zone** — would need a real `upgrade_of` variant FK. A `type=PRIVATE`+same-cat+loc heuristic guesses the twin (false positives) → deliberately NOT built. 3 zones, not 4.
- **No weekly/trending social proof** — uses lifetime `booked_count`. Real "booked X this week" needs a counter + reset task; faking it = dark-pattern (EU/US trust risk).
- **Mobile scroll** — 3 sections before payment CTA is the practical max for mobile checkout; do NOT add a 4th zone above the fold. If UPGRADE lands later, consider collapsing or limiting to 2 visible zones on mobile.
- **No add_cart→purchase analytics** — can't yet measure which zone converts. Add GTM events before claiming any lift.
- **`booked_count` default=10** still inflates new contracts in the popularity tiebreak.

**Net:** algorithm is correct and best-practice for current catalog at 3 zones. 4th zone (UPGRADE) is correctly gated on a schema change, not shipped as a guess. Next highest-value: add_cart/purchase GTM (measure), then upgrade_of FK (true UPGRADE zone).

## Related
[[people-also-book-checkout-audit]] [[cross-sell-placement-strategy]] [[recommendation-type-selection-by-service-category]] [[recommendation-anchor-first-transport-rule]] [[activity-to-activity-cross-sell]] [[django-m2m-location-join-recommendations]]
