# ADR — Airport-Transfer Zone Pricing (+ Activity-Mode Surfacing)

**Status:** Accepted — **Slices 1–4 built + tested** (zone core, AD draw page, FE picker, coord persistence) + **Slice 6 = multi-contract-per-zone built** (see §6) + **Slice 7 = multi-airport-per-zone built** (see §7). **§8 = known limitation documented, fix deferred; §9 = fix built same-day, superseding §8** (contract×airport scoping within a shared zone). Branches unmerged: BE `feat/airport-transfer-zone-pricing`, FE `feat/airport-transfer-zone-picker`, AD `feat/transfer-zone-admin`. Superseded the initial tag-based approach after 2 rounds of user clarification + a 4-agent polygon debate.
**Date:** 2026-07-30 (§6 added 2026-08-01, §7 added 2026-08-14, §8 added 2026-08-14, §9 added 2026-08-14)
**Deciders:** 5-agent review (UXUI, BD, MK, Next.js, Django) + 4-agent shape debate (Django/geo, Next.js/maps, BD/ops, UXUI) + user
**Full context:** [[airport-transfer-competitor-review-2026]]

## Context
Airport-transfer prices are fixed **station→station** (`Contract.trip` FK → Route(Station→Station) + `Contract_RateCard`, VEHICLE qty `ceil(pax/vehicle_seat)`). Covering a market needs N×M route SKUs (~500 for BKK). 

**Requirement evolved through clarification** — user wants pickup/dropoff = **any address in Thailand (hotel/home/Airbnb)** typed via **Google Places autocomplete** → selection returns **lat/lng** → lat/lng resolves to a geographic **ZONE** → zone sets a **fixed price** → exact address + lat/lng saved on booking for the driver. Unbounded address input **forces** an address provider (can't seed millions of addresses); price stays coarse (few zones/airport), exact point is booking data. Constraints: no tech debt, no over-engineering, reuse-first, no side effects, never change a shared serializer/helper return shape.

Secondary: activity-mode airport options (meet-&-greet, add-ons) exist in the model (`ContractAddon`) but aren't surfaced on the airport page.

## Problem
Add address-input + zone pricing without: (a) forking the cart/booking pricing loop, (b) changing `Contract_RateCard` shape (breaks all callers — CLAUDE.md rule #4), (c) touching `/trips` or `/activities`, (d) an over-built pricing/geo table, (e) installing PostGIS.

## Decision

### 1. Zone = airport-anchored POLYGON, priced by an existing Contract. Google Places + lat/lng resolves it.
New `TransferZone` model (`stations/models.py`): `airport` FK→`Station`, `name`, `boundary` **JSONField** (`[[lat,lng],…]` vertices), `contract` FK→`operators.Contract`, `priority` (overlap tie-break), `is_active`. **Zone price = its Contract's existing `Contract_RateCard`** (`'TRANSFER'` already in `_TRANSPORT_CATEGORIES`) — pricing engine + ratecard shape **untouched**. 

**Resolution = ray-casting, NO PostGIS:** `stations/geo.py` `_point_in_polygon()` (~15 lines) + `resolve_zone(airport,lat,lng)` (first active zone by `-priority` containing the point; `None`→gap fallback). Read-only endpoint `GET /stations/resolve-zone/?airport=&lat=&lng=` → `{zone,contract,price}`. Server-authoritative (no client geometry leak).

**Address input:** Google Places autocomplete — `react-places-autocomplete`+`@react-google-maps/api` **already installed FE** (demo `components/search/autocompleteinput.js` already extracts lat/lng, `country:['th']`). Lift into `components/airport-transfer/PlacePicker.js`. Client-side lib → **no server Google key**; add restricted `NEXT_PUBLIC_APP_GMAP_API_KEY`.

**Exact point persistence (additive):** add `pickup/dropoff lat/lng` cols to `bookings/models.py InfoFields` + `carts/models.py CheckoutInfo`; wire two `.get()` sites in `carts/utils.py`. `InfoFieldsSerializer(fields='__all__')` auto-serializes to booking detail/PDF. Existing text `pickuppoint` preserved.

**Gap fallback (must-have):** lat/lng in no polygon must NOT dead-end a booking — per-airport catch-all zone (lowest priority) or nearest-centroid with disclosure. Build before first zone live.

### 1b. Shape verdict — POLYGON only (4-agent debate).
Debated polygon vs circle(center+radius) vs hybrid, judged simplest-meets-accuracy. Django/geo + Next.js/maps → polygon; BD/ops → hybrid (Phuket headlands misprice); UXUI → circle for admin simplicity. **Resolved: polygon only** — a circle is a low-vertex polygon, so **one model subsumes both**, collapsing hybrid's two-code-path cost into "draw fewer vertices for simple zones." Decisive: `@react-google-maps/api` `DrawingManager` is **already in the installed lib → zero new dep** for polygon draw. BD's phasing = rollout (precise Phuket polygons, rough few-vertex benign airports), not a second architecture.

### 2. Customer-facing copy = "Fixed price", never "zone".
"Zone" is the backend mechanism; the customer benefit is price certainty. Layer "Fixed price · no meter" at hero / card / listing (MK). FE surfaces it in the existing price slot (`AirportTransferRouteCard.js:36-44`) — no structural change.

### 3. Meet-&-greet via existing `ContractAddon` (1 line + data). Full activity listing deferred.
Add `('MEET_AND_GREET','Meet & Greet')` to `ContractAddon.ADDON_TYPE_CHOICES` (`operators/models.py:1017-1028`) — no migration (CharField choices aren't DB-enforced). `ContractDetailSerializer.addons` already serializes it. Optional list badge = add `addons` to `ContractSerializer.Meta.fields` + `Prefetch('addons', ...)` on `products/views.py` list queryset (isolated to list serializer). **Full activity-mode airport listing is deferred** — it needs a new BE endpoint filtered by airport slug + a new `AirportActivitiesSection` (reusing `DayTripCard`); meet-&-greet delivers the same value cheaper, ship it first.

### 4. Admin draws polygons — AD map page (click-to-draw).
Polygon vertices can't be hand-typed reliably → AD page with `@react-google-maps/api`. **UPDATE (build): Google REMOVED `DrawingManager` in Maps JS v3.65** (deprecated Aug 2025, removed June 2026) — the debate's "DrawingManager = zero new dep" premise is dead. Pivoted to **click-to-draw**: capture `GoogleMap onClick` → append vertex → render `<Polygon editable>` once ≥3 (vertex-drag edits still supported; only the `DrawingManager` *class* was removed, not `Polygon`/`editable`). **Still zero new drawing dep, no Terra Draw** — plain click handlers (~30 lines, `components/transfer-zones/ZoneMap.js`). Only `libraries:['places']` needed now. **Validity guards on save:** min 3 vertices, priority for overlaps. Django admin = power-user fallback. Price still edited in existing AD contract pages (zone→contract pointer).

### 6. Multi contracts per zone — M:N via `ZoneContract` link table, traveler picks (2026-08-01).
**Supersedes §1's `TransferZone.contract` single FK.** Staff need one zone priced by **many contracts/operators** (different operators, vehicle types), assignable from **both** the AD contract page and the zone page; the traveler sees **all contracts as options** and picks one.

**Decision:** new `ZoneContract` link table (`stations/models.py`) — `zone` FK(CASCADE), `contract` FK(PROTECT), `is_active`, `unique(zone,contract)`. Same M2M-through idiom `Contract` already uses for ratecard/transport_composit/info_fields — **not new tech**. Old `TransferZone.contract` FK **kept but deprecated** (help_text), data-migrated into one `is_active` link per zone (migration `0032`, reversible), then **never read** by any code path (one read path, no ambiguity). No destructive drop.

**Resolution now returns options[]:** `ResolveZoneView` response changed `{contract_id, price}` → `{matched, zone, options:[{contract_id, contract_name, price}]}`, one option per active linked contract, each price = that contract's MIN active `selling_rate` (existing query, per-contract). Empty active links → `matched:false`. `resolve_zone()` geometry + `Contract_RateCard` **untouched**.

**One write path both sides:** `stations/services.py sync_zone_contracts(zone, contract_ids)` + mirror `sync_contract_zones(contract, zone_ids)` share one row-diff (create/deactivate, never hard-delete → keeps history, dodges PROTECT). Zone page submits `contract_ids` via `TransferZoneSerializer` (writable list, reads back `contracts[]`); contract page hits `POST /admin-dashboard-stations/contract-zones/` (+ `GET .../{id}/` prefill), both routing to the same helper — no drift.

**FE `ZonePriceBox` → tier cards** over `options[]`; new `ZoneOptionCard` fetches its own full contract per Book (reuses existing Immer-clone, `stashTripInfo`, `loginUserId`, `BookButton`). `matched:false` soft-state unchanged.

**Scrutiny cuts (kept minimum):** dropped a per-link `label` (duplicates contract/operator name → drift) and `is_default` (no consumer — traveler picks all). Add only if ops ask. `ZoneContract` = pure link table.

**Blast radius = 1 shape change (resolve-zone response), grep-verified 3 consumers** — FE `ZonePriceBox`, AD `TestLocationPanel` (both updated to `options[]`), FE query def (passthrough). Migrated single-contract zone → one-item options = behaviorally identical to old single price (regression-tested). 19 stations tests pass. Untouched: `/trips`, `/activities`, `BookButton`, checkout, booking write path (Slice 4a).

**Rejected here:** geometry+`ZonePricing` through-table returning a price *and* boundary-reuse self-FK (`boundary_source`) — solved a different problem (draw-once shape reuse), not the stated multi-contract need. M:N link is the honest model.

### 6b. Zone contracts restricted to PRIVATE/CHARTER — JOIN blocked (2026-08-01).
**Which `Contract.type` may link to a zone.** Scan found no gate: BE FK, AD zone picker, and FE all accepted any type, and the traveler widget (`ZonePriceBox`) **hardcodes ADULT=1/total=1** (no passenger selector). By type: **PRIVATE/CHARTER** → `ceil(1/seats)=1` vehicle, flat per-vehicle price = correct; **JOIN** → per-seat ratecard locked to 1 adult → a group silently under-books (family of 4 pays 1 seat). BD+UXUI debate → **allow PRIVATE+CHARTER, block JOIN.** CHARTER kept (booking math identical to PRIVATE, `VEHICLE` ratecard, safe; blocking it would be taxonomy opinion not correctness). **JOIN block is correctness + deferred, not permanent** — re-enable once the widget gains a pax selector.

**Enforcement (nextjs+django+senior-reviewed, 4 corrections folded):** SSOT helper `stations/services.py assert_zone_eligible(contract_ids)` raises **DRF** ValidationError → clean 400 (not django's → would 500). Called from `TransferZoneSerializer.validate_contract_ids` (zone page) + `SetContractZonesView.post` (contract page). `ZoneContract.clean()` (django ValidationError) seals the Django-admin inline path. Rule NOT buried in `_apply_diff` (kept a pure diff util; it's side-blind to which arg is the contract). **Migration `0033`** deactivates legacy active JOIN links that migration 0032 backfilled without a type filter — else the first admin edit of such a zone 400s (live-caught: contract 184/zone 2 was JOIN, now `is_active=False`). AD `ZoneForm` reuses the existing `?contract_type=PRIVATE,CHARTER` param → JOIN never in the picker; chips resolve against the (already JOIN-free) active list, no MUI crash. 28 stations tests pass (+6). Zero side effect on resolve geometry / `Contract_RateCard` / booking.

### 7. Multi airports per zone — M:N via `ZoneAirport` link table, ops-driven zone reuse (2026-08-14).
**Supersedes §1's `TransferZone.airport` single FK.** Staff need one zone (e.g. "Chiang Mai Zone A/B/C") reusable across **multiple airports** — both CNX and CEI can each offer transfer into the same Chiang Mai zone, not just its own airport-exclusive zone set. Exact precedent as §6, mirrored onto the other side of `TransferZone`.

**Decision:** new `ZoneAirport` link table (`stations/models.py`) — `zone` FK(CASCADE), `airport` FK(CASCADE, `limit_choices_to={'station_type':'airport'}`), `is_active`, `unique(zone,airport)`. Same M2M-through idiom as `ZoneContract` — not new tech, not a new pattern to learn. Old `TransferZone.airport` FK **kept but deprecated** (made nullable, help_text updated), data-migrated into one `is_active` link per zone (migration `0035`, reversible, mirrors `0032`'s shape), then **never read for resolution** by any code path — `TransferZone.__str__` guards the now-nullable FK instead of crashing.

**`resolve_zone(airport_id, lat, lng)` unchanged signature/return, changed query:** filters `TransferZone` through `zone_airports__airport_id=` + `zone_airports__is_active=True` instead of the flat `airport_id=` FK match, `.distinct()` added defensively. `ResolveZoneView` response shape **untouched** — it only ever read `zone.id`/`zone.name` from the result, never `zone.airport`, so this is a pure internal-query change with zero blast radius on the one shared (non-admin) consumer, `resolveZone` in FE `store/api/tripsApi.js` → `ZonePriceBox.js`.

**One write path, mirrors `sync_zone_contracts`:** generalized `_apply_diff(model, fixed_field, fixed_id, var_field, var_ids)` in `services.py` to take the link-table model as a param (was hardcoded to `ZoneContract`) — both `sync_zone_contracts`/`sync_contract_zones` now pass `ZoneContract` explicitly, new `sync_zone_airports(zone, airport_ids)` passes `ZoneAirport`. Same row-diff (create/deactivate, never hard-delete). `TransferZoneSerializer` gains `airports`/`airport_ids` alongside the existing `contracts`/`contract_ids`, `validate_airport_ids` checks `station_type='airport'` (one query, no eligibility gate needed — no JOIN-style restriction applies to airports).

**Admin list/filter:** `TransferZoneViewSet.filterset_fields=['airport','is_active']` (exact-FK auto-filter) replaced with a custom `TransferZoneFilterSet` — `?airport=` now filters through the active `ZoneAirport` link, transparent to the FE (same query param name, same semantics from the caller's POV). `queryset` swapped `select_related('airport')` → `prefetch_related('zone_airports__airport')` to avoid N+1 on the new `airports` serializer field.

**FE `ZoneForm.js`:** single `Autocomplete` → `multiple` (mirrors the `contract_ids` picker already in the same file). `TestLocationPanel`'s map-test tool still resolves against one airport at a time by design (ops verifies a specific pickup point) — when a zone has >1 linked airport, a small `Select` lets ops choose which linked airport to test from, defaulting to the first.

**Scrutiny cuts:** no eligibility/type gate on `airport_ids` beyond `station_type='airport'` (unlike §6's JOIN-contract block) — there's no equivalent correctness hazard for airports, so no `assert_*_eligible` helper was added. Considered and rejected a separate "airport → zones" reverse-picker APIView (`SetContractZonesView` equivalent) — the zone-side `airport_ids` write already covers the stated requirement; add only if ops asks to assign from the airport side.

**Blast radius = 1 internal query change (`resolve_zone`) + 1 filterset swap, zero response-shape changes.** Migrated single-airport zone → one-item `ZoneAirport` link = behaviorally identical to old single-FK resolution (regression-tested). 36 stations tests pass (+6 vs. §6's 30). Untouched: `ResolveZoneView` response shape, `resolve-zone` request params, `/trips`, `/activities`, booking write path, `products/serializers.py`/`bookings/serializers.py`/`carts/serializers.py` (still correctly read the deprecated single `zone.airport` for booking-time display — that's the airport the traveler actually searched from, not the zone's full airport list).

**Rejected here:** decoupling `TransferZone` from `airport` entirely (zone = pure geometry, `resolve_zone(lat,lng)` with no airport param) — user confirmed origin airport still matters for the resolve flow and per-airport contract pricing; that's a bigger reframe solving a problem not asked for.

### 8. Known limitation — contracts are zone-wide, not airport-scoped within a shared zone (2026-08-14, no code change).
**Gap:** §6 (`ZoneContract`) and §7 (`ZoneAirport`) are independent M:N tables with no relationship to each other. `resolve_zone(airport_id, lat, lng)` finds a zone via `ZoneAirport`, but `ResolveZoneView` then returns **all** of that zone's active `zone_contracts` — `airport_id` is discarded after the zone match, never used to filter which contracts are offered. So once a zone is shared across multiple airports (§7's whole point), every contract linked to it is offered from every linked airport, with no way to restrict a contract to only be bookable via a specific one.

**Real-world risk:** an operator whose fleet is physically stationed at only one airport (airport-exclusive concession, common at Thai airports where AOT slots differ per airport) would incorrectly surface as bookable from a second airport sharing the same zone — traveler could book a transfer the operator can't fulfill.

**Reviewed by a 4-agent team (BD/ops, Django, Next.js, SWE) on 2026-08-14** — full reports in that session's transcript. BD recommended fixing now (real ops risk, low fix cost); SWE recommended waiting (zero-code workaround exists, no real operator hitting it yet, feature still mid-slice — Google Maps billing blocker open, §7 not yet browser-tested/merged). Django and Next.js designed the fix assuming it gets built, independent of timing: a nullable `airport` FK directly on `ZoneContract` (`null` = unrestricted/current behavior, set = restricted to one airport) — not a new 3-way junction table — plus a one-line `Q(airport__isnull=True) | Q(airport_id=airport_id)` filter in `ResolveZoneView`. Zero customer-FE impact either way (server-side filtering only); admin FE would need a small optional per-contract airport-scope control on `ZoneForm.js`, not a matrix UI.

**Decision: WAIT.** User chose the zero-code operational workaround over building the fix now. **Operational rule (do this instead of code):** if an operator is airport-exclusive, do not link that operator's contract to a zone shared with an airport it doesn't serve. Create a separate `TransferZone` row scoped to just that airport instead (duplicate the polygon if the shape is the same) and link the exclusive contract only there. This fully closes the gap with existing tooling — cost is a duplicate zone row (re-drawn/copied boundary) whenever shared geometry meets exclusive vendors, which is judged cheaper than the schema change until a real operator actually needs both shared geometry *and* per-airport exclusivity at once.

**Revisit trigger:** a real operator reports (or ops discovers) an airport-exclusive-fleet conflict on a shared zone that the workaround can't reasonably absorb (e.g. too many zones needing duplication). At that point, build the deferred design above — it's fully specified, no re-discovery needed.

### 9. Fix built — `ZoneContract.airport` pin, superseding §8's WAIT (2026-08-14, same day).
**Trigger for reversal:** user walked through a concrete numeric example in the same session: Contract-001 (Company A, fleet only at CNX), Contract-002 (Company A, fleet only at CEI), Contract-003 (Company B, fleet only at CEI) — all three linked to shared "Chiang Mai Zone A" (itself linked to both CNX and CEI). Searching CEI → Zone A returned all three; correct answer is only 002 and 003. This concrete, undeniable case is what flipped the decision from "wait for a real operator" to "build now" — same session, no new information beyond making the abstract gap concrete.

**Second review round:** a more rigorous 3-agent team (Django, Next.js, SWE — BD dropped since the business case was no longer in question) validated the §8 candidate design against this project's actual CLAUDE.md rules rather than rubber-stamping it. Two corrections surfaced and were adopted:
- `unique_together` on `ZoneContract` stays `('zone','contract')`, **not widened** to include `airport` — Django review confirmed by reading the model that Company A's CNX-pin and CEI-pin are already two separate `ZoneContract` rows (different `contract_id`s under the same `zone_id`), which the existing constraint already permits. Widening would only matter for "one contract, multiple airport-scoped rows," which isn't the requirement.
- Added a `clean()` gap-check (not in the original candidate): nothing stopped pinning a contract to an airport the zone itself isn't linked to via `ZoneAirport` — a silent dead-pin. Mirrors the existing JOIN-contract gate's pattern in the same `clean()` method.

**Shipped:**
- `stations/models.py` — nullable `ZoneContract.airport` FK (`limit_choices_to={'station_type':'airport'}`, `related_name='zone_contract_pins'`). `null` = unrestricted (default, current behavior for every pre-existing row). `clean()` extended with the gap-check above.
- Migration `0036_zonecontract_airport.py` — single additive `AddField`, no backfill (NULL is correct for 100% of existing rows, not a value to compute).
- `stations/views.py ResolveZoneView` (~line 707) — one-line filter: `zone.zone_contracts.filter(Q(airport__isnull=True) | Q(airport_id=airport_id), is_active=True)`. `resolve_zone()` in `geo.py` untouched — constraint applies one layer up, where `airport_id` is already in scope. Response shape unchanged (`{matched,zone,options[]}`) — zero blast radius on the one shared (non-admin, `AllowAny`) FE consumer.
- `stations/services.py` — **`_apply_diff` left untouched** (confirmed by both Django and SWE reviews: it's a strict 2-key existence diff, adding a 3rd "pin" dimension risked the tested idempotent-reactivate behavior). New standalone `set_zone_contract_airport(zone_id, contract_id, airport_id)` — direct fetch-clean-save on an already-identified row (goes through `clean()`, not a bare `.update()`, so the gap-check actually runs; re-raises as DRF `ValidationError` → 400, matching `assert_zone_eligible`'s convention).
- `stations/serializers.py` — `ZoneContractSerializer` gains `airport` in its read output. `TransferZoneSerializer` gains write-only `contract_airport_pins: {contract_id: airport_id|null}`, applied via `_apply_contract_airport_pins()` after `contract_ids` syncs the links (so the row to pin already exists).
- `stations/tests.py` — new `ZoneContractAirportPinTests`, mapped directly to the 001/002/003 example: resolve-from-CNX excludes the CEI-pinned contract, resolve-from-CEI excludes the CNX-pinned one (the exact bug repro), regression for all-unpinned zones, `clean()` rejection of a dead-pin (both at the model level and re-raised as DRF 400 through the service). 42/42 stations tests pass (+6 vs. §8's 36).
- **Admin dashboard** `components/transfer-zones/ZoneForm.js` — zone-side only (contract-page's `TransferZonesSection.js` intentionally left airport-unaware, see Scope below). `contract_airport_pins` formik field added alongside the existing `contract_ids`. Per-chip pin control via the contracts `Autocomplete`'s `renderTags` — click a chip to cycle unrestricted → each linked airport → back to unrestricted — **shown only when the zone has >1 linked airport**; single-airport zones render identical plain chips, no UI change visible for the common case.
- **Customer-facing `smartenplus-frontend` — zero changes**, confirmed directly by reading `store/api/tripsApi.js` and `ZonePriceBox.js`/`ZoneOptionCard.js`: filtering is entirely server-side, the `resolveZone` request/response contract is untouched, and once the backend returns the correctly filtered list the customer page displays it automatically.

**Scope decision:** pin is settable from the **Zone edit page only**. `components/contracts/TransferZonesSection.js` (the reverse-direction picker, contract page → zones served) and its backing `getContractZones`/`setContractZones` endpoints keep their flat `zone_ids` shape — can still link/unlink a zone, just can't set the pin from that side. Chosen as the minimum that fixes the reported bug; extending symmetrically was considered and deferred (zone-side already has the airport list in scope to render the picker; contract-side would need to fetch it separately).

**Rollout order:** BE shipped first — the new column defaults to `NULL` on every row, so BE alone changed nothing observably until AD lets a row's `airport` actually be set. No broken intermediate state either order.

## Alternatives rejected
- **PostGIS / GeoDjango** — over-engineering for <20 zones/airport + low query volume; installs GIS extension + GDAL + Docker image swap. Ray-casting over ~200 vertex-iterations/booking is ample.
- **`ZoneRateCard` / new pricing table** — forks the pricing loop (`carts/utils.py:146-166`), zeroes `min_rate` annotation (`products/views.py:476`), breaks serializer callers. Zone→Contract FK reuses the existing engine.
- **Circle+radius as a separate zone type** — a low-vertex polygon subsumes it; two types = needless second data-entry + resolution path.
- **Hybrid (circle + polygon)** — two code paths + discriminator; polygon-only handles both. Rejected as more complex than committing to polygon.
- **`shapely` now** — defer; hand-rolled ray-casting = zero dep. Add one line only if boundary-validation/union needed later (interface unchanged).
- **Turf.js client-side point-in-polygon** — leaks full pricing geometry to browser + bundle cost. Resolve server-side.
- **Seeding all hotels/homes/Airbnb as Stations** — millions of rows, stale immediately; Google Places supplies unbounded input live.
- **Per-hotel Route+Contract** — N×M explosion; zone polygon prices the area, exact hotel = booking data.
- **Merging activity items into transport `FilteredTripList`** — component shaped for route/station data; activity renders wrong.

## Tradeoffs
- Google Places = paid API (per-session Places billing) + a restricted key to manage — accepted as the only way to get unbounded Thailand address coverage (hotels/homes/Airbnb).
- Zone polygons need someone to draw + maintain boundaries (Phuket ~2-3h once, occasional edits). Fewer, rougher polygons for benign airports keep this cheap.
- Airbnb exact unit stays private (guest types it); Places resolves building/soi/condo — good enough for pricing + driver nav.
- Ray-casting (not PostGIS) means no DB-level spatial index — irrelevant at <20 zones/airport, low volume.

## Consequences
- Launch gated on: `TransferZone` model + `geo.py` + endpoint + AD draw page + Google key + additive coord cols. All additive migrations; `Contract_RateCard` untouched.
- Zero blast radius on `/trips`, `/activities`, `StickySearchBar`, existing `/stations/?search=`, non-airport info fields.
- Gap fallback is a launch blocker — no valid Thailand address may dead-end a booking.
- Activity-mode airport listing remains a clean future option (routing via `getTripDetailPath` already works).

## Build sequencing (future sessions, off this ADR)
1. **BE zone core:** `TransferZone` polygon model + `stations/geo.py` ray-casting + `resolve-zone` endpoint + gap fallback + zone CRUD + tests. No FE dep.
2. **AD draw page:** `DrawingManager` polygon draw/edit/save + validity guards + priority. Seed Phuket (precise) + benign airports (few-vertex).
3. **FE picker:** lift `autocompleteinput.js` → `PlacePicker` (extract lat/lng) + `resolveZone` RTK query + price display + restricted key.
4. **Coord persistence:** additive lat/lng cols cart→booking, wire `.get()` sites.
5. **Meet-&-greet (parallel):** 1-line `ContractAddon` choice + `Prefetch` badge + admin data.
6. **Copy + SEO:** "Fixed price" messaging, `Service` schema, direction toggle.
7. **Fast-follow:** driver map-link on booking; GeoJSON boundary import if admin boundaries become available.

## Related
- [[airport-transfer-competitor-review-2026]] — research + full findings
- [[products-live-catalog-audit]] · [[transfer-category-vs-airport-filter-independence]]
- [[seat-availability-reseller-operator-gap]] · [[station-mapping-multi-operator-design]]
- [[adr-operator-scoped-trip-station-override]] — shared-Trip ripple caution when creating zone Routes
