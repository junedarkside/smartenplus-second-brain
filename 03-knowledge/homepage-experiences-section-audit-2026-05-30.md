# Homepage Experiences Section — Feasibility Audit

## Summary
Assessed adding "Explore Experiences" carousel section to homepage, alongside existing Popular Routes. Three-agent research (frontend, backend, vault) + one scrutinize pass. Corrected 3 critical wrong claims.

## Verdict
**VIABLE — after AT-1 completes + inventory check. All design decisions locked (grill pass 2026-05-30).**

---

## Debate

### For
- Backend Contract model has `booked_count`, `service_category`, `is_actived` — sufficient for ordering + filtering
- `/front-page/` already returns `home_routes[]` + `airport_routes[]` — same pattern for `popular_experiences[]`
- Frontend: `CardCarouselContainer`, `Section`, lib-version `PopularRoutesSection` all reusable unchanged
- Vault strategy (`smartenplus-uxui-redesign-research-2026.md` §8) explicitly endorses experiences on homepage

### Against
- Inventory unknown — if < 6 active experience contracts, section is harmful
- AT-1 (Airport Transfer redesign) is open P0 — close debt first
- No `featured_image` on Contract model — image strategy needed before building

---

## Grill Decisions (2026-05-30)

All locked. Do not re-debate.

| Decision | Choice | Reason |
|----------|--------|--------|
| `average_rating` in serializer | **Skip** | `get_average_rating()` runs 2 DB queries per contract (ContentType lookup + Review aggregate). 8 contracts = 16 extra queries per cache miss. Not worth it. |
| `booked_count` display on card | **Hide** | `Contract.booked_count` defaults to 10 for ALL new contracts (`operators/models.py:268`). Showing number is misleading. |
| Card content | **title + category badge + min_price only** | Clean, no fake social proof |
| Image source | **`imagegallery_set.first().image.url`** | S3 storage confirmed (`DEFAULT_FILE_STORAGE = MediaStorage`). `.url` returns full CDN URL. No migration needed. |
| `min_price` query | **`Contract_RateCard.filter(contract=obj, is_active=True).order_by('selling_rate').first()`** | Reuse exact pattern at `products/serializers.py:1040–1045` |
| Serializer base | **Standalone `ModelSerializer`** — NOT inheriting `ContractSerializer` | `ContractSerializer` is massive (50+ fields, `to_representation` override, ratecard date filtering). Inheriting adds all that weight for a 6-field homepage card. |
| Image N+1 | **`prefetch_related('imagegallery_set')`** on queryset | Reduces 8 image queries → 1 prefetch |
| `min_price` N+1 | **Acceptable** | 8 separate `Contract_RateCard` queries per cache miss. Small table, fast. If becomes problem: annotate with `Min()` in queryset. |

---

## Scrutinize Corrections (2026-05-30)

### Correction 1 — `featured_image` field does NOT exist
- **Wrong claim:** "Contract model has `featured_image`"
- **Reality:** `operators/models.py` — Contract has `ImageGallery` relationship but no `featured_image` field
- **Fix:** Serializer SerializerMethodField → `obj.imagegallery_set.first()` (Option A, no migration). Or add `featured_image = URLField(blank=True, null=True)` + migration (Option B). **Recommend Option A.**

### Correction 2 — `service_category` choices list was incomplete
- **Wrong claim:** Choices listed without `TRANSPORTATION`, `ACCOMMODATION`
- **Actual full list:** `TRANSPORTATION`, `DAY_TOUR`, `MULTI_DAY_TOUR`, `SPA_WELLNESS`, `EVENT_TICKET`, `ATTRACTION_TICKET`, `FOOD_DINING`, `ACCOMMODATION`, `TRANSFER`, `OTHER`
- **Fix:** Inventory check and serializer filter must use correct experience-only subset: `['DAY_TOUR','MULTI_DAY_TOUR','SPA_WELLNESS','EVENT_TICKET','ATTRACTION_TICKET','FOOD_DINING']`. Exclude `TRANSPORTATION`, `TRANSFER`, `ACCOMMODATION`.

### Correction 3 — `HomeSerializer` is wrong copy template
- **Wrong claim:** "HomeSerializer at products/serializers.py:706 is the copy template"
- **Reality:** HomeSerializer is for the `Route` model (transport), not Contract
- **Fix:** New `PopularExperienceSerializer` must inherit from ContractSerializer or be standalone for Contract model. Do NOT copy HomeSerializer.

### Verified (correct)
- `booked_count` — PositiveIntegerField on Contract, line 268 (`operators/models.py`)
- `average_rating` — SerializerMethodField on ContractSerializer (line 309–317, products/serializers.py). Aggregates Review model. Not stored — computed per query. Acceptable for homepage (cached 300s).
- `booking_count_30d` — SerializerMethodField lines 328–337, counts booking_item_contract last 30 days
- `_fetch_home_routes_data()` at `pages_info/views.py:189` — pattern correct for copy
- `FRONT_PAGE_CACHE_TTL = 300` at line 37 — applies to full response_data dict
- `CardCarouselContainer` — `renderCard(item, index)` prop at line 16, correct
- `PopularRouteImageCard` — image `h-[200px]` (not 180px), white panel below, clean to copy
- `getStaticProps` — passes entire `frontPageData` object; backend adding `popular_experiences[]` = automatic frontend passthrough, no new fetch code
- `/activities/detail/[...slug].js` — catch-all route, works for single slug

---

## Backend Findings (corrected)

**Models ready:**
- `operators/models.py` — `Contract`: `booked_count`, `service_category`, `is_actived`, `name`, `slug`
- `average_rating` — computed via ContractSerializer method (ContentType + Review aggregation), NOT stored field
- **No `featured_image`** — use ImageGallery relationship (`imagegallery_set.first()`)

**Experience categories (correct filter):**
`DAY_TOUR`, `MULTI_DAY_TOUR`, `SPA_WELLNESS`, `EVENT_TICKET`, `ATTRACTION_TICKET`, `FOOD_DINING`
Exclude: `TRANSPORTATION`, `TRANSFER`, `ACCOMMODATION`

**API extension path:**
- `products/serializers.py` — new `PopularExperienceSerializer` (standalone `ModelSerializer`, NOT HomeSerializer, NOT ContractSerializer)
- Fields: `['id', 'name', 'slug', 'service_category', 'image', 'min_price']` — nothing else
- `pages_info/views.py:189` — `_fetch_popular_experiences()` mirrors `_fetch_home_routes_data()` pattern
- Queryset: `Contract.objects.filter(...).prefetch_related('imagegallery_set').order_by('-booked_count')[:limit]`
- Add to `response_data` dict in `list()` before `cache.set()`
- **NO new endpoint. NO new URL. NO new model. NO migration.**

---

## Frontend Findings (corrected)

**Reuse unchanged:**
- `components/UI/CardCarouselContainer.js` — `renderCard(item, index)` prop, ready
- `components/UI/Section.js` — standard wrapper
- `lib/homepage/components/PopularRoutesSection.js` — **lib/ version** (clean template, accepts `routes` prop)

**Do NOT reuse:**
- `components/activities/browse/DayTripCard.js` — 255 lines, browse-page weight, too heavy
- `HomeSerializer` — wrong model (Route, not Contract)

**Create lightweight:**
- `components/UI/ExperienceCard.js` (~60 lines) — copy `PopularRouteImageCard.js` structure
  - Image `h-[200px]` top, white panel below: `service_category` badge (gray), `name` h3 (line-clamp-2), "From THB {min_price}"
  - NO rating. NO booked count.
  - Link to `/activities/detail/${item.slug}`

**SSR pattern:**
- No RTK Query needed
- `getStaticProps` already passes `frontPageData` object through — adding `popular_experiences[]` to backend response is sufficient. Frontend just destructures + passes as prop.

---

## Implementation (When Ready)

### Gate: Inventory Check
```bash
python manage.py shell -c "
from operators.models import Contract
from django.db.models import Count
EXPERIENCE_CATS = ['DAY_TOUR','MULTI_DAY_TOUR','SPA_WELLNESS','EVENT_TICKET','ATTRACTION_TICKET','FOOD_DINING']
print(Contract.objects.filter(is_actived=True, service_category__in=EXPERIENCE_CATS).values('service_category').annotate(n=Count('id')))"
```
Require ≥6 total. Stop if not.

### Files to Touch (5 files, ~160 lines)

| File | Change |
|------|--------|
| `products/serializers.py` | Add `PopularExperienceSerializer` (after ContractSerializer, ~25 lines) |
| `pages_info/views.py` | Add `_fetch_popular_experiences()` + wire to response_data (~12 lines) |
| `lib/homepage/components/ExploreExperiencesSection.js` | New — copy lib/PopularRoutesSection (~60 lines) |
| `components/UI/ExperienceCard.js` | New — copy PopularRouteImageCard (~60 lines) |
| `pages/homepagev2.js` | Destructure `popular_experiences` + add section after line ~347 (~4 lines) |

### Placement
After `<PopularRoutesSection>` (~line 347), before `<ReviewsSection>`. Discovery flow: transport → experiences → social proof.

### Empty State
Hide section entirely if `!experiences?.length`. No empty UI.

---

## Blockers / Prerequisites

1. **AT-1 first** — Airport Transfer redesign (open P0 on `260528-feat/header-redesign-2026`)
2. **Inventory check** — verify ≥6 experience contracts before any code
3. **New branch** — after AT-1 merges to `main`

Image strategy locked: Option A (gallery method field, no migration). No longer a blocker.

---

## Related
[[homepage-ux-review-2026-05-21]] [[smartenplus-uxui-redesign-research-2026]] [[airport-transfer-redesign-2026]] [[recommendation-system]] [[tour-system-status]]
