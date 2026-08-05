# Session History

Archived from master-state.md. Latest session stays in master-state.md Section 1.

---

## Session #295 (2026-08-05)

**Achieved — Backend: root-caused + fixed the airport-transfer booking-confirmation email (zone-transfer bookings showed time as "—", From/To mismatched the hero line, passenger count was an unlabeled "1A"), resent the dev-test booking, merged to develop.** User forwarded a broken confirmation email for dev-test booking `WET4806711` (deliberately messy test input on a Hatyai↔George Town zone-price contract) and asked why — first suspected a regression of the prior session's `has_range` From/To fix, but `git show` on both commits (`a5c2ce3f`, `cefa9cdd`) confirmed those touched only the pre-checkout search-results price widget, never the email path; unrelated. Traced the real cause via direct file reads (backend `orders/services.py`, `carts/utils.py`, `bookings/emails/booking_confirmation_template.html`) cross-checked against an Explore-agent pass that landed on the same files independently. Root cause: zone/airport-transfer bookings have no `Contract.trip` (pickup time is customer-chosen at checkout, not a fixed schedule), so the email's time slot — which only ever read `booking.contract_departure_time`/`departure_time` from `Contract.trip` — was structurally always `None`, always rendering "—". A *prior* fix session (commit `d32bd18`, the day before) had already patched the **station** half of this same From/To block to fall back to `pickup_info`/`dropoff_info` when direction-branched, but never touched the **time** span — same fix pattern, half-applied, which is why the user's "we tried to fix this before" was right but the fix didn't fully land. Also found the hero line ("You're all set for X to Y") was built from the direction-agnostic `route_name` (fixed `Route` model field), so it could disagree with the direction-aware From/To timeline below it. User clarified mid-investigation that the visible garbled text ("eewew", "eee", pickup-time-after-dropoff-time) was intentional messy test input for this dev contract, not a real bug — descoped a planned checkout-validation fix accordingly, keeping only the two real template/backend defects. Fix: (1) `booking_confirmation_template.html` — time spans now fall back to `pickup_info.pickup_time`/`dropoff_info.dropoff_time` mirroring the station fallback already there; hero line rebuilt from resolved pickup/dropoff per direction instead of `route_name` for zone bookings. (2) `bookings/admin.py` `build_booking_context()` (the function backing the admin "resend confirmation email" action) was found to never set `booking.direction` at all — meaning even with the template fixed, admin-triggered resends would always hit the blank-direction fallback branch and still look broken; added the missing field from `InfoFields.direction`. Verified by rendering the real template against `WET4806711`'s live context (not a mock) — confirmed hero and timeline now agree, To time went from "—" to "09:00". Verified non-zone (fixed-route, `direction=''`) bookings are unaffected via a second real booking render. Resent the email live via SES through the admin action's underlying task (had to clear 3 stale `UserJourneyEvent` idempotency-guard rows for this one test booking — dev data only, no other booking touched). User then separately flagged the passenger count "1A" as cryptic; fixed same session to spell out "1 Adult" / "2 Adults, 1 Child" etc. via Django's `pluralize` filter, verified against 5 count combinations, resent again. Committed (`e606724`), pushed `fix/airport-transfer-email-time-direction`, merged → backend develop `6f9bfaa`, pushed. Plan mode used throughout investigation (Explore agent + direct file reads before any edit); an HTML before/after mockup artifact was also produced mid-investigation (before the real direction value was confirmed, so its Pickup/Dropoff assignment was illustrative, not DB-verified — superseded by the actual fix): https://claude.ai/code/artifact/591bd25f-1a1d-4db3-b4b5-25d0b37eed43

**Workspace (#295):**
- frontend: `develop` `a5c2ce3f` (clean)
- backend: `develop` `6f9bfaa` (pushed origin)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #294 (2026-08-05)

**Achieved — Backend: fixed date-specific ratecard priority bug across 4 sites + honest "from" price label on airport-transfer cards, merged to develop (both repos).** User asked why airport-transfer vehicle cards always show "from THB X" even for contracts with only one price ever — traced to `has_range` (added this session) being computed against a per-date `Contract_RateCard` queryset built with `Q(rate_date=date) | Q(rate_date__isnull=True)` (OR). User caught the deeper issue: submitting a specific date should resolve to exactly ONE applicable rate, but the OR-filter fetches both the date-specific override row AND the NULL base-rate row when both exist, then takes `Min()`/`min()` across them — silently picking whichever is *cheaper*, not the correct date-specific one (e.g. a NULL base rate at 5,000 wrongly wins over an intended holiday-surge override at 8,000). Confirmed via `Contract_RateCard.Meta.unique_together = ['contract','ratecard','rate_date']` that at most one NULL row and one date-specific row can exist per (contract, ratecard) — "prefer date-specific, else NULL" is deterministic, no ambiguity. Same bug pattern found in 4 places total via repo-wide grep (`stations/views.py` resolve-zone + `products/views.py` ×3: `_get_display_rate` helper, trip-search loop, fare-calendar loop) — pre-existing, not introduced this session. Fix: new shared `operators/rate_resolution.py` with `resolve_ratecards_for_date()` (date-specific wins outright, NULL fallback only when no override exists for that date — returns a queryset so each site keeps its own aggregation style/type-filtering/positivity-check quirks intact) and `contract_has_date_range()` (redefines `has_range` as "does this contract have 2+ date-specific override rows *anywhere on the calendar*", independent of the single date being queried — since post-fix the resolved-for-date queryset always collapses to 1 row, the old `count()>1` logic would've always been `False`). All 4 call sites updated to use the shared resolver, preserving every existing per-site inconsistency (site 1 has no type filtering, sites 2-4 do; positivity-check style differs slightly; `_is_contract_bookable` gate at site 4 untouched). Added 5 new resolver unit tests + 2 regression tests (date-specific price wins over cheaper NULL) + 1 new `has_range` semantics test proving the calendar-wide-variance definition (1 override → False; 2nd override on a different date → True, even though the resolved price for the queried date is still exactly 1 row). Built as two branches (`fix/airport-transfer-from-price-flag` for `has_range`, `fix/ratecard-date-priority` for the resolver) then merged together by hand-resolving the expected `stations/views.py` conflict to the combined form. `python manage.py check` clean; 121/122 backend tests pass (1 pre-existing unrelated failure, confirmed via `git stash` on develop before this session's changes). Frontend consumer (`ZoneOptionCard.js`/`ZonePriceBox.js`) renders `hasRange===false ? price : "from "+price`, missing/undefined field falls back to "from" for old cached responses. Both branches pushed + fast-forward merged → develop in backend (`38c0470→53506e9`) and frontend (`a1fd3cca→a5c2ce3f`), both pushed to origin. Also produced a diagram artifact tracing the full options-list render mechanism (address pick → resolve-zone API → per-card contract fetch → BookButton) for reference: https://claude.ai/code/artifact/47ba1a2d-6215-4196-bfdb-ee70db9d2762

**Workspace (#294):**
- frontend: `develop` `a5c2ce3f` (pushed origin)
- backend: `develop` `53506e9` (pushed origin)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #293 (2026-08-04)

**Achieved — Frontend: redesigned Booking Items card layout for airport transfer (guest-order + booking detail), plus fixed an unrelated CartButton crash it uncovered.** User flagged `/guest-order/[orderId]` "Booking Items" card as ugly for airport-transfer bookings — route text (e.g. "Hatyai Airport (HDY) to Lee Gardens Plaza Hotel Hat Yai, ถนน ประชาธิปัตย์…") collided with the "Airport Transfer" badge on desktop, and wrapped character-by-character on mobile with the badge clipped off-edge. Explored+confirmed root cause directly in `OrderBookingCard.js` (`components/order/`) and the near-duplicate `BookingItemCard.js` (`components/bookings/`) — both had the route row as a single `flex justify-between items-center` div with an unbounded text `<div>` (no `min-w-0`/wrap control) sitting directly beside the badge, so flexbox couldn't shrink the text and the badge got squeezed/pushed. Fixed both: row → `flex flex-wrap`, route text → `min-w-0 flex-1 basis-full sm:basis-0 break-words` (full-width on mobile so badge always drops to its own line; inlines on ≥sm when it fits), badge+direction-label → separate `flex-shrink-0 ml-auto` group. Also fixed `duration (0 hr)` noise — `duration` is a truthy `"00:00:00"` time string, not a number, so the old `duration && …` guard never caught the zero case; added a `hasDuration` check that parses hours/minutes. First fix pass (min-w-0/break-words alone) fixed desktop but NOT mobile — root cause was `flex-1`'s default `flex-basis:0%` letting the badge share the first line before wrap kicked in; `basis-full sm:basis-0` was the actual fix, confirmed via a Playwright DOM-width probe (text div went from a squeezed width to full 275px row width, badge cleanly dropped below). While live-verifying via Playwright screenshots at 375/768/1200px, hit an unrelated pre-existing crash blocking the whole guest-order page in dev: `CartButton.js:41` called `refetch()` on a RTK Query query that `useCheckCartIdQuery` skips when `cartId` is null (guest sessions on `/guest-order/*` have none) → "Cannot refetch a query that has not been started yet." Confirmed present on unmodified `develop` too (not caused by this session's edit) — got user go-ahead before touching it, fixed with a one-line `cartId` guard on the `refetch()` call. All three files lint-clean; verified live via Playwright screenshots + user's own phone screenshot confirming the fix. Committed + pushed `fix/airport-transfer-card-layout`, merged → frontend `develop` `a1fd3cca`, pushed.

**Workspace (#293):**
- frontend: `develop` `a1fd3cca` (pushed origin)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #292 (2026-08-04)

**Achieved — Frontend: airport-transfer From/To widget rebalance + tablet layout + row-height match.** User flagged `/airport-transfer/hatyai-airport` "Private transfer — fixed price" From/To widget (`ZonePriceBox.js`) as visually imbalanced — screenshot showed a compact static airport pill vs. a longer focus-highlighted address autocomplete input, plus a swap button stretched full-height via `items-stretch`/`w-11` into a tall thin sliver, and icon asymmetry (plane icon only on the airport row). Root cause confirmed by reading `ZonePriceBox.js`/`PlacePicker.js` directly; fix reused the exact sitewide swap-control pattern already proven in `components/search/TransportationSearch.js` (circular 40×40 `IconButton` badge on the row seam, `SwapVertOutlinedIcon`/`SwapHorizOutlinedIcon`, `FmdGoodOutlinedIcon` for the destination-icon convention) rather than inventing new treatment. Three incremental passes, each verified live via the `design-review` agent (Playwright) before moving on: **(1)** rebalanced rows — added an optional `icon` prop to `PlacePicker` (backward-compatible, single caller confirmed via grep), matched `AirportEndPill`'s icon chrome to it, replaced the stretched rectangle swap button with a 40×40 circular badge on the seam; **(2)** added `md:`+ (tablet/desktop) horizontal side-by-side layout matching the homepage search form's `flex-col md:flex-row` responsive pattern (`TransportationSearch.js:138`) — kept mobile stacked, added a second breakpoint-scoped swap button (`SwapHorizOutlinedIcon`, centered in the gap between `md:w-1/2` rows) since icon+position differ between stacked/horizontal; extracted a small `SwapButton` sub-component to de-duplicate the two `IconButton` instances; **(3)** user reported row height still didn't match the homepage search form despite the redesign — root cause was `py-2`/no `min-h` vs. the reference's `min-h-[44px] py-3` — one-line fix per spot (`AirportEndPill`, both `PlacePicker` input variants). All three passes lint-clean, verified live at 375/768/1024/1280px (stacked↔horizontal swap, autocomplete dropdown unclipped, icons vertically centered, no console errors, no layout jump on swap-click). Committed + pushed `fix/airport-transfer-fromto-balance`, merged → frontend `develop` `cfb3872d`, pushed.

**Workspace (#292):**
- frontend: `develop` `cfb3872d` (pushed origin)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #291 (2026-08-04)

**Achieved — Frontend: airport-transfer fare-card vehicle icon + operator identity.** User flagged `/airport-transfer/hatyai-airport` "Private transfer — fixed price" fare list: every option (van/suv/sedan/demo) rendered the same generic MUI `AirportShuttleOutlinedIcon`, no visual distinction between vehicle types, and no operator info surfaced pre-booking. Explored `ZoneOptionCard.js` (the actual fare-card component under `ZonePriceBox.js`) + its data source (`useCheckContractQuery` → `Contract`/`ContractSerializer`, which already includes `operator.operator_name`/`operator.image` — unread by the component). Researched real-world consolidator platforms (Klook, Kiwitaxi, Suntransfers, Booking.com Airport Taxis — same fixed-price model as SmartEnPlus): they use one generic icon per vehicle *class*, not real photos, and initially hide operator identity pre-booking (bidding marketplaces like GetTransfer are the exception). First pass (per that norm) added only vehicle-class icons — reused existing `helpers/transportMode.js` → `TransportMode(vehicleName)`, which already string-matches `"van standard"/"suv standard"/"sedan standard"` (from `contract.transport_composit[0].transport_composit`) to existing SVG icon components (`VanIcon`/`SuvIcon`/`CarIcon`), with graceful fallback to the original MUI icon on no match (e.g. the seeded `[DEMO] Airport Private Transfer` contract). User then reconsidered — no real vehicle/operator photos exist in the app at all, and wanted the customer to know who services the transfer before booking — so added operator name + logo too, reusing the same field pattern already proven in `TripItemOperatorInfo.js` (`contract?.operator?.operator_name || 'smartenplus'`, `contract?.operator?.image || smartenplusIcon`), rendered as a small 16px logo + gray text line directly under the vehicle name, no new API call (data was already in the existing `checkContract` fetch). Domains for `next/image` already whitelisted in `next.config.js` (same ones `TripItem.js` uses). Lint clean. Committed + pushed `fix/airport-transfer-vehicle-icons`, merged → frontend `develop` `4bd5f1ef`, pushed.

**Workspace (#291):**
- frontend: `develop` `4bd5f1ef` (pushed origin)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (clean)
- content: `master` `3756e5b` (clean)

---

## Session #290 (2026-08-04)

**Achieved — Admin-dashboard: transfer-zone workflow audit + gate/nudge fix.** Ran a 3-agent read-only audit (UXUI + BD + SWE) of the full airport-transfer zone-price→contract→booking admin workflow, sourced from existing vault research (`adr-airport-transfer-zone-pricing.md`, `airport-transfer-rate-dynamic-pricing.md`, `checkout-zone-transfer-card-spec.md`) plus live reads of `components/transfer-zones/*` and `components/contracts/TransferZonesSection.js`. All three agents independently converged on the same top risk: the PRIVATE/CHARTER-only zone-linking gate (JOIN contracts must never link — they price per-seat with no pax selector in the traveler widget, so linking one would silently under-charge groups) was enforced by two different mechanisms depending on screen — a hard server-side query filter on the zone form, but on the contract form (`TransferZonesSection.js`) protection came *only* from the caller's render-gate condition in `ContractFormFields.js`, with zero internal awareness in the component itself. Also flagged: `TestLocationPanel` (address→price verification tool) is fully optional — a zone can Save and go live (`is_active:true` default) without ever being tested against a real address. Implemented both fixes, scoped deliberately small per explicit "no tech debt / no over-engineering / reuse / no side effects" instruction: (1) `TransferZonesSection` now accepts a `contractType` prop and self-guards (`if (contractType && !['PRIVATE','CHARTER'].includes(contractType)) return null`) — mirrors the file's existing `if (!contractId) return null` idiom, omitted prop = old behavior, zero side effect on the one existing caller; `ContractFormFields.js` now threads `contractType={formik.values.type?.value}` the same way it already threads a `contractType` prop to a sibling component one line below (established pattern, not new). (2) `ZoneForm.js` shows a passive warning caption ("Not yet tested against a real address…") when a polygon is drawn but `testMarker` (existing state, already set by `TestLocationPanel`'s `onResolved`) is still null — informational only, no Yup/Formik error key, never blocks Save (rejected a hard block deliberately — punishes legitimate no-test edits like a priority bump on an already-verified zone). Explicitly rejected as out-of-scope for this pass: overlap/priority-tie detection UI, delete-impact preview, unified save button across zone+contract forms, repo-wide `transformResponse` convention retrofit — all real findings, each a separate larger-scope change. Lint clean on all 3 touched files. Committed + pushed directly to admin-dashboard `develop` (`45cbb85`) — already on develop, no separate branch/merge needed.

**Workspace (#290):**
- frontend: `develop` `8c2b5c33` (clean)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `45cbb85` (pushed origin)
- content: `master` `3756e5b` (clean)

---

## Session #289 (2026-08-04)

**Achieved — Admin-dashboard: booking detail table text-overflow fix.** User flagged screenshot of `/bookings/PPF3522223` — Pickup/Dropoff Point and other long values were cut off at the viewport edge instead of wrapping. Root cause: `components/booking/BookingDetails.js:29` wrapped the whole two-column layout in a div with Tailwind `whitespace-nowrap`, which cascaded (CSS `white-space` is inherited) into every `TableCell` in the desktop `BookingInfoDetails.js` table; combined with `TableContainer`'s `overflow: 'hidden'`, long text simply clipped. Only the Remark row had a local `whitespace-normal break-words` override, proving the intended pattern was never applied elsewhere. Fix: removed the stray `whitespace-nowrap` from the ancestor div, and added `sx={{ whiteSpace: 'normal', wordBreak: 'break-word' }}` to all desktop-table value cells (Operator, Contract Id, Type, Travel Mode, dates, Route, stations, flight info, Pickup/Dropoff Point/Time) for belt-and-suspenders wrapping on unbroken long strings. Mobile card layout was already unaffected (had its own `wordBreak: 'break-word'`). Committed + pushed directly to admin-dashboard `develop` (`cb9df45`) — no PR/merge needed since branch was already develop.

**Workspace (#289):**
- frontend: `develop` `8c2b5c33` (clean)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `cb9df45` (pushed origin)
- content: `master` `3756e5b` (clean)

---

## Session #288 (2026-08-04)

**Achieved — Admin-dashboard: airport-transfer coords + booking type badge on booking detail page.** Investigated why `/bookings/PPF3522223` looked like it had no airport-transfer info — confirmed data was present (`InfoFields.direction='address_to_airport'`, `pickuplat/pickuplng`), the FE just never rendered it. Built `MapLinkIcon.js` (pickup/dropoff lat/lng → Google Maps link, inline next to existing Pickup/Dropoff rows in `BookingInfoDetails.js`). Ran a UXUI+BD agent debate on "how should staff tell Airport Transfer / Tour / Transfer apart at a glance" → consensus: explicit badge, `direction`-based, plus a 4th "Needs Review" state for ambiguous data (TRANSFER category + no direction) instead of silently guessing. Ran nextjs+django agent pair to verify the data path — found category lives at `Contract.service_category` on the detail endpoint (confirmed via `operators/models.py:330`, `bookings/serializers.py:79-113`), and that the *list-grid* endpoint exposes the same value under a differently-named key (`contract.type`, `bookings/serializers.py:265`) — scope trimmed to detail-page-only to avoid a two-shape helper (grid deferred). Built `bookingTypeUtils.js` (`getBookingType()`) + `BookingTypeBadge.js`, wired into `pages/bookings/[slug].js` header. Zero backend changes — all fields already serialized. Admin-dashboard `develop` `f65a805` (committed, not pushed).

**Workspace (#288):**
- frontend: `develop` `8c2b5c33` (clean)
- backend: `develop` `38c0470` (clean)
- admin-dashboard: `develop` `f65a805` (pushed origin)
- content: `master` `3756e5b` (clean)

---

## Session #287 (2026-08-04)

**Achieved:** Airport transfer date-aware dynamic pricing. Diagnosed: `resolveZone` returned date-agnostic base price → displayed price ≠ cart price when date-specific ratecards exist. Fixed: BE `ResolveZoneView` now accepts optional `?date=YYYY-MM-DD`, applies `Q(rate_date=date)|Q(rate_date__isnull=True)` (mirrors `_get_display_rate()`). FE `resolveZone` RTK query passes `date` param; `ZonePriceBox` sends `bookingDate` on address select + `useEffect` re-triggers on date change. Vault note created: `03-knowledge/airport-transfer-rate-dynamic-pricing.md`. Both branches merged → develop. BE `38c0470` · FE `8c2b5c33`.

**Workspace:** frontend `develop` `8c2b5c33` · backend `develop` `38c0470` · admin-dashboard `develop` `c003314` (clean) · content `master` `3756e5b` (all clean)

---

## Session #286 (2026-08-04)

**Achieved:** Airport transfer `/airport-transfer/[slug]` full style+UX overhaul. Removed wrong-product elements (TripListingSection, hero search, price subtext). Fixed style tokens (5 components). Calendar date centering fixed via `showFares={false}`. Back button removed, breadcrumb promoted. Breadcrumb invisible bug fixed (double ssr:false → direct NextBreadcrumbs import). Moved breadcrumb above trust strip. Merged to develop `944b2b1f`.

**Workspace:** frontend `develop` `944b2b1f` · backend `develop` `aa56361` · admin `develop` `c003314` · content `master` `3756e5b` (all clean)

---

## #285 (2026-08-04) — Airport transfer detail page UX/style overhaul shipped to develop

**Achieved:** Full style + UX audit of `/airport-transfer/[slug]` page. Removed wrong-product elements: `TripListingSection` (intercity trips, not zone transfers), hero search input (opened intercity trip modal), price subtext (`fromPrice` chain — backend `contracts` field = intercity trip contracts, not zone prices). Fixed style tokens across 5 components: `ZonePriceBox` (`rounded-2xl→rounded-xl`, `rounded-lg→rounded-input`, `bg-gray-50→bg-white`), `ZoneOptionCard` (`rounded-lg→rounded-container`, `bg-gray-50→bg-warm-surface`, `text-green-700→text-status-success`), `PlacePicker` (`focus:border-primary→focus:border-fb-blue` [was broken], `z-50→z-popover`, `rounded-lg→rounded-input/container`), `AirportTransferTrustStrip` (`max-w-[1200px]→max-w-container`), `StationInformation` (`color="primary"→className="text-fb-blue"`, `sm:rounded-lg→sm:rounded-container`, description typo fallback). Calendar date text centering fixed via additive `showFares={false}` prop on `SlideCalendar2` — skips invisible placeholder row that was pushing date text top-aligned. Removed back arrow button from `AirportTransferHeader` (props 8→1, `departureStation` only) — breadcrumb handles navigation. Breadcrumb invisible bug fixed: double `ssr:false` wrapping (`StandardBreadcrumb` → `NextBreadcrumbs`) caused silent render failure — import `NextBreadcrumbs` directly, one dynamic layer. Moved breadcrumb above trust strip (immediately below hero). All changes on `fix/style-consistency-airport-transfer` → merged to develop `944b2b1f`.

## #284 (2026-08-03) — Airport-transfer checkout zone card + notification fixes: validated + shipped to develop

**Achieved:** Validated merged airport-transfer stack on real BE data (user junedarkside@gmail.com, order VAR1397366, items Aug 6–8). Found + fixed 3 bugs post-merge: (1) `ZoneTransferRoute.js` — `address` var always picked `dropoffPoint` first regardless of direction (now branches on `isAirportFirst`); (2) `TripsConfirmation.js` — same address-pick bug + `airportName` resolved to route placeholder "Hatyai Any Hotel" instead of real airport (fixed: `zoneAirportFirst` computed before `zoneAddress`, `airportName` from `contract.transfer_airport.station_name`); (3) BE carts `ContractSerializer` missing `transfer_airport` field — added `get_transfer_airport()` (same ZoneContract query as products serializer). `EnhancedTripCard` updated to pass `airportStation` + `airportIata` from `transfer_airport`. `ZoneTransferRoute` now accepts `airportIata` prop + renders `Hatyai Airport (HDY)`. Notification gaps fixed: `orders/services.py` — added `direction` to `context` from `InfoFields.direction` + added `direction/pickuppoint/dropoffpoint/pickuptime/dropofftime` to `context_message` (Telegram payload) + added `booking.direction` to `customer_context` (email). `bookings/tasks.py` — zone-transfer block in Telegram message (direction label + pickup + dropoff, guarded by empty-check, zero side-effect on non-zone). Email template `booking_confirmation_template.html` — timeline FROM/TO station now branches on `booking.direction` (airport_to_address → typed address as arrival; address_to_airport → typed address as departure; blank → unchanged for route-list + activity). Tested synchronously: all 3 bookings SAW4621917/AJW0055474/PPF3522223 Telegram + email sent OK.

**Git:** FE uncommitted (3 files: `ZoneTransferRoute.js`, `TripsConfirmation.js`, `EnhancedTripCard.js`). BE uncommitted (4 files: `booking_confirmation_template.html`, `bookings/tasks.py`, `carts/serializers.py`, `orders/services.py`).

---

## #283 (2026-08-03) — Airport-transfer checkout + booking display: 6 branches shipped (FE 5 + BE 1), MERGED to develop + pushed

**Achieved:** FE + BE checkout-zone-card direction-storage pipeline, booking-display direction gate (no guessing), merged 6-branch stack to develop and pushed to origin. System check + migration validation passed. Git: FE `b9c14639`, BE `f6a9146`.

**Sequence:** (1) UXUI+BD agent research → 3-reviewer impl plan for detail-page conversion spec (8 ROI-ranked FE changes, DO-NOT-BUILD patterns). (2) FE airport-detail-cosmetics: R1 "from THB 400" hero price, R5 hero copy fix, R6 "All Destinations" label fix, R3 static trust strip, R7/R8 deferred, Bug B AirportTransferJsonLd empty-crash guard, dead `pickupMode` cut, **PlacePicker transparency fix** (inline-style override, not z-index). (3) FE airport-zone-card-rich: ZoneOptionCard extracted + vehicle/seats + Instant/Free-cancel row + direction chip. (4) FE airport-zone-direction-switch: deleted clear-on-tab useEffect, added `From ⇄ To` swap, removed route tabs. (5) 3-agent checkout-zone-card debate: direction inversion + address on card. FE fix/checkout-zone-card: EnhancedTripCard reads `selectTripInfo` → address+direction+vehicle, React.memo, ZonePriceBox stash explicit direction. Senior FE flagged guest→auth merge ID-change (deferred). (6) BE+FE cross-repo direction+framing: BE `feat/checkout-direction-and-station-type` added `CartItemCheckoutInfo.direction` + `InfoFields.direction` columns, persisted both write paths, TripSerializer +station_type/iata (migrations carts 0017 + bookings 0048, system-check clean, 28 tests pass). FE `feat/checkout-airport-framed-card`: getAirportEnd() → "Hatyai Airport (HDY)→…" for route-list, priority: zone-address > airport-framed > station-route > name, degrades safe.

**Booking display:** Gate on `hasStoredDirection()` only (no guessing). Stored direction → full airport treatment (badge, route frame, label). No stored direction → plain station route (general booking). New zone-swap bookings store direction end-to-end via stash→checkout→booking.

**Git state:** All 6 branches **MERGED to develop** and **PUSHED to origin**. FE `develop` tip `b9c14639`, BE `develop` tip `f6a9146`. Main untouched. No stashed work.

---

## #282 (2026-08-02) — /airport-transfer INDEX card redesign: image-led picker cards SHIPPED to develop (FE only, 0 BE)
UXUI+BD agent team → bare text StationCard → image card (`next/image` fill + object-cover group-hover:scale-105 + blur + onError→bgDefault, idiom copied from PopularRouteImageCard NOT forked). IATA chip, Popular badge (BKK/DMK/HKT), city·province subtitle, focus-ring a11y fix. Data caveat verified: `location_name.image` null for ALL 4 airports → branded fallback today. Width matched homepage "Explore Popular Routes" via shared Section+SectionHeader (py-6 px-4 xl:px-0). Fixed crash: capitalizeWords got nested location_name OBJECT. Demand-first IATA pin sort (zero-BE, degrades safe). 2 branches → develop: `0b24cc82`, `7d9d9dd3` (final). main untouched. Atoms: [[nextimage-card-fallback-idiom]], [[demand-first-iata-pin-sort]].

---

## #281 (2026-08-01) — Airport-transfer multi-contract-per-zone + JOIN-restriction: committed+merged+pushed (3 repos) + AD UX fixes

**Merged + pushed all 3 develops** (the #280 feature was uncommitted; now shipped to `origin/develop`): backend `8fb94ea` (multi-contract M:N + JOIN-block + migrations 0030–0033; 28 tests) `126f213..8fb94ea`; admin-dashboard `c003314` (Slice 2 + both pages + 3 UX fixes) `3ea1fa5..c003314`; frontend `3c3e590c` (tier cards) `b959f1ea..3c3e590c`. **AD UX fixes** (branch `fix/transfer-zones-gate-transport-private-charter` `29f0925`): (1) contract-page zones gate widened — was `service_category==='TRANSFER'` (hid transport contracts like 183=TRANSPORTATION+PRIVATE), now `isTransportationCategory(cat) && type∈{PRIVATE,CHARTER}` + added missing import (else ReferenceError); (2) transfer-zones list page client-side search+status filter (mirrors vehicle-types, 0 BE); (3) ZoneForm contract picker operator+station dropdowns + `isOptionEqualToValue` (no MUI chip crash). JOIN-trap root cause: contract 184=type JOIN → guard 400s correctly; fix = widened gate hides section for JOIN. All lint clean; BE 28 tests green; `migrate --check` clean.

## #280 (2026-08-01) — Airport-transfer zone: multi-contract-per-zone + JOIN-restriction (built, uncommitted at session end)

**Multi contracts per zone (M:N):** `TransferZone.contract` single FK → `ZoneContract` link table (zone·contract·is_active·unique), M2M-through idiom. Migrations 0031 (schema) + 0032 (backfill). SSOT `_apply_diff` sync (both admin sides, race-safe). `resolve-zone` → `options:[{contract_id,contract_name,price}]` (per-contract MIN, skip null). FE `ZonePriceBox` tier cards (`ZoneOptionCard`). AD `ZoneForm` multi-select + contract-page `TransferZonesSection` + `contract-zones/` endpoints + `TestLocationPanel` options. **3-agent scrutiny → fix-then-ship** (sync single-source, null-price skip, FE tab-reset, dead-code cut). **JOIN-restriction** (BD+UXUI debate → nextjs/django/senior review): `assert_zone_eligible` SSOT (serializer + APIView + model.clean) + migration 0033 (deactivate legacy JOIN links, live-caught 184/zone2) + AD picker `?contract_type=PRIVATE,CHARTER`. 28 tests. CHARTER kept, JOIN deferred (unblock w/ pax selector). ADR §6+§6b. All 3 branches uncommitted at #280 close (committed+merged+pushed in #281).

## #277-279 (2026-07-30 → -31) — Airport-transfer zone pricing: Slices 1–4b built + live-verified

5-agent review + 4-agent polygon-shape debate → POLYGON only (JSONField + ray-casting, NO PostGIS); Google DrawingManager removed v3.65 → click-to-draw. **Slice 1** BE zone core (`TransferZone` + `stations/geo.py` + `resolve-zone` + admin + migration 0030, 13 tests). **Slice 2** AD polygon-draw page (`transfer-zones/` DataGrid+drawer, `ZoneMap` click-to-draw+undo/delete/finish, `ZoneForm`, `TestLocationPanel`, sidebar+icon, `@react-google-maps/api`). **Slice 3** FE traveler picker (`ZonePriceBox`+`PlacePicker`, `tripsApi.resolveZone`, mounted on `[slug].js`, show-price-only). **Slice 4a** BE booking persistence (+4 coord FloatField + `resolved_contract` FK on InfoFields+CartItemCheckoutInfo, migrations 0047/0016, 17 tests, SPLIT verdict). **Slice 4b** FE Book wiring (withCartValidation, bookingDate+tabValue, full-contract fetch, BookButton+saveTripInfo stash). 2 bugs fixed: `session.id` gotcha; RTK Immer-frozen clone. Branches: BE `feat/airport-transfer-zone-pricing` `0da5a1c`, AD `feat/transfer-zone-admin` `6f36624`, FE `feat/airport-transfer-zone-picker` `00000a80`. Google billing was the live-map blocker (later resolved). All unmerged.

---

## Session #275 — 2026-07-29 — coupon admin management shipped to PROD (BE CRUD + AD UI)

- **5-agent marketing debate** (UXUI/marketing/nextjs/django/biz-dev) → verdict: ship coupon admin UI first (trapped capability — BE `Coupon` model built, zero admin UI). Report → `02-areas/marketing-tools-debate-2026.md`.
- **BE**: `CouponAdminSerializer` (write-capable, reuses model `clean()`) + `CouponViewSet` (`IsAdminOrIsStaff`) at `/admin-dashboard-orders/admin/coupons/`. No new model/migration. Develop `13ce885`.
- **AD**: coupon CRUD page + `CouponForm.js` (Formik+Yup) + `couponsApi.js` + `CouponRestrictionSelect.js` (operator/route M2M autocomplete). Develop `3ea1fa5`.
- **2 shared-form bugfixes**: `CustomSelect` key-gotcha (`option.key` not `label`); `CheckBoxControl` Formik-binding (render-prop + `type="checkbox"`). Affected coupon + hero-banner + ModalPopUp.
- Both repos DEPLOYED TO PROD 2026-07-29.

**Session #274 (2026-07-29) — personalized homepage band for logged-in users + card token fixes (FE):**
- New `components/FrontPage/PersonalizedHomeBand.js` — client-only `dynamic(ssr:false)` band below hero. Logged-in: "Welcome back, {name}" + upcoming confirmed trips (`BookingItemCard`, dynamic 1-col/2-col grid) + "Book again" rebook chips from completed history (deduped by route). Guest: `null` → byte-identical static/ISR homepage (no cross-user leak).
- `homepagev2.js` — band after `<DiscoverySection>` + `useSession` gate hiding guest booking-lookup strip + `MyBookingsSection` for logged-in. No `getStaticProps` change.
- Card token fixes: `PopularRouteImageCard` `rounded-lg`→`rounded-xl` + dropped inline `boxShadow:'none'`; `GuideCard` → standard `border-gray-200 shadow-sm hover:shadow-lg`. `ReviewCard` left `rounded-md`.
- Gotcha: `/bookingsummary/` reads `tab` numeric (`'1'`=upcoming); string `'upcoming'` silently returns ALL rows. Guarded w/ `getBookingStatus==='confirmed'`.
- Shipped `86912129` → merged develop `a505cfcb`. Deployed prod 2026-07-29.

**Session #273 (2026-07-26) — login page input focus ring removed:**
- Removed focus ring flash from email + password inputs on `/account/login`.
- `AuthInput` + `AuthPassword` in `FormControl.js`: replaced `focus:ring-2 focus:ring-blue-500 focus:border-transparent` → `outline-none focus:border-blue-500`. Base `outline-none` (not focus variant) prevents browser default outline flash before React render.
- Committed `9b37ef92` on `fix/login-input-focus-ring`, merged → develop, pushed.

---

**Session #272 (2026-07-26) — Dashboard redesign merge + profile menu link:**
- Added Dashboard link to profile menu Account section (`components/auth/ProfileMenu.js`).
- Merged `feat/dashboard-redesign` → develop `8401d3fd`, pushed.

---

**Session #271 (2026-07-26) — Account dashboard redesign + profile menu dashboard link:**
- Audited `/account/dashboard` with 3-specialist agent team (UX/UI + React architecture + Next.js perf) + design token audit.
- `ProfileHeader.js`: 358→90 lines — collapsed mobile/desktop JSX duplication, removed `showStats`/`stats` props, extracted `stringToColor`/`stringAvatar` to `helpers/avatarHelpers.js`, applied COLORS tokens.
- `AccountCard.js`: removed `hover:scale-105` (touch persist bug), `transition-all` → `transition-shadow`, `rounded-xl` → `rounded-container`, white-card variant added.
- `StatCard.js` (new): uniform neutral stat tile — gray icon column + hairline divider + dark number + muted label. No per-card color variation.
- `ActivityFeed.js` (new, `components/account/`): extracted activity list, `onNavigate` prop (no internal router side-effect).
- `helpers/avatarHelpers.js` (new): reusable avatar utils extracted from ProfileHeader.
- `store/api/accountApi.js`: fixed circular `providesTags`, added `keepUnusedDataFor: 60` on stats+activity.
- `pages/account/dashboard.js`: `getServerSideProps` server-side auth redirect, per-section loading, primary action strip, `max-w-container`, 0 gradient surfaces.
- `helpers/designSystem.js` + `tailwind.config.js`: added `brand.indigo`/`brand.indigo-light` tokens.
- `components/auth/ProfileMenu.js`: added Dashboard link (first item in Account section) → `/account/dashboard`.
- Merged `feat/dashboard-redesign` → develop `8401d3fd`. Build: ✓

---

**Session #270 (2026-07-25) — All 3 repos shipped to production:**
- Fixed git checkout error (`migration.js` uncommitted WIP blocked branch switch).
- AD `migration.js`: added `HelpIcon` tooltip to Trip Migration page. Committed `1b079b2` → main.
- BE + FE + AD all on `main` — shipped to production.
- Workspace: frontend `main` (`b3ee0fdf`) clean; backend `main` (`ae68e51`) `resources.txt` uncommitted; admin `main` (`1b079b2`) clean; content `master` (`3756e5b`) clean.

---

**Session #269 (2026-07-24) — AD contracts: Trip/Route column + grouped trip picker:**
- `ContractSerializer` exposes nested `trip` via `TripWithRouteSerializer`. `select_related` extended to cover `trip__route__departure_station/arrival_station`. BE `ae68e51` → develop.
- `ContractsDataGrid.jsx`: new "Trip / Route" col (`flex:1, minWidth:220`) — `departure_station → arrival_station`; non-transport = `-`; Tooltip clips. AD `0484eac` → develop.
- ⚠️ Manual QA NOT run.

---

**Session #268 (2026-07-24) — AD locations: soft duplicate warning (FE-only):**
- `/routemanagement/locations` create+edit warns on duplicate name (normalized). Save Anyway override. No BE change.
- Shared utils: `locationDuplicateUtils.js` + `useLocationDuplicateCheck.js`. Pattern from route duplicate check.
- Modified: `locationsApi.js`, `locationEdit.js`, `LocationCreateDialog.js`.
- Shipped: `f5ec0a6` → merged `--no-ff` → AD develop `1923124`. ⏳ Manual QA not run.

---

**Session #267 (2026-07-24) — AD bookings: Support SEP resend counter live update:**
- **Root cause traced end-to-end.** "Support SEP" col (`DataGridComp.js:230`) → `renderResendOp` → `ResendOp` `Resend (N)` button (`number=row.added`). N stuck at (0) despite backend working.
- **Backend CORRECT (untouched):** POST `/admin-dashboard/booking-send/` → `SendBookingViewSet.create` → `booking.added += 1; booking.save()` (`bookings/views.py:406`). `added` in `BookingSummarySerializer` (`serializers.py:191`). DB increment persists.
- **Bug 1 (primary):** `ResendOp` POSTed via raw `clientFetchDataFromApi` — no cache invalidation → RTK held stale `added:0` for the session. **Fix:** new `resendBookingToOperator` mutation in `ordersApi.js` (`invalidatesTags:['Booking','BookingSummary']`); `ResendOp` rewritten to `useResendBookingToOperatorMutation` — same props (no ripple to `DataGridComp`), added error branch + `disabled` while sending. Grid auto-refetches → N updates live.
- **Bug 2 (latent):** `getBookingSummary` missing `transformResponse` that every sibling query has (BE paginated `{results}`). Added `(r) => r?.results ?? r` — one-liner, so `added`/all fields reach rows.
- **Files:** `store/api/ordersApi.js`, `components/booking/ResendOp.js`. Committed `7aea52c` → merged `--no-ff` → AD develop (`36ec8ea`), pushed. No lint/build run this session.
- ⏳ Manual QA NOT run — click Resend, expect (N+1) live + persist on reload.
- **⚠️ Flagged (out of scope):** `BookingSummaryViewSet.get_queryset` filters `user=request.user` + `order__status='paid'` (`bookings/views.py:48-52`) — admin page scoped to logged-in admin's own paid bookings. If admin should see ALL users' bookings, that endpoint is wrong. User's call.
- ✅ Backend #264 search fix COMMITTED this session — `d39ca6d` → develop, pushed. All 4 repos now clean.

---

**Session #266 (2026-07-24) — AD trips: Copy Trip + time-aware duplicate warning:**
- **Copy Trip** — `ContentCopyOutlined` row action opens dialog in create-mode prefilled from source row. Frontend-only (no backend endpoint — trip has no deep children). "Copy Trip — {route}" title.
- **Time-aware duplicate warning** (frontend-only, non-blocking). 3-way rule: scheduled = route+operator+dep_time+arr_time; timeless charter/transfer = route+operator+override stations. Operator NULL (shared) normalized both sides (`?? ''`). Confirm dialog names matched trip(s) + 100-row-cap disclosure. Ports the `routeEdit.js` lazy-query pattern from #265.
- **`tripsApi.js`** — transform preserves raw override station ids + null-guard; exports `useLazyGetTripsQuery`. `contract_trip_count` in list operator column.
- Fixed pre-existing edit-prefill bug (override stations blank on edit). Copy-of-shared blast-radius guardrail Alert.
- UX + BD experts audited plan pre-build. Committed `78c7fa2` → merged `--no-ff` → AD develop (`0b0b301`). Lint clean, `next build` passes. Manual QA (10-item) NOT run.

**Session #265 (2026-07-24) — AD route management: auto-name + duplicate detection:**
- Auto-default route name from dep → arr station names on create; stops on manual edit (`nameEditedByUser` ref); resets on close
- Station-pair dup check on select (lazy `useLazyGetRoutesQuery`) + route-name dup check at submit (case-insensitive), merged
- Confirm dialog to override any dup; edit mode excludes self
- `FormControl` → `Field`+`TextField` for route_name (Formik onChange override bug)
- Committed `e02fff3` → AD develop, pushed

---

**Session #264 (2026-07-24) — space-insensitive search on 6 admin viewsets:**
- Normalized search added to `RouteViewSet`, `TripDashBoardViewSet`, `migration_audit`, `PlaceViewset`, `DashBoardStationViewSet`, `DashBoardLocationViewSet`
- Pattern: `normalize_search(s)` strips spaces/hyphens + lowercases → annotate FK fields with `Replace(Lower(F(...)), output_field=CharField())` → filter annotated fields
- `output_field=CharField()` fix for Django 3.2 nullable FK expression inference
- Backend curl-verified (trips 19, routes 11, stations 4, locations 1, places 1, migration audit 19)
- Backend only — no frontend changes, no migrations
- Uncommitted at session end (`products/views.py` + `stations/views.py`)

---

## Session #263 — 2026-07-23

**Achieved:**
- **Cart 400 fixed.** `carts/serializers.py` `get_departure_station`/`get_arrival_station` returned `ReturnDict(<string>)` → `ValueError` → 400 on every transport cart. Fixed: return `station.station_name` directly.
- **FE stale-token 401 storm fixed.** Extended `publicEndpoints` skip-list in `store/api/tripsApi.js` + `store/api/api-slice.js`.
- **B1 effective-station in recommendations + detail** — `ContractRecommendationSerializer.get_route` + `ProductDetailSerializer.to_representation` patched.
- **B2 admin trip search fixed** — `route__departure_station__icontains` (FK int) → `route__departure_station__station_name__icontains` + OR-branch for override stations.
- **N+1 prevented** via `select_related` in 5 service chains.
- **All merged → develop** (BE `8d03b30`, FE `b3ee0fdf`).

---

## Session #263 — 2026-07-23
CART + FE FIXES. Fixed universal cart 400 (`GET /carts/{uuid}/` broken for all transport trips since `c00c87a` merge): `carts/serializers.py` `get_departure_station`/`get_arrival_station` called `StationSerializer(station).data` → `ReturnDict(<string>)` → `ValueError 400`; fixed by returning `station.station_name` directly. Fixed FE 401 storm on public endpoints (tripfilter, carts): extended existing `publicEndpoints` skip-list in `store/api/tripsApi.js` + `store/api/api-slice.js` so stale Bearer never attached to AllowAny endpoints. Also fixed B1/B2 effective-station: `ContractRecommendationSerializer.get_route` + `ProductDetailSerializer.to_representation` now use `effective_*_station` override; admin trip search fixed (`route__departure_station__icontains` FK-int bug → `__station_name__icontains`); N+1 prevented via `select_related` in services.py + views.py. All merged → develop (BE `8d03b30`, FE `b3ee0fdf`). → [[operator-scoped-trip-station]] · [[guest-cart-401-refresh-storm]]

---

## Session #262 — 2026-07-22
PROD SEAT-CHECK DEBUGGING (real Lomprayah live). Diagnosed prod MAPPING_NOT_FOUND = station-record mismatch: contract `bangkok-khao-san-to-koh-tao-1220` route dep station = `"boonsiri counter khaosan bangkok"` but mapping row targets a different record `"Lomprayah Bangkok khao san"` (backend matches by station FK) — data-entry issue. Built BE debug block on `check-seat-availability` (operator, dep/arr station id+name, from/to/date/time, n8n URL, all operator mappings; always-on for MAPPING_NOT_FOUND, `?debug=1` elsewhere) + AD panel to render it. Timeout 15→25s (n8n `/webhook/search` latency 10-19s variable; "browser-first then works" = timing luck). Fixed HTTP 500: n8n returns `{"data":"no trip"}` STRING when no service → parser did `data_list[0]`.get on a char → `AttributeError`; now guards `data` type. 4 branches merged develop → deployed main (BE `073623b`, AD `ef41c7b`). Atom [[n8n-seat-search-response-contract]]. Resume: fix prod mapping data (delete+recreate against correct dep station → id 43/44), then E2E. → [[seat-availability-reseller-operator-gap]] · [[station-mapping-multi-operator-design]] · [[n8n-seat-search-response-contract]]

---

## Session #261 — 2026-07-22
SEAT-CHECK Part B SHIPPED → main — `operator_station_id` in Station Mapping dialog is now a Supabase `RouteID` autocomplete (unblocks #260's deferred item; **no BE proxy needed**). PostgREST leaks the exposed-schema list in the error `hint` on any invalid `Accept-Profile` → hook probes `schema('__probe__')`, parses hint, matches operator schema by name-prefix (longest, denylisted non-operator schemas), confirms via `Operator` col. `Lomprayah`→`lompraya` (lowercased 8-char truncation, not derivable); `RouteID` cols `Route`/`ID`/`Operator`, 39 rows. Label `"Route (ID)"`, saves `ID`; `freeSolo` preserves stale ids; no schema → free-text fallback. New `helpers/operatorRouteIds.js` (pure) + `hooks/useOperatorRouteIds.js` (module-cached discovery). Grid sorts by id asc. AD+BE deployed → main (AD `8780af4`, BE `5baebe8`). Prod remaining: `migrate operators` 0069+0070; recreate "lomprayah" op+mappings as real data. 2 atoms extracted. → [[postgrest-exposed-schema-hint-discovery]] · [[supabase-per-operator-schema-routeid]] · [[station-mapping-multi-operator-design]]

---

## Session #260 — 2026-07-22
SEAT-CHECK-RESELLER — `Contract.seat_check_operator` FK lets a reseller contract check seat availability against a source operator (Silaphat resells "lomprayah"). Resolution `operator = contract.seat_check_operator or contract.operator` covers mapping lookups + api_url. BE migration `0069`, AD form Autocomplete + transform. STATION-MAPPING-SEAT-API-VISIBILITY: page shows operator/API per mapping (chip + `Seat API` grid col via `operator_has_api` serializer field + `?our_station=` filter). DROP-CONTRACT-SEAT-API-URL: removed redundant `Contract.seat_availability_api_url` (1/81 usage, migration `0070`) + URL `.strip()` fix. All merged → develop + pushed (BE `5baebe8`, AD `3fc14e0`). Part B (Supabase id autocomplete) deferred — assumed `RouteID` anon-unreadable, needs BE proxy. → [[seat-availability-reseller-operator-gap]] [[station-mapping-multi-operator-design]]

---

## Session #259 — 2026-07-22
FAQ CSS FIX — Trip detail page FAQ section alignment + spacing fixed. Removed conflicting `mx-auto mx-2` → `mx-auto px-2 md:px-3 xl:px-0`. Fixed padding conflict (`p-4` outer → inner `<div className="p-4 md:p-5">`). Tightened heading `mb-3→mb-2`, item padding `py-2→py-3`, `rounded-md md:rounded-lg` → `rounded-md`. Committed `1e6eaec0` on `fix/faq-spacing-alignment` → merged develop → pushed `4758b4b1`.

## Session #258 — 2026-07-21
TRIPS QA + PROD DEPLOY + CHAT-IMAGE-SEND + SEAT-AVAILABILITY MIGRATE — Trips redesign QA passed, prod deployed (ISR cache flushed). CHAT-IMAGE-SEND prod deploy: Supabase SQL 003, Pillow bump, BE→AD→FE deployed, smoke passed. manage.py migrate 0066/0067/0068 on prod.

---

## Session #257 — 2026-07-21
SEAT-AVAILABILITY commit+push — Committed BE (`c535dd3`: 4 files + migrations 0066-0068) + AD (`b1996c7`: 4 files) to develop. Then completed: Trips Redesign QA, CHAT-IMAGE-SEND prod deploy, `manage.py migrate` 0066-0068 on prod.

---

## Session #256 — 2026-07-21
SEAT-AVAILABILITY-CHECKER-REBUILD — BE station-mapping feature was never committed (migration existed, model/views/serializer lost). Rebuilt from scratch: `OperatorStationMapping` model + CRUD viewset + `check-seat-availability` @action on `ContractDetailViewSet`. Wired n8n webhook (`https://n8n.smartenplus.co.th/webhook/search`). Added `seat_availability_api_url` field to Operator + Contract models (migrations 0067+0068) with priority chain: contract > operator. Fixed `seatStatus` parsing bug (`== 'Available'` exact match → `!= 'Sold Out'` logic). Added API URL fields in AD: OperatorForm + ContractFormFields + useContractFormData + contractUtils. All uncommitted (BE 4 files + 3 migrations; AD 4 files).

---

## Session #255 — 2026-07-20
STATION-MAPPING + SUPABASE-ERROR-LOGGING — Diagnosed Supabase 406 (transient outage, not code bug). Added HTTPError body logging to `_fetch_schema`. Committed + merged BE fix (`fix/cs-supabase-error-logging` → develop). Committed + merged AD station-mapping feature (`feat/station-mapping` → develop): SeatAvailabilityChecker, station-mapping page, nav entry, CRUD API endpoints.

---

## Session #254 — 2026-07-20
BRANCH-CLEANUP + CHAT-DESIGN-TOKENS — Pruned 45 merged branches across all 3 repos. Fixed ScrollTop overlap. Added CHAT design tokens. Refactored ChatBubble + ChatPanel to use tokens. Commit `4957f22b` → develop.

---

## Session #253 — 2026-07-19
TRIPS-PAGE-REDESIGN — `/trips` index redesigned via 3-agent team (UX auditor → designer → frontend implementer). `pages/trips/index.js` rewritten 733→162 lines: `getStaticProps` + ISR revalidate:3600, `PageSeo`, reuses `components/locations/{SearchBar,FilterControls,StatsDisplay,EmptyState}` unchanged. New: `components/trips/RouteCard.js` (image-forward, `TouristTrip` schema, gradient overlay, `departure → arrival` text), `hooks/useTripsFiltering.js` (memoised search+sort on joined route string), `hooks/useTripsStructuredData.js` (`ItemList` of `TouristTrip` + `BreadcrumbList` + `CollectionPage` with `speakable`). First page in codebase with `hreflang="en"` + `hreflang="x-default"`. Projected SEO 8.5 / AEO 8.5 / GEO 7.0. **Status: COMMITTED `db5982be`, not yet pushed.** Branch `feat/trips-page-redesign`.

---

## Session #252 — 2026-07-18
LOCATIONS-PAGE-REDESIGN — visual redesign of `/locations` index page on branch `feat/locations-page-redesign`. Mirror of destinations redesign: image-forward `LocationCard`, hero with H1 "Where in Thailand Do You Want to Travel?", back+share overlay (`top-2 z-40 pointer-events-none/auto`), `SearchBar` + `FilterControls` + `StatsDisplay` extracted into `components/locations/`. Two new hooks: `useLocationsFiltering(allLocations, searchTerm, sortOption)` (memoised filter+sort) and `useLocationsStructuredData(allLocations, domainURL, lastReviewedTimestamp)` (returns `seo`, `itemListElements` for `ItemList` JSON-LD `TouristDestination`, `breadcrumbItems`, `organizationSchema`, `CollectionPage` schema with `lastReviewed`). `pages/locations/index.js` reduced to composition. Status at session end: UNCOMMITTED on `feat/locations-page-redesign` (`354889f1`); later merged → develop `a25ff23d`. Workspace: backend `main` `06423c5` · admin `main` `21d03eb` · content `master` `3756e5b` — clean. Resume was: commit + push + verify locations JSON-LD/OG + mobile QA 375/768/1280 + parity vs destinations redesign.

---

## Session #251 — 2026-07-18
DESTINATIONS-PAGE-REDESIGN — full visual redesign of `/destinations` index shipped → develop. 3-agent team (design-review auditor → designer w/ 12Go/Booking/GYG/Klook research → react-specialist impl). Image-forward overlay cards (`location.image || DEFAULT_ROUTE_IMAGE`), go-TO intent H1 "Where in Thailand Do You Want to Go?", full a11y pass. 2-agent mobile debate (verdict YES-WITH-FIXES) → sticky FilterControls (`top-0 md:top-20`), mobile SearchBar moved hero→sticky bar, responsive MUI select widths, Book CTA pinned card-bottom (`mt-auto`). 4 commits → merge `354889f1` → develop (pushed): `943deb7d` redesign · `6d89c875` CTA pin · `24c92257` mobile sticky · `1e4f2f46` hero pill buttons 36→44px sitewide (16 non-destinations files). 22 files total. Lint clean. Build skipped (trivial touch-target change). Full design+debate record: `01-projects/destinations-page-redesign.md`. Workspace: frontend `develop` `354889f1` clean; `feat/destinations-page-redesign` kept on remote. Resume: (1) destinations live test (grid/card interactions, search/filter/expand/CTA) — local dev backend returned 0 locations; (2) carry-forward prod-deploy queue: TRIP-CARD-V2 (ISR cache flush + ENV.md row), REC-PRICE-FIX (Redis `recommendations:*` flush + `manage.py migrate` operators/0064), CHAT-IMAGE-SEND (Supabase SQL 003 + Pillow bump + deploy BE→AD→FE + smoke).

---

## Session #250 — 2026-07-15
TRIP-CARD-V2 — built flight-OTA style card from scratch (`TripCardV2.js` + `TripItemLayoutV2.js`). Env flag `NEXT_PUBLIC_TRIP_CARD_V2` (unset=V2, `false`=V1 rollback). 2-agent UX/Design audit → scorecard V2 7/7 vs V1 4.5/5. P1 batch: stops text under arrow, JOIN chip, amenity icons, station `line-clamp-2`, `max-w-[560px]`, 44px chevron. `SkeletonSection` rewritten to V2 anatomy; `TripSearchResults` inline skeleton replaced. Mobile compact legs breakpoint-split (`hidden sm:flex` full / `flex sm:hidden` compact). 8 commits → develop, pushed `f70dbe5d`. `NEXT_PUBLIC_TRIP_CARD_V2` row still needs adding to ENV.md (docs/ permission denied this session). VAULT AUDIT — `01-projects/trip-card-v2-flight-style-audit.md` created; `index.md` + `log.md` updated. Workspace: frontend `main` `f70dbe5d` · backend `main` `06423c5` · admin `main` `21d03eb` · content `master` `3756e5b` — all clean. Resume: (1) TRIP-CARD-V2 prod deploy — ISR cache clear (`smartenplus_next_cache` Docker volume) + add `NEXT_PUBLIC_TRIP_CARD_V2` to ENV.md; (2) REC-PRICE-FIX prod — BE main has `06423c5`, deploy + MANDATORY Redis flush `redis-cli --scan --pattern "recommendations:*" | xargs redis-cli del` + `manage.py migrate` (operators/0064); (3) CHAT-IMAGE-SEND prod — Supabase SQL 003 + `pip install -r requirements.txt` (Pillow bump) + deploy BE→AD→FE + smoke.

---

## Session #249 — 2026-07-15
BE-HOMEPAGE-PRICE FIXED — all 8 `Min(selling_rate)` finder annotations in `products/services.py` now filter `contract_ratecard__is_active=True` (inactive ratecards could win Min → unbookable "From" prices on rec cards). Branch `fix/rec-price-active-filter` → develop `06423c5`, pushed to origin. 4-agent audit (BD/UX/BE/FE) confirmed fix complete; other price paths already `is_active`-filtered. DEPLOY GOTCHA: Redis `recommendations:*` flush mandatory post-deploy (skip-if-fresh guard `tasks.py:66-75` serves stale prices up to 24h). REC-SLOT-WASTE closed DO-NOTHING per 4-agent audit — near-zero incidence, `checkout_recommendation_empty` GTM monitors it. Vault: `01-projects/rec-engine-report-audit.md` created, atom extracted `[[precompute-cache-stale-after-logic-fix]]`. Vault commit `eea2c7f` pushed.

---

## Session #248 — 2026-07-15
REC ENGINE — 5 phases shipped across FE + BE, all → develop. Phase 1 (`fix/rec-quick-wins`): 2s timeout on recommendationsApi · `recommendation_modal_open` GTM · `chidren` typo fix · sessionStorage Safari guard. Phase 2 (`feat/rec-purchase-event`): purchase attribution — `markRecSourcedContract` + `fireRecommendationPurchaseEvents` in `helpers/gtmUtils.js`; wired in `RecommendationBookingModal.js` + `hooks/useOmisePayment.js`. Funnel complete: view→click→modal→add_cart→purchase. Phase 3 (`fix/rec-checkout-filter`): `filterValidRecommendations` applied at checkout rec list. Phase 4 (`chore/rec-remove-ratecard-hook`): deleted `hooks/useRecommendationRatecards.js` (−138 lines). Phase 5 (`feat/rec-never-empty-fallback`): `find_global_fallback()` in `products/services.py`; hybrid dedupe; `booked_count` default 10→0; migration `operators/0064` applied locally. 28/29 BE tests pass (1 pre-existing failure `test_find_similar_contracts`). FE develop: `9fd5b0a5` · BE develop: `f0aea8c`.

---
