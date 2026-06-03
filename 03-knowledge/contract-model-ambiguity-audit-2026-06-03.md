# Contract Model Ambiguity — Team Audit 2026-06-03

## Summary

Multi-repo audit of the `Contract` model fields that govern customer location discovery and operator-declared meeting/pickup points: `primary_location`, `service_areas`, `meeting_point_*`, the per-trip `InfoField` casing sprawl, and the `Trip.route` vs `timeline_place` split. 4 rounds (R1 backend/frontend/domain, R2 cross-exam, R3 skeptic) read `smartenplus-backend`, `smartenplus-frontend`, `admin-dashboard`, and the vault. **6 conceptual overlaps confirmed; 1 is customer-visible today (i18n on `meeting_point_details`); 5 are staff-side or dormant.** Recommendation posture: **document + 1 small backend fix, no model consolidation.** The model shape is right; the help text, admin UX, and i18n resolver are not.

## Context

- **Trigger:** staff confusion reported after the 2026-06-01 OR-fix ([[activities-location-search-bug-2026-06-01]] Debate 3) — `primary_location` was added to the location filter, contradicting the admin help text. The 2026-06-01 audit did not resolve the underlying field-intent question.
- **Audit surface:** `operators/models.py:380-415`, `operators/serializers.py:170-178, 558-560`, `operators/views.py:178-209, 1067-1102`, `products/views.py:355-475, 555-588`, `products/serializers.py:518-587`, `carts/models.py:111-157`, `carts/utils.py:235-260, 330-371`, `bookings/models.py:151-180`, `smartenplus-frontend/components/forms/checkout/Passengers.js:259-275, 531-537, 1091`, `smartenplus-frontend/helpers/checkoutPersistence.js:179-194, 421-427`, `smartenplus-frontend/components/bookings/BookingDetail/ServiceDetail.js:35`, `smartenplus-frontend/components/activities/detail/DayTripDetailPage.js:202`, `smartenplus-frontend/store/api/dayTripsApi.js:128-133`, `admin-dashboard/components/contracts/ContractFormFields.js:176-261`.
- **Repos affected:** `smartenplus-backend`, `smartenplus-frontend`, `admin-dashboard`. **No code changes recommended in this report** — actions are recommendations for separate work.

## Current State Map

### Schema (Backend)

| Field | Model | Type | Categories where set | Public API exposure |
|-------|-------|------|----------------------|---------------------|
| `primary_location` | `Contract` (`operators/models.py:402-409`) | FK `stations.Location`, nullable | All non-transport | Detail: yes. List: **omitted** (`operators/serializers.py:170-178`) |
| `service_areas` | `Contract` (`operators/models.py:411-414`) | M2M `stations.Location`, nullable | All non-transport | Detail: yes. List: **omitted** |
| `meeting_point_type` | `Contract` (`operators/models.py:380`) | enum HOTEL_PICKUP/MEET_ON_LOCATION/SPECIFIC_POINT | All non-transport | Detail: yes. Form: yes |
| `meeting_point_details` | `Contract` + `ContractTranslation` (`operators/models.py:385-392, 1095`) | TextField | All non-transport | Detail: yes. **Translation unwired** |
| `meeting_point_place` | `Contract` (`operators/models.py:385-392`) | FK `stations.Place`, `db_constraint=False` | SPECIFIC_POINT only | Detail: yes. Form: yes. Tests use it |
| `Trip.route.route_name` | `Trip` → `Route` | TextField | TRANSPORTATION | All transport read paths (25+ call sites) |
| `Trip.route.departure_station` / `arrival_station` | `Trip` → `Route` → `Place` | FK | TRANSPORTATION | Search + cart + PDP |
| `timeline.timeline_place` | `Timeline` | M2M `Place` | DAY_TOUR + MULTI_DAY_TOUR | PDP only (`DayTripDetailPage.js:200-203`) |
| `CartItemCheckoutInfo.pickup_point` | `carts/models.py:111-157` | CharField | Transport guest input | Saved in `carts_checkout_info` |
| `InfoField.pickup_point` (schema enum) | `operators/models.py:183-184` | CharField with constant `pickup_point` | Per-contract M2M | Wire: snake_case in `field_type` |
| `InfoFields.pickuppoint` (persistence) | `bookings/models.py:151-180` | CharField column | Persisted booking | Wire: **lowercase, no underscore** |

### UI Consumption (Frontend + Admin)

| Surface | Field(s) fed | What user sees |
|---------|--------------|----------------|
| Search facet chip | `service_areas` ∪ `primary_location` (post-2026-06-01 OR-fix) | Location pills on `/activities` |
| Autocomplete dropdown | `primary_location` ∪ `service_areas` distinct (`products/views.py:574-585`) | Flat `{location_name, province}[]` |
| PDP hero | **none of these fields** — no component reads `primary_location` | City name (unverified) |
| PDP meeting point | `meeting_point_type` + `meeting_point_details` | `MeetingPointCard.js:7-31` label + text |
| Tour timeline | `timeline.timeline_place` (DAY_TOUR + MULTI_DAY_TOUR) | `DayTripDetailPage.js:200-203` + `TimeLineDisplay.js` |
| Transport route | `Trip.route.route_name` + stations | 25+ call sites (TripDetail2/3, FilteredTripList, OrderPrint) |
| Checkout form input | `InfoField.field_type` schema (snake_case) | Formik `pickupPoint` (camelCase) |
| Booking detail | `InfoFields.pickuppoint` (lowercase) | `BookingDetail/index.js:127-141` + `PdfView.js:189-220` |
| Admin form | `primary_location` + `service_areas` + meeting point + place | `ContractFormFields.js:176-261` |

### API Filtering

| Viewset | Location fields filtered | Source |
|---------|--------------------------|--------|
| Public `ContractViewSet` (`products/views.py:355, 458-475, 555-588`) | `service_areas` ∪ `primary_location` (OR, post-2026-06-01) + text fallback | Public list + autocomplete |
| Admin `ContractViewSet` (`operators/views.py:95, 178-209`) | `trip.route.*station.location_name` + `primary_location` + `service_areas` (priority order) | Admin internal |

## Discrepancies — Debate Table

| ID | Topic | Backend (R1/R2) | Frontend (R1/R2) | Domain (R1/R2) | Skeptic (R3) | Resolution |
|----|-------|------------------|--------------------|------------------|----------------|------------|
| **D1** | `primary_location` vs `service_areas` overlap | B-2: list omits both; B-4: filter unions both. R2 confirms omission is payload-size, not bug | F-02: zero customer consumers. R2 confirms with grep — no `primary_location` in `smartenplus-frontend/components/` | D-1: help text says "not for search", D-3: intent unstable across 3 docs. R2: customer impact = 0 | S-5/S-6: reinforce the conflict. S-6 concrete: `primary_location` is the deletion candidate | **Keep both. Fix help text. Defer deletion pending data inventory.** Field semantics are valid (HQ vs service radius), but help text lies. Staff surprise is real; customer impact is zero today |
| **D2** | Pickup data path sprawl | R2: 3 distinct casing systems (`pickup_point` enum, `pickuppoint` wire, `pickupPoint` Formik). Server-side converter in `carts/utils.py:235-260` | F-01: 4 paths. R2 refute: 1 input + 3 read + 1 dead backup. F-04: casing asymmetry | R2: 2 casing systems, 1 read inconsistency | S-9: refutes F-01 overcount. S-10: refutes F-04 P0 — doc gap, not bug | **P3 doc gap.** Server-side `extract_trips_info` is the SSOT. Round-trip works. Comment asymmetry (`arrivalFlighttime` documented, `pickuppoint` not) is the only customer-adjacent cost |
| **D3** | `pickuppoint` casing — **3 agents genuinely disagreed** | R1 B-6: schema enum is snake_case `'pickup_point'` (verbatim) | R1 F-01: wire format is lowercase `'pickuppoint'`. R1 F-04: asymmetry with `arrivalFlightTime` | R2: lowered to P3, doc gap | S-10: refutes P0 framing, not the casing itself | **LOWERCASE WINS for the wire format** (verified: `bookings/models.py:151-180` columns are `pickuppoint`/`pickuptime`/`extrainfo`; `carts/utils.py:248` `to_dict()` returns `'pickupPoint'` for cart-save; `carts/utils.py:235-260` `extract_trips_info` does camelCase→lowercase conversion). **The schema enum `pickup_point` is a separate concept (lookup key) that never appears in the booking detail wire format**. The F-04 "arrivalFlightTime" comment is misleading — actual wire key is all lowercase, no underscores |
| **D4** | `meeting_point_place` alive? | R1 B-8: "dead-ish, no validation" | R2: out of scope, admin-only | R2: P3, cosmetic | **S-2 OVERTURN**: migration 0052 modified it (`db_constraint=False`); `operators/admin.py:1034, 1093`; tests at `operators/tests.py:139, 247, 263, 453, 456`; serializer at `operators/serializers.py:560`; clone at `operators/views.py:985`; `docs/features/TOUR_SYSTEM.md:482` | **ALIVE. Keep.** Cross-field validation gap (`meeting_point_place.location` vs `primary_location`) is the real P2 admin-UX issue |
| **D5** | `Trip.route` alive? | n/a (transport shape) | R1 F-10 / R2: "stops not observable" | n/a | **S-1 OVERTURN**: 25+ call sites — `OrderPrint.js:52`, `BookButton.js:129`, `SearchHeader.js:13`, `TripDetail2.js:159`, `TripDetail3.js:208-230`, `tripdetail.js:92-149`, `FilteredTripList.js:37-97`, `CartDetailDisplay.js:238`, etc. The dead thing is the `showStations` config flag, not the data | **ALIVE. Heavily used.** R2 misread F-10 (which was about `stops`, not `Trip.route`). Delete the `showStations` config flag (P2 cleanup) |
| **D6** | `timeline_place` vs `trip stops` overlap | R1 B-3: no category/field enforcement at DB level | R1 F-05: matrix in `serviceCategoryHelper.js:17-99` is the only render-gate. If both populated, `showRoute=false/showTimeline=true` wins silently | D-7: both fields added in same 2026-01-25 migration — designed together | n/a (no direct S-N) | **Renders are mutually exclusive by category config, not data.** A contract with both populated shows timeline only. P2 hardening: add server-side `clean()` to reject this state. Not a customer bug today |

## Recommended Actions

| P# | ID | Action | Owner | ETA | Risk |
|----|----|--------|-------|-----|------|
| **P0** | D1 | Fix admin help text in `admin-dashboard/components/contracts/ContractFormFields.js:184` — change "Not used for customer location search" to "Used in customer location search (OR'd with service_areas) since 2026-06-01 fix". Mirror in `:227` for `service_areas`. 1 PR, ~10 lines | admin-dashboard team (A) | 1 day | None — text change |
| P1 | D2 | Write 1-paragraph ADR covering the 3 casing systems + the server-side `extract_tops_info` SSOT. Add cross-link from `checkoutPersistence.js:179-194` and `Passengers.js:531-537`. Eliminates the comment asymmetry | backend lead (B) | 1 day | None — docs |
| P1 | B-1 | Wire `get_translated_meeting_point_details` `SerializerMethodField` on `ProductDetailSerializer` (mirror `get_translated_inclusions` at `products/serializers.py:518-522, 569-587`). Closes `DayTripDetailPage.js:202` silent-fallback to parent (untranslated) field. Blocked on translation-management UI existing | backend (B) + frontend (C) | gated on product | Low — additive |
| P1 | B-7 | Add model `clean()` on `Contract` rejecting creation of a non-transport contract with `meeting_point_type=HOTEL_PICKUP AND service_areas=[] AND primary_location=NULL`. Defense-in-depth — form already gates (`ContractFormFields.js:177, 220`), but a bulk-import or shell bypass could break this | backend (B) | 1 PR, ~15 lines | Low — narrows invalid states |
| P2 | B-9 | Wrap admin PATCH `Location.objects.get(id=primary_location)` in `try/except → 400` at `operators/views.py:802-809, 819-822`. Staff error quality | backend (B) | 1 PR, ~10 lines | None |
| P2 | F-10 | Delete dead `showStations` config flag in `serviceCategoryHelper.js:23`. Replace with direct `getServiceCategoryConfig()` consumers | frontend (C) | 1 PR, ~5 lines | None — dead code |
| P2 | S-Q4 | Run data inventory: `SELECT primary_location_set, service_areas_set, COUNT(*) FROM operators_contract WHERE is_actived GROUP BY 1, 2`. Determines whether `primary_location` deletion is viable in 6 months | backend/data (B) | 1 SQL + 1 report | None — read-only |
| Backlog | B-3 | Add cross-field validation: `meeting_point_place.location == primary_location` if both set. Real admin UX issue, not customer bug | backend (B) | gated on category model cleanup | Low |

## Open Questions for Staff

1. **City search:** When a customer types "Phuket" into the search bar, should the dropdown say "Phuket" or "Phuket — 3 tours" or "Phuket — 2 tour operators"? Today it just says the city name.
2. **Tour card city label:** Below each tour's title on the listing page, do you want to show the city where the operator is based, the city where customers get picked up, or both? Today neither is shown on the customer card.
3. **Tour detail page header:** Should the "Phuket" label on a tour's detail page come from the operator's office address, from the pickup zone, or from a separate "where this tour operates" field?
4. **Tour translations:** When the Thai-language site launches, should tour descriptions be translated by a translator we hire, by AI, or stay English-only and the team re-writes them later?
5. **Bangkok tour operator in Phuket:** A Phuket tour is run by a Bangkok-based company. Should the tour show up when customers search "Bangkok" (operator's base) or "Phuket" (tour location) or both? Today it shows in both, and there's no way to tell which is which.

## Tradeoffs

| Decision | Chosen | Skipped |
|----------|--------|---------|
| `primary_location` deletion | **Deferred** — data inventory first (P2 S-Q4). Risk of silent removal of admin-side metadata | Delete now — saves one form field but loses the legitimate "operator HQ" concept (R3 Q2) |
| `Trip.route` rename / consolidation | **No change** — 25+ customer read sites; rename is 6-week migration | Consolidate route + timeline into one polymorphic field — would touch every trip-related component |
| Casing system unification (`pickuppoint` → `pickup_point`) | **Keep shim** — server-side `extract_trips_info` is 1 function in 1 file; round-trip works; 1 migration + 2 serializers + 4 read sites + 2 test files for cosmetic gain | Rename — high cost, no behavior change |
| i18n resolver for `meeting_point_details` | **Wire SerializerMethodField now** (1 line, additive) | Wait for translation UI — dormant for Thailand today |
| Help text fix scope | **Two-line text edit** in `ContractFormFields.js:184, 227` | Full admin UX redesign (required marker, hierarchy, per-category help) — 1-2 week effort |
| Server-side `clean()` for category/field invariants | **Defer until form is bypassed in production** — form is the only write path today | Add now — defense-in-depth without observed failure |

## Consequences

**If all P0/P1 actions land:**
- Staff creating a new contract will not be surprised when a `primary_location`-only contract appears in location search (help text matches code).
- Non-English customers viewing the PDP will see the translated meeting point text instead of the English parent field.
- A bulk-import or admin shell bypass creating an invalid `meeting_point_type + service_areas + primary_location` combination will fail at `model.clean()` instead of producing a broken PDP.
- Documentation: 1 ADR + 1 line per file removes the "3 casing systems" ambiguity in 3 places.

**If actions are deferred:**
- The help text remains stale. New staff continue to set `primary_location=Phuket` for "display only" and are surprised when the contract appears in Phuket searches. Recoverable but recurring.
- The 12-language i18n table at `[[operators]]:44` ships with the resolver still unwired. The first translated contract will silently render English.
- `Trip.route` stays alive but the `showStations` config flag stays dead, confusing future readers.
- `primary_location` and `service_areas` intent remains split across 3 documents (admin help, model comment, 2026-06-01 bug audit). New staff can't tell which doc is canonical.

## Related

- [[contract-serializer-non-transport-fields-2026-06-03]] — companion: missing fields on `ContractSerializer`
- [[contract-trip-null-non-transport-pattern]] — companion: `trip=None` guard pattern
- [[admin-dashboard-contracts]] — visibility matrix source; primary_location row at line 24
- [[activities-location-search-bug-2026-06-01]] — Debate 3 (this audit's trigger); OR-fix at `products/views.py:462-465`
- [[operators]] — `Contract`, `ContractTranslation`, 12-language registry
- [[stations]] — `Location`, `Place`, `Timeline` models
- [[transportation-category-audit-2026-05-30]] — Level-1/2 category classification
