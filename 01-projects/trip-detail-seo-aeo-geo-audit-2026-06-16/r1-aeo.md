# r1 — Answer Engine Optimization (AEO) Findings (Trip Detail)

> Raw specialist output. How the page feeds AI answer engines (ChatGPT, Perplexity, AI Overviews). Synthesis → [[r2-leader-synthesis]].
> Caveat: source-derived (no live localhost DOM); file:line verified.

**6 findings — 3 HIGH, 2 MED, 1 LOW.**

## HIGH

### No FAQPage schema on transport detail — helper exists, proven elsewhere
Page emits only `ProductJsonLd`. Zero pre-formatted Q&A → no signal for "how much / how long / which operator" queries. Day-trip path AND route listing already ship FAQPage.
- Evidence: `components/trips/detail/TripDetailSEO.js:59-64` (Product only; false FAQ claim `:14-15`); precedent `helpers/seo/dayTripSEOUtils.js:320-359` (`generateFAQSchema`), `components/trips/RouteFAQ.js:95-103`, wired `components/trips/FilterTripsPage.js:292`.
- Fix: detail-scoped FAQ builder modeled on `generateFAQSchema`, pull single-product fields from `productData` (stations, route_name, duration, departure/arrival times, operator, lowestRate). Emit via next-seo `FAQPageJsonLd` in `TripDetailSEO.js`. Questions: "How much {from}→{to}?", "How long?", "Who operates?", "What time departs?".

### Only generic Product schema — no TouristTrip/Trip type
Point-to-point transport typed as plain Product. Engines can't infer trip-with-endpoints/times/provider. `Trip`/`TouristTrip` exposes `departureLocation`/`arrivalLocation` (Place), `departure/arrivalTime`, `provider`.
- Evidence: `hooks/useTripSEO.js:190-236` (Product + flattened `additionalProperty` text strings `:213-234`); fields exist on `productData` (`TripDetailsAttribute.js:25-26`, `[...slug].js:124-125`).
- Fix: add second JSON-LD block (TouristTrip/Trip) alongside Product, reuse `generateProviderSchema` (`dayTripSEOUtils.js:381-385`) for provider node. Keep Product for price rich result.

### Core route facts trapped in UI tables/badges/tooltips, not extractable prose
Duration/stops/type/times/stations in icon rows, MUI Tooltips, rate table — engines parse poorly. No factual sentence "{Route} departs {from} at {t}, arrives {to} at {t}, takes {duration} with {operator}". Only prose is operator marketing HTML under an empty `<h2>`.
- Evidence: duration in Tooltip `TripDetailsAttribute.js:86-99`; times in graphic `:44-49`; hero badge `TripDetailHero.js:71-73`; empty h2 `TripDetailContent.js:139-140`.
- Fix: FAQ answers (finding #1) double as extractable prose. Fill empty `<h2>` with route name + one factual summary sentence above route_info. All values already in `productData`.

## MED

### aggregateRating conditional + CSR-only (may be absent from crawled HTML)
Rating gated behind reviews (correct), but reviews are CSR-fetched → may be missing from SSR/ISR HTML the crawler/engine sees. Not echoed in any prose.
- Evidence: `productProperties.js:100-106`; CSR fetch `[...slug].js:74-80`; SSR init `:70`.
- Fix: ensure SSR shell carries `productData.reviews`; include rating in Trip schema + a one-line rating sentence.

### No self-contained answer for canonical "X to Y" queries
Can't answer "How much {from}→{to}?" / "How long?" in one extractable string. Price only in title+table; duration only in tooltip.
- Evidence: price `[...slug].js:135`; duration `TripDetailsAttribute.js:92-94`; contrast listing FAQ `RouteFAQ.js:58-67`.
- Fix: covered by per-product FAQPage — answer strings colocate question entities + answer.

## LOW

### Operator/stations weakly anchored as entities
Operator is a link + Product `brand` string; stations only in `geo.placename` + PropertyValue text. Not typed entities.
- Evidence: brand `useTripSEO.js:90`; stations `:122-124,220-223`.
- Fix: resolved as side effect of Trip schema (#2) — provider=TravelAgency, locations=Place.
