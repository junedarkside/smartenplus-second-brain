# Airport-transfer DETAIL page — conversion research + design spec

**Page:** `/airport-transfer/[slug]` (e.g. `/hatyai-airport`) — the money page. Visitor lands from Google ("hatyai airport transfer") → should book. **Goal: CONVERSION. Scope: FE-only, 0 BE. Deliverable: report + spec (no code).** #282, 2026-08-02. UXUI (ux-research-specialist) + BD (business-analyst-expert) agent team researched best transfer platforms (Klook, GetYourGuide, Welcome Pickups, Kiwitaxi, Blacklane, Transferhood, Booking Taxi). Both converged on same top items. All load-bearing data claims verified against live SSR payload first (index-page lesson: agents over-assert data presence).

## Current page anatomy (mapped top→bottom)
```
[HERO airportThailand1Image]  h1 "Hatyai Airport Transfers"
   title prop = "SmartEnPlus Booking Center"   ✗ no price, no value prop
breadcrumb
[date slide calendar]                          ← friction before any price
ZonePriceBox "Private transfer to your address"  ⚠ FULLY WIRED, looks like a filter, LOW prominence
TripListingSection [Pickup|Dropoff] route cards  ← 2nd Book surface, EQUAL weight → competes
StationInformation → "About All Destinations"    ✗ bug on every airport
GuidesSection (blog)
✗ NO trust band  ✗ NO FAQ  ✗ NO FAQ JSON-LD  ✗ NO mobile sticky bar
```

## ROOT PROBLEM — two competing CTAs, no sequencing
`ZonePriceBox` (address→fixed price, door-to-door) and `TripListingSection` (pick a route, airport→city-zone) are two DIFFERENT products at EQUAL visual weight, same `BookButton`, no sequencing. Visitor whose head-question is "what's it cost to MY hotel?" hits both, sees different prices → confusion → drop-off. Best platforms make **address-first the PRIMARY** (matches "I know my hotel, not abstract zones"); route-list is a labelled SECONDARY "browse". Our page buries the primary.

## Data VERIFIED against live SSR `__NEXT_DATA__` (hatyai-airport)
- ✅ **"From THB X" is real:** 3 contracts, 9 ratecards, `selling_rate` present → **min = THB 400**. `Math.min` over `data.contracts[].ratecards[].selling_rate`, client-side, 0 BE.
- ✅ IATA `HDY`, city `Hatyai City`, province `Songkhla` present.
- ✅ `AirportTransferHeader.js:47` = `title={\`SmartEnPlus Booking Center\`}` → generic-hero bug confirmed.
- ✅ `[slug].js:94` = `const arrivalStation = 'All Destinations'` → "About All Destinations" heading bug confirmed.
- ⚠️ **SSR contract keys = `['end_date','operator','ratecards','slug']` ONLY** — NO `cancellation_policy`, `transport_composit`, `type`, `average_rating`, `booked_count`. → trust badges must be **STATIC honest copy**, NOT payload-derived. Don't gate on absent fields. (async client trip API may carry some, if at all.)
- ⚠️ `bar_rate: null` → anchor on `selling_rate`, NEVER `bar_rate` (would fabricate a struck price).
- `loc.image` null (as on index) but hero uses `airportThailand1Image` → unaffected.

## Reuse (verified present) — copy pattern, don't fork
- `components/trips/RouteFAQ.js` — `FAQPage` JSON-LD via `<details>` + `application/ld+json` (L97,109,119). FAQ template.
- `components/activities/detail/DayTripMobileBookingBar.js` — `fixed bottom-0 z-50 xl:hidden`. Sticky-bar template.
- `components/UI/BadgeChip.js` — trust chips.
- `components/common/Section.js`+`SectionHeader.js` — width parity (`max-w-[1200px]`, `px-4 xl:px-0`).
- `hooks/useFormatPrice.js` — "from" price format.
- `components/destinations/StationInformation.js` — shared About (imported `[slug].js:28`).

## Best-practice verdict on current direction/funnel (post-review) — strategy YES, mechanism NO
- ✅ KEEP: address-first primary funnel (Welcome Pickups/Kiwitaxi/Blacklane lead w/ "type your address"); fixed-price framing; browsable route list as fallback.
- ❌ NOT best-practice: pickup/dropoff `tabValue` direction control. Standard is a directional **`From [x] ⇄ To [y]` swap row** (Google Flights/Booking Taxi), not tabs. Tabs force label→direction translation; airport end is INVISIBLE in the zone picker.
- ❌ Anti-pattern: two FULL Book surfaces at equal weight = choice overload. R2+R8 demote/sequence (pragmatic, keeps inventory) but don't eliminate.
- ⚠️ `arrivalStation='All Destinations'` (`[slug].js:94`) = data smell in UX (placeholder "other end", breaks About heading, non-place route `to`).

## Route list — KEEP, do not remove (answered)
`TripListingSection` (`/trips/{from}/{to}/`) vs `ZonePriceBox` (`/resolve-zone`) = DIFFERENT products. Route list = pick pre-defined airport↔named-place route, works WITHOUT Google (current fallback while billing closed), only listed contracts. Zone picker = door-to-door to ANY typed address, needs Google, any polygon. Removing list breaks no-Google fallback + drops address coverage + discards live inventory. Spec re-SEQUENCES (R8), never removes.

## How direction works today (traced)
Tab (`tabValue`) flips `from`/`to` for BOTH funnels (`[slug].js:95-96`): tab 0 Airport Pickup = airport→your place; tab 1 Drop-off = your place→airport. `departureStation`=this airport (fixed), `arrivalStation`='All Destinations' (literal). Route list fires `useGetTripsQuery({from,to,type:'private'})`. Zone picker uses tab only to pick the coord slot the typed address fills (`ZonePriceBox.js:128`): pickup→dropoff pt, dropoff→pickup pt. One address box; airport end implicit.

## Address search mechanism (traced)
`PlacePicker.js`: `react-places-autocomplete` + Google Maps JS, TH-restricted (`country:['th']`). Type→200ms debounce→suggestions→select→`geocodeByAddress`→`getLatLng`→`onSelect({address,lat,lng})`. lat/lng (not text) → `GET /api/v1/resolve-zone/?airport&lat&lng` → BE `stations/geo.py` ray-casting `point_in_polygon` over active zones ordered `-priority`, first-containing wins, fallback whole-area zone → `{matched,options:[{contract_id,contract_name,price}]}`. ⚠ Google-billing-closed → autocomplete/geocode dead → input disabled (standing AIRPORT-TRANSFER-ZONE blocker).

## SPEC — ROI-ranked, all FE-only 0 BE
| # | Change | ROI | Files |
|---|--------|-----|-------|
| **0** | **Replace pickup/dropoff tabs → `From [x] ⇄ To [y]` swap field** (genuine best-practice direction control; both endpoints visible; also resolves 'All Destinations' smell). ⚠ NOT copy — rewires trips-query direction + ZonePriceBox tab logic + Redux stash. BIGGER, own pass AFTER cosmetic cluster | High (clarity) | `[slug].js` L82,95-96 · `ZonePriceBox.js` L105-107,128 · reuse `PlacePicker` |
| **1** ★ | "From THB 400" price anchor in hero (`Math.min` reduce + 1 prop) | High | `[slug].js`, `AirportTransferHeader.js` |
| **2** | Elevate ZonePriceBox → primary CTA + "Get your fixed price — enter your hotel" headline + Step-1 accent band. Keep DOM pos (needs bookingDate; do NOT move above calendar) | High | `ZonePriceBox.js` L145-150 |
| 3 | Static trust strip (Fixed Price·Flight Tracking·Meet&Greet·Free Cancellation·Private Vehicle) below hero. ⚠ confirm flight-track/meet-greet real w/ ops else drop those 2 | High | new `AirportTransferTrustStrip.js` |
| **4** ★ | FAQ + `FAQPage` JSON-LD (~6 static Q&A, interpolate station_name) after Guides — dual conversion+SEO | High | new `AirportTransferFAQ.js` |
| 5 | Hero copy fix "Booking Center" → value prop | Med-High | `AirportTransferHeader.js:47` |
| 6 | Fix "About All Destinations" heading → station name | Med(trust) | `[slug].js:94` |
| 7 | Mobile sticky booking bar (From THB 400 + See Transfers scroll) | High(mobile) | new `AirportTransferMobileBookingBar.js` |
| 8 | Divider "Or browse available routes" between 2 CTAs + green "Fixed price to your address" badge in ZoneOptionCard | Med | `ZonePriceBox.js` ~45-52 |

**Lowest-risk high-ROI cluster to ship first:** R1+R5+R6 (three ~1-line changes) → then R4 FAQ + R3 trust + R7 sticky.

## DO NOT BUILD (trust-negative / wrong product / no data)
- Fake reviews / "0 reviews" stars — no reviews DB; average_rating/booked_count not in SSR, often 0.
- Countdown / "only 2 seats left" scarcity — private vehicles have no seat pressure; dark pattern, TH/EU consumer-law risk.
- "Book before price rises" false urgency — unsupported.
- `bar_rate` struck-price — it's null.
- 2-col ZonePriceBox+TripList sidebar — mobile-breaks (majority traffic). Keep linear, promote via R2.

## Deferred (needs BE)
Real per-route reviews (data floor ≥5); live booking-velocity scarcity (agg endpoint); CMS FAQ via existing `RouteFAQS` model (serializer+view; static copy interim); cancellation/vehicle badges from contract (fields absent from SSR — needs serializer expansion).

Related: [[airport-transfer-at1-redesign-spec]] · [[nextimage-card-fallback-idiom]] · [[adr-airport-transfer-zone-pricing]] · full plan `~/.claude/plans/check-vault-and-create-composed-pond.md`
