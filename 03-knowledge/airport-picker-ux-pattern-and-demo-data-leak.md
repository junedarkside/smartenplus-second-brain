---
name: airport-picker-ux-pattern-and-demo-data-leak
description: 3-agent debate verdict on Airport Transfer search tab's picker UI (native select vs autocomplete vs chip grid) + a confirmed demo-data leak in the airport list. Unanimous: replace select with chip/card grid reusing StationCard visual language; filter demo rows client-side as a stop-gap, fix backend properly later.
metadata:
  type: knowledge
  status: active
  date: 2026-08-06
  parent: airport-transfer-redesign-2026
---

# Airport Picker UX Pattern + Demo-Data Leak

## Summary
3-agent debate (UX research, UI implementation, design system) unanimously rejected the shipped native `<select>` airport picker in favor of a chip/card grid reusing `StationCard`'s visual language. Separately confirmed a real bug: demo/test stations (`[DEMO] Phuket Hotel Zone`, `Demo Phuket Airport`) leak into the live customer-facing airport list — 2 of 4 visible entries in a screenshot were fake.

## Context
Airport Transfer search tab (3rd tab in `TabbedSearchPanel.js`, shipped `feat/airport-transfer-search-tab` `a78c06d9`) used a native `<select>` for airport choice — reasoning at ship time: small closed set (~4-10 airports) doesn't need Transportation tab's autocomplete typeahead. User saw it live, questioned the pattern choice and flagged the demo-data pollution in the same screenshot. Spawned a 3-agent debate (`ux-research-specialist`, `ui-component-engineer`, `design-review`) to settle both questions with one recommendation.

## Decision

**Picker pattern: replace `<select>` with a chip/card grid.** All 3 agents converged independently, no dissent:
- **UX case**: at n=4-10, tap-to-select beats typeahead — scanning is faster than summoning a keyboard + typing + reading filtered results at this size (Hick's Law: log(n) term is small enough that scan/motor cost dominates over query-interface cost). Typeahead also invites typos/empty-states a closed set doesn't need. Reject the `AutoCompleteSearch.js` modal reuse — it solves a search problem (large open-ended station list) this tab doesn't have.
- **Implementation case**: `<select>` is the only field in the 3-tab search panel that hands rendering to the OS — no image/icon per option, can't show the "Popular" airport cue that exists elsewhere, native picker chrome (esp. iOS wheel) visually clashes with every other custom-styled control in this panel. Reusing `AutoCompleteSearch.js` as-is would either drag Redux coupling into a component deliberately kept local-state (`AirportTransferSearch.js` matches `ExperiencesSearch.js`'s local-state precedent) or require forking it — real new-component cost, not reuse, fails REUSE FIRST in spirit. The right-sized build: a chip/button row copying `ExperiencesSearch.js`'s existing category-chip pattern (`ExperiencesSearch.js:66-85`, `aria-pressed` selection state) — same file already proves this pattern fits the shared `md:min-h-[120px]` panel height budget. Estimated ~40-60 line diff to `AirportTransferSearch.js` (currently 77 lines total, well under the 200-line component ceiling).
- **Design case**: `<select>` is a 3rd distinct visual treatment for the same data type (modal-autocomplete for locations, image-card grid for airports via `StationCard`, now bare OS-select for airports again) — inconsistency, not simplicity. Recommend a lightweight variant of `StationCard`'s visual language (IATA badge, `rounded-md`/`rounded-xl` token, not full photo-card weight) rather than either extreme.

**Demo-data leak: real bug, ship a client-side stop-gap now, fix backend properly later.**
- Confirmed via backend code read (not speculation): `Station` model (`stations/models.py:79-125`) has no `is_demo`/`is_active`/`is_published` field. `DashBoardStationViewSet.get_queryset` (`stations/views.py:446-485`) filters only `search`/`location`/`station_type` — returns every row matching `station_type=airport`, demo or real. Demo rows come from a real runnable command `operators/management/commands/seed_demo_destination.py` (`PREFIX = '[DEMO]'`), documented "dev/test only" but with **zero code-level environment guard** — nothing stops it running against shared/staging/prod.
- A ready-made pattern already exists in the same codebase to copy: `TransferZone.is_active`, `ZoneContract.is_active`, `Contract.is_actived` are boolean soft-flags already filtered in queries — `Station` never got the same treatment.
- Design-debater's stance (unopposed): a customer choosing between `[DEMO] Phuket Hotel Zone` and `Phuket Airport (HKT)` mid-booking isn't seeing clutter, they're seeing an unvetted platform — a trust failure in a payment-adjacent flow, not a cosmetic nit. Ranked as a shipping blocker independent of the picker-pattern decision.
- Recommended interim fix: a client-side filter at the point `airportOptions` is derived from the query response, excluding names matching `/^\[DEMO\]|^Demo /i` — a 3-line guard at a data-shaping boundary, explicitly scoped with an expiry (remove once backend stops returning demo rows), not a permanent workaround. This is justified as urgent stop-gap specifically because the real fix (a `Station.is_active`-style flag + backend filter, or removing the unguarded seed command's prod-reachability) has no committed timeline and the leak is live today.

## Consequences
- Not yet implemented — this is a recommendation, no code changed in this pass.
- Next build step (if approved): swap `AirportTransferSearch.js`'s `<select>` block for a chip row (copy `ExperiencesSearch.js`'s chip pattern), add the demo-name regex filter at the `airportOptions` derivation line, both scoped to the single file already shipped.
- Backend fix (separate, larger effort, not scoped here): add `Station.is_active` (or equivalent) following the `TransferZone`/`Contract` precedent, filter it in `DashBoardStationViewSet.get_queryset`, and/or add an environment guard to `seed_demo_destination.py` so it can't run against non-dev databases.

## Related
- [[airport-transfer-redesign-2026]] — parent project, homepage airport transfer section history
- [[transfer-category-vs-airport-filter-independence]] — companion architecture fact about `station_type` filtering
