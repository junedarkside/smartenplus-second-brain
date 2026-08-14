# "Join" Label Transport UX Debate

## Summary
User report: "Join" label for transportation contract-type ("shared vehicle" vs "private vehicle") fails UX best practice on `/trips/hatyai/koh-lipe`. 3-agent debate (UX research + UI engineering + BD) unanimous on placement fix, split on final wording. **DECIDED 2026-08-13: JOIN → "Shared Ride"** (user picked UX Research's recommendation). PRIVATE label not yet finalized (leaning "Private Ride" for parallel construction) — implementation ticket still open.

## Context
Not a booking CTA — `BookButton` always renders "Book Now" (`components/UI/BookButton.js:31`). The actual issue: `CONTRACT_TYPE.JOIN` / `PRIVATE` / `CHARTER` (`constants/dayTripApi.js:42-53`) is a contract-type label distinguishing shared-seat vs private-vehicle transport, currently displayed as `CONTRACT_TYPE_NAMES.JOIN = "Join Tour"`.

**Where it shows today:**
- Filter chip on operator listing: `OperatorFilterBar.js:7` — own hardcoded `FILTER_LABELS = { JOIN: 'Join', ... }`, **not** sourced from `CONTRACT_TYPE_NAMES` (drift risk, two maps to keep in sync)
- Checkout-stage badge only: `EnhancedTripCard.js:356,463`, `ServiceCategoryDetail.js:191` — "Join Tour" via `CONTRACT_TYPE_NAMES`

**Where it's missing:** trip search cards (`TripCardV2.js`) and trip detail page (`TripDetailBooking.js`) show **no** shared-vs-private indicator at all. Known pre-existing gap — V1 card showed "1 stop • 4 hr 30 min • JOIN" via `transportDescriptionText` (computed in `TripItem.js`), but V2's `TripItemLayoutV2` never renders it (dead code on that path). Already flagged as P1 in [[trip-card-v2-flight-style-audit]].

A ready-made display component exists — `ContractTypeBadge.js` (icon + label Chip, sources `CONTRACT_TYPE_NAMES`, follows the single-color/icon-differentiated pattern from [[unified-badge-system-pattern]]) — but its **only consumer repo-wide is `pages/operators/[slug].js`**. Never wired into trip search or detail pages.

"Tour" is borrowed day-tour/activities vocabulary; product is point-to-point transport (ferry/bus/van route legs), not a guided tour.

User's own suggestion (translated from Thai): rename to plain language like **"Shared Boat/Van"**, fixed once at a central template so it covers every route.

## Debate — 3 Independent Positions

### UX Research (comprehension lens)
"Join"/"Join Tour" fails on first exposure — "Join" is an object-less verb that collides with unrelated UI actions (join waitlist/call/membership) and doesn't carry travel-industry meaning for point-to-point transport; "Tour" primes the wrong mental model entirely. Rejects user's literal "Shared Boat/Van" — vehicle-specific wording breaks the moment a JOIN route runs by bus instead of boat/van.

**Recommends:** JOIN → **"Shared Ride"**, PRIVATE → **"Private Ride"** (parallel construction, one modifier flips), CHARTER unchanged. "Shared Ride" is vehicle-agnostic and leans on ridesharing vocabulary now globally familiar (Grab/Uber) across target markets (Europe/USA/Asia).

**Placement:** both search card and detail page — comprehension risk is highest at decision time, not just before payment. Discovering "shared" for the first time at checkout reads as bait-and-switch.

### UI Engineering (implementation lens)
Agrees `CONTRACT_TYPE_NAMES` should be the single source of truth; `OperatorFilterBar.js`'s duplicate `FILTER_LABELS` should be deleted in favor of importing it. Only carve-out: filter chips need shorter text than a card badge — proposes adding a `CONTRACT_TYPE_SHORT` variant in the same file rather than a second parallel map, so there's still exactly one file to edit.

Rejects wiring `ContractTypeBadge.js` (full MUI Chip) into `TripCardV2` as-is — too heavy for the flight-card density at 375px (already tight per prior audit). Recommends reusing the icon+label *mapping logic*, shipped as a compact inline variant (icon glyph + short text, no chip padding/border) on the legs/duration row — the exact placement the prior V1→V2 audit already flagged as the fix (P1#1, `BadgeChip` on stops+duration line).

**Wording:** keep "Join Tour"/"Private Tour" (full) + "Join"/"Private" (short). Explicitly rejects "Shared Boat/Van" as a *type*-label value — same reasoning as UX (vehicle mode ≠ contract type, and vehicle-type text already exists as a separate field elsewhere in trip data). Argues "Join Tour" is already an established travel-industry term, unlike raw "JOIN".

### Business/BD (conversion lens)
Hiding the indicator until checkout is a CS-cost problem more than a conversion blocker — trust violation is asymmetric: a traveler expecting Private and discovering Shared at checkout feels tricked (disproportionate complaint/refund risk); a traveler expecting Shared (the common/default case) is only mildly surprised. Net effect: erodes trust/repeat-booking more than it kills first-time conversion, and simply relocates friction to the highest-cost point in the funnel (post-effort cart abandonment).

Current neutral "Tour" wording sells neither side of the choice — argues for benefit-framed copy: Private/Charter is higher-margin per booking and under-sold by neutral wording; JOIN is the volume driver and could convert better framed as the budget-smart default rather than a neutral/ambiguous label.

**Recommends:** JOIN → **"Shared & Save"**, PRIVATE → **"Private Vehicle"** (benefit self-evident, no oversell needed), CHARTER unchanged. Placement: both search results (self-select before clicking in, reduces wasted funnel entries) and detail page (reinforcement right before "Book Now," the actual commitment moment). Checkout badge stays as confirmation, not first disclosure.

## Agreement
- **Placement: unanimous.** Indicator must reappear on both the trip search card (`TripCardV2`) and the detail/booking page (`TripDetailBooking`), not just checkout. All 3 lenses independently reached this — comprehension (UX), the pre-existing dead-code gap (UI), and funnel-cost economics (BD) all point the same direction.
- **Central source of truth: unanimous.** `CONTRACT_TYPE_NAMES` in `constants/dayTripApi.js` should be the one map; `OperatorFilterBar.js`'s duplicate `FILTER_LABELS` should be deleted and replaced with an import. Matches user's explicit ask ("fix once at the central template").
- **Reject literal "Shared Boat/Van": 2 of 3 (UX, UI).** Vehicle-mode wording baked into the contract-type field breaks on any route where JOIN runs by bus/car instead of boat/van — the same route can vary by operator. Vehicle-type wording, if wanted, belongs on the separate vehicle-type field that already exists in trip data, not on `CONTRACT_TYPE_NAMES`.
- **"Tour" is the wrong noun:** UX and BD agree it doesn't fit point-to-point transport; UI is the lone dissent, calling "Join Tour" an already-established travel-industry term worth keeping.

## Disagreement — Final Wording (unresolved, 3-way split)

| Contract type | UX Research | UI Engineering | BD/Conversion |
|---|---|---|---|
| JOIN | "Shared Ride" | "Join Tour" (unchanged) | "Shared & Save" |
| PRIVATE | "Private Ride" | "Private Tour" (unchanged) | "Private Vehicle" |
| CHARTER | Charter (unchanged) | Charter (unchanged) | Charter (unchanged) |

No consensus reached on copy. UI's position leans conservative (don't touch working, already-familiar travel-industry vocabulary; solve the real gap which is placement, not wording). UX and BD both want new copy but diverge on tone — neutral/plain ("Shared Ride") vs benefit-framed/sales ("Shared & Save").

## Competitor Reference (added 2026-08-13)
Live-checked how comparable multi-modal transport platforms (same product shape as `/trips/hatyai/koh-lipe`: ferry/bus/van route search + booking) actually label shared vs private on real route pages.

**Bookaway** — checked 2 independent routes (`bangkok-to-koh-chang`, `rio-de-janeiro-to-ilha-grande`):
- Filter tabs: `Bus` / `Ferry` / `Flight` / `Shuttle` / `Private Transfers`
- Result cards: **only the private option carries an explicit label** — "Private Transfer" / "Private car" (described "door-to-door service on your schedule")
- Every shared option (bus, ferry, minivan/shuttle) is shown by **vehicle name alone** — no "Shared," "Join," or equivalent badge word anywhere. Site copy states it outright: *"All of these transportation options are shared besides the private car."*
- No icon convention distinguishing shared vs private observed in fetched content.

**12Go** (SE-Asia multi-modal authority, cited in [[airport-transfer-competitor-review-2026]]) — site is JS-rendered client-side, could not extract live label text via fetch this session; a Tripadvisor review references a "shared mini van" product existing on the platform but page content itself wasn't retrievable. Gap, not a negative finding — needs a browser-driven check (Playwright) to close, not re-attempted via plain fetch.

**Omio/GoOpti** — listing page confirmed as offering "shared and private airport transfers" via search snippet, but the live page blocked WebFetch (403). Unconfirmed live-label gap, same as 12Go.

### 4th position this surfaces
None of the 3 internal debate agents considered **not labeling JOIN at all** — Bookaway's actual production pattern is to only badge the *premium* option (Private) and let the default/cheap option go unmarked, implicitly communicated by the absence of a private badge plus the vehicle-type name itself (Bus/Ferry/Van already implies shared to a traveler who's seen those words before). This sidesteps the entire "what do we call JOIN" debate by not needing a JOIN-facing word at all — it only requires one good, unambiguous **PRIVATE** label, which all 3 internal agents already converge close to ("Private Ride"/"Private Tour"/"Private Vehicle" are near-synonyms, unlike the 3-way JOIN split).

**Caveat:** SmartEnPlus's UI already renders JOIN routes as visually equal-weight cards to PRIVATE ones (unlike Bookaway's tabbed-by-vehicle-type layout, where "shared" is implied by which tab you're already in). A same-vehicle-type page (all van options, some JOIN some PRIVATE) can't rely on vehicle-name-only disambiguation the way Bookaway's tab structure does — so omission-only labeling is not a direct port, but the underlying insight (badge the premium option, don't force a positive word onto the default) is directly applicable and simplifies the wording decision to just "pick one good PRIVATE label."

## Recommendation (leader synthesis)
1. **Ship the placement + architecture fix regardless of wording decision** — this closes the actual functional gap (missing indicator on search+detail) and the drift risk (duplicate label maps), both unanimous and lower-risk than a copy change.
2. **Competitor evidence narrows the wording decision, doesn't fully resolve it.** Bookaway's production pattern (badge Private only, leave shared unmarked) isn't directly portable — SmartEnPlus needs both types visually distinguishable on the same card grid, unlike Bookaway's tab-separated layout. But it validates that PRIVATE naming is low-risk (all 3 agents + Bookaway converge near "Private Ride/Vehicle/Transfer") while JOIN naming is the only real open question. Recommend a short follow-up decision (owner: product) between: (a) keep neutral "Join Tour" (UI eng + closest to status quo), (b) "Shared Ride" (UX, vehicle-agnostic plain language), or (c) benefit-framed "Shared & Save" (BD, testable via A/B). Ship PRIVATE as "Private Ride" or "Private Vehicle" with more confidence regardless.
3. Implementation, once wording is picked: compact icon+short-label inline component (new, lighter than `ContractTypeBadge`) on `TripCardV2`'s legs/duration row and `TripDetailBooking`'s route summary; `OperatorFilterBar.js` migrated off `FILTER_LABELS` onto `CONTRACT_TYPE_NAMES` (+ new `CONTRACT_TYPE_SHORT` if chip width requires it).

## Decision
**JOIN → "Shared Ride".** User chose UX Research's recommendation over UI Engineering's "keep Join Tour" and BD's "Shared & Save" — 2026-08-13, after competitor reference added (competitor check didn't resolve JOIN wording directly but de-risked moving off "Join Tour"). PRIVATE label left open (recommend "Private Ride" to match, parallel one-word-modifier construction per UX's original rationale) — confirm before implementation.

## Status
**Wording decided, not yet implemented.** No code changed this session. Follow-up: implementation ticket covering `TripCardV2` legs/duration row, `TripDetailBooking` route summary, `OperatorFilterBar.js` migrated off duplicate `FILTER_LABELS`, `constants/dayTripApi.js` `CONTRACT_TYPE_NAMES.JOIN` updated to "Shared Ride" (single source of truth — fixes both wording and the drift risk in one change, per user's original "fix once centrally" ask).

## Related
[[trip-card-v2-flight-style-audit]] · [[unified-badge-system-pattern]] · [[trip-route-page-seo-aeo-geo-audit]]
