# ADR: Trip Confidence Score Algorithm

> **Audited 2026-06-14** — formula field claims verified against `products/serializers.py`. Rejected Alternative B corrected (recommendation endpoint exists). See "Rejected Alternatives" → B.

## Status: Proposed

---

## Context

The trip search results redesign (2026-06-14) requires a "Recommended" sort order and a "Confidence Score" badge on contract cards. The score must synthesize four existing backend signals into a single 0-100 number that ranks contracts by overall trustworthiness.

The four signals available on `Contract` are:

| Signal | Model field | Type | Nullable | Source |
|--------|-------------|------|----------|--------|
| `score` | `FloatField(null=True, blank=True)` | Manual | Yes — null by default | Admin-set only; no auto-compute |
| `average_rating` | `SerializerMethodField` on `ContractSerializer` | Computed | Returns `None` if no approved reviews | `Review.objects.filter(is_approved=True).aggregate(Avg('rating'))` |
| `review_count` | `SerializerMethodField` on `ContractSerializer` | Computed | Returns `0` if no reviews | `Review.objects.filter(is_approved=True).count()` |
| `booked_count` | `PositiveIntegerField(default=10, blank=True)` | Cumulative total | No — defaults to 10 on creation | Incremented by booking system |

The originally proposed client-side formula was:

```
score_component  = (contract.score || 0) / 100     × 0.40
rating_component = (contract.average_rating || 0) / 5  × 0.30
review_trust     = min(review_count / 50, 1)         × 0.15
popularity       = min(booked_count / 500, 1)         × 0.15
output           = round(total * 100)   → 0-100
```

Analysis of field semantics revealed that:
1. `contract.score` is `null` on any contract that has not been manually touched by an admin. It is not auto-computed. Assigning 40% weight to a field that is null for most contracts renders the largest single weight meaningless.
2. `booked_count` defaults to `10` (seeded) at creation — not `0` — to avoid a zero cold-start problem. The 15% popularity component therefore yields approximately `0.003` for brand-new contracts regardless of seeding.
3. `average_rating` and `review_count` are computed via separate N+1 DB queries per contract per serialization. If `confidence_score` is added as a third `SerializerMethodField`, a query consolidation is required.

---

## Decision

**Compute `confidence_score` on the backend as a `SerializerMethodField` on `ContractSerializer`.** Do not compute it client-side.

**Rationale:**
- The admin dashboard, mobile app (future), and any other consumer will need a consistent score. Formula drift between clients creates support burden.
- `score`, `booked_count` are already model attributes (no DB query). `average_rating` and `review_count` already require DB hits that are paid regardless. Adding `confidence_score` as a fourth method does not add query cost if the review stats queries are consolidated into a shared internal method.
- A backend field enables server-side `order_by('-confidence_score')` if a dedicated `/recommended/` endpoint is added in a future sprint.

---

## Formula

The validated formula reweights the `score` component from 40% to 10% to reflect its actual population rate (admin-only, nullable):

```
rating_component = (average_rating / 5)           × 0.45
review_trust     = min(review_count / 50, 1)       × 0.25
popularity       = min(booked_count / 500, 1)      × 0.20
score_bonus      = (score / 100)                   × 0.10

confidence_score = round(sum_of_components * 100)  # 0–100
```

Null handling:
- `average_rating` is `None` when no approved reviews exist → treat as `0`
- `score` is `None` when admin has not set it → treat as `0` (score_bonus contributes nothing)
- `booked_count` is always an integer (minimum 10 by DB default)

**Implementation location:** Add `get_confidence_score(self, obj)` as a `SerializerMethodField` on `ContractSerializer` in `products/serializers.py`. Add `'confidence_score'` to the `Meta.fields` list (currently line 375-377).

> **Audit-verified (2026-06-14):** All 4 input fields confirmed in `ContractSerializer.Meta.fields` (serializers.py:375-377): `score`, `average_rating`, `review_count`, `booked_count`. `confidence_score` does NOT yet exist (no `get_confidence_score` in codebase — must be added). `score` = `FloatField(null=True)` at `operators/models.py:265` (manual, no auto-compute — verified). `booked_count` = `PositiveIntegerField(default=10)` at line 268 (verified). `average_rating`/`review_count` method bodies at serializers.py:323-331 + 333-340 (field declarations at 265-266) — both N+1, no prefetch (verified).

**Query consolidation:** Refactor `get_average_rating`, `get_review_count`, and `get_confidence_score` to call a shared `_get_review_stats(obj)` private method that executes a single aggregate query:

```python
def _get_review_stats(self, obj):
    Review = apps.get_model('dialogue', 'Review')
    contract_ct = ContentType.objects.get_for_model(Contract)
    return Review.objects.filter(
        content_type=contract_ct,
        object_id=obj.id,
        is_approved=True
    ).aggregate(avg_rating=Avg('rating'), count=Count('id'))
```

Each of `get_average_rating`, `get_review_count`, and `get_confidence_score` should call this method. Django ORM caching will not help here across three separate method calls — use Python-level instance caching (e.g., store the result on `self._review_stats_cache`).

**Frontend change required:** Update `sortContractsByScore` in `helpers/tripSorting.js` to sort on `contract.confidence_score` rather than `contract.score`. The current implementation reads the raw admin field, which is null for most contracts and produces a flat tie across the entire result set.

---

## Cold-Start Handling

A brand-new contract with the validated formula produces:

```
rating_component = 0   (no reviews)
review_trust     = 0   (0 reviews)
popularity       = 0.003  (seeded booked_count=10, min(10/500,1)*0.20 = 0.004)
score_bonus      = 0   (score=null)
confidence_score = round(0.004 * 100) = 0
```

**This is acceptable** — new contracts will appear at the bottom of the "Recommended" sort, not suppressed from results entirely.

**Cold-start mitigation (chosen approach):** Document `contract.score` as the admin's explicit onboarding lever. During operator onboarding, admins set `score` to `50` in Django Admin. This immediately gives the new contract `score_bonus = 0.05`, yielding `confidence_score ≈ 5`. Contracts with `confidence_score < 5` are not shown with a "Recommended Pick" badge but remain visible in date/price sorts. No code change required.

**Rejected mitigation:** A time-based `new_operator_boost` field was considered (flat +15 for contracts < 90 days old). Rejected because it requires a migration and creates a cliff effect where visibility drops sharply at 90 days.

---

## Consequences

**Positive:**
- Single source of truth for the recommended score across all clients.
- `sortContractsByScore` in `tripSorting.js` becomes a meaningful sort (currently sorts on a field that is null for most contracts).
- Enables server-side sort and a future `/recommended/` endpoint without formula reimplementation.
- Reduces client complexity — frontend receives one number and sorts on it.

**Negative:**
- Adds one `SerializerMethodField` to `ContractSerializer`, which is already large (29 fields in Meta.fields).
- Requires query consolidation work to avoid a third N+1 hit on the review table — this is the main implementation risk.
- Formula is locked in the serializer; A/B testing formula weights requires a backend deploy.

**Neutral:**
- The `score` field retains its existing admin UI and audit trail via `HistoricalRecords`. It shifts semantic role from "primary sort key" to "admin override boost" (10% weight).

---

## Rejected Alternatives

### A: Pure client-side formula (original proposal)
Rejected because multiple clients (admin dashboard, potential mobile app) would need to replicate the formula. The 40% weight on the `score` field — which is null for most contracts — makes the proposed formula produce near-identical (near-zero) scores for the majority of contracts, defeating the purpose of the sort.

### B: Dedicated `/api/v1/trips/<from>/<to>/recommended/` endpoint
Rejected for this sprint.

> **AUDIT CORRECTION (2026-06-14):** An earlier draft said the recommendation serializer was "scaffolding not yet wired to a view." **This is false.** A live `RecommendationViewSet` exists at `products/views.py:1685`, serving `GET /api/v1/recommendations/<contract_id>/?type=hybrid&limit=8`, importing and using `RecommendationItemSerializer` (serializers.py:1203-1235) at views.py:1773 + 1779.
>
> **However** — that endpoint is a **cross-sell / related-products** engine keyed by a single known `contract_id` (returns similar trips, alternative operators, packages). It is NOT a search-results ranker that answers "which trip is best for this route+date search." It solves a different problem.

**Decision stands:** defer a dedicated *search-results ranking* endpoint. The existing `RecommendationViewSet` does not replace the `confidence_score` sort on search results — different input (contract_id vs route+date) and different purpose (cross-sell vs ranking). Client-side sort on the backend `confidence_score` field remains the right approach for search-results ranking.

**Before building:** audit `RecommendationViewSet` + `get_recommendations` service (`products/services.py`) to confirm no overlap and to see whether its scoring logic (it already references `score, popularity` per the docstring) can be reused for the `confidence_score` computation.

### C: Store computed score as a denormalized `FloatField`
Rejected because it requires a signal/management command to keep it fresh whenever reviews are approved or bookings are confirmed. Adds operational complexity (stale data windows, backfill on deploy). The four input signals are cheap enough to compute at serialization time after query consolidation.

### D: Keep `score` at 40% weight, require admin population
Rejected because it creates a business dependency on admin discipline. Operators with unpopulated `score` fields (the majority) would receive `confidence_score = 0` regardless of their rating or booking history, making the "Recommended" sort indistinguishable from an arbitrary order.
