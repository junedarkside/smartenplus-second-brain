---
name: stationsinfo-contracts-field-is-intercity-not-zone
description: The `contracts` field on the /stationsinfo/{slug} endpoint returns intercity trip contracts (Contract.objects.filter(trip__route__arrival_station=obj)), NOT zone transfer prices. Never use it to display airport transfer pricing.
type: knowledge-atom
date: 2026-08-04
---

# stationsinfo `contracts` Field = Intercity Trips, Not Zone Prices

## The Trap

`/stationsinfo/{slug}` response includes a `contracts` array. On the airport transfer detail page (`/airport-transfer/[slug]`), it's tempting to use `Math.min(contracts[*].rate)` as a "from price" anchor in the hero.

**This is wrong.** The field returns intercity bus/van trip contracts, not airport zone transfer prices.

## Backend Source

```python
# stations/serializers.py (stationsinfo endpoint)
contracts = Contract.objects.filter(trip__route__arrival_station=obj)
```

`trip__route__arrival_station` = intercity trip routes arriving at this station. These are bus/van contracts — price, schedule, operators for trips *to* this airport, not private zone transfers *from* it.

## Zone Transfer Prices

Zone pricing lives in `TransferZone` model (stations app, migration 0030). Accessed via `/api/resolve-zone/` endpoint with lat/lng → polygon lookup → fixed rate. Not included in `stationsinfo` response.

## Rule

On `/airport-transfer/[slug]`: do not derive or display price from `stationsinfo.contracts`. Use `ZonePriceBox` (which calls `resolve-zone`) for pricing. If no zone resolved yet, show no price — don't fall back to intercity contract rates.

## Where It Was Misused

`AirportTransferHeader.js` had a `fromPrice` prop chain deriving `Math.min` from `contracts` and showing "Private transfers from THB X · Fixed price, no surge". Removed 2026-08-04 — wrong product, wrong data source.
