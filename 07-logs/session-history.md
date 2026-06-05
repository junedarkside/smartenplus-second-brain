# Session History

Archived from master-state.md. Latest session stays in master-state.md Section 1.

---

## Session #51 (2026-06-06)
- **HEIC review upload — IMPLEMENTATED, local deps ready** — pillow-heif 0.15.0 + libheif 1.23.0 installed locally. Backend restarted with HEIC opener registered. Code committed: backend `f82b182`, frontend `0a4e6d4`. Branch: `260606-fix/heic-review-upload`.
- **Multi-agent debate** — 2 agents evaluated base64 proxy vs pillow-heif. Chose server-side (5 lines, 33% less payload, no memory spike).
- **Test deferred** — User to test HEIC upload later, then merge to production.

**Resume point:**
1. **Test HEIC upload locally** — Upload HEIC file via review form, verify WebP conversion ≤120KB.
2. **Merge `260606-fix/heic-review-upload`** → main (backend) + develop (frontend).
3. **Build production Docker** with libheif-dev.

---

## Session #50 (2026-06-05)
- **DOMAIN-1 closed** — deploy + cache clear confirmed. `NEXT_PUBLIC_DOMAIN` propagated.
- **GYG-THUMB Review Images — DONE (unmerged)** — Full image support across 2 repos: ReviewImage model + WebP ≤120KB conversion + lightbox thumbnails + file upload form + profile menu + review detail page + CSR refetch. 7 bugs found+fixed. Backend `3d1d91a`, frontend `e73fc23`, both pushed.
- **Vault optimized** — extracted dead weight to `vault-protocol.md`, `vault-guardrails.md`, `session-history.md`, `closed-items.md`. 78% reduction in master-state.md size. Report: [[vault-wrapup-optimization-report]].

**Resume point:**
1. Merge `260605-feat/review-images` → develop (frontend) + main (backend). Run migration on production.
2. GYG-THUMB follow-up: Review edit mode (RateAndReviewForm dual-mode). Backend `partial_update`.

---

## Session #49 (2026-06-05)
- **Activities /activities default category — FIXED + SHIPPED** — `hooks/useDayTripFilters.js` `DEFAULT_FILTERS.category`: DAY_TOUR → null. `filtersFromQuery` `|| null` fallback. Commit `3a4db81` → frontend develop → pushed.
- **Activities pagination reset bug — ROOT CAUSE FOUND + FIXED + SHIPPED** — StrictMode + didMountRef. No-op guard in `useDayTripFilters.js:67-75`. `scroll: false` on `router.push`. Commit `01b3708` → frontend develop → pushed.
- 3 atoms: [[react-strictmode-useref-persistence]], [[react-state-no-op-guard-side-effect-prevention]], [[nextjs-shallow-router-push-scroll-false]]

## Session #48 (2026-06-05)
- **GSC-1 Phase 1 + Phase 2 — SHIPPED** — `seoConfig.js:41` noindex fix + station-sitemap removal. Branch `effdc49` → develop `0eaf9b2`.
- **NEXT_PUBLIC_DOMAIN leading-space bug — FOUND + USER FIXED**
- Multi-agent review: SEO + frontend + /scrutinize + /debug-mantra.

## Session #47 (2026-06-05)
- **GSC 52,400 "Crawled Not Indexed" — RESEARCH COMPLETE, NO CODE** — 3-team review. Primary cause: empty ISR trip pages. Three-tier plan designed.

## Session #46 (2026-06-04)
- **Blog canonical URL bug — FIXED + SHIPPED** — WP subdomain rewrite fix. Commits `3d30407` + `b0fce4f` → develop.

## Session #45 (2026-06-04)
- **Homepage terminology audit — DONE** — Nav labels fixed. Branch `36e2786` → develop `aef5548`.
- **Production SEO phase 2 — DONE** — /locations + /destinations confirmed different products.
- 3 atoms extracted.

## Session #44 (2026-06-04)
- **GYG P1 not-suitable badges — DONE** — `IncludedExcluded.js` + `DayTripDetailPage.js`. Branch `3f12f52` → develop.
- **GYG P2 review filter — DONE** — `ReviewListByProduct.js` filter chips. Branch `d5d7482` → develop.

## Session #43 (2026-06-03)
- **CMA-1 HOTEL_PICKUP invariant — DONE** — `ContractDetailSerializer.validate()`. Commit `3a59a41` → backend main.
- **Admin-dashboard HOTEL_PICKUP validation — DONE** — Yup schema. Commits `c2e8e4e` + `5f068ef` → admin main.

## Session #42 (2026-06-03)
- **CMA-1 casing ADR — DONE** — 6 inline comments. Frontend `375e501` → develop.
- **CMA-2 meeting_point_details — FIXED** — 2 lines in `AdminBookingSummarySerializer`. Commit `09d6f3a` → backend main.

## Session #41 (2026-06-03)
- **CMA-1 partial — 2 of 6 shipped** — `showStations` deleted `ff8006e`. Admin PATCH guard `22dc045`.

## Session #40 (2026-06-03)
- **Timeline stop deletion bug — FIXED + SHIPPED** — 5 changes across 3 repos. Migration 0028.

## Session #39 (2026-06-03)
- **Contract model ambiguity audit** — 4-round debate. 6 overlaps confirmed. Vault: [[contract-model-ambiguity-audit-2026-06-03]]
- **Contract location help text fix (P0)** — admin form 4 strings. Commit `fa2f16a` → main.

## Session #38 (2026-06-03)
- **booking-summary 500 fix** — trip=None guard. Commit `4bec691` → backend main.
- **Frontend test infrastructure audit** — 54% pass rate, 6 CRITICAL. Vault: [[frontend-test-infrastructure-audit-2026-06-03]]
