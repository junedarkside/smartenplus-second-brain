# R2 Backend Cross-Exam

**Role:** Backend Analyst
**Date:** 2026-06-03
**Scope:** Cross-examine R1 Frontend (F-01..F-10) and R1 Domain (D-01..D-10) findings against the backend source.

---

## On Frontend (F-N)

### F-01: Refine (the contradiction is real, but the description conflates 3 different casing systems)

Peer claim: "Free-text textarea is gated by `info_fields` schema (`field_type === "pickup_point"` → camelCase `trip.pickupPoint`); the same data is then *stored* in `info_fields.pickuppoint` (lowercase)."

The contradiction with my B-6 is real, but the truth is more nuanced: there are **three independent casing systems** for the same data, and both peer and I were partially right.

| Layer | Casing | Where defined | Evidence |
|-------|--------|---------------|----------|
| `InfoField.field_type` (the enum) | `pickup_point` (snake_case) | `operators/models.py:184` `PICKUP_POINT = 'pickup_point'` | My B-6 cited this correctly |
| `InfoFields` (note: **plural** — different model!) DB column + wire payload | `pickuppoint` (lowercase, no underscore) | `bookings/models.py:171` `pickuppoint = models.CharField(...)`; `carts/utils.py:350` `pickup_point = trip.get('pickuppoint')` | Peer was right about this layer |
| Frontend **Formik shape** (in-memory form state) | `pickupPoint` (camelCase) | `Passengers.js:1091` `name={`trips.${fieldIndex}.pickupPoint`}`; `checkoutPersistence.js:181` `pickupPoint: trip.pickupPoint` | Peer was right about this layer too |

The frontend switch at `Passengers.js:261` and `:503` uses `case "pickup_point":` (snake_case) to **match the enum string** returned in the `field_type` field. This is *not* the same key as the wire payload `pickuppoint` (lowercase). Both keys coexist and are correct in their respective contexts.

**The actual bug is the conversion step at the API boundary**: `create_info_fields` (`carts/utils.py:330-371`) reads `trip.get('pickuppoint')` (lowercase) and the frontend must send lowercase keys in `trips_payload`. The form state uses camelCase internally, so the conversion happens in some builder — let me note this as an unverified assumption since I did not find the explicit `pickupPoint` → `pickuppoint` mapping in `helpers/getBillingAndOrder.js`. **The Q1 from F-01's open questions is therefore still open.**

### F-02: Refine (claim is true, but implication differs from the audit's framing)

Peer claim: "`primary_location` is admin-only — never rendered to a customer."

**Verified.** `grep -rn "primary_location\|service_areas\|primaryLocation\|serviceAreas" smartenplus-frontend/components` returns **zero hits** in customer-facing components. The fields are referenced only in the admin-dashboard (`/Users/charuwatnaranong/Desktop/AdminDashBoard/admin-dashboard/components/utils/contractUtils.js:88-91` does the snake_case↔camelCase conversion for the admin POST payload). The customer frontend never reads these fields from a contract object.

**Refinement:** the audit's implication that this is a "stale field, or undocumented role" is **partly wrong** — the field is not stale, it is **deliberately invisible to customers**. The reason is: the customer uses the `/contract/locations/` autocomplete endpoint (`products/views.py:555-588`) for location filtering, which returns a flat list and abstracts away the `primary_location`/`service_areas` distinction. The fields are an admin/filter concern only. This is consistent with B-2's omission from the public list serializer — it's intentional, not a bug.

### F-03: Refine (the `DAY_TOUR` default lives in BOTH places, not just the RTK Query hook)

Peer claim: "`getActivityLocations` ... `service_category=DAY_TOUR` is hard-coded to DAY_TOUR as default" (Q6, Q7).

**Verified, with refinement.** The `DAY_TOUR` default appears in **two places**:

1. Frontend RTK Query hook: `smartenplus-frontend/store/api/dayTripsApi.js:129` `({ serviceCategory = 'DAY_TOUR' } = {})` — peer's claim
2. Backend viewset: `smartenplus-backend/products/views.py:562` `service_category = request.query_params.get('service_category', 'DAY_TOUR')` — peer missed this

So the dropdown hard-codes to DAY_TOUR even if the caller sends `?service_category=SPA_WELLNESS` — because **no caller currently passes anything other than DAY_TOUR**. The frontend consumer `ActivitySearch.js:40-42` does pass `filters.category` when present, but `filters.category` defaults to `DAY_TOUR` upstream in the day-trip browse filter (per the F-03 Q6 / Q7 framing).

**Net effect:** MULTI_DAY_TOUR, SPA_WELLNESS, FOOD_DINING, etc. never appear in the location autocomplete. This is a **double-fault** — fixing only the frontend hook would not help, because the backend would still default to DAY_TOUR if the hook sent `undefined`.

### F-04: Refine (the "two casing systems" framing is correct but the example is misleading)

Peer claim: "Form input uses camelCase (`pickupPoint`, `arrivalFlighttime`, `dropoffPoint`) per Formik shape. The auto-save normaliser (checkoutPersistence.js:179-194) emits `pickupPoint` to Redux but explicitly maps `arrivalFlighttime` → `arrivalFlightTime` (capital T) for the backend."

**Verified for the read/display path** — `Passengers.js:531-537` has the explicit `arrivalFlightTime` → `arrivalFlighttime` reverse mapping.

**Refinement on the wire format:** the **backend `create_info_fields`** (`carts/utils.py:330-371`) does **not** expect `arrivalFlightTime` (capital T) — it expects `arrivalflighttime` (all lowercase, no underscore). So the comment in `Passengers.js:531-533` ("Backend stores arrivalFlightTime (capital 'T'), frontend uses arrivalFlighttime (lowercase 't')") is **misleading** — the actual wire key is **all lowercase, no underscores at all**. This is the same casing system as the F-01 "pickuppoint" case. The peer's F-04 framing implies the discrepancy is `camelCase` ↔ `PascalCase` between form and backend, but the actual discrepancy is `camelCase` ↔ `lowercase_no_underscore` for ALL info-field keys (not just `arrivalFlighttime`).

### F-05: Confirm (timeline vs route gating is hard-coded in the config, not via data)

`helpers/serviceCategoryHelper.js:17-99` `SERVICE_CATEGORY_CONFIG` matrix — `showRoute: true, showTimeline: false` for TRANSPORTATION; `showRoute: false, showTimeline: true` for DAY_TOUR/MULTI_DAY_TOUR; both `false` for SPA, FOOD, EVENT, ATTRACTION, ACCOM, OTHER. **No data-driven branch.** If a contract has both `timeline.timeline_place` AND `trip.route.route_name` populated, the `showRoute=false/showTimeline=true` flag wins silently — the route is suppressed even though the data exists. Peer's claim is correct.

### F-06: Confirm (two autocomplete endpoints, two response shapes)

`useGetStationSuggestionsQuery` → `tripsApi.js:90-93` → `/stations/?search=` (raw `Place[]` array)
`useGetActivityLocationsQuery` → `dayTripsApi.js:128-133` → `/api/v1/contract/locations/?service_category=DAY_TOUR` (`{location_name, province}[]`)

No shared contract between the two. **Confirmed.**

### F-07: Confirm (two `TimelineDisplay` implementations in separate trees)

`components/itinerary/TimeLineDisplay.js` (customer read-only) and `components/draganddrop/TimeLineDisplay.js` (admin read+DnD) — **two files, same name pattern, different propTypes**. Customer requires `data: [{order, place:{name,google_url,image_gallery}, description}]` (PropTypes:291-313). Admin consumes `formik.values.dndCharacterData?.place` (F-07 Q5 raised the same concern). **Confirmed.**

### F-08: Confirm (three customer surfaces read `meeting_point_type` independently)

`components/bookings/BookingDetail/ServiceDetail.js:35` reads `contract?.meeting_point_details` (no translation fallback).
`components/activities/detail/DayTripDetailPage.js:202` reads `contract.translated_meeting_point_details || contract.meeting_point_details` (has fallback, but see B-1 below).
`components/activities/detail/MeetingPointCard.js:7-31` reads `meetingPointType` for the label.

**Confirmed**, with the **important refinement** that the second surface's `translated_meeting_point_details` field is **never populated by the backend** (see B-1 — `ProductDetailSerializer` is missing the `translated_meeting_point_details` method, only has `translated_inclusions`/`translated_exclusions`). So the fallback always wins and the translation is silently dropped.

### F-09: Confirm (commented shim for flight times, no comment for pickup)

`checkoutPersistence.js:387, 421-427` documents the `arrivalFlighttime` ↔ `arrivalFlightTime` reverse mapping. There is no equivalent comment for the `pickuppoint` ↔ `pickupPoint` casing shim. **Confirmed** — and the shim is more critical than the comment suggests because the wire format is `pickuppoint` (lowercase), not `pickuppoint` (camelCase) — see F-01 above.

### F-10: Confirm (no `stops` field is rendered to customers)

`grep -rn "stops"` against `smartenplus-frontend/components` returns no direct render paths. The config flag `showStations: true` for TRANSPORTATION (`serviceCategoryHelper.js:23`) is referenced via `shouldShowRoute`/`getServiceCategoryConfig` consumers, but the `stops` array (admin `TransportComposit`) is admin-only. **Confirmed.**

---

## On Domain (D-N)

### D-1: Confirm (the documented intent of `primary_location` is overridden by the OR-fix)

`products/views.py:462-465` (the OR-filter from the 2026-06-01 fix) treats `primary_location` as a search facet. The admin help text at `ContractFormFields.js:184` says `primary_location` is "**Not** used for customer location search". The two are in direct conflict. **Confirmed.** This is a documentation/code drift, not a backend-only issue.

### D-2: Refute (the model `help_text` is NOT "for upselling")

Peer claim: "The Django model `help_text` says 'for upselling' (`'Location-based fields for upselling'`)."

**Refute.** `operators/models.py:401` `help_text='Location-based fields for upselling'` does NOT exist verbatim. The actual text on `models.py:401-414` is:

```python
# Location-based fields for upselling
primary_location = models.ForeignKey(
    'stations.Location',
    ...
    help_text='Primary location for this tour/service'
)
service_areas = models.ManyToManyField(
    'stations.Location',
    ...
    help_text='Additional areas where this service operates'
)
```

The phrase "for upselling" is a **comment** above the fields (line 401), not the `help_text` argument. The `help_text` for `primary_location` is `'Primary location for this tour/service'` and for `service_areas` is `'Additional areas where this service operates'`. **The "for upselling" intent is a developer comment, not user-facing documentation.** The admin form's "for display and branding" claim is in tension with the developer comment but not the `help_text` itself.

**Severity unchanged** — there are still three contradictory framings (admin help, model help, model comment) — but the specific claim that the model `help_text` says "for upselling" is wrong.

### D-3: Refine (the "unstable intent" framing is correct, but the artifact location is partially wrong)

D-2 above refutes where the "for upselling" string lives. The rest of D-3 (intent unstable across three write-ups: the 2026-06-01 bug audit, the migration help_text, the admin form help text) is **correct in spirit but the artifact cited is wrong** — the migration `0045_add_tour_fields.py` does not contain "for upselling" either; the `help_text` arguments are "Primary location for this tour/service" and "Additional areas where this service operates".

### D-4: Confirm (no visual hierarchy between the two `LocationSelector` instances)

`ContractFormFields.js:176-261` — both `primary_location` and `service_areas` use the same `LocationSelector` component, no required asterisk, no color difference. **Confirmed.**

### D-5: Confirm (no per-category UX distinction for non-transport categories)

`ContractFormFields.js:176-261` shows both fields for all categories except TRANSPORTATION/TRANSFER. **Confirmed.**

### D-6: Confirm (the `/contract/locations/` endpoint unions both fields)

`products/views.py:574-585` — `primary_ids = contracts.filter(primary_location__isnull=False).values_list('primary_location_id', flat=True)` and `service_ids = contracts.exclude(service_areas__isnull=True).values_list('service_areas__id', flat=True)`, then `location_ids = set(primary_ids) | set(service_ids)` — the two fields are unioned and **the distinction is lost** in the response. **Confirmed.** The dropdown cannot tell the customer "this is a primary location" vs "this is a service area".

### D-7: Refine (the migration history is correct, but D-7's claim is too narrow)

`migrations/0045_add_tour_fields.py` does add both fields in the same operation. **Confirmed.** However D-7 frames this as "they were designed together for the day-tour feature launch" — I cannot verify the "designed together" intent from code alone; the migration only shows they were committed in the same `operations` block on 2026-01-25. The narrow claim is correct, the design-intent narrative is not provable from the migration file.

### D-8: Confirm (serializer exposes both fields for all categories)

`operators/serializers.py:558-559` `primary_location = LocationSerailizer()` and `service_areas = LocationSerailizer(many=True, read_only=True)` are defined on `ContractDetailSerializer` (which has `fields = '__all__'` at line 603), not gated by `service_category`. The serializer is generic. **Confirmed.**

### D-9: Confirm (`primary_location` is nullable, no required marker)

`operators/models.py:402-409` `primary_location = models.ForeignKey(..., null=True, blank=True, ...)` — **no `null=False`**. The admin form at `ContractFormFields.js:194-216` shows `LocationSelector` with no required indicator. The 2026-06-01 OR-fix at `products/views.py:462-465` will silently match nothing if both fields are null, producing empty search results rather than 400. **Confirmed.**

### D-10: Confirm (architectural critique)

`stations/models.py` `Location` is a city/province/country hierarchy, no spatial granularity. Both `primary_location` (FK) and `service_areas` (M2M) point at the same `Location` model. The single/fork distinction is the root cause of the ambiguity. **Confirmed** (file:line not in scope of this cross-exam — the architecture is what it is).

---

## Resolved Truths

1. **Pickup field casing is THREE systems, not two.** The `InfoField.field_type` enum is `pickup_point` (snake_case, with underscore) — matches F-01's `case "pickup_point":` correctly. The `InfoFields` DB column and `create-infofields` wire payload is `pickuppoint` (lowercase, no underscore) — matches the PDF/booking-detail display path. The Formik shape is `pickupPoint` (camelCase) — internal to the form. The peer's F-01 is **partly right**; my B-6 was **partly right**; the contradiction is the audit-summary oversimplification of a 3-layer system.

2. **`getActivityLocations` DAY_TOUR default is double-fault.** Both the frontend RTK Query hook (`dayTripsApi.js:129`) AND the backend viewset (`products/views.py:562`) default to `DAY_TOUR`. Neither has been changed. Fixing only the frontend is insufficient.

3. **Customer frontend never reads `primary_location` or `service_areas` on contract objects.** The B-2 (public list serializer omits these fields) is **not customer-visible** — but is a documentation/API contract gap rather than a customer UX bug. Future features that start consuming these fields will silently not find them in list responses.

4. **`ProductDetailSerializer` is missing `translated_meeting_point_details`.** `products/serializers.py:521-522` exposes `translated_inclusions` and `translated_exclusions` (with `get_translated_*` methods at lines 581-587) but **not** `translated_meeting_point_details`, even though `ContractTranslation.meeting_point_details` exists (`operators/models.py:1095`). The frontend's `DayTripDetailPage.js:202` fallback `contract.translated_meeting_point_details || contract.meeting_point_details` always picks the parent (untranslated) field for the customer-facing PDP. **B-1 is customer-visible** — translated `meeting_point_details` are silently dropped on the PDP.

5. **`operators/serializers.py` and `products/serializers.py` have two separate detail serializers with inconsistent translation support.** `ContractDetailSerializer` (admin) has a generic `get_localized_field()` method (line 571-599) but does not wire it up. `ProductDetailSerializer` (customer) has hard-coded `translated_inclusions`/`translated_exclusions` (line 581-587) but not `meeting_point_details` or `what_to_bring`. The two serializers evolved independently.

6. **"For upselling" is a comment, not `help_text`.** `operators/models.py:401` is a developer comment, the actual `help_text` arguments are `'Primary location for this tour/service'` and `'Additional areas where this service operates'`. D-2 cited the wrong artifact.

7. **Service-category config matrix (`serviceCategoryHelper.js:17-99`) is the **only** place render-gating lives.** Two `TimelineDisplay` files (F-07), two autocomplete endpoints (F-06), three `meeting_point_*` read sites (F-08) all depend on this matrix. Any category flip mid-lifecycle silently changes what the customer sees.

---

## New Questions Surfaced

1. **Where is the camelCase→lowercase conversion for the `trips_payload` argument to `create_info_fields`?** The frontend form state is `pickupPoint` (camelCase) but the wire payload must be `pickuppoint` (lowercase). The conversion must happen somewhere between the Redux checkout state and `helpers/getBillingAndOrder.js:318` `axios.post('/create-infofields/', { trips_payload })`. **I could not find the conversion function** — it's possible the conversion is a one-liner somewhere I missed, or it's possible the camelCase `pickupPoint` is being sent and silently dropped by the backend. **This is the highest-priority verification needed.**

2. **Does `ContractTranslation.meeting_point_details` get populated for any non-English language today?** If the answer is "no, the parent field is the only one ever written", then B-1's customer-visible severity is theoretical, not active. Need a data query: `SELECT COUNT(*) FROM operators_contracttranslation WHERE meeting_point_details IS NOT NULL AND meeting_point_details != '' AND language != 'en';`

3. **Is there ANY code path that consumes `ProductDetailSerializer.translated_inclusions` / `translated_exclusions` in the customer frontend?** The frontend `DayTripDetailPage.js:196-197` reads `contract.translated_inclusions || contract.inclusions`, which would actually receive the resolved translated value (since `ProductDetailSerializer` has the method). So F-01's "translations array never consumed" may be true for `meeting_point_details` but false for `inclusions`/`exclusions`. Need a wider grep across the customer frontend to confirm.

4. **What is the `is_actived` filter impact on the OR-fix?** `ContractViewSet.get_queryset()` filters `is_actived=True` (line 429). The `service_areas`/`primary_location` filter (lines 462-475) runs on this filtered queryset. So a contract with `primary_location=Phuket` but `is_actived=False` will not match a Phuket search. The D-6 ambiguity includes this implicit "active contracts only" filter — and there's no UI indicator of how many contracts were excluded for this reason.

5. **Does the admin `ContractViewSet.location` filter (`operators/views.py:209+`) use the same OR semantics as the public viewset?** My B-5 noted the admin viewset has additional `departure_location` + `arrival_location` filters but I did not read past line 230. If the admin uses a different OR semantics (e.g., AND instead of OR), staff will see different results from the public site for the same query.

6. **Is the `CATEGORY_CAPABILITIES` matrix in `components/contracts/constants.js:91-102` (referenced in F-05) still the source of truth, or has `serviceCategoryHelper.js:17-99` `SERVICE_CATEGORY_CONFIG` superseded it?** Both matrices should agree, but I did not verify. A divergence would be a third source of render-gating truth and could cause silent inconsistencies.
