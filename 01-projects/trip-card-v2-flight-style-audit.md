# Trip Card V2 Flight-Style Audit

## Summary
2-agent audit (UX/UI + Visual Design) of trip card V2 (`2931d22d`, flight-OTA layout) vs legacy V1 on `/trips/hatyai/koh-lipe`. **V2 wins: UX 7 vs 4.5, Design 7 vs 5.** Upgrade legit but shipped info regressions — stops count + JOIN chip + amenity icons dropped from card face; mobile station truncation.

## Context
V2 built 2026-07-15 from flight-card benchmark (Trip.com style: bold times, dashed duration arrow, strikethrough bar rate, slim footer). Env flag `NEXT_PUBLIC_TRIP_CARD_V2` (unset=V2, `false`=V1). Files: `TripCardV2.js`, `TripItemLayoutV2.js`, flag branch `TripItem.js`. Evidence: 10 screenshots (both versions × 375/768/1440 × collapsed/open) + code. Leader hand-verified token/code claims; 1 finding overturned.

## Scorecard

| Dimension | V1 | V2 |
|---|---|---|
| Scannability / decision speed | 4 | 8 |
| Information hierarchy | 3 | 8 |
| Cross-card comparability | 5 | 7 |
| Mobile 375 usability | 6 | 5 |
| Touch targets / affordances | 4 | 5 |
| Conversion elements | 5 | 8 |
| Information completeness | 8 | 6 |
| Typography | 3 | 7 |
| Spacing / alignment | 5 | 6.5 |
| Color / token compliance | 6 | 7 |
| Design-system consistency | 6.5 | 7 |
| Responsive integrity | 5 | 6 |
| OTA polish | 4 | 6.5 |
| Ethical pricing | 7 | 9 |
| **Overall UX/UI** | **4.5** | **7** |
| **Overall Design** | **5** | **7** |

Strongest single piece: strikethrough honesty — `barRateDisplay` pulls bar rate from SAME `getMaxRate` ratecard entry as displayed selling price, renders only when `bar > selling` (`TripItem.js` memo). Meets UK CMA / EU Omnibus anchor norms.

## P1 findings (fix before calling V2 done)

> **STATUS 2026-07-15: items 1–6 FIXED** in `fix/trip-card-v2-p1` (`2b26af9f` → develop `133d7ecb`). Verified via 375/768/1440 screenshots + build exit 0; V1 files zero diff; `TransportItems` gained opt-in `wrap` prop (default unchanged, 4 other consumers safe). Item 7 (chat FAB) deferred — page-level widget config. P2/P3 batch still open.
>
> **SKELETON 2026-07-15** (`c6c37212` → develop `1f43b452`): `SkeletonSection.js` rewritten to V2 anatomy (was V1 timeline shape); `TripSearchResults.js` 60-line inline duplicate (with phantom gallery tiles) replaced by SkeletonSection reuse. Covers all 3 consumers (trips listing, airport-transfer, destinations — all render V2). Skeleton is V2-only by design; V1 rollback path gets mismatched skeleton, accepted (no dual-skeleton over-engineering). User confirmed card design correct; legs+amenities same-line ruled 12Go-aligned. Known P2 remains: amenity icons tooltip-only — dead on touch.
1. **Stops count + JOIN/PRIVATE chip dropped.** V1 showed "1 stop • 4 hr 30 min • JOIN". `transportDescriptionText` computed in `TripItem.js` but dead in V2 path — `TripItemLayoutV2` never renders it. Flight-card convention puts stops under duration arrow. Fix: stops label under arrow in `TripCardV2`; JOIN via `BadgeChip` on legs line.
2. **Mobile stations truncate to "HATYAI…"** — disambiguating token (AIRPORT/PIER) is what's cut; Thai cities have multiple boarding points. Fix: `line-clamp-2` on mobile, arrow min-w down to 24px.
3. **Legs line clipped at 375, zero affordance** — `overflow-x-auto no-scrollbar` hides second vehicle leg (van invisible; trip reads boat-only). Fix: `flex-wrap` below sm, or edge fade.
4. **1440 arrow overstretch (~700px)** — arrival cluster visually fuses with price. Fix: `max-w-[560px]` on TripCardV2 wrapper (Trip.com caps segment block).
5. **Amenity chips (`ExtraItemsList`) dropped** — benchmark's baggage-chip equivalent; V1 footer had them. Fix: render in footer left cluster.
6. **Chevron/••• touch targets ~20px** — `sx={{padding:0}}` vs own `TOUCH_TARGET.minHeight 44px` (`designSystem.js:307`). Pre-existing in V1 too.
7. **Chat FAB overlaps BOOK NOW on first card** (375+768, both versions, page-level, pre-existing).

## P2
+1 day indicator missing (23:00→06:30 reads as arriving before departing); no "per adult" price qualifier (OTA norm); **duration data mismatch** — 11:30→15:30 labeled "4h 30m", backend duration ≠ arr−dep, V2 billboards it (pre-existing data issue → backend); gray-400 legs/strikethrough fail AA 4.5:1 (own `CONTRAST_RATIOS`); 3 fragmented click zones + price dead zone; no keyboard access on nav divs (WCAG 2.1.1); duplicate DOM ids `accordion-collapse*` across every card (V1 legacy, copied into V2); arrival column not grid-aligned across cards.

## P3
`rounded-lg` vs token `rounded-md` (`designSystem.js:150`, both versions); Top Pick `border-emerald-400` ≠ `status.success` #10B981; badge px misalign; footer padding drift; station names as `<h3>` polluting outline; "THB 1,000.00" decimals (THB convention = whole); duration label `text-[10px]`.

## Overturned by leader
- "Blank gallery in V2 accordion" (both agents flagged from `audit-v2-1440-open.png`) — **capture artifact**: earlier same-path screenshot showed gallery fully loaded; lazy images not ready at 1.5s wait.

## Decision
Keep V2 default. P1 list = follow-up branch before prod deploy. Touch targets/contrast/duplicate-ids/FAB are pre-existing shared debt — fix once in V2 (V1 is rollback-only).

## Related
[[trip-search-results-redesign-2026-06-14]] · [[currency-context-price-rendering-rule]] · [[trip-page-full-audit]] · [[gyg-card-rate-analysis-2026-06-05]] · [[unified-badge-system-pattern]] · [[design-systems]]
