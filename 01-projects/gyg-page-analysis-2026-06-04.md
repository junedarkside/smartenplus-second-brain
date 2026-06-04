---
name: gyg-page-analysis-2026-06-04
description: 3-specialist GYG Chiang Rai tour analysis vs SmartEnPlus /activities/detail/[slug]. 11 candidates surfaced, 5 adopted (P0/P1/P2), 4 backend debt flagged, AI summary deferred. Supplements [[experience-detail-page-redesign-2026-06-02]] (additive gap analysis; not a replacement).
metadata:
  type: project
  reviewed_by: gyg-vs-smartenplus-orchestrator
  date: 2026-06-04
  page: https://www.getyourguide.com/chiang-mai-l271/chiang-mai-chiang-rai-temples-day-trip-with-hot-springs-t846675/
  gyg_product_id: 846675
  smartenplus_route: /activities/detail/[...slug]
---

# GYG Page Analysis 2026-06-04

## Summary

GYG Chiang Rai tour (product 846675) analyzed section-by-section vs SmartEnPlus `/activities/detail/[slug]`. 22 GYG sections mapped, 11 candidates surfaced, 5 adopted (1 P0, 2 P1, 2 P2), 4 P3 backend debt flagged, 1 user-deferred (AI summary). Top impact: P0 footer meta strip — trivial effort, dual-purpose (visual + JSON-LD provider field).

## Context

**Why this analysis:** GYG = world-class activity detail page benchmark. SmartEnPlus already has 2026-06-02 redesign doc covering major GYG patterns (AirbnbPhotoGrid, ExperienceTitleArea, WhyTravelersLove, etc.). This round = incremental gap analysis on what 2026-06-02 missed.

**GYG page:** Chiang Rai White/Blue/Red Temple & Karen Tribe day trip. 4.8★ from 6,940 reviews. Operator: MONKEY TRAVEL ASIA. WebFetch unavailable this session — text dump used.

**SmartEnPlus state:** `/activities/detail/[...slug].js` (SSG, revalidate 3600s). 14 components post-2026-06-02 redesign. `DayTripDetailSEO.js` handles JSON-LD. 2-col grid `xl:grid-cols-[1fr_380px]`.

**Decisions locked:**
- Incremental gap analysis only (skip patterns in 2026-06-02 doc)
- Max 5 GYG patterns adopted (skeptic enforces)
- New doc supersedes 2026-06-02 deltas
- Backend-data gaps → P3 backend debt (audio guide, private group)
- AI-summarized review → deferred P3 (user confirmed)

## Specialist Findings

### R1-IA (Information Architect) — 6 missing-candidates surfaced

22 GYG sections mapped. 12 already-have, 8 partial, 6 missing. SmartEnPlus inventions (no GYG equivalent): WhyTravelersLove 5-card grid, premium glassmorphism sticky booking panel, glassmorphism back/share pill, "What to bring" as FAQ accordion. See `r1-ia.md` for full section diff.

### R1-UX (UX/Conversion Designer) — 5 KEEP, 1 DROP, 4 P3

Re-examination surfaced 11 candidates (was 6 from IA). Scoring: ROI (high/med/low), brand-fit (yes/maybe/no), effort (trivial/small/medium/large). Auto-DROP applied: brand-fit=no (UX-6 SEO footer blocks) + ROI=low+brand-fit=maybe (UX-4 page feedback, UX-10 stop-type legend). UX-2 per-aspect rating, UX-7 review thumbnails, UX-9 provider response all P3 backend debt. See `r1-ux.md` for full scoring.

### R1-SEO (SEO/Schema) — 0 P0, 3 P1, 5 P2, 1 P3

No P0 = confirms 2026-06-02 redesign covered critical SEO surface. P1 gaps: TouristAttraction schema, Review schema (nested author/datePublished/reviewBody), BreadcrumbList schema. All in `DayTripDetailSEO.js`, ~30 lines total. UX-5 footer meta strip doubles as SEO-9 (provider in JSON-LD). See `r1-seo.md` for full audit.

## Discussion: Debate

### Skeptic (R2) — challenges + auto-DROP

- **UX-4 (page feedback):** ROI=low + brand-fit=maybe → AUTO-DROP. GYG's widget is generic telemetry; SmartEnPlus can use GA event instead, zero UI cost.
- **UX-6 (SEO footer blocks):** brand-fit=no → AUTO-DROP. 4×20=80 footer links = GYG-conversion-density smell. Conflicts with premium calm.
- **UX-10 (stop-type legend):** ROI=low + brand-fit=maybe → AUTO-DROP. GYG-specific. SmartEnPlus tours have fewer stops, legend = visual noise.
- **UX-3 (sort/filter):** DOWNGRADE to P2. Verify SSR vs client data flow before commit. If SSR, effort escalates medium → large.
- **UX-5/UX-7:** KEEP conditional. Verify `Review.images[]` backend field + `operator.operator_name` duplicate risk.

### Leader (R3) — final 5 adjudicated

Adopted Skeptic verdicts. Best-case-for-pattern assumption: if verify fails at implementation, pattern drops to P3 (not P0/P1). P0/P1/P2 assignment:

- P0 = free-win tier: trivial effort + brand-fit yes + visible-or-JSON-LD signal (NOT gated on conversion ROI)
- P1 = trust/scanability lift + brand-fit yes (med-high ROI)
- P2 = polish + small/medium effort + brand-fit yes/maybe (low-med ROI)

## Leader Synthesis — Final 5 Ranked

| # | Priority | Pattern | ROI | Brand-fit | Effort | LoC | Caveat |
|---|----------|---------|-----|-----------|--------|-----|--------|
| 1 | **P0** | Footer meta strip + provider JSON-LD | low | yes | trivial | 4-6 | Verify no duplicate in ExperienceTitleArea |
| 2 | **P1** | Not-suitable-for badges | med | yes | small | 8-12 | Verify `restrictions` or derive from `difficulty_level` |
| 3 | **P1** | Review thumbnails in review cards | med | yes | small | 6-10 | **Verify `Review.images[]` backend field exists** |
| 4 | **P2** | Review sort + filter | med | maybe | medium | 25-40 | **Verify `ReviewListByProduct` is client-rendered** |
| 5 | **P2** | "For reference only" itinerary disclaimer | low | yes | trivial | 1-2 | None |

**Highest ROI-per-effort:** #1 footer meta strip — P0, trivial, dual-purpose (visible footer + JSON-LD `provider` field). Pure free win. Note: ROI=low (not conversion); P0 placement justified by free-win tier (trivial cost + brand-fit yes).

## Priority Fix Queue

- [ ] **P0** Footer meta strip — `components/activities/detail/DayTripDetailPage.js` (visual) + `components/activities/detail/DayTripDetailSEO.js` (JSON-LD `provider` field)
- [ ] **P1** Not-suitable-for badges — new component or inline in `components/activities/detail/IncludedExcluded.js`
- [ ] **P1** Review thumbnails — modify `components/review/ReviewListByProduct.js` (verify `Review.images[]` first)
- [ ] **P2** Review sort + filter — modify `components/review/ReviewListByProduct.js` (verify client-render first)
- [ ] **P2** "For reference only" disclaimer — modify `components/activities/detail/DayTripDetailPage.js`

**P3 Backend Debt (out of scope this round):**
- Audio guide 41 languages — needs `audio_guide_languages[]` on Contract
- Private group badge — needs `is_private_group` boolean on Contract
- Per-aspect rating (Guide/Transport/Value) — needs `ReviewAspect` model + aggregation
- Provider response to reviews — needs `provider_response_text` + `provider_response_date` on Review
- AI-summarized review — LLM service, user-deferred

## Verification Matrix

4 backend/data questions block adoption. Each must be verified before commit. If verify fails, pattern drops to P3 (not P0/P1/P2).

| # | Pattern | Verify | Where to check | Drop-to-P3 if |
|---|---------|--------|----------------|---------------|
| V1 | UX-1 Not-suitable-for badges | `Contract.restrictions` field exists? | Backend serializer (Django admin) or API response | No `restrictions` field AND `difficulty_level` enum insufficient |
| V2 | UX-3 Review sort + filter | `ReviewListByProduct` is client-rendered? | Component source + Redux store | SSR/SSG baked — sort needs API params (effort escalates medium → large) |
| V3 | UX-5 Footer meta strip | `operator.operator_name` not already visible in `ExperienceTitleArea`? | Read `ExperienceTitleArea.js` for operator logo/text | Already visible — DROP entirely (duplicate = noise) |
| V4 | UX-7 Review thumbnails | `Review.images[]` array exists in backend serializer? | Backend `Review` model + API response sample | Field absent — DEFER P3 (no frontend workaround) |

**Verification owner:** backend team for V1, V4 (field existence); frontend lead for V2, V3 (code inspection). All 4 should be checked in a single dev-day before any P0/P1 implementation starts.

## Key Files

### Vault files created
- `01-projects/gyg-page-analysis-2026-06-04/r1-ia.md`
- `01-projects/gyg-page-analysis-2026-06-04/r1-ux.md`
- `01-projects/gyg-page-analysis-2026-06-04/r1-seo.md`
- `01-projects/gyg-page-analysis-2026-06-04/r2-skeptic.md`
- `01-projects/gyg-page-analysis-2026-06-04/r3-leader-synthesis.md`
- `01-projects/gyg-page-analysis-2026-06-04.md` (this file)

### SmartEnPlus components referenced
- `pages/activities/detail/[...slug].js`
- `components/activities/detail/DayTripDetailPage.js`
- `components/activities/detail/DayTripDetailSEO.js`
- `components/activities/detail/IncludedExcluded.js`
- `components/activities/detail/ExperienceTitleArea.js`
- `components/review/ReviewListByProduct.js`
- `helpers/designSystem.js`

## Out of Scope (this round)

- Phase 4 — gap analysis vs 2026-06-02 implementation status
- Phase 5 — redesign plan with sequenced PRs
- Vault git commit/push (user commits manually)
- Frontend code changes (R3 outputs implementation hints only)
- Backend field additions (4 P3 debt items)

## Related

- [[experience-detail-page-redesign-2026-06-02]] — predecessor doc, 9 components already implemented
- [[business-development-thailand-platform-analysis]] — 12Go vs Klook vs GYG competitive positioning
- [[trip-detail-page-review-2026-05-20]] — prior detail page audit
- [[trip-detail-uxui-audit-2026-05-22]] — 3-specialist audit: 32 issues
- [[seo-homepage-auditor]] — SEO specialist team pattern
- [[homepage-seo-performance-deep-review-2026-05-21]] — prior SEO deep review
