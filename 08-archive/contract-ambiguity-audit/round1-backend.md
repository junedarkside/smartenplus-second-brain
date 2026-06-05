# R1 Backend Audit — Contract model: location, pickup, stops

**Repo:** `/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-backend/`
**Date:** 2026-06-03
**Author:** Backend Analyst (read-only research)

---

## Scope of Investigation

Mapped the `Contract` model from schema → serializer → viewset → URL, then traced:
- `meeting_point_type` / `meeting_point_details` / `meeting_point_place` (Contract)
- `primary_location` / `service_areas` (Contract)
- `pickup_point` / `pickup_time` (CartItemCheckoutInfo) and `InfoField` lookup keys
- `Place` (stations) used as FK target for `meeting_point_place`

Two viewsets:
- **Public** `ContractViewSet` → `apis/urls.py:38` (`/contract/`) — `products/views.py:357`
- **Admin** `ContractViewSet` → `operators/urls.py:40` (`/admin-dashboard-operators/contracts/`) — `operators/views.py:95`

---

## Findings

| ID   | Sev | File:line                                | Finding |
|------|-----|------------------------------------------|---------|
| B-1  | P1  | `operators/models.py:380` and `:1095`     | `meeting_point_details` is defined on **both** `Contract` and `ContractTranslation`. Both were added in the same 24h window (2026-01-25) — migration `0045_add_tour_fields.py` (parent field) and `0049_contracttranslation.py` (i18n child field). This is the **standard Django i18n pattern** (translatable fields live on a Translation child with a `get_localized_field()` resolver), not a copy-paste bug. **However**, the public `ContractSerializer` (line 154) exposes only the parent field, while the public `ContractDetailSerializer` does not currently call `get_localized_field()` for `meeting_point_details` — translations are returned as a separate `translations` array the frontend must join. The frontend probably picks the parent field and never reads `translations[].meeting_point_details`, which silently drops the translation. |
| B-2  | P1  | `operators/serializers.py:170-178`       | **Public list serializer omits `primary_location` and `service_areas`.** `ContractSerializer.Meta.fields` (line 172) lists 24 fields but skips both. Only `ContractDetailSerializer` (line 558-560) exposes them via `LocationSerailizer()`. Consequence: the public `/contract/` list endpoint, which **filters on both fields** (see B-4), cannot tell the client which locations a contract actually matched on. The frontend must call the detail endpoint (or `/contract/locations/`) to learn anything about the contract's location. |
| B-3  | P0  | `operators/models.py:225-415`            | **No DB constraint, no model `clean()`, no signal enforces category-vs-field consistency.** `Contract.service_category` (added 0045, default `TRANSPORTATION`) has 10 choices (TOUR/TICKET/FOOD/etc.) but nothing prevents a `DAY_TOUR` contract from having `meeting_point_type='HOTEL_PICKUP'` set, or a `TRANSPORTATION` contract from having `service_areas` populated. The only category-aware logic is in `operators/views.py:1067-1102` (create flow), which special-cases transport categories to require a `trip` and disallow some fields. Existing data is unconstrained — admin can create a `SPA_WELLNESS` with `primary_location` and `service_areas` set, and there's nothing in `signals.py` or `validators.py` to block it. **Customer-visible risk:** search results may include tour categories that get filtered with transport semantics, producing empty `meeting_point_*` on day-tour detail pages. |
| B-4  | P1  | `products/views.py:458-475`              | **Public `/contract/` location filter unions both fields.** The filter is: `Q(service_areas__id__in=ids) \| Q(primary_location__id__in=ids)` with a text fallback to `location_name`/`city`/`province` on **both** relations. Combined with B-2, the API can rank contracts by location relevance but cannot tell the client *which* field matched. The `/contract/locations/` action (line 555) likewise unions `primary_ids \| service_ids` and returns them as a flat deduped list — losing the distinction between "primary" and "service-area" matches. |
| B-5  | P2  | `operators/views.py:178-209`              | **Admin `ContractViewSet` has a different filter surface than the public one.** Priority order is `departure_location` + `arrival_location` (joined through `trip.route.*station.location_name`) → `location` (line 209+, on `primary_location`/`service_areas`) — but only the public viewset's `location` clause is documented; the admin's `location` clause is on line 209 and was not visible in the first 230-line read. Two viewsets, two semantics: public is `primary_location ∪ service_areas`; admin is `trip.route.station.location_name` ∪ `primary_location ∪ service_areas`. Staff viewing admin sees different results from the public site. |
| B-6  | P2  | `operators/models.py:182-216`             | **Fact-correction on the explorer's claim:** `InfoField` does **not** use lowercased `pickuppoint` / `pickuptime`. The actual constants (lines 183-184) are `PICKUP_POINT = 'pickup_point'` and `PICKUP_TIME = 'pickup_time'` (snake_case). The DB column is a single `field_type` CharField with the value as a *string*; the underscore is part of the value. The frontend-side mapping in `infoFields` Redux is probably building lookup keys like `info.field_type === 'pickup_point'` and matching the snake_case string — any frontend code that does `'pickuppoint'` (no underscore) will silently never match. Worth verifying against the frontend's checkout info builder. |
| B-7  | P2  | `carts/models.py:111-157`                | `CartItemCheckoutInfo.pickup_point` (CharField) and `pickup_time` (TimeField) are the **persisted checkout form data**, with parallel `dropoff_point` / `dropoff_time` fields. These are *not* contract fields — they are guest-supplied values stored per cart item. The frontend then maps them onto `InfoField` rows (using the snake_case `field_type` keys from B-6) when calling `create-infofields`. There is no server-side validation that the contract's `info_fields` M2M actually contains a `pickup_point` row before persisting — the frontend decides. If a TRANSPORTATION contract has `info_fields` empty, the form still saves `pickup_point="Hotel Lobby"` into `CartItemCheckoutInfo` but never into the booking `InfoField` answer, leading to missing pickup info on the booking confirmation. |
| B-8  | P2  | `operators/models.py:385-392`            | `meeting_point_place` FK uses `'stations.Place'` but the import in the file (`from stations.models import ... Place`) would work — the string ref is just lazy resolution. **No validation** that `meeting_point_place.location` matches `primary_location`. Admin can set a `meeting_point_place` in Bangkok while `primary_location` is Chiang Mai. Surface-level cosmetic in admin, but the public `ContractDetailSerializer` exposes both as nested objects — clients see conflicting cities. |
| B-9  | P2  | `operators/views.py:801-822`             | Admin PATCH for `primary_location` (line 802-809) and `service_areas` (line 819-822) does **not** validate that the location exists or that the M2N list contains valid IDs — it just calls `Location.objects.get(id=primary_location)` and lets it 404 on bad input, with no try/except. A malformed admin request returns 500 instead of 400. |

---

## What Works

- **i18n pattern is sound.** `ContractTranslation` is properly keyed on `(contract, language)` with `unique_together` (models.py:1104) and the `get_localized_field()` resolver (serializers.py:571-599) implements the correct fallback chain (requested lang → English → original). This is a strong foundation; it's just under-used for `meeting_point_details`.
- **Public location filter is OR-union by design** (products/views.py:462-465) — covers both "tour operates from X" and "tour goes to X" search intents in one query. Better than forcing a single semantic.
- **Pagination is consistent** between public and admin (`CustomPagination`, same `page_size` semantics).
- **Caching has a sane key** (products/views.py:392) that includes sorted query params + page + page_size.
- **Migration discipline is clean:** 0045 introduced all tour fields (service_category, primary_location, service_areas, meeting_point_*) in one cohesive change. No half-migrated state.

---

## Open Questions

1. **Does the frontend `Contract` RTK Query cache** expect `primary_location` / `service_areas` on the list response? If yes, B-2 is a customer-visible bug (location-search results missing the field that was used to find them). If no, B-2 is purely a documentation gap.
2. **Is the `translations` array actually consumed** by the frontend booking flow for `meeting_point_details`? Or is the parent field used directly, dropping translations? (Need frontend audit to confirm.)
3. **Is there a UX reason `service_areas` is plural M2M** while `primary_location` is a single FK? It looks like an "areas served" vs "main hub" distinction, but the public filter and the `/contract/locations/` action flatten both into a single set — losing the hub/area distinction in the API response. Should the response keep them separate?
4. **What's the intended category for `meeting_point_type`?** All three choices (HOTEL_PICKUP / MEET_ON_LOCATION / SPECIFIC_POINT) are valid for tours AND transportation, but `meeting_point_place` (the `stations.Place` FK) is most natural for a SPECIFIC_POINT. Are there any contracts in the DB with `meeting_point_type=HOTEL_PICKUP` and `meeting_point_place` set? (Need a data query to confirm.)
5. **Why does the admin `ContractViewSet` prioritize `departure_location` + `arrival_location` filters** (operators/views.py:180-208) that the public viewset doesn't expose? Are these admin-only search affordances, or is the public viewset missing a feature?
6. **Is `meeting_point_details` (parent field) still being written to** by the admin, or has it been superseded by `ContractTranslation.meeting_point_details`? The admin PATCH at operators/views.py:792 still writes to it. If translations are now authoritative, the parent field is dead but kept for backward-compat — should be marked `deprecated` in `help_text`.

---

## Cross-Repo Implications

- **`admin-dashboard`** will be affected by B-3 (no validation), B-8 (no cross-field check), B-9 (no try/except). Staff creating TRANSPORTATION contracts with `service_areas` set will succeed, and 500s on bad IDs will surface in the admin UI.
- **`smartenplus-frontend`** is most affected by B-2 (list response missing fields) and B-6 (InfoField lookup key case). Need to verify the frontend Redux/Formik code expects snake_case keys.
- **No DB migration needed** to fix any of these — all are serializer/viewset/model-`clean()` changes, plus documentation.
