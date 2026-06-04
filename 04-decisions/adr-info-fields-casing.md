# ADR: `info_fields` Casing Convention

## Summary
Backend stores `info_fields` keys fully-lowercase (no separator). Frontend uses camelCase internally. A single boundary function handles the translation.

## Context
`InfoField.key` values are typed by operators in the admin dashboard — Django never enforced a casing format. This produced fully-lowercase concatenated keys: `arrivalairline`, `pickuptime`, `dropoffpoint`, `extrainfo`. The frontend uses React/Formik conventions (camelCase). Rather than normalizing at the DB layer (a migration + admin change risk), the boundary is held at the persistence layer.

## Decision
**Keep the casing boundary at `checkoutPersistence.js:normalizeTripData()`.**

- Backend → frontend read path: `BookingDetail/index.js` passes snake_case values directly as props to `Information.js` (camelCase prop names, snake_case values). PDF layer (`PdfView.js`, `PdfViewImproved.js`) destructures snake_case directly — no conversion needed.
- Frontend → backend write path: `normalizeTripData()` in `checkoutPersistence.js` maps camelCase Formik state to capital-T keys (`arrivalFlightTime`, `departureFlightTime`) before POST.
- On load: `Passengers.js:536–537` normalizes capital-T keys from sessionStorage back to lowercase-t Formik state keys (`arrivalFlighttime`, `departureFlighttime`).

## The `arrivalFlighttime` Lowercase-t Inconsistency
Formik state uses `arrivalFlighttime` / `departureFlighttime` (lowercase `t`). The backend stores and returns `arrivalFlightTime` / `departureFlightTime` (capital `T`). This is intentional: the normalization in `Passengers.js:536–537` handles both spellings at load time. Do not "fix" this inconsistency by renaming Formik keys without updating all callers.

## Tradeoffs
- **Pro:** Zero migration risk. Backend field names stay as operators entered them.
- **Pro:** PDF and booking-detail read paths are simple — destructure backend keys directly.
- **Con:** `Information.js` props are camelCase names receiving snake_case values — visually confusing without this ADR.
- **Con:** The lowercase-t / capital-T split requires two-way normalization code.

## Consequences
Do not add new `info_fields` access without following this pattern:
- Read (display/PDF): destructure backend snake_case directly
- Write (form → API): go through `normalizeTripData()` or equivalent
- Load from sessionStorage: handle both `arrivalFlightTime` and `arrivalFlighttime` spellings

## Related
- [[contract-model-ambiguity-audit-2026-06-03]] — D3 debate that surfaced this item
- `helpers/checkoutPersistence.js` — `normalizeTripData()` is the single conversion boundary
- `components/forms/checkout/Passengers.js:531–537` — load-time normalization
