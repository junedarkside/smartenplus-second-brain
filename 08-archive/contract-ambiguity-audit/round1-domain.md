# R1 Domain Audit

**Scope:** Business intent for `Contract.primary_location` (FK) vs `Contract.service_areas` (M2M) — both pointing at `stations.Location`. Per-category interpretation, customer-journey surface mapping, history of the field split. Read-only research; no code changes.

**Audited by:** Domain / Business Analyst
**Date:** 2026-06-03
**Inputs read:** `[[admin-dashboard-contracts]]`, `[[08-archive/.originals/activities-location-search-bug-2026-06-01.original]]`, `[[contract-trip-null-non-transport-pattern]]`, `[[contract-serializer-non-transport-fields-2026-06-03]]`, `[[01-projects/operators]]`, `[[transportation-category-audit-2026-05-30]]`, `[[activities-search-merge-review-2026-06-01]]`, `[[stations]]`, `smartenplus-backend/operators/models.py:402-415`, `smartenplus-backend/operators/admin.py:1038-1102`, `smartenplus-backend/operators/migrations/0045_add_tour_fields.py`, `admin-dashboard/components/contracts/ContractFormFields.js:176-261`, `admin-dashboard/hooks/useContractFormData.js:127-128`, `admin-dashboard/components/utils/contractUtils.js:88-89`.

---

## Findings

| ID | Sev | Source | Finding |
|----|-----|--------|---------|
| **D-1** | **P0** | `[[contract-trip-null-non-transport-pattern]]` + `ContractFormFields.js:184` | The two fields have **opposite, documented intents** but the codebase mixes them. Admin help text (lines 184, 227) says: `primary_location` = "display and branding" / "Not used for customer location search"; `service_areas` = "All locations where customers can find and book". Backend public filter (`products/views.py`) until 2026-06-01 only consulted `service_areas` — matching the docs. The 2026-06-01 fix added `primary_location` to the filter with `Q \| Q`, **silently overriding the documented contract**. A staff member who set `primary_location=Phuket` for "display only" is now surprised when the contract appears in "Phuket" searches. |
| **D-2** | **P1** | `operators/models.py:402-415` + `ContractFormFields.js:178-188` | The **Django model `help_text` says "for upselling"** (`'Location-based fields for upselling'`). The **admin form help text says "for display and branding"**. Two different product framings in two files owned by the same team. Upselling implies algorithmic matching (e.g. "you viewed Phuket → Phuket contracts first"); display/branding implies a label on the PDP. The "upselling" intent is not implemented anywhere in the public API we audited. |
| **D-3** | **P0** | `[[08-archive/.originals/activities-location-search-bug-2026-06-01.original]]` Debate 3 (line 110) | The 2026-06-01 audit labelled `primary_location` as "**single FK for upselling**". This is asserted as the canonical intent in the most recent domain write-up, but no code path implements upselling on this field. The most recent customer-facing decision (the OR-fix) **uses `primary_location` for filter, not upsell** — yet another framing. The intent is unstable across three different write-ups. |
| **D-4** | **P1** | `ContractFormFields.js:191,235` + `admin-dashboard-contracts.md:23-24` | The admin form gives both fields the **same UI affordance** — a `LocationSelector` with the same `locationOptions` list. No visual hierarchy, no "required" marker on `primary_location` (the doc `tours-vs-transportation.md` says it's "Required" for tours, but the model is `null=True, blank=True`). Staff cannot tell from the form that the two fields serve different purposes. |
| **D-5** | **P1** | `operators/models.py:402` + `ContractFormFields.js:176,219` | Both fields are nullable and both shown for ALL non-transport categories including `OTHER`. The form is identical for `SPA_WELLNESS`, `EVENT_TICKET`, `ATTRACTION_TICKET`, `FOOD_DINING`, `ACCOMMODATION`. There is no per-category UX distinction even though the semantic differs (e.g. `ACCOMMODATION` "primary location" is the hotel's address — directly true; `EVENT_TICKET` "primary location" is the venue's city — likely true; `SPA_WELLNESS` "service areas" *plural* may indicate pickup radius vs multiple branches). |
| **D-6** | **P1** | `ContractFormFields.js:184` + `activities-search-merge-review-2026-06-01.md:114` | The autocomplete endpoint `GET /api/v1/contract/locations/` is built from `primary_location` FK + `service_areas` M2M. So the **dropdown the customer sees in the search bar mixes the two fields with no distinction**. Same dropdown entry for a Phuket-spa whose only `service_areas` is Phuket vs a Phuket-spa whose `primary_location` is Phuket but `service_areas` is empty. The recent fix made both filter; both feed the dropdown; both show as equal. |
| **D-7** | **P2** | `operators/migrations/0045_add_tour_fields.py` | **Both fields were added in the SAME migration on 2026-01-25.** `primary_location` was NOT created first and `service_areas` added later as a fix. They were designed together for the day-tour feature launch. Any narrative about "we added service_areas because primary_location wasn't enough" is false. The two-field split is a design decision, not a data-evolved workaround. |
| **D-8** | **P2** | `operators/serializers.py:558-559` | `ContractSerializer` exposes `primary_location = LocationSerailizer()` and `service_areas = LocationSerailizer(many=True)` — both for ALL categories including TRANSPORTATION. For a transport contract, both fields will be `null`/empty by design (see `contract-trip-null-non-transport-pattern.md`). The serializer does NOT gate by `service_category`, so the frontend has to filter or accept empty. |
| **D-9** | **P1** | `tours-vs-transportation.md` + `ContractFormFields.js:179-188` | The **architectural doc says** `primary_location` is "Required" for tours, but the **model field is nullable** and the **admin form has no asterisk / required indicator**. New staff can save a contract with both null. The downstream filter (now `OR`) will still match nothing in location search — silent failure, not a 400. This is the gap the customer-facing bug exploited. |
| **D-10** | **P2** | `stations/models.py` (`Location` model) | `Location` is a city/province/country hierarchy. Using it as the target for BOTH a single "home" pointer and a many-to-many "service radius" bag is the architectural reason the ambiguity exists at all. A SPA at "Phuket" vs a SPA that "operates in Phuket + Krabi" is the same `Location` row. There's no spatial granularity (no district, no neighborhood, no coordinates) to distinguish "where it is" from "where it serves". |

---

## Customer Journey Touchpoints

| # | Surface | Field(s) fed | What customer sees | Source of evidence |
|---|---------|---------------|--------------------|--------------------|
| 1 | `/activities` browse filter chip | `service_areas` (post-2026-06-01: also `primary_location`) | Location pills / dropdown | `[[08-archive/.originals/activities-location-search-bug-2026-06-01.original]]` Fix 1 |
| 2 | `/activities` "Day Trips in **Phuket**" H1 | `service_areas[0]` (first match) or `primary_location` | City name in heading | `useDayTripFilters` — not directly documented in vault but inferred from `ActivitySearch` flow |
| 3 | ActivitySearch dropdown suggestions | `primary_location` ∪ `service_areas` (distinct) | Auto-suggest city names | `activities-search-merge-review-2026-06-01.md:114` — `getActivityLocations` endpoint |
| 4 | Homepage card (`DayTripCard`) | likely `primary_location` | City label below title | inferred from `homepage-uxui-redesign-research-2026.md` patterns; not directly evidenced for location field |
| 5 | PDP hero (`/product-detail/{slug}`) | **`primary_location`** per admin help text | "Located in Phuket" + map pin | `ContractFormFields.js:184` — "Used for display and branding on the product page" |
| 6 | PDP "Available in" or "Service area" badge | `service_areas` (plural) | "Available in Phuket, Krabi, Phi Phi" | inferred from `admin-dashboard-contracts.md` visibility; **not directly evidenced in vault — likely a UI gap** |
| 7 | Checkout summary / cart line item | unclear | Likely none — contract location rarely shown at cart level | `[[contract-serializer-non-transport-fields-2026-06-03]]` — serializer exposes location but no UX consumer mentioned |
| 8 | Voucher / confirmation email | unclear | Not in vault | gap |
| 9 | Booking detail page (post-booking) | unclear | `ServiceTabbedInfo.js` — no location field documented in `[[service-detail-non-transport-display]]` | gap |
| 10 | SEO metadata (meta description, og tags) | `primary_location` likely | City name in search snippet | inferred — not directly evidenced |

**Two surfaces are well-evidenced (#1, #3, #5). Four surfaces (#4, #6, #7, #8, #9) are inferred or undocumented.** The PDP hero consumption of `primary_location` is the **only** place where the field's stated "display/branding" intent is realized in documented UX.

---

## Per-Category Intent

| Category | `primary_location` intent (per admin help text) | `service_areas` intent (per admin help text) | Real-world operator mental model (inferred) |
|----------|--------------------------------------------------|------------------------------------------------|---------------------------------------------|
| **TRANSPORTATION / TRANSFER** | Hidden in form; field unused | Hidden in form; field unused | N/A — these contracts use `trip.route.departure_station` / `arrival_station` instead. Location is intrinsic to the route, not the contract. The form correctly omits both fields. |
| **DAY_TOUR** | "Home base" — the city where the tour starts. Single point. | All pickup zones / reachable cities. E.g. Phuket tour that picks up in Patong, Karon, Kata. | Operator thinks: "My tour *lives* in Phuket Town but I drive customers from all over the island." |
| **MULTI_DAY_TOUR** | Same as DAY_TOUR — start city. | Cities visited across multiple days. E.g. "Northern Thailand loop" → Chiang Mai, Chiang Rai, Pai, Mae Hong Son. | Operator thinks: "Tour starts in Chiang Mai and visits these places." The M2M is the **itinerary cities**, not pickup zones. |
| **SPA_WELLNESS** | The spa's physical address (city level). | Cities the operator will travel to. Mobile spa? Multiple branches? Hotel partnerships that span cities? | **Ambiguous.** Could be (a) branches of a chain, (b) pickup radius, (c) hotel partners in nearby cities. No category-specific help text. |
| **EVENT_TICKET** | The venue's city. | Other cities where the same ticket/operator runs the event. | Mostly redundant with `primary_location` for one-off events. Plausible only for touring shows. |
| **ATTRACTION_TICKET** | The attraction's city. | Other branches / sister attractions. | Likely always = `primary_location` for single-site attractions. Multi-site (e.g. aquarium chain) is the exception. |
| **FOOD_DINING** | The restaurant's city. | Delivery zones? Branches? Pop-up locations? | Strongest case for `service_areas` ≠ `primary_location` — but the form help text doesn't address delivery. |
| **ACCOMMODATION** | The property's address. | Useless — a hotel "serves" only its own address. | **Likely always redundant.** Strongest case that `primary_location` alone is enough for ACCOMMODATION. |
| **OTHER** | Undefined. Catch-all. | Undefined. | The "OTHER" escape hatch is not actually modeled in help text. |

**Bottom line:** the "service_areas = pickup zones" mental model that the help text uses (`ContractFormFields.js:230` example: "spa with hotel pickup in Patong, Karon, Kata") fits DAY_TOUR, possibly SPA. It breaks for ACCOMMODATION (no pickup) and FOOD_DINING (delivery != pickup). It is a **tour-shaped** model applied to all non-transport categories.

---

## What Works

- **Admin form has the right help text.** `ContractFormFields.js:184` and `:227` clearly differentiate the two fields. A staff member who reads the help text understands the intent.
- **Visibility matrix is correct.** `admin-dashboard-contracts.md:24` correctly hides both fields from TRANSPORTATION. The category gating at the form level is sound.
- **The 2026-06-01 fix closed the customer-side hole.** `products/views.py` now ORs `primary_location` into the search filter, so customers typing "Phuket" do find Phuket contracts whether the operator set `primary_location` or `service_areas`. `[[08-archive/.originals/activities-location-search-bug-2026-06-01.original]]` Fix 1.
- **Migration history is clean.** `0045_add_tour_fields.py` adds both fields in one operation with consistent `related_name` choices (`contracts` vs `tours_in_area`). No "we bolted on service_areas later" tech debt.
- **The auto-suggest endpoint correctly aggregates both.** `activities-search-merge-review-2026-06-01.md:114` — `getActivityLocations` distinct-unions both fields, so the dropdown is complete.

---

## Open Questions

1. **Where does `primary_location` actually appear on the customer-facing PDP?** The admin help text says "display and branding on the product page" but I could not find a vault note describing which component reads `contract.primary_location` on the PDP. This is a **gap in vault coverage of the customer journey**, not necessarily a code gap — but if no component reads it, the "for upselling" model `help_text` is the more accurate description and the form help text is aspirational.
2. **Is there ANY upselling logic on `primary_location`?** Search `smartenplus-backend` for `/upsell/`, `recommendations`, or `primary_location` joined to a user-context query. If not, the "for upselling" `help_text` is dead documentation.
3. **Does the PDP ever show `service_areas` (plural)?** If not, the M2M is used only for **search** — it's a backend index, not a customer-visible attribute. This would validate the "two-field split is for backend performance / filter granularity" theory.
4. **For ACCOMMODATION, why does the form show `service_areas` at all?** The form has no category-specific hiding for ACCOM. If ACCOM operators never populate it, the field is a data-quality trap.
5. **Who owns the field-naming decision now?** Three documents (the 2026-06-01 bug audit, the migration help text, the admin form help text) describe the same two fields with three different framings: "upselling", "display and branding", and "discoverability via search". A 1-line ADR would resolve the contradiction.
6. **Was the help text in `ContractFormFields.js` added before or after the 2026-06-01 OR-fix?** The help text says `primary_location` is "Not used for customer location search" — but the OR-fix made it exactly that. Either the help text is now stale, or the OR-fix is wrong, or both fields should be considered search-relevant going forward. A deliberate decision is missing.

---

## Severity Summary

| Priority | Count | Items |
|----------|-------|-------|
| P0 (breaks customer experience) | 2 | D-1 (help text contradicts code), D-3 (intent unstable across docs) |
| P1 (staff confusion costing time) | 4 | D-2 (model vs form help text), D-4 (no visual hierarchy), D-5 (per-category UX missing), D-6 (dropdown mixes fields), D-9 (silent null failure) |
| P2 (doc/cleanup) | 3 | D-7, D-8, D-10 |

---

## Related

- [[admin-dashboard-contracts]] — visibility matrix source
- [[08-archive/.originals/activities-location-search-bug-2026-06-01.original]] — Debate 3 (prior unresolved framing)
- [[contract-trip-null-non-transport-pattern]] — companion null-guard
- [[contract-serializer-non-transport-fields-2026-06-03]] — serializer gap, related to D-8
- [[transportation-category-audit-2026-05-30]] — Level-1 / Level-2 classification
- [[activities-search-merge-review-2026-06-01]] — `getActivityLocations` endpoint
- [[stations]] — `Location` model hierarchy
- [[01-projects/operators]] — Contract model + service_category enum
