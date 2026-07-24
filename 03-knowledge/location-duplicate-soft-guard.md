# Location Duplicate Soft Guard (FE-only)

## Summary

Admin-dashboard `/routemanagement/locations` warns before creating/editing a location that duplicates an existing one, with a "Save Anyway" override. Frontend-only soft guard — no backend enforcement.

## Context

Location create/edit had NO dedup anywhere. Backend `DashBoardLocationWriteSerializer` has no `validate()`; `Location` model has no `unique_together` / `unique=True`. Duplicate `(location_name, city, province)` rows accumulate silently. Admin action `show_duplicates` (`stations/admin.py`) confirms dupes already exist in prod. Contrast: `DashBoardStationWriteSerializer.validate()` already blocks dup station names iexact — Location simply never got the equivalent.

## Problem

Where to enforce? Backend hard-block is the strongest guarantee but:
- Adding `unique_together` requires a migration that **FAILS** while existing prod dupes remain (would need a data-cleanup/merge step first).
- Adding serializer `validate()` touches a code path also reachable by admin/API/import — broader blast radius than the ask.

## Decision

Soft FE-only warning (user's call). On submit, both location dialogs run a duplicate check; on match, show an `Alert` listing matches + require **Save Anyway**. Backend still accepts dupes from any path — accepted tradeoff. Goal is to stop the *obvious accidental* admin dupe, not to guarantee uniqueness.

Implementation (admin-dashboard):
- `components/location/locationDuplicateUtils.js` — `normalizeLocationName(name)` **mirrors backend `normalize_location()`** in `stations/models.py` (`lower()` + strip spaces/hyphens), so FE detection == BE search semantics. Plus `findDuplicateLocations(list, {name,city,province}, excludeId)` — normalized-name match, iexact city/province when present, drops `excludeId` in edit mode.
- `components/location/useLocationDuplicateCheck.js` — hook wrapping `useLazyGetLocationsQuery`; **fails open** (returns `[]` on error → network failure never blocks a save).
- Both `locationEdit.js` + `LocationCreateDialog.js` split submit into `doSubmit` + a pre-check wrapper; store pending submit in a `useRef`, show warning, "Save Anyway" runs it. Edit passes `excludeId` so a row never self-flags.
- Reuses the write-time dup UX pattern from `route/routeEdit.js` (`runDuplicateCheck` + confirm dialog). Shared util means the two dialogs share one impl — no copy-paste.

## Tradeoffs

- ✅ No migration risk, no shared-path/backend change, purely additive, reusable.
- ❌ Dupes still creatable via API/admin/import/bulk. FE check is best-effort — relies on the `search` query returning the candidate (page_size 50).
- If true uniqueness is ever required: clean existing prod dupes (merge FKs — stations/places/routes/contracts reference Location) THEN add `unique_together` + serializer `validate()` mirroring the Station pattern.

## Related

- [[stations]] — Location/Station/Place/Route model home; Station serializer already has the iexact dup-validate Location lacks.
- Backend `normalize_location()` (`stations/models.py`) — the normalizer FE mirrors; keep the two in sync.
- Pattern source: `route/routeEdit.js` runDuplicateCheck + Save-Anyway confirm dialog.
