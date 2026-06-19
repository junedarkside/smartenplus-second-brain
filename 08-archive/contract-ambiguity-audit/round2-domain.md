# R2 Domain Cross-Exam

**Scope:** Operational reality vs technical claims from R1 Backend (B-1 to B-9) and R1 Frontend (F-01 to F-10). Reclassify findings where technical truth diverges from customer/staff impact.
**Author:** Domain / Business Analyst
**Date:** 2026-06-03
**Method:** Vault evidence (operators, services, contract, transport-audit notes) + spot-checked code paths. Anti-rubber-stamp: at least one Refute/Refine per side; one finding reclassified.

---

## On Backend (B-N)

### B-1: i18n not resolving `meeting_point_details` (was P1)
**Refine (downgrade to P2, dormant).** The technical claim is correct: `get_localized_field()` is defined at `operators/serializers.py:571` but is **never called** as a `SerializerMethodField` (searched the file — only the method definition appears, no consumer). The frontend PDP at `smartenplus-frontend/components/activities/detail/DayTripDetailPage.js:202` reads `contract.translated_meeting_point_details || contract.meeting_point_details`, expecting a field that the serializer does NOT emit — `ContractDetailSerializer.Meta.fields = '__all__'` (line 603) returns the parent's `meeting_point_details` plus a separate `translations` array, but no flattened `translated_*` top-level fields.
**However, operationally this is dormant for the Thailand market.** Evidence:
- The admin form has a single English-only `meetingPointDetails` textarea (`admin-dashboard/components/forms/contract/DayTripDetails.js:67-77`). There is no UI to populate per-language translations.
- 12 languages are registered per `[[operators]]` line 44, but no operator flows to translate.
- The `[[contract-serializer-non-transport-fields]]` audit (which read the same serializer) flagged `meeting_point_details` as a flat field — it never mentioned translations.
- The frontend fallback `translated_X || X` pattern is also used for `name`, `description`, `tour_highlights`, `inclusions`, `exclusions`, `what_to_bring` (per `[[experience-detail-page-redesign]]` line 219-227). If B-1 was a P0 bug, all 7 fields would be broken. None of those are reported as broken by customers.
- Resolution: P2 dormant/aspirational. Will become P0 the moment a translation management UI ships.

### B-2: list serializer omits `primary_location` and `service_areas` (was P1)
**Confirm with nuance.** `ContractSerializer.Meta.fields` (line 172-178) is explicit and omits both. `ContractDetailSerializer.Meta.fields = '__all__'` (line 603) includes them. Confirmed at the code level.
**Operational reality check:**
- The customer-facing search list (`/activities` browse) renders cards via `DayTripCard.js` (per F-02 audit, line 16) and shows city names. Whether the city comes from `service_areas[0]` or `primary_location` is not visible in audited code — neither field is consumed by the card (`smartenplus-frontend/components/activities/browse/DayTripCard.js` is not in the R1 grep results for `primary_location`).
- `grep -rn "primary_location\|primaryLocation" smartenplus-frontend/` returns ZERO hits in source code. The only mention is `docs/features/daytrip/DAYTRIP_FEATURE_REPORT.md` (5 hits — all documentation, not code).
- The autocomplete dropdown (`getActivityLocations`) is **denormalised** — returns `{location_name, province}[]`, not full Contract rows. The list-endpoint missing these fields does not affect the dropdown.
- Resolution: stays P1 because it IS a contract-quality gap (clients cannot introspect match source), but the customer-facing impact is **the staff-debugging story** (an operator complaining "why does my Phuket contract appear in Krabi results" cannot be answered from the list response), not customer UX. Reclassify as "internal-tooling gap" rather than "customer-facing bug."

### B-3: no category enforcement on `service_areas`/`meeting_point_*` (was P0)
**Refute (P0 → P2).** Technical claim correct: `operators/models.py:225-415` has no `clean()`, no signal, no DB constraint linking `service_category` to field presence. The 2026-05-30 transport audit (`[[transportation-category-audit]]` line 158) literally says: *"Whether meaningful inventory exists in non-transport categories: unknown without DB access."*
**Operational reality:**
- The admin form **does** gate by category. `ContractFormFields.js:177, 220` wraps both `primary_location` and `service_areas` in `{!isTransport && (...)}` — only the form hides them. Form gating is the actual enforcement layer.
- The form is the only path to populate these fields. The PdfContractImport flow (`[[pdf-contract-import-research]]`) goes through the same admin form, so it inherits the same gating.
- Risk scenario: an admin uses the Django shell to bypass the form. P0 risk requires a deliberate bypass or a future bulk-import that skips the form. Today: P2.
- Related: `[[contract-trip-null-non-transport-pattern]]` confirms `sanitize_category_fields()` runs on the create flow (`operators/views.py:1067-1102`) which DOES enforce the `trip=None` invariant for non-transport. The pattern for "category enforcement" exists — it just doesn't extend to location fields.

### B-4: public location filter unions both fields (was P1) — **Confirm.**
The 2026-06-01 OR-fix is the right call. `[[activities-location-search-bug]]` Fix 1 (line 116-151) explicitly chose OR. Operationally correct.

### B-5: admin `ContractViewSet` has different filter surface (was P2) — **Confirm.**
Two viewsets, two semantics. Staff viewing admin sees transport routes + location; public sees only location. This is intentional (admin needs to find a contract by route number) and the divergence is documented in `[[backend-architecture]]` (products=public, operators=admin).

### B-6: `InfoField` constants are snake_case `'pickup_point'`, not `'pickuppoint'` (was P2) — **Confirm.** Verified at `operators/models.py:183-184`. The frontend `Passengers.js:261, 503` switch on `"pickup_point"` matches. This is a useful fact-check, not a customer bug.

### B-7: no server-side validation that `info_fields` M2M contains `pickup_point` before persisting (was P2) — **Confirm.** This is a P3 latent issue — currently the frontend gates the form by `info_fields` schema, so the gap never fires. Reclassify as a defense-in-depth improvement, not an active bug.

### B-8: no validation that `meeting_point_place.location` matches `primary_location` (was P2) — **Refine (P2 → P3).** Cosmetic admin inconsistency. PDP hero is the only surface that could expose both (`[[admin-dashboard-contracts]]`), and `MeetingPointCard.js` renders neither `meeting_point_place` nor `primary_location` — it renders `meetingPointDetails` text. So conflicting cities is not customer-facing.

### B-9: admin PATCH 500s on bad IDs (was P2) — **Confirm.** Staff-side error quality issue. Not customer-facing.

---

## On Frontend (F-N)

### F-01: 4 pickup data paths (was P1) — **REFUTE.**
**Counted in code:** the data flow is ONE input → TWO read shapes, not 4 paths.
- **Input:** 1 path. `Passengers.js:261, 503, 1091` all reference the same Formik `trip.pickupPoint` field. The form input is a single textarea gated by `info_fields` schema (`field_type === "pickup_point"` → `trip.pickupPoint = ''`).
- **Persistence:** 1 path. `helpers/checkoutPersistence.js:181` writes `pickupPoint: trip.pickupPoint` to the Redux+save payload.
- **Read sites (where data is consumed):** 4. `BookingDetail/index.js:137` (read), `Information.js:11, 21, 57, 59` (read+display), `PdfView.js:192, 198, 214` (read+display), `PdfViewImproved.js:257, 263, 277` (read+display). Plus `BookingDetail.js.backup:346` which is **dead code** (F-04 Q4 confirmed: `.backup` files are not in active use).
- **Operational reading:** 3 read sites in active code, 1 dead. F-01 overcounts by 1 (the dead backup) and mislabels them as "paths" — they are read sites. The data flow is sound. The "implicit shim" F-01 mentions is the `info_fields` dict the backend returns with lowercase keys (`pickuppoint`, `pickuptime`) per `BookingDetail/index.js:129-139` — this is the SAME dict, not a separate path.
- **Reclassify:** P1 → P3 (cosmetic inconsistency: the same field is rendered with two different variable names — `pickupPoint` in the form, `pickuppoint` in the read). The customer never sees this.

### F-02: `primary_location` is admin-only (was P1) — **Confirm.** Direct grep: `grep -rn "primary_location\|primaryLocation" smartenplus-frontend/` returns 0 hits in source, 5 hits in `docs/features/daytrip/DAYTRIP_FEATURE_REPORT.md` (documentation only). The field is admin-side metadata that the OR-filter happens to use, but the customer never sees it directly. **Strong evidence. The R1 finding is correct.**

### F-03: `getActivityLocations` hard-coded to DAY_TOUR (was P1) — **REFUTE.**
`dayTripsApi.js:128-130` shows the default is `'DAY_TOUR'`, but the call site `ActivitySearch.js:40-42` reads:
```js
const { data: locations = [] } = useGetActivityLocationsQuery(
  filters.category ? { serviceCategory: filters.category } : undefined
);
```
- When `filters.category` is set (e.g. `?category=SPA_WELLNESS`), the API IS called with that category. Not hard-coded.
- When `filters.category` is null (default browse), the API defaults to `DAY_TOUR`. This matches the default filter on `/activities`.
- **The customer CAN search SPA/EVENT/FOOD by location** by selecting a category chip first. The default being DAY_TOUR matches the dominant use case (Thailand = tours).
- Reclassify: P1 → P3. The "hard-coded" framing is incorrect; the "default-favors-DAY_TOUR" framing is correct. No fix needed for the current product surface.

### F-04: two casing systems for `pickupPoint` / `arrivalFlighttime` (was P0) — **Refine (P0 → P3).**
The code shows a clean pattern, not a bug:
- `checkoutPersistence.js:181` — `pickupPoint: trip.pickupPoint` (no transformation).
- `checkoutPersistence.js:190` — `arrivalFlightTime: safeTimeToString(trip.arrivalFlighttime)` (capital T at save).
- `checkoutPersistence.js:421` — `normalizedTripInfo.arrivalFlighttime = timeStringToDate(savedTripInfo.arrivalFlightTime)` (lowercase at restore).
- The comment at line 176 explains: "Backend expects arrivalFlightTime/departureFlightTime (capital 'T')" — and the transformation happens explicitly. The pickupPoint case doesn't need transformation because the Formik name and the backend name are already the same (camelCase).
- **What the R1 finding actually identified:** there is an asymmetric pattern (explicit transformation for flight times, implicit for pickup). The asymmetry is **documented in a comment** for flight times but undocumented for pickup. That's a doc gap, not a bug.
- Reclassify: P0 → P3. The data round-trips correctly. The implicit-shim concern is that a backend rename would break the form silently — true, but no such rename is in progress.

### F-05: `timeline_place[]` and `route.route_name` never render together (was P1) — **Confirm.** The category matrix in `serviceCategoryHelper.js:17-99` is the source of truth. Operationally this is fine; the categories are mutually exclusive in the database by design (transport has route, no timeline; tour has timeline, no route).

### F-06: two "where to" autocompletes (was P1) — **Confirm.** Two endpoints, two shapes. Operationally they serve different surfaces (transport home vs activities browse). The lack of shared contract is tech debt but not a customer bug.

### F-07: two near-identical `TimelineDisplay` (was P2) — **Confirm.** Admin DnD variant + customer read-only. Both are maintained. Not customer-facing.

### F-08: 3 customer surfaces read `meeting_point_type`/`meeting_point_details` independently (was P2) — **Refine (P2 → P3).** Three read sites with the same label-lookup pattern. The `MEETING_POINT_TYPE_LABELS` constant is the SSOT. The "no central helper" claim is true but the cost is one new enum value = three grep-replace operations — low risk.

### F-09: commented shim at restore time (was P2) — **Confirm.** Documentation gap. P3.

### F-10: `stops` field is not observable in customer (was P2) — **Confirm.** Dead config flag. P3.

---

## Resolved Truths

1. **`primary_location` is admin-side metadata that survives only via the OR-filter and via the admin form's help text.** The customer never sees it directly. The "for display and branding on the product page" claim in `ContractFormFields.js:184` is **aspirational** — no customer component reads it. (`[[admin-dashboard-contracts]]` line 24 hides it from transport but the visibility matrix for non-transport is "Y" — but the customer-facing render path is empty.)

2. **`service_areas` is the only customer-relevant location field.** It feeds the autocomplete, the location filter, and the contract card. The M2M is the load-bearing field; the FK is a legacy tag.

3. **The i18n resolver is dormant architecture.** `get_localized_field()` is defined and never called. The frontend's `translated_X || X` pattern is correct *intent* but depends on fields the backend doesn't emit. For Thailand (English-only contracts), this is fine. The architecture will need rewiring when translations ship.

4. **The 4-path pickup story is a 1-input, 3-read, 1-dead-backup design.** F-01 overcounts paths. F-04's casing concern is an asymmetric documentation gap, not a bug.

5. **Category gating is form-enforced, not DB-enforced.** B-3 is real but operational risk is low because the admin form is the only write path.

---

## New Questions Surfaced

- **Q-NEW-1:** Does the customer PDP hero actually render *any* location label, or is the "display and branding" claim purely aspirational? `[[admin-dashboard-contracts]]` line 5 says "Used for display and branding on the product page" but no PDP component reads `primary_location`. If no component reads it, the "for upselling" `help_text` in `operators/models.py:402` is the more accurate description. **This is the un-asked question from R1 D-1.**
- **Q-NEW-2:** When the i18n resolver gets wired up, will it call `get_localized_field()` per request or use a `SerializerMethodField`? The current design is method-only, no field, so the calling convention needs to be designed.
- **Q-NEW-3:** Why does `Passengers.js:261, 503` initialise `trip.pickupPoint = ''` (empty string) for text fields but `trip.pickupTime = null` for time fields? The mix is suspicious — is the empty-string for text fields masking a bug where the API sends `null`?
- **Q-NEW-4:** The admin's `DayTripDetails.js:67-77` shows `meetingPointDetails` as a single field. Is there a parallel translation-management UI elsewhere (e.g. an i18n tab) that staff use, or are translations truly never populated?

---

## Ops vs Tech Distinction

### Technically true but operationally irrelevant
- **B-1** (i18n resolver unwired) — dormant in Thailand; becomes real when translations ship.
- **B-8** (no cross-field validation for `meeting_point_place` vs `primary_location`) — admin cosmetic; PDP doesn't render either.
- **F-01** (4 pickup paths) — actually 1 input + 3 read + 1 dead backup. F-01 overcounts.
- **F-04** (casing asymmetry) — round-trip works; only the comments differ.
- **F-08** (3 surfaces read `meeting_point_type`) — `MEETING_POINT_TYPE_LABELS` is the SSOT; the duplication is one-grep-replace cheap.
- **F-10** (dead `showStations` config flag) — dead code; no impact.

### Operationally matters but lacks technical evidence
- **D-1 / B-3 (P0)** — the conflict between the help text "Not used for customer location search" and the OR-fix that uses it. The technical fix is in place; the documentation is now stale. Staff who read the help text and set `primary_location=Phuket` for "display only" are still surprised when the contract appears in Phuket searches. **Fix the help text.**
- **D-3 / B-3 (P0)** — three documents (the 2026-06-01 bug audit, the migration help text, the admin form help text) describe the same two fields with three different framings. **Write a 1-paragraph ADR.**
- **D-9** — "Required" for tours in `tours-vs-transportation.md` but the model is `null=True, blank=True`. **Either enforce or remove the doc.**

### Cross-cutting operational bug not surfaced by R1
- **The form `meetingPointDetails` field in admin (DayTripDetails.js:67-77) writes to the parent `Contract.meeting_point_details`.** No translation UI exists. When translations are added later, existing English-only content in the parent field will be the fallback — fine. But there's no audit path to find contracts with no translation populated, which will become a content gap when the team wants to enable the Thai-language site for domestic customers.

---

## Top 1 Ops-vs-Tech Gap

**B-1's i18n resolver.** The technical claim ("defined but never called as SerializerMethodField") is true. The operational claim ("translations are silently dropped") is dormant for English-only Thailand and the `en, th, zh, ja, ko, ...` 12-language table at `[[operators]]` line 44 is forward-looking. Customer impact: zero today. Staff impact: zero today. Future impact: a P0 the day translations are populated without re-wiring the resolver. The fix is small (1 SerializerMethodField per translatable field) but the trigger is product-side, not engineering.

## Top 1 Finding Reclassified

**F-01 P1 → P3** (4 pickup paths → 1 input + 3 read + 1 dead backup). The "implicit property-rename shim" framing misrepresents a data flow that round-trips correctly. The "central mapper" the R1 finding asks for would add indirection to fix a doc gap. Recommend closing F-01 and the related F-09 as P3 doc items.

**Honourable mention: B-3 P0 → P2.** Category enforcement is real but the admin form is the only write path and the form already gates correctly. The P0 framing overweights the "what if the form is bypassed" scenario.
