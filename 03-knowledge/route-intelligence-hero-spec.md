# RouteIntelligenceHero Spec (Locked 2026-06-14)

## Summary
New gradient hero component for `/trips/[from]/[to]` showing route identity + stats (no photo). Replaces photo hero that ate ~540px first screen.

## Why It Matters
Photo hero dominated first viewport, hid bookable results. Real route-level data (price, duration-range, departure count, first/last) is more useful than decoration. 3-agent review (FE-arch + UX + BE-data) locked spec.

## Detail
**New file:** `components/trips/RouteIntelligenceHero.js`. Gradient (ocean-blue→seafoam), NO photo, **180px desktop / 140px mobile (max 220px)**. < 200 lines.

**Layout (top→bottom):**
1. Back + Share row (reuse existing)
2. **Leg badge** (round-trip only): `[OUTBOUND JOURNEY]` blue / `[RETURN JOURNEY]` green, none for one-way. Driven by `isReturnJourneyActive` + `tripModeDisplay`.
3. **Route title** active direction. Return SWAPS `Koh Lipe → Hat Yai` (mirror `activeFrom/activeTo`).
4. **Stats row:** `From ฿N` · duration RANGE `4h30m–6h` (never average) · `N departures` · `First HH:MM · Last HH:MM`
5. **Edit Search** trigger + passenger chip (reuse `SearchDialogTrigger` + passenger modal — NO inline form)

**3 refinements from screenshot review:**
- ADD First/Last departure via `Math.min/max(trip.departure_time)`
- "From ฿N" must match bookable cards — use advance_hr-filtered `min_display_rate` (hero cannot advertise unbookable contract)
- DROP "today" → show `N departures on 16 Jun` (date-scoped)

**Overlap:** Hero owns route identity. `ResultsPageHeader` reduces to trust-chip row only (Phase 2). Keep `SearchCover`/`FeaturedImageHeader` untouched (homepage/other pages).

## Constraints / Gotchas
- **CUT (3-agent consensus, no data backing):** confidence score (no on-time/transfer data), trust badges (per-contract → card-level), travel insight (fake data), most-popular-departure (cold query).
- **BLOCKED separately:** route timeline viz — `Contract.timeline` per-contract, no canonical route path. Needs product/BE selection-rule decision.
- DO NOT use raw `min_display_rate` for hero — must apply `advance_hr` filter (same set as cards). Screenshot bug: cards ฿1,000 / strip ฿990 while ฿700 was advance_hr-excluded.

## Related
- [[trip-search-results-implementation-plan-2026-06-14]] (parent — Phase 1)
- [[contract-confidence-score-algorithm]] (related but CUT from hero)
- [[nextjs-patterns]] (data source pattern)
