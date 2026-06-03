# R2 Frontend Cross-Exam

**Repo:** `/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus-frontend/`
**Author:** Frontend Analyst (Round 2)
**Date:** 2026-06-03

Reviewed: `round1-backend.md` (B-1..B-9), `round1-domain.md` (D-1..D-10)
**Anti-rubber-stamp:** 4 Refutes + 2 Refines in this file. Not all peer claims survive contact with the actual wire format.

---

## On Backend (B-N)

### B-01: `meeting_point_details` duplicated + i18n not resolving
**Refute (partly) and Refine.** Peer is right that the bug exists; peer is wrong about the shape of the brokenness.

- The frontend **never** reads `translations: []` array. Both PDP and booking detail pages use **flat sibling fields with fallback**:
  - `components/activities/detail/DayTripDetailPage.js:202` — `contract.translated_meeting_point_details || contract.meeting_point_details`
  - `components/bookings/BookingDetail/ServiceDetail.js:35` — `contract?.meeting_point_details` (no fallback)
- `ProductDetailSerializer` (`products/serializers.py:518-522`) does have `translated_name`, `translated_description`, `translated_tour_highlights`, `translated_inclusions`, `translated_exclusions` as `SerializerMethodField`. **But there is no `translated_meeting_point_details` sibling.** The pattern was never extended to this field.
- So the day-trip PDP reads `translated_meeting_point_details` (always `undefined`) and silently falls back to the parent field's **original-language** value. This is the bug.
- `ContractDetailSerializer` (`operators/serializers.py:565`) does emit `translations = ContractTranslationSerializer(many=True, …)`, but no consumer in the customer frontend traverses that array. It is dead data on the wire for our flows.
- `ContractDetailSerializer` defines `get_localized_field()` (`operators/serializers.py:571-599`) but it is **never invoked** by any serializer method or `SerializerMethodField`. It's dead code in the operator detail serializer.
- **Refined claim:** The bug is that `ProductDetailSerializer` is missing a `get_translated_meeting_point_details` `SerializerMethodField`. The backend B-1 narrative ("translations array the frontend must join") misdescribes the design intent — the design intent is **flat sibling field with server-side resolution**, and the bug is one missing field on the `ProductDetailSerializer` (not a missing client-side join logic). `ContractDetailSerializer` also needs the same fix if the operator-side flows ever read i18n.

### B-02: Public list serializer omits `primary_location` / `service_areas`
**Refute.** The omission is not customer-visible, because the customer-facing list view **does not consume either field**.

- `store/api/dayTripsApi.js:53-95` `getContracts` calls `/api/v1/contract/` (the public list endpoint). 
- Consumer: `components/activities/browse/FilterDayTripsPage.js:46-60` → `DayTripList` → `DayTripCard.js`.
- `DayTripCard.js` field usage is exactly: `ratecards` / `ratecard`, `translated_name` / `name`, `image`, `extra` (features), `tour_duration_days`, `slug`, `review_count`, `average_rating`, `booking_count_30d` / `booked_count`, `original_price`. **No `primary_location`, no `service_areas`, no `primaryLocation`, no `serviceAreas`** anywhere in the customer browse path.
- The autocomplete consumer is the **separate** `getActivityLocations` endpoint (`dayTripsApi.js:128-133`) which returns `{location_name, province}[]` — the search dropdown does NOT need per-contract `primary_location` / `service_areas`; it needs aggregated city names.
- Repo-wide grep for `primary_location` / `primaryLocation` returns zero hits in any `components/` or `pages/` file. The only references are in `docs/features/daytrip/DAYTRIP_FEATURE_REPORT.md` (documentation, not code).
- **Conclusion:** The omission is a deliberate payload-size optimization (list cards don't need the nested `LocationSerailizer()` expansion). The peer concern is correct that "the filter cannot tell the client which field matched" — but **no client surface needs to know**, and the field-level distinction is already lost at the autocomplete endpoint per D-6 (which the domain analyst already flagged).
- **Refined claim:** B-2 is a documentation gap (frontend never needs these on list), not a customer-visible bug. If the autocomplete dropdown ever needs to label entries as "primary" vs "service area" (per D-6), the fix is in the `/contract/locations/` serializer, not the list serializer.

### B-03: No category/field enforcement; `info_fields` schema is per-trip dynamic
**Confirm with nuance.**

- Frontend is dynamic-per-trip. `components/forms/checkout/Passengers.js:259-275` switches on `field.field_type` per row:
  - `pickup_point`, `pickup_time`, `flight_in`, `flight_out`, `dropoff_time`, `dropoff_point`, `extra_info` — 7 cases
  - `default: break;` — unknown `field_type` is silently dropped
- The schema source is `item.contract?.info_fields`, fetched at booking time from the contract detail endpoint. There is **no frontend-side whitelist** by category; a TRANSPORTATION contract whose `info_fields` is empty just renders no inputs.
- The lack of server enforcement is **partially hidden** (frontend silently no-ops) and **partially customer-visible** (per backend B-7, a TRANSPORTATION contract with `info_fields` empty will still let the user type `pickupPoint="Hotel Lobby"` into Formik, but it never persists into the booking's `InfoFields` row — only into `CartItemCheckoutInfo`).
- B-3 is correct: a server-side `clean()` would prevent admin from creating a `DAY_TOUR` with `meeting_point_type='HOTEL_PICKUP' AND service_areas=[] AND primary_location=NULL` — which currently can happen and produces an empty meeting-point UI on the PDP.

### B-04: Public `/contract/` filter unions both location fields
**Refine.** The union is correct in API, but the frontend **never observes** which field matched.

- Confirmed: `dayTripsApi.getContracts` (line 62) sends `?location=...` and consumes the response as opaque cards.
- `getActivityLocations` (line 128-133) returns a flat deduped list of `{location_name, province}` — no metadata about which contracts matched or via which field. Customer can't tell.
- `useDayTripFilters` (called from `FilterDayTripsPage.js:6, 18`) and `ActivitySearch` (line 10, 40) only carry a single `filters.location` string. No client-side distinction.
- The dropdown mixing (D-6) and the filter union (B-4) compound: a customer typing "Phuket" gets a mix of `primary_location=Phuket` and `service_areas contains Phuket` contracts, ranked together. From D-1 + D-6, the doc says the union is "wrong" but the **product** wants the union. The bug is the **help text**, not the filter.

### B-05: Admin `ContractViewSet` has a different filter surface than public
**Out of scope for this frontend audit** (admin is a separate repo; `admin-dashboard` not present in this checkout at `../../AdminDashBoard/admin-dashboard/` — path from CLAUDE.md is unresolvable on this machine). Confirming the public-side flows; admin filter surface needs admin-side audit. **No confirmation or refutation from the customer frontend.**

### B-06: `InfoField` constants are snake_case (`pickup_point`), not lowercase (`pickuppoint`)
**Refute.** Peer is correct about the **schema** model but wrong about the **wire format** for persisted booking data. The frontend reads **two different InfoField-shaped models** with **two different casings**:

- **`stations.InfoField`** (schema) — `operators/models.py:182-216` defines `PICKUP_POINT = 'pickup_point'` (snake_case). This is what the frontend reads at `Passengers.js:259-275` via `field.field_type === "pickup_point"`. Peer is correct here.
- **`bookings.InfoFields`** (data) — `bookings/models.py:151-180` defines model fields as **lowercase, no separator**: `pickuppoint`, `pickuptime`, `arrivalairline`, `extrainfo`, etc. **These are the actual Django column names** (not just constants). The frontend reads these at `components/bookings/BookingDetail/index.js:127-141` (`info_fields.pickuppoint`, `info_fields.pickuptime`, `info_fields.extrainfo`, etc.) and `components/bookings/PdfView.js:189-220` (destructures `pickuppoint`, `pickuptime`, `dropoffpoint`, `dropofftime`, `extrainfo`, …).
- **The conversion point** is `carts/utils.py:235-260` `extract_trips_info()`:
  - Input (camelCase, what frontend sends): `trip_dict.get('departureAirline')`, `get('pickupPoint')`, `get('remark')`
  - Output (lowercase, what gets stored): `trip_info['departureairline']`, `trip_info['pickuppoint']`, `trip_info['extrainfo']` (note the `remark` → `extrainfo` semantic rename)
  - Then `create_info_fields()` (`carts/utils.py:330-371`) reads `trip['pickuppoint']` etc. and writes to the lowercase model fields.
- **Refined claim:** The wire format the customer frontend reads on the booking detail page is **lowercase, no separator** (`pickuppoint`), not snake_case. The snake_case `field_type` constant is a separate concept (schema lookup key) and never appears in the booking detail wire format. The conversion from camelCase (form) → lowercase (persisted) is a **server-side** decision in `extract_trips_info`, not a client-side shim — frontend's F-01 / F-04 frontend-side observations are about the **in-memory** shape (camelCase Formik) vs the **wire** shape (lowercase), which is server-controlled.
- This also explains why the frontend-side F-04/Passengers.js asymmetry (camelCase `pickupPoint` vs camelCase `arrivalFlightTime`) only matters on the **save** path; the restore path always reads from the lowercase wire.

### B-07: `CartItemCheckoutInfo.pickup_point` is a CharField, not contract-derived
**Confirm with refinement.**

- `carts/views.py:583-593` confirms the backend reads `trip.get('pickupPoint', '')` from frontend camelCase and stores in snake_case model field `checkout_info.pickup_point`. Django's ORM handles the attribute-name conversion.
- The frontend side is exactly as peer describes: `helpers/checkoutPersistence.js:179-194` `normalizeTripData` emits `pickupPoint: trip.pickupPoint` (line 181) — no rename, just pass-through. The string survives the round trip only because both sides agree on camelCase.
- Refined claim: the customer-visible risk is wider than peer notes. Even if `info_fields` is empty, the **form input is still saved into `CartItemCheckoutInfo.pickup_point`** and rehydrated on next page load (see `checkoutPersistence.js:414-419` reading `savedTripInfo.pickupTime` etc.). This means the customer thinks they filled the form, but the **booking confirmation page** (`ServiceDetail.js`) never shows it because `ServiceDetail.js:35` only reads `contract.meeting_point_details`, not the booking's `info_fields.pickuppoint`. The pickup string is **saved but never displayed** for transport bookings on the post-booking page. This is a real, narrow P1.

### B-08: `meeting_point_place` FK not validated against `primary_location`
**Out of scope for customer frontend.** No consumer in the audited code reads `meeting_point_place` directly. The PDP passes `contract.meeting_point_place` to `MeetingPointCard` only via `meetingPointType` (the enum). If a customer ever sees "Located in Bangkok" from one field and "Meeting point: Chiang Mai" from another, that's a content-team issue, not a frontend code issue.

### B-09: Admin PATCH for `primary_location` / `service_areas` has no try/except
**Out of scope for customer frontend.** Admin is a separate repo; not verified.

---

## On Domain (D-N)

### D-1: `primary_location` "display only" help text contradicts the OR-fix
**Refute the surface claim; confirm the underlying tension.**

- Grep across `smartenplus-frontend` for `primary_location`, `primaryLocation`, `service_areas`, `serviceAreas` returns **zero hits** in `components/` and `pages/`. The customer-facing frontend **does not render `primary_location` anywhere** — not on PDP hero, not on DayTripCard, not on ServiceDetail, not on BookingDetail.
- The only frontend code that touches the **concept** of "where this contract lives" is the autocomplete dropdown (`ActivitySearch.js:40-42` → `useGetActivityLocationsQuery` → `/contract/locations/?service_category=DAY_TOUR`), which returns aggregate city names — no per-contract metadata.
- This means the **"Located in Phuket" map pin** claimed in D-1's customer-journey table is **not implemented in the customer frontend** as of this audit. Either (a) it's a planned feature, (b) it lives in a component not in the audited subset, or (c) the Domain analyst inferred it from `ContractFormFields.js:184` help text without finding the consumer.
- **Refined claim:** The contradiction in D-1 is real at the help-text level but **invisible to customers today** because the customer frontend never displays `primary_location`. The OR-fix is a backend filter that customers benefit from; the help text lying about "display and branding" is only seen by staff. The P0 rating is too high — it's a P2 (staff confusion + dead-code "for display" intent).

### D-2: Model `help_text` says "for upselling" vs admin form "for display and branding"
**Cannot fully verify from customer frontend.** The Django `help_text` lives in the backend (verified `operators/models.py:402-415` "Location-based fields for upselling" per the R1 audit). The admin form help text lives in `admin-dashboard/components/contracts/ContractFormFields.js:184, 227` (per R1 cite) — **the admin-dashboard repo is not present in this checkout**. So I confirm the backend `help_text` but cannot independently confirm the admin form's text from the customer frontend.
- **Refined claim:** the contradiction exists in the documentation trail; from the customer frontend side, the practical effect is zero (the field isn't rendered). R3 skeptic should sample-verify the admin-dashboard file directly.

### D-3: Intent is unstable across three docs ("upselling" / "display" / "search-discoverability")
**Confirm with refinement.** Confirmed at the docs level (Round 1 R-domain already cited `[[08-archive/activities-location-search-bug-2026-06-01.original]]` Debate 3, `ContractFormFields.js:184`, `operators/models.py:402-415` as three sources). From the customer frontend: zero evidence the "upselling" intent is realized. Zero evidence the "display" intent is realized. Only the "search-discoverability" intent is realized (the autocomplete dropdown).

### D-4: Admin form gives both fields the same UI affordance with no hierarchy
**Out of scope (admin-dashboard not in checkout).** Cannot refute from customer frontend. R3 skeptic should verify.

### D-5: Both fields nullable, both shown for all non-transport categories
**Confirm with refinement from the customer side.** The customer frontend's category matrix (`helpers/serviceCategoryHelper.js:17-99` `SERVICE_CATEGORY_CONFIG`) does NOT gate by `primary_location` / `service_areas` — but it also doesn't render them at all. So the "no per-category UX distinction" claim is true for the form (in admin) but irrelevant for the customer surface. The category matrix IS distinct: `showTimeline: true` only for `DAY_TOUR` / `MULTI_DAY_TOUR`; `showRoute: true` only for `TRANSPORTATION`. So the **system has per-category distinction at the data-presentation level, just not at the location-field level**.

### D-6: Autocomplete endpoint mixes both fields with no distinction
**Confirm.** `components/activities/shared/ActivitySearch.js:40-42` calls `useGetActivityLocationsQuery({})` (no filter) and the endpoint returns the flat deduped list. Combined with Q6 from R1-frontend (the `serviceCategory` default is `DAY_TOUR`), the dropdown never includes `MULTI_DAY_TOUR` / `SPA_WELLNESS` / `ATTRACTION_TICKET` contracts' locations at all. This is a real customer-visible bug, but it's the **opposite** of what the Domain D-1 narrative implies — the bug is **too narrow**, not too broad.

### D-7: Both fields added in the same 2026-01-25 migration
**Confirm** (out of scope of frontend code; backend migration history per R1 audit).

### D-8: `ContractSerializer` exposes both fields for ALL categories including TRANSPORTATION
**Refute the implication.** Even if the backend serializer exposes them, the customer frontend does NOT consume them on any surface. So "frontend has to filter or accept empty" — the frontend simply doesn't read them. The "accept empty" cost is zero.

### D-9: `primary_location` nullable but architectural doc says "Required" for tours
**Confirm with refinement.** The downstream filter's silent-failure mode (B-3 + D-1) is real. Customer searches return empty results, but the customer can't tell whether that's "no tours in Phuket" or "operator forgot to set primary_location". From the customer side this is a P1 (silent empty search results).

### D-10: `Location` is city/province hierarchy; "where it is" vs "where it serves" can't be distinguished
**Confirm.** Customer frontend has no district / neighborhood / coordinate-level data. The day-trip detail page (`DayTripDetailPage.js`) doesn't render a map pin. The booking detail (`ServiceDetail.js`) doesn't show a location. So the architectural gap exists, but the customer frontend doesn't trip on it (no rendering means no incorrect rendering).

---

## Resolved Truths

1. **B-06 / F-01 / F-04: There are TWO InfoField-shaped models and THREE casing systems in play.**
   - `stations.InfoField` schema: `field_type` in snake_case (`pickup_point`) — used by `Passengers.js:259-275` to decide which form fields to render.
   - `bookings.InfoFields` data model: column names in lowercase, no separator (`pickuppoint`, `arrivalairline`, `extrainfo`) — read by `BookingDetail/index.js:127-141` and `PdfView.js:189-220`.
   - Frontend Formik state: camelCase (`pickupPoint`, `arrivalFlighttime`) — kept in Redux, sent to `/cart-checkout-info/save/`.
   - Server-side `extract_trips_info` (`carts/utils.py:235-260`) is the conversion point. The conversion also semantically renames `remark` → `extrainfo`. There is **no client-side casing shim for `pickuppoint`** (F-01's claim is the symptom, not the cause — the inconsistency is server-determined).

2. **B-01: The `meeting_point_details` i18n bug exists but the shape is wrong in B-1's description.** The fix is a single missing `get_translated_meeting_point_details` `SerializerMethodField` on `ProductDetailSerializer` (mirroring the existing `get_translated_name` / `get_translated_description` / `get_translated_inclusions` / `get_translated_exclusions` pattern at `products/serializers.py:518-522, 569-587`). `DayTripDetailPage.js:202` is **already coded to read it** — it falls through to the parent field because the field doesn't exist. `ServiceDetail.js:35` doesn't even have the fallback (booking page always shows original-language details).

3. **B-02: The public list serializer omission is a payload-size optimization, not a customer-visible bug.** Zero customer-facing code in this repo reads `primary_location` or `service_areas` from the list response. The autocomplete dropdown is served by a separate endpoint.

4. **D-1: The "Located in Phuket" PDP hero claim is unverified.** No code in `components/activities` or `pages/` renders `primary_location`. The customer-facing impact of the help-text contradiction is zero today.

---

## New Questions Surfaced

1. **Q-A.** The `extract_trips_info` rename of `remark` → `extrainfo` is a **semantic mapping**, not a casing conversion. Is there any other place in the codebase that does a similar `field_name → different_name` mapping? (The R1 backend audit found `carts/views.py:583-593` separately reading `pickupPoint` — is that the same camelCase input? If so, why does the cart-save use camelCase but the booking-persist use lowercase?)
2. **Q-B.** `BookingDetail/index.js:127-141` reads `props.booking?.info_fields` — is this the `bookings.InfoFields` model serialized by `bookings/serializers.py:122-125 InfoFieldsSerializer` (fields = `__all__`)? If so, the lowercase names are the model field names, not a custom serializer output. Confirmed above by reading the model. But the **wire path** from a "checkout save" → "booking created" → "booking detail fetch" goes through `extract_trips_info` → `create_info_fields` → `InfoFields.objects.create(pickuppoint=...)`. The persistence is correct, the rendering is correct (lowercase matches model). So the data path is **internally consistent** but the frontend's `BookingDetail` reader is **implicitly coupled to Django's column-naming convention**. If a future refactor renames the model field to `pickup_point` snake_case, the customer booking detail page silently breaks.
3. **Q-C.** `ServiceDetail.js:35` is the **post-booking** page, and reads `booking.contract.meeting_point_details` — but the booking was placed in some language (e.g., `en`). If the customer later switches UI language, the meeting-point details don't re-translate (they're a snapshot). Is this the intended UX? Probably yes for booking history (you don't want past bookings to "change"), but worth confirming with product.
4. **Q-D.** The B-3 (no server enforcement) + B-7 (frontend decides which fields to save) + B-9 (no admin validation) chain means a contract can be created in a broken state, get listed in search results, and customers fill out fields that the backend silently discards. The customer sees a confirmation, but the operator sees no pickup info. No automated test catches this. Is there a way to add a "soft warning" at booking confirmation time (e.g., "You entered pickup info but this tour doesn't track pickup — your note will be sent to the operator but the tour will meet at the standard point")?
5. **Q-E.** The B-2 / D-1 combined: if the customer-facing frontend doesn't render `primary_location` today, **should the team add a PDP "Located in {primary_location.location_name}" label**? It would (a) make the D-1 help text true, (b) make the OR-fix in B-4 visible to customers, (c) reduce silent-empty-search frustrations in D-9. But it would also need an i18n solution for the city name. Worth a Round-3 design discussion.

---

## Summary for Round Lead

- **Top contradiction resolved:** The casing claim (B-6) was over-stated. The wire format is **lowercase** (`pickuppoint`), not snake_case. Conversion happens server-side in `carts/utils.py:235-260`, not client-side. The frontend's F-04 (camelCase `pickupPoint` in form) vs persisted `pickuppoint` is **server-determined**, not a frontend shim.
- **Top contradiction unresolved:** B-1's description of the i18n fix shape ("translations array the frontend must join") does not match the actual design — the design is "flat sibling field with server-side resolution" and the bug is one missing `SerializerMethodField` on `ProductDetailSerializer`. R3 should validate this against the actual `ProductDetailSerializer` fields list (I read it — `translated_meeting_point_details` is absent; `translated_name/description/inclusions/exclusions/tour_highlights` are present).
- **Top customer-visible bug found in R2 (not in R1):** `ServiceDetail.js:35` reads `contract.meeting_point_details` with no i18n fallback. This is a real P1 for non-English customers viewing their post-booking details.
