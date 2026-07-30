# Airport-Transfer Competitor Review & Improvement Plan 2026

## Summary
5-agent review (UXUI, BD, MK, Next.js, Django) of SmartEnPlus airport-transfer across FE+BE+AD, benchmarked vs Thai airport-transfer platforms. Verdict: the product is thin (transport-mode only, near-empty catalog) and invisible on the trust signals every competitor leads with. **Zone-based pricing** is the single highest-leverage fix — and it needs almost no new code (existing schema already supports it as pure data). Decision on the zone model → [[adr-airport-transfer-zone-pricing]].

## Context
Airport-transfer today = `pages/airport-transfer/[slug].js`, pickup/drop-off tabs that swap from/to, querying `tripsApi.getTrips` with `type:'private'`. Pricing = fixed station→station route + `Contract_RateCard` (VEHICLE qty = `ceil(pax/vehicle_seat)`). No zone concept. Only ~6 charter routes live; TRANSFER category near-empty (see [[products-live-catalog-audit]]). User asked: research Thai platforms, recommend improvements, and evaluate **zone areas for drop-off/pickup with zone pricing** — under hard constraints (no tech debt, no over-engineering, reuse-first, no side effects).

## Problem
Two gaps, both costing conversion:
1. **Catalog architecture** — station-pair pricing needs N×M SKUs to cover a market (~500 for BKK). Users can't find a transfer to their hotel; supply can't be onboarded at scale.
2. **Trust invisibility** — meet-&-greet, fixed price, flight tracking, free waiting time, free cancellation are the sector's standard trust signals; SmartEnPlus surfaces none of them, despite already having fixed prices.

## Details

### Competitor matrix (Thailand airport transfer)
| Platform | Pricing | Meet&Greet | Flight track | Free wait | Cancellation | Lead trust signal |
|---|---|---|---|---|---|---|
| Welcome Pickups | Per-vehicle fixed, tolls incl. | Named sign | Yes (proactive) | 60 min | Flexible | English driver + flight monitor |
| Kiwitaxi | Per-vehicle fixed, "pay what you see" | Named sign | 30-min adjust | 90 min | Premium=anytime refund | Fixed fare locked at checkout |
| GetYourGuide | Per-vehicle, reserve-now-pay-later | VIP tier | Yes | 30 min | **Free cancellation (headline)** | Free cancellation in page title |
| Klook | Aggregated fixed | Named sign | Yes | Varies | 24h free | 4.7/832k reviews, instant confirm |
| 12Go | Per-vehicle flat | — | — | — | Varies | SE-Asia multi-modal authority |
| AOT Limo | **Zone-band counter price** | Porter | No | Walk-up | None | Official AOT + police-vetted |

**Underlying market reality:** the two highest-volume airports already price by zone even when the UI says "point-to-point." Phuket has ~7 natural zones (Mai Khao THB 550 → Rawai THB 1,500 sedan); Bangkok clusters into 3 (inner/outer/extended); Samui and Chiang Mai are naturally zoned by geography.

### Zone verdict (BD)
Zone pricing wins commercially: **5 zones × 5 airports = 25 SKUs** cover Thailand vs ~500 station-pairs. It matches how customers think ("I'm going to Kata Beach", not "which station serves Kata"), protects margin (operator prices worst-case distance in-zone), and cuts supply onboarding ~85%.

### Zone verdict (MK)
Do **not** market the word "zone" to customers — market the *outcome*: **"Fixed price — no meter, no surprises."** Zone is the backend mechanism; "fixed price" is the benefit. Layer the message 3× (hero / card / listing), mirroring Kiwitaxi. Bonus angle: "Skip the AOT Limo queue — your driver is already waiting."

### FE feasibility (Next.js)
- **Zone pricing = MODERATE, contained.** Add `zone` param to `tripsApi.getTrips`/`getTripFilterSet` (~2 lines each), a `zone` `useState` in `[slug].js` (orthogonal to `tabValue` swap), a small zone picker in `TripListingSection`. **Untouched:** `TransportationSearch`, `StickySearchBar`, `SearchModeTabs`, `/trips`, `/activities`.
- **Activity-mode listing = NEEDS-NEW** (blocked on a BE list endpoint filtered by airport slug). New `AirportActivitiesSection` reusing existing `DayTripCard`. `getTripDetailPath` already forks routing correctly — no helper change.

### BE feasibility (Django)
- **Zone pricing = Option (c) pure-data, ZERO schema change** recommended first: each zone = one Route (existing `Station` types already include `hotel`/`beach`/`airport`) + one `Contract(service_category='TRANSFER')` + normal `Contract_RateCard`. Admin data entry only.
- **Option (a)** — add one nullable `Station.zone` CharField — only if admin needs to group/filter zones. Additive migration, no FK cascade, `OperatorStationMapping` unaffected, seat-check unaffected, `Contract_RateCard` shape **unchanged**.
- **Option (b)** new Zone+ZoneRateCard table = **REJECTED** (forks the cart/booking pricing loop `carts/utils.py:146-166`, breaks `min_rate` annotation `products/views.py:476`, breaks serializer callers).
- **Meet-&-greet = 1 line + data:** add `('MEET_AND_GREET','Meet & Greet')` to `ContractAddon.ADDON_TYPE_CHOICES`; `ContractDetailSerializer.addons` already serializes it. Optional list-badge = add `addons` to `ContractSerializer` + a `Prefetch`.

### UX findings (severity-tagged, file:line)
- **[CRITICAL]** Pickup/Drop-off tabs swap direction with no visual feedback; both TabPanels render the same content block → false "no results" on the opposite direction. `[slug].js:79-94`, `TripListingSection.js:114-124`.
- **[HIGH]** Search modal on the airport page pushes to `/trips/...`, ejecting the user from the funnel. `[slug].js:108-122,301-326`.
- **[HIGH]** Generic hero title "SmartEnPlus Booking Center" instead of the station name. `AirportTransferHeader.js:48-55`.
- **[MEDIUM]** Dead `pickupMode` state proves a direction-toggle was intended in the header (implemented as tabs instead). `AirportTransferHeader.js:28`.
- **[MEDIUM]** "About All Destinations" bug — `arrivalStation='All Destinations'` fed to `StationInformation`. `[slug].js:290`.
- **[MEDIUM]** Route card shows only "From {price}" — no vehicle class, no "Private", no "Fixed". `AirportTransferRouteCard.js:36-44`.

**UX zone selector (simplest viable):** extend existing `AutoCompleteSearch` (already modal-mounted in `TransportationSearch`) with a "Zones" section in results; select → same `locationActions` payload shape; card copy becomes "Zone price". **No map** (bundle weight, informal Thai boundaries, mobile tap accuracy).

## Prioritized improvements (P0/P1/P2)
Each tagged effort × reuse × blast-radius. Over-engineered options rejected inline.

**P0 (launch-blocking, mostly copy/data — near-zero code)**
- **P0-1 Zone pricing as pure data** (BE Option c) — *effort S · reuse total · blast none*. Onboard HKT (5 zones) + BKK (3 zones) as Route+Contract+RateCard records. No migration.
- **P0-2 Trust-signal copy** at checkout/card — meet-&-greet, "Fixed price · no meter", waiting-time, cancellation. *effort S · reuse total · blast none*. Touches `AirportTransferRouteCard`, `AirportTransferHeader`, SEO component.
- **P0-3 UX crits** — direction toggle in header (reuse `SearchModeTabs` pattern, kill dead `pickupMode`), fix "About All Destinations" one-liner. *effort S · reuse high · blast none*.

**P1 (one sprint)**
- **P1-1 Meet-&-greet via `ContractAddon`** — 1-line choice add + admin data; badge on card via list-serializer `Prefetch`. *effort S · reuse total · blast low (list serializer)*.
- **P1-2 FE zone picker + zone param** — `tripsApi` param + `TripListingSection` selector + `AutoCompleteSearch` zones section. *effort M · reuse high · blast none*.
- **P1-3 Search-modal refetch-in-place** (don't `router.push` for date/pax changes) + station-name hero + vehicle-class badge on card. *effort M · reuse high · blast none*.
- **P1-4 SEO landing** — `Service` schema (`serviceType:"Airport Transfer"`, `areaServed`, `provider`), station-name H1, "fixed price / included / how-it-works" content blocks in existing `StationInformation`. Ties to [[seo-aeo-geo-live-audit-2026-06-22/r14-live-prod-2026-07-11]]. Drop FAQPage JSON-LD (Google deprecated May 2026) but keep Q&A copy for AEO.

**P2 (next quarter)**
- Automated flight-status monitoring + driver notify; USM/DMK zones; child-seat/extra-stop add-ons; operator review count + free-cancellation badge on cards; `AggregateRating` schema.

**Rejected (over-engineering):** new Zone/ZoneRateCard table; zone Redux slice / zone context / separate zone search form; map-based zone picker; merging activity items into transport `FilteredTripList`.

## Tradeoffs
- Pure-data zones (no `Station.zone`) = zero code but no admin grouping/filtering; add the field later only when a real admin need appears (YAGNI).
- Activity-mode airport listing deferred — needs a new BE endpoint; meet-&-greet delivers the same customer value at 1-line cost, so ship that first.

## Consequences
- Zone pricing unblocks a real transfer catalog (HKT/BKK first) without a migration — commercial launch gated on data + copy, not engineering.
- Build work splits into shippable slices; no change touches `/trips` or `/activities`.

## Related
- [[adr-airport-transfer-zone-pricing]] — the zone-model decision
- [[products-live-catalog-audit]] — thin transfer catalog evidence
- [[transfer-category-vs-airport-filter-independence]] · [[station-type-airport-first-class-iata-restriction]]
- [[seat-availability-reseller-operator-gap]] · [[station-mapping-multi-operator-design]]
- [[adr-operator-scoped-trip-station-override]] — shared-Trip ripple (relevant to zone Route creation)
