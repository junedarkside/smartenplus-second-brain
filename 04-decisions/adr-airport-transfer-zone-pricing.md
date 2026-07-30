# ADR — Airport-Transfer Zone Pricing (+ Activity-Mode Surfacing)

**Status:** Accepted — **BE Slice 1 built + tested + committed** (branch `feat/airport-transfer-zone-pricing` `3d10a61`, not merged). Slices 2-5 pending. Superseded the initial tag-based approach after 2 rounds of user clarification + a 4-agent polygon debate.
**Date:** 2026-07-30
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
