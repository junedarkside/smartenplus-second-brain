# Checkout FormData Time Fields

## Summary
Frontend time fields use lowercase-t camelCase. Backend expects capital-T camelCase. Backend TimeField format is HH:MM:SS, not ISO. Three conversion helpers bridge the gap. Getting this wrong causes silent data loss.

## Context
`helpers/checkoutPersistence.js:175-196, 386-428`. Time fields appear in airport transfer and flight pickup checkout forms. Mismatch = field saved but never restored, or backend rejects with 400.

## The Casing Boundary

| Field | Frontend (Formik) | Backend (API) |
|---|---|---|
| Pickup time | `pickupTime` | `pickupTime` (same) |
| Arrival flight time | `arrivalFlighttime` | `arrivalFlightTime` |
| Departure flight time | `departureFlighttime` | `departureFlightTime` |

Note: `pickupTime` matches but `arrivalFlighttime` differs at the `t` → `T`. Frontend uses lowercase-t consistently; backend uses capital-T after "Flight".

**Source:** `adr-info-fields-casing.md` documents this boundary. Conversion happens in `checkoutPersistence.js:normalizeTripData()`.

## Backend Time Format
Django `TimeField` expects `HH:MM:SS` string:
```
✓  "14:30:00"
✗  "2026-06-12T14:30:00.000Z"  (full ISO — rejected)
✗  "14:30"                      (missing seconds — rejected)
```

## Three Conversion Helpers

### `safeTimeToString(value)` → `"HH:MM:SS"`
```js
// Input: Date object or "HH:MM" or "HH:MM:SS"
// Output: always "HH:MM:SS"
// Returns null on invalid input (never throws)
```
Used when saving to backend.

### `safeDateToISO(value)` → ISO string or null
```js
// Input: Date object, ISO string, or null
// Output: ISO string for date-only fields (not time)
```

### `timeStringToDate(value)` → Date object
```js
// Input: "HH:MM:SS" from backend
// Output: Date object for MUI TimePicker
// Attaches time to today's date (date part irrelevant, time part is what matters)
```
Used when restoring from backend to Formik.

## Conversion Points
```
Frontend Formik state (Date objects from MUI TimePicker)
  ↓ safeTimeToString()
Backend save (HH:MM:SS string) — field key: arrivalFlightTime (capital T)
  ↓ timeStringToDate()
Frontend Formik restore (Date object) — field key: arrivalFlighttime (lowercase t)
```

Field key must be lowercased on Formik side when restoring:
```js
// Correct restore:
setFieldValue('arrivalFlighttime', timeStringToDate(backendData.arrivalFlightTime))
//                         ^ lowercase t                           ^ capital T
```

## Silent Failure Mode
If capital-T used on Formik side:
- Field appears to save correctly (no error)
- On restore: Formik key not found → field renders empty
- User must re-enter time on every checkout visit
- No error logged

## Related
- [[checkout-state-persistence]] — where conversion happens in persistence flow
- [[adr-info-fields-casing]] — canonical casing boundary ADR
- [[checkout-formdata-persist-guard-pattern]] — other formData restore hazards
