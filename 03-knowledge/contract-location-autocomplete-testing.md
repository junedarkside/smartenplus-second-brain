# Contract Location Autocomplete — Testing Requirements

**Status: READY TO TEST — scheduled 2026-09-14 morning. Audit + test plan complete. Handbook published.**

## Summary
What can be tested and verified for contract pickup/dropoff location assignment across FE, BE, and Admin Dashboard. Compiled from 3-specialist code review (2026-09-13), corrected 2026-09-13.

## Context
Review spec assumed "Contract stores pickup/dropoff locations with Google Place IDs." **Actual architecture differs.** Contract = product config (zone flags only). `CartItemCheckoutInfo` = where customer-chosen pickup/dropoff coords are stored at checkout.

**PlacePicker is NOT airport-transfer exclusive.** `ZoneGatedField.js` wraps PlacePicker for ANY contract with `pickup_requires_zone=true` or `dropoff_requires_zone=true`. Airport transfer and general-transfer contracts share the same Google autocomplete + zone-resolve flow at checkout.

---

## Actual Architecture

### What Lives Where

| Concern | Model | Fields |
|---------|-------|--------|
| Should pickup be a real address? | `Contract` | `pickup_requires_zone` (bool, migration 0071) |
| Should dropoff be a real address? | `Contract` | `dropoff_requires_zone` (bool, migration 0071) |
| Customer's typed pickup address | `CartItemCheckoutInfo` | `pickup_point` (CharField) |
| Customer's typed dropoff address | `CartItemCheckoutInfo` | `dropoff_point` (CharField) |
| Customer's pickup GPS coords | `CartItemCheckoutInfo` | `pickup_lat`, `pickup_lng` (FloatField, migration 0016) |
| Customer's dropoff GPS coords | `CartItemCheckoutInfo` | `dropoff_lat`, `dropoff_lng` (FloatField, migration 0016) |
| Transfer direction | `CartItemCheckoutInfo` | `direction` (`airport_to_address` \| `address_to_airport`) |
| Which contract resolved the zone | `CartItemCheckoutInfo` | `resolved_contract` (FK, SET_NULL) |

**`place_id` is NOT stored anywhere in BE or FE.** The review spec's expectation of place_id storage does not match the implementation.

### Google Autocomplete Implementation

Both FE and AD use the **geocoder two-step** (not Places geometry):

```
User picks suggestion
    → geocodeByAddress(value)       ← Geocoding API call (2nd network round-trip)
    → getLatLng(results[0])
    → { address, lat, lng } emitted
```

Library: `react-places-autocomplete` 7.3.0 (both repos)
Maps loader: `@react-google-maps/api` 2.13.1 (both repos)
API key env: `NEXT_PUBLIC_APP_GMAP_API_KEY`

FE loads Maps JS at component level via `useJsApiLoader` in `PlacePicker.js` + `autocompleteinput.js` — no global script tag in `_app.js` or `_document.js`.
AD loads Maps JS at component level via `useJsApiLoader` in `ZoneMap.js` only — `TestLocationPanel.js` polls `window.google?.maps?.places`.

### Checkout Flow (Any Contract with Zone Flags)

```
Admin sets Contract.pickup_requires_zone = true
    ↓
Customer hits checkout → Passengers.js
    ↓
ZoneGatedField rendered (isInfoFieldEnabled AND pickup_requires_zone=true)
    ↓
Customer types → Google Places suggestions (PlacePicker.js)
    ↓
Customer selects → geocodeByAddress → { address, lat, lng }
    ↓
ZoneGatedField.handleSelect:
  trips[i].pickupPoint = address
  trips[i].pickupLat = lat
  trips[i].pickupLng = lng
  GET /api/v1/resolve-general-zone/?contract=<id>&lat=<>&lng=<>&field=pickup
    ↓
  matched=true  → pickupZoneMatched=true → Yup passes → Continue unlocked
  matched=false → error shown → pickupZoneMatched=false → Continue BLOCKED
    ↓
CartItemCheckoutInfo: pickup_point, pickup_lat, pickup_lng saved
```

### Key Files Per Layer

**FE (smartenplus-frontend)**
- `components/forms/checkout/ZoneGatedField.js` — **primary component** — wraps PlacePicker for any contract with zone flags; calls resolve-general-zone; sets `{field}ZoneMatched` in Formik
- `components/airport-transfer/PlacePicker.js` — Google autocomplete UI (shared by ZoneGatedField + ZonePriceBox + AddressField)
- `components/airport-transfer/ZonePriceBox.js` — airport transfer PDP only (different flow — no zone-match gate, uses resolveZone not resolveGeneralZone)
- `components/search/AddressField.js` — wraps PlacePicker for airport transfer search bar
- `components/search/autocompleteinput.js` — standalone, NOT wired to checkout (no onSelect prop emit)
- `components/forms/checkout/Passengers.js:1104-1107` — renders ZoneGatedField conditionally; `:666-687` — Yup `.test()` gates on `pickupZoneMatched`/`dropoffZoneMatched`
- `helpers/checkoutPersistence.js:198-201` — serializes lat/lng into BE payload

**BE (smartenplus-backend)**
- `carts/models.py:138-203` — CartItemCheckoutInfo model fields
- `carts/views.py:597-602` — saves pickupLat/dropoffLat from payload
- `carts/utils.py:372-415` — coordinate extraction + fallback + zone booking detection
- `carts/serializers.py:1020-1022` — exposes pickup_lat, dropoff_lat in API response
- `stations/views.py` — `GET /api/v1/resolve-general-zone/` endpoint
- `operators/models.py:380-414` — Contract location config fields

**AD (admin-dashboard)**
- `components/contracts/ContractFormFields.js:91-92, 331` — pickup/dropoff requires-zone logic
- `components/forms/contract/TransferZoneFieldToggles.js` — MUI Switch toggles for zone flags
- `hooks/useContractFormData.js:143-144` — maps API response to Formik initial values
- `components/transfer-zones/TestLocationPanel.js` — Google autocomplete (diagnostic tool only, NOT in contract form)

---

## Existing Test Coverage

### BE Tests (what's covered)

| File | Tests | What's covered |
|------|-------|----------------|
| `operators/tests/test_contract_zone_requirement_save.py` | 4 | PATCH sets pickup/dropoff_requires_zone; unchecking persists false; unrelated PATCH leaves flags unchanged |
| `stations/tests.py:610-695` | ~10 | resolve-general-zone: matched/unmatched, cross-contract isolation, missing/invalid params, flag defaults, independent settability |
| `carts/tests.py` | 14 | Cart dedup, session merge, advance-hour cutoff, timezone — **zero coordinate tests** |

### FE Tests (what's covered)

| File | What's tested | lat/lng tested? |
|------|---------------|-----------------|
| `__tests__/helpers/checkoutPersistence.test.js` | pickupPoint, dropoffPoint (strings), time fields, passengers | **No** |
| `__tests__/helpers/checkoutBackendLoad.test.js` | pickupPoint pass-through, contact merge, passenger merge | **No** |
| `components/autocompletesearch/SearchInput*.test.js` | Search bar autocomplete (stations, not Google Places) | N/A |

PlacePicker.js — **0 tests**
autocompleteinput.js — **0 tests**
ZonePriceBox.js — **0 tests**

### AD Tests (what's covered)

| File | Coverage |
|------|----------|
| `__tests__/cs/csApi.test.js` | CS API only |
| `__tests__/pages/orders/index.test.js` | Orders page only |

Contract location: **0% coverage**

---

## Missing Tests — Priority Order

### BE: Top 5

**BE-1 (P0) — Coordinates persist via save endpoint**
- File: `carts/tests.py` (new class `CartItemCheckoutInfoCoordTests`)
- Under test: `POST /api/v1/cart-checkout-info/save/`
- Input: `tripInfo.pickupLat=13.7563, pickupLng=100.5018, dropoffLat=7.886, dropoffLng=98.3923, direction=airport_to_address`
- Expected: DB row has all 4 coords + direction saved
- Why: No test verifies the coordinate save path at `views.py:597-602`

**BE-2 (P0) — Partial update silently zeroes unmentioned coords**
- File: `carts/tests.py` (same class)
- Under test: same endpoint
- Input: existing row has `pickup_lat=13.75`; PATCH body contains `dropoffLat=7.886` but no `pickupLat` key
- Expected: document whether `pickup_lat` is preserved or set None — this is an active data-loss footgun at `views.py:598` (`trip.get('pickupLat')` → None when key absent)
- Why: if confirmed bug, prevents wrong coordinates sent to operator

**BE-3 (P1) — Coord fallback from CartItemCheckoutInfo on booking creation**
- File: new `carts/tests/test_utils.py`
- Under test: coordinate extraction in `carts/utils.py:372-389`
- Input: `CartItemCheckoutInfo` pre-seeded with `pickup_lat=13.75, direction=airport_to_address`; booking payload has `pickuplat=None, direction=''`
- Expected: `InfoFields` row created with `pickuplat=13.75, direction=airport_to_address` (fallback applied)
- Why: the fallback path is the only path for users who let autosave handle coords then don't resend them at submit

**BE-4 (P1) — is_zone_booking detection controls resolved_contract**
- File: `carts/tests/test_utils.py`
- Under test: `carts/utils.py:394-397`
- Input A: payload with `pickuplat=13.75, pickuplng=100.5` → `InfoFields.resolved_contract` = contract FK
- Input B: all coords None → `InfoFields.resolved_contract` = None
- Why: resolved_contract is used downstream to attribute the booking to the correct zone contract

**BE-5 (P1) — direction empty-string operator precedence edge**
- File: `carts/tests/test_utils.py`
- Under test: `carts/utils.py:381` condition `if not direction or pickup_lat is None and dropoff_lat is None`
- Input: `direction=''`, `pickuplat=13.75`, `dropofflat=None`; CI row has `direction=address_to_airport`
- Expected: fallback triggers (empty string is falsy), `InfoFields.direction = 'address_to_airport'`
- Why: Python precedence trap — `not direction` short-circuits before coord check; undocumented behavior that could silently swap direction

### FE: Top 5

**FE-1 (P0) — PlacePicker: selection extracts lat/lng and calls onSelect**
- File: `__tests__/components/airport-transfer/PlacePicker.test.js`
- Setup: mock `useJsApiLoader` → `{ isLoaded: true }`, mock `geocodeByAddress` → `[{ geometry: {} }]`, mock `getLatLng` → `{ lat: 13.7563, lng: 100.5018 }`
- Input: user clicks suggestion `'Bangkok, Thailand'`
- Expected: `onSelect({ address: 'Bangkok, Thailand', lat: 13.7563, lng: 100.5018 })` called once
- Why: geocoder error path at `PlacePicker.js:86-88` swallows failures silently; no test would catch a regression where onSelect is never called

**FE-2 (P0) — PlacePicker: clear button calls onClear, onSelect not re-emitted**
- File: same
- Input: render with prior address; click clear (aria-label "Clear address")
- Expected: `onClear` called once; `onSelect` not called; input value empty
- Why: stale coords from un-cleared PlacePicker flow into Redux and get submitted to BE on booking

**FE-3 (P0) — checkoutPersistence: lat/lng/direction/resolvedContract survive round-trip**
- File: `__tests__/helpers/checkoutPersistence.test.js` (new describe block)
- Under test: `restoreCheckoutData`
- Input: `tripInfo['101'] = { pickupLat: 13.7563, pickupLng: 100.5018, dropoffLat: 7.886, dropoffLng: 98.3923, direction: 'address_to_airport', resolvedContract: 42 }`
- Expected: all 6 fields survive with exact values
- Why: `normalizeTripData:198-201` serializes these to BE; existing tests only verify string pickupPoint, never coords — null regression here silently drops airport-transfer coordinates after page refresh

**FE-4 (P1) — ZonePriceBox: tab direction controls which coord slot is written**
- File: `__tests__/components/airport-transfer/ZonePriceBox.test.js`
- Input A: `tabValue=0`, `selected = { lat: 7.886, lng: 98.3923, address: 'Patong' }` → dispatch must contain `{ direction: 'airport_to_address', dropoffLat: 7.886, dropoffLng: 98.3923 }`, no pickupLat
- Input B: `tabValue=1`, same → `{ direction: 'address_to_airport', pickupLat: 7.886, pickupLng: 98.3923 }`, no dropoffLat
- Why: tab inversion is a one-line branch with no guard; wrong tab → pickup/dropoff coords swapped → wrong pickup given to operator

**FE-5 (P1) — PlacePicker: typing without selecting never calls onSelect or geocoder**
- File: `__tests__/components/airport-transfer/PlacePicker.test.js`
- Input: fire change event on input (type 'Silom'); do not click any suggestion
- Expected: `onSelect` not called; `geocodeByAddress` not called
- Why: partial text must not trigger geocoding or populate lat/lng — would silently submit null coords while showing text to user

**FE-6 (P0) — ZoneGatedField: place selected → zone matched=true → pickupZoneMatched=true → Yup passes**
- File: `__tests__/components/forms/checkout/ZoneGatedField.test.js`
- Setup: mock `useLazyResolveGeneralZoneQuery` trigger returning `{ data: { matched: true } }`; mock PlacePicker to call `onSelect({ address: 'Bangkok Hotel', lat: 13.75, lng: 100.5 })`
- Input: field='pickup', contractId=42, fieldIndex=0
- Expected: `setFieldValue('trips.0.pickupPoint', 'Bangkok Hotel')`, `setFieldValue('trips.0.pickupLat', 13.75)`, `setFieldValue('trips.0.pickupZoneMatched', true)`, "Zone matched" text renders
- Why: this is the critical happy path — no test verifies zone resolve fires and unlocks checkout

**FE-7 (P0) — ZoneGatedField: zone matched=false → pickupZoneMatched=false → error shown**
- File: `__tests__/components/forms/checkout/ZoneGatedField.test.js`
- Setup: mock trigger returning `{ data: { matched: false } }`
- Expected: `setFieldValue('trips.0.pickupZoneMatched', false)`, error text "outside this route's service zone" renders; "Zone matched" not present
- Why: the checkout block depends entirely on this path — if matched=false doesn't set the boolean, Yup test passes anyway and customer proceeds with unserviceable address

**FE-8 (P1) — ZoneGatedField: saved address from pre-zone-flag era shows idle warning, not auto-matched**
- File: `__tests__/components/forms/checkout/ZoneGatedField.test.js`
- Setup: render with `values.trips[0].pickupPoint = 'Old Hotel A'` (from persistence) but no prior zone resolve
- Expected: "Please reselect to confirm" text renders; `pickupZoneMatched` stays false; no zone API call made on mount
- Why: a customer whose saved address predates the zone flag being turned on must re-confirm — if this shows as "matched" without re-resolve, they bypass zone gating

### AD: Top 5

**AD-1 (P0) — useContractFormData maps pickup_requires_zone from API response**
- File: `__tests__/hooks/useContractFormData.test.js`
- Input: mock API returns `{ pickup_requires_zone: true, dropoff_requires_zone: false, ...fields }`
- Expected: `initialValues.pickupRequiresZone === true`, `initialValues.dropoffRequiresZone === false`
- Edge: API returns undefined both → both default false (the `?? false` branch)

**AD-2 (P0) — TransferZoneFieldToggles renders correct switch state and fires setFieldValue**
- File: `__tests__/components/forms/contract/TransferZoneFieldToggles.test.js`
- Input: formik `{ values: { pickupRequiresZone: true }, setFieldValue: jest.fn() }`, `hasPickupPoint=true`
- Expected: switch aria-label `pickupRequiresZone` is checked; click → `setFieldValue('pickupRequiresZone', false)` called

**AD-3 (P1) — transformContractFormValues serializes pickupRequiresZone → pickup_requires_zone**
- File: `__tests__/utils/contractUtils.test.js`
- Input: `{ pickupRequiresZone: true, dropoffRequiresZone: false, ...minimalTransportFields }`
- Expected: output has `pickup_requires_zone: true`, `dropoff_requires_zone: false`; no camelCase keys in output

**AD-4 (P1) — TransferZoneFieldToggles hidden when no pickup/dropoff infoFields**
- File: same as AD-2
- Input: `hasPickupPoint=false, hasDropoffPoint=false`
- Expected: no Switch rendered

**AD-5 (P1) — ContractFormFields shows toggles for PRIVATE/CHARTER, hides for JOIN**
- File: `__tests__/components/contracts/ContractFormFields.test.js`
- Input A: `type.value='PRIVATE'`, pickup_point infoField active → toggles render
- Input B: `type.value='JOIN'`, pickup_point infoField active → toggles hidden
- Input C: `type.value='PRIVATE'`, no infoField → toggles hidden

---

## FE ↔ BE ↔ AD Consistency

| Feature | FE | BE | AD | Status |
|---------|----|----|-----|--------|
| pickup_requires_zone flag | Reads via contract detail API | Model + migration 0071 | PATCH via contract form | ✅ Consistent |
| dropoff_requires_zone flag | Reads via contract detail API | Model + migration 0071 | PATCH via contract form | ✅ Consistent |
| Pickup lat/lng stored | Sends pickupLat/pickupLng at checkout | CartItemCheckoutInfo.pickup_lat/lng | Does not write coords | ✅ Correct separation |
| Google Place ID | Not stored | Not stored | Not stored | N/A — not part of design |
| Google Autocomplete library | react-places-autocomplete | — | react-places-autocomplete | ✅ Same lib |
| Geocoding method | geocodeByAddress (2-step) | — | geocodeByAddress (2-step) | ✅ Same method |
| place_id extraction | No | No | No | N/A |
| Coordinates on contract edit | Not applicable | Not applicable | Not applicable | N/A |
| Coordinates at checkout | PlacePicker → ZonePriceBox | views.py:597-602 | Not in checkout flow | ✅ Correct |

---

## Critical Risks Not Yet Tested

1. **Partial update coord wipe** (`carts/views.py:597-602`): PATCH body missing `pickupLat` key → `trip.get('pickupLat')` returns None → existing pickup_lat silently overwritten with None. May affect any zone-transfer booking re-submitted without resending location.

2. **direction operator precedence** (`carts/utils.py:381`): `if not direction or pickup_lat is None and dropoff_lat is None` — empty string direction short-circuits entire condition, triggers coord fallback even when valid coords are present.

3. **Two-step geocoder drift**: FE uses `geocodeByAddress` (Geocoding API) not Places geometry. If Google's geocoder resolves slightly differently from the Places result, stored coords may not match the selected place — no validation or fallback exists.

4. **autocompleteinput.js not wired**: `components/search/autocompleteinput.js` has a full Google Places autocomplete with internal lat/lng state but emits nothing to parent — no checkout or booking integration. If someone tries to reuse this for contract location, it silently does nothing.

## Related
- [[contract-model-ambiguity-audit]] — field intent, primary_location vs service_areas
- [[airport-transfer-rate-dynamic-pricing]] — ZonePriceBox + fare-calendar flow
- [[frontend-test-infrastructure-audit]] — broader FE test gaps (pickup fields 0% coverage confirmed here)
- [[seat-availability-reseller-operator-gap]] — related Contract config changes (migration 0070)
